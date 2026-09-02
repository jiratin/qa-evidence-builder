"""Dark and light visual themes for the Qt desktop application."""

PALETTES = {
    "dark": {"window": "#0b1020", "sidebar": "#11182a", "surface": "#151d31", "surface_alt": "#1b2540", "input": "#0f1628", "border": "#273452", "text": "#f4f7ff", "muted": "#93a4c3", "primary": "#7c6df2", "primary_hover": "#9185f7", "danger": "#ff5c6c", "table_alt": "#121a2d", "selected": "#403a82", "selected_text": "#ffffff", "scroll": "#354362"},
    "light": {"window": "#f5f7fb", "sidebar": "#ffffff", "surface": "#ffffff", "surface_alt": "#eef1f8", "input": "#f9faff", "border": "#d8deeb", "text": "#172033", "muted": "#64748b", "primary": "#6657e8", "primary_hover": "#5949d7", "danger": "#d92d3a", "table_alt": "#f8f9fc", "selected": "#c9c2ff", "selected_text": "#111827", "scroll": "#aeb8ca"},
}
COLORS = PALETTES["dark"]


def stylesheet(mode="dark") -> str:
    c = PALETTES.get(mode, PALETTES["dark"])
    return f"""
    * {{ font-family: 'Segoe UI', 'Inter', 'Noto Sans Thai', sans-serif; font-size: 13px; }}
    QMainWindow, QDialog {{ background: {c['window']}; color: {c['text']}; }} QWidget {{ color: {c['text']}; }}
    QFrame#sidebar {{ background: {c['sidebar']}; border-right: 1px solid {c['border']}; }}
    QFrame#card, QFrame#panel {{ background: {c['surface']}; border: 1px solid {c['border']}; border-radius: 12px; }}
    QLabel#brand {{ font-size: 18px; font-weight: 700; }} QLabel#pageTitle {{ font-size: 25px; font-weight: 700; }}
    QLabel#sectionTitle {{ font-size: 15px; font-weight: 650; }} QLabel#metric {{ font-size: 25px; font-weight: 750; }}
    QLabel#muted, QLabel#cardLabel {{ color: {c['muted']}; }}
    QLabel#alert, QLabel#errorText, QCheckBox#danger {{ color: {c['danger']}; font-weight: 650; }}
    QLabel#filterTitle {{ color: {c['muted']}; font-size: 11px; font-weight: 700; }}
    QFrame#filterGroup {{ background: {c['surface_alt']}; border: 1px solid {c['border']}; border-radius: 9px; }}
    QPushButton {{ background: transparent; border: 1px solid {c['border']}; border-radius: 8px; padding: 8px 12px; }}
    QPushButton:hover {{ background: {c['surface_alt']}; }} QPushButton#primary {{ background: {c['primary']}; color: #ffffff; border-color: {c['primary']}; font-weight: 650; }} QPushButton#primary:hover {{ background: {c['primary_hover']}; }}
    QPushButton#nav {{ border: none; text-align: left; color: {c['muted']}; padding: 11px 14px; }} QPushButton#nav:hover {{ color: {c['text']}; background: {c['surface_alt']}; }} QPushButton#nav:checked {{ color: {c['text']}; background: {c['surface_alt']}; border-left: 3px solid {c['primary']}; }}
    QPushButton#filterChip {{ color: {c['primary']}; background: {c['surface_alt']}; border-color: {c['primary']}; padding: 4px 8px; }}
    QPushButton#filterClear {{ color: {c['muted']}; border: none; padding: 1px 4px; font-size: 11px; }} QPushButton#filterClear:hover {{ color: {c['danger']}; }}
    QLineEdit, QComboBox, QPlainTextEdit, QTextEdit, QTextBrowser, QListWidget {{ background: {c['input']}; border: 1px solid {c['border']}; border-radius: 8px; padding: 7px; selection-background-color: {c['primary']}; selection-color: #ffffff; }}
    QLineEdit:focus, QComboBox:focus, QPlainTextEdit:focus, QTextEdit:focus {{ border-color: {c['primary']}; }} QComboBox::drop-down {{ border: none; width: 24px; }}
    QComboBox QAbstractItemView {{ background: {c['surface']}; color: {c['text']}; border: 1px solid {c['border']}; selection-background-color: {c['primary']}; selection-color: #ffffff; outline: 0; padding: 4px; }}
    QCheckBox {{ spacing: 8px; }} QCheckBox::indicator {{ width: 17px; height: 17px; border: 1px solid {c['muted']}; border-radius: 4px; background: {c['input']}; }} QCheckBox::indicator:checked {{ background: {c['primary']}; border-color: {c['primary']}; }}
    QTableWidget {{ background: {c['surface']}; alternate-background-color: {c['table_alt']}; border: none; gridline-color: {c['border']}; }} QHeaderView::section {{ background: {c['sidebar']}; color: {c['muted']}; border: none; border-bottom: 1px solid {c['border']}; padding: 9px 7px; font-weight: 650; }} QTableWidget::item {{ padding: 7px; border-bottom: 1px solid {c['border']}; }} QTableWidget::item:selected {{ background: {c['selected']}; color: {c['selected_text']}; }}
    QScrollBar:vertical {{ background: transparent; width: 10px; margin: 2px; }} QScrollBar::handle:vertical {{ background: {c['scroll']}; border-radius: 4px; min-height: 30px; }} QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
    QSplitter::handle {{ background: {c['border']}; width: 1px; height: 1px; }} QToolTip {{ background: {c['surface_alt']}; color: {c['text']}; border: 1px solid {c['border']}; }}
    """
