import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
root = Path(__file__).parents[1]
sys.path.insert(0, str(root / "src"))

from PySide6.QtWidgets import QApplication
from qa_evidence.app import MainWindow
from qa_evidence.parser import parse_auto

application = QApplication.instance() or QApplication([])
window = MainWindow()
window.entries = parse_auto((root / "samples/sample_logs.json").read_text(encoding="utf-8"))
window.refresh()

assert window.table.rowCount() == len(window.entries)
assert window.pages.count() == 4
assert window.mask.isChecked()
assert window.export_group.count() == 4
assert not window.include_zip.isChecked()
original_theme = window.theme_mode
window.toggle_theme()
assert window.theme_mode != original_theme
window.toggle_theme()
window.include_all_filtered()
assert len(window.included_entries()) == len(window.entries)
assert window.preview.toPlainText().strip()

window.close()
application.quit()
print("ALL_UI_SMOKE_TESTS_PASSED")
