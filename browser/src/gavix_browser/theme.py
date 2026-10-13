"""
GAVIX Browser - Theme System and Styling Tokens.
Design inspired by the GAVIX aesthetic: Deep space background, sleek dark surfaces,
emerald-green glow highlights (#00E599), and cyan accents (#06B6D4).
"""

class GavixColors:
    # Primary Backgrounds
    BG_MAIN = "#080B10"          # Deep space dark chrome
    BG_SURFACE = "#121721"       # Nav rail and secondary panels
    BG_RAISED = "#1A2230"        # Address bar, cards, inputs
    BG_HOVER = "#242F42"         # Button hover state
    BG_ACTIVE = "#2C394F"        # Button pressed state

    # Borders & Lines
    BORDER_SUBTLE = "#1E2738"    # Subtle boundaries
    BORDER_MUTED = "#2A364C"     # Input borders
    BORDER_FOCUS = "#00E599"     # Neon Emerald focus highlight

    # Accent Brand Colors
    EMERALD = "#00E599"          # Primary GAVIX Electric Emerald
    CYAN = "#06B6D4"             # Secondary futuristic cyan
    EMERALD_MUTED = "rgba(0, 229, 153, 0.15)" # Subtle accent glow background

    # Typography
    TEXT_PRIMARY = "#F1F5F9"     # Crisp bright off-white
    TEXT_SECONDARY = "#94A3B8"   # Secondary muted slate
    TEXT_MUTED = "#64748B"       # Placeholder and disabled text

    # State indicators
    SUCCESS = "#10B981"
    ERROR = "#EF4444"
    WARNING = "#F59E0B"


def get_app_stylesheet() -> str:
    """Returns the comprehensive dark QSS stylesheet for GAVIX Browser."""
    return f"""
    QMainWindow {{
        background-color: {GavixColors.BG_MAIN};
    }}

    QWidget {{
        color: {GavixColors.TEXT_PRIMARY};
        font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
        font-size: 13px;
    }}

    /* Top Chrome / Tab Bar Container */
    #TopTabBar {{
        background-color: #05080C;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        padding-top: 4px;
    }}

    /* Top Chrome / Navigation Bar */
    #TopBar {{
        background-color: #080D13;
        border-bottom: 1px solid rgba(255, 255, 255, 0.07);
        padding: 5px 12px;
    }}

    /* Action & Nav Buttons */
    QToolButton, QPushButton {{
        background-color: transparent;
        color: #94A3B8;
        border: 1px solid transparent;
        border-radius: 8px;
        padding: 6px 10px;
        font-weight: 500;
    }}

    QToolButton:hover, QPushButton:hover {{
        background-color: rgba(255, 255, 255, 0.08);
        color: #F1F5F9;
        border: 1px solid rgba(255, 255, 255, 0.12);
    }}

    QToolButton:pressed, QPushButton:pressed {{
        background-color: rgba(0, 229, 153, 0.2);
        color: #00E599;
    }}

    QToolButton:disabled, QPushButton:disabled {{
        color: #475569;
        background-color: transparent;
    }}

    /* Address Bar / Omnibox */
    #AddressBar {{
        background-color: rgba(20, 29, 40, 0.75);
        color: #F1F5F9;
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 12px;
        padding: 6px 14px;
        font-size: 13px;
        selection-background-color: #00E599;
        selection-color: #080B10;
    }}

    #AddressBar:hover {{
        border-color: rgba(255, 255, 255, 0.2);
        background-color: rgba(26, 37, 52, 0.85);
    }}

    #AddressBar:focus {{
        border: 1px solid #00E599;
        background-color: #121B27;
        color: #FFFFFF;
    }}

    /* Security / HTTPS Badge */
    #SecurityBadge {{
        color: #00E599;
        font-weight: 600;
        font-size: 12px;
        padding-right: 6px;
    }}

    /* Left Navigation Rail (Matching Screenshot 1) */
    #NavRail {{
        background-color: #0A1118;
        border-right: 1px solid rgba(255, 255, 255, 0.06);
        min-width: 78px;
        max-width: 78px;
    }}

    #NavRail QToolButton {{
        border-radius: 12px;
        padding: 8px 4px 6px 4px;
        margin: 2px 8px;
        color: rgba(255, 255, 255, 0.7);
        font-size: 11px;
        font-weight: 500;
        border: 1px solid transparent;
        qproperty-iconSize: 22px 22px;
    }}

    #NavRail QToolButton:hover {{
        background-color: rgba(255, 255, 255, 0.08);
        color: #FFFFFF;
        border: 1px solid rgba(255, 255, 255, 0.12);
    }}

    #NavRail QToolButton[active="true"] {{
        background-color: rgba(0, 229, 153, 0.14);
        color: #00E599;
        border: 1px solid rgba(0, 229, 153, 0.45);
        font-weight: 600;
    }}

    /* Progress Bar */
    QProgressBar {{
        background-color: transparent;
        border: none;
        height: 2px;
        text-align: center;
    }}

    QProgressBar::chunk {{
        background-color: qlineargradient(
            x1:0, y1:0, x2:1, y2:0,
            stop:0 {GavixColors.EMERALD},
            stop:1 {GavixColors.CYAN}
        );
    }}

    /* Status Bar */
    QStatusBar {{
        background-color: {GavixColors.BG_MAIN};
        color: {GavixColors.TEXT_MUTED};
        border-top: 1px solid {GavixColors.BORDER_SUBTLE};
        font-size: 11px;
    }}

    /* Tooltips */
    QToolTip {{
        background-color: {GavixColors.BG_RAISED};
        color: {GavixColors.TEXT_PRIMARY};
        border: 1px solid {GavixColors.BORDER_MUTED};
        border-radius: 6px;
        padding: 4px 8px;
    }}
    """
