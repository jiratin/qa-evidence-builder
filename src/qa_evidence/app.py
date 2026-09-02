"""Modern PySide6 desktop interface for QA Evidence Builder."""

import sys
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QSettings, Qt
from PySide6.QtGui import QColor, QIcon, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QApplication, QCheckBox, QComboBox, QDialog, QFileDialog, QFrame,
    QGridLayout, QHBoxLayout, QHeaderView, QLabel, QLineEdit, QMainWindow,
    QMessageBox, QPlainTextEdit, QPushButton, QScrollArea, QSizePolicy,
    QSplitter, QStackedWidget, QTableWidget, QTableWidgetItem, QTabWidget,
    QVBoxLayout, QWidget,
)

from . import __version__
from .analyzer import build_auto_summary, error_fingerprint, find_duplicate_errors
from .evidence import build_markdown, build_ticket
from .exporter import export_package
from .filtering import filter_entries, group_by_transaction
from .help_dialog import HelpDialog
from .parser import parse_auto, parse_with_report
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
        lay.addWidget(button("Import JSON / HAR", self.import_file))
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
            card_layout = QVBoxLayout()
            cap = QLabel(label)
            cap.setObjectName("cardLabel")
            value = QLabel("0")
            value.setObjectName("metric")
            value.setStyleSheet(f"color: {color};")
            card_layout.addWidget(cap)
            card_layout.addWidget(value)
            card_layout.setContentsMargins(15, 12, 15, 12)
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
        lay = QGridLayout()
        lay.setContentsMargins(12, 10, 12, 10)
        self.search = QLineEdit(); self.search.setPlaceholderText("Search API, request ID…")
        self.method = QComboBox(); self.method.addItems(["ALL", "GET", "POST", "PUT", "PATCH", "DELETE"])
        self.status = QComboBox(); self.status.addItems(["ALL", "2xx", "3xx", "4xx", "5xx", "Other"])
        self.min_ms = QLineEdit(); self.min_ms.setPlaceholderText("Minimum ms")
        self.page_filter = QLineEdit(); self.page_filter.setPlaceholderText("Page")
        self.topic = QLineEdit(); self.topic.setPlaceholderText("Kafka topic")
        self.transaction = QLineEdit(); self.transaction.setPlaceholderText("Transaction ID")
        self.errors_only = QCheckBox("Errors only")
        self.slow_only = QCheckBox("Slow only")
        controls = [self.search, self.method, self.status, self.min_ms, self.page_filter, self.topic, self.transaction]
        for col, widget in enumerate(controls):
            lay.addWidget(widget, 0, col)
        lay.addWidget(self.errors_only, 1, 0)
        lay.addWidget(self.slow_only, 1, 1)
        lay.addWidget(button("Reset filters", self.reset_filters), 1, 6)
        return panel(lay)

    def _timeline_panel(self):
        lay = QVBoxLayout()
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
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Stretch)
        self.table.cellDoubleClicked.connect(self.toggle_include_from_row)
        self.table.itemSelectionChanged.connect(self.update_inspector)
        lay.addWidget(self.table, 1)
        return panel(lay)

    def _inspector_panel(self):
        lay = QVBoxLayout()
        title = QLabel("Log inspector"); title.setObjectName("sectionTitle")
        hint = QLabel("Select a timeline row to inspect its normalized fields and raw payload.")
        hint.setWordWrap(True); hint.setObjectName("muted")
        self.inspector = QPlainTextEdit(); self.inspector.setReadOnly(True)
        lay.addWidget(title); lay.addWidget(hint); lay.addWidget(self.inspector, 1)
        return panel(lay)

    def _transactions_page(self):
        page = QWidget(); root = QVBoxLayout(page); root.setContentsMargins(0, 0, 0, 0)
        info = QLabel("Transaction journeys — double-click a row to apply it to the Dashboard filter."); info.setObjectName("muted")
        root.addWidget(info)
        self.tx_table = QTableWidget(0, 4)
        self.tx_table.setHorizontalHeaderLabels(("Transaction ID", "APIs", "Errors", "Slow"))
        self.tx_table.setSelectionBehavior(QTableWidget.SelectRows); self.tx_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tx_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tx_table.doubleClicked.connect(self.apply_transaction_group)
        root.addWidget(panel_with_widget(self.tx_table), 1)
        return page

    def _evidence_page(self):
        page = QWidget(); root = QHBoxLayout(page); root.setContentsMargins(0, 0, 0, 0)
        left = QVBoxLayout()
        ea = QSplitter(Qt.Horizontal)
        self.expected = QPlainTextEdit(); self.expected.setPlaceholderText("Expected result")
        self.actual = QPlainTextEdit(); self.actual.setPlaceholderText("Actual result")
        ea.addWidget(self.expected); ea.addWidget(self.actual)
        left.addWidget(ea)
        preview_title = QLabel("Included evidence preview"); preview_title.setObjectName("sectionTitle")
        self.preview = QPlainTextEdit(); self.preview.setReadOnly(True)
        left.addWidget(preview_title); left.addWidget(self.preview, 1)
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
        self.raw_warning.setWordWrap(True); self.raw_warning.setObjectName("warning"); self.raw_warning.setVisible(False)
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
        options.addWidget(self.export_group); options.addWidget(self.custom_group_name); options.addWidget(self.include_zip)
        self.export_group.currentIndexChanged.connect(self._update_grouping_options)
        options.addStretch()
        options.addWidget(button("Copy for ticket", self.copy_ticket))
        options.addWidget(button("Copy as Markdown", self.copy_markdown))
        options.addWidget(button("Export evidence", self.export, primary=True))
        root.addWidget(panel(options), 1)
        self.expected.textChanged.connect(self.update_preview); self.actual.textChanged.connect(self.update_preview)
        self.mask.toggled.connect(self.update_preview); self.extra_mask.textChanged.connect(self.update_preview)
        return page

    def _analysis_page(self):
        page = QWidget(); root = QVBoxLayout(page); root.setContentsMargins(0, 0, 0, 0)
        note = QLabel("Auto defect analysis, error fingerprints, and duplicate detection for the current filtered logs."); note.setObjectName("muted")
        self.analysis = QPlainTextEdit(); self.analysis.setReadOnly(True)
        root.addWidget(note); root.addWidget(panel_with_widget(self.analysis), 1)
        return page

    def _connect_filters(self):
        for edit in (self.search, self.min_ms, self.page_filter, self.topic, self.transaction): edit.textChanged.connect(self.refresh)
        self.method.currentTextChanged.connect(self.refresh); self.status.currentTextChanged.connect(self.refresh)
        self.errors_only.toggled.connect(self.refresh); self.slow_only.toggled.connect(self.refresh)

    def _apply_theme(self):
        QApplication.instance().setStyleSheet(stylesheet(self.theme_mode))
        self.theme_button.setText("Dark mode" if self.theme_mode == "light" else "Light mode")

    def toggle_theme(self):
        self.theme_mode = "light" if self.theme_mode == "dark" else "dark"
        self.settings.setValue("theme", self.theme_mode)
        self._apply_theme()

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
        path, _ = QFileDialog.getOpenFileName(self, "Import logs", "", "JSON / HAR (*.json *.har);;All files (*)")
        if not path: return
        try:
            result = parse_with_report(Path(path).read_text(encoding="utf-8"))
            if not result.entries: raise ValueError("No usable log records were found.")
            self.entries = result.entries; self.included_indexes.clear(); self.refresh()
            self._show_import_report(result.report, Path(path).name)
        except Exception as exc: QMessageBox.critical(self, "Import failed", str(exc))

    def paste_json(self):
        dialog = PasteDialog(self)
        if dialog.exec() != QDialog.Accepted: return
        try:
            result = parse_with_report(dialog.editor.toPlainText().strip())
            if not result.entries: raise ValueError("No usable log records were found.")
            self.entries = result.entries; self.included_indexes.clear(); self.refresh()
            self._show_import_report(result.report, "pasted JSON")
        except Exception as exc: QMessageBox.critical(self, "Invalid input", str(exc))

    def _show_import_report(self, report, source_name):
        summary = f"Imported {report.imported_count} of {report.source_count} logs from {source_name}"
        if report.skipped_count:
            summary += f" · {report.skipped_count} skipped"
        if report.warning_count:
            summary += f" · {report.warning_count} warnings"
        self.status_label.setText(summary)
        if not report.skipped_count and not report.warning_count:
            return
        details = [summary, ""]
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

    def reset_filters(self):
        for edit in (self.search, self.min_ms, self.page_filter, self.topic, self.transaction): edit.clear()
        self.method.setCurrentText("ALL"); self.status.setCurrentText("ALL"); self.errors_only.setChecked(False); self.slow_only.setChecked(False); self.refresh()

    def refresh(self):
        self.filtered = filter_entries(self.entries, search=self.search.text(), errors_only=self.errors_only.isChecked(), slow_only=self.slow_only.isChecked(), method=self.method.currentText(), status_class=self.status.currentText(), min_ms=self.min_ms.text(), page=self.page_filter.text(), topic=self.topic.text(), transaction=self.transaction.text())
        self.table.setRowCount(len(self.filtered))
        for row, entry in enumerate(self.filtered):
            values = ("●" if entry.index in self.included_indexes else "○", entry.timestamp_display, entry.severity, error_fingerprint(entry), entry.request_method, entry.request_uri, entry.response_status, entry.response_time, entry.request_id, entry.transaction_id)
            for col, value in enumerate(values):
                item = QTableWidgetItem(str(value)); item.setData(Qt.UserRole, entry.index)
                if col == 0: item.setForeground(QColor("#7c6df2" if entry.index in self.included_indexes else "#62708e"))
                if col == 2 and entry.is_error: item.setForeground(QColor("#ff6b7a"))
                self.table.setItem(row, col, item)
        groups = group_by_transaction(self.filtered); self.tx_table.setRowCount(len(groups))
        for row, (tx, items) in enumerate(groups.items()):
            for col, value in enumerate((tx, len(items), sum(x.is_error for x in items), sum(x.is_slow for x in items))): self.tx_table.setItem(row, col, QTableWidgetItem(str(value)))
        success = sum(1 for x in self.entries if not x.is_error)
        for key, value in (("total", len(self.entries)), ("success", success), ("errors", sum(x.is_error for x in self.entries)), ("slow", sum(x.is_slow for x in self.entries)), ("included", len(self.included_indexes))): self.metrics[key].setText(str(value))
        self.result_count.setText(f"{len(self.filtered)} results"); self.status_label.setText(f"Showing {len(self.filtered)} / {len(self.entries)} logs  •  Included {len(self.included_indexes)}  •  Sensitive data {'masked' if self.mask.isChecked() else 'visible'}")
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
    def toggle_include_from_row(self, row, _column):
        index = self.filtered[row].index
        self.included_indexes.discard(index) if index in self.included_indexes else self.included_indexes.add(index)
        self.refresh()

    def apply_transaction_group(self):
        row = self.tx_table.currentRow()
        if row < 0: return
        value = self.tx_table.item(row, 0).text(); self.transaction.setText("" if value == "(no transaction)" else value); self._navigate(0)

    def update_inspector(self):
        selected = self.selected_filtered_entries()
        if not selected: self.inspector.clear(); return
        e = selected[0]
        source = TRANSACTION_SOURCE_LABELS.get(e.transaction_source, e.transaction_source)
        source_detail = f" · {e.transaction_source_field}" if e.transaction_source_field else ""
        self.inspector.setPlainText(f"{e.request_method} {e.request_uri}\nHTTP {e.response_status}  •  {e.response_time} ms\nRequest ID: {e.request_id}\nTransaction: {e.transaction_id}\nTransaction Source: {source}{source_detail}\nPage: {e.page_name}\nPage URL: {e.page_url}\nKafka topic: {e.kafka_topic}\n\nREQUEST HEADERS\n{e.request_header}\n\nREQUEST BODY\n{e.request_body}\n\nRESPONSE BODY\n{e.response_body}")

    def _extra_mask_keys(self): return [x.strip() for x in self.extra_mask.text().split(",") if x.strip()]
    def update_preview(self): self.preview.setPlainText(build_ticket(self.included_entries(), self.mask.isChecked(), self.expected.toPlainText().strip(), self.actual.toPlainText().strip(), self._extra_mask_keys()))
    def update_analysis(self):
        duplicates = find_duplicate_errors(self.filtered); lines = [build_auto_summary(self.filtered), "", "Duplicate / Similar Error Signatures", "=" * 72]
        if not duplicates: lines.append("No repeated error fingerprints found in current filtered logs.")
        for fingerprint, items in duplicates.items():
            lines.append(f"{fingerprint}: {len(items)} occurrence(s)")
            lines.extend(f"  - {e.timestamp_display} {e.request_method} {e.request_uri} HTTP {e.response_status}" for e in items)
            lines.append("")
        self.analysis.setPlainText("\n".join(lines))

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
        destination = Path(parent) / ("QA_Evidence_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
        try:
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
