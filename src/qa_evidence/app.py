"""Modern PySide6 desktop interface for QA Evidence Builder."""

import sys
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QSettings, Qt
from PySide6.QtGui import QColor, QIcon, QKeySequence, QShortcut, QTextCursor, QTextDocument
from PySide6.QtWidgets import (
    QAbstractItemView, QApplication, QCheckBox, QComboBox, QDialog, QFileDialog, QFrame,
    QGridLayout, QHBoxLayout, QHeaderView, QLabel, QLineEdit, QMainWindow,
    QMessageBox, QPlainTextEdit, QPushButton, QScrollArea, QSizePolicy,
    QSplitter, QStackedWidget, QTableWidget, QTableWidgetItem, QTabWidget,
    QVBoxLayout, QWidget,
)

from . import __version__
from .analyzer import (
    build_auto_summary, error_fingerprint, find_duplicate_errors, transaction_journey,
)
from .evidence import build_markdown, build_ticket
from .exporter import build_export_folder_name, export_package
from .filtering import filter_entries, group_by_transaction
from .help_dialog import HelpDialog
from .parser import parse_auto, parse_files, parse_with_report
from .theme import COLORS, stylesheet


def resource_path(relative):
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).parents[2]))
    return base / relative


TRANSACTION_SOURCE_LABELS = {
    "request_body": "Request Body",
    "url_query": "URL Query",
    "request_params": "Request Params",
    "transaction_field": "Transaction Field",
    "request_header": "Request Header",
    "request_id_fallback": "Request ID fallback",
    "not_found": "Not found",
}


def button(text, slot=None, primary=False, name=None):
    widget = QPushButton(text)
    widget.setCursor(Qt.PointingHandCursor)
    if primary:
        widget.setObjectName("primary")
    elif name:
        widget.setObjectName(name)
    if slot:
        widget.clicked.connect(slot)
    return widget


def panel(layout=None):
    frame = QFrame()
    frame.setObjectName("panel")
    frame.setLayout(layout or QVBoxLayout())
    return frame


class PasteDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Paste JSON Array / HAR")
        self.resize(850, 560)
        root = QVBoxLayout(self)
        title = QLabel("Paste JSON")
        title.setObjectName("pageTitle")
        root.addWidget(title)
        self.editor = QPlainTextEdit()
        self.editor.setPlaceholderText("Paste a JSON array or HAR object here…")
        root.addWidget(self.editor, 1)
        actions = QHBoxLayout()
        actions.addStretch()
        actions.addWidget(button("Cancel", self.reject))
        actions.addWidget(button("Load logs", self.accept, primary=True))
        root.addLayout(actions)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QA Evidence Builder")
        self.setWindowIcon(QIcon(str(resource_path("assets/icons/png/icon-256.png"))))
        self.resize(1480, 900)
        self.setMinimumSize(860, 620)
        self.settings = QSettings("QA Evidence Builder", "QA Evidence Builder")
        self.theme_mode = self.settings.value("theme", "dark")
        try:
            self.slow_threshold_ms = max(1.0, float(self.settings.value("slow_threshold_ms", 3000)))
        except (TypeError, ValueError):
            self.slow_threshold_ms = 3000.0
        stored_codes = str(self.settings.value("success_result_codes", "0,200,20000,SUCCESS,OK"))
        self.success_result_codes = tuple(code.strip() for code in stored_codes.split(",") if code.strip())
        self.entries, self.filtered = [], []
        self.included_indexes = set()
        self._build()
        self._connect_filters()
        self._apply_theme()
        QShortcut(QKeySequence("Ctrl+O"), self, activated=self.import_file)
        QShortcut(QKeySequence("Ctrl+E"), self, activated=self.export)
        self.refresh()

    def _build(self):
        root = QWidget()
        self.setCentralWidget(root)
        layout = QHBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.sidebar = self._sidebar()
        layout.addWidget(self.sidebar)
        body = QWidget()
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(24, 18, 24, 14)
        body_layout.setSpacing(14)
        body_layout.addLayout(self._header())
        self.pages = QStackedWidget()
        self.pages.addWidget(self._dashboard_page())
        self.pages.addWidget(self._transactions_page())
        self.pages.addWidget(self._evidence_page())
        self.pages.addWidget(self._analysis_page())
        body_layout.addWidget(self.pages, 1)
        self.status_label = QLabel("Ready — import JSON or HAR to begin")
        self.status_label.setObjectName("muted")
        body_layout.addWidget(self.status_label)
        layout.addWidget(body, 1)

    def _sidebar(self):
        side = QFrame()
        side.setObjectName("sidebar")
        side.setFixedWidth(220)
        lay = QVBoxLayout(side)
        lay.setContentsMargins(16, 22, 16, 16)
        brand = QLabel("◈  QA Evidence")
        brand.setObjectName("brand")
        lay.addWidget(brand)
        subtitle = QLabel("Local evidence workspace")
        subtitle.setObjectName("muted")
        lay.addWidget(subtitle)
        lay.addSpacing(22)
        self.nav_buttons = []
        for index, label in enumerate(("▦  Dashboard", "↔  Transactions", "◇  Evidence", "⌁  Analysis")):
            nav = button(label, name="nav")
            nav.setCheckable(True)
            nav.clicked.connect(lambda checked=False, i=index: self._navigate(i))
            self.nav_buttons.append(nav)
            lay.addWidget(nav)
        self.nav_buttons[0].setChecked(True)
        lay.addStretch()
        lay.addWidget(button("?  Help / User Guide", self.open_help, name="nav"))
        version = QLabel(f"v{__version__}  •  Local only")
        version.setObjectName("muted")
        lay.addWidget(version)
        return side

    def _header(self):
        lay = QHBoxLayout()
        titles = QVBoxLayout()
        self.page_title = QLabel("Dashboard")
        self.page_title.setObjectName("pageTitle")
        self.page_subtitle = QLabel("Inspect logs, isolate failures, and build shareable evidence.")
        self.page_subtitle.setObjectName("muted")
        titles.addWidget(self.page_title)
        titles.addWidget(self.page_subtitle)
        lay.addLayout(titles)
        lay.addStretch()
        self.theme_button = button("Light mode", self.toggle_theme)
        lay.addWidget(self.theme_button)
        lay.addWidget(button("Import JSON / HAR File(s)", self.import_file))
        lay.addWidget(button("Paste JSON", self.paste_json))
        lay.addWidget(button("Clear", self.clear_all))
        lay.addWidget(button("Export Evidence", self.export, primary=True))
        return lay

    def _dashboard_page(self):
        page = QWidget()
        root = QVBoxLayout(page)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(12)
        cards = QHBoxLayout()
        self.metrics = {}
        for key, label, color in (
            ("total", "Total logs", COLORS["primary"]), ("success", "Successful", "#42d392"),
            ("errors", "Errors", "#ff6b7a"), ("slow", "Slow APIs", "#f6c85f"),
            ("included", "Included", "#72b7ff"),
        ):
            card_layout = QHBoxLayout()
            cap = QLabel(label)
            cap.setObjectName("cardLabel")
            value = QLabel("0")
            value.setObjectName("metric")
            value.setStyleSheet(f"color: {color};")
            card_layout.addWidget(cap)
            card_layout.addStretch()
            card_layout.addWidget(value)
            card_layout.setContentsMargins(12, 5, 12, 5)
            cards.addWidget(panel(card_layout), 1)
            self.metrics[key] = value
        root.addLayout(cards)
        root.addWidget(self._filters())
        split = QSplitter(Qt.Horizontal)
        split.addWidget(self._timeline_panel())
        split.addWidget(self._inspector_panel())
        split.setSizes([980, 340])
        split.setCollapsible(1, True)
        root.addWidget(split, 1)
        return page

    def _filters(self):
        content_layout = QVBoxLayout(); content_layout.setContentsMargins(0, 4, 0, 0); content_layout.setSpacing(8)
        self.search = QLineEdit(); self.search.setPlaceholderText("Search API, request ID…")
        self.method = QComboBox(); self.method.addItems(["ALL", "GET", "POST", "PUT", "PATCH", "DELETE"])
        self.status = QComboBox(); self.status.addItems(["ALL", "2xx", "3xx", "4xx", "5xx", "Other"])
        self.min_ms = QLineEdit(); self.min_ms.setPlaceholderText("Minimum ms")
        self.page_filter = QLineEdit(); self.page_filter.setPlaceholderText("Page")
        self.topic = QLineEdit(); self.topic.setPlaceholderText("Kafka topic")
        self.transaction = QLineEdit(); self.transaction.setPlaceholderText("Transaction ID")
        self.errors_only = QCheckBox("Errors only")
        self.business_errors_only = QCheckBox("Business errors")
        self.slow_only = QCheckBox("Slow only")
        self.errors_only.setObjectName("danger"); self.business_errors_only.setObjectName("danger")

        def group(title, widgets, clear_slot, stretch=False):
            frame = QFrame(); frame.setObjectName("filterGroup")
            layout = QVBoxLayout(frame); layout.setContentsMargins(9, 7, 9, 9); layout.setSpacing(5)
            title_row = QHBoxLayout()
            label = QLabel(title.upper()); label.setObjectName("filterTitle"); title_row.addWidget(label); title_row.addStretch()
            clear_button = button("Clear", clear_slot, name="filterClear"); title_row.addWidget(clear_button)
            layout.addLayout(title_row)
            controls = QHBoxLayout(); controls.setSpacing(6)
            for widget in widgets: controls.addWidget(widget, 1 if stretch else 0)
            layout.addLayout(controls)
            return frame

        preset_row = QHBoxLayout(); preset_row.addWidget(QLabel("Quick preset"))
        self.filter_preset = QComboBox()
        self.filter_preset.addItems(["Choose preset…", "All Errors", "Slow APIs", "Current Transaction"])
        preset_row.addWidget(self.filter_preset); preset_row.addWidget(button("Apply", self.apply_filter_preset)); preset_row.addStretch()
        content_layout.addLayout(preset_row)
        content_layout.addWidget(group("Search across logs", [self.search], self.clear_search_filter, stretch=True))
        categories = QGridLayout(); categories.setSpacing(8)
        categories.addWidget(group("Request", [self.method, self.status], self.clear_request_filters), 0, 0)
        categories.addWidget(group("Result", [self.errors_only, self.business_errors_only], self.clear_result_filters), 0, 1)
        categories.addWidget(group("Performance", [self.min_ms, self.slow_only], self.clear_performance_filters), 1, 0)
        categories.addWidget(group("Context", [self.page_filter, self.topic, self.transaction], self.clear_context_filters), 1, 1)
        categories.setColumnStretch(1, 1)
        self.reset_filters_button = button("Reset all filters", self.reset_filters); categories.addWidget(self.reset_filters_button, 1, 2)
        content_layout.addLayout(categories)
        self.filter_content = QWidget(); self.filter_content.setLayout(content_layout)
        expanded_value = str(self.settings.value("filters_expanded", "false")).lower()
        expanded = expanded_value in {"1", "true", "yes"}
        self.filter_content.setVisible(expanded)
        outer = QVBoxLayout(); outer.setContentsMargins(12, 7, 12, 7); outer.setSpacing(4)
        header = QHBoxLayout(); title = QLabel("Search & Filters"); title.setObjectName("sectionTitle")
        self.filter_toggle = button("Hide filters ▲" if expanded else "Show filters ▼", self.toggle_filters)
        header.addWidget(title); header.addStretch(); header.addWidget(self.filter_toggle)
        outer.addLayout(header); outer.addWidget(self.filter_content)
        return panel(outer)

    def _timeline_panel(self):
        lay = QVBoxLayout()
        self.active_filters_row = QWidget(); self.active_filters_layout = QHBoxLayout(self.active_filters_row)
        self.active_filters_layout.setContentsMargins(0, 0, 0, 0); self.active_filters_layout.setSpacing(6)
        lay.addWidget(self.active_filters_row)
        header = QHBoxLayout()
        title = QLabel("Timeline"); title.setObjectName("sectionTitle")
        self.result_count = QLabel("0 results"); self.result_count.setObjectName("muted")
        header.addWidget(title); header.addWidget(self.result_count); header.addStretch()
        header.addWidget(button("Include selected", self.include_selected))
        header.addWidget(button("Exclude selected", self.exclude_selected))
        header.addWidget(button("Select all", self.include_all_filtered))
        header.addWidget(button("Deselect all", self.clear_included))
        lay.addLayout(header)
        columns = ("Export", "Timestamp", "Flag", "Fingerprint", "Method", "API", "Status", "ms", "Request ID", "Transaction")
        self.table = QTableWidget(0, len(columns))
        self.table.setHorizontalHeaderLabels(columns)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.ExtendedSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        table_header = self.table.horizontalHeader()
        table_header.setSectionResizeMode(QHeaderView.Interactive)
        table_header.setMinimumSectionSize(44)
        table_header.setStretchLastSection(False)
        for column, width in enumerate((58, 175, 120, 115, 75, 320, 72, 82, 180, 190)):
            self.table.setColumnWidth(column, width)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.table.cellClicked.connect(self.toggle_include_from_indicator)
        self.table.itemSelectionChanged.connect(self.update_inspector)
        self.timeline_space_shortcut = QShortcut(QKeySequence(Qt.Key_Space), self.table)
        self.timeline_space_shortcut.setContext(Qt.WidgetWithChildrenShortcut)
        self.timeline_space_shortcut.activated.connect(self.toggle_include_selected_rows)
        lay.addWidget(self.table, 1)
        return panel(lay)

    def _inspector_panel(self):
        lay = QVBoxLayout()
        title = QLabel("Log inspector"); title.setObjectName("sectionTitle")
        hint = QLabel("Select a timeline row to inspect its normalized fields and raw payload.")
        hint.setWordWrap(True); hint.setObjectName("muted")
        self.inspector = QPlainTextEdit(); self.inspector.setReadOnly(True)
        self.inspector_alert = QLabel(); self.inspector_alert.setObjectName("errorText"); self.inspector_alert.setWordWrap(True); self.inspector_alert.hide()
        note_title = QLabel("Evidence note"); note_title.setObjectName("sectionTitle")
        self.note_editor = QPlainTextEdit(); self.note_editor.setPlaceholderText("Add a note for the selected log…")
        self.note_editor.setMaximumHeight(90)
        lay.addWidget(title); lay.addWidget(hint); lay.addWidget(self.inspector_alert); lay.addWidget(self.inspector, 1)
        lay.addWidget(note_title); lay.addWidget(self.note_editor)
        lay.addWidget(button("Save note", self.save_log_note))
        return panel(lay)

    def _transactions_page(self):
        page = QWidget(); root = QVBoxLayout(page); root.setContentsMargins(0, 0, 0, 0)
        info = QLabel("Transaction journeys — double-click a row to apply it to the Dashboard filter."); info.setObjectName("muted")
        root.addWidget(info)
        self.tx_table = QTableWidget(0, 7)
        self.tx_table.setHorizontalHeaderLabels(("Transaction ID", "APIs", "HTTP", "Business", "Slow", "Duration", "Source"))
        self.tx_table.setSelectionBehavior(QTableWidget.SelectRows); self.tx_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tx_table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        for column, width in enumerate((260, 70, 70, 90, 70, 110, 120)):
            self.tx_table.setColumnWidth(column, width)
        self.tx_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.tx_table.doubleClicked.connect(self.apply_transaction_group)
        self.tx_table.itemSelectionChanged.connect(self.update_journey_detail)
        root.addWidget(panel_with_widget(self.tx_table), 1)
        actions = QHBoxLayout(); actions.addWidget(button("Include journey", self.include_transaction_journey)); actions.addStretch()
        root.addLayout(actions)
        self.journey_detail = QPlainTextEdit(); self.journey_detail.setReadOnly(True); self.journey_detail.setMaximumHeight(220)
        self.journey_alert = QLabel(); self.journey_alert.setObjectName("errorText"); self.journey_alert.hide()
        root.addWidget(self.journey_alert)
        root.addWidget(self.journey_detail)
        return page

    def _evidence_page(self):
        page = QWidget(); root = QHBoxLayout(page); root.setContentsMargins(0, 0, 0, 0)
        left = QVBoxLayout()
        ea = QSplitter(Qt.Horizontal)
        self.expected = QPlainTextEdit(); self.expected.setPlaceholderText("Expected result")
        self.actual = QPlainTextEdit(); self.actual.setPlaceholderText("Actual result")
        ea.addWidget(self.expected); ea.addWidget(self.actual)
        left.addWidget(ea)
        preview_header = QHBoxLayout()
        preview_title = QLabel("Included evidence preview"); preview_title.setObjectName("sectionTitle")
        self.evidence_search = QLineEdit(); self.evidence_search.setPlaceholderText("Find in evidence")
        self.evidence_search.setClearButtonEnabled(True); self.evidence_search.setMaximumWidth(320)
        self.evidence_search.setAccessibleName("Find in evidence preview")
        self.evidence_search_previous = button("Previous", lambda: self.find_in_evidence(backward=True))
        self.evidence_search_next = button("Next", self.find_in_evidence)
        self.evidence_match_case = QCheckBox("Match case")
        self.evidence_search_status = QLabel(); self.evidence_search_status.setObjectName("muted")
        preview_header.addWidget(preview_title); preview_header.addStretch()
        preview_header.addWidget(self.evidence_search); preview_header.addWidget(self.evidence_search_previous)
        preview_header.addWidget(self.evidence_search_next); preview_header.addWidget(self.evidence_match_case)
        preview_header.addWidget(self.evidence_search_status)
        self.preview = QPlainTextEdit(); self.preview.setReadOnly(True)
        left.addLayout(preview_header); left.addWidget(self.preview, 1)
        root.addWidget(panel_from_layout(left), 3)
        options = QVBoxLayout(); options.setContentsMargins(15, 15, 15, 15)
        opt_title = QLabel("Evidence options"); opt_title.setObjectName("sectionTitle")
        options.addWidget(opt_title)
        self.mask = QCheckBox("Mask sensitive data"); self.mask.setChecked(True)
        self.extra_mask = QLineEdit(); self.extra_mask.setPlaceholderText("Extra mask keys, comma separated")
        options.addWidget(self.mask); options.addWidget(self.extra_mask); options.addSpacing(12)
        pkg = QLabel("Package contents"); pkg.setObjectName("sectionTitle"); options.addWidget(pkg)
        self.summary_txt = QCheckBox("summary.txt"); self.summary_txt.setChecked(True)
        self.summary_md = QCheckBox("summary.md"); self.summary_md.setChecked(True)
        self.raw = QCheckBox("Raw log files")
        self.sanitized = QCheckBox("Sanitized log files"); self.sanitized.setChecked(True)
        for check in (self.summary_txt, self.summary_md, self.raw, self.sanitized): options.addWidget(check)
        self.raw_warning = QLabel("⚠ Raw logs are exported without sensitive-data masking.")
        self.raw_warning.setWordWrap(True); self.raw_warning.setObjectName("alert"); self.raw_warning.setVisible(False)
        options.addWidget(self.raw_warning)
        self.raw.toggled.connect(self.raw_warning.setVisible)
        options.addSpacing(12)
        grouping = QLabel("Folder grouping"); grouping.setObjectName("sectionTitle"); options.addWidget(grouping)
        self.export_group = QComboBox()
        self.export_group.addItem("No grouping", "none")
        self.export_group.addItem("Kafka topic", "kafka")
        self.export_group.addItem("Page name", "page")
        self.export_group.addItem("Page URL", "page_url")
        self.export_group.addItem("Custom folder", "custom")
        self.custom_group_name = QLineEdit(); self.custom_group_name.setPlaceholderText("Custom folder name")
        self.custom_group_name.setVisible(False)
        self.include_zip = QCheckBox("Also create ZIP archive")
        folder_format = QLabel("Export folder format"); folder_format.setObjectName("sectionTitle")
        self.export_folder_format = QLineEdit(str(self.settings.value("export_folder_format", "Log_{date}_{time}")))
        self.export_folder_format.setPlaceholderText("Log_{date}_{time}")
        self.export_folder_format.setToolTip("Supported tokens: {date}, {time}")
        options.addWidget(self.export_group); options.addWidget(self.custom_group_name); options.addWidget(self.include_zip)
        options.addWidget(folder_format); options.addWidget(self.export_folder_format)
        self.export_group.currentIndexChanged.connect(self._update_grouping_options)
        options.addStretch()
        options.addWidget(button("Copy for ticket", self.copy_ticket))
        options.addWidget(button("Copy as Markdown", self.copy_markdown))
        options.addWidget(button("Export evidence", self.export, primary=True))
        root.addWidget(panel(options), 1)
        self.expected.textChanged.connect(self.update_preview); self.actual.textChanged.connect(self.update_preview)
        self.mask.toggled.connect(self.update_preview); self.extra_mask.textChanged.connect(self.update_preview)
        self.evidence_search.textChanged.connect(self.restart_evidence_search)
        self.evidence_search.returnPressed.connect(self.find_in_evidence)
        self.evidence_match_case.toggled.connect(self.restart_evidence_search)
        self.evidence_search_previous_shortcut = QShortcut(QKeySequence("Shift+Return"), self.evidence_search)
        self.evidence_search_previous_shortcut.setContext(Qt.WidgetShortcut)
        self.evidence_search_previous_shortcut.activated.connect(lambda: self.find_in_evidence(backward=True))
        return page

    def _analysis_page(self):
        page = QWidget(); root = QVBoxLayout(page); root.setContentsMargins(0, 0, 0, 0)
        note = QLabel("Auto defect analysis, error fingerprints, and duplicate detection for the current filtered logs."); note.setObjectName("muted")
        settings_row = QHBoxLayout()
        settings_row.addWidget(QLabel("Slow threshold (ms)"))
        self.slow_threshold = QLineEdit(str(self.slow_threshold_ms)); self.slow_threshold.setMaximumWidth(110)
        settings_row.addWidget(self.slow_threshold)
        settings_row.addWidget(QLabel("Success result codes"))
        self.success_codes = QLineEdit(",".join(self.success_result_codes)); self.success_codes.setPlaceholderText("0,20000,SUCCESS")
        settings_row.addWidget(self.success_codes, 1)
        settings_row.addWidget(button("Apply", self.apply_analysis_settings))
        self.analysis = QPlainTextEdit(); self.analysis.setReadOnly(True)
        self.analysis_alert = QLabel(); self.analysis_alert.setObjectName("errorText"); self.analysis_alert.hide()
        root.addWidget(note); root.addLayout(settings_row); root.addWidget(self.analysis_alert); root.addWidget(panel_with_widget(self.analysis), 1)
        return page

    def _connect_filters(self):
        for edit in (self.search, self.min_ms, self.page_filter, self.topic, self.transaction): edit.textChanged.connect(self.refresh)
        self.method.currentTextChanged.connect(self.refresh); self.status.currentTextChanged.connect(self.refresh)
        self.errors_only.toggled.connect(self.refresh); self.business_errors_only.toggled.connect(self.refresh); self.slow_only.toggled.connect(self.refresh)

    def _apply_theme(self):
        QApplication.instance().setStyleSheet(stylesheet(self.theme_mode))
        self.theme_button.setText("Dark mode" if self.theme_mode == "light" else "Light mode")

    def toggle_theme(self):
        self.theme_mode = "light" if self.theme_mode == "dark" else "dark"
        self.settings.setValue("theme", self.theme_mode)
        self._apply_theme()

    def toggle_filters(self):
        expanded = self.filter_content.isHidden()
        self.filter_content.setVisible(expanded)
        self.filter_toggle.setText("Hide filters ▲" if expanded else "Show filters ▼")
        self.settings.setValue("filters_expanded", expanded)

    def _update_grouping_options(self):
        self.custom_group_name.setVisible(self.export_group.currentData() == "custom")

    def _navigate(self, index):
        titles = ("Dashboard", "Transactions", "Evidence", "Analysis")
        subtitles = ("Inspect logs, isolate failures, and build shareable evidence.", "Follow related API calls across a transaction journey.", "Write expected/actual results and review the exact export.", "Find repeated failure signatures in the current result set.")
        self.pages.setCurrentIndex(index); self.page_title.setText(titles[index]); self.page_subtitle.setText(subtitles[index])
        for i, nav in enumerate(self.nav_buttons): nav.setChecked(i == index)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.sidebar.setFixedWidth(76 if self.width() < 1050 else 220)
        for nav in self.nav_buttons:
            full = nav.property("fullText") or nav.text(); nav.setProperty("fullText", full)
            nav.setText(full[:1] if self.width() < 1050 else full)

    def import_file(self):
        paths, _ = QFileDialog.getOpenFileNames(self, "Import logs", "", "JSON / HAR (*.json *.har);;All files (*)")
        if not paths: return
        try:
            result = parse_files(paths)
            if not result.entries: raise ValueError("No usable log records were found.")
            self.entries = result.entries; self._configure_entries(); self.included_indexes.clear(); self.refresh()
            source_name = Path(paths[0]).name if len(paths) == 1 else f"{len(paths)} files"
            self._show_import_report(result.report, source_name)
        except Exception as exc: QMessageBox.critical(self, "Import failed", str(exc))

    def paste_json(self):
        dialog = PasteDialog(self)
        if dialog.exec() != QDialog.Accepted: return
        try:
            result = parse_with_report(dialog.editor.toPlainText().strip())
            if not result.entries: raise ValueError("No usable log records were found.")
            self.entries = result.entries; self._configure_entries(); self.included_indexes.clear(); self.refresh()
            self._show_import_report(result.report, "pasted JSON")
        except Exception as exc: QMessageBox.critical(self, "Invalid input", str(exc))

    def _show_import_report(self, report, source_name):
        summary = f"Imported {report.imported_count} of {report.source_count} logs from {source_name}"
        if report.skipped_count:
            summary += f" · {report.skipped_count} skipped"
        if report.warning_count:
            summary += f" · {report.warning_count} warnings"
        self.status_label.setText(summary)
        self.status_label.setObjectName("alert" if report.skipped_count or report.warning_count else "muted")
        self.status_label.style().unpolish(self.status_label); self.status_label.style().polish(self.status_label)
        if not report.skipped_count and not report.warning_count:
            return
        details = [summary, ""]
        if len(report.file_reports) > 1:
            details.append("Files:")
            details.extend(
                f"• {item.source_name}: {item.imported_count}/{item.source_count} imported, {item.skipped_count} skipped"
                for item in report.file_reports
            )
            details.append("")
        if report.invalid_timestamp_count:
            details.append(f"• {report.invalid_timestamp_count} timestamp(s) missing or unreadable")
        if report.missing_endpoint_count:
            details.append(f"• {report.missing_endpoint_count} endpoint(s) missing")
        categories = {}
        for issue in report.issues:
            if issue.category in {"invalid_timestamp", "missing_endpoint"}:
                continue
            categories[issue.message] = categories.get(issue.message, 0) + 1
        details.extend(f"• {count} record(s): {message}" for message, count in categories.items())
        QMessageBox.warning(self, "Import completed with warnings", "\n".join(details))

    def clear_all(self):
        self.entries = []
        self.filtered = []
        self.included_indexes.clear()
        self.expected.clear()
        self.actual.clear()
        self.reset_filters()
        self.status_label.setText("Cleared — import JSON or HAR to begin")

    def clear_search_filter(self): self.search.clear()
    def clear_request_filters(self): self.method.setCurrentText("ALL"); self.status.setCurrentText("ALL")
    def clear_result_filters(self): self.errors_only.setChecked(False); self.business_errors_only.setChecked(False)
    def clear_performance_filters(self): self.min_ms.clear(); self.slow_only.setChecked(False)
    def clear_context_filters(self): self.page_filter.clear(); self.topic.clear(); self.transaction.clear()

    def apply_filter_preset(self):
        preset = self.filter_preset.currentText()
        if preset == "Choose preset…": return
        transaction_id = ""
        if preset == "Current Transaction":
            selected = self.selected_filtered_entries()
            transaction_id = selected[0].transaction_id if selected else self.transaction.text().strip()
            if not transaction_id:
                QMessageBox.information(self, "Transaction unavailable", "Select a Timeline row with a Transaction ID first.")
                self.filter_preset.setCurrentIndex(0)
                return
        self.reset_filters()
        if preset == "All Errors": self.errors_only.setChecked(True)
        elif preset == "Slow APIs": self.slow_only.setChecked(True)
        elif preset == "Current Transaction": self.transaction.setText(transaction_id)
        self.filter_preset.setCurrentIndex(0)

    def _active_filter_specs(self):
        specs = []
        if self.search.text().strip(): specs.append((f"Search: {self.search.text().strip()}", self.search.clear))
        if self.method.currentText() != "ALL": specs.append((self.method.currentText(), lambda: self.method.setCurrentText("ALL")))
        if self.status.currentText() != "ALL": specs.append((self.status.currentText(), lambda: self.status.setCurrentText("ALL")))
        if self.errors_only.isChecked(): specs.append(("All Errors", lambda: self.errors_only.setChecked(False)))
        if self.business_errors_only.isChecked(): specs.append(("Business Errors", lambda: self.business_errors_only.setChecked(False)))
        if self.min_ms.text().strip(): specs.append((f">= {self.min_ms.text().strip()} ms", self.min_ms.clear))
        if self.slow_only.isChecked(): specs.append(("Slow APIs", lambda: self.slow_only.setChecked(False)))
        if self.page_filter.text().strip(): specs.append((f"Page: {self.page_filter.text().strip()}", self.page_filter.clear))
        if self.topic.text().strip(): specs.append((f"Topic: {self.topic.text().strip()}", self.topic.clear))
        if self.transaction.text().strip(): specs.append((f"Transaction: {self.transaction.text().strip()}", self.transaction.clear))
        return specs

    def update_active_filter_chips(self):
        while self.active_filters_layout.count():
            item = self.active_filters_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        specs = self._active_filter_specs()
        label = QLabel("Active filters" if specs else "No active filters"); label.setObjectName("muted")
        self.active_filters_layout.addWidget(label)
        for text, clear_action in specs:
            chip = button(f"{text}  ×", name="filterChip")
            chip.clicked.connect(lambda checked=False, action=clear_action: action())
            self.active_filters_layout.addWidget(chip)
        self.active_filters_layout.addStretch()
        count = len(specs)
        self.reset_filters_button.setText(f"Reset all filters ({count})" if count else "Reset all filters")

    def reset_filters(self):
        for edit in (self.search, self.min_ms, self.page_filter, self.topic, self.transaction): edit.clear()
        self.method.setCurrentText("ALL"); self.status.setCurrentText("ALL"); self.errors_only.setChecked(False); self.business_errors_only.setChecked(False); self.slow_only.setChecked(False); self.refresh()

    def _configure_entries(self):
        for entry in self.entries:
            entry.slow_threshold_ms = self.slow_threshold_ms
            entry.success_result_codes = self.success_result_codes

    def apply_analysis_settings(self):
        try:
            threshold = float(self.slow_threshold.text().strip())
            if threshold <= 0: raise ValueError
        except ValueError:
            QMessageBox.information(self, "Invalid threshold", "Slow threshold must be a positive number.")
            return
        codes = tuple(code.strip() for code in self.success_codes.text().split(",") if code.strip())
        if not codes:
            QMessageBox.information(self, "Success codes required", "Enter at least one success result code.")
            return
        self.slow_threshold_ms = threshold; self.success_result_codes = codes
        self.settings.setValue("slow_threshold_ms", threshold)
        self.settings.setValue("success_result_codes", ",".join(codes))
        self._configure_entries(); self.refresh()
        self.status_label.setText(f"Analysis settings applied · Slow >= {threshold:g} ms")

    def refresh(self):
        self.filtered = filter_entries(self.entries, search=self.search.text(), errors_only=self.errors_only.isChecked(), business_errors_only=self.business_errors_only.isChecked(), slow_only=self.slow_only.isChecked(), method=self.method.currentText(), status_class=self.status.currentText(), min_ms=self.min_ms.text(), page=self.page_filter.text(), topic=self.topic.text(), transaction=self.transaction.text())
        self.update_active_filter_chips()
        self.table.setRowCount(len(self.filtered))
        for row, entry in enumerate(self.filtered):
            values = ("●" if entry.index in self.included_indexes else "○", entry.timestamp_display, entry.severity, error_fingerprint(entry), entry.request_method, entry.request_uri, entry.response_status, entry.response_time, entry.request_id, entry.transaction_id)
            for col, value in enumerate(values):
                item = QTableWidgetItem(str(value)); item.setData(Qt.UserRole, entry.index)
                if col == 0: item.setForeground(QColor("#7c6df2" if entry.index in self.included_indexes else "#62708e"))
                if entry.has_error and col in {2, 3, 6}: item.setForeground(QColor("#ff5c6c"))
                self.table.setItem(row, col, item)
        groups = group_by_transaction(self.filtered); self.tx_table.setRowCount(len(groups))
        for row, (tx, items) in enumerate(groups.items()):
            journey = transaction_journey(items)
            source = "Fallback" if journey["uses_fallback"] else "Transaction"
            values = (tx, len(items), journey["http_errors"], journey["business_errors"], journey["slow_count"], f"{journey['duration_ms']:.0f} ms", source)
            for col, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                if col in {2, 3} and int(value): item.setForeground(QColor("#ff5c6c"))
                self.tx_table.setItem(row, col, item)
        success = sum(1 for x in self.entries if not x.has_error)
        for key, value in (("total", len(self.entries)), ("success", success), ("errors", sum(x.has_error for x in self.entries)), ("slow", sum(x.is_slow for x in self.entries)), ("included", len(self.included_indexes))): self.metrics[key].setText(str(value))
        self.result_count.setText(f"{len(self.filtered)} results"); self.status_label.setText(f"Showing {len(self.filtered)} / {len(self.entries)} logs  •  Included {len(self.included_indexes)}  •  Sensitive data {'masked' if self.mask.isChecked() else 'visible'}")
        if self.status_label.objectName() != "muted":
            self.status_label.setObjectName("muted"); self.status_label.style().unpolish(self.status_label); self.status_label.style().polish(self.status_label)
        self.update_preview(); self.update_analysis()

    def selected_filtered_entries(self): return [self.filtered[i.row()] for i in self.table.selectionModel().selectedRows()]
    def included_entries(self): return [e for e in self.entries if e.index in self.included_indexes]

    def include_selected(self):
        selected = self.selected_filtered_entries()
        if not selected: QMessageBox.information(self, "No rows selected", "Select one or more Timeline rows first."); return
        self.included_indexes.update(e.index for e in selected); self.refresh()

    def exclude_selected(self):
        selected = self.selected_filtered_entries()
        if not selected: QMessageBox.information(self, "No rows selected", "Select one or more Timeline rows first."); return
        self.included_indexes.difference_update(e.index for e in selected); self.refresh()

    def include_all_filtered(self): self.included_indexes.update(e.index for e in self.filtered); self.refresh()
    def clear_included(self): self.included_indexes.clear(); self.refresh()
    def toggle_include_from_indicator(self, row, column):
        if column != 0: return
        index = self.filtered[row].index
        self.included_indexes.discard(index) if index in self.included_indexes else self.included_indexes.add(index)
        self.refresh()

    def toggle_include_selected_rows(self):
        selected = self.selected_filtered_entries()
        if not selected and self.table.currentRow() >= 0:
            selected = [self.filtered[self.table.currentRow()]]
        if not selected: return
        indexes = {entry.index for entry in selected}
        if all(index in self.included_indexes for index in indexes):
            self.included_indexes.difference_update(indexes)
        else:
            self.included_indexes.update(indexes)
        self.refresh()

    def apply_transaction_group(self):
        row = self.tx_table.currentRow()
        if row < 0: return
        value = self.tx_table.item(row, 0).text(); self.transaction.setText("" if value == "(no transaction)" else value); self._navigate(0)

    def _selected_transaction_entries(self):
        row = self.tx_table.currentRow()
        if row < 0 or not self.tx_table.item(row, 0): return []
        key = self.tx_table.item(row, 0).text()
        return group_by_transaction(self.filtered).get(key, [])

    def include_transaction_journey(self):
        entries = self._selected_transaction_entries()
        if not entries:
            QMessageBox.information(self, "No transaction selected", "Select a transaction journey first.")
            return
        self.included_indexes.update(entry.index for entry in entries); self.refresh()

    def update_journey_detail(self):
        journey = transaction_journey(self._selected_transaction_entries())
        if not journey: self.journey_detail.clear(); self.journey_alert.hide(); return
        first_error = journey["first_error"]
        slowest = journey["slowest_api"]
        lines = [
            f"First API: {journey['first_api'].request_method} {journey['first_api'].request_uri}",
            f"First Error: {first_error.request_method} {first_error.request_uri}" if first_error else "First Error: -",
            f"Slowest API: {slowest.request_method} {slowest.request_uri} ({slowest.response_time} ms)" if slowest else "Slowest API: -",
            f"Duration: {journey['duration_ms']:.0f} ms",
            "Warning: grouped by Request ID fallback" if journey["uses_fallback"] else "Source: explicit transaction identifier",
            "",
        ]
        for position, entry in enumerate(journey["entries"]):
            arrow = "  " if position == 0 else "→ "
            lines.append(f"{arrow}{entry.request_method or '-'} {entry.request_uri or '-'}  {entry.response_status or '-'}  {entry.response_time or '-'} ms  [{entry.severity}]")
        self.journey_detail.setPlainText("\n".join(lines))
        alert_parts = []
        if journey["http_errors"]: alert_parts.append(f"{journey['http_errors']} HTTP error(s)")
        if journey["business_errors"]: alert_parts.append(f"{journey['business_errors']} business error(s)")
        if journey["uses_fallback"]: alert_parts.append("Request ID fallback grouping")
        self.journey_alert.setText("⚠ " + " · ".join(alert_parts) if alert_parts else "")
        self.journey_alert.setVisible(bool(alert_parts))

    def update_inspector(self):
        selected = self.selected_filtered_entries()
        if not selected: self.inspector.clear(); self.note_editor.clear(); self.inspector_alert.hide(); return
        e = selected[0]
        source = TRANSACTION_SOURCE_LABELS.get(e.transaction_source, e.transaction_source)
        source_detail = f" · {e.transaction_source_field}" if e.transaction_source_field else ""
        self.inspector.setPlainText(f"{e.request_method} {e.request_uri}\nHTTP {e.response_status}  •  {e.response_time} ms\nBusiness Error: {e.business_error_reason or '-'}\nRequest ID: {e.request_id}\nTransaction: {e.transaction_id}\nTransaction Source: {source}{source_detail}\nSource File: {e.source_file or '-'}\nSource Record: {e.source_record_index or '-'}\nPage: {e.page_name}\nPage URL: {e.page_url}\nKafka topic: {e.kafka_topic}\n\nREQUEST HEADERS\n{e.request_header}\n\nREQUEST BODY\n{e.request_body}\n\nRESPONSE BODY\n{e.response_body}")
        alert = ""
        if e.is_error: alert = f"HTTP ERROR {e.response_status}"
        if e.is_business_error: alert += (" · " if alert else "") + f"BUSINESS ERROR: {e.business_error_reason}"
        self.inspector_alert.setText("⚠ " + alert if alert else ""); self.inspector_alert.setVisible(bool(alert))
        self.note_editor.setPlainText(e.note)

    def save_log_note(self):
        selected = self.selected_filtered_entries()
        if not selected:
            QMessageBox.information(self, "No log selected", "Select a Timeline row before saving a note.")
            return
        selected[0].note = self.note_editor.toPlainText().strip()
        self.update_preview()
        self.status_label.setText("Evidence note saved")

    def _extra_mask_keys(self): return [x.strip() for x in self.extra_mask.text().split(",") if x.strip()]

    def _evidence_find_flags(self, backward=False):
        flags = QTextDocument.FindFlags()
        if backward: flags |= QTextDocument.FindBackward
        if self.evidence_match_case.isChecked(): flags |= QTextDocument.FindCaseSensitively
        return flags

    def restart_evidence_search(self):
        cursor = self.preview.textCursor()
        cursor.clearSelection()
        cursor.movePosition(QTextCursor.Start)
        self.preview.setTextCursor(cursor)
        if self.evidence_search.text():
            self.find_in_evidence()
        else:
            self.evidence_search_status.clear()

    def find_in_evidence(self, backward=False):
        query = self.evidence_search.text()
        if not query:
            self.evidence_search_status.clear()
            return
        flags = self._evidence_find_flags(backward)
        found = self.preview.find(query, flags)
        if not found:
            cursor = self.preview.textCursor()
            cursor.movePosition(QTextCursor.End if backward else QTextCursor.Start)
            self.preview.setTextCursor(cursor)
            found = self.preview.find(query, flags)
        self.evidence_search_status.setText("Match" if found else "No matches")

    def update_preview(self):
        self.preview.setPlainText(build_ticket(self.included_entries(), self.mask.isChecked(), self.expected.toPlainText().strip(), self.actual.toPlainText().strip(), self._extra_mask_keys()))
        self.restart_evidence_search()
    def update_analysis(self):
        duplicates = find_duplicate_errors(self.filtered); lines = [build_auto_summary(self.filtered), "", "Duplicate / Similar Error Signatures", "=" * 72]
        if not duplicates: lines.append("No repeated error fingerprints found in current filtered logs.")
        for fingerprint, items in duplicates.items():
            lines.append(f"{fingerprint}: {len(items)} occurrence(s)")
            lines.extend(f"  - {e.timestamp_display} {e.request_method} {e.request_uri} HTTP {e.response_status}" for e in items)
            lines.append("")
        self.analysis.setPlainText("\n".join(lines))
        http_errors = sum(entry.is_error for entry in self.filtered)
        business_errors = sum(entry.is_business_error for entry in self.filtered)
        error_text = []
        if http_errors: error_text.append(f"{http_errors} HTTP error(s)")
        if business_errors: error_text.append(f"{business_errors} business error(s)")
        self.analysis_alert.setText("⚠ " + " · ".join(error_text) if error_text else "")
        self.analysis_alert.setVisible(bool(error_text))

    def _require_included(self):
        entries = self.included_entries()
        if not entries: QMessageBox.information(self, "Nothing included", "Include Timeline rows before copying or exporting evidence.")
        return entries

    def copy_ticket(self):
        entries = self._require_included()
        if entries: QApplication.clipboard().setText(build_ticket(entries, self.mask.isChecked(), self.expected.toPlainText().strip(), self.actual.toPlainText().strip(), self._extra_mask_keys())); self.status_label.setText(f"Copied {len(entries)} logs for ticket")

    def copy_markdown(self):
        entries = self._require_included()
        if entries: QApplication.clipboard().setText(build_markdown(entries, self.mask.isChecked(), self.expected.toPlainText().strip(), self.actual.toPlainText().strip(), self._extra_mask_keys())); self.status_label.setText(f"Copied {len(entries)} logs as Markdown")

    def export(self):
        entries = self._require_included()
        if not entries: return
        if self.raw.isChecked():
            choice = QMessageBox.warning(
                self,
                "Export raw logs?",
                f"{len(entries)} raw log file(s) will be exported without sensitive-data masking.\n\n"
                "They may contain tokens, cookies, personal data, or internal system information.",
                QMessageBox.Cancel | QMessageBox.Yes,
                QMessageBox.Cancel,
            )
            if choice != QMessageBox.Yes: return
        parent = QFileDialog.getExistingDirectory(self, "Choose export folder")
        if not parent: return
        try:
            folder_name = build_export_folder_name(self.export_folder_format.text().strip(), datetime.now())
            self.settings.setValue("export_folder_format", self.export_folder_format.text().strip() or "Log_{date}_{time}")
            destination = Path(parent) / folder_name
            if self.export_group.currentData() == "custom" and not self.custom_group_name.text().strip():
                QMessageBox.information(self, "Folder name required", "Enter a custom folder name before exporting.")
                return
            path = export_package(entries=entries, destination=destination, mask=self.mask.isChecked(), expected=self.expected.toPlainText().strip(), actual=self.actual.toPlainText().strip(), extra_mask_keys=self._extra_mask_keys(), include_summary_txt=self.summary_txt.isChecked(), include_summary_md=self.summary_md.isChecked(), include_raw=self.raw.isChecked(), include_sanitized=self.sanitized.isChecked(), group_by=self.export_group.currentData(), custom_group_name=self.custom_group_name.text().strip(), include_zip=self.include_zip.isChecked())
            QMessageBox.information(self, "Export complete", f"Exported {len(entries)} logs.\n\nCreated:\n{path}")
        except Exception as exc: QMessageBox.critical(self, "Export failed", str(exc))

    def open_help(self): HelpDialog(self).exec()


def panel_with_widget(widget):
    lay = QVBoxLayout(); lay.setContentsMargins(1, 1, 1, 1); lay.addWidget(widget); return panel(lay)


def panel_from_layout(layout):
    frame = QFrame(); frame.setObjectName("panel"); frame.setLayout(layout); return frame


App = MainWindow


def main():
    application = QApplication.instance() or QApplication(sys.argv)
    application.setApplicationName("QA Evidence Builder")
    application.setApplicationDisplayName("QA Evidence Builder")
    application.setApplicationVersion(__version__)
    application.setOrganizationName("Guide Jir")
    application.setWindowIcon(QIcon(str(resource_path("assets/icons/png/icon-256.png"))))
    application.setStyle("Fusion")
    application.setStyleSheet(stylesheet())
    window = MainWindow(); window.show()
    return application.exec()


if __name__ == "__main__":
    raise SystemExit(main())
