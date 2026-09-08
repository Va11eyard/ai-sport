# Downloads only if ~/.kaggle/kaggle.json exists. Do not call without a key.

from __future__ import annotations

import os
import sys
from pathlib import Path


def main() -> int:
    cred = Path.home() / ".kaggle" / "kaggle.json"
    if not cred.exists():
        print("kaggle credentials missing; skip download", file=sys.stderr)
        return 2
    print("credentials present — wire kaggle CLI in a later iteration")
    return 0


if __name__ == "__main__":
    sys.exit(main())