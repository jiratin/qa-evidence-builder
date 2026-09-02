from pathlib import Path

app = (Path(__file__).parents[1] / "src/qa_evidence/app.py").read_text(encoding="utf-8")

assert 'button("?  Help / User Guide", self.open_help, name="nav")' in app
assert "def open_help(self):" in app
assert "HelpDialog(self)" in app
assert "lay.addWidget(button(\"?  Help / User Guide\"" in app

print("ALL_HELP_VISIBILITY_TESTS_PASSED")
