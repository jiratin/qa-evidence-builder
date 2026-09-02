import os
import sys
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
root = Path(__file__).parents[1]
sys.path.insert(0, str(root / "src"))

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QHeaderView, QMessageBox
from qa_evidence.app import MainWindow
from qa_evidence.parser import parse_auto

application = QApplication.instance() or QApplication([])
window = MainWindow()
assert window.brand_icon.pixmap() is not None
assert not window.brand_icon.pixmap().isNull()
window.entries = parse_auto((root / "samples/sample_logs.json").read_text(encoding="utf-8"))
window._configure_entries()
window.refresh()

assert window.table.rowCount() == len(window.entries)
assert window.pages.count() == 4
assert window.tx_table.columnCount() == 7
assert window.table.horizontalHeader().sectionResizeMode(0) == QHeaderView.Interactive
assert window.table.horizontalScrollBarPolicy() == Qt.ScrollBarAsNeeded
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
assert not window.include_zip.isChecked()
assert not window.raw.isChecked()
assert not window.raw_warning.isVisible()
window.raw.setChecked(True)
assert not window.raw_warning.isHidden()
window.raw.setChecked(False)
original_theme = window.theme_mode
window.toggle_theme()
assert window.theme_mode != original_theme
window.toggle_theme()
window.include_all_filtered()
assert len(window.included_entries()) == len(window.entries)
assert window.preview.toPlainText().strip()
window.evidence_search.setText("Evidence")
assert window.preview.textCursor().selectedText().lower() == "evidence"
assert window.evidence_search_status.text() == "Match"
window.evidence_match_case.setChecked(True)
window.evidence_search.setText("evidence-value-that-does-not-exist")
assert window.evidence_search_status.text() == "No matches"
window.evidence_search.clear()
window.raw.setChecked(True)
with patch("qa_evidence.app.QMessageBox.warning", return_value=QMessageBox.Cancel), \
     patch("qa_evidence.app.QFileDialog.getExistingDirectory") as choose_folder:
    window.export()
    choose_folder.assert_not_called()

window.close()
application.quit()
print("ALL_UI_SMOKE_TESTS_PASSED")
