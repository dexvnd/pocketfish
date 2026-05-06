DARK_QSS = """
QWidget {
    background: #15171c;
    color: #e8e8e8;
    font-family: 'Segoe UI', sans-serif;
    font-size: 12px;
}
QGroupBox {
    border: 1px solid #2a2d35;
    border-radius: 6px;
    margin-top: 12px;
    padding-top: 8px;
    background: #1a1c22;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 6px;
    color: #7a8290;
    font-size: 10px;
}
QPushButton {
    background: #23262e;
    border: 1px solid #2e323b;
    border-radius: 5px;
    padding: 6px 10px;
    color: #d8d8d8;
}
QPushButton:hover { background: #2c3038; }
QPushButton:pressed { background: #1c1f26; }
QPushButton:checked { background: #2c5c3c; border-color: #4caf50; color: #ffffff; }
QPushButton[primary="true"] {
    background: #3563f0; border-color: #4575ff; font-weight: 600; color: #ffffff;
}
QPushButton[primary="true"]:hover { background: #4575ff; }
QPushButton[primary="true"]:checked { background: #2c5c3c; border-color: #4caf50; }
QPushButton[side="true"] {
    background: #23262e; border: 2px solid #2e323b;
    padding: 12px 10px; font-size: 14px; font-weight: 600;
}
QPushButton[side="true"]:checked {
    background: #3563f0; border-color: #4575ff; color: #ffffff;
}
QComboBox, QSpinBox, QLineEdit {
    background: #1c1e24; border: 1px solid #2a2d35; border-radius: 4px;
    padding: 4px 8px; color: #e8e8e8;
    selection-background-color: #3563f0;
}
QSlider::groove:horizontal {
    height: 3px; background: #2a2d35; border-radius: 2px;
}
QSlider::handle:horizontal {
    background: #4575ff; width: 12px; margin: -5px 0; border-radius: 6px;
}
QSlider::handle:horizontal:hover { background: #5a85ff; }
QLabel[role="status"]     { color: #7a8290; font-size: 11px; }
QLabel[role="statusGood"] { color: #5cb85c; font-size: 11px; font-weight: 600; }
QLabel[role="statusWarn"] { color: #f0ad4e; font-size: 11px; font-weight: 600; }
QLabel[role="statusBad"]  { color: #d9534f; font-size: 11px; font-weight: 600; }
QLabel[role="header"]     { font-size: 13px; font-weight: 600; color: #ffffff; }
QLabel[role="big"]        { font-size: 18px; font-weight: 700; color: #5cb85c; }
QLabel[role="muted"]      { color: #7a8290; }
QLabel[role="metric"]     { color: #d8d8d8; font-family: 'Consolas', monospace; font-size: 11px; }
QPlainTextEdit {
    background: #0f1115; border: 1px solid #23262e; border-radius: 4px;
    color: #b8b8b8; font-family: 'Consolas', monospace; font-size: 10px;
    padding: 4px;
}
QTabWidget::pane {
    border: 1px solid #2a2d35; border-radius: 4px; top: -1px;
    background: #1a1c22;
}
QTabBar::tab {
    background: transparent; color: #7a8290; padding: 6px 16px;
    border-bottom: 2px solid transparent;
    margin-right: 2px;
}
QTabBar::tab:hover { color: #d8d8d8; }
QTabBar::tab:selected {
    color: #ffffff; border-bottom: 2px solid #3563f0; font-weight: 600;
}
"""
