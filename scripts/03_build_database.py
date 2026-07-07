"""
03_build_database.py
--------------------
Loads the processed CSVs into SQLite so sql/analysis_queries.sql runs as
written.

Output:  data/credit.db  (gitignored — rebuild any time)

Run:   python scripts/03_build_database.py
Then:  sqlite3 data/credit.db
       .mode column
       .headers on
       .read sql/analysis_queries.sql
"""

import sqlite3
from pathlib import Path

import pandas as pd

DB_FILE = Path("data/credit.db")
PROCESSED = Path("data/processed")

TABLES = {
    "clients": "clients_clean.csv",
    "segment_rates": "segment_default_rates.csv",
}


def main() -> None:
    DB_FILE.unlink(missing_ok=True)
    conn = sqlite3.connect(DB_FILE)

    for table, csv_name in TABLES.items():
        df = pd.read_csv(PROCESSED / csv_name)
        df.to_sql(table, conn, index=False)
        print(f"  {table:14s} {len(df):>7,} rows")

    cur = conn.cursor()
    cur.execute("CREATE INDEX idx_clients_status ON clients(latest_repay_status)")
    cur.execute("CREATE INDEX idx_clients_default ON clients(defaulted)")
    conn.commit()
    conn.close()
    print(f"Database ready: {DB_FILE}")


if __name__ == "__main__":
    main()
