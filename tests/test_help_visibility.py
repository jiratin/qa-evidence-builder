from pathlib import Path

app = (Path(__file__).parents[1] / "src/qa_evidence/app.py").read_text(encoding="utf-8")

assert 'text="Help / User Guide"' in app
assert 'label="User Guide"' in app
assert "def open_help(self):" in app
assert "HelpDialog(self)" in app
assert "def _build_menu(self):" in app
assert "self._build_menu()" in app

print("ALL_HELP_VISIBILITY_TESTS_PASSED")
