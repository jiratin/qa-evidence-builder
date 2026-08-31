from pathlib import Path

root = Path(__file__).parents[1]
app = (root / "src/qa_evidence/app.py").read_text(encoding="utf-8")
help_dialog = (root / "src/qa_evidence/help_dialog.py").read_text(encoding="utf-8")
theme = (root / "src/qa_evidence/theme.py").read_text(encoding="utf-8")

assert "tkinter" not in app.lower()
assert "PySide6" in app
assert "class MainWindow(QMainWindow)" in app
assert "def import_file(self):" in app
assert "def paste_json(self):" in app
assert "def open_help(self):" in app
assert "HelpDialog(self)" in app
assert "QSplitter" in app
assert "PySide6" in help_dialog
assert "HELP_SECTIONS" in help_dialog
assert "QFrame#sidebar" in theme
assert "QPushButton#primary" in theme
assert '"light"' in theme
assert "Also create ZIP archive" in app
assert "Kafka topic" in app

print("ALL_UI_SOURCE_TESTS_PASSED")
