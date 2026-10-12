"""
GAVIX Browser - New Tab / Home Page Generator.
Reads and returns the local home.html template for GAVIX New Tab experience.
"""

from pathlib import Path


def get_home_page_html() -> str:
    """Reads the static GAVIX Home HTML file."""
    assets_dir = Path(__file__).resolve().parent.parent.parent / "assets"
    home_file = assets_dir / "home.html"
    if home_file.exists():
        with open(home_file, "r", encoding="utf-8") as f:
            return f.read()
    return "<html><body style='background:#07090E;color:#00E599;'><h1>GAVIX</h1></body></html>"
