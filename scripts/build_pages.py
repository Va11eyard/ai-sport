"""Build a self contained static site for GitHub Pages.

The source page lives in site/ and uses paths relative to the repository.
GitHub Pages will serve the project from the repository subpath, so this
script copies only the files the page needs and rewrites the paths.

Run from the project root:
    python scripts/build_pages.py
"""

from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build" / "pages"

REPORT = ROOT / "report" / "Assignment5_Report.pdf"
SLIDES = ROOT / "presentation" / "Assignment5_Presentation.pdf"
APP_SHOT = ROOT / "demo" / "screenshots" / "01_decision.png"
KANTE = ROOT / "outputs" / "figures" / "kante_actions.png"
BACKTEST = ROOT / "outputs" / "figures" / "backtest_uplift.png"

REPLACEMENTS = {
    "../assets/design.css": "assets/design.css",
    "../assets/fonts/Manrope-VariableFont_wght.ttf": "assets/fonts/Manrope-VariableFont_wght.ttf",
    "../demo/screenshots/01_decision.png": "assets/img/app_decision.png",
    "../outputs/figures/kante_actions.png": "assets/img/kante_actions.png",
    "../outputs/figures/backtest_uplift.png": "assets/img/backtest_uplift.png",
    "../report/Assignment5_Report.pdf": "report/Assignment5_Report.pdf",
    "../presentation/Assignment5_Presentation.pdf": "presentation/Assignment5_Presentation.pdf",
    "../README.md": "https://github.com/Va11eyard/ai-sport/blob/dev/README.md",
}


def rewrite(text: str) -> str:
    for old, new in REPLACEMENTS.items():
        text = text.replace(old, new)
    return text


def main() -> None:
    if OUT.exists():
        for child in OUT.iterdir():
            if child.name == ".git":
                continue
            if child.is_dir():
                shutil.rmtree(child)
            else:
                child.unlink()
    (OUT / "assets" / "fonts").mkdir(parents=True)
    (OUT / "assets" / "img").mkdir(parents=True)
    (OUT / "report").mkdir(parents=True)
    (OUT / "presentation").mkdir(parents=True)

    html = (ROOT / "site" / "index.html").read_text(encoding="utf-8")
    (OUT / "index.html").write_text(rewrite(html), encoding="utf-8")

    not_found = (ROOT / "site" / "404.html").read_text(encoding="utf-8")
    not_found = not_found.replace("../assets/design.css", "assets/design.css")
    (OUT / "404.html").write_text(not_found, encoding="utf-8")

    shutil.copy2(ROOT / "site" / "favicon.svg", OUT / "favicon.svg")
    shutil.copy2(ROOT / "assets" / "design.css", OUT / "assets" / "design.css")
    shutil.copy2(ROOT / "assets" / "fonts" / "Manrope-VariableFont_wght.ttf", OUT / "assets" / "fonts" / "Manrope-VariableFont_wght.ttf")
    shutil.copy2(ROOT / "assets" / "fonts" / "OFL.txt", OUT / "assets" / "fonts" / "OFL.txt")
    shutil.copy2(APP_SHOT, OUT / "assets" / "img" / "app_decision.png")
    shutil.copy2(KANTE, OUT / "assets" / "img" / "kante_actions.png")
    shutil.copy2(BACKTEST, OUT / "assets" / "img" / "backtest_uplift.png")
    shutil.copy2(REPORT, OUT / "report" / "Assignment5_Report.pdf")
    shutil.copy2(SLIDES, OUT / "presentation" / "Assignment5_Presentation.pdf")
    (OUT / ".nojekyll").write_text("", encoding="utf-8")

    print("Built", OUT)
    for path in sorted(OUT.rglob("*")):
        if path.is_file():
            print(f"  {path.relative_to(OUT)}  {path.stat().st_size/1e6:.2f} MB")


if __name__ == "__main__":
    main()
