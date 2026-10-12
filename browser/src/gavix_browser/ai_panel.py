"""
GAVIX Browser - AI Assistant Side Panel.
Implements the collapsible right-side AI assistant panel matching the MVP specification.
Includes action chips, honest consent toggles, and privacy disclosure.
"""

from pathlib import Path
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QToolButton,
    QLineEdit,
    QCheckBox,
    QScrollArea,
    QFrame
)
from gavix_browser.theme import GavixColors


class GavixAiPanel(QWidget):
    """Collapsible right-side AI Assistant panel."""

    close_requested = Signal()
    prompt_submitted = Signal(str, bool)  # (prompt_text, use_page_content)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("AiPanel")
        self.setFixedWidth(340)
        self.setStyleSheet(f"""
            #AiPanel {{
                background-color: {GavixColors.BG_SURFACE};
                border-left: 1px solid {GavixColors.BORDER_SUBTLE};
            }}
            QLabel {{
                color: {GavixColors.TEXT_PRIMARY};
            }}
            QLineEdit {{
                background-color: {GavixColors.BG_RAISED};
                border: 1px solid {GavixColors.BORDER_MUTED};
                border-radius: 8px;
                padding: 10px 12px;
                color: {GavixColors.TEXT_PRIMARY};
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border: 1px solid {GavixColors.EMERALD};
            }}
            QCheckBox {{
                color: {GavixColors.TEXT_SECONDARY};
                font-size: 12px;
            }}
        """)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # 1. Header with GAVIX Emblem and Close Button
        header_row = QHBoxLayout()
        header_row.setSpacing(8)

        # Emblem Icon
        assets_dir = Path(__file__).resolve().parent.parent.parent / "assets"
        icon_path = assets_dir / "gavix_icon.png"
        icon_lbl = QLabel(self)
        if icon_path.exists():
            pix = QPixmap(str(icon_path)).scaled(
                22, 22, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
            )
            icon_lbl.setPixmap(pix)
        else:
            icon_lbl.setText("✦")
            icon_lbl.setStyleSheet(f"color: {GavixColors.EMERALD}; font-weight: bold;")
        header_row.addWidget(icon_lbl)

        title = QLabel("GAVIX AI", self)
        title.setStyleSheet(f"font-size: 15px; font-weight: bold; color: {GavixColors.EMERALD}; letter-spacing: 1px;")
        header_row.addWidget(title)

        header_row.addStretch()

        btn_close = QToolButton(self)
        btn_close.setText("✕")
        btn_close.setToolTip("Close AI Panel")
        btn_close.setStyleSheet("border: none; font-size: 13px; padding: 4px;")
        btn_close.clicked.connect(self.close_requested.emit)
        header_row.addWidget(btn_close)

        layout.addLayout(header_row)

        # Subtitle
        sub = QLabel("Intelligent Page Companion", self)
        sub.setStyleSheet(f"color: {GavixColors.TEXT_MUTED}; font-size: 12px; margin-bottom: 6px;")
        layout.addWidget(sub)

        # Separator line
        sep = QFrame(self)
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"border-color: {GavixColors.BORDER_SUBTLE};")
        layout.addWidget(sep)

        # 2. Scrollable Body
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background: transparent;")

        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setContentsMargins(0, 4, 0, 4)
        scroll_layout.setSpacing(10)

        # Action Chips Section
        chips_lbl = QLabel("Suggested Actions", scroll_widget)
        chips_lbl.setStyleSheet(f"color: {GavixColors.TEXT_SECONDARY}; font-size: 12px; font-weight: 600;")
        scroll_layout.addWidget(chips_lbl)

        actions = [
            ("📄 Summarize page", "summarize"),
            ("💡 Explain simply", "explain"),
            ("🔍 Key takeaways", "key_points"),
            ("🌐 Translate content", "translate"),
            ("⚖ Compare sources", "compare"),
            ("🔬 Research help", "research"),
        ]

        for text, act_id in actions:
            btn = QPushButton(text, scroll_widget)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {GavixColors.BG_RAISED};
                    border: 1px solid {GavixColors.BORDER_SUBTLE};
                    border-radius: 8px;
                    padding: 8px 12px;
                    text-align: left;
                    font-size: 12px;
                    color: {GavixColors.TEXT_PRIMARY};
                }}
                QPushButton:hover {{
                    background-color: {GavixColors.BG_HOVER};
                    border-color: {GavixColors.BORDER_FOCUS};
                    color: {GavixColors.EMERALD};
                }}
            """)
            btn.clicked.connect(lambda checked=False, a=text: self._on_action_clicked(a))
            scroll_layout.addWidget(btn)

        # Response / Chat Display Area
        self.response_card = QFrame(scroll_widget)
        self.response_card.setStyleSheet(f"""
            background-color: {GavixColors.BG_MAIN};
            border: 1px solid {GavixColors.BORDER_SUBTLE};
            border-radius: 10px;
            padding: 12px;
        """)
        card_layout = QVBoxLayout(self.response_card)
        card_layout.setContentsMargins(10, 10, 10, 10)

        self.status_title = QLabel("AI Status: Standby", self.response_card)
        self.status_title.setStyleSheet(f"font-size: 12px; font-weight: bold; color: {GavixColors.EMERALD};")
        card_layout.addWidget(self.status_title)

        self.status_text = QLabel(
            "Local and private. Connects to local Ollama or sovereign inference in production.",
            self.response_card
        )
        self.status_text.setWordWrap(True)
        self.status_text.setStyleSheet(f"font-size: 12px; color: {GavixColors.TEXT_MUTED}; line-height: 1.4;")
        card_layout.addWidget(self.status_text)

        scroll_layout.addWidget(self.response_card)
        scroll_layout.addStretch()

        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll, stretch=1)

        # 3. Privacy Consent Toggle (OFF by default)
        self.chk_use_content = QCheckBox("Use page content (Requires consent)", self)
        self.chk_use_content.setChecked(False)
        self.chk_use_content.setToolTip("When OFF, no text from the current page is transmitted or processed.")
        layout.addWidget(self.chk_use_content)

        # 4. Input Area
        input_row = QHBoxLayout()
        input_row.setSpacing(6)

        self.prompt_input = QLineEdit(self)
        self.prompt_input.setPlaceholderText("Ask GAVIX AI anything...")
        self.prompt_input.returnPressed.connect(self._on_send_clicked)
        input_row.addWidget(self.prompt_input, stretch=1)

        btn_send = QToolButton(self)
        btn_send.setText("➤")
        btn_send.setToolTip("Send Prompt")
        btn_send.setStyleSheet(f"""
            QToolButton {{
                background: linear-gradient(135deg, {GavixColors.EMERALD}, {GavixColors.CYAN});
                color: #080B10;
                font-weight: bold;
                border-radius: 8px;
                padding: 10px 14px;
            }}
            QToolButton:hover {{
                filter: brightness(1.15);
            }}
        """)
        btn_send.clicked.connect(self._on_send_clicked)
        input_row.addWidget(btn_send)

        layout.addLayout(input_row)

    def _on_action_clicked(self, action_name: str):
        """Triggered when an action chip is pressed."""
        self.status_title.setText(f"Action: {action_name}")
        if self.chk_use_content.isChecked():
            self.status_text.setText(
                f"Page content consent enabled. Ready to process '{action_name}' when local model backend is active."
            )
        else:
            self.status_text.setText(
                f"Page content consent is OFF. To allow '{action_name}' to inspect the current page, check the consent toggle below."
            )

    def _on_send_clicked(self):
        text = self.prompt_input.text().strip()
        if not text:
            return

        use_page = self.chk_use_content.isChecked()
        self.prompt_submitted.emit(text, use_page)
        self.prompt_input.clear()

        self.status_title.setText(f"Prompt Sent: {text[:25]}...")
        if use_page:
            self.status_text.setText(
                "Consent granted. Context included safely under local privacy rules."
            )
        else:
            self.status_text.setText(
                "Prompt submitted in standalone mode (no page content sent)."
            )
