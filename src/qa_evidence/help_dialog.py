from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QHBoxLayout, QLabel, QLineEdit, QListWidget, QPushButton, QSplitter, QTextBrowser, QVBoxLayout, QWidget

from .help_content import HELP_SECTIONS


class HelpDialog(QDialog):
    """Searchable, custom-styled user guide."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("User Guide — QA Evidence Builder")
        self.resize(980, 720)
        self.setMinimumSize(700, 500)
        self.sections = list(HELP_SECTIONS)
        root = QVBoxLayout(self)
        header = QHBoxLayout()
        title = QLabel("QA Evidence Builder — User Guide")
        title.setObjectName("pageTitle")
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search Export, Mask, Transaction, Error, HAR…")
        header.addWidget(title)
        header.addStretch()
        header.addWidget(self.search, 1)
        root.addLayout(header)
        split = QSplitter(Qt.Horizontal)
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.addWidget(QLabel("Topics"))
        self.topics = QListWidget()
        left_layout.addWidget(self.topics)
        self.content = QTextBrowser()
        self.content.setOpenExternalLinks(True)
        split.addWidget(left)
        split.addWidget(self.content)
        split.setSizes([270, 690])
        root.addWidget(split, 1)
        footer = QHBoxLayout()
        tip = QLabel("Tip: search works across topic titles and guide content.")
        tip.setObjectName("muted")
        close = QPushButton("Close")
        close.clicked.connect(self.accept)
        footer.addWidget(tip)
        footer.addStretch()
        footer.addWidget(close)
        root.addLayout(footer)
        self.search.textChanged.connect(self._refresh)
        self.topics.currentRowChanged.connect(self._show)
        self._refresh()

    def _refresh(self):
        query = self.search.text().strip().lower()
        self.sections = [s for s in HELP_SECTIONS if not query or query in s[0].lower() or query in s[1].lower()]
        self.topics.clear()
        self.topics.addItems([title for title, _ in self.sections])
        if self.sections:
            self.topics.setCurrentRow(0)
        else:
            self.content.setPlainText("No guide topics match your search.")

    def _show(self, row):
        if 0 <= row < len(self.sections):
            title, body = self.sections[row]
            self.content.setMarkdown(f"## {title}\n\n{body.strip()}")
