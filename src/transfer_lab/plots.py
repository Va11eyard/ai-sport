from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Arc, Circle, Rectangle

from .config import FIGURES, PROCESSED, SB_RAW, TABLES
from .names import clean_name

plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "font.size": 10,
        "axes.edgecolor": "#222222",
        "axes.labelcolor": "#222222",
        "text.color": "#222222",
        "xtick.color": "#444444",
        "ytick.color": "#444444",
        "axes.titlesize": 12,
        "axes.titleweight": "bold",
        "figure.facecolor": "white",
        "savefig.facecolor": "white",
    }
)
GREYS = ["#111111", "#444444", "#777777", "#a6a6a6", "#c9c9c9", "#e3e3e3"]


def _save(fig, name: str):
    FIGURES.mkdir(parents=True, exist_ok=True)
    path = FIGURES / name
    fig.savefig(path, dpi=220, bbox_inches="tight")
    plt.close(fig)
    return path


def collect_kante_events(force: bool = False) -> pd.DataFrame:
    path = TABLES / "kante_events.csv"
    if path.exists() and not force:
        return pd.read_csv(path)
    rows = []
    files = sorted((SB_RAW / "events").glob("*.json"))
    for i, file in enumerate(files, 1):
        with file.open(encoding="utf-8") as fh:
            events = json.load(fh)
        for e in events:
            player = e.get("player") or {}
            if player.get("id") != 3961:
                continue
            loc = e.get("location")
            if not loc:
                continue
            etype = e["type"]["name"]
            end = None
            outcome = None
            if etype == "Pass":
                end = (e.get("pass") or {}).get("end_location")
                outcome = (e.get("pass") or {}).get("outcome", {}).get("name") if (e.get("pass") or {}).get("outcome") else "Complete"
            elif etype == "Carry":
                end = (e.get("carry") or {}).get("end_location")
            elif etype == "Duel":
                outcome = (e.get("duel") or {}).get("outcome", {}).get("name") if (e.get("duel") or {}).get("outcome") else None
            rows.append(
                {
                    "match_id": file.stem,
                    "type": etype,
                    "minute": e.get("minute"),
                    "x": loc[0],
                    "y": loc[1],
                    "end_x": end[0] if end else np.nan,
                    "end_y": end[1] if end else np.nan,
                    "outcome": outcome,
                    "duel_type": ((e.get("duel") or {}).get("type") or {}).get("name") if etype == "Duel" else None,
                }
            )
        if i % 50 == 0:
            print(f"scanned {i}/{len(files)} match files", flush=True)
    df = pd.DataFrame(rows)
    df.to_csv(path, index=False)
    return df


def draw_pitch(ax):
    ax.set_xlim(-2, 122)
    ax.set_ylim(-2, 82)
    ax.set_aspect("equal")
    ax.axis("off")
    lw = 1.1
    color = "#333333"
    ax.add_patch(Rectangle((0, 0), 120, 80, fill=False, edgecolor=color, lw=lw))
    ax.plot([60, 60], [0, 80], color=color, lw=lw)
    ax.add_patch(Circle((60, 40), 9.15, fill=False, edgecolor=color, lw=lw))
    ax.add_patch(Circle((60, 40), 0.6, color=color))
    ax.add_patch(Rectangle((0, 18), 18, 44, fill=False, edgecolor=color, lw=lw))
    ax.add_patch(Rectangle((0, 30), 6, 20, fill=False, edgecolor=color, lw=lw))
    ax.add_patch(Rectangle((102, 18), 18, 44, fill=False, edgecolor=color, lw=lw))
    ax.add_patch(Rectangle((114, 30), 6, 20, fill=False, edgecolor=color, lw=lw))
    ax.add_patch(Arc((12, 40), 18.3, 18.3, theta1=310, theta2=50, color=color, lw=lw))
    ax.add_patch(Arc((108, 40), 18.3, 18.3, theta1=130, theta2=230, color=color, lw=lw))
    ax.plot([12], [40], marker="o", ms=2.5, color=color)
    ax.plot([108], [40], marker="o", ms=2.5, color=color)


def pitch_actions(events: pd.DataFrame):
    defensive = events[
        ((events["type"] == "Duel") & (events["duel_type"] == "Tackle"))
        | events["type"].isin(["Interception", "Ball Recovery", "Pressure", "Block"])
    ]
    progress = events[
        ((events["type"] == "Pass") & (events["outcome"] == "Complete"))
        | (events["type"] == "Carry")
    ].copy()
    progress = progress.dropna(subset=["end_x", "end_y"])
    progress["advance"] = progress["end_x"] - progress["x"]
    progress = progress[(progress["advance"] >= 8) & (progress["end_x"] >= 35)]

    fig, axes = plt.subplots(1, 2, figsize=(11.6, 4.2))
    for ax, data, title, note in [
        (axes[0], defensive, "Where Kanté wins the ball", f"{len(defensive)} defensive actions, 37 matches"),
        (axes[1], progress, "Where Kanté moves the ball forward", f"{len(progress)} progressive passes and carries"),
    ]:
        draw_pitch(ax)
        hb = ax.hexbin(data["x"], data["y"], gridsize=20, cmap="Greys", mincnt=1, linewidths=0.2)
        ax.set_title(f"{title}\n{note}", loc="left", fontsize=11, fontweight="bold")
        cb = fig.colorbar(hb, ax=ax, fraction=0.035, pad=0.01)
        cb.ax.tick_params(labelsize=8)
        cb.set_label("actions", fontsize=8)
    fig.suptitle("N'Golo Kanté, Premier League 2015/16: real match actions", x=0.02, ha="left", fontsize=13, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    return _save(fig, "kante_actions.png")


def leicester_style():
    team = pd.read_csv(PROCESSED / "sb_team_matches.csv")
    agg = (
        team.groupby("team_name")
        .agg(
            matches=("match_id", "nunique"),
            possession=("pass_share", "mean"),
            pass_completion=("pass_completion", "mean"),
            long_share=("long_ball_share", "mean"),
            xg=("xg", "sum"),
            xga=("xg_against", "sum"),
            counter=("counter_xg_share", "mean"),
            setp=("set_piece_xg_share", "mean"),
        )
        .reset_index()
    )
    agg["xg_pm"] = agg["xg"] / agg["matches"]
    agg["xga_pm"] = agg["xga"] / agg["matches"]
    metrics = [
        ("possession", "Possession, %"),
        ("pass_completion", "Pass completion, %"),
        ("long_share", "Long balls, % of passes"),
        ("xg_pm", "xG per match"),
        ("xga_pm", "xGA per match"),
        ("counter", "Counterattack xG, %"),
        ("setp", "Set-piece xG, %"),
    ]
    lei = agg[agg["team_name"] == "Leicester City"].iloc[0]
    rows = []
    for col, label in metrics:
        values = agg[col].astype(float)
        z = (float(lei[col]) - values.mean()) / values.std(ddof=0)
        rows.append({"metric": label, "z": z, "value": float(lei[col]), "mean": float(values.mean())})
    rows = sorted(rows, key=lambda r: r["z"])
    fig, ax = plt.subplots(figsize=(9.0, 4.8))
    ys = np.arange(len(rows))
    colors = ["#c9c9c9" if r["z"] < 0 else "#222222" for r in rows]
    ax.barh(ys, [r["z"] for r in rows], color=colors, height=0.62)
    ax.axvline(0, color="#333333", lw=1)
    ax.set_yticks(ys)
    ax.set_yticklabels([f"{r['metric']}  {r['value']:.2f}" for r in rows])
    ax.set_xlabel("Standard deviations from the league average")
    ax.set_title("Leicester 2015/16: style fingerprint", loc="left")
    ax.grid(axis="x", color="#ececec", lw=0.8)
    ax.set_axisbelow(True)
    ax.set_xlim(min(r["z"] for r in rows) - 0.35, max(r["z"] for r in rows) + 0.35)
    ax.spines[["top", "right"]].set_visible(False)
    fig.text(0.02, 0.01, "League average is zero. One unit is one standard deviation across 20 teams.", fontsize=8, color="#555555")
    fig.tight_layout(rect=[0, 0.04, 1, 1])
    return _save(fig, "leicester_style.png")


def kante_percentiles():
    players = pd.read_csv(PROCESSED / "sb_players.csv")
    mf = players[(players["position_group"] == "MF") & (players["minutes"] >= 900)]
    k = players[players["player_name"].str.contains("Kant", na=False)].iloc[0]
    metrics = [
        ("ball_winning_p90", "Ball winning"),
        ("recoveries_p90", "Recoveries"),
        ("tackles_p90", "Tackles"),
        ("interceptions_p90", "Interceptions"),
        ("pressures_p90", "Pressures"),
        ("progressive_carries_p90", "Progressive carries"),
        ("pass_completion", "Pass completion"),
        ("progressive_passes_p90", "Progressive passes"),
        ("passes_p90", "Pass volume"),
        ("shots_p90", "Shots"),
    ]
    values = [float((mf[col] <= k[col]).mean() * 100) for col, _ in metrics]
    labels = [label for _, label in metrics]
    fig, ax = plt.subplots(figsize=(8.6, 4.8))
    ys = np.arange(len(metrics))[::-1]
    ax.barh(ys, values, color="#333333", height=0.62)
    for y, v in zip(ys, values):
        ax.text(v + 1.5, y, f"p{v:.0f}", va="center", fontsize=9)
    ax.set_yticks(ys)
    ax.set_yticklabels(labels)
    ax.set_xlim(0, 108)
    ax.set_xlabel("Percentile among Premier League midfielders with 900+ minutes")
    ax.set_title("Kanté is a 100th percentile ball winner", loc="left")
    ax.grid(axis="x", color="#e3e3e3", lw=0.8)
    ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    return _save(fig, "kante_percentiles.png")


def value_parity():
    hold = pd.read_csv(TABLES / "global_holdout_predictions.csv")
    local = pd.read_csv(TABLES / "case_predictions.csv")
    fig, axes = plt.subplots(1, 2, figsize=(11.0, 4.5))
    for ax, actual, pred, title, note in [
        (axes[0], hold["log_value_rel"], hold["pred_lgbm"], "Global model, 2021/22 to 2024/25", f"n={len(hold):,}"),
        (axes[1], local["log_value_rel"], local["local_pred_rel"], "Local model, Premier League 2015/16", f"n={len(local):,}"),
    ]:
        ax.hexbin(actual, pred, gridsize=35, cmap="Greys", mincnt=1, linewidths=0.2)
        lim = [min(actual.min(), pred.min()) - 0.5, max(actual.max(), pred.max()) + 0.5]
        ax.plot(lim, lim, color="#111111", lw=1.2, ls="--")
        ax.set_xlim(lim)
        ax.set_ylim(lim)
        ax.set_xlabel("Actual log value relative to league median")
        ax.set_ylabel("Predicted log value relative to league median")
        ax.set_title(title, loc="left", fontsize=11)
        ax.text(0.03, 0.95, note, transform=ax.transAxes, fontsize=9, color="#555555", va="top")
        ax.spines[["top", "right"]].set_visible(False)
    fig.suptitle("Market value models, out of sample", x=0.02, ha="left", fontsize=13, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    return _save(fig, "value_parity.png")


def backtest_plot():
    local = pd.read_csv(TABLES / "backtest_local.csv")
    glob = pd.read_csv(TABLES / "backtest_global.csv")
    fig, axes = plt.subplots(1, 2, figsize=(11.6, 4.4), gridspec_kw={"width_ratios": [1, 2.1]})
    ax = axes[0]
    row = local[local["horizon_years"] == 2].iloc[0]
    labels = ["Undervalued\nbottom 20%", "Rest"]
    vals = [row["median_growth_undervalued"] * 100, row["median_growth_rest"] * 100]
    bars = ax.bar(labels, vals, color=["#111111", "#c9c9c9"], width=0.55)
    for bar, v in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width() / 2, v / 2, f"{v:+.1f}%", ha="center", va="center", fontsize=10, color="white" if v > 0 else "#222222", fontweight="bold")
    ax.axhline(0, color="#333333", lw=1)
    ax.set_ylim(min(vals) - 4, max(vals) + 4)
    ax.set_ylabel("Median market value change, 2 years, %")
    ax.set_title("Local model, 2015/16", loc="left", fontsize=11, pad=14)
    ax.spines[["top", "right"]].set_visible(False)

    ax = axes[1]
    glob["uplift"] = (glob["median_growth_undervalued"] - glob["median_growth_rest"]) * 100
    ax.bar(glob["season"], glob["uplift"], color="#555555", width=0.62)
    ax.axhline(0, color="#333333", lw=1)
    for x, v in zip(range(len(glob)), glob["uplift"]):
        ax.text(x, v + (0.8 if v >= 0 else -1.6), f"{v:+.0f}", ha="center", va="bottom" if v >= 0 else "top", fontsize=8)
    ax.set_xticks(range(len(glob)))
    ax.set_xticklabels(glob["season"], rotation=45, ha="right")
    ax.set_ylabel("Median growth gap, undervalued minus rest, pp")
    ax.set_title("Global model, all evaluation seasons", loc="left", fontsize=11)
    ax.spines[["top", "right"]].set_visible(False)
    fig.suptitle("The undervalued signal holds in relative terms", x=0.02, ha="left", fontsize=13, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    return _save(fig, "backtest_uplift.png")


def candidate_map():
    cand = pd.read_csv(TABLES / "candidates.csv")
    needs = ["CM", "CB", "ST"]
    fig, axes = plt.subplots(1, 3, figsize=(12.4, 4.3))
    for ax, need in zip(axes, needs):
        part = cand[cand["need"] == need].copy()
        sizes = 22 + part["cost_m"] * 5
        ax.scatter(part["value"], part["fit"], s=sizes, c="#777777", alpha=0.55, edgecolor="#333333", linewidth=0.5)
        top = part.sort_values("score", ascending=False).head(3)
        ax.scatter(top["value"], top["fit"], s=80, facecolor="white", edgecolor="#111111", linewidth=1.4)
        offsets = {"Cook": (6, 8), "van Dijk": (-12, -14), "Mori": (6, 6), "Coquelin": (6, 6), "Gueye": (6, 6), "Wanyama": (6, 6), "Ighalo": (6, 6), "Deeney": (6, 6), "King": (6, 6)}
        for _, row in top.iterrows():
            parts = row["display_name"].split()
            short = " ".join(parts[-2:]) if len(parts) > 1 and parts[-2].lower() in {"van", "de", "di", "da"} else parts[-1]
            ax.annotate(short, (row["value"], row["fit"]), textcoords="offset points", xytext=offsets.get(short, (6, 6)), fontsize=8)
        ax.set_xlim(-3, 103)
        ax.set_ylim(-3, 103)
        ax.set_xlabel("Value score (percentile)")
        ax.set_ylabel("Fit score")
        ax.set_title(need, loc="left", fontsize=12)
        ax.grid(color="#ededed", lw=0.8)
        ax.set_axisbelow(True)
        ax.spines[["top", "right"]].set_visible(False)
        ax.axvline(50, color="#cccccc", lw=0.8, ls=":")
        ax.axhline(50, color="#cccccc", lw=0.8, ls=":")
    fig.suptitle("Candidate map: tactical fit against market value, point size is fee", x=0.02, ha="left", fontsize=13, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    return _save(fig, "candidate_map.png")


def shortlist_plot():
    short = pd.read_csv(TABLES / "shortlist_safety_first.csv")
    short["display_name"] = short["display_name"].map(clean_name)
    short = short.sort_values("need")
    metrics = ["fit", "value", "safety"]
    labels = ["Fit", "Value", "Safety"]
    fig, ax = plt.subplots(figsize=(9.2, 3.9))
    x = np.arange(len(short))
    width = 0.24
    for i, (m, lab) in enumerate(zip(metrics, labels)):
        bars = ax.bar(x + (i - 1) * width, short[m], width, color=GREYS[i + 1], edgecolor="#333333", linewidth=0.5, label=lab)
        for bar, v in zip(bars, short[m]):
            ax.text(bar.get_x() + bar.get_width() / 2, v + 1.5, f"{v:.0f}", ha="center", fontsize=8)
    ax.set_xticks(x)
    ax.set_xticklabels([f"{r['display_name']}\n{r['need']}, EUR {r['market_value']/1e6:.0f}m" for _, r in short.iterrows()], fontsize=9)
    ax.set_ylim(0, 124)
    ax.set_ylabel("Score, 0 to 100")
    ax.set_title("Recommended plan: fit, value and availability", loc="left")
    for i, lab in enumerate(labels):
        ax.text((i - 1) * width, 114, lab, ha="center", fontsize=8, color="#333333")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    return _save(fig, "shortlist.png")


def cluster_map():
    from sklearn.decomposition import PCA
    from sklearn.preprocessing import StandardScaler
    from .scouting import CLUSTER_FEATURES, assign_clusters, load_merged

    df = assign_clusters(load_merged())
    df = df[df["cluster_label"].notna()].copy()
    X = df[CLUSTER_FEATURES].apply(pd.to_numeric, errors="coerce").fillna(0)
    Z = StandardScaler().fit_transform(X)
    pcs = PCA(n_components=2, random_state=42).fit_transform(Z)
    df["pc1"], df["pc2"] = pcs[:, 0], pcs[:, 1]
    fig, ax = plt.subplots(figsize=(8.8, 5.6))
    markers = ["o", "s", "^", "D", "v", "P"]
    labels = sorted(df["cluster_label"].unique())
    for i, lab in enumerate(labels):
        part = df[df["cluster_label"] == lab]
        ax.scatter(part["pc1"], part["pc2"], s=18, marker=markers[i % len(markers)], color=GREYS[i % len(GREYS)], alpha=0.55, label=lab, linewidths=0)
    highlights = {
        "N'Golo Kanté": ("Kanté", "o"),
        "Francis Joseph Coquelin": ("Coquelin", "s"),
        "Idrissa Gana Gueye": ("Gueye", "^"),
        "Steve Cook": ("Cook", "D"),
        "Odion Jude Ighalo": ("Ighalo", "P"),
    }
    for name, (lab, marker) in highlights.items():
        row = df[df["display_name"] == name]
        if row.empty:
            continue
        ax.scatter(row["pc1"], row["pc2"], s=110, marker=marker, facecolor="white", edgecolor="#111111", linewidth=1.6, zorder=5)
        offsets = {"van Dijk": (-8, -16), "Cook": (8, -14), "Kanté": (-38, 4), "Gueye": (8, 4)}
        ax.annotate(lab, (row["pc1"].iloc[0], row["pc2"].iloc[0]), textcoords="offset points", xytext=offsets.get(lab, (6, 6)), fontsize=9, fontweight="bold")
    ax.set_title("Role clusters from real match actions", loc="left")
    ax.set_xlabel("Principal component 1")
    ax.set_ylabel("Principal component 2")
    ax.grid(color="#ededed", lw=0.7)
    ax.set_axisbelow(True)
    ax.legend(frameon=False, fontsize=8, loc="best")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    return _save(fig, "cluster_map.png")


def make_all():
    events = collect_kante_events()
    paths = [
        pitch_actions(events),
        leicester_style(),
        kante_percentiles(),
        value_parity(),
        backtest_plot(),
        candidate_map(),
        shortlist_plot(),
        cluster_map(),
    ]
    return paths


if __name__ == "__main__":
    for p in make_all():
        print(p)
