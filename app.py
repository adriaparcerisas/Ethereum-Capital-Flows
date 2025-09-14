# app.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
import os

# -----------------------------------------------------------
# Page config
# -----------------------------------------------------------
st.set_page_config(
    page_title="Ethereum On-Chain Traction — Capital Flows & User Dynamics",
    page_icon="📈",
    layout="wide"
)

# -----------------------------------------------------------
# CSS  (light mode, single separators, compact KPI chips)
# -----------------------------------------------------------
st.markdown("""
<style>
:root{
  --border:#dbe4f3; --text:#0f172a; --muted:#475569; --soft:#f8fafc;
  --pill-bg:#eef2ff; --pill-text:#3730a3; --badge:#e2e8f0; --accent:#0ea5e9;
  --sep:#e5edf7;
  --kpi-a:#14b8a6; /* teal: activity */
  --kpi-b:#7c3aed; /* violet: cohort/typology */
  --kpi-c:#1d4ed8; /* blue: volumes/tx */
  --kpi-d:#10b981; /* green: lending/bridge */
}
html,body,[class^="css"],.stApp{color:var(--text);}

h1,h2,h3{margin:0 0 .3rem 0; font-weight:800;}
.section-title{font-size:1.35rem; font-weight:800; margin:.25rem 0 .5rem 0;}
.section-def{background:#f6f8ff; border:1px solid var(--border); padding:.8rem 1rem; border-radius:.75rem; margin:.25rem 0 1rem 0; color:var(--muted);}
.def-pill{display:inline-block; font-weight:700; color:var(--pill-text); background:var(--pill-bg); border-radius:999px; padding:.15rem .6rem; margin-right:.6rem; border:1px solid #c7d2fe;}

.sep{height:1px; background:var(--sep); margin:1.25rem 0 .85rem 0;}

.card{background:#fff; border:1px solid var(--border); border-radius:.9rem; padding:1rem;}
.card.tight{padding:.6rem .85rem;}

.hero{background:#fff; border:1px solid var(--border); border-radius:1rem; padding:1rem 1.2rem;}
.hero .context{background:#f7f9ff; border:1px solid var(--border); padding:.9rem 1rem; border-radius:.75rem; color:var(--muted);}

/* KPI compact chip */
.kpi{display:flex; align-items:center; gap:.6rem;
     border:1px solid var(--border); border-radius:.75rem;
     padding:.55rem .8rem; font-size:1.05rem; background:#fff;}
.kpi .stripe{width:.4rem; height:1.35rem; border-radius:.25rem;}
.kpi .v{font-weight:800;}

/* color map */
.kpi.a .stripe{background:var(--kpi-a);}  /* teal */
.kpi.b .stripe{background:var(--kpi-b);}  /* violet */
.kpi.c .stripe{background:var(--kpi-c);}  /* blue */
.kpi.d .stripe{background:var(--kpi-d);}  /* green */

/* Insight pill */
.insight{background:#f6faff; border:1px solid var(--border);
         padding:.8rem 1rem; border-radius:.75rem; margin:.6rem 0 0 0;}
.insight strong{margin-right:.35rem;}
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------
# Helpers
# -----------------------------------------------------------
DATA_DIR = Path("data")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def read_csv(name: str, parse_month=True):
    fp = DATA_DIR / name
    if not fp.exists():
        st.info(f"Missing data file: {name}")
        return pd.DataFrame()
    df = pd.read_csv(fp)
    if parse_month and "MONTH" in df.columns:
        df["MONTH"] = pd.to_datetime(df["MONTH"])
    return df

def draw_section(title: str, definition: str):
    st.markdown('<div class="sep"></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-def"><span class="def-pill">Definition</span>{definition}</div>', unsafe_allow_html=True)

def kpi_inline(container, html: str, style: str = "c"):
    container.markdown(f'<div class="kpi {style}"><div class="stripe"></div><div>{html}</div></div>', unsafe_allow_html=True)

def insight(text: str):
    st.markdown(f'<div class="insight"><strong>Insight.</strong>{text}</div>', unsafe_allow_html=True)

# Color classes map (match series)
KPI_STYLE = {
    "teal": "a",   # users/addresses/swappers
    "violet": "b", # typology derived
    "blue": "c",   # volume/tx
    "green": "d",  # lending/bridge
}

# -----------------------------------------------------------
# Title + Executive Summary (whole text inside "context" box)
# -----------------------------------------------------------
st.markdown(
    "<h1>Ethereum On-Chain Traction at New High — Capital Flows & User Dynamics</h1>",
    unsafe_allow_html=True
)
st.caption("Data as of most recent month available")

st.markdown("""
<div class="section">
  <div class="section-title">Executive Summary: Assessing Ethereum’s Traction</div>
  <div class="section-def">
    <span class="def-pill">Context</span>
    <span>
This dashboard analyzes why Ethereum’s on-chain activity is surging and whether it is translating into price. It combines throughput (USD volume), usage breadth (active addresses/transactions), execution costs (fees), and external demand signals (ETF primary flows, policy-rate expectations). It concludes with a composite Macro-Chain Impulse Score (MCIS) to summarize the net macro tailwind/headwind on activity and price.<br><br>

<strong>August set a new record high in on-chain USD volume (~$341B)</strong> (<a href="https://crypto.com/us/research/research-roundup-sep-2025" target="_blank" rel="noopener">Crypto.com Research</a>, <a href="https://cryptorank.io/news/feed/d31b4-why-ethereum-just-posted-its-third-biggest-month-in-history" target="_blank" rel="noopener">CryptoRank</a>) registering levels not seen since May 2021, with activity broadening across sectors. The rise coincided with lower average fees (improved affordability) and positive ETF net flows (exogenous demand). These drivers align with an uptick in a simple activity index and a constructive MCIS reading.<br><br>

<strong>Key findings.</strong><br>
(i) When fees compress and ETF net flows are positive, activity scales;<br>
(ii) rate-cut-leaning months are generally supportive risk-on regimes; and<br>
(iii) activity and price tend to co-move, but MCIS helps distinguish durable demand from temporary bursts.<br><br>

This view sets the stage for the panel discussion: the sustainability of the move, the durability of demand, and where capital and usage are concentrating across Ethereum’s ecosystem.
    </span>
  </div>
</div>
<hr class="sep">
""", unsafe_allow_html=True)




# -----------------------------------------------------------
# Load data
# -----------------------------------------------------------
df_volcat   = read_csv("volume_category.csv")      # MONTH, CATEGORY, VOLUME_USD, VOLUME_USD_BILLIONS
#df_active   = read_csv("active_addresses.csv")     # MONTH, CATEGORY, ACTIVE_ADDRESSES, TRANSACTIONS
df_cohort   = read_csv("user_cohort.csv")          # MONTH, COHORT, UNIQUE_USERS, TOTAL_VOLUME, AVG_VOLUME_PER_USER
df_typology = read_csv("user_typology.csv")        # MONTH, USER_TYPE, ACTIVITY_LEVEL, UNIQUE_USERS, AVG_VOLUME_PER_USER, AVG_TRANSACTIONS_PER_USER
df_dex      = read_csv("dex_volume.csv")           # MONTH, ACTIVE_SWAPPERS, TOTAL_VOLUME_USD, TOTAL_VOLUME_BILLIONS, AVG_SWAP_SIZE, TOTAL_SWAPS
df_bridge   = read_csv("bridged_volume.csv")       # MONTH, INFLOW_BILLIONS, OUTFLOW_BILLIONS, NET_FLOW_BILLIONS, UNKNOWN_FLOW_BILLIONS, TOTAL_BRIDGE_VOLUME_BILLIONS
df_eth      = read_csv("eth_price.csv")            # MONTH, AVG_ETH_PRICE_USD, TOTAL_TRANSACTIONS, UNIQUE_USERS, TOTAL_VOLUME_BILLIONS, ACTIVITY_INDEX
df_lend     = read_csv("lending_deposits.csv")     # MONTH, PLATFORM, UNIQUE_DEPOSITORS, TOTAL_DEPOSIT_VOLUME, VOLUME_BILLIONS, AVG_DEPOSIT_SIZE, MONTHLY_TOTAL_BILLIONS, PLATFORM_MARKET_SHARE
df_fees     = read_csv("fees_activity.csv")        # MONTH, AVG_FEE_USD, FEE_CATEGORY, TOTAL_TRANSACTIONS, UNIQUE_USERS, TRANSACTIONS_MILLIONS, USERS_MILLIONS, ...
def load_active_activity(path="data/active_addresses.csv"):
    """
    Reads MONTH;SECTOR;AVG_DAILY_ACTIVE_ADDRESSES;TRANSACTIONS
    Accepts ';' or ',' (auto-detect). Parses MONTH (YYYY-MM), trims SECTOR, and
    coerces numeric columns.
    """
    with open(path, "r", encoding="utf-8") as f:
        head = f.read(4096)
    default_sep = ";" if head.count(";") > head.count(",") else ","

    df = pd.read_csv(
        path,
        sep=default_sep if default_sep in [";", ","] else None,
        engine="python"
    )

    # Normalize columns
    df.columns = [c.strip() for c in df.columns]
    rename_map = {
        "Month": "MONTH",
        "Sector": "SECTOR",
        "Avg_Daily_Active_Addresses": "AVG_DAILY_ACTIVE_ADDRESSES",
        "Transactions": "TRANSACTIONS",
    }
    df.rename(columns=rename_map, inplace=True)

    expected = {"MONTH", "SECTOR", "AVG_DAILY_ACTIVE_ADDRESSES", "TRANSACTIONS"}
    missing = expected - set(df.columns)
    if missing:
        st.warning(f"[active_addresses.csv] Missing columns: {', '.join(sorted(missing))}")
        return pd.DataFrame(columns=list(expected))

    df["MONTH"] = pd.to_datetime(df["MONTH"], format="%Y-%m", errors="coerce")
    df["SECTOR"] = df["SECTOR"].astype(str).str.strip()

    for c in ["AVG_DAILY_ACTIVE_ADDRESSES", "TRANSACTIONS"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    df = df.dropna(subset=["MONTH", "SECTOR"])
    df = df.sort_values(["MONTH", "SECTOR"], kind="stable").reset_index(drop=True)
    return df

# Call the loader
df_active = load_active_activity("data/active_addresses.csv")
# -----------------------------------------------------------
# 1) Monthly On-Chain USD Volume by Category  (Stacked Area)
# -----------------------------------------------------------
draw_section(
    "1. Monthly On-Chain USD Volume by Category",
    "Stacked on-chain volume (USD billions) by vertical; highlights peak throughput and category mix."
)

if not df_volcat.empty:
    latest_month = df_volcat["MONTH"].max()
    peak_total = df_volcat.groupby("MONTH")["VOLUME_USD_BILLIONS"].sum().max()

    c1, c2 = st.columns(2)
    kpi_inline(c1, f"<strong>Peak Volume:</strong> <span class='v'>${peak_total:,.2f}B</span>", style=KPI_STYLE["teal"])
    # quick dominance proxy: DEX share latest
    dex_share = df_volcat.query("MONTH == @latest_month").pipe(
        lambda d: 100 * d.loc[d["CATEGORY"]=="DEX Trading","VOLUME_USD_BILLIONS"].sum() / d["VOLUME_USD_BILLIONS"].sum()
        if d["VOLUME_USD_BILLIONS"].sum() else np.nan
    )
    kpi_inline(c2, f"<strong>DEX Dominance (latest):</strong> <span class='v'>{dex_share:,.1f}%</span>", style=KPI_STYLE["blue"])

    cats = df_volcat["CATEGORY"].unique().tolist()
    colors = {
        "Bridge Activity":"#14b8a6",
        "DEX Trading":"#1d4ed8",
        "Lending Deposits":"#10b981",
        "Lending Borrows":"#7c3aed",
        "Liquidations":"#f59e0b",
        "NFT Sales":"#fb7185",
        "Token Transfers":"#64748b"
    }

    fig = go.Figure()
    for cat in cats:
        d = df_volcat[df_volcat["CATEGORY"]==cat].sort_values("MONTH")
        fig.add_trace(go.Scatter(
            x=d["MONTH"], y=d["VOLUME_USD_BILLIONS"],
            name=cat, mode="lines", stackgroup="one",
            line=dict(width=0.7, color=colors.get(cat, "#94a3b8"))
        ))
    fig.update_layout(
        height=420, margin=dict(l=10,r=10,t=20,b=10),
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, x=0),
        yaxis_title="Volume (USD Billions)"
    )
    st.plotly_chart(fig, use_container_width=True)

    insight("Throughput printed a new high in August (~$341B). Flow remains concentrated in DEXs and lending, while bridges and token transfers provide breadth. Mix helps read risk-on (DEX/lending heavy) vs. defensive rotations.")


# -----------------------------------------------------------
# 2) Monthly Active Addresses and Transactions by Sector (Toggle)
# -----------------------------------------------------------
draw_section(
    "2. Monthly Active Addresses and Transactions by Sector",
    "Choose one metric at a time to isolate user base (avg daily active addresses) vs network load (transactions)."
)

if not df_active.empty:
    # Expecting MONTH, SECTOR, AVG_DAILY_ACTIVE_ADDRESSES, TRANSACTIONS
    required = {"MONTH","SECTOR","AVG_DAILY_ACTIVE_ADDRESSES","TRANSACTIONS"}
    missing = required - set(df_active.columns)
    if missing:
        st.warning(f"Active activity CSV missing columns: {', '.join(sorted(missing))}")
    else:
        # ❗ Merge NFT Transfers into Others (token transfers)
        data = df_active.copy()
        data["SECTOR"] = data["SECTOR"].replace({"NFT Transfers": "Others"})
        # aggregate in case both 'Others' and 'NFT Transfers' existed for a month
        data = (
            data.groupby(["MONTH","SECTOR"], as_index=False)
                .agg({
                    "AVG_DAILY_ACTIVE_ADDRESSES": "sum",
                    "TRANSACTIONS": "sum"
                })
                .sort_values(["MONTH","SECTOR"])
        )

        # UI: metric toggle
        metric = st.radio(
            "Metric", options=["Avg Daily Active Addresses","Transactions"],
            horizontal=True, index=0, key="active_metric"
        )
        if metric == "Avg Daily Active Addresses":
            y_col = "AVG_DAILY_ACTIVE_ADDRESSES"
            kpi_style = KPI_STYLE["teal"]   # users
        else:
            y_col = "TRANSACTIONS"
            kpi_style = KPI_STYLE["blue"]   # tx

        latest = data["MONTH"].max()
        d_last = data[data["MONTH"]==latest]

        # KPIs
        peak_val = data.groupby("MONTH")[y_col].sum().max()
        c1, c2 = st.columns(2)
        kpi_inline(
            c1,
            f"<strong>Peak {metric}:</strong> <span class='v'>{peak_val:,.0f}</span>",
            style=kpi_style
        )

        dex_share = np.nan
        if not d_last.empty and d_last[y_col].sum() > 0:
            dex_share = 100 * d_last.loc[d_last["SECTOR"]=="DEX Trading", y_col].sum() / d_last[y_col].sum()
        kpi_inline(
            c2,
            f"<strong>DEX Trading Share (latest):</strong> <span class='v'>{(0 if pd.isna(dex_share) else dex_share):,.1f}%</span>",
            style=KPI_STYLE["blue"]
        )

        # Fixed order (without a separate NFT Transfers; it's merged into Others)
        desired_order = [
            "DEX Trading",
            "Lending Deposits",
            "Lending Borrows",
            "NFT Sales",
            "Others",  # includes NFT Transfers
        ]
        # Keep unexpected sectors (if any) at the end
        seen = [s for s in desired_order if s in data["SECTOR"].unique()]
        tail = [s for s in data["SECTOR"].unique() if s not in desired_order]
        sectors_order = seen + tail

        # Colors per sector
        sector_colors = {
            "DEX Trading": "#1d4ed8",       # blue
            "Lending Deposits": "#10b981",  # green
            "Lending Borrows": "#7c3aed",   # violet
            "NFT Sales": "#f59e0b",         # amber
            "Others": "#64748b",            # slate  (now includes NFT Transfers)
        }

        # Plot lines per sector
        fig2 = go.Figure()
        for sec in sectors_order:
            d = data[data["SECTOR"]==sec].sort_values("MONTH")
            if d.empty:
                continue
            fig2.add_trace(go.Scatter(
                x=d["MONTH"], y=d[y_col], name=sec,
                mode="lines+markers",
                line=dict(width=2, color=sector_colors.get(sec, None))
            ))
        fig2.update_layout(
            height=420, margin=dict(l=10, r=10, t=10, b=10),
            yaxis_title=metric,
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, x=0)
        )
        st.plotly_chart(fig2, use_container_width=True)

        insight("Breadth and load trend higher. ‘Others’ (token transfers, incl. NFT transfers) is among the fastest-growing segments, while DEX trading and lending remain the cyclical anchors of network demand.")


# ================================
# 3) Activity Drivers — Fees, ETF Flows & Rates Direction
# ================================
import os, pandas as pd, numpy as np, altair as alt, streamlit as st

# --- light fallback for kpi cards if your helper isn't present
#if "kpi_card" not in globals():
#    def kpi_card(title: str, value: str, color: str = "#2563eb"):
#        st.markdown(
#            f"""
#            <div style="
#                border:1px solid #e5e7eb;border-left:6px solid {color};
#                border-radius:10px;padding:10px 12px;margin:4px 0;">
#                <div style="font-size:12px;color:#6b7280;margin-bottom:2px;">{title}</div>
#                <div style="font-size:18px;font-weight:600;color:#111827;">{value}</div>
#            </div>
#            """,
#            unsafe_allow_html=True,
#        )

# ---------- Metric card helpers (light-mode boxes) ----------
from textwrap import dedent

if "kpi_card" not in globals():
    def kpi_card(label: str, value: str, pill: str | None = None, pill_color: str = "#10B981"):
        """
        Render a KPI in a rounded card with a thin border and optional pill badge.
        - label: small heading text
        - value: main number/text
        - pill: optional badge text (e.g., 'Tailwind', 'Headwind', 'Neutral')
        - pill_color: badge color (hex)
        """
        pill_html = (
            f"""<span style="
                    display:inline-block;padding:2px 10px;margin-left:8px;
                    border-radius:999px;font-size:12px;
                    background:{pill_color};color:white;">{pill}</span>"""
            if pill else ""
        )

        st.markdown(
            dedent(f"""
            <div style="
                border:1px solid rgba(23,43,77,0.15);
                border-left:6px solid rgba(59,130,246,0.85);
                border-radius:14px; padding:14px 16px; background:#F8FAFC;">
                <div style="font-size:13px; color:#475569; font-weight:600; margin-bottom:6px;">
                    {label}
                </div>
                <div style="font-size:26px; color:#0F172A; font-weight:700; line-height:1.1;">
                    {value}{pill_html}
                </div>
            </div>
            """),
            unsafe_allow_html=True,
        )


if "draw_metrics_row" not in globals():
    def draw_metrics_row(metrics: list[dict], cols: int = 4):
        """
        metrics = [
          {"label": "...", "value": "...", "pill": "Tailwind", "pill_color": "#10B981"},
          ...
        ]
        """
        cols = st.columns(cols)
        for i, m in enumerate(metrics):
            with cols[i % len(cols)]:
                kpi_card(
                    m.get("label", ""),
                    m.get("value", "—"),
                    m.get("pill"),
                    m.get("pill_color", "#10B981"),
                )


def _to_month(s: pd.Series) -> pd.Series:
    """Coerce to 'YYYY-MM' (tz-naive)."""
    dt = pd.to_datetime(s, errors="coerce", utc=True).dt.tz_localize(None)
    return dt.dt.to_period("M").astype(str)

def _coerce_num(s, div=None):
    out = pd.to_numeric(s, errors="coerce")
    if div:
        out = out / div
    return out

def _fmt_money_m(x):
    if pd.isna(x):
        return "—"
    return f"${x:,.0f}M"

# ---- Load sources
try:
    fees_p = pd.read_csv("data/fees_price.csv")
except Exception:
    fees_p = pd.DataFrame()
try:
    eth_p = pd.read_csv("data/eth_price.csv")
except Exception:
    eth_p = pd.DataFrame()

etf_m   = pd.read_csv("data/etf_flows_monthly.csv")
rates_m = pd.read_csv("data/rates_expectations_monthly.csv")
fed_m   = pd.read_csv("data/fedfunds_history_monthly.csv")

# Normalize MONTH for all
for df in [etf_m, rates_m, fed_m, fees_p, eth_p]:
    if not df.empty:
        if "MONTH" in df.columns:
            df["MONTH"] = _to_month(df["MONTH"])
        elif "DATE" in df.columns:
            df["MONTH"] = _to_month(df["DATE"])

# Fees: ensure AVG_TX_FEE_USD exists (fallback = ETH fee * price)
if not fees_p.empty:
    if "AVG_TX_FEE_USD" not in fees_p.columns:
        if set(["AVG_TX_FEE_ETH","AVG_ETH_PRICE_USD"]).issubset(fees_p.columns):
            fees_p["AVG_TX_FEE_USD"] = _coerce_num(fees_p["AVG_TX_FEE_ETH"]) * _coerce_num(fees_p["AVG_ETH_PRICE_USD"])
        else:
            fees_p["AVG_TX_FEE_USD"] = np.nan
    fees_p = fees_p[["MONTH","AVG_TX_FEE_USD"]].drop_duplicates("MONTH")

# ETH price & activity
if not eth_p.empty:
    keep_cols = [c for c in ["MONTH","ACTIVITY_INDEX","AVG_ETH_PRICE_USD"] if c in eth_p.columns]
    eth_p = eth_p[keep_cols].drop_duplicates("MONTH")

# ETF flows (monthly sums)
if "ETF_NET_FLOW_USD_MILLIONS" in etf_m.columns:
    etf_m = etf_m[["MONTH","ETF_NET_FLOW_USD_MILLIONS"]].groupby("MONTH", as_index=False).sum()
else:
    etf_m["ETF_NET_FLOW_USD_MILLIONS"] = np.nan
    etf_m = etf_m[["MONTH","ETF_NET_FLOW_USD_MILLIONS"]]

# Rates: clean prob to [0,1]
if "RATES_PROB" in rates_m.columns:
    p95 = pd.to_numeric(rates_m["RATES_PROB"], errors="coerce").quantile(0.95)
    if pd.notna(p95) and p95 > 1.5:  # looks like 0–100
        rates_m["RATES_PROB"] = pd.to_numeric(rates_m["RATES_PROB"], errors="coerce")/100.0
    else:
        rates_m["RATES_PROB"] = pd.to_numeric(rates_m["RATES_PROB"], errors="coerce")
else:
    rates_m["RATES_PROB"] = np.nan
if "RATES_DIR" not in rates_m.columns:
    rates_m["RATES_DIR"] = np.nan
rates_m = rates_m[["MONTH","RATES_DIR","RATES_PROB"]].drop_duplicates("MONTH")

# Merge panel on MONTH
panel = None
for d in [eth_p, fees_p, etf_m, rates_m]:
    if d is None or d.empty:
        continue
    panel = d if panel is None else panel.merge(d, on="MONTH", how="outer")

# STOP if empty
if panel is None or panel.empty:
    draw_section(
        "3. Activity Drivers — Fees, ETF Flows & Rates Direction",
        definition=(
        "Relates <strong>transaction costs</strong>, <strong>ETF net flows</strong> and "
        "<strong>policy direction</strong> to Ethereum’s on-chain activity. "
        "Ethereum recently recorded <strong>all-time-high levels of on-chain activity</strong>, "
        "marking one of the busiest months in its history "
        "([Crypto.com Research, Sep 2025](https://crypto.com/us/research/research-roundup-sep-2025); "
        "[CryptoRank, 2025](https://cryptorank.io/news/feed/d31b4-why-ethereum-just-posted-its-third-biggest-month-in-history)). "
        "This section investigates the <em>drivers</em> behind that surge — namely whether lower fees, stronger ETF inflows, "
        "and shifting interest-rate expectations can explain the rise, and how these factors may spill over to ETH price."
    ),
    )
    st.info("Data not found. Ensure these exist under /data: eth_price.csv, fees_price.csv, etf_flows_monthly.csv, rates_expectations_monthly.csv, fedfunds_history_monthly.csv.")
    st.stop()


# Sort, coerce, and drop September 2025+
panel["MONTH_DT"] = pd.to_datetime(panel["MONTH"], format="%Y-%m", errors="coerce")
panel = panel.sort_values("MONTH_DT")

# EXCLUDE any data beyond 2025-08
cutoff = pd.to_datetime("2025-08")
panel = panel[panel["MONTH_DT"] <= cutoff]

for c in ["ACTIVITY_INDEX","AVG_TX_FEE_USD","ETF_NET_FLOW_USD_MILLIONS","AVG_ETH_PRICE_USD"]:
    if c in panel.columns:
        panel[c] = pd.to_numeric(panel[c], errors="coerce")

# Latest row for KPIs
latest = panel.dropna(subset=["MONTH_DT"]).tail(1).squeeze()
k1 = latest["ACTIVITY_INDEX"] if "ACTIVITY_INDEX" in panel.columns else np.nan
k2 = latest["AVG_TX_FEE_USD"] if "AVG_TX_FEE_USD" in panel.columns else np.nan
k3 = latest["ETF_NET_FLOW_USD_MILLIONS"] if "ETF_NET_FLOW_USD_MILLIONS" in panel.columns else np.nan
k4_dir = latest["RATES_DIR"] if "RATES_DIR" in panel.columns else np.nan
k4_p   = latest["RATES_PROB"] if "RATES_PROB" in panel.columns else np.nan

# --- Render section
draw_section(
    "3) Activity Drivers — Fees, ETF Flows & Rate Expectations",
    "Relates <strong>transaction costs</strong>, <strong>ETF net flows</strong> and "
    "<strong>policy direction</strong> to Ethereum’s on-chain activity. "
    "Ethereum recently recorded <strong>highest levels of on-chain activity since 2021</strong>, "
    "marking one of the busiest months in its history (see references at the end). "
    "This section investigates the <em>drivers</em> behind that surge — namely whether lower fees, stronger ETF inflows, "
    "and shifting interest-rate expectations can explain the rise, and how these factors may spill over to ETH price."
)


# KPIs
c1, c2, c3, c4 = st.columns(4)
with c1: kpi_card("Activity Index (latest)", f"{k1:,.2f}" if pd.notna(k1) else "—")
with c2: kpi_card("Avg Tx Fee (USD)", f"${k2:,.2f}" if pd.notna(k2) else "—")
with c3: kpi_card("ETF Net Flow (M)", _fmt_money_m(k3))
with c4:
    if pd.notna(k4_dir):
        prob_txt = f"{k4_p*100:,.0f}%" if pd.notna(k4_p) else "—"
        kpi_card("Rates Direction", f"{k4_dir} ({prob_txt})")
    else:
        kpi_card("Rates Direction", "—")

# --- Charts
alt.data_transformers.disable_max_rows()


# 3A) Time series — Activity vs Fees & ETF flows
st.markdown("")
st.markdown("")
st.markdown("**Chart A: Activity vs Fees & ETF flows**")

ts_cols = [c for c in ["MONTH","MONTH_DT","ACTIVITY_INDEX","AVG_TX_FEE_USD","ETF_NET_FLOW_USD_MILLIONS"] if c in panel.columns]
ts = panel[ts_cols].dropna(subset=["MONTH_DT"]).copy()

left = alt.Chart(ts).mark_line(point=False, color="#0ea5e9").encode(
    x=alt.X("MONTH_DT:T", title="Month"),
    y=alt.Y("ACTIVITY_INDEX:Q", title="Activity Index", axis=alt.Axis(grid=True)),
    tooltip=[
        alt.Tooltip("MONTH:N", title="Month"),
        alt.Tooltip("ACTIVITY_INDEX:Q", title="Activity", format=",.2f")
    ],
)

fee_line = alt.Chart(ts).mark_line(strokeDash=[4,3], color="#f59e0b").encode(
    x=alt.X("MONTH_DT:T", title="Month"),
    y=alt.Y("AVG_TX_FEE_USD:Q", title="Avg Tx Fee (USD)"),
    tooltip=[alt.Tooltip("AVG_TX_FEE_USD:Q", title="Fee (USD)", format=",.2f")],
)

etf_bar = alt.Chart(ts).mark_bar(opacity=0.35, color="#10b981").encode(
    x=alt.X("MONTH_DT:T", title="Month"),
    y=alt.Y("ETF_NET_FLOW_USD_MILLIONS:Q", title="ETF Net Flow (USD M)"),
    tooltip=[alt.Tooltip("ETF_NET_FLOW_USD_MILLIONS:Q", title="ETF Flow (M)", format=",.0f")],
)

chart_ts = alt.layer(left, fee_line, etf_bar).resolve_scale(y="independent").properties(height=360)
st.altair_chart(chart_ts, use_container_width=True)

# --- Insight line
insights = []
if set(["ACTIVITY_INDEX","AVG_TX_FEE_USD"]).issubset(panel.columns):
    r = panel[["ACTIVITY_INDEX","AVG_TX_FEE_USD"]].corr().iloc[0,1]
    if pd.notna(r): insights.append(f"Activity vs Fees corr: {r:+.2f} (usually negative).")
if set(["ACTIVITY_INDEX","ETF_NET_FLOW_USD_MILLIONS"]).issubset(panel.columns):
    r = panel[["ACTIVITY_INDEX","ETF_NET_FLOW_USD_MILLIONS"]].corr().iloc[0,1]
    if pd.notna(r): insights.append(f"Activity vs ETF Flows corr: {r:+.2f}.")
if set(["ACTIVITY_INDEX","AVG_ETH_PRICE_USD"]).issubset(panel.columns):
    r = panel[["ACTIVITY_INDEX","AVG_ETH_PRICE_USD"]].corr().iloc[0,1]
    if pd.notna(r): insights.append(f"Price vs Activity corr: {r:+.2f}.")

insight("Lower fees and positive ETF net flows tend to coincide with stronger activity. Policy leaning (cut vs. hold) is a secondary tailwind when aligned with cheap execution.")



# -----------------------------------------------------------
# 3B) User Adoption During Fee Evolution
# -----------------------------------------------------------
#draw_section(
#    "Fee Sensitivity — User Adoption During Fee Evolution",
#    "Overlay unique users (millions) with average fee (USD). Tests whether affordability expands the user base."
#)
st.markdown("")
st.markdown("")
st.markdown("**Chart B: User Adoption During Fee Evolution:** Overlay unique users (millions) with average fee (USD). Tests whether affordability expands the user base.")

if not df_fees.empty:
    # collapse to monthly totals (if multiple FEE_CATEGORY rows)
    agg = df_fees.groupby("MONTH", as_index=False).agg({
        "USERS_MILLIONS":"sum",
        "AVG_FEE_USD":"mean"
    }).sort_values("MONTH")

    # KPIs
    growth_users = 100 * (agg.iloc[-1]["USERS_MILLIONS"] - agg.iloc[0]["USERS_MILLIONS"]) / max(agg.iloc[0]["USERS_MILLIONS"], 1e-9)
    fee_change   = 100 * (agg.iloc[-1]["AVG_FEE_USD"] - agg.iloc[0]["AVG_FEE_USD"]) / max(agg.iloc[0]["AVG_FEE_USD"], 1e-9)

    c1, c2 = st.columns(2)
    kpi_inline(c1, f"<strong>User Growth:</strong> <span class='v'>{growth_users:,.1f}%</span>", style=KPI_STYLE["teal"])
    kpi_inline(c2, f"<strong>Fee Change:</strong> <span class='v'>{fee_change:,.1f}%</span>", style=KPI_STYLE["blue"])

    fig8 = make_subplots(specs=[[{"secondary_y": True}]])
    fig8.add_trace(go.Scatter(x=agg["MONTH"], y=agg["USERS_MILLIONS"],
                              name="Unique Users (M)", mode="lines+markers",
                              line=dict(color="#7c3aed", width=3)))
    fig8.add_trace(go.Scatter(x=agg["MONTH"], y=agg["AVG_FEE_USD"],
                              name="Average Fee (USD)", mode="lines+markers",
                              line=dict(color="#f59e0b", width=2, dash="dash")),
                   secondary_y=True)
    fig8.update_yaxes(title_text="Users (Millions)", secondary_y=False)
    fig8.update_yaxes(title_text="Avg Fee (USD)", secondary_y=True, showgrid=False)
    fig8.update_layout(height=420, margin=dict(l=10,r=10,t=10,b=10))
    st.plotly_chart(fig8, use_container_width=True)

insight("User growth accelerates when average fees compress. Spikes in fees are typically followed by softer user growth, consistent with a price-of-blockspace constraint on mainstream adoption.")

# -----------------------------------------------------------
# ---- 3C) Drivers vs Activity — interactive scatter + regression ----
# -----------------------------------------------------------

#draw_section(
#    "3C) What Maps to Activity? — Driver vs Activity",
#    "Choose a driver to compare against the Activity Index; the fitted line is OLS. The ‘Recent trend’ note reflects the last three observations."
#)
st.markdown("")
st.markdown("")
st.markdown("**Chart C: What Maps to Activity? — Driver vs Activity**: Choose a driver to compare against the Activity Index; the fitted line is OLS. The ‘Recent trend’ note reflects the last three observations.")


# Human labels → (panel column, x-axis title, tooltip title)
driver_options = {
    "Avg Tx Fee (USD)": ("AVG_TX_FEE_USD", "Avg Tx Fee (USD)", "Fee (USD)"),
    "ETF Net Flow (USD M)": ("ETF_NET_FLOW_USD_MILLIONS", "ETF Net Flow (USD M)", "ETF Flow (M)"),
    "Rates — Cut Probability (%)": ("RATES_PROB", "Cut Probability (%)", "Cut Prob (%)"),
    "ETH Price (USD)": ("AVG_ETH_PRICE_USD", "ETH Price (USD)", "ETH Price (USD)"),
}

choice = st.selectbox("Driver", list(driver_options.keys()), index=0)
col_x, x_title, tip_title = driver_options[choice]

# Prepare data safely
need_cols = ["MONTH", "MONTH_DT", "ACTIVITY_INDEX", col_x]
if not set(need_cols).issubset(panel.columns):
    missing = [c for c in need_cols if c not in panel.columns]
    st.warning(f"Missing columns for this view: {', '.join(missing)}")
else:
    df_drv = panel[need_cols].copy()

    # Coerce numeric just in case
    df_drv[col_x] = pd.to_numeric(df_drv[col_x], errors="coerce")
    df_drv["ACTIVITY_INDEX"] = pd.to_numeric(df_drv["ACTIVITY_INDEX"], errors="coerce")
    df_drv = df_drv.dropna(subset=[col_x, "ACTIVITY_INDEX", "MONTH_DT"])

    if df_drv.empty:
        st.info("No overlapping data points to plot.")
    else:
        scatter = alt.Chart(df_drv).mark_circle(size=70, opacity=0.7, color="#0ea5e9").encode(
            x=alt.X(f"{col_x}:Q", title=x_title),
            y=alt.Y("ACTIVITY_INDEX:Q", title="Activity Index"),
            tooltip=[
                alt.Tooltip("MONTH:N", title="Month"),
                alt.Tooltip(f"{col_x}:Q", title=tip_title, format=",.2f"),
                alt.Tooltip("ACTIVITY_INDEX:Q", title="Activity", format=",.2f"),
            ],
        )

        reg = scatter.transform_regression(col_x, "ACTIVITY_INDEX").mark_line(color="#111827")

        st.altair_chart((scatter + reg).properties(height=340), use_container_width=True)

        # Recent 3-observation direction cue
        tail = df_drv.sort_values("MONTH_DT").tail(3)
        if len(tail) >= 2:
            dx = tail[col_x].iloc[-1] - tail[col_x].iloc[0]
            dy = tail["ACTIVITY_INDEX"].iloc[-1] - tail["ACTIVITY_INDEX"].iloc[0]
            trend_x = "↑" if dx > 0 else ("↓" if dx < 0 else "→")
            trend_y = "↑" if dy > 0 else ("↓" if dy < 0 else "→")
            st.caption(f"Recent trend (last 3 obs): {x_title} {trend_x}, Activity {trend_y}.")


insight("The slope quantifies sensitivity. Negative slope for fees (cheaper → more activity) and positive slope for ETF net flows are consistent with Section 3.")



# -----------------------------------------------------------
# 4) ETH Price Overlay with Activity Index
# -----------------------------------------------------------
draw_section(
    "4) Price Linkage — ETH Price vs Activity Index",
    "Compares average ETH price (USD) to a composite activity index. Co-movement suggests fundamental participation; divergences can flag speculative or efficiency phases."
)


if not df_eth.empty:
    price_min, price_max = df_eth["AVG_ETH_PRICE_USD"].min(), df_eth["AVG_ETH_PRICE_USD"].max()
    corr = np.corrcoef(
        df_eth["AVG_ETH_PRICE_USD"].astype(float),
        df_eth["ACTIVITY_INDEX"].astype(float)
    )[0,1] if len(df_eth)>1 else np.nan

    c1, c2 = st.columns(2)
    kpi_inline(c1, f"<strong>Price Range:</strong> <span class='v'>${price_min:,.0f} – ${price_max:,.0f}</span>", style=KPI_STYLE["blue"])
    kpi_inline(c2, f"<strong>Correlation (Price vs. Activity):</strong> <span class='v'>{corr:,.2f}</span>", style=KPI_STYLE["teal"])

    fig7 = make_subplots(specs=[[{"secondary_y": True}]])
    fig7.add_trace(go.Scatter(x=df_eth["MONTH"], y=df_eth["AVG_ETH_PRICE_USD"],
                              name="ETH Price (USD)", mode="lines+markers",
                              line=dict(color="#1d4ed8", width=2)))
    fig7.add_trace(go.Scatter(x=df_eth["MONTH"], y=df_eth["ACTIVITY_INDEX"],
                              name="Activity Index", mode="lines+markers",
                              line=dict(color="#14b8a6", width=3, dash="dot")),
                   secondary_y=True)
    fig7.update_yaxes(title_text="ETH Price (USD)", secondary_y=False)
    fig7.update_yaxes(title_text="Activity Index", secondary_y=True, showgrid=False)
    fig7.update_layout(height=420, margin=dict(l=10,r=10,t=10,b=10))
    st.plotly_chart(fig7, use_container_width=True)

insight("Price and activity generally co-move. Short stretches of divergence often resolve as fees normalize or as ETF flow direction stabilizes.")


# ================================
# 5) Macro-Chain Impulse (MCIS)
# ================================

draw_section(
    "5) Macro-Chain Impulse (MCIS) — composite driver of on-chain activity & price",
    "MCIS z-scores and stacks three standardized drivers with small lags: +ETF net flows, +rate-cut probability, and −fees (made positive). Weights are ridge-estimated with a 5% per-factor floor and renormalization."
)

need = {
    "MONTH", "ACTIVITY_INDEX", "AVG_TX_FEE_USD",
    "ETF_NET_FLOW_USD_MILLIONS", "RATES_PROB", "AVG_ETH_PRICE_USD"
}
if not need.issubset(panel.columns):
    st.warning("MCIS: missing columns: " + ", ".join(sorted(need - set(panel.columns))))
else:
    # --- base frame, make a proper monthly index and trim any partial last month
    df = panel.copy()
    if "MONTH_DT" in df.columns and pd.api.types.is_datetime64_any_dtype(df["MONTH_DT"]):
        df = df.sort_values("MONTH_DT").set_index("MONTH_DT")
    else:
        mdt = pd.to_datetime(df["MONTH"], errors="coerce", utc=False)
        df = df.assign(MONTH_DT=mdt).sort_values("MONTH_DT").set_index("MONTH_DT")

    # drop the very last row if it looks like a partial future/ongoing month
    #if len(df) >= 2:
    #    last, prev = df.index[-1], df.index[-2]
    #    if last.to_period("M") == prev.to_period("M") + 1 and last.day <= 15:
    #        df = df.iloc[:-1]

    # --- numeric coercion
    y = pd.to_numeric(df["ACTIVITY_INDEX"], errors="coerce")
    price = pd.to_numeric(df["AVG_ETH_PRICE_USD"], errors="coerce")
    Xraw = pd.DataFrame({
        "etf":  pd.to_numeric(df["ETF_NET_FLOW_USD_MILLIONS"], errors="coerce"),
        "rate": pd.to_numeric(df["RATES_PROB"], errors="coerce"),   # probability of cuts (0-1 or 0-100)
        "fee":  pd.to_numeric(df["AVG_TX_FEE_USD"], errors="coerce"),
    }, index=df.index)

    # normalize rate probability to 0..1 if it comes as percent
    if Xraw["rate"].dropna().max() > 1.00001:
        Xraw["rate"] = Xraw["rate"] / 100.0

    # --- choose lags (0..2) that maximize |corr| with activity
    lags = {}
    for col, sign in [("etf", +1), ("rate", +1), ("fee", -1)]:
        best_lag, best_score = 0, -np.inf
        for L in (0, 1, 2):
            corr = pd.concat([y, Xraw[col].shift(L)], axis=1).corr().iloc[0, 1]
            if pd.notna(corr):
                score = abs(corr * sign)
                if score > best_score:
                    best_score, best_lag = score, L
        lags[col] = best_lag

    # --- lag and flip fees so "higher is better" for all features
    Xlag = pd.DataFrame({c: Xraw[c].shift(lags[c]) for c in Xraw.columns}, index=df.index)
    Xlag["fee"] = -Xlag["fee"]

    # --- standardize (z-scores) and align
    Z = (Xlag - Xlag.mean()) / Xlag.std(ddof=0)
    data = pd.concat([Z, y.rename("y")], axis=1).dropna()

    if len(data) < 3:
        st.info("Too few overlapping months (<3) to compute MCIS.")
    else:
        Z = data[["etf", "rate", "fee"]]
        y_aligned = data["y"]

        # --- ridge weights (λ=1) with non-negativity clamp + renormalize
        XtX = Z.T @ Z
        lam = 1.0
        w = np.linalg.solve(XtX + lam * np.eye(3), Z.T @ y_aligned)

        # Turn into a non-negative Series
        weights = pd.Series(w, index=["etf", "rate", "fee"]).clip(lower=0)
        
        # If everything is ~0, fall back to equal weights
        if weights.sum() <= 1e-12 or (weights <= 1e-12).all():
            weights = pd.Series([1/3, 1/3, 1/3], index=["etf", "rate", "fee"])
        else:
            weights = weights / weights.sum()
        
        # --- Apply a per-factor floor and renormalize
        MIN_W = 0.05  # 5% floor per factor
        n = len(weights)
        if MIN_W * n < 1.0:
            # Scale the original weights into the remaining (1 - n*MIN_W) mass, then add the floor
            weights = (1 - MIN_W * n) * weights + MIN_W
            # (Numerically) re-normalize to be safe
            weights = weights / weights.sum()
        # else: if the floor would exceed 100% in total (not our case), keep the normalized weights as-is


        MCIS = (Z @ weights).rename("MCIS")
        MCISz = (MCIS - MCIS.mean()) / MCIS.std(ddof=0)

        # --- diagnostics
        dy_next = y_aligned.shift(-1) - y_aligned
        p_next = price.reindex(MCISz.index)
        ret_next = p_next.pct_change().shift(-1)

        hit_rate = float((dy_next[MCISz > 0] > 0).mean()) if (MCISz > 0).any() else np.nan
        corr_price = float(MCISz.corr(ret_next))
        current = MCISz.dropna().iloc[-1]
        regime = "Tailwind" if current > 0.5 else ("Headwind" if current < -0.5 else "Neutral")

        # ---------- KPI CARDS ----------
        pill_color = {"Tailwind": "#10B981", "Headwind": "#EF4444", "Neutral": "#64748B"}.get(regime, "#64748B")
        metrics = [
            {
                "label": "MCIS (z-score, latest)",
                "value": f"{current:,.2f}",
                "pill": regime,
                "pill_color": pill_color,
            },
            {
                "label": "P(Activity ↑ next month | MCIS>0)",
                "value": f"{hit_rate*100:,.0f}%" if pd.notna(hit_rate) else "—",
            },
            {
                "label": "Corr(MCIS, next-month ETH return)",
                "value": f"{corr_price:,.2f}" if pd.notna(corr_price) else "—",
            },
            {
                "label": "Weights (etf / rate / fee)",
                "value": f"<span style='font-size:0.9em; color:#374151;'>"
                         + " + ".join([f"{k} {v*100:,.0f}%" for k, v in weights.items()])
                         + "</span>",
                "delta": None,
                "unsafe_allow_html": True,  # tell your renderer it's HTML
            },

        ]
        draw_metrics_row(metrics, cols=4)

        if len(data) < 6:
            st.caption("⚠️ Very few months of history, results fragile!")

        # --- Chart A: MCIS vs Activity (both z-scored)
        st.markdown("")
        st.markdown("**Chart A. MCIS vs Activity (z-scored)**")
        line_df = pd.DataFrame({
            "MONTH": MCISz.index,
            "MCIS (z)": MCISz.values,
            "Activity (z)": ((y_aligned - y_aligned.mean()) / y_aligned.std(ddof=0)).reindex(MCISz.index).values
        }).dropna()
        long_line = line_df.melt(id_vars="MONTH", var_name="Series", value_name="Value")
        ch_line = (
            alt.Chart(long_line)
            .mark_line(strokeWidth=2)
            .encode(
                x=alt.X("MONTH:T", title="Month"),
                y=alt.Y("Value:Q", title="z-score"),
                color=alt.Color("Series:N", scale=alt.Scale(scheme="tableau20"))
            )
            .properties(height=320)
        )
        st.altair_chart(ch_line, use_container_width=True)
        
        
        # --- Prepare scatter data (MCIS vs ΔActivity)
        sc_df = pd.DataFrame({
            "MONTH": MCISz.index,
            "MCIS": MCISz.values,
            "DeltaActivityNext": dy_next.reindex(MCISz.index).values
        }).dropna()

        st.markdown(
            "- **Interpretation.** MCIS > 0 signals a supportive backdrop (ETF demand + policy ease − fees). "
            "In sample, positive MCIS months are more likely to be followed by rising activity; the magnitude is summarized in the hit-rate KPI. "
            "Weights indicate which driver is doing the heavy lifting currently."
        )

        
        
        # --- Chart C: Regimes on ETH price
        if len(MCISz) >= 3:
            st.markdown("")
            st.markdown("**Chart B. ETH Price with MCIS Regimes**")
            st.caption("Shaded regions mark MCIS regimes: green (≥ +1σ tailwind) and red (≤ −1σ headwind). Useful to contextualize price runs with fundamentals vs. macro support.")
            
            reg_df = pd.DataFrame({
                "MONTH": MCISz.index,
                "ETH_USD": p_next.values,
                "MCIS": MCISz.values
            }).dropna()
            base = alt.Chart(reg_df).encode(x=alt.X("MONTH:T", title="Month"))
            price_line = base.mark_line(strokeWidth=2, color="#111827").encode(
                y=alt.Y("ETH_USD:Q", title="ETH price (USD)")
            )
            hi = base.transform_filter(alt.datum.MCIS >= 1.0).mark_rect(opacity=0.12, color="#16a34a").encode()
            lo = base.transform_filter(alt.datum.MCIS <= -1.0).mark_rect(opacity=0.12, color="#ef4444").encode()
            st.altair_chart((hi + lo + price_line).properties(height=300), use_container_width=True)


        # --- Insight
        hit_txt = f"{hit_rate*100:,.0f}%" if pd.notna(hit_rate) else "—"
        st.markdown(
            "- **Interpretation.** MCIS > 0 indicates a supportive backdrop (ETF demand + rate-cut odds – fees). "
            "In this sample, months with positive MCIS saw activity rise the following month about "
            f"**{hit_txt}** of the time. Green shading on the ETH price marks **MCIS ≥ +1σ** (tailwind), "
            "red marks **≤ −1σ** (headwind)."
        )


# ================================
# References & Data Sources
# ================================
st.markdown("### References & Data Sources")

st.markdown(
    """
- **Ethereum activity surges**  
  [Crypto.com Research Roundup — Sep 2025](https://crypto.com/us/research/research-roundup-sep-2025)  
  [CryptoRank — Why Ethereum just posted its third biggest month in history](https://cryptorank.io/news/feed/d31b4-why-ethereum-just-posted-its-third-biggest-month-in-history)

- **Interest rates / monetary policy**  
  [FRED — Federal Funds Rate](https://fred.stlouisfed.org/series/FEDFUNDS)  
  [CME FedWatch Tool](https://www.cmegroup.com/markets/interest-rates/cme-fedwatch-tool.html?utm_source=chatgpt.com)

- **ETF flows**  
  [Farside Investors — Ethereum ETF Flows](https://farside.co.uk/eth/?utm_source=chatgpt.com)

- **On-chain data provider**  
  [FlipsideCrypto](https://flipsidecrypto.xyz)
    """
)



# -----------------------------------------------------------
# Footer
# -----------------------------------------------------------
st.markdown('<div class="sep"></div>', unsafe_allow_html=True)
st.caption("Built by Adrià Parcerisas • Data via Flipside exports • Code quality and metric selection optimized for panel discussion.")













