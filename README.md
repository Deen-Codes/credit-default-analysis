# Who Defaults? Credit Card Risk in 30,000 Customers

**How well does last month's repayment behaviour predict next month's
default?** An analysis of the UCI "Default of Credit Card Clients" dataset —
30,000 real credit card customers with demographics, credit limits, six
months of repayment history and a default flag — using Python, SQL and
dashboard tooling.

**[→ Live dashboard](https://deen-codes.github.io/credit-default-analysis/)** · **[Tableau version](https://public.tableau.com/app/profile/deen.ali/viz/CreditCardDefaultRisk-UKPortfolioProject/Dashboard1)**

> **Headline:** one missed payment changes everything. Customers current on
> their payments defaulted at **13.8%**; one month behind, **34.0%**; two
> months behind, **69.1%**. Delinquency status dwarfs every demographic
> variable in this data.

---

## Key findings

**1. Repayment status is the signal.** Default rates by latest status:
on time 13.8% → 1 month late 34.0% → 2 months late 69.1% → 3+ months 71.9%.
Nothing demographic comes close to this gradient.

**2. But the base-rate trap is real.** The *rate* is highest among the
delinquent, yet **48% of all defaulters were "on time" last month** — because
on-time customers are 77% of the book. A collections team watching only the
delinquent list misses half of next month's defaults. This distinction —
risk rate vs share of risk — is the most useful sentence in the project.

**3. The credit limit already encodes risk.** Default rate falls monotonically
with limit: 31.8% in the <NT$50k band vs 14.0% in the 240k+ band, and the
median defaulter's limit (NT$90k) is 40% below the median non-defaulter's
(NT$150k). The bank's own limit decisions are a visible risk score.

**4. A three-rule risk flag beats demographics.** A simple traffic-light flag
(red = 2+ months late, or 1 month late with 80%+ utilisation) isolates a
red group of 3,918 customers defaulting at **63.5%** — while the green group
defaults at 13.1%. Three business rules recover most of the signal a model
would; the value of a model is the middle amber band.

**5. Age and education move the needle far less** — default rates sit within
a few points of the 22.1% overall rate across age bands (20.3%–28.3%) and
education levels, and small segments (60+, "other") have wide uncertainty.

<!-- TODO: screenshots once built:
![Dashboard](tableau/dashboard.png)
![Pivot analysis](spreadsheet/pivots.png)
-->

## How it's built

```
scripts/01_fetch.py           UCI download -> data/raw/
scripts/02_clean.py           readable columns, documented recodes -> data/processed/
scripts/03_build_database.py  SQLite -> data/credit.db
sql/analysis_queries.sql      10 questions (CTEs, window functions, risk flag)
credit_analysis.xlsx          Excel workbook: segment pivots, lookups, charts
```

Reproduce:

```bash
pip install -r requirements.txt
python scripts/01_fetch.py
python scripts/02_clean.py
python scripts/03_build_database.py
sqlite3 data/credit.db        # .read sql/analysis_queries.sql
```

## Limitations

- **Taiwan, 2005.** Behavioural patterns (delinquency → default) travel well
  across markets; absolute rates and currency amounts do not. Treat this as
  a methods showcase, not a UK credit model.
- **One-month outcome window.** "Default next month" is a short horizon;
  lifetime default behaves differently.
- **Undocumented codes.** EDUCATION values 0, 5, 6 are not in the data
  dictionary; they are grouped as "other/unknown" rather than guessed at.
- **No income data.** Utilisation and limit act as income proxies, which is
  exactly how they'd behave in a real bank dataset — but it caps how much
  the demographic comparisons can say.

## Data source & licence

- [UCI Machine Learning Repository — Default of Credit Card Clients](https://archive.ics.uci.edu/dataset/350)
  (CC BY 4.0). Citation: Yeh, I-C. (2016).

## Author

**Deen Ali** — five years in UK retail banking (fraud & KYC, Halifax) before
moving into data analysis. [github.com/deen-codes](https://github.com/deen-codes) ·
[linkedin.com/in/deen321](https://linkedin.com/in/deen321)
