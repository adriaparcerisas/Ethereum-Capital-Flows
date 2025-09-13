# Ethereum Capital Flows & User Dynamics Dashboard

A Streamlit dashboard analyzing Ethereum’s on-chain capital flows and user dynamics.  
It focuses on institution-grade KPIs: category volumes, active user base, cohort behavior, DEX activity, lending deposits by platform, bridging, and the interaction between ETH price, activity, and fees.

---

## Executive Summary

This dashboard presents a comprehensive analysis of Ethereum’s on-chain activity, offering critical insights into capital flows and user engagement. By tracking metrics across DeFi, bridges, and fees, it provides a sophisticated perspective for crypto-savvy readers to evaluate Ethereum’s overall market traction, economic vitality, and evolving user base. All metrics are derived from canonical datasets to ensure reliability for decision-making.

August set a new all-time high for on-chain volume (≈ **$341B**), eclipsing the previous 2021 peak. The surge coincided with stronger corporate treasury accumulation, higher spot ETH ETF trading, and lower average fees, enabling heavier throughput. In parallel, protocols executed buybacks (~**$46M** in late August, with Hyperliquid ≈ **$25M**). While buybacks can stabilize prices during volatility, their long-run efficacy depends on fundamentals and sustained revenue.

The analysis highlights where capital is accumulating (DEXs, lending, bridges), how fee regimes shape adoption, and how price co-moves with network activity. Together, these signals help assess Ethereum’s durability and growth pathways.

---

## How this addresses the assignment

**Task (abridged):** Create a dashboard using Dune/Flipside or similar to evaluate a crypto project/sector/theme; ≤ **8 charts**; use relevant KPIs; include a 2–3 paragraph rationale; present findings to a panel.

**What this delivers**
- A curated **rationale** (Executive Summary above) that motivates the topic and ties it to current market context.
- **Eight core charts** geared to an expert audience, plus two optional analytical add-ons that can be hidden if a strict eight-chart limit is enforced.
- **KPIs and definitions** embedded in each section to make assessment of code accuracy and metric relevance straightforward.
- Reproducible Python/Streamlit code with clear data expectations.

---

## Core Visuals (8)

1. **Monthly On-Chain USD Volume by Category** — stacked volumes (billions) across major verticals; highlights peak throughput and category mix.  
2. **Active Addresses & Transactions by Category** — dual-axis view of user base and activity load.  
3. **User Cohorts by Monthly USD Volume** — cohort distribution (e.g., whales vs. retail) and contribution to total flow.  
4. **User Typology (100% Stacked)** — multi-sector vs. single-sector participation and engagement.  
5. **DEX Volume & Active Swappers** — core DeFi utilization signal.  
6. **Lending Deposits — Evolution per Platform** — deposit depth and platform share over time.  
7. **Total Bridge Volume** — cross-chain connectivity and liquidity migration.  
8. **ETH Price Overlay with Total Activity** — co-movement between price and a composite activity index.

**Optional analytical add-ons (hide if needed for ≤8):**
- **User Adoption During Fee Evolution** — unique users vs. average fee (USD).  
- **Price vs. Fee Correlation** — scatter with OLS trendline.

---

## Run locally

```bash
# (Optional) Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Launch the app
streamlit run app.py
````

---

## Data & methodology (concise)

* **Time axis**: `MONTH` parsed with `pandas.to_datetime`.
* **Scaling**: columns ending in `_BILLIONS` are already scaled (e.g., `2.5` = \$2.5B); values in USD use standard formatting.
* **Shares & dominance**: computed per-month from category sums.
* **Correlations**: Pearson on overlapping, non-NaN pairs.
* **Trendlines**: Plotly OLS (requires `statsmodels`, included).

---

## What reviewers should look for

* **Metric definition fidelity** (e.g., category volumes, cohort composition, platform shares).
* **Code correctness** (explicit column names, defensive parsing, rolling calculations kept transparent).
* **Interpretability** (KPI badges + succinct definitions/insights per visualization).
* **Judgment** (why these eight visuals best capture traction, sustainability, and user dynamics).

---

## Troubleshooting (already handled)

* **Mixed delimiters / BOM in CSVs** → robust CSV loader auto-detects separators and trims BOM.
* **Inconsistent date formats** → automatic `MONTH` parsing with graceful fallback.
* **Missing optional columns** → sections degrade gracefully and display helpful notices.
* **Trendline dependency** → `statsmodels` is included to avoid missing OLS fits.

---

## License & attribution

MIT.
Built by **Adrià Parcerisas**. Data via Flipside/Dune-style exports and curated datasets suitable for reproducible evaluation.


