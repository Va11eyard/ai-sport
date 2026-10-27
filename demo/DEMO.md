# Assignment 5 demo

The demo shows how a sporting director can move from a squad problem to a budget-feasible plan.

## Run the app

```bash
python -m streamlit run app.py
```

Open http://localhost:8501. The app reads only the committed processed tables.

## Five-step demo

1. **Decision.** Start on the Decision tab. Point at the three cards and the EUR 24m total. Say that Gueye is the fit pick, Cook is the value pick and Ighalo is the striker.
2. **Squad need.** Open the Squad need tab. Show the style fingerprint and the Kanté action maps. Explain why the team needs a destroyer, not a playmaker.
3. **Market.** Open the Market tab. Show the two models and the backtest. State the key caveat: the value gap is a signal, not a target.
4. **Shortlist.** Open the Shortlist tab. Change the budget to EUR 30m, then to EUR 20m. Show how the feasible plan changes. Select Steve Cook and show the percentile detail.
5. **Method.** Open the Method tab. Show the limitations, the AI-use disclosure and the reproduce commands. Close with the decision rule.

## What to say in 13 to 15 minutes

- 0 to 2 minutes: the decision and the three players.
- 2 to 5 minutes: the data and the real-match style analysis.
- 5 to 8 minutes: the two value models and the backtest.
- 8 to 11 minutes: the shortlist and the optimisation.
- 11 to 14 minutes: risks, budget sensitivity and limitations.
- 14 to 15 minutes: what the system does and what it does not do.

## Files

- `demo/screenshots/` contains the captured screens.
- `demo/record_demo.py` captures them again with Playwright.
- `report/Assignment5_Report.pdf` is the full report.
- `presentation/Assignment5_Presentation.pdf` is the slide deck.

## Re-record the screens

Start the app on port 8601:

```bash
python -m streamlit run app.py --server.port 8601 --server.headless true
python demo/record_demo.py
```

The script opens the app, captures the five tabs and the shortlist table, and writes the images to `demo/screenshots`.
