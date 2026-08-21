from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText

from .parser import parse_auto
from .filtering import filter_entries, group_by_transaction
from .evidence import build_ticket, build_markdown
from .exporter import export_package
from .help_dialog import HelpDialog
from .analyzer import (
    error_fingerprint,
    find_duplicate_errors,
    build_auto_summary,
)

class ScrollableSidebar(ttk.Frame):
    def __init__(self, master, width=300):
        super().__init__(master)
        self.canvas = tk.Canvas(
            self,
            width=width,
            highlightthickness=0,
            borderwidth=0,
        )
        self.scrollbar = ttk.Scrollbar(
            self,
            orient="vertical",
            command=self.canvas.yview,
        )
        self.inner = ttk.Frame(self.canvas)

        self.inner.bind(
            "<Configure>",
            lambda _event: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            ),
        )

        self.window_id = self.canvas.create_window(
            (0, 0),
            window=self.inner,
            anchor="nw",
        )

        self.canvas.configure(
            yscrollcommand=self.scrollbar.set
        )

        self.canvas.bind(
            "<Configure>",
            self._resize_inner,
        )

        self.canvas.pack(
            side="left",
            fill="both",
            expand=True,
        )

        self.scrollbar.pack(
            side="right",
            fill="y",
        )

        self.canvas.bind_all(
            "<MouseWheel>",
            self._on_mousewheel,
            add="+",
        )

    def _resize_inner(self, event):
        self.canvas.itemconfigure(
            self.window_id,
            width=max(event.width, 250),
        )

    def _on_mousewheel(self, event):
        if self.winfo_containing(
            self.winfo_pointerx(),
            self.winfo_pointery(),
        ) in self._descendants():
            delta = -1 if event.delta > 0 else 1
            self.canvas.yview_scroll(delta, "units")

    def _descendants(self):
        widgets = {self, self.canvas, self.inner}
        stack = list(self.inner.winfo_children())
        while stack:
            widget = stack.pop()
            widgets.add(widget)
            stack.extend(widget.winfo_children())
        return widgets

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("QA Evidence Builder — V3.1.1 0.3.1.1")
        self.geometry("1360x820")
        self.minsize(840, 560)

        self.entries = []
        self.filtered = []
        self.included_indexes = set()

        self.search_var = tk.StringVar()
        self.error_only_var = tk.BooleanVar(value=False)
        self.slow_only_var = tk.BooleanVar(value=False)
        self.mask_var = tk.BooleanVar(value=True)
        self.method_var = tk.StringVar(value="ALL")
        self.status_var = tk.StringVar(value="ALL")
        self.min_ms_var = tk.StringVar()
        self.page_var = tk.StringVar()
        self.topic_var = tk.StringVar()
        self.transaction_var = tk.StringVar()
        self.extra_mask_var = tk.StringVar()

        self.export_summary_txt_var = tk.BooleanVar(value=True)
        self.export_summary_md_var = tk.BooleanVar(value=True)
        self.export_raw_var = tk.BooleanVar(value=False)
        self.export_sanitized_var = tk.BooleanVar(value=True)

        self._build()
        self._build_menu()

    def _build_menu(self):
        menu_bar = tk.Menu(self)

        help_menu = tk.Menu(
            menu_bar,
            tearoff=0,
        )
        help_menu.add_command(
            label="User Guide",
            command=self.open_help,
        )
        help_menu.add_separator()
        help_menu.add_command(
            label="About",
            command=self.show_about,
        )

        menu_bar.add_cascade(
            label="Help",
            menu=help_menu,
        )

        self.config(menu=menu_bar)

    def show_about(self):
        messagebox.showinfo(
            "About QA Evidence Builder",
            (
                "QA Evidence Builder\n"
                "Version 1.0.0\n\n"
                "Local-only QA log analysis and evidence tool."
            ),
        )

    def _build(self):
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        sidebar = ScrollableSidebar(self, width=310)
        sidebar.grid(
            row=0,
            column=0,
            sticky="nsew",
        )

        main = ttk.Frame(self, padding=(8, 8, 8, 8))
        main.grid(
            row=0,
            column=1,
            sticky="nsew",
        )
        main.columnconfigure(0, weight=1)
        main.rowconfigure(1, weight=1)

        self._build_sidebar(sidebar.inner)
        self._build_main(main)

    def _section(self, parent, title):
        frame = ttk.LabelFrame(
            parent,
            text=title,
            padding=8,
        )
        frame.pack(
            fill="x",
            padx=8,
            pady=(8, 0),
        )
        return frame

    def _large_checkbutton(
        self,
        parent,
        text,
        variable,
        command=None,
    ):
        """Large checkbox row with a bigger click target."""
        return tk.Checkbutton(
            parent,
            text=text,
            variable=variable,
            command=command,
            anchor="w",
            justify="left",
            font=("TkDefaultFont", 12),
            padx=10,
            pady=8,
            borderwidth=0,
            highlightthickness=0,
            cursor="hand2",
        )

    def _build_sidebar(self, parent):
        source = self._section(parent, "Source")

        ttk.Button(
            source,
            text="Import JSON / HAR",
            command=self.import_file,
        ).pack(fill="x")

        ttk.Button(
            source,
            text="Paste JSON",
            command=self.paste_json,
        ).pack(fill="x", pady=(6, 0))

        ttk.Button(
            source,
            text="Clear",
            command=self.clear_all,
        ).pack(fill="x", pady=(6, 0))

        filters = self._section(parent, "Filters")

        for label, var in [
            ("Search API / ID", self.search_var),
            ("Minimum response ms", self.min_ms_var),
            ("Page", self.page_var),
            ("Kafka Topic", self.topic_var),
            ("Transaction ID", self.transaction_var),
        ]:
            ttk.Label(filters, text=label).pack(
                anchor="w",
                pady=(4, 0),
            )
            ttk.Entry(
                filters,
                textvariable=var,
            ).pack(fill="x")

        ttk.Label(
            filters,
            text="HTTP Method",
        ).pack(anchor="w", pady=(4, 0))

        ttk.Combobox(
            filters,
            textvariable=self.method_var,
            values=[
                "ALL", "GET", "POST",
                "PUT", "PATCH", "DELETE",
            ],
            state="readonly",
        ).pack(fill="x")

        ttk.Label(
            filters,
            text="HTTP Status",
        ).pack(anchor="w", pady=(4, 0))

        ttk.Combobox(
            filters,
            textvariable=self.status_var,
            values=[
                "ALL", "2xx", "3xx",
                "4xx", "5xx", "Other",
            ],
            state="readonly",
        ).pack(fill="x")

        self._large_checkbutton(
            filters,
            text="Errors only",
            variable=self.error_only_var,
            command=self.refresh,
        ).pack(fill="x", pady=(4, 0))

        self._large_checkbutton(
            filters,
            text="Slow only",
            variable=self.slow_only_var,
            command=self.refresh,
        ).pack(fill="x")

        ttk.Button(
            filters,
            text="Reset Filters",
            command=self.reset_filters,
        ).pack(fill="x", pady=(6, 0))

        selection = self._section(
            parent,
            "Export Selection",
        )

        ttk.Label(
            selection,
            text=(
                "เลือก row ใน Timeline ก่อน แล้วใช้ปุ่มด้านล่าง\n"
                "ไฟล์ที่ Include เท่านั้นที่จะถูก Export"
            ),
            wraplength=260,
        ).pack(anchor="w")

        ttk.Button(
            selection,
            text="Include Selected",
            command=self.include_selected,
        ).pack(fill="x", pady=(6, 0))

        ttk.Button(
            selection,
            text="Exclude Selected",
            command=self.exclude_selected,
        ).pack(fill="x", pady=(4, 0))

        bulk_row = ttk.Frame(selection)
        bulk_row.pack(fill="x", pady=(8, 0))
        bulk_row.columnconfigure(0, weight=1)
        bulk_row.columnconfigure(1, weight=1)

        ttk.Button(
            bulk_row,
            text="Select All",
            command=self.include_all_filtered,
        ).grid(
            row=0,
            column=0,
            sticky="ew",
            padx=(0, 3),
        )

        ttk.Button(
            bulk_row,
            text="Deselect All",
            command=self.clear_included,
        ).grid(
            row=0,
            column=1,
            sticky="ew",
            padx=(3, 0),
        )

        ttk.Label(
            selection,
            text=(
                "Select All: เลือกทุก log ที่ผ่าน Filter ปัจจุบัน\n"
                "Deselect All: ยกเลิก Included ทั้งหมด"
            ),
            wraplength=260,
        ).pack(anchor="w", pady=(6, 0))

        self.included_label = ttk.Label(
            selection,
            text="Included: 0",
        )
        self.included_label.pack(
            anchor="w",
            pady=(6, 0),
        )

        evidence = self._section(
            parent,
            "Evidence Options",
        )

        self._large_checkbutton(
            evidence,
            text="Mask sensitive data",
            variable=self.mask_var,
            command=self.update_preview,
        ).pack(fill="x")

        ttk.Label(
            evidence,
            text="Extra mask keys (comma separated)",
        ).pack(anchor="w", pady=(4, 0))

        ttk.Entry(
            evidence,
            textvariable=self.extra_mask_var,
        ).pack(fill="x")

        export_content = self._section(
            parent,
            "Package Contents",
        )

        self._large_checkbutton(
            export_content,
            text="summary.txt",
            variable=self.export_summary_txt_var,
        ).pack(fill="x")

        self._large_checkbutton(
            export_content,
            text="summary.md",
            variable=self.export_summary_md_var,
        ).pack(fill="x")

        self._large_checkbutton(
            export_content,
            text="Raw log files",
            variable=self.export_raw_var,
        ).pack(fill="x")

        self._large_checkbutton(
            export_content,
            text="Sanitized log files",
            variable=self.export_sanitized_var,
        ).pack(fill="x")

        actions = self._section(
            parent,
            "Actions",
        )

        ttk.Button(
            actions,
            text="Copy Included for Ticket",
            command=self.copy_ticket,
        ).pack(fill="x")

        ttk.Button(
            actions,
            text="Copy Included as Markdown",
            command=self.copy_markdown,
        ).pack(fill="x", pady=(4, 0))

        ttk.Button(
            actions,
            text="Export Included Evidence",
            command=self.export,
        ).pack(fill="x", pady=(4, 0))

        footer_tools = ttk.Frame(parent)
        footer_tools.pack(
            fill="x",
            padx=8,
            pady=(14, 10),
        )

        ttk.Button(
            footer_tools,
            text="Help / User Guide",
            command=self.open_help,
        ).pack(
            fill="x",
            ipady=5,
        )

        ttk.Label(
            footer_tools,
            text="QA Evidence Builder v1.0",
            anchor="center",
        ).pack(
            fill="x",
            pady=(8, 0),
        )

        for var in [
            self.search_var,
            self.method_var,
            self.status_var,
            self.min_ms_var,
            self.page_var,
            self.topic_var,
            self.transaction_var,
        ]:
            var.trace_add(
                "write",
                lambda *_: self.refresh(),
            )

        self.extra_mask_var.trace_add(
            "write",
            lambda *_: self.update_preview(),
        )

    def _build_main(self, main):
        header = ttk.Frame(main)
        header.grid(
            row=0,
            column=0,
            sticky="ew",
            pady=(0, 8),
        )
        header.columnconfigure(1, weight=1)

        ttk.Label(
            header,
            text="QA Evidence Builder",
            font=("TkDefaultFont", 16, "bold"),
        ).grid(row=0, column=0, sticky="w")

        self.status = ttk.Label(
            header,
            text="Import JSON Array or HAR to begin.",
        )
        self.status.grid(
            row=0,
            column=1,
            sticky="e",
        )

        notebook = ttk.Notebook(main)
        notebook.grid(
            row=1,
            column=0,
            sticky="nsew",
        )

        timeline_tab = ttk.Frame(notebook)
        transactions_tab = ttk.Frame(notebook)
        evidence_tab = ttk.Frame(notebook)
        analysis_tab = ttk.Frame(notebook)

        notebook.add(
            timeline_tab,
            text="Timeline",
        )
        notebook.add(
            transactions_tab,
            text="Transactions",
        )
        notebook.add(
            evidence_tab,
            text="Evidence",
        )
        notebook.add(
            analysis_tab,
            text="Analysis",
        )

        self._build_timeline(timeline_tab)
        self._build_transactions(transactions_tab)
        self._build_evidence(evidence_tab)
        self._build_analysis(analysis_tab)

    def _build_timeline(self, parent):
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)

        columns = (
            "include",
            "time",
            "severity",
            "fingerprint",
            "method",
            "api",
            "status",
            "ms",
            "request_id",
            "transaction",
        )

        self.tree = ttk.Treeview(
            parent,
            columns=columns,
            show="headings",
            selectmode="extended",
        )

        definitions = [
            ("include", "Export", 60),
            ("time", "Timestamp", 155),
            ("severity", "Flag", 65),
            ("fingerprint", "Fingerprint", 95),
            ("method", "Method", 65),
            ("api", "API", 300),
            ("status", "Status", 60),
            ("ms", "ms", 70),
            ("request_id", "Request ID", 160),
            ("transaction", "Transaction", 180),
        ]

        for column, title, width in definitions:
            self.tree.heading(column, text=title)
            self.tree.column(
                column,
                width=width,
                minwidth=50,
                anchor="w",
                stretch=(column == "api"),
            )

        xscroll = ttk.Scrollbar(
            parent,
            orient="horizontal",
            command=self.tree.xview,
        )
        yscroll = ttk.Scrollbar(
            parent,
            orient="vertical",
            command=self.tree.yview,
        )

        self.tree.configure(
            xscrollcommand=xscroll.set,
            yscrollcommand=yscroll.set,
        )

        self.tree.grid(
            row=0,
            column=0,
            sticky="nsew",
        )
        yscroll.grid(
            row=0,
            column=1,
            sticky="ns",
        )
        xscroll.grid(
            row=1,
            column=0,
            sticky="ew",
        )

        self.tree.bind(
            "<Double-1>",
            self.toggle_include_from_row,
        )

    def _build_transactions(self, parent):
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)

        tx_columns = (
            "transaction",
            "count",
            "errors",
            "slow",
        )

        self.tx_tree = ttk.Treeview(
            parent,
            columns=tx_columns,
            show="headings",
            selectmode="browse",
        )

        for column, title, width in [
            ("transaction", "Transaction ID", 420),
            ("count", "APIs", 80),
            ("errors", "Errors", 80),
            ("slow", "Slow", 80),
        ]:
            self.tx_tree.heading(
                column,
                text=title,
            )
            self.tx_tree.column(
                column,
                width=width,
                anchor="w",
            )

        self.tx_tree.grid(
            row=0,
            column=0,
            sticky="nsew",
        )

        ttk.Label(
            parent,
            text="Double-click a transaction to apply it as a filter.",
        ).grid(
            row=1,
            column=0,
            sticky="w",
            pady=6,
        )

        self.tx_tree.bind(
            "<Double-1>",
            self.apply_transaction_group,
        )

    def _build_evidence(self, parent):
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(2, weight=1)

        expected_actual = ttk.Panedwindow(
            parent,
            orient="horizontal",
        )
        expected_actual.grid(
            row=0,
            column=0,
            sticky="ew",
            pady=(0, 8),
        )

        expected_frame = ttk.LabelFrame(
            expected_actual,
            text="Expected Result",
            padding=6,
        )
        actual_frame = ttk.LabelFrame(
            expected_actual,
            text="Actual Result",
            padding=6,
        )

        expected_actual.add(
            expected_frame,
            weight=1,
        )
        expected_actual.add(
            actual_frame,
            weight=1,
        )

        self.expected = tk.Text(
            expected_frame,
            height=5,
            wrap="word",
        )
        self.expected.pack(
            fill="both",
            expand=True,
        )

        self.actual = tk.Text(
            actual_frame,
            height=5,
            wrap="word",
        )
        self.actual.pack(
            fill="both",
            expand=True,
        )

        self.expected.bind(
            "<KeyRelease>",
            lambda _event: self.update_preview(),
        )
        self.actual.bind(
            "<KeyRelease>",
            lambda _event: self.update_preview(),
        )

        ttk.Label(
            parent,
            text="Included Evidence Preview",
        ).grid(
            row=1,
            column=0,
            sticky="w",
        )

        self.preview = ScrolledText(
            parent,
            wrap="word",
            font=("Menlo", 10),
        )
        self.preview.grid(
            row=2,
            column=0,
            sticky="nsew",
            pady=(4, 0),
        )

    def _build_analysis(self, parent):
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)

        ttk.Label(
            parent,
            text="Auto Defect Analysis",
        ).grid(
            row=0,
            column=0,
            sticky="w",
            pady=(0, 4),
        )

        self.analysis_text = ScrolledText(
            parent,
            wrap="word",
            font=("Menlo", 10),
        )
        self.analysis_text.grid(
            row=1,
            column=0,
            sticky="nsew",
        )

    def open_help(self):
        HelpDialog(self)

    def _read_expected_actual(self):
        return (
            self.expected.get("1.0", "end").strip(),
            self.actual.get("1.0", "end").strip(),
        )

    def _extra_mask_keys(self):
        return [
            item.strip()
            for item in self.extra_mask_var.get().split(",")
            if item.strip()
        ]

    def import_file(self):
        path = filedialog.askopenfilename(
            filetypes=[
                ("JSON / HAR", "*.json *.har"),
                ("JSON files", "*.json"),
                ("HAR files", "*.har"),
                ("All files", "*.*"),
            ]
        )

        if not path:
            return

        try:
            payload = Path(path).read_text(
                encoding="utf-8"
            )
            self.entries = parse_auto(payload)
            self.included_indexes.clear()
            self.refresh()
        except Exception as exc:
            messagebox.showerror(
                "Import failed",
                str(exc),
            )

    def paste_json(self):
        win = tk.Toplevel(self)
        win.title("Paste JSON Array / HAR JSON")
        win.geometry("850x560")
        win.minsize(600, 400)

        text = ScrolledText(
            win,
            wrap="none",
            font=("Menlo", 10),
        )
        text.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10,
        )

        button_frame = ttk.Frame(win)
        button_frame.pack(
            fill="x",
            padx=10,
            pady=(0, 10),
        )

        def load():
            try:
                self.entries = parse_auto(
                    text.get("1.0", "end").strip()
                )
                self.included_indexes.clear()
                win.destroy()
                self.refresh()
            except Exception as exc:
                messagebox.showerror(
                    "Invalid input",
                    str(exc),
                    parent=win,
                )

        ttk.Button(
            button_frame,
            text="Load Logs",
            command=load,
        ).pack(side="right")

    def clear_all(self):
        self.entries = []
        self.filtered = []
        self.included_indexes.clear()
        self.expected.delete("1.0", "end")
        self.actual.delete("1.0", "end")
        self.reset_filters()

    def reset_filters(self):
        self.search_var.set("")
        self.error_only_var.set(False)
        self.slow_only_var.set(False)
        self.method_var.set("ALL")
        self.status_var.set("ALL")
        self.min_ms_var.set("")
        self.page_var.set("")
        self.topic_var.set("")
        self.transaction_var.set("")
        self.refresh()

    def refresh(self):
        self.filtered = filter_entries(
            self.entries,
            search=self.search_var.get(),
            errors_only=self.error_only_var.get(),
            slow_only=self.slow_only_var.get(),
            method=self.method_var.get(),
            status_class=self.status_var.get(),
            min_ms=self.min_ms_var.get(),
            page=self.page_var.get(),
            topic=self.topic_var.get(),
            transaction=self.transaction_var.get(),
        )

        for item in self.tree.get_children():
            self.tree.delete(item)

        for display_index, entry in enumerate(self.filtered):
            included = (
                "☑"
                if entry.index in self.included_indexes
                else "☐"
            )

            self.tree.insert(
                "",
                "end",
                iid=str(display_index),
                values=(
                    included,
                    entry.timestamp_display,
                    entry.severity,
                    error_fingerprint(entry),
                    entry.request_method,
                    entry.request_uri,
                    entry.response_status,
                    entry.response_time,
                    entry.request_id,
                    entry.transaction_id,
                ),
            )

        for item in self.tx_tree.get_children():
            self.tx_tree.delete(item)

        groups = group_by_transaction(self.filtered)

        for i, (transaction_id, items) in enumerate(groups.items()):
            self.tx_tree.insert(
                "",
                "end",
                iid=f"tx{i}",
                values=(
                    transaction_id,
                    len(items),
                    sum(
                        1
                        for entry in items
                        if entry.is_error
                    ),
                    sum(
                        1
                        for entry in items
                        if entry.is_slow
                    ),
                ),
            )

        self._update_counts()
        self.update_preview()
        self.update_analysis()

    def _update_counts(self):
        self.included_label.config(
            text=f"Included: {len(self.included_indexes)}"
        )
        self.status.config(
            text=(
                f"Showing {len(self.filtered)} / "
                f"{len(self.entries)} logs • "
                f"Included {len(self.included_indexes)}"
            )
        )

    def selected_filtered_entries(self):
        ids = self.tree.selection()
        return [
            self.filtered[int(item_id)]
            for item_id in ids
        ]

    def included_entries(self):
        return [
            entry
            for entry in self.entries
            if entry.index in self.included_indexes
        ]

    def include_selected(self):
        selected = self.selected_filtered_entries()
        if not selected:
            messagebox.showinfo(
                "No rows selected",
                "Select one or more rows in Timeline first.",
            )
            return

        for entry in selected:
            self.included_indexes.add(entry.index)

        self.refresh()

    def exclude_selected(self):
        selected = self.selected_filtered_entries()
        if not selected:
            messagebox.showinfo(
                "No rows selected",
                "Select one or more rows in Timeline first.",
            )
            return

        for entry in selected:
            self.included_indexes.discard(entry.index)

        self.refresh()

    def include_all_filtered(self):
        for entry in self.filtered:
            self.included_indexes.add(entry.index)
        self.refresh()

    def clear_included(self):
        self.included_indexes.clear()
        self.refresh()

    def toggle_include_from_row(self, event):
        row_id = self.tree.identify_row(event.y)
        if not row_id:
            return

        entry = self.filtered[int(row_id)]

        if entry.index in self.included_indexes:
            self.included_indexes.discard(entry.index)
        else:
            self.included_indexes.add(entry.index)

        self.refresh()

    def apply_transaction_group(self, _event=None):
        selection = self.tx_tree.selection()
        if not selection:
            return

        values = self.tx_tree.item(
            selection[0],
            "values",
        )

        if not values:
            return

        transaction_id = values[0]

        self.transaction_var.set(
            ""
            if transaction_id == "(no transaction)"
            else transaction_id
        )

    def update_preview(self):
        expected, actual = self._read_expected_actual()
        entries = self.included_entries()

        self.preview.delete("1.0", "end")
        self.preview.insert(
            "1.0",
            build_ticket(
                entries,
                self.mask_var.get(),
                expected,
                actual,
                self._extra_mask_keys(),
            ),
        )

    def update_analysis(self):
        duplicate_groups = find_duplicate_errors(
            self.filtered
        )

        lines = [
            build_auto_summary(self.filtered),
            "",
            "Duplicate / Similar Error Signatures",
            "=" * 72,
        ]

        if not duplicate_groups:
            lines.append(
                "No repeated error fingerprints found in current filtered logs."
            )
        else:
            for fingerprint, items in duplicate_groups.items():
                lines.append(
                    f"{fingerprint}: {len(items)} occurrence(s)"
                )

                for entry in items:
                    lines.append(
                        f"  - {entry.timestamp_display} "
                        f"{entry.request_method} "
                        f"{entry.request_uri} "
                        f"HTTP {entry.response_status}"
                    )

                lines.append("")

        self.analysis_text.delete(
            "1.0",
            "end",
        )
        self.analysis_text.insert(
            "1.0",
            "\n".join(lines),
        )

    def _require_included(self):
        entries = self.included_entries()

        if not entries:
            messagebox.showinfo(
                "Nothing included",
                (
                    "No logs are marked for export.\n\n"
                    "Select rows in Timeline and click "
                    "'Include Selected', or use "
                    "'Include All Filtered'."
                ),
            )
            return []

        return entries

    def copy_ticket(self):
        entries = self._require_included()
        if not entries:
            return

        expected, actual = self._read_expected_actual()

        text = build_ticket(
            entries,
            self.mask_var.get(),
            expected,
            actual,
            self._extra_mask_keys(),
        )

        self.clipboard_clear()
        self.clipboard_append(text)
        self.status.config(
            text=f"Copied {len(entries)} included log(s) for ticket."
        )

    def copy_markdown(self):
        entries = self._require_included()
        if not entries:
            return

        expected, actual = self._read_expected_actual()

        text = build_markdown(
            entries,
            self.mask_var.get(),
            expected,
            actual,
            self._extra_mask_keys(),
        )

        self.clipboard_clear()
        self.clipboard_append(text)
        self.status.config(
            text=f"Copied {len(entries)} included log(s) as Markdown."
        )

    def export(self):
        entries = self._require_included()
        if not entries:
            return

        parent = filedialog.askdirectory()

        if not parent:
            return

        folder_name = (
            "QA_Evidence_"
            + datetime.now().strftime(
                "%Y%m%d_%H%M%S"
            )
        )

        expected, actual = self._read_expected_actual()

        try:
            path = export_package(
                entries=entries,
                destination=Path(parent) / folder_name,
                mask=self.mask_var.get(),
                expected=expected,
                actual=actual,
                extra_mask_keys=self._extra_mask_keys(),
                include_summary_txt=self.export_summary_txt_var.get(),
                include_summary_md=self.export_summary_md_var.get(),
                include_raw=self.export_raw_var.get(),
                include_sanitized=self.export_sanitized_var.get(),
            )

            messagebox.showinfo(
                "Export complete",
                (
                    f"Exported {len(entries)} selected log(s).\n\n"
                    f"Created:\n{path}"
                ),
            )

        except Exception as exc:
            messagebox.showerror(
                "Export failed",
                str(exc),
            )

def main():
    App().mainloop()

if __name__ == "__main__":
    main()
