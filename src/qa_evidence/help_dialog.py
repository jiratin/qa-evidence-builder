import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

from .help_content import HELP_SECTIONS

class HelpDialog(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)

        self.title("Help — QA Evidence Builder")
        self.geometry("980x720")
        self.minsize(700, 500)

        self.transient(master)

        self.search_var = tk.StringVar()

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self._build()

    def _build(self):
        header = ttk.Frame(
            self,
            padding=(10, 10, 10, 6),
        )
        header.grid(
            row=0,
            column=0,
            sticky="ew",
        )

        ttk.Label(
            header,
            text="QA Evidence Builder — User Guide",
            font=("TkDefaultFont", 15, "bold"),
        ).pack(side="left")

        ttk.Label(
            header,
            text="Search:",
        ).pack(
            side="left",
            padx=(20, 4),
        )

        search = ttk.Entry(
            header,
            textvariable=self.search_var,
            width=28,
        )
        search.pack(
            side="left",
            fill="x",
            expand=True,
        )

        body = ttk.Panedwindow(
            self,
            orient="horizontal",
        )
        body.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=10,
            pady=(0, 10),
        )

        nav_frame = ttk.Frame(body)
        content_frame = ttk.Frame(body)

        body.add(nav_frame, weight=1)
        body.add(content_frame, weight=3)

        nav_frame.columnconfigure(0, weight=1)
        nav_frame.rowconfigure(1, weight=1)

        ttk.Label(
            nav_frame,
            text="หัวข้อ",
        ).grid(
            row=0,
            column=0,
            sticky="w",
            pady=(0, 4),
        )

        self.listbox = tk.Listbox(
            nav_frame,
            exportselection=False,
        )
        nav_scroll = ttk.Scrollbar(
            nav_frame,
            orient="vertical",
            command=self.listbox.yview,
        )

        self.listbox.configure(
            yscrollcommand=nav_scroll.set,
        )

        self.listbox.grid(
            row=1,
            column=0,
            sticky="nsew",
        )
        nav_scroll.grid(
            row=1,
            column=1,
            sticky="ns",
        )

        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(1, weight=1)

        self.title_label = ttk.Label(
            content_frame,
            text="",
            font=("TkDefaultFont", 13, "bold"),
        )
        self.title_label.grid(
            row=0,
            column=0,
            sticky="w",
            pady=(0, 4),
        )

        self.content = ScrolledText(
            content_frame,
            wrap="word",
            font=("TkDefaultFont", 11),
        )
        self.content.grid(
            row=1,
            column=0,
            sticky="nsew",
        )

        footer = ttk.Frame(
            self,
            padding=(10, 0, 10, 10),
        )
        footer.grid(
            row=2,
            column=0,
            sticky="ew",
        )

        ttk.Label(
            footer,
            text=(
                "Tip: ใช้ Search เพื่อค้นคำ เช่น Export, Mask, "
                "Transaction, Error หรือ HAR"
            ),
        ).pack(side="left")

        ttk.Button(
            footer,
            text="Close",
            command=self.destroy,
        ).pack(side="right")

        self.filtered_sections = list(HELP_SECTIONS)

        self.listbox.bind(
            "<<ListboxSelect>>",
            self._on_select,
        )

        self.search_var.trace_add(
            "write",
            lambda *_: self._refresh_sections(),
        )

        self._refresh_sections()

    def _refresh_sections(self):
        query = self.search_var.get().strip().lower()

        if query:
            self.filtered_sections = [
                section
                for section in HELP_SECTIONS
                if (
                    query in section[0].lower()
                    or query in section[1].lower()
                )
            ]
        else:
            self.filtered_sections = list(HELP_SECTIONS)

        self.listbox.delete(0, "end")

        for title, _body in self.filtered_sections:
            self.listbox.insert("end", title)

        if self.filtered_sections:
            self.listbox.selection_set(0)
            self.listbox.activate(0)
            self._show_section(0)
        else:
            self.title_label.config(
                text="ไม่พบหัวข้อ",
            )
            self.content.config(state="normal")
            self.content.delete("1.0", "end")
            self.content.insert(
                "1.0",
                "ไม่พบหัวข้อที่ตรงกับคำค้น",
            )
            self.content.config(state="disabled")

    def _on_select(self, _event=None):
        selection = self.listbox.curselection()
        if selection:
            self._show_section(selection[0])

    def _show_section(self, index):
        if not (
            0 <= index < len(self.filtered_sections)
        ):
            return

        title, body = self.filtered_sections[index]

        self.title_label.config(
            text=title,
        )

        self.content.config(state="normal")
        self.content.delete("1.0", "end")
        self.content.insert(
            "1.0",
            body.strip(),
        )
        self.content.config(state="disabled")
        self.content.see("1.0")
