from __future__ import annotations

import html
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from transfer_lab.names import clean_name  # noqa: E402

OUT = ROOT / "outputs"
FIG = OUT / "figures"
TAB = OUT / "tables"
PRES = ROOT / "presentation"
PRES.mkdir(exist_ok=True)


def esc(value: object) -> str:
    text = str(value).replace("\u2014", ", ").replace("\u2013", "-").replace("\u2192", "to")
    return html.escape(text)


def eur(value: float) -> str:
    return f"EUR {value/1e6:.1f}m"


def slide(kicker: str, title: str, body: str, number: int, dark: bool = False, extra: str = "") -> str:
    cls = "slide dark" if dark else "slide"
    return f"""
<section class="{cls}">
  <div class="kicker"><span>{esc(kicker)}</span><span>{number:02d}</span></div>
  <h1>{esc(title)}</h1>
  <div class="body">{body}</div>
  {extra}
  <div class="footer"><span>Assignment 5 | AAI-2504M</span><span>Leicester City, summer 2016</span></div>
</section>
"""


def figure(name: str, caption: str = "") -> str:
    src = f"../outputs/figures/{name}"
    cap = f"<div class='caption'>{esc(caption)}</div>" if caption else ""
    return f"<figure><img src='{esc(src)}'>{cap}</figure>"


def stat(value: str, label: str) -> str:
    return f"<div class='stat'><b>{esc(value)}</b><span>{esc(label)}</span></div>"


def build() -> str:
    decision = json.loads((OUT / "decision_summary.json").read_text(encoding="utf-8"))
    rec = decision["recommended"]
    players = {p["need"]: p for p in rec["players"]}

    slides = []

    title_body = f"""
    <div class="title-grid">
      <div>
        <p class="lede">Leicester City, summer 2016. Replace N'Golo Kanté, rebuild the spine, keep the budget.</p>
        <p class="author">Dinmukhammed Mynzhassar, AAI-2504M</p>
        <div class="stats">
          {stat("380", "real matches parsed")}
          {stat("30,939", "player seasons priced")}
          {stat("3", "signings recommended")}
        </div>
      </div>
      <div class="title-image">{figure("kante_actions.png")}</div>
    </div>
    """
    slides.append(
        slide(
            "Assignment 5 | AI Football Intelligence",
            "From data to transfer decisions",
            title_body,
            1,
        )
    )

    decision_body = f"""
    <p class="big-line">Sign Gueye, Cook and Ighalo for EUR 24m</p>
    <div class="cards three">
      <div class="card"><div class="tag">CM</div><h2>Idrissa Gueye</h2><p class="club">Aston Villa</p><p class="fee">EUR 9m</p><p class="small">Fit 95 | Safety 91</p></div>
      <div class="card"><div class="tag">CB</div><h2>Steve Cook</h2><p class="club">AFC Bournemouth</p><p class="fee">EUR 3m</p><p class="small">Value 100 | Safety 96</p></div>
      <div class="card"><div class="tag">ST</div><h2>Odion Ighalo</h2><p class="club">Watford</p><p class="fee">EUR 12m</p><p class="small">Fit 79 | Value 82</p></div>
    </div>
    <div class="bottom-line"><span>EUR 50m budget</span><span>EUR 26m left for wages and a January buffer</span><span>Two year value backtest: +52%</span></div>
    <p class="small">The case for Gueye is tactical fit, not a bargain. The money is made on Cook. Ighalo is the best available box threat.</p>
    """
    slides.append(slide("The decision", "Replace Kanté without losing the identity", decision_body, 2, dark=True))

    data_body = f"""
    <p class="lede">Two independent sources, one cutoff date: 1 July 2016.</p>
    <div class="stats four">
      {stat("380", "Premier League matches")}
      {stat("10,385", "player-match rows")}
      {stat("30,939", "top five player seasons")}
      {stat("1.1m", "transfer records")}
    </div>
    <div class="pipeline">
      <div class="step"><b>01</b><h2>Parse events</h2><p>Passes, carries, shots, pressures, defensive actions</p></div>
      <div class="step"><b>02</b><h2>Build profiles</h2><p>Per-90 rates, role clusters, similarity</p></div>
      <div class="step"><b>03</b><h2>Price the market</h2><p>Global and local value models</p></div>
      <div class="step"><b>04</b><h2>Score fits</h2><p>Kanté similarity, need profiles, risk</p></div>
      <div class="step"><b>05</b><h2>Optimise</h2><p>Binary plan under the fee budget</p></div>
    </div>
    <p class="small">Raw data is not committed. The download script and processed tables make the result reproducible.</p>
    """
    slides.append(slide("The data", "What the data can see", data_body, 3))

    style_body = f"""
    <div class="two-col wide-left">
      <div>{figure("leicester_style.png")}</div>
      <div>
        <div class="stats two">
          {stat("42.6%", "possession")}
          {stat("68.0%", "pass completion")}
          {stat("1.74", "xG per match")}
          {stat("15.1%", "set-piece xG share")}
        </div>
        <p class="lede">Low possession, direct passing, high xG, set pieces and counters. The style did not need a playmaker. It needed a destroyer who could carry the ball.</p>
      </div>
    </div>
    """
    slides.append(slide("Squad need", "What Leicester were", style_body, 4))

    kante_body = f"""
    <div class="two-col">
      <div>{figure("kante_percentiles.png")}</div>
      <div>
        <p class="lede">Kanté was a 100th percentile ball winner. He was not a high-volume passer.</p>
        <p class="small">Cosine similarity to Kanté</p>
        <div class="rank-list">
          <div><b>0.93</b><span>Idrissa Gueye</span></div>
          <div><b>0.75</b><span>Jan Kirchhoff</span></div>
          <div><b>0.70</b><span>Victor Wanyama</span></div>
          <div><b>0.68</b><span>Francis Coquelin</span></div>
          <div class="muted"><b>0.00</b><span>Aaron Ramsey, a label warning</span></div>
        </div>
        <p class="small">Cosine similarity on ten per-90 actions. Formation labels are not roles.</p>
      </div>
    </div>
    """
    slides.append(slide("The replacement", "Kanté was not a playmaker", kante_body, 5))

    market_body = f"""
    <div class="two-col">
      <div>{figure("value_parity.png")}</div>
      <div>
        <div class="stats two">
          {stat("0.734", "global R2")}
          {stat("0.855", "global Spearman")}
          {stat("0.614", "local R2")}
          {stat("0.785", "local Spearman")}
        </div>
        <p class="lede">The market pays for goals, assists, passing volume and club reputation. It discounts defensive actions once position and possession are controlled.</p>
        <p class="small">Local baseline R2 0.495. The event model adds 0.119. Global test seasons: 2021/22 to 2024/25.</p>
      </div>
    </div>
    """
    slides.append(slide("Market value", "Two market models", market_body, 6))

    signal_body = f"""
    <div class="two-col">
      <div>{figure("backtest_uplift.png")}</div>
      <div>
        <div class="stats two">
          {stat("+11.8%", "undervalued, 2 years")}
          {stat("-10.9%", "rest, 2 years")}
          {stat("52.8%", "hit rate, undervalued")}
          {stat("35.8%", "hit rate, rest")}
        </div>
        <p class="lede">The global model beat the rest in all 10 evaluation seasons on a relative basis. Absolute values fell in several seasons.</p>
        <p class="small">This is a signal, not a target. Individual outcomes vary.</p>
      </div>
    </div>
    """
    slides.append(slide("Validation", "The undervalued signal is modest but real", signal_body, 7))

    table_rows = []
    for need, label in (("CM", "Midfield"), ("CB", "Defence"), ("ST", "Attack")):
        part = __import__("pandas").read_csv(TAB / "candidates.csv")
        part["display_name"] = part["display_name"].map(clean_name)
        part = part[part["need"] == need].sort_values("score", ascending=False).head(3)
        names = ", ".join(f"{r['display_name'].split()[-1]} {r['market_value']/1e6:.0f}m" for _, r in part.iterrows())
        best = part.iloc[0]
        table_rows.append(f"<tr><td>{esc(label)}</td><td>{esc(best['display_name'])}</td><td>{eur(best['market_value'])}</td><td>{best['fit']:.0f}</td><td>{best['value']:.0f}</td><td>{best['safety']:.0f}</td><td>{best['score']:.0f}</td></tr>")
    short_body = f"""
    <div class="two-col wide-left">
      <div>{figure("candidate_map.png")}</div>
      <div>
        <table class="mini">
          <thead><tr><th>Need</th><th>Best balanced</th><th>Fee</th><th>Fit</th><th>Value</th><th>Safety</th><th>Score</th></tr></thead>
          <tbody>{''.join(table_rows)}</tbody>
        </table>
        <p class="small">The shortlist is a trade-off surface, not a single ranking. Cook is the value extreme. Gueye is the fit extreme. Coquelin is the balance.</p>
      </div>
    </div>
    """
    slides.append(slide("Shortlist", "The shortlist", short_body, 8))

    plan_body = f"""
    <div class="cards three">
      <div class="card"><div class="tag">CM</div><h2>Idrissa Gueye</h2><p class="club">Aston Villa</p><p class="fee">EUR 9m</p><p class="small">Fit 95 | Value 22 | Safety 91</p></div>
      <div class="card"><div class="tag">CB</div><h2>Steve Cook</h2><p class="club">AFC Bournemouth</p><p class="fee">EUR 3m</p><p class="small">Fit 57 | Value 100 | Safety 96</p></div>
      <div class="card"><div class="tag">ST</div><h2>Odion Ighalo</h2><p class="club">Watford</p><p class="fee">EUR 12m</p><p class="small">Fit 79 | Value 82 | Safety 96</p></div>
    </div>
    <div class="bottom-line"><span>Total EUR 24m</span><span>Left EUR 26m</span><span>Age 25 to 27</span><span>All three needs filled</span></div>
    <div class="outcome">
      <div><b>+80%</b><span>Gueye, 2016 to 2018</span></div>
      <div><b>+85%</b><span>Cook, 2016 to 2018</span></div>
      <div><b>-23%</b><span>Ighalo, 2016 to 2018</span></div>
    </div>
    <p class="small">Backtest, not a promise. Two hits and one miss. The plan leaves room for wages, agent fees and a January move.</p>
    """
    slides.append(slide("Recommendation", "The plan", plan_body, 9, dark=True))

    risk_body = f"""
    <div class="two-col">
      <div>
        <h2 class="sub">What could go wrong</h2>
        <ul class="risk">
          <li><b>Gueye's passing.</b> A safe short passer, not a creative progressor. Keep Drinkwater as the passer.</li>
          <li><b>Cook's step up.</b> Bournemouth defended deep. Pair him with a progressive partner.</li>
          <li><b>Ighalo's outlier.</b> One strong season at 27. Use him as rotation, not a long contract.</li>
          <li><b>Adaptation.</b> The 4-4-2 pressing triggers need pre-season work.</li>
        </ul>
      </div>
      <div>
        <h2 class="sub">What would change the answer</h2>
        <ul class="risk">
          <li>Budget minus 20%: the recommended plan still fits at EUR 24m.</li>
          <li>Budget minus 40%: the base plan still fits at EUR 27m.</li>
          <li>If the board wants a higher ceiling, Cook can become van Dijk for EUR 33m total.</li>
          <li>If the board wants more passing, Gueye can become Coquelin for EUR 27m.</li>
        </ul>
        <p class="small">Limitations: one league of event data, market value as a fee proxy, retrospective outcomes, noisy residuals.</p>
      </div>
    </div>
    """
    slides.append(slide("Decision quality", "Risks and what would change", risk_body, 10))

    close_body = f"""
    <p class="big-line">It does not pick a player. It makes the trade-offs visible.</p>
    <div class="three-cols">
      <div><h2>Reproduce</h2><p>python scripts/download_data.py<br>python scripts/build_all.py<br>python -m streamlit run app.py</p></div>
      <div><h2>Verify</h2><p>9 unit tests<br>Brute-force optimum matches MILP<br>All report numbers generated from scripts</p></div>
      <div><h2>Decide</h2><p>Fit, value and safety are explicit.<br>The weights are a choice.<br>The cash buffer is a decision.</p></div>
    </div>
    <p class="small">AI was used for scaffolding and drafting. The author checked the mapping, the model specification and the recommendation.</p>
    """
    slides.append(slide("Close", "A decision system, not a black box", close_body, 11))

    css = """
    @page { size: 13.333in 7.5in; margin: 0; }
    * { box-sizing: border-box; }
    html, body { margin: 0; padding: 0; background: #ffffff; }
    body { font-family: var(--font); color: #111111; }
    .slide { width: 13.333in; height: 7.5in; padding: 0.38in 0.55in 0.42in; position: relative; page-break-after: always; overflow: hidden; background: #ffffff; }
    .slide.dark { background: #181818; color: #f5f5f5; }
    .kicker { display: flex; justify-content: space-between; font-size: 10pt; letter-spacing: 0.12em; text-transform: uppercase; color: #666666; border-bottom: 1px solid #d8d8d8; padding-bottom: 5px; }
    .dark .kicker { color: #aaaaaa; border-color: #3a3a3a; }
    h1 { font-size: 36pt; line-height: 1.04; margin: 14pt 0 8pt; letter-spacing: -0.01em; max-width: 11.8in; text-wrap: balance; font-weight: 700; }
    h2 { font-size: 16pt; margin: 0 0 3pt; }
    .lede { font-size: 15pt; line-height: 1.28; color: #333333; max-width: 10.8in; }
    .dark .lede { color: #dddddd; }
    .body { margin-top: 8pt; }
    .footer { position: absolute; left: 0.55in; right: 0.55in; bottom: 0.18in; display: flex; justify-content: space-between; font-size: 8pt; color: #777777; border-top: 1px solid #dddddd; padding-top: 4px; }
    .dark .footer { color: #999999; border-color: #3a3a3a; }
    .small { font-size: 10pt; color: #555555; line-height: 1.35; }
    .dark .small { color: #bbbbbb; }
    .caption { font-size: 8pt; color: #666666; margin-top: 2pt; }
    .title-grid { display: grid; grid-template-columns: 1.05fr 1fr; gap: 0.35in; align-items: start; }
    .title-image figure { margin: 0; }
    .title-image img { width: 100%; max-height: 4.4in; object-fit: contain; }
    .author { font-size: 12pt; color: #333333; margin-top: 12pt; }
    .stats { display: flex; gap: 0.22in; margin-top: 14pt; flex-wrap: wrap; }
    .stats.four { margin-top: 10pt; }
    .stats.two { margin-top: 0; margin-bottom: 12pt; }
    .stat { border: 1px solid #d8d8d8; border-radius: 12px; background: #f7f7f7; padding: 10px 12px; min-width: 1.4in; }
    .stat b { display: block; font-size: 22pt; font-weight: 700; line-height: 1; }
    .stat span { display: block; font-size: 9pt; color: #555555; margin-top: 3pt; }
    .dark .stat { border-color: #3a3a3a; background: #1f1f1f; }
    .dark .stat span { color: #bbbbbb; }
    .cards { display: grid; gap: 0.18in; margin: 12pt 0; }
    .cards.three { grid-template-columns: repeat(3, 1fr); }
    .card { border: 1px solid #d8d8d8; border-radius: 12px; background: #f7f7f7; padding: 12pt 14pt; min-height: 1.6in; }
    .dark .card { background: #1f1f1f; border-color: #3a3a3a; }
    .tag { font-size: 8pt; letter-spacing: 0.12em; text-transform: uppercase; color: #666666; }
    .card h2 { font-size: 19pt; margin-top: 4pt; }
    .club { font-size: 10pt; color: #555555; margin: 0; }
    .dark .club { color: #bbbbbb; }
    .dark .tag { color: #aaaaaa; }
    .fee { font-size: 20pt; font-weight: 700; margin: 8pt 0 0; }
    .big-line { font-size: 30pt; font-weight: 700; line-height: 1.1; margin: 18pt 0 8pt; max-width: 11.8in; }
    .bottom-line { display: flex; gap: 0.25in; flex-wrap: wrap; border: 1px solid #d8d8d8; border-radius: 12px; background: #f7f7f7; padding: 10pt 14pt; margin: 10pt 0 8pt; font-size: 12pt; font-weight: 600; }
    .dark .bottom-line { border-color: #3a3a3a; background: #1f1f1f; }
    .pipeline { display: grid; grid-template-columns: repeat(5, 1fr); gap: 0.12in; margin: 16pt 0 10pt; }
    .step { border: 1px solid #d8d8d8; border-radius: 12px; background: #f7f7f7; padding: 9pt; min-height: 1.5in; }
    .step b { font-size: 8pt; color: #777777; }
    .step h2 { font-size: 12.5pt; margin: 4pt 0; }
    .step p { font-size: 9pt; color: #555555; line-height: 1.3; margin: 0; }
    .two-col { display: grid; grid-template-columns: 1.15fr 1fr; gap: 0.3in; align-items: start; }
    .two-col.wide-left { grid-template-columns: 1.55fr 1fr; }
    .two-col figure { margin: 0; }
    .two-col img { width: 100%; max-height: 4.0in; object-fit: contain; }
    .rank-list { margin: 8pt 0; }
    .rank-list > div { display: flex; justify-content: space-between; border-bottom: 1px solid #dddddd; padding: 5pt 0; font-size: 12pt; }
    .rank-list b { font-size: 14pt; }
    .rank-list .muted { color: #888888; }
    .mini { width: 100%; border-collapse: collapse; font-size: 9pt; margin: 6pt 0; }
    .mini th { background: #e8e8e8; text-align: left; padding: 4pt; border-bottom: 1px solid #999999; }
    .mini td { padding: 4pt; border-bottom: 1px solid #dddddd; }
    .outcome { display: flex; gap: 0.25in; margin: 10pt 0 4pt; }
    .outcome > div { border: 1px solid #3a3a3a; border-radius: 12px; background: #1f1f1f; padding: 10px 12px; }
    .outcome b { display: block; font-size: 22pt; }
    .outcome span { display: block; font-size: 9pt; color: #bbbbbb; }
    .sub { font-size: 13pt; margin-top: 0; }
    .risk { font-size: 11.5pt; line-height: 1.35; padding-left: 16pt; margin: 4pt 0 10pt; }
    .risk li { margin-bottom: 5pt; }
    .three-cols { display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.25in; margin-top: 16pt; }
    .three-cols h2 { font-size: 13pt; }
    .three-cols p { font-size: 10pt; line-height: 1.4; color: #444444; }
    """

    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><title>Assignment 5 | Presentation</title><link rel="stylesheet" href="../assets/design.css"><style>{css}</style></head><body>
{''.join(slides)}
</body></html>"""


def print_pdf(html_path: Path, pdf_path: Path):
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(html_path.as_uri(), wait_until="load")
        page.pdf(
            path=str(pdf_path),
            width="13.333in",
            height="7.5in",
            print_background=True,
            prefer_css_page_size=True,
        )
        browser.close()


def main():
    html_path = PRES / "presentation.html"
    pdf_path = PRES / "Assignment5_Presentation.pdf"
    html_path.write_text(build(), encoding="utf-8")
    print_pdf(html_path, pdf_path)
    print("wrote", html_path)
    print("wrote", pdf_path)


if __name__ == "__main__":
    main()
