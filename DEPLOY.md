# Deploy the app

GitHub Pages serves the static project page only. Streamlit needs a Python process, so the app must run on a Python host. Streamlit Community Cloud is the shortest path.

## Streamlit Community Cloud

1. Open https://share.streamlit.io and sign in with GitHub.
2. Select **New app**.
3. Use these settings:
   - Repository: `Va11eyard/ai-sport`
   - Branch: `dev`
   - Main file path: `app.py`
   - App URL: choose a subdomain, for example `transfer-decision-lab`
4. Select **Deploy**.
5. Wait for the build. The app reads `data/processed`, `outputs` and `assets` from the repository. Raw data is not needed.

The app URL will look like:

`https://transfer-decision-lab.streamlit.app`

After deployment, add the URL to `site/index.html`, `README.md` and the report if needed. Rebuild the static page with:

```bash
python scripts/build_pages.py
```

Then commit the built page to the `gh-pages` branch.

## Dependencies

- `requirements.txt` contains only the app runtime: Streamlit, pandas, numpy, scipy and Plotly.
- `requirements-dev.txt` adds the pipeline and report tools: LightGBM, scikit-learn, matplotlib, rapidfuzz, python-docx, joblib, pytest and Playwright.

Streamlit Cloud uses `requirements.txt`. Local pipeline work should use:

```bash
pip install -r requirements-dev.txt
```

## Troubleshooting

**Build fails on a package**

Open the build logs in Streamlit Cloud. The app only needs the five runtime packages. If a package was added to `requirements.txt` for the pipeline, move it to `requirements-dev.txt`.

**App cannot find the data**

Check that the selected branch contains `data/processed`, `outputs/tables` and `outputs/figures`. The app uses paths relative to its own folder.

**Python version**

If the platform asks for a version, add `runtime.txt` with `python-3.12`. The runtime packages support Python 3.12.

**The app sleeps**

Streamlit Community Cloud sleeps after inactivity. Open the URL again and wait for the app to wake.

**The page is blank or a widget errors**

Check the app logs. A common cause is a missing package in `requirements.txt` or a processed file that was not committed.

## Alternatives

**Hugging Face Spaces**

Create a public Space with the Streamlit SDK, then upload `app.py`, `src`, `data/processed`, `outputs`, `assets` and a Space `README.md` with the Streamlit front matter. This requires a Hugging Face account and token.

**Quick temporary test**

For a local demo on another device, expose the running app with a tunnel:

```bash
npx localtunnel --port 8501
```

This is temporary and only works while the computer and the tunnel stay on. Do not use it for the final submission link.

## What not to use

- GitHub Pages cannot run Streamlit, Flask or any Python server.
- Vercel can host the Next.js app in the `main` branch, but not this Streamlit app.
- Do not commit `.env` files or tokens. The app uses public data and has no secrets.
