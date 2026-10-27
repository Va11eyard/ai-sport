"""Capture the Assignment 5 demo screens with Playwright.

Start the app first:
    python -m streamlit run app.py --server.port 8601 --server.headless true

Then run:
    python demo/record_demo.py
"""

from __future__ import annotations

import argparse
from pathlib import Path

from playwright.sync_api import sync_playwright

OUT = Path(__file__).resolve().parent / "screenshots"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://localhost:8601")
    parser.add_argument("--wait", type=int, default=5000)
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        page.goto(args.url, wait_until="networkidle", timeout=120000)
        page.wait_for_timeout(args.wait)
        page.screenshot(path=str(OUT / "01_decision.png"), full_page=False)

        page.get_by_role("tab", name="Squad need").click()
        page.wait_for_timeout(2500)
        page.screenshot(path=str(OUT / "02_squad_need.png"), full_page=False)
        page.get_by_role("tab", name="Market").click()
        page.wait_for_timeout(2500)
        page.screenshot(path=str(OUT / "03_market.png"), full_page=False)
        page.get_by_role("tab", name="Shortlist").click()
        page.wait_for_timeout(2500)
        page.screenshot(path=str(OUT / "04_shortlist.png"), full_page=False)
        page.get_by_text("Shortlist", exact=True).last.scroll_into_view_if_needed()
        page.wait_for_timeout(1000)
        page.screenshot(path=str(OUT / "05_shortlist_table.png"), full_page=False)
        page.get_by_text("Player detail", exact=True).scroll_into_view_if_needed()
        page.wait_for_timeout(1000)
        page.screenshot(path=str(OUT / "06_player_detail.png"), full_page=False)
        page.get_by_role("tab", name="Method").click()
        page.wait_for_timeout(2000)
        page.screenshot(path=str(OUT / "07_method.png"), full_page=False)
        browser.close()
    print("wrote", OUT)


if __name__ == "__main__":
    main()
