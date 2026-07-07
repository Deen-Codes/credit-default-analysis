-- ============================================================================
-- analysis_queries.sql
-- Ten questions about credit card default risk (UCI Taiwan dataset, 30,000
-- customers). Run: sqlite3 data/credit.db  →  .read sql/analysis_queries.sql
--
-- Tables:
--   clients        one row per customer (cleaned, readable columns)
--   segment_rates  default rate by pre-computed segment
-- ============================================================================


-- Q1. The headline: how does repayment status predict default?
SELECT   latest_repay_status,
         COUNT(*)                                   AS customers,
         ROUND(AVG(defaulted) * 100, 1)             AS default_rate_pct
FROM     clients
GROUP BY latest_repay_status
ORDER BY latest_repay_status;


-- Q2. Default rate by credit limit band — does the bank already know?
-- Lower limits carry higher default rates: the limit itself encodes the
-- bank's own prior risk assessment.
SELECT   limit_band,
         COUNT(*)                        AS customers,
         ROUND(AVG(defaulted) * 100, 1)  AS default_rate_pct,
         CAST(AVG(credit_limit) AS INT)  AS avg_limit
FROM     clients
GROUP BY limit_band
ORDER BY avg_limit;


-- Q3. Age: mostly flat until 50+, where risk creeps up.
SELECT   age_band,
         COUNT(*)                        AS customers,
         ROUND(AVG(defaulted) * 100, 1)  AS default_rate_pct
FROM     clients
GROUP BY age_band
ORDER BY age_band;


-- Q4. Compound risk: repayment status WITHIN each limit band.
-- Shows the two effects are independent — being behind is bad at every
-- limit level, and low limits are worse at every delinquency level.
SELECT   limit_band,
         latest_repay_status,
         COUNT(*)                        AS customers,
         ROUND(AVG(defaulted) * 100, 1)  AS default_rate_pct
FROM     clients
GROUP BY limit_band, latest_repay_status
HAVING   customers >= 50                 -- suppress tiny unstable cells
ORDER BY limit_band, latest_repay_status;


-- Q5. High utilisation + behind on payments: the riskiest combination.
SELECT   CASE WHEN utilisation >= 0.8 THEN 'high (80%+)'
              WHEN utilisation >= 0.4 THEN 'medium (40-80%)'
              ELSE 'low (<40%)' END      AS utilisation_band,
         CASE WHEN repay_sep > 0 THEN 'behind' ELSE 'on time' END AS status,
         COUNT(*)                        AS customers,
         ROUND(AVG(defaulted) * 100, 1)  AS default_rate_pct
FROM     clients
GROUP BY utilisation_band, status
ORDER BY default_rate_pct DESC;


-- Q6. How much of the default population sits in each status bucket?
-- Risk RATE is highest for 2+ months late, but most defaultERS were
-- "on time" last month — the base-rate trap in one query.
SELECT   latest_repay_status,
         SUM(defaulted)                                        AS defaulters,
         ROUND(100.0 * SUM(defaulted) /
               (SELECT SUM(defaulted) FROM clients), 1)        AS pct_of_all_defaulters
FROM     clients
GROUP BY latest_repay_status
ORDER BY defaulters DESC;


-- Q7. Median credit limit, defaulters vs non-defaulters (window-function
-- median, since SQLite has no MEDIAN aggregate).
WITH ranked AS (
    SELECT defaulted, credit_limit,
           ROW_NUMBER() OVER (PARTITION BY defaulted ORDER BY credit_limit) AS rn,
           COUNT(*)    OVER (PARTITION BY defaulted)                        AS n
    FROM clients
)
SELECT   defaulted,
         AVG(credit_limit) AS median_credit_limit
FROM     ranked
WHERE    rn IN ((n + 1) / 2, (n + 2) / 2)
GROUP BY defaulted;


-- Q8. Did customers who defaulted pay less of their bills through the summer?
-- Payment-to-bill ratio June-August, guarded against divide-by-zero.
SELECT   defaulted,
         COUNT(*) AS customers,
         ROUND(AVG(CASE WHEN bill_aug > 0 THEN CAST(paid_aug AS REAL) / bill_aug END), 3) AS avg_aug_payment_ratio,
         ROUND(AVG(CASE WHEN bill_jul > 0 THEN CAST(paid_jul AS REAL) / bill_jul END), 3) AS avg_jul_payment_ratio
FROM     clients
GROUP BY defaulted;


-- Q9. Rank education segments by default rate with sample sizes visible —
-- always show the denominator before quoting a segment difference.
SELECT   education,
         COUNT(*)                        AS customers,
         ROUND(AVG(defaulted) * 100, 1)  AS default_rate_pct,
         RANK() OVER (ORDER BY AVG(defaulted) DESC) AS risk_rank
FROM     clients
GROUP BY education
ORDER BY risk_rank;


-- Q10. A simple three-tier risk flag an analyst could hand to a business
-- team, and how it performs.
WITH scored AS (
    SELECT *,
           CASE WHEN repay_sep >= 2 OR (repay_sep = 1 AND utilisation >= 0.8)
                     THEN 'red'
                WHEN repay_sep = 1 OR utilisation >= 0.8
                     THEN 'amber'
                ELSE 'green' END AS risk_flag
    FROM clients
)
SELECT   risk_flag,
         COUNT(*)                        AS customers,
         ROUND(AVG(defaulted) * 100, 1)  AS default_rate_pct,
         SUM(defaulted)                  AS defaulters_caught
FROM     scored
GROUP BY risk_flag
ORDER BY default_rate_pct DESC;
