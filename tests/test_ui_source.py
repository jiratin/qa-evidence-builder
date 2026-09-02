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
assert "setWindowIcon" in app
assert "Import completed with warnings" in app
assert "Export raw logs?" in app
assert "without sensitive-data masking" in app
assert "QSplitter" in app
assert "PySide6" in help_dialog
assert "HELP_SECTIONS" in help_dialog
assert "QFrame#sidebar" in theme
assert "QPushButton#primary" in theme
assert '"light"' in theme
assert "QComboBox QAbstractItemView" in theme
assert "Also create ZIP archive" in app
assert "Kafka topic" in app
assert "Page URL" in app
assert "Business errors" in app
assert "Success result codes" in app
assert "Include journey" in app
assert "Evidence note" in app
assert "getOpenFileNames" in app
assert "parse_files" in app
assert 'group("Search across logs"' in app
assert 'group("Request"' in app
assert 'group("Result"' in app
assert 'group("Performance"' in app
assert 'group("Context"' in app
assert "QLabel#alert" in theme
assert "QLabel#errorText" in theme
assert "QCheckBox#danger" in theme
assert "update_active_filter_chips" in app
assert "Reset all filters (" in app
assert "Current Transaction" in app
assert "clear_request_filters" in app
assert "QPushButton#filterChip" in theme

print("ALL_UI_SOURCE_TESTS_PASSED")
