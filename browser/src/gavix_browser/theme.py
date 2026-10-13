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

    /* Top Chrome / Navigation Bar */
    #TopBar {{
        background-color: {GavixColors.BG_MAIN};
        border-bottom: 1px solid {GavixColors.BORDER_SUBTLE};
        padding: 6px 12px;
    }}

    /* Action & Nav Buttons */
    QToolButton, QPushButton {{
        background-color: transparent;
        color: {GavixColors.TEXT_SECONDARY};
        border: 1px solid transparent;
        border-radius: 8px;
        padding: 6px 10px;
        font-weight: 500;
    }}

    QToolButton:hover, QPushButton:hover {{
        background-color: {GavixColors.BG_HOVER};
        color: {GavixColors.TEXT_PRIMARY};
        border: 1px solid {GavixColors.BORDER_MUTED};
    }}

    QToolButton:pressed, QPushButton:pressed {{
        background-color: {GavixColors.BG_ACTIVE};
        color: {GavixColors.EMERALD};
    }}

    QToolButton:disabled, QPushButton:disabled {{
        color: {GavixColors.TEXT_MUTED};
        background-color: transparent;
    }}

    /* Address Bar / Omnibox */
    #AddressBar {{
        background-color: {GavixColors.BG_RAISED};
        color: {GavixColors.TEXT_PRIMARY};
        border: 1px solid {GavixColors.BORDER_MUTED};
        border-radius: 10px;
        padding: 6px 14px;
        font-size: 13px;
        selection-background-color: {GavixColors.EMERALD};
        selection-color: #080B10;
    }}

    #AddressBar:focus {{
        border: 1px solid {GavixColors.BORDER_FOCUS};
        background-color: #161E2B;
    }}

    /* Security / HTTPS Badge */
    #SecurityBadge {{
        color: {GavixColors.EMERALD};
        font-weight: 600;
        font-size: 12px;
        padding-right: 6px;
    }}

    /* Left Navigation Rail (Matching Screenshot 1) */
    #NavRail {{
        background-color: #0A1118;
        border-right: 1px solid rgba(255, 255, 255, 0.06);
        min-width: 72px;
        max-width: 72px;
    }}

    #NavRail QToolButton {{
        border-radius: 12px;
        padding: 10px 4px;
        margin: 4px 6px;
        color: rgba(255, 255, 255, 0.65);
        font-size: 10px;
        font-weight: 500;
        border: 1px solid transparent;
    }}

    #NavRail QToolButton:hover {{
        background-color: rgba(255, 255, 255, 0.08);
        color: #FFFFFF;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }}

    #NavRail QToolButton[active="true"] {{
        background-color: rgba(0, 229, 153, 0.15);
        color: #00E599;
        border: 1px solid rgba(0, 229, 153, 0.4);
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
