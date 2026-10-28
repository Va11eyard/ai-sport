from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from transfer_lab.names import clean_name, clean_frame  # noqa: E402

OUT = ROOT / "outputs"
FIG = OUT / "figures"
TAB = OUT / "tables"
REPORT = ROOT / "report"
REPORT.mkdir(exist_ok=True)


def sanitize(text: object) -> str:
    value = str(text)
    value = value.replace("\u2014", ", ").replace("\u2013", "-")
    value = value.replace("\u2192", "to").replace("\u2190", "from").replace("\u00bb", " ")
    return value


def eur(value: float) -> str:
    return f"EUR {value/1e6:.1f}m"


def pct(value: float, signed: bool = False) -> str:
    return f"{value*100:+.1f}%" if signed else f"{value*100:.1f}%"


def load_all():
    value = json.loads((OUT / "value_model_summary.json").read_text(encoding="utf-8"))
    decision = json.loads((OUT / "decision_summary.json").read_text(encoding="utf-8"))
    cand = clean_frame(pd.read_csv(TAB / "candidates.csv"))
    scen = pd.read_csv(TAB / "scenarios.csv")
    dec = clean_frame(pd.read_csv(TAB / "decision.csv"))
    local_bt = pd.read_csv(TAB / "backtest_local.csv")
    global_bt = pd.read_csv(TAB / "backtest_global.csv")
    sens = pd.read_csv(TAB / "sensitivity.csv")
    return value, decision, cand, scen, dec, local_bt, global_bt, sens


VALUE, DECISION, CAND, SCEN, DEC, LOCAL_BT, GLOBAL_BT, SENS = load_all()
G = VALUE["global_metrics"]
L = VALUE["local_metrics"]
REC = DECISION["recommended"]
VAL = DECISION["value"]
FIT = DECISION["fit"]


def plan_players(plan: str) -> pd.DataFrame:
    return DEC[DEC["plan"] == plan].copy()


def table_top(need: str, n: int = 5) -> pd.DataFrame:
    part = CAND[CAND["need"] == need].sort_values("score", ascending=False).head(n).copy()
    part["fee"] = (part["market_value"] / 1e6).round(1)
    return part


class Blocks:
    def __init__(self):
        self.items = []

    def cover(self, **kw):
        self.items.append(("cover", kw))

    def h1(self, text):
        self.items.append(("h1", text))

    def h2(self, text):
        self.items.append(("h2", text))

    def p(self, text, lead=None):
        self.items.append(("p", {"text": text, "lead": lead}))

    def bullets(self, items):
        self.items.append(("bullets", items))

    def table(self, headers, rows, caption=None):
        self.items.append(("table", {"headers": headers, "rows": rows, "caption": caption}))

    def figure(self, filename, caption):
        self.items.append(("figure", {"filename": filename, "caption": caption}))

    def pagebreak(self):
        self.items.append(("pagebreak", None))


def build_blocks() -> Blocks:
    b = Blocks()
    b.cover(
        title="AI Football Intelligence",
        subtitle="From data to transfer decisions",
        assignment="Assignment 5",
        case="Replacing N'Golo Kanté at Leicester City, summer 2016",
        author="Dinmukhammed Mynzhassar, Laura Duisenova, Zhaidar Kairat",
        team="AAI-2504M",
        date="October 2026",
        strip=[
            ("Decision", "Sign Gueye, Cook and Ighalo for EUR 24m"),
            ("Budget", "EUR 50m, leaving EUR 26m"),
            ("Evidence", "380 real matches, 30,939 player-seasons"),
        ],
    )

    b.h1("Executive summary")
    b.p(
        "Leicester City won the Premier League in 2015/16 and lost N'Golo Kanté to Chelsea weeks later. "
        "The club had to replace a midfielder who was a 100th percentile ball winner, keep the counterattacking style and stay inside a limited budget. "
        "This report builds a transfer decision system from two independent data sources: StatsBomb event data for all 380 Premier League matches and a Transfermarkt datalake with market values, performances, transfers and injuries."
    )
    b.p(
        "The recommended plan signs Idrissa Gueye from Aston Villa for EUR 9m, Steve Cook from AFC Bournemouth for EUR 3m and Odion Ighalo from Watford for EUR 12m. "
        "The three fees total EUR 24m and leave EUR 26m for wages, agent fees and a January buffer. "
        "Gueye is the closest real-match profile to Kanté (cosine similarity 0.93, 100th percentile ball winning). "
        "Cook is the strongest value signal in the candidate pool, with a local market gap of +61% and a global gap of +64% at a EUR 3m fee. "
        "Ighalo is the best available box threat, with 15 league goals and 16.9 xG in 2015/16."
    )
    b.p(
        "The evidence is deliberately separated from the recommendation. "
        "The global market model reaches R2 0.734 and Spearman 0.855 on future seasons. "
        "The local model reaches R2 0.614 against 0.495 for a baseline that knows only age, minutes, role and club rank. "
        "Players flagged as undervalued in 2015/16 gained 11.8% in market value over the next two years, while the rest lost 10.9%. "
        "The hit rate was 52.8% against 35.8%. The signal is useful but modest, and the decision rule says so."
    )
    b.p(
        "The plan is a portfolio, not a ranking. Kanté is unique and Gueye is fairly priced by the market, so the value model does not call him a bargain. "
        "The money is made on Cook, while Ighalo supplies a proven box threat at a modest fee. "
        "The report also shows what happened after 2016: Gueye and Cook gained value, Ighalo lost value, and the plan gained 52% in total. "
        "That is a backtest, not a promise, and it is used only to judge the method. The plan had two hits and one miss."
    )

    b.h1("1. Problem and decision")
    b.h2("The situation")
    b.p(
        "Leicester City finished the 2015/16 season with 81 points, 68 goals scored and 36 conceded. "
        "They won the league with 42.6% average possession, the lowest pass completion in the division and the highest xG per match. "
        "N'Golo Kanté played 37 of the 38 league matches and 3,019 minutes. "
        "He then joined Chelsea for a reported EUR 35.8m fee, against a market value of EUR 20m on 1 July 2016. "
        "The transfer was a sporting loss and a financial gain at the same time."
    )
    b.p(
        "The decision is not simply to buy the player with the highest rating. "
        "Leicester needed a midfielder who could replace Kanté's defensive volume and carrying, a centre back who could succeed Robert Huth and Wes Morgan, and a forward who could compete with Jamie Vardy and Shinji Okazaki. "
        "The budget is EUR 50m in fees. Age, availability, injury history and tactical fit all matter. "
        "The sporting director has to choose three players, not rank a list."
    )
    b.h2("Research questions")
    b.bullets(
        [
            "What exactly made Kanté valuable in Leicester's style, measured from real match actions rather than reputation?",
            "Which 2015/16 Premier League players reproduce that profile, and which of them are mispriced by the market?",
            "Which three-player plan maximises tactical fit, market value and availability under a EUR 50m fee budget?",
            "How reliable is the evidence, and which limitations would change the answer?",
        ]
    )
    b.p(
        "The case is retrospective. The analysis uses only information available on 1 July 2016 for the recommendation. "
        "Market values from 2017 and 2018 are used only for validation and for the what happened next section. "
        "This avoids the usual trap of a 2026 scouting report that has no observable outcome."
    )

    b.pagebreak()
    b.h1("2. Data")
    b.h2("Sources and coverage")
    b.p(
        "The project combines event-level match data with market data. "
        "StatsBomb open data provides the 2015/16 Premier League season: 380 matches, 10,385 player-match rows and 548 players. "
        "Each match file contains every pass, carry, shot, pressure, tackle, interception, clearance and recovery with coordinates and pressure flags. "
        "Lineups provide formation slots and minutes."
    )
    b.p(
        "The Transfermarkt datalake provides 92,671 player profiles, 901,429 market value observations, 1,878,719 player-season performance rows, 1,101,440 transfer records and injury histories. "
        "For the market model the analysis uses the top five leagues from 2010/11 to 2024/25, giving 30,939 player-seasons with a market value and at least five appearances. "
        "The case cutoff is 1 July 2016. Market values are in euros."
    )
    b.table(
        ["Source", "What it provides", "Scale", "Use"],
        [
            ["StatsBomb open data", "Premier League 2015/16 events and lineups", "380 matches, 10,385 player-match rows, 548 players", "Real match style, Kanté profile, local value model, candidate fit"],
            ["Transfermarkt datalake", "Profiles, market values, performances, transfers, injuries", "92,671 profiles, 901,429 values, 1.88m performance rows, 1.1m transfers", "Global value model, case values, fees proxy, risk"],
            ["Analysis cohort", "Top five leagues, 2010/11 to 2024/25", "30,939 player-seasons", "Market model training and temporal validation"],
        ],
        "Table 1: Data sources and scale",
    )
    b.h2("Preparation and matching")
    b.p(
        "The raw data is not committed to the repository because the event files alone are about 1.1 GB. "
        "The download script recreates it from public URLs, and the processed tables are committed so the app runs offline. "
        "Market value at the cutoff is the latest observation on or before 1 July 2016, with a maximum staleness of 550 days. "
        "Season end values use 1 July of the following year."
    )
    b.p(
        "Player matching between StatsBomb and Transfermarkt uses normalized names, club mapping, position group and nationality, with rapidfuzz scores and manual checks. "
        "Of 421 StatsBomb players with at least 300 minutes, 408 are mapped. The 13 low-confidence matches are rejected rather than forced. "
        "All shortlisted players and the Leicester squad were checked by hand. "
        "The candidate pool requires at least 1,500 minutes, which excludes players whose per-90 rates are unstable."
    )
    b.p(
        "Two data quality problems shaped the method. First, the Transfermarkt minutes column is unreliable for some high scorers: Harry Kane is listed with 135 minutes and 25 goals, Jamie Vardy with 131 minutes and 24 goals. "
        "The column behaves like minutes per goal in those rows. The local model therefore uses StatsBomb minutes, and the global model avoids minutes entirely and uses appearances and starts. "
        "Second, some 2015/16 profiles are missing from the datalake, including Charlie Daniels, Daryl Janmaat and Lee Cattermole. "
        "The matching keeps only verified players, and the report states that the candidate pool is a sample of the league, not a complete market."
    )
    b.table(
        ["Check", "Result", "Action"],
        [
            ["StatsBomb matches", "380 of 380", "Full season used"],
            ["Leicester matches", "38", "Club style and Kanté actions"],
            ["StatsBomb players", "548", "10,385 player-match rows"],
            ["Mapped players", "408 of 421 with 300+ minutes", "13 low-confidence matches rejected"],
            ["Candidate pool", "19 central midfielders, 13 centre backs, 8 centre forwards", "1,500+ minutes, age limit, EUR 1m to EUR 30m"],
            ["Market cohort", "30,939 player-seasons", "Top five leagues, 2010/11 to 2024/25"],
        ],
        "Table 2: Coverage and validation checks",
    )

    b.h1("3. What Leicester were")
    b.p(
        "The style analysis uses the full season, not a highlight reel. "
        "Leicester had 42.6% possession against a league average of 50.0%, completed 68.0% of passes against 75.4%, and played 23.4% of passes long against 19.8%. "
        "They created 1.74 xG per match against a league average of 1.28 and conceded 1.21 against 1.28. "
        "Counterattacks produced 9.2% of their xG against 5.7% for the league, and set pieces produced 15.1% against 7.1%. "
        "This was a low-possession, direct, set-piece-heavy and counterattacking team."
    )
    b.figure("leicester_style.png", "Figure 1: Leicester 2015/16 style fingerprint, in standard deviations from the league average. Raw values are shown next to each label.")
    b.p(
        "The style matters for the replacement. A possession midfielder who needs the ball at his feet would change the team's shape. "
        "Leicester needed someone who could cover ground without the ball, win it back and carry it into space. "
        "The event data makes that requirement measurable."
    )
    b.figure("kante_actions.png", "Figure 2: Kanté's defensive actions and progressive passes and carries across 37 matches. The left panel has 1,594 defensive actions, the right panel 545 progressive passes and carries.")
    b.p(
        "Kanté's percentile ranks among Premier League midfielders with at least 900 minutes are extreme: 100th for ball winning, recoveries, tackles and interceptions, 98th for pressures, 72nd for progressive carries. "
        "He is not a high-volume passer: 44 passes per 90, 34th percentile for progressive passes and 54th for pass completion. "
        "The asymmetry is the point. Leicester did not need a deep-lying playmaker. They needed a destroyer who could also carry the ball."
    )
    b.figure("kante_percentiles.png", "Figure 3: Kanté percentile ranks among Premier League midfielders with 900+ minutes.")
    b.p(
        "A k-means clustering of all outfield players with 900+ minutes, using ball winning, pressing, progression, shooting, box presence, clearing and passing security, produces six readable roles. "
        "Kanté sits in the ball winning and pressing cluster. The cluster map is a descriptive check, not the decision model. "
        "It shows that the candidate pool contains players with genuinely different functions, and that a formation label alone is not enough."
    )
    b.figure("cluster_map.png", "Figure 4: Role clusters from real match actions, projected on two principal components. Selected players are highlighted.")
    b.h2("The three needs")
    b.table(
        ["Need", "Why", "Required profile", "Pool"],
        [
            ["Central midfield", "Kanté leaves after 3,019 minutes", "Elite ball winning, pressing, carries, Premier League readiness", "19 players"],
            ["Centre back", "Huth is 32 and Morgan is 32", "Clearances, blocks, aerial duels, enough passing to escape the block", "13 players"],
            ["Centre forward", "Vardy is 29 and Okazaki is 30", "Box threat, shots, xG, pressing, affordable fee", "8 players"],
        ],
        "Table 3: The three squad needs and the candidate pool",
    )

    b.pagebreak()
    b.h1("4. Replacing Kanté")
    b.p(
        "The midfield fit score is built in two steps. "
        "First, ten per-90 metrics for each midfielder are standardized within the candidate pool: ball winning, pressures, progressive passes, progressive carries, pass completion, recoveries, tackles, interceptions, xG and shots. "
        "The cosine similarity between a candidate and Kanté is computed on that vector. "
        "Second, the similarity is combined with minutes and pass completion: 75% similarity, 15% minutes and 10% pass completion. "
        "The weights are explicit and can be changed in the app."
    )
    b.p(
        "Gueye is the closest match at 0.93 cosine. Jan Kirchhoff is second at 0.75, Victor Wanyama third at 0.70 and Francis Coquelin fourth at 0.68. "
        "Aaron Ramsey, listed by the data as a left defensive midfielder, has a similarity of about zero. "
        "That is a useful warning: formation labels are not roles. Ramsey is a box-to-box and attacking midfielder, not a Kanté replacement, and the similarity score captures it."
    )
    rows = []
    for need in ("CM", "CB", "ST"):
        for _, row in table_top(need, 5).iterrows():
            rows.append(
                [
                    need,
                    row["display_name"],
                    row["team_name"],
                    f"{row['age']:.1f}",
                    eur(row["market_value"]),
                    f"{row['fit']:.0f}",
                    f"{row['value']:.0f}",
                    f"{row['safety']:.0f}",
                    f"{row['score']:.0f}",
                    row.get("cluster_label", ""),
                ]
            )
    b.table(
        ["Need", "Player", "Club", "Age", "Fee", "Fit", "Value", "Safety", "Score", "Role cluster"],
        rows,
        "Table 4: Top five candidates per need after the filters. Fit, value and safety are 0 to 100 percentiles. Score uses the balanced weights 0.55 fit, 0.25 value and 0.20 safety.",
    )
    b.p(
        "The differences inside the midfield group are instructive. "
        "Coquelin has the best balanced score (79.9) because his market gap is large and his profile is still close to Kanté. "
        "Gueye has the best fit (95.3) but the weakest value score (22.1), because the market already prices his defensive output. "
        "Wanyama sits between them. "
        "The final choice depends on what the club is trying to buy: a bargain, a tactical facsimile or a robust portfolio."
    )

    b.h1("5. Market value models")
    b.h2("Global model")
    b.p(
        "The global model predicts log market value relative to the league-season median. "
        "The target removes inflation and league level: a player is priced against peers in the same league and season. "
        "Features are age, appearances, starts, substitute appearances, goals and assists per appearance, non-penalty goals, cards, injury days, height, club rank, league, position group, role and foot. "
        "Market value itself is never a feature. The model is trained on seasons up to 2020/21 and tested on 2021/22 to 2024/25, giving 9,015 held-out player-seasons."
    )
    b.table(
        ["Model", "MAE, log", "RMSE, log", "R2", "Spearman"],
        [
            ["Role median baseline", f"{G['baseline_role_median']['mae']:.3f}", f"{G['baseline_role_median']['rmse']:.3f}", f"{G['baseline_role_median']['r2']:.3f}", f"{G['baseline_role_median']['spearman']:.3f}"],
            ["Ridge regression", f"{G['ridge']['mae']:.3f}", f"{G['ridge']['rmse']:.3f}", f"{G['ridge']['r2']:.3f}", f"{G['ridge']['spearman']:.3f}"],
            ["LightGBM", f"{G['lightgbm']['mae']:.3f}", f"{G['lightgbm']['rmse']:.3f}", f"{G['lightgbm']['r2']:.3f}", f"{G['lightgbm']['spearman']:.3f}"],
        ],
        "Table 5: Global market value model, holdout seasons 2021/22 to 2024/25",
    )
    b.p(
        "The LightGBM model reduces the log error from 0.961 to 0.488 and raises R2 from 0.007 to 0.734. "
        "The rank correlation is 0.855. The largest gains come from club rank, age, appearances, starts and goals per appearance. "
        "The model is strong but not surprising: club reputation and playing time dominate market value. "
        "That is exactly why the residual is interesting only when a player's profile is unusual."
    )
    b.figure("value_parity.png", "Figure 5: Actual and predicted log value relative to the league median. Left: global model on future seasons. Right: local model on 2015/16 with out-of-fold predictions.")
    b.h2("Local model")
    b.p(
        "The local model uses the 2015/16 Premier League cross-section and real match actions. "
        "It predicts the same relative log value from 31 event features, age, minutes, starts and club rank. "
        "The model is a ridge regression with standardized features and five-fold out-of-fold predictions. "
        "The baseline uses only age, minutes, starts, role and club rank. The full model adds passes, completion, progression, carries, xG, xA, box touches, pressures, tackles, interceptions, blocks, clearances, recoveries, aerial losses, dribbles, turnovers, fouls and line height."
    )
    b.table(
        ["Local model", "MAE, log", "R2", "Spearman", "n"],
        [
            ["Baseline", f"{L['baseline']['mae']:.3f}", f"{L['baseline']['r2']:.3f}", f"{L['baseline']['spearman']:.3f}", str(L["baseline"]["n"])],
            ["Full event model", f"{L['full']['mae']:.3f}", f"{L['full']['r2']:.3f}", f"{L['full']['spearman']:.3f}", str(L["full"]["n"])],
        ],
        "Table 6: Local 2015/16 market value model, five-fold out-of-fold predictions",
    )
    b.p(
        "The event model improves R2 from 0.495 to 0.614 and reduces the log error from 0.529 to 0.446. "
        "Pass volume and pass completion have the largest positive coefficients. "
        "Pressures and recoveries have negative coefficients once position, minutes and club rank are controlled. "
        "In other words, the market pays for passing and attacking output more than for defensive actions. "
        "That is a market bias, not a football verdict, and it explains why Gueye can be the best tactical fit and still receive a negative value gap."
    )
    b.p(
        "Leakage controls are explicit. The target is the market value at the end of the 2015/16 season. "
        "All features are known during the season. No future value, transfer fee, contract outcome or 2016 to 2018 information enters the model. "
        "The global model is tested on future seasons. The case model is trained on seasons up to 2014/15 when it scores 2015/16. "
        "The local model uses out-of-fold predictions, so no player's own value is used to predict himself."
    )

    b.pagebreak()
    b.h1("6. Is the undervalued signal real")
    b.p(
        "The value gap is the difference between the log market value and the model prediction. "
        "A player with a positive gap is cheaper than similar players. "
        "The local backtest flags the bottom 20% of residuals within each position group as undervalued and follows their market value for one, two and three years. "
        "Only players with a positive future value are included, and the attrition is reported."
    )
    b.table(
        ["Horizon", "n", "Undervalued", "Median growth, undervalued", "Median growth, rest", "Hit rate, undervalued", "Hit rate, rest"],
        [
            [
                f"{int(r['horizon_years'])} year" + ("s" if int(r["horizon_years"]) > 1 else ""),
                str(int(r["n"])),
                str(int(r["undervalued_n"])),
                pct(r["median_growth_undervalued"], True),
                pct(r["median_growth_rest"], True),
                pct(r["hit_rate_undervalued"]),
                pct(r["hit_rate_rest"]),
            ]
            for _, r in LOCAL_BT.iterrows()
        ],
        "Table 7: Local undervaluation backtest, 2015/16 Premier League cohort",
    )
    b.p(
        "At two years the undervalued group gained 11.8% in median market value, while the rest lost 10.9%. "
        "The hit rate was 52.8% against 35.8%. At three years the gap widened: +10.5% against -26.9%. "
        "At one year both medians were flat, which is consistent with a slow-moving market. "
        "The signal is not a guarantee. It is a modest edge in a noisy market."
    )
    b.p(
        "The global model provides a second test across seasons. "
        "For each evaluation season, the model is trained on all earlier seasons and the bottom 20% of residuals within each position group are followed for two years. "
        "The undervalued group beat the rest in all 10 evaluation seasons on a relative basis. "
        "Absolute market values fell in several seasons, especially after 2018/19, so the correct claim is relative: the flagged players lost less value, and in some seasons gained more."
    )
    gb_rows = []
    for _, r in GLOBAL_BT.iterrows():
        gb_rows.append(
            [
                r["season"],
                str(int(r["n"])),
                str(int(r["undervalued_n"])),
                pct(r["median_growth_undervalued"], True),
                pct(r["median_growth_rest"], True),
                pct(r["median_growth_undervalued"] - r["median_growth_rest"], True),
                pct(r["hit_rate_undervalued"]),
                pct(r["hit_rate_rest"]),
            ]
        )
    b.table(
        ["Season", "n", "Undervalued", "Growth, undervalued", "Growth, rest", "Gap", "Hit rate, undervalued", "Hit rate, rest"],
        gb_rows,
        "Table 8: Global undervaluation backtest, two-year horizon, expanding window",
    )
    b.figure("backtest_uplift.png", "Figure 6: The local two-year gap and the global season-by-season gap. The global model is positive in relative terms in all 10 evaluation seasons.")
    b.p(
        "The value gap is a signal, not a target. "
        "The market can be wrong about a player for reasons the model cannot see: a contract clause, a club's need, an injury that is not in the data, or a tactical role that changes after the transfer. "
        "The decision model therefore treats value as one input, not as the answer."
    )

    b.h1("7. Shortlist and scoring")
    b.p(
        "Every candidate receives three scores from 0 to 100. "
        "Fit measures the tactical profile. For central midfield it is the Kanté similarity. For centre backs it is a weighted percentile profile of clearances, blocks, interceptions, recoveries, aerial losses, progressive passes, pass completion and minutes. For forwards it is xG, shots, box touches, progressive carries, pressures, pass completion, minutes and conversion. "
        "Value is the average of the local and global market gap percentiles, with a 60/40 weight. "
        "Safety is the inverse of a risk score built from minutes availability, injury days, age and cards."
    )
    b.p(
        "The balanced score uses 0.55 fit, 0.25 value and 0.20 safety. "
        "The app lets the user change the weights, budget, risk limit and age limit and re-solve the optimisation. "
        "The candidate map shows the trade-off directly: Gueye is at the top of the fit axis, Cook is at the far right of the value axis, and Coquelin sits in the middle."
    )
    b.figure("candidate_map.png", "Figure 7: Candidate map. Horizontal axis: value score. Vertical axis: fit score. Point size: fee. Top three per need are outlined.")
    b.p(
        "The shortlist is not a single ranking. "
        "In midfield, Coquelin is the best balanced pick, Gueye is the best tactical pick and Wanyama is the middle option. "
        "In defence, Cook is the value pick and van Dijk is the higher-ceiling option at a higher fee. "
        "In attack, Ighalo is the clear first choice, with Deeney and Joshua King as cheaper alternatives. "
        "The next section turns these options into budget-feasible plans."
    )

    b.h1("8. Optimisation and scenarios")
    b.p(
        "The plan is a binary optimisation. Each candidate is a binary variable. "
        "The constraints require exactly one player for each of the three needs, total fees at or below the budget, risk at or below the limit and age at or below the policy. "
        "The objective maximises the weighted score. The problem is small enough to solve exactly with a MILP solver, and an independent brute-force check over the top eight candidates per need reproduces the optimum."
    )
    b.p(
        "The scenario table changes the preference weights and the constraints. "
        "The base scenario uses the balanced weights. The value-first scenario raises the value weight to 0.45. The quality-first scenario raises fit to 0.75. The safety-first scenario raises safety to 0.40. "
        "The budget is cut by 20% and 40%, the age limit falls to 24, and a risk-averse scenario caps risk at 45."
    )
    b.pagebreak()
    scen_rows = []
    name_map = {
        "base": "Base",
        "value_first": "Value first",
        "quality_first": "Quality first",
        "safety_first": "Safety first",
        "budget_minus_20": "Budget -20%",
        "budget_minus_40": "Budget -40%",
        "youth_policy": "Youth policy",
        "risk_averse": "Risk averse",
    }
    for _, r in SCEN.iterrows():
        players = str(r["players"])
        for long, short in {
            "Francis Joseph Coquelin": "Francis Coquelin",
            "Odion Jude Ighalo": "Odion Ighalo",
            "Idrissa Gana Gueye": "Idrissa Gueye",
            "José Ramiro Funes Mori": "Ramiro Funes Mori",
            "Chancel Mbemba Mangulu": "Chancel Mbemba",
            "Aleksandar Mitrović": "Aleksandar Mitrovic",
        }.items():
            players = players.replace(long, short)
        short_names = []
        for segment in players.split("; "):
            name = segment.split(": ", 1)[-1].split(" (")[0].strip()
            parts = name.split()
            if len(parts) > 1 and parts[-2].lower() in {"van", "de", "di", "da"}:
                short_names.append(" ".join(parts[-2:]))
            else:
                short_names.append(parts[-1] if parts else name)
        players = ", ".join(short_names)
        scen_rows.append(
            [
                name_map.get(r["scenario"], r["scenario"]),
                f"{r['budget_m']:.0f}",
                f"{r['cost_m']:.1f}",
                f"{r['leftover_m']:.1f}",
                f"{r['score']:.1f}",
                players,
            ]
        )
    b.table(
        ["Scenario", "Budget, EUR m", "Cost, EUR m", "Left, EUR m", "Score", "Selected plan"],
        scen_rows,
        "Table 9: Budget and preference scenarios. All plans satisfy the budget and fill at least one need.",
    )
    b.p(
        "The base plan is Coquelin, Cook and Ighalo for EUR 27m. "
        "The value-first weights select the same plan, because Coquelin's market gap is large. "
        "The quality-first weights move the midfield to Gueye and the centre back to Funes Mori, for EUR 31m. "
        "The safety-first weights select the recommended plan: Gueye, Cook and Ighalo for EUR 24m. "
        "The youth policy selects Mbemba, Emre Can and Mitrovic for EUR 42m. "
        "The budget cuts still fit the base plan at EUR 30m, which is a sign that the recommendation is not fragile to a 40% budget cut."
    )
    b.p(
        "Sensitivity to the weights is transparent. "
        "With safety fixed at 0.20 and fit rising from 0.30 to 0.80, Coquelin is selected until fit reaches 0.55, Gueye enters at 0.60, and Funes Mori replaces Cook at 0.70. "
        "Ighalo is selected in every scenario. "
        "The stable core is the striker and the value defender; the midfield is the genuine judgement call."
    )

    b.pagebreak()
    b.h1("9. Decision")
    b.p(
        "The recommendation is Idrissa Gueye, Steve Cook and Odion Ighalo for EUR 24m. "
        "This is the safety-first optimum: 0.40 fit, 0.20 value and 0.40 safety. "
        "It is appropriate for a club that has just lost a unique midfielder and cannot afford a failed replacement. "
        "The plan fills all three needs, leaves EUR 26m for wages, agent fees and a January buffer, and keeps the age profile young enough to retain resale value."
    )
    rec_rows = []
    for _, r in plan_players("recommended").sort_values("need").iterrows():
        rec_rows.append(
            [
                r["need"],
                r["display_name"],
                r["team_name"],
                f"{r['age']:.1f}",
                eur(r["market_value"]),
                f"{r['fit']:.0f}",
                f"{r['value']:.0f}",
                f"{r['safety']:.0f}",
                f"{r['score_w']:.1f}",
            ]
        )
    b.table(
        ["Need", "Player", "Club", "Age", "Fee", "Fit", "Value", "Safety", "Weighted score"],
        rec_rows,
        "Table 10: Recommended plan, safety-first weights",
    )
    b.figure("shortlist.png", "Figure 8: The recommended plan. Fit, value and safety are percentiles. The bar labels show the score for each dimension.")
    b.h2("Why these three")
    b.bullets(
        [
            "Gueye is the closest available tactical replacement for Kanté. He played 3,073 minutes, won the ball 15.5 times per 90, pressed 29.3 times per 90, and carried the ball 5.4 times per 90. He is 27, Premier League proven and available for EUR 9m. He is not a bargain: both value models call him fairly or richly priced. The case for him is fit and availability.",
            "Cook is the best value signal in the pool. He played 3,195 minutes for Bournemouth, won 7.1 clearances and 1.75 blocks per 90, and cost EUR 3m. The local model puts him at the 100th value percentile and the global model at +64%. The risk is a step up from a relegation-threatened side and limited progressive passing.",
            "Ighalo is the best available box threat. He scored 15 league goals from 16.9 xG, took 2.6 shots per 90 and touched the box 20.7 times per 90, for EUR 12m. The risk is that 2015/16 was a career outlier and that his market value fell after the move.",
        ]
    )
    b.h2("Alternatives")
    b.p(
        "Coquelin is the value alternative in midfield: EUR 12m, fit 81, value 82, safety 74. "
        "He is a more conservative passer than Gueye and less similar to Kanté, but the market gap is much larger. "
        "Van Dijk is the premium alternative in defence: EUR 12m, fit 57, value 83, safety 95. "
        "He offers more progressive passing and a higher ceiling than Cook, but the model does not separate them enough on fit to justify the extra EUR 9m in the recommended plan. "
        "Deeney is the cheaper forward alternative: EUR 9m, fit 55, value 80, safety 95. "
        "He is a better link player than Ighalo but less of a pure box threat."
    )
    b.p(
        "A board that wants a higher ceiling can replace Cook with van Dijk for EUR 33m in total, or replace Gueye with Coquelin for EUR 27m. "
        "A board that wants to preserve cash can keep the recommended plan at EUR 24m. "
        "The scenarios show that the striker and the value defender are stable; the midfield is the decision that changes with the weights."
    )
    b.h2("Risks and mitigations")
    b.table(
        ["Risk", "Why it matters", "Mitigation"],
        [
            ["Gueye's passing", "He is a safe short passer but not a creative progressor", "Keep Drinkwater as the passer, use Gueye as the destroyer, train the first phase"],
            ["Cook's step up", "Bournemouth defended deep and conceded chances", "Pair him with a progressive partner, start him as the third centre back or rotate"],
            ["Ighalo's outlier", "One strong season at 27, value fell after 2016", "Use him as a rotation striker, avoid a long contract, include a performance clause"],
            ["Adaptation", "A new midfielder changes the pressing and coverage", "Pre-season work on the 4-4-2 shape, video review of Kanté's pressing triggers"],
            ["Injury and suspension", "The plan relies on three starters", "Keep the EUR 26m buffer for January"],
        ],
        "Table 11: Risks and mitigations for the recommended plan",
    )
    b.h2("What happened next")
    b.p(
        "The market values after 2016 are a backtest, not a promise. "
        "Gueye rose from EUR 9m to EUR 20m, Cook from EUR 3m to EUR 7m, and Ighalo fell from EUR 12m to EUR 9.5m. "
        "The plan's total value rose from EUR 24m to EUR 36.5m, a gain of 52%. "
        "The value plan rose only 5.6%, and the fit plan rose 27.4%. "
        "Two hits and one miss is a realistic result for a three-player plan, and the report does not hide it."
    )
    hist_rows = []
    for _, r in plan_players("recommended").sort_values("need").iterrows():
        hist_rows.append(
            [
                r["display_name"],
                eur(r["market_value"]),
                eur(r["value_1y"]) if pd.notna(r["value_1y"]) else "n/a",
                eur(r["value_2y"]) if pd.notna(r["value_2y"]) else "n/a",
                pct(r["growth_2y"], True) if pd.notna(r["growth_2y"]) else "n/a",
            ]
        )
    b.table(
        ["Player", "Value 2016", "Value 2017", "Value 2018", "Growth 2016 to 2018"],
        hist_rows,
        "Table 12: What happened next for the recommended plan, used as a validation only",
    )
    b.p(
        "The outcome supports the method but does not prove it. "
        "Gueye's rise validates the fit-first view of the midfield. Cook's rise validates the value signal. Ighalo's fall validates the risk warning. "
        "A different three-player plan would have produced a different story, which is why the report shows the alternatives and the scenario table."
    )

    b.pagebreak()
    b.h1("10. Quality control and limitations")
    b.p(
        "The assignment asks for at least two potential errors or limitations. This project treats ten as part of the method, not as a disclaimer at the end. "
        "Each one changed a modelling or interpretation choice."
    )
    b.table(
        ["Pitfall", "What happened in this project", "Effect on the method"],
        [
            ["Data leakage", "Future market values and transfer fees could leak into the value model", "Target is the season-end value; features are known during the season; the global model is tested on future seasons; the case model is trained on seasons up to 2014/15"],
            ["Insufficient playing time", "Per-90 rates after a few matches are unstable", "The candidate pool requires 1,500 minutes; the local model uses 900+ minutes; safety penalises low availability"],
            ["Different positions", "One set of criteria cannot compare defenders, midfielders and forwards", "Scores are need-specific; value residuals are ranked within position groups; roles are clustered from actions"],
            ["Different leagues", "The candidate pool is Premier League only", "The case is a one-league study; the global model includes five leagues but the local fit does not"],
            ["Correlation and causation", "A high fit score does not prove that a signing improves the team", "The report recommends a portfolio and a tactical plan, not a causal claim"],
            ["Outdated data", "The full event season is 2015/16 and the market data ends in 2025", "The case cutoff is explicit; the retrospective design is justified by the two-year outcome window"],
            ["Sample bias", "Some 2015/16 profiles are missing and the datalake is not the full transfer market", "Low-confidence matches are rejected; the pool is described as a sample; the report does not claim full market coverage"],
            ["Uncertainty", "The value gap is noisy and individual outcomes vary", "The backtest reports medians and hit rates, not a single forecast; the plan keeps a cash buffer"],
            ["Fee proxy", "Market value is not a transfer fee", "The budget uses market value as a proxy; the report notes clauses, wages and agent fees"],
            ["Retrospective design", "The outcomes are known to the author", "The recommendation uses only pre-cutoff information; outcomes are used only for validation"],
        ],
        "Table 13: Pitfalls, evidence and methodological response",
    )
    b.p(
        "The most serious data issue is the Transfermarkt minutes column. "
        "Harry Kane is listed with 135 minutes and 25 goals, Jamie Vardy with 131 minutes and 24 goals. "
        "The column behaves like minutes per goal in those rows, not total minutes. "
        "Using it directly would have inflated per-90 rates for the best scorers and distorted the value model. "
        "The local model uses StatsBomb minutes. The global model uses appearances and starts instead of minutes. "
        "This is a concrete example of why source validation matters."
    )
    b.p(
        "The second serious issue is position labels. "
        "StatsBomb positions are formation slots. Ramsey is listed as a left defensive midfielder but plays as a box-to-box and attacking midfielder. "
        "The similarity score corrects the label, but a simpler model that trusted the label would have recommended the wrong profile. "
        "The role clusters are a check on this, not a replacement for watching the player."
    )
    b.p(
        "The third issue is market bias. "
        "The local model shows that the market pays for passing and attacking output and discounts defensive actions once position and possession are controlled. "
        "A negative value gap for Gueye is therefore not evidence that he is a bad player. It is evidence that the market does not pay for his main skill. "
        "The final decision uses fit and availability, not only the market gap."
    )
    b.p(
        "What would change the answer? "
        "More complete event data for other leagues would widen the candidate pool. "
        "Wage and contract data would make the budget constraint more realistic. "
        "Tracking data would measure off-ball movement and pressing better than event data. "
        "Scouting reports would capture personality, language and adaptation risk. "
        "The model is a decision aid, not a replacement for a sporting director."
    )

    b.h1("11. AI tool use")
    b.p(
        "An LLM coding assistant was used for code scaffolding, event-schema checks, debugging and drafting. "
        "The assistant was given the StatsBomb and Transfermarkt schemas, the case constraints, the cutoff date and the rule that future values must not enter the recommendation. "
        "It was not given a target answer, and it did not generate the reported numbers. "
        "Every table and figure is produced by the committed scripts from the raw data."
    )
    b.p(
        "Verification was manual and programmatic. "
        "The author checked the player mapping, the Kanté profile, the top shortlist and the recommended plan by hand. "
        "The unit tests check the counts, the model improvement over the baseline, the absence of future columns in the feature list, the budget constraint and the brute-force optimum. "
        "The backtest is a separate script and uses only post-cutoff values for evaluation. "
        "LLM limitations are real: it can invent names, confuse similar players and overstate a result. "
        "The report treats every number as a script output, not as a model statement."
    )

    b.h1("12. Reproducibility")
    b.p(
        "The repository contains the code, the processed tables and the figures. "
        "Raw data is downloaded by script and is not committed. "
        "The app runs offline from the processed tables. "
        "The report and slides are generated from the same outputs, so the numbers agree across formats."
    )
    b.p(
        "Commands: python scripts/download_data.py, then python scripts/build_all.py, then python scripts/verify.py, then python -m streamlit run app.py. "
        "The test suite has 9 tests. The independent brute-force check reproduces the MILP optimum. "
        "The report build script writes the DOCX and the HTML, and Playwright prints the PDF."
    )
    b.table(
        ["Path", "Content"],
        [
            ["src/transfer_lab/", "Parsing, features, value models, scouting, optimisation, figures"],
            ["scripts/download_data.py", "Public raw data download"],
            ["scripts/build_all.py", "End-to-end pipeline"],
            ["scripts/verify.py", "Evidence table and test run"],
            ["data/processed/", "Compact processed tables used by the app"],
            ["outputs/tables/", "Candidate, model, scenario and decision tables"],
            ["outputs/figures/", "Report and slide figures"],
            ["app.py", "Streamlit decision support app"],
            ["report/", "DOCX and PDF report"],
            ["presentation/", "Slide deck"],
        ],
        "Table 14: Repository structure",
    )

    b.pagebreak()
    b.h1("Appendix A. Metric definitions")
    b.table(
        ["Metric", "Definition"],
        [
            ["Ball winning per 90", "Tackles, interceptions and recoveries per 90 minutes"],
            ["Pressure per 90", "StatsBomb Pressure and Counterpress events per 90 minutes"],
            ["Progressive pass", "A completed pass that advances the ball at least 10 units toward goal and ends beyond x = 40"],
            ["Progressive carry", "A carry that advances the ball at least 10 units toward goal and ends beyond x = 40"],
            ["xG", "StatsBomb expected goals for shots"],
            ["xA", "Sum of shot xG for passes that key the shot"],
            ["Box touch", "An event located in the penalty area, x at least 102 and y between 18 and 62"],
            ["Value gap", "Actual log market value minus predicted log market value, relative to the league-season median"],
            ["Fit", "Need-specific tactical percentile, 0 to 100"],
            ["Value score", "Average of local and global value-gap percentiles, 0 to 100"],
            ["Safety", "100 minus a risk score built from availability, injury days, age and cards"],
        ],
        "Table A1: Metric definitions",
    )
    b.pagebreak()
    b.h1("Appendix B. Candidate tables")
    for idx, (need, label) in enumerate((("CM", "central midfield"), ("CB", "centre back"), ("ST", "centre forward"))):
        if idx > 0:
            b.pagebreak()
        part = table_top(need, 8)
        rows = [
            [
                r["display_name"],
                r["team_name"],
                f"{r['age']:.1f}",
                f"{r['minutes']:.0f}",
                eur(r["market_value"]),
                f"{r['fit']:.0f}",
                f"{r['value']:.0f}",
                f"{r['safety']:.0f}",
                f"{r['score']:.0f}",
            ]
            for _, r in part.iterrows()
        ]
        b.table(
            ["Player", "Club", "Age", "Minutes", "Fee", "Fit", "Value", "Safety", "Score"],
            rows,
            f"Table B{ {'CM':'1','CB':'2','ST':'3'}[need] }: Top eight {label} candidates, balanced score",
        )
    b.h1("Appendix C. Scenario and sensitivity tables")
    b.p(
        "The full scenario table is in Table 9. The sensitivity table below holds safety at 0.20 and moves the fit weight from 0.30 to 0.80. "
        "The selected striker is always Ighalo. The selected defender is Cook until fit reaches 0.70, when Funes Mori takes over. The midfielder switches from Coquelin to Gueye at a fit weight of 0.60."
    )
    sens_rows = []
    for _, r in SENS.iterrows():
        sens_rows.append(
            [
                f"{r['fit_weight']:.2f}",
                f"{r['value_weight']:.2f}",
                str(r["CM"]).split(" (")[0],
                str(r["CB"]).split(" (")[0],
                str(r["ST"]).split(" (")[0],
                f"{r['cost_m']:.1f}",
            ]
        )
    b.table(
        ["Fit weight", "Value weight", "CM", "CB", "ST", "Cost, EUR m"],
        sens_rows,
        "Table C1: Weight sensitivity",
    )
    b.pagebreak()
    b.h1("Appendix D. Verification output")
    b.p("The full command output is saved in outputs/verification.txt. The key checks are summarized below. Run python scripts/verify.py to reproduce them.")
    b.table(
        ["Check", "Result"],
        [
            ["StatsBomb matches", "380"],
            ["StatsBomb player-match rows", "10,385"],
            ["Market player-seasons", "30,939"],
            ["Global model R2 and Spearman", "0.734 and 0.855"],
            ["Local model R2 and Spearman", "0.614 and 0.785"],
            ["Local 2-year hit rate, undervalued and rest", "52.8% and 35.8%"],
            ["Base MILP score and brute-force score", "238.98 and 238.98"],
            ["Unit tests", "9 passed"],
        ],
        "Table D1: Verification summary",
    )
    return b


def shade(cell, fill: str):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)
    tc_pr.append(shd)


def add_page_number(paragraph):
    run = paragraph.add_run()
    fld_begin = OxmlElement("w:fldChar")
    fld_begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = "PAGE"
    fld_end = OxmlElement("w:fldChar")
    fld_end.set(qn("w:fldCharType"), "end")
    run._r.append(fld_begin)
    run._r.append(instr)
    run._r.append(fld_end)


def render_docx(blocks: Blocks, out_path: Path):
    doc = Document()
    normal = doc.styles["Normal"]
    normal.font.name = "Calibri"
    normal.font.size = Pt(10.5)
    normal.element.rPr.rFonts.set(qn("w:eastAsia"), "Calibri")
    normal.paragraph_format.space_after = Pt(5)
    normal.paragraph_format.line_spacing = 1.12
    for section in doc.sections:
        section.left_margin = section.right_margin = Cm(2.0)
        section.top_margin = Cm(1.8)
        section.bottom_margin = Cm(1.7)
        header = section.header.paragraphs[0]
        header.text = "Assignment 5 | AI Football Intelligence"
        header.runs[0].font.size = Pt(8)
        header.runs[0].font.color.rgb = RGBColor(0x66, 0x66, 0x66)
        footer = section.footer.paragraphs[0]
        footer.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        run = footer.add_run("Page ")
        run.font.size = Pt(8)
        run.font.color.rgb = RGBColor(0x66, 0x66, 0x66)
        add_page_number(footer)
    for level, size in ((1, 17), (2, 12.5)):
        style = doc.styles[f"Heading {level}"]
        style.font.name = "Calibri"
        style.font.size = Pt(size)
        style.font.bold = True
        style.font.color.rgb = RGBColor(0x11, 0x11, 0x11)
        style.element.rPr.rFonts.set(qn("w:eastAsia"), "Calibri")
        style.paragraph_format.space_before = Pt(12 if level == 1 else 9)
        style.paragraph_format.space_after = Pt(4)

    for kind, data in blocks.items:
        if kind == "cover":
            for _ in range(3):
                doc.add_paragraph()
            title = doc.add_paragraph()
            title.alignment = WD_ALIGN_PARAGRAPH.LEFT
            r = title.add_run(sanitize(data["title"]))
            r.font.size = Pt(30)
            r.font.bold = True
            r.font.color.rgb = RGBColor(0x11, 0x11, 0x11)
            sub = doc.add_paragraph()
            r = sub.add_run(sanitize(data["subtitle"]))
            r.font.size = Pt(17)
            r.font.color.rgb = RGBColor(0x33, 0x33, 0x33)
            doc.add_paragraph()
            for label in ("assignment", "case"):
                p = doc.add_paragraph()
                r = p.add_run(sanitize(data[label]))
                r.font.size = Pt(12)
                r.font.color.rgb = RGBColor(0x33, 0x33, 0x33)
            doc.add_paragraph()
            for label in ("author", "team", "date"):
                p = doc.add_paragraph()
                r = p.add_run(sanitize(data[label]))
                r.font.size = Pt(10.5)
                r.font.color.rgb = RGBColor(0x55, 0x55, 0x55)
            doc.add_paragraph()
            table = doc.add_table(rows=1, cols=3)
            table.alignment = WD_TABLE_ALIGNMENT.CENTER
            table.style = "Table Grid"
            for i, (label, value) in enumerate(data["strip"]):
                cell = table.rows[0].cells[i]
                cell.text = ""
                p = cell.paragraphs[0]
                r = p.add_run(sanitize(label))
                r.bold = True
                r.font.size = Pt(8)
                r.font.color.rgb = RGBColor(0x33, 0x33, 0x33)
                p2 = cell.add_paragraph()
                r2 = p2.add_run(sanitize(value))
                r2.font.size = Pt(9)
                r2.font.color.rgb = RGBColor(0x11, 0x11, 0x11)
                shade(cell, "F2F2F2")
            doc.add_page_break()
        elif kind == "h1":
            doc.add_heading(sanitize(data), level=1)
        elif kind == "h2":
            doc.add_heading(sanitize(data), level=2)
        elif kind == "p":
            p = doc.add_paragraph()
            if data["lead"]:
                r = p.add_run(sanitize(data["lead"]) + " ")
                r.bold = True
            p.add_run(sanitize(data["text"]))
        elif kind == "bullets":
            for item in data:
                p = doc.add_paragraph(style="List Bullet")
                p.add_run(sanitize(item))
        elif kind == "table":
            headers = data["headers"]
            rows = data["rows"]
            table = doc.add_table(rows=1, cols=len(headers))
            table.style = "Table Grid"
            table.alignment = WD_TABLE_ALIGNMENT.CENTER
            for i, header in enumerate(headers):
                cell = table.rows[0].cells[i]
                cell.text = ""
                p = cell.paragraphs[0]
                r = p.add_run(sanitize(header))
                r.bold = True
                r.font.size = Pt(8)
                r.font.color.rgb = RGBColor(0x11, 0x11, 0x11)
                shade(cell, "E6E6E6")
            for row in rows:
                cells = table.add_row().cells
                for i, value in enumerate(row):
                    cells[i].text = ""
                    p = cells[i].paragraphs[0]
                    r = p.add_run(sanitize(value))
                    r.font.size = Pt(8)
                    r.font.color.rgb = RGBColor(0x11, 0x11, 0x11)
            if data["caption"]:
                cap = doc.add_paragraph()
                r = cap.add_run(sanitize(data["caption"]))
                r.italic = False
                r.font.size = Pt(8)
                r.font.color.rgb = RGBColor(0x55, 0x55, 0x55)
        elif kind == "figure":
            fig_path = FIG / data["filename"]
            if fig_path.exists():
                doc.add_picture(str(fig_path), width=Cm(16.5))
                cap = doc.add_paragraph()
                r = cap.add_run(sanitize(data["caption"]))
                r.italic = False
                r.font.size = Pt(8)
                r.font.color.rgb = RGBColor(0x55, 0x55, 0x55)
        elif kind == "pagebreak":
            doc.add_page_break()
    doc.save(out_path)


def render_html(blocks: Blocks, path: Path):
    import html

    def esc(text):
        return html.escape(sanitize(text))

    css = """
    @page { size: A4; margin: 22mm 18mm 18mm; }
    * { box-sizing: border-box; }
    body { font-family: var(--font); color: #111111; margin: 0; font-size: 10pt; line-height: 1.45; }
    .page { padding: 0; }
    h1 { font-size: 17pt; margin: 18pt 0 6pt; border-bottom: 1px solid #bbbbbb; padding-bottom: 4pt; page-break-after: avoid; }
    h2 { font-size: 12.5pt; margin: 13pt 0 4pt; page-break-after: avoid; }
    p { margin: 0 0 7pt; text-align: justify; }
    ul { margin: 3pt 0 8pt 18pt; padding: 0; }
    li { margin-bottom: 4pt; }
    table { width: 100%; border-collapse: collapse; margin: 6pt 0 8pt; font-size: 8pt; page-break-inside: avoid; break-inside: avoid; }
    th { background: #e6e6e6; border: 1px solid #999999; padding: 3.5pt; text-align: left; font-weight: bold; }
    td { border: 1px solid #bbbbbb; padding: 3pt; vertical-align: top; }
    tr { page-break-inside: avoid; break-inside: avoid; }
    .table-block { page-break-inside: avoid; break-inside: avoid; }
    figure { margin: 10pt 0; page-break-inside: avoid; text-align: center; }
    figure img { width: 100%; max-width: 100%; }
    figcaption { font-size: 8pt; color: #555555; margin-top: 3pt; text-align: left; }
    .caption { font-size: 8pt; color: #555555; margin: 2pt 0 8pt; }
    .cover { min-height: 165mm; padding: 18mm 4mm 0; page-break-after: always; }
    .cover h1 { font-size: 33pt; border: none; margin: 0 0 8pt; padding: 0; }
    .cover .sub { font-size: 18pt; color: #333333; margin-bottom: 26pt; }
    .cover .case { font-size: 13pt; color: #333333; margin-bottom: 4pt; }
    .cover .meta { font-size: 10.5pt; color: #555555; margin-top: 28pt; }
    .cover .strip { display: flex; gap: 8pt; margin-top: 26pt; }
    .cover .cell { flex: 1; border: 1px solid #999999; background: #f2f2f2; padding: 8pt; }
    .cover .cell b { display: block; font-size: 8pt; text-transform: uppercase; letter-spacing: 0.04em; color: #333333; margin-bottom: 4pt; }
    .cover .cell span { font-size: 9.5pt; color: #111111; }
    .small { font-size: 9pt; color: #555555; }
    .pagebreak { page-break-before: always; }
    a { color: #222222; text-decoration: underline; }
    """
    parts = ["<!DOCTYPE html><html><head><meta charset='utf-8'><title>Assignment 5</title><link rel='stylesheet' href='../assets/design.css'><style>", css, "</style></head><body>"]
    for kind, data in blocks.items:
        if kind == "cover":
            parts.append("<section class='cover'>")
            parts.append(f"<h1>{esc(data['title'])}</h1>")
            parts.append(f"<div class='sub'>{esc(data['subtitle'])}</div>")
            parts.append(f"<div class='case'>{esc(data['assignment'])}</div>")
            parts.append(f"<div class='case'>{esc(data['case'])}</div>")
            parts.append(f"<div class='meta'>{esc(data['author'])}<br>{esc(data['team'])}<br>{esc(data['date'])}</div>")
            parts.append("<div class='strip'>")
            for label, value in data["strip"]:
                parts.append(f"<div class='cell'><b>{esc(label)}</b><span>{esc(value)}</span></div>")
            parts.append("</div></section>")
        elif kind == "h1":
            parts.append(f"<h1>{esc(data)}</h1>")
        elif kind == "h2":
            parts.append(f"<h2>{esc(data)}</h2>")
        elif kind == "p":
            if data["lead"]:
                parts.append(f"<p><strong>{esc(data['lead'])}</strong> {esc(data['text'])}</p>")
            else:
                parts.append(f"<p>{esc(data['text'])}</p>")
        elif kind == "bullets":
            parts.append("<ul>")
            for item in data:
                parts.append(f"<li>{esc(item)}</li>")
            parts.append("</ul>")
        elif kind == "table":
            parts.append("<div class='table-block'><table>")
            parts.append("<thead><tr>" + "".join(f"<th>{esc(h)}</th>" for h in data["headers"]) + "</tr></thead><tbody>")
            for row in data["rows"]:
                parts.append("<tr>" + "".join(f"<td>{esc(v)}</td>" for v in row) + "</tr>")
            parts.append("</tbody></table>")
            if data["caption"]:
                parts.append(f"<div class='caption'>{esc(data['caption'])}</div>")
            parts.append("</div>")
        elif kind == "figure":
            src = f"../outputs/figures/{data['filename']}"
            parts.append(f"<figure><img src='{esc(src)}'><figcaption>{esc(data['caption'])}</figcaption></figure>")
        elif kind == "pagebreak":
            parts.append("<div class='pagebreak'></div>")
    parts.append("</body></html>")
    path.write_text("\n".join(parts), encoding="utf-8")


def print_pdf(html_path: Path, pdf_path: Path):
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(html_path.as_uri(), wait_until="load")
        page.pdf(
            path=str(pdf_path),
            format="A4",
            print_background=True,
            prefer_css_page_size=True,
        )
        browser.close()

    import fitz

    doc = fitz.open(pdf_path)
    total = len(doc)
    for index, page in enumerate(doc):
        rect = page.rect
        page.insert_text(
            (rect.width - 68, rect.height - 16),
            f"Page {index + 1} of {total}",
            fontsize=7,
            color=(0.42, 0.42, 0.42),
        )
    doc.saveIncr()
    doc.close()


def main():
    blocks = build_blocks()
    docx_path = REPORT / "Assignment5_Report.docx"
    html_path = REPORT / "report.html"
    pdf_path = REPORT / "Assignment5_Report.pdf"
    render_docx(blocks, docx_path)
    render_html(blocks, html_path)
    print_pdf(html_path, pdf_path)
    print("wrote", docx_path)
    print("wrote", html_path)
    print("wrote", pdf_path)


if __name__ == "__main__":
    main()
