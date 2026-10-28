from __future__ import annotations

import base64
import json
import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from transfer_lab.config import FIGURES, OUTPUTS, PROCESSED, TABLES  # noqa: E402
from transfer_lab.names import clean_frame, clean_name  # noqa: E402
from transfer_lab.optimize import select  # noqa: E402

st.set_page_config(page_title="Transfer Decision Lab", page_icon="", layout="wide")

FONT_B64 = base64.b64encode((ROOT / "assets" / "fonts" / "Manrope-VariableFont_wght.ttf").read_bytes()).decode("ascii")

APP_CSS = """
<style>
  @font-face {
    font-family: "Manrope";
    src: url(data:font/ttf;base64,__FONT__) format("truetype");
    font-weight: 200 800;
    font-style: normal;
    font-display: swap;
  }
  :root {
    --font: "Manrope", "Segoe UI", sans-serif;
    --ink: #111111;
    --ink-soft: #333333;
    --muted: #5b5b5b;
    --line: #d8d8d8;
    --surface-2: #f7f7f7;
    --radius: 12px;
    --ease: cubic-bezier(0.22, 1, 0.36, 1);
  }
  html, body, [class*="css"] {font-family: var(--font); font-size: 16px; color: var(--ink);}
  .block-container {padding-top: 32px; padding-bottom: 48px; max-width: 1280px;}
  h1, h2, h3 {letter-spacing: -0.01em; text-wrap: balance; font-weight: 700;}
  h1 {font-size: 36px; line-height: 40px; margin: 0 0 12px;}
  h2 {font-size: 24px; line-height: 32px; margin: 24px 0 8px;}
  h3 {font-size: 18px; line-height: 28px; margin: 16px 0 4px;}
  p {font-size: 16px; line-height: 24px; margin: 0 0 12px; text-wrap: pretty;}
  a {color: var(--ink); text-decoration: underline; text-underline-offset: 3px;}
  [data-testid="stMetricValue"] {font-size: 24px; line-height: 32px; font-weight: 700;}
  [data-testid="stMetricLabel"] {font-size: 14px; line-height: 20px; color: var(--muted);}
  [data-testid="stSidebar"] {background: var(--surface-2); border-right: 1px solid #e5e5e5;}
  [data-testid="stSidebar"] p, [data-testid="stSidebar"] label {font-size: 14px; line-height: 20px;}
  [data-testid="stVerticalBlockBorderWrapper"] {border: 1px solid var(--line) !important; border-radius: var(--radius) !important; background: #ffffff; padding: 16px !important;}
  [data-testid="stCaptionContainer"] p {font-size: 14px; line-height: 20px; color: var(--muted);}
  .callout {border: 1px solid var(--line); background: var(--surface-2); border-radius: var(--radius); padding: 16px 20px; margin: 16px 0 24px; font-size: 16px; line-height: 24px;}
  .small {color: var(--muted); font-size: 14px; line-height: 20px;}
  .rule {border-top: 1px solid var(--line); margin: 16px 0 24px;}
  .pill {display: inline-block; border: 1px solid var(--line); border-radius: 8px; padding: 2px 8px; margin-right: 6px; font-size: 14px; line-height: 20px; color: var(--ink-soft);}
  .stButton > button {border-radius: 8px; font-family: var(--font); font-weight: 700;}
  [data-testid="stToolbar"] {visibility: hidden;}
  #MainMenu {visibility: hidden;}
  footer {visibility: hidden;}
</style>
""".replace("__FONT__", FONT_B64)
st.markdown(APP_CSS, unsafe_allow_html=True)

PRESETS = {
    "Recommended": {"fit": 0.40, "value": 0.20, "safety": 0.40},
    "Balanced": {"fit": 0.55, "value": 0.25, "safety": 0.20},
    "Value first": {"fit": 0.35, "value": 0.45, "safety": 0.20},
    "Quality first": {"fit": 0.75, "value": 0.10, "safety": 0.15},
}


@st.cache_data
def load_data():
    cand = clean_frame(pd.read_csv(TABLES / "candidates.csv"))
    decision = clean_frame(pd.read_csv(TABLES / "decision.csv"))
    scenarios = pd.read_csv(TABLES / "scenarios.csv")
    case = clean_frame(pd.read_csv(PROCESSED / "case_players.csv"))
    predictions = clean_frame(pd.read_csv(TABLES / "case_predictions.csv"))
    backtest = clean_frame(pd.read_csv(TABLES / "case_backtest_players.csv"))
    local_metrics = pd.read_csv(TABLES / "backtest_local.csv")
    global_metrics = pd.read_csv(TABLES / "backtest_global.csv")
    summary = json.loads((OUTPUTS / "decision_summary.json").read_text(encoding="utf-8"))
    value_summary = json.loads((OUTPUTS / "value_model_summary.json").read_text(encoding="utf-8"))
    return cand, decision, scenarios, case, predictions, backtest, local_metrics, global_metrics, summary, value_summary


cand, decision, scenarios, case, predictions, backtest, local_bt, global_bt, summary, value_summary = load_data()

st.title("Transfer Decision Lab")
st.markdown(
    '<div class="small">Leicester City, summer 2016. Replace N\'Golo Kanté, rebuild the spine, keep the budget. All numbers use information available at the 1 July 2016 cutoff. The 2016 to 2018 market values are used only for the validation, never for the recommendation.</div>',
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Decision settings")
    preset = st.selectbox("Preference preset", list(PRESETS), index=0)
    weights = PRESETS[preset]
    budget_m = st.slider("Transfer budget, EUR million", 20, 60, 50, 1)
    max_risk = st.slider("Maximum risk score", 20, 90, 70, 5)
    max_age = st.slider("Maximum age", 21, 30, 29, 1)
    st.markdown(
        f'<div class="small">Weights: fit {weights["fit"]:.2f}, value {weights["value"]:.2f}, safety {weights["safety"]:.2f}</div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="rule"></div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="small">The optimizer fills three needs: central midfield, centre back and centre forward. Market value is used as the fee proxy because most 2016 fees are not public at the cutoff.</div>',
        unsafe_allow_html=True,
    )

plan = select(cand, budget_m * 1_000_000, weights, max_risk, max_age)

tabs = st.tabs(["Decision", "Squad need", "Market", "Shortlist", "Method"])

with tabs[0]:
    if not plan.get("feasible"):
        st.warning("No feasible plan under these constraints. Increase the budget, relax the risk limit or raise the age limit.")
    else:
        sel = clean_frame(plan["selected"])
        st.subheader("The plan")
        cols = st.columns(4)
        cols[0].metric("Players", len(sel))
        cols[1].metric("Fees", f"EUR {plan['cost']/1e6:.1f}m")
        cols[2].metric("Budget left", f"EUR {plan['leftover']/1e6:.1f}m")
        cols[3].metric("Plan score", f"{plan['score']:.1f}")
        if plan.get("relaxed"):
            st.caption("The budget does not cover all three needs. The optimizer selected a subset.")
        for _, row in sel.iterrows():
            with st.container(border=True):
                left, mid, right = st.columns([2.2, 1.4, 1.4])
                left.markdown(f"**{row['display_name']}**  \n{row['team_name']}  \n{row['need']} · age {row['age']:.0f} · {row['minutes']:.0f} minutes")
                mid.metric("Fee", f"EUR {row['market_value']/1e6:.0f}m")
                right.metric("Fit / value / safety", f"{row['fit']:.0f} / {row['value']:.0f} / {row['safety']:.0f}")
                st.caption(
                    f"Market value gap: {row['local_discount_pct']:+.0f}% local, {row['global_discount_pct']:+.0f}% global. "
                    f"Role cluster: {row.get('cluster_label', 'not available')}."
                )
        st.markdown(
            f'<div class="callout">The recommendation is a portfolio, not a ranking. Kanté is unique: the closest profile (Gueye) is fairly priced, so the value model does not call him a bargain. The money is made on Cook, while Ighalo supplies a proven box threat at a modest fee. The plan leaves EUR {plan["leftover"]/1e6:.0f}m for wages, agent fees and a January buffer.</div>',
            unsafe_allow_html=True,
        )
        st.subheader("Alternatives")
        alt = decision.pivot_table(index="plan", columns="need", values="display_name", aggfunc="first").reset_index()
        alt = alt.rename(columns={"plan": "Plan", "CB": "Centre back", "CM": "Central midfield", "ST": "Centre forward"})
        st.dataframe(alt, hide_index=True, use_container_width=True)
        st.caption("Recommended uses the fit and availability weights. Value prioritises the market gap. Fit prioritises the tactical profile.")
        st.subheader("What happened next")
        hist = sel.merge(backtest[["player_id", "value_1y", "value_2y", "growth_2y"]], on="player_id", how="left")
        hist = hist[["display_name", "market_value", "value_1y", "value_2y", "growth_2y"]].copy()
        hist.columns = ["Player", "Value 2016", "Value 2017", "Value 2018", "Growth 2016 to 2018"]
        for col in ["Value 2016", "Value 2017", "Value 2018"]:
            hist[col] = hist[col].map(lambda v: f"EUR {v/1e6:.1f}m" if pd.notna(v) else "n/a")
        hist["Growth 2016 to 2018"] = hist["Growth 2016 to 2018"].map(lambda v: f"{v*100:+.0f}%" if pd.notna(v) else "n/a")
        st.dataframe(hist, hide_index=True, use_container_width=True)
        st.caption("This is a backtest, not a promise. One hit, one flat outcome and one miss is a realistic result for a three-player plan.")

with tabs[1]:
    st.subheader("What Leicester were")
    c1, c2 = st.columns([1.2, 1])
    with c1:
        if (FIGURES / "leicester_style.png").exists():
            st.image(str(FIGURES / "leicester_style.png"), use_container_width=True)
        if (FIGURES / "kante_actions.png").exists():
            st.image(str(FIGURES / "kante_actions.png"), use_container_width=True)
    with c2:
        st.markdown(
            "Leicester won the league with 42.6% possession, the lowest pass completion in the league and the highest xG per match. "
            "They defended deep, attacked directly and scored from set pieces and counters. The style did not require a midfield playmaker. "
            "It required a midfielder who could cover ground, win the ball back and carry it forward."
        )
        if (FIGURES / "kante_percentiles.png").exists():
            st.image(str(FIGURES / "kante_percentiles.png"), use_container_width=True)
        st.markdown(
            '<div class="callout">Kanté was a 100th percentile ball winner among Premier League midfielders, with 17.1 tackles, interceptions and recoveries per 90. '
            "He was not a high-volume passer: 44 passes per 90 and the 34th percentile for progressive passes. The replacement profile should mirror that asymmetry.</div>",
            unsafe_allow_html=True,
        )
    st.subheader("The three needs")
    needs = pd.DataFrame(
        [
            ["Central midfield", "Replace Kanté", "Elite ball winning, pressing, carries, Premier League readiness", "Gueye, Coquelin, Wanyama"],
            ["Centre back", "Succession for Huth and Morgan", "Clearances, blocks, aerial duels, enough passing to escape the block", "Cook, van Dijk, Funes Mori"],
            ["Centre forward", "Depth and competition for Vardy", "Box threat, shots, xG, pressing, affordable fee", "Ighalo, Deeney, King"],
        ],
        columns=["Need", "Why", "Profile", "Candidates"],
    )
    st.dataframe(needs, hide_index=True, use_container_width=True)

with tabs[2]:
    st.subheader("Two value models")
    st.markdown(
        "The global model learns market pricing across 30,939 player seasons in the top five leagues from 2010/11 to 2024/25. "
        "The local model learns the 2015/16 Premier League cross-section from real match actions. Both predict value relative to the league median, so inflation is removed."
    )
    if (FIGURES / "value_parity.png").exists():
        st.image(str(FIGURES / "value_parity.png"), use_container_width=True)
    m1, m2, m3 = st.columns(3)
    glob = value_summary["global_metrics"]["lightgbm"]
    loc = value_summary["local_metrics"]["full"]
    m1.metric("Global R2", f"{glob['r2']:.3f}")
    m2.metric("Local R2", f"{loc['r2']:.3f}")
    m3.metric("Local Spearman", f"{loc['spearman']:.3f}")
    st.caption("Global test seasons: 2021/22 to 2024/25, n=9,015. Local model: 2015/16 Premier League, n=285, 5-fold out-of-fold predictions.")
    if (FIGURES / "backtest_uplift.png").exists():
        st.image(str(FIGURES / "backtest_uplift.png"), use_container_width=True)
    st.markdown(
        '<div class="callout">The market rewards goals, assists, pass volume and club reputation. Defensive actions enter the local model with negative coefficients once position and possession are controlled. '
        "That is a market bias, not a football verdict. Gueye is fairly priced by the market and still the closest tactical match to Kanté. The value gap is a signal, not a target.</div>",
        unsafe_allow_html=True,
    )
    st.subheader("Metrics")
    metrics = pd.DataFrame(
        [
            ["Global baseline", value_summary["global_metrics"]["baseline_role_median"]["mae"], value_summary["global_metrics"]["baseline_role_median"]["r2"], value_summary["global_metrics"]["baseline_role_median"]["spearman"]],
            ["Global ridge", value_summary["global_metrics"]["ridge"]["mae"], value_summary["global_metrics"]["ridge"]["r2"], value_summary["global_metrics"]["ridge"]["spearman"]],
            ["Global LightGBM", value_summary["global_metrics"]["lightgbm"]["mae"], value_summary["global_metrics"]["lightgbm"]["r2"], value_summary["global_metrics"]["lightgbm"]["spearman"]],
            ["Local baseline", value_summary["local_metrics"]["baseline"]["mae"], value_summary["local_metrics"]["baseline"]["r2"], value_summary["local_metrics"]["baseline"]["spearman"]],
            ["Local full", value_summary["local_metrics"]["full"]["mae"], value_summary["local_metrics"]["full"]["r2"], value_summary["local_metrics"]["full"]["spearman"]],
        ],
        columns=["Model", "MAE, log", "R2", "Spearman"],
    )
    st.dataframe(metrics.style.format({"MAE, log": "{:.3f}", "R2": "{:.3f}", "Spearman": "{:.3f}"}), hide_index=True, use_container_width=True)

with tabs[3]:
    st.subheader("Candidate map")
    need_filter = st.multiselect("Needs", ["CM", "CB", "ST"], default=["CM", "CB", "ST"])
    part = cand[
        (cand["need"].isin(need_filter))
        & (cand["risk"] <= max_risk)
        & (cand["age"] <= max_age)
        & (cand["market_value"] <= budget_m * 1_000_000)
    ].copy()
    fig = go.Figure()
    for i, need in enumerate(["CM", "CB", "ST"]):
        g = part[part["need"] == need]
        fig.add_trace(
            go.Scatter(
                x=g["value"],
                y=g["fit"],
                mode="markers",
                name=need,
                text=g["display_name"] + "<br>" + g["team_name"] + "<br>EUR " + (g["market_value"] / 1e6).round(1).astype(str) + "m",
                hovertemplate="%{text}<br>Fit %{y:.0f}, value %{x:.0f}<extra></extra>",
                marker=dict(size=8 + g["market_value"] / 4e6, color=["#222222", "#777777", "#b5b5b5"][i], line=dict(color="#333333", width=0.5)),
            )
        )
    fig.update_layout(
        height=430,
        margin=dict(l=10, r=10, t=20, b=10),
        xaxis_title="Value score, percentile",
        yaxis_title="Fit score",
        legend=dict(orientation="v", x=1.02, y=1.0),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="Manrope, Segoe UI, sans-serif", color="#222222"),
    )
    fig.update_xaxes(range=[-3, 103], gridcolor="#eeeeee")
    fig.update_yaxes(range=[-3, 103], gridcolor="#eeeeee")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Shortlist")
    show = part.sort_values(["need", "score"], ascending=[True, False]).copy()
    show["fee_m"] = (show["market_value"] / 1e6).round(1)
    table = show[["need", "display_name", "team_name", "age", "minutes", "fee_m", "fit", "value", "safety", "score", "cluster_label"]].copy()
    table.columns = ["Need", "Player", "Club", "Age", "Minutes", "Fee, EUR m", "Fit", "Value", "Safety", "Score", "Role cluster"]
    st.dataframe(
        table.style.format({"Age": "{:.1f}", "Minutes": "{:.0f}", "Fee, EUR m": "{:.1f}", "Fit": "{:.0f}", "Value": "{:.0f}", "Safety": "{:.0f}", "Score": "{:.0f}"}),
        hide_index=True,
        use_container_width=True,
        height=360,
    )
    st.download_button("Download shortlist CSV", table.to_csv(index=False), file_name="leicester_2016_shortlist.csv", mime="text/csv")

    st.subheader("Player detail")
    names = show["display_name"].tolist()
    if names:
        pick = st.selectbox("Player", names)
        row = show[show["display_name"] == pick].iloc[0]
        d1, d2, d3, d4 = st.columns(4)
        d1.metric("Fee proxy", f"EUR {row['market_value']/1e6:.1f}m")
        d2.metric("Fit", f"{row['fit']:.0f}")
        d3.metric("Value", f"{row['value']:.0f}")
        d4.metric("Safety", f"{row['safety']:.0f}")
        metrics_by_need = {
            "CM": [("ball_winning_p90", "Ball winning"), ("pressures_p90", "Pressures"), ("progressive_passes_p90", "Progressive passes"), ("progressive_carries_p90", "Progressive carries"), ("pass_completion", "Pass completion"), ("minutes", "Minutes")],
            "CB": [("clearances_p90", "Clearances"), ("blocks_p90", "Blocks"), ("interceptions_p90", "Interceptions"), ("aerials_lost_p90", "Aerial duels lost"), ("progressive_passes_p90", "Progressive passes"), ("pass_completion", "Pass completion")],
            "ST": [("xg_p90", "xG per 90"), ("shots_p90", "Shots per 90"), ("touches_box_p90", "Touches in box"), ("progressive_carries_p90", "Progressive carries"), ("pressures_p90", "Pressures"), ("minutes", "Minutes")],
        }
        pool = cand[cand["need"] == row["need"]]
        items = []
        for col, label in metrics_by_need[row["need"]]:
            pct = (pool[col] <= row[col]).mean() * 100
            items.append((label, pct, row[col]))
        detail = pd.DataFrame(items, columns=["Metric", "Percentile", "Value"])
        bar = go.Figure(go.Bar(x=detail["Percentile"], y=detail["Metric"], orientation="h", marker_color="#333333", text=detail["Percentile"].round(0), textposition="outside"))
        bar.update_layout(height=300, margin=dict(l=10, r=10, t=10, b=10), xaxis=dict(range=[0, 105], title="Percentile in the need pool"), yaxis=dict(autorange="reversed"), plot_bgcolor="white", paper_bgcolor="white", font=dict(family="Manrope, Segoe UI, sans-serif", color="#222222"))
        st.plotly_chart(bar, use_container_width=True)
        st.caption(
            f"Local market gap {row['local_discount_pct']:+.0f}%, global gap {row['global_discount_pct']:+.0f}%. "
            f"Risk {row['risk']:.0f}, age {row['age']:.1f}, {row['minutes']:.0f} minutes. Role cluster: {row['cluster_label']}."
        )

    st.subheader("Build a plan")
    picks = {}
    cols = st.columns(3)
    for col, need in zip(cols, ["CM", "CB", "ST"]):
        options = part[part["need"] == need].sort_values("score", ascending=False)["display_name"].tolist()
        if options:
            default = options[0]
            picks[need] = col.selectbox(f"{need} pick", options, index=0, key=f"pick_{need}")
    if len(picks) == 3:
        chosen = part[part["display_name"].isin(picks.values())].copy()
        chosen["score_w"] = chosen["fit"] * weights["fit"] + chosen["value"] * weights["value"] + chosen["safety"] * weights["safety"]
        total_cost = chosen["market_value"].sum()
        st.markdown(
            f"**Fees:** EUR {total_cost/1e6:.1f}m · **Left:** EUR {(budget_m*1e6-total_cost)/1e6:.1f}m · **Portfolio score:** {chosen['score_w'].sum():.1f}"
        )
        st.dataframe(chosen[["need", "display_name", "team_name", "market_value", "fit", "value", "safety", "score_w"]].style.format({"market_value": "EUR {:,.0f}", "fit": "{:.0f}", "value": "{:.0f}", "safety": "{:.0f}", "score_w": "{:.1f}"}), hide_index=True, use_container_width=True)

with tabs[4]:
    st.subheader("Method")
    st.markdown(
        "Problem: Leicester City enter the summer 2016 window as champions, lose N'Golo Kanté and must replace his defensive and carrying output under a limited budget. "
        "The decision is which three players to sign, at what fee, and which risks to accept."
    )
    st.markdown(
        "Data: StatsBomb open data for all 380 Premier League matches in 2015/16 (events, lineups, 10,385 player-match rows). "
        "Transfermarkt datalake for 92,671 player profiles, 901,429 market values, 1.88 million performance rows, 1.1 million transfers and injury records. "
        "The analysis cutoff is 1 July 2016. Raw data is not committed; the download script and processed tables are."
    )
    st.markdown(
        "Pipeline: parse events, build per-90 profiles, cluster roles, train two value models, score candidates on fit, value and risk, then solve a budget-constrained binary optimisation. "
        "The local model uses 5-fold out-of-fold predictions. The global model is trained on seasons up to 2020/21 and tested on 2021/22 to 2024/25."
    )
    st.subheader("Validation")
    v1, v2, v3 = st.columns(3)
    v1.metric("Global MAE", f"{value_summary['global_metrics']['lightgbm']['mae']:.3f}")
    v2.metric("Local R2", f"{value_summary['local_metrics']['full']['r2']:.3f}")
    v3.metric("Local 2-year hit rate", f"{local_bt[local_bt['horizon_years']==2]['hit_rate_undervalued'].iloc[0]*100:.1f}%")
    st.markdown(
        "The local backtest flags the bottom 20% of residuals as undervalued. Over two years their median market value rose 11.8%, while the rest fell 10.9%. "
        "The hit rate was 52.8% against 35.8%. The global model's undervalued quintile beat the rest in all 10 evaluation seasons on a relative basis, although absolute values fell in several seasons. "
        "The signal is modest and should not be treated as a forecast."
    )
    st.subheader("Limitations")
    st.markdown(
        "- Market value is a fee proxy, not a transfer fee. Fees also depend on contract length, clauses, agent fees and competition.\n"
        "- The Transfermarkt minutes column is unreliable for some high scorers: it stores minutes per goal for several rows. The local model uses StatsBomb minutes; the global model avoids minutes and uses appearances.\n"
        "- StatsBomb open data covers one Premier League season fully. The case is retrospective and the candidate pool is limited to the league.\n"
        "- Position labels come from formation slots, not roles. Ramsey is listed as a defensive midfielder but does not play like Kanté. The similarity score, not the label, drives the midfield fit.\n"
        "- The value model learns market prices, including the market's bias against defensive actions. A negative gap does not mean a player is bad value for the club.\n"
        "- The 2016 to 2018 outcomes are hindsight. They validate the method, not the decision process.\n"
        "- Correlation is not causation: a high fit score does not guarantee that a signing improves the team."
    )
    st.subheader("AI use")
    st.markdown(
        "LLM assistance was used for code scaffolding, data checks and drafting. All metrics, tables and figures are produced by the committed scripts. "
        "The author reviewed the data mapping, the model specification and the backtest. AI did not make the final selection; the decision rule and the scenario weights are explicit and reproducible."
    )
    st.subheader("Reproduce")
    st.code(
        "pip install -r requirements.txt\n"
        "python scripts/download_data.py\n"
        "python scripts/build_all.py\n"
        "streamlit run app.py",
        language="bash",
    )
    st.caption("Author: Dinmukhammed Mynzhassar, AAI-2504M. Case: Leicester City, summer 2016. Data: StatsBomb open data and Transfermarkt datalake.")
