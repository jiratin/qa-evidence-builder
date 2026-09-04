import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
root = Path(__file__).parents[1]
sys.path.insert(0, str(root / "src"))

from PySide6.QtCore import QSettings, Qt
from PySide6.QtWidgets import QApplication, QHeaderView, QMessageBox
from qa_evidence.app import MainWindow
from qa_evidence.parser import parse_auto

application = QApplication.instance() or QApplication([])
settings_directory = tempfile.TemporaryDirectory()
QSettings.setDefaultFormat(QSettings.IniFormat)
QSettings.setPath(QSettings.IniFormat, QSettings.UserScope, settings_directory.name)
window = MainWindow()
assert window.brand_icon.pixmap() is not None
assert not window.brand_icon.pixmap().isNull()
window.entries = parse_auto((root / "samples/sample_logs.json").read_text(encoding="utf-8"))
window._configure_entries()
window.refresh()

assert window.table.rowCount() == len(window.entries)
assert window.table.horizontalHeaderItem(10).text() == "Kafka Topic"
assert "kafka_topic_name" in window._source_fields()
assert window.pages.count() == 4
assert window.tx_table.columnCount() == 7
assert window.table.horizontalHeader().sectionResizeMode(0) == QHeaderView.Interactive
assert window.table.horizontalHeader().sectionsMovable()
assert window.table.horizontalScrollBarPolicy() == Qt.ScrollBarAsNeeded
api_logical = next(
    column for column in range(window.table.columnCount())
    if window.table.horizontalHeaderItem(column).text() == "API"
)
window.table.horizontalHeader().moveSection(window.table.horizontalHeader().visualIndex(api_logical), 0)
assert window.table.horizontalHeader().logicalIndex(0) == api_logical
assert "request_uri" in str(window.settings.value("timeline_column_order"))
filter_was_hidden = window.filter_content.isHidden()
window.toggle_filters()
assert window.filter_content.isHidden() != filter_was_hidden
window.toggle_filters()
assert not window.business_errors_only.isChecked()
window.status.setCurrentText("5xx")
assert window.reset_filters_button.text().endswith("(1)")
window.clear_request_filters()
assert window.reset_filters_button.text() == "Reset all filters"
window.filter_preset.setCurrentText("All Errors")
window.apply_filter_preset()
assert window.errors_only.isChecked()
window.reset_filters()
window.table.selectRow(0)
first_index = window.filtered[0].index
window.toggle_include_selected_rows()
assert first_index in window.included_indexes
window.table.selectRow(0)
window.toggle_include_selected_rows()
assert first_index not in window.included_indexes
window.toggle_include_from_indicator(0, 0)
assert first_index in window.included_indexes
window.clear_included()
assert window.mask.isChecked()
assert window.export_group.count() == 5
assert window.evidence_preview_tabs.count() == 2
assert window.evidence_preview_tabs.tabText(0) == "Included Evidence Preview"
assert window.evidence_preview_tabs.tabText(1) == "Export Tree Preview"
assert not window.include_zip.isChecked()
assert not window.raw.isChecked()
assert not window.raw_warning.isVisible()
window.raw.setChecked(True)
assert not window.raw_warning.isHidden()
window.raw.setChecked(False)
window.export_file_format.setText("{date}_{endpoint}")
window.export_group.setCurrentIndex(window.export_group.findData("kafka"))
window.include_zip.setChecked(True)
assert window.settings.value("export_file_format") == "{date}_{endpoint}"
assert window.settings.value("export_group") == "kafka"
assert str(window.settings.value("include_zip")).lower() == "true"
restored_window = MainWindow()
assert restored_window.export_file_format.text() == "{date}_{endpoint}"
assert restored_window.export_group.currentData() == "kafka"
assert restored_window.include_zip.isChecked()
assert restored_window.mask.isChecked()
assert not restored_window.raw.isChecked()
restored_window.close()
original_theme = window.theme_mode
window.toggle_theme()
assert window.theme_mode != original_theme
window.toggle_theme()
window.include_all_filtered()
assert len(window.included_entries()) == len(window.entries)
assert window.export_tree.topLevelItemCount() >= 1
assert window.export_tree.topLevelItem(0).text(1).endswith("logs")
assert window.export_tree_status.text().startswith("Included ")
included_before_append = set(window.included_indexes)
existing_count = len(window.entries)
window._append_entries(parse_auto({"fields": {
    "TIMESTAMP": ["2026-08-21 11:03:39.000"],
    "REQUEST_URI": ["/appended"],
    "CUSTOM_TIMELINE_FIELD": ["visible-value"],
}}))
assert len(window.entries) == existing_count + 1
assert included_before_append.issubset(window.included_indexes)
assert "CUSTOM_TIMELINE_FIELD" in window._source_fields()
window._toggle_timeline_field("CUSTOM_TIMELINE_FIELD", True)
assert window.table.horizontalHeaderItem(window.table.columnCount() - 1).text() == "CUSTOM_TIMELINE_FIELD"
assert any(
    window.table.item(row, window.table.columnCount() - 1).text() == "visible-value"
    for row in range(window.table.rowCount())
)
assert window.preview.toPlainText().strip()
window.evidence_search.setText("Evidence")
assert window.preview.textCursor().selectedText().lower() == "evidence"
assert window.evidence_search_status.text().endswith("matches")
assert int(window.evidence_search_status.text().split(" / ")[1].split()[0]) > 1
first_match_status = window.evidence_search_status.text()
window.find_in_evidence()
assert window.evidence_search_status.text() != first_match_status
window.find_in_evidence(backward=True)
assert window.evidence_search_status.text() == first_match_status
window.evidence_match_case.setChecked(True)
window.evidence_search.setText("evidence-value-that-does-not-exist")
assert window.evidence_search_status.text() == "0 matches"
window.evidence_search.clear()
window.raw.setChecked(True)
with patch("qa_evidence.app.QMessageBox.warning", return_value=QMessageBox.Cancel), \
     patch("qa_evidence.app.QFileDialog.getExistingDirectory") as choose_folder:
    window.export()
    choose_folder.assert_not_called()

window.close()
application.quit()
settings_directory.cleanup()
print("ALL_UI_SMOKE_TESTS_PASSED")
