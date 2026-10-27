"""Download the public raw data used by Assignment 5.

Run from the project root:
    python scripts/download_data.py

The script is idempotent. Existing files are skipped unless --force is used.
Total download is roughly 1.4 GB, mostly StatsBomb event files.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
TM = RAW / "transfermarkt"
SB = RAW / "statsbomb"
SB_MATCHES = SB / "matches"
SB_EVENTS = SB / "events"
SB_LINEUPS = SB / "lineups"

TM_RAW = "https://raw.githubusercontent.com/salimt/football-datasets/main/datalake/transfermarkt"
TM_MEDIA = "https://media.githubusercontent.com/media/salimt/football-datasets/main/datalake/transfermarkt"
SB_BASE = "https://raw.githubusercontent.com/statsbomb/open-data/master/data"

TM_FILES = [
    "player_profiles/player_profiles.csv",
    "player_market_value/player_market_value.csv",
    "player_latest_market_value/player_latest_market_value.csv",
    "player_injuries/player_injuries.csv",
    "team_competitions_seasons/team_competitions_seasons.csv",
    "team_details/team_details.csv",
    "player_performances/player_performances.csv",
    "transfer_history/transfer_history.csv",
]


def _download(url: str, path: Path, force: bool, session: requests.Session) -> tuple[str, str]:
    if path.exists() and path.stat().st_size > 1000 and not force:
        return str(path), "skip"
    path.parent.mkdir(parents=True, exist_ok=True)
    for attempt in range(5):
        try:
            response = session.get(url, timeout=120)
            if response.status_code == 200:
                tmp = path.with_suffix(path.suffix + ".part")
                with tmp.open("wb") as fh:
                    for chunk in response.iter_content(chunk_size=1 << 20):
                        if chunk:
                            fh.write(chunk)
                tmp.replace(path)
                return str(path), "ok"
        except Exception:
            pass
        time.sleep(1 + attempt)
    return str(path), "FAIL"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()

    for folder in (TM, SB_MATCHES, SB_EVENTS, SB_LINEUPS):
        folder.mkdir(parents=True, exist_ok=True)

    session = requests.Session()
    failures = []

    print("Transfermarkt datalake", flush=True)
    for rel in TM_FILES:
        base = TM_MEDIA if rel in {"player_performances/player_performances.csv", "transfer_history/transfer_history.csv"} else TM_RAW
        path, status = _download(f"{base}/{rel}", TM / Path(rel).name, args.force, session)
        print(f"  {status:4} {Path(rel).name}", flush=True)
        if status == "FAIL":
            failures.append(path)

    print("StatsBomb Premier League 2015/16 index", flush=True)
    index_path = SB_MATCHES / "premier_league_1516.json"
    path, status = _download(f"{SB_BASE}/matches/2/27.json", index_path, args.force, session)
    print(f"  {status:4} {index_path.name}", flush=True)
    if status == "FAIL":
        print("Cannot continue without the match index", file=sys.stderr)
        return 1

    matches = json.loads(index_path.read_text(encoding="utf-8"))
    ids = [m["match_id"] for m in matches]
    print(f"StatsBomb matches: {len(ids)}", flush=True)

    jobs = []
    for match_id in ids:
        jobs.append((f"{SB_BASE}/events/{match_id}.json", SB_EVENTS / f"{match_id}.json"))
        jobs.append((f"{SB_BASE}/lineups/{match_id}.json", SB_LINEUPS / f"{match_id}.json"))

    done = 0
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        futures = [pool.submit(_download, url, path, args.force, session) for url, path in jobs]
        for future in as_completed(futures):
            path, status = future.result()
            done += 1
            if status == "FAIL":
                failures.append(path)
            if done % 40 == 0 or done == len(jobs):
                print(f"  {done}/{len(jobs)} files, failures {len(failures)}", flush=True)

    if failures:
        print("Failed files:", file=sys.stderr)
        for path in failures:
            print(f"  {path}", file=sys.stderr)
        return 1
    print("Download complete", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
