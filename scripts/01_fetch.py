"""
01_fetch.py
-----------
Downloads the "Default of Credit Card Clients" dataset from the UCI Machine
Learning Repository: 30,000 credit card customers in Taiwan (April-September
2005), each labelled with whether they defaulted on their next payment.

Data source: https://archive.ics.uci.edu/dataset/350 (CC BY 4.0)
Citation:    Yeh, I-C. (2016). UCI Machine Learning Repository.
Output:      data/raw/default_of_credit_card_clients.xls

Why this dataset:
  It is one of the standard public credit-risk datasets: real customer-level
  records with demographics, credit limits, six months of repayment history
  and a default flag — the same shape of problem a bank's credit analytics
  team works on daily.

Run:  python scripts/01_fetch.py   (from the repo root)
"""

import io
import zipfile
from pathlib import Path

import requests

RAW_DIR = Path("data/raw")
URL = "https://archive.ics.uci.edu/static/public/350/default+of+credit+card+clients.zip"


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    print("Downloading UCI credit default dataset (~5 MB)...")

    response = requests.get(URL, timeout=120)
    response.raise_for_status()

    # The UCI archive ships a zip containing a single .xls file — extract it
    # straight into data/raw/ without touching the disk twice.
    with zipfile.ZipFile(io.BytesIO(response.content)) as zf:
        for name in zf.namelist():
            target = RAW_DIR / "default_of_credit_card_clients.xls"
            target.write_bytes(zf.read(name))
            print(f"Saved {target} ({target.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
