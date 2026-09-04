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
assert 'setObjectName("brandIcon")' in app
assert "QPixmap" in app
assert 'brand_pixmap.scaled(36, 36' in app
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
assert "QMenu {" in theme
assert "QMenu::item:selected" in theme
assert "QMenu::indicator:checked" in theme
assert "QTabWidget::pane" in theme
assert "QTabBar::tab:hover" in theme
assert "QTabBar::tab:selected" in theme
assert "QTabBar::tab:disabled" in theme
assert "QAbstractScrollArea::corner" in theme
assert "QTableCornerButton::section" in theme
assert "QScrollBar:horizontal" in theme
assert "QScrollBar::handle:horizontal" in theme
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
assert "QHeaderView.Interactive" in app
assert "setSectionsMovable(True)" in app
assert "sectionMoved.connect(self._persist_timeline_column_order)" in app
assert "def _restore_timeline_column_order(self):" in app
assert "Qt.ScrollBarAsNeeded" in app
assert "toggle_include_from_indicator" in app
assert "toggle_include_selected_rows" in app
assert "Qt.Key_Space" in app
assert "toggle_filters" in app
assert "selected_text" in theme
assert "assets/icons/png/icon-256.png" in (root / "README.md").read_text(encoding="utf-8")
assert "export_folder_format" in app
assert "Log_{date}_{time}" in app
assert "export_file_format" in app
assert "DEFAULT_EXPORT_LOG_FILENAME_FORMAT" in app
assert "def _append_entries(self, new_entries):" in app
assert "def _rebuild_timeline_field_menu(self):" in app
assert 'button("Timeline fields")' in app
assert "QTreeWidget" in app
assert 'addTab(preview_page, "Included Evidence Preview")' in app
assert 'addTab(tree_page, "Export Tree Preview")' in app
assert "def update_export_tree(self, *args):" in app
assert "build_export_structure" in app
assert "QTreeWidget::item:selected" in theme
assert "Find in evidence" in app
assert "find_in_evidence" in app
assert "QTextDocument.FindCaseSensitively" in app
assert 'QKeySequence("Shift+Return")' in app
assert "_evidence_match_starts" in app
assert 'f"{current} / {len(matches)} {noun}"' in app

print("ALL_UI_SOURCE_TESTS_PASSED")
