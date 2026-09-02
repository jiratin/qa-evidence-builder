import os
import sys
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
root = Path(__file__).parents[1]
sys.path.insert(0, str(root / "src"))

from PySide6.QtWidgets import QApplication, QMessageBox
from qa_evidence.app import MainWindow
from qa_evidence.parser import parse_auto

application = QApplication.instance() or QApplication([])
window = MainWindow()
window.entries = parse_auto((root / "samples/sample_logs.json").read_text(encoding="utf-8"))
window._configure_entries()
window.refresh()

assert window.table.rowCount() == len(window.entries)
assert window.pages.count() == 4
assert window.tx_table.columnCount() == 7
assert not window.business_errors_only.isChecked()
window.status.setCurrentText("5xx")
assert window.reset_filters_button.text().endswith("(1)")
window.clear_request_filters()
assert window.reset_filters_button.text() == "Reset all filters"
window.filter_preset.setCurrentText("All Errors")
window.apply_filter_preset()
assert window.errors_only.isChecked()
window.reset_filters()
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
window.raw.setChecked(True)
with patch("qa_evidence.app.QMessageBox.warning", return_value=QMessageBox.Cancel), \
     patch("qa_evidence.app.QFileDialog.getExistingDirectory") as choose_folder:
    window.export()
    choose_folder.assert_not_called()

window.close()
application.quit()
print("ALL_UI_SMOKE_TESTS_PASSED")
