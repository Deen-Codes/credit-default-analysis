"""
02_clean.py
-----------
Turns the raw UCI spreadsheet into analysis-ready tables with readable names
and documented recoding decisions. Credit data lives or dies on definitions,
so every recode is stated here rather than buried in a formula.

Input:   data/raw/default_of_credit_card_clients.xls
Outputs (data/processed/):
  clients_clean.csv       one row per customer, readable columns
  segment_default_rates.csv  default rate by every segment used in the report

Run:  python scripts/02_clean.py   (from the repo root, after 01)
"""

from pathlib import Path

import pandas as pd

RAW = Path("data/raw/default_of_credit_card_clients.xls")
OUT = Path("data/processed")

# --- Recoding maps (from the UCI data dictionary) ----------------------------
# EDUCATION: 1-4 are documented; 0, 5, 6 are undocumented codes present in the
# data — we group them as "other/unknown" rather than guessing.
EDUCATION = {1: "graduate school", 2: "university", 3: "high school",
             4: "other", 0: "other/unknown", 5: "other/unknown", 6: "other/unknown"}
MARRIAGE = {1: "married", 2: "single", 3: "other", 0: "other"}
SEX = {1: "male", 2: "female"}


def repayment_status_label(code: int) -> str:
    """PAY_* codes: -2/-1/0 mean no delay (paid duly / revolving credit);
    1+ is months behind. We collapse to an ordered label for pivoting."""
    if code <= 0:
        return "0_on_time"
    if code == 1:
        return "1_month_late"
    if code == 2:
        return "2_months_late"
    return "3+_months_late"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    # Header row is the second row of the sheet (row 0 is a banner row).
    df = pd.read_excel(RAW, header=1)
    print(f"Loaded {len(df):,} customers")

    # --- Readable column names ------------------------------------------------
    df = df.rename(columns={
        "ID": "customer_id",
        "LIMIT_BAL": "credit_limit",
        "SEX": "sex", "EDUCATION": "education", "MARRIAGE": "marital_status",
        "AGE": "age",
        # PAY_0 is September (most recent), PAY_2..PAY_6 walk back to April.
        "PAY_0": "repay_sep", "PAY_2": "repay_aug", "PAY_3": "repay_jul",
        "PAY_4": "repay_jun", "PAY_5": "repay_may", "PAY_6": "repay_apr",
        "BILL_AMT1": "bill_sep", "BILL_AMT2": "bill_aug", "BILL_AMT3": "bill_jul",
        "BILL_AMT4": "bill_jun", "BILL_AMT5": "bill_may", "BILL_AMT6": "bill_apr",
        "PAY_AMT1": "paid_sep", "PAY_AMT2": "paid_aug", "PAY_AMT3": "paid_jul",
        "PAY_AMT4": "paid_jun", "PAY_AMT5": "paid_may", "PAY_AMT6": "paid_apr",
        "default payment next month": "defaulted",
    })

    # --- Recodes and derived fields -------------------------------------------
    df["sex"] = df["sex"].map(SEX)
    df["education"] = df["education"].map(EDUCATION)
    df["marital_status"] = df["marital_status"].map(MARRIAGE)

    # Most recent repayment status drives the headline segmentation.
    df["latest_repay_status"] = df["repay_sep"].apply(repayment_status_label)

    # Age bands for pivot tables — decade bands, 60+ pooled (small sample).
    df["age_band"] = pd.cut(df["age"], [20, 30, 40, 50, 60, 100],
                            labels=["21-30", "31-40", "41-50", "51-60", "60+"],
                            right=False)

    # Credit limit bands (NT$). Quartile-ish round numbers, stated not derived,
    # so the bands stay stable if the data is refreshed.
    df["limit_band"] = pd.cut(df["credit_limit"],
                              [0, 50_000, 140_000, 240_000, 2_000_000],
                              labels=["<50k", "50-140k", "140-240k", "240k+"])

    # Utilisation: September bill as share of limit. Negative bills (credit
    # balances) floored at 0; capped at 2 to stop a few extreme rows dominating.
    df["utilisation"] = (df["bill_sep"].clip(lower=0) / df["credit_limit"]).clip(upper=2).round(3)

    df.to_csv(OUT / "clients_clean.csv", index=False)

    # --- One tidy file of default rates by segment, for charts and pivots -----
    segments = []
    for col in ["latest_repay_status", "age_band", "limit_band",
                "education", "marital_status", "sex"]:
        g = (df.groupby(col, observed=True)["defaulted"]
               .agg(customers="size", default_rate="mean").reset_index())
        g["default_rate"] = g["default_rate"].round(4)
        g.insert(0, "segment_type", col)
        g = g.rename(columns={col: "segment"})
        segments.append(g)
    seg = pd.concat(segments, ignore_index=True)
    seg.to_csv(OUT / "segment_default_rates.csv", index=False)

    # Console summary — the numbers the README quotes.
    print(f"Overall default rate: {df['defaulted'].mean():.1%}")
    print(seg[seg.segment_type == "latest_repay_status"].to_string(index=False))


if __name__ == "__main__":
    main()
