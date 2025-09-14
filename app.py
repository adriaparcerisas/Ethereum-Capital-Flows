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
      This dashboard analyzes Ethereum’s on-chain capital flows and user dynamics across DeFi, bridges, and fees.
      Metrics are sourced from canonical exports and designed for a crypto-savvy audience.<br><br>
      <strong>August set a new all-time high for on-chain volume (~$341B)</strong>, eclipsing the 2021 peak.
      Tailwinds included corporate treasury accumulation, stronger spot ETH ETF trading, and lower average fees
      that enabled higher throughput. Protocol buybacks (≈$46M late August; Hyperliquid ≈$25M) supported prices
      in volatility, though long-run impact depends on fundamentals and recurring revenue.<br><br>
      The sections below track capital allocation, breadth vs. intensity of usage, execution costs, and cross-chain flows.
      Pay particular attention to fee-sensitive adoption and to segments where capital concentration rises (DEXs, lending, bridges).
      Results are intended for panel discussion: what’s driving throughput, which users are sticky, how costs affect adoption,
      and where liquidity is migrating across chains and venues.
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

    insight("DeFi lending and DEX trading typically drive most on-chain flow; the mix contextualizes risk-on vs defensive phases.")

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

        insight("Both active addresses and transactions have shown strong growth over time. "
                "Among the sectors, 'Others' — mainly token transfers (now including NFT transfers) — "
                "emerges as one of the fastest-growing categories, underscoring its central role in on-chain activity.")

# -----------------------------------------------------------
# 3) User Activity & Sector Breadth (Merged)
# -----------------------------------------------------------
draw_section(
    "3. User Activity & Sector Breadth",
    "Compare user types by activity (Casual vs Power) and sector breadth (Single-sector vs Multi-sector). Use 100% view to compare shares; enable log scale when absolute counts diverge."
)

if not df_typology.empty:
    # Build a composite label to plot both dimensions together
    df_typology["LABEL"] = df_typology["USER_TYPE"].fillna("") + " — " + df_typology["ACTIVITY_LEVEL"].fillna("")
    df_typology["LABEL"] = df_typology["LABEL"].str.replace("  —  "," — ").str.strip(" —")

    view = st.radio("View", ["Absolute", "100% share"], index=0, horizontal=True, key="typ_view")
    logy = st.checkbox("Log scale (y)", value=True)

    # KPI latest shares among LABELS
    latest = df_typology["MONTH"].max()
    d_last = df_typology[df_typology["MONTH"]==latest]
    totals = d_last.groupby("LABEL")["UNIQUE_USERS"].sum().sort_values(ascending=False)
    top_label = totals.index[0] if len(totals)>0 else "—"
    top_share = 100 * totals.iloc[0] / totals.sum() if totals.sum()>0 else np.nan
    c1, c2 = st.columns(2)
    kpi_inline(c1, f"<strong>Top segment (latest):</strong> <span class='v'>{top_label}</span>", style=KPI_STYLE["violet"])
    kpi_inline(c2, f"<strong>Share (latest):</strong> <span class='v'>{top_share:,.1f}%</span>", style=KPI_STYLE["violet"])

    fig3 = go.Figure()
    for lab in sorted(df_typology["LABEL"].unique()):
        d = df_typology[df_typology["LABEL"]==lab].sort_values("MONTH")
        y = d["UNIQUE_USERS"].astype(float)
        if view=="100% share":
            # percent each month
            month_sum = df_typology.groupby("MONTH")["UNIQUE_USERS"].transform("sum")
            y = 100 * d["UNIQUE_USERS"].values / month_sum[d.index].values
        fig3.add_trace(go.Scatter(
            x=d["MONTH"], y=y, name=lab, mode="lines+markers"
        ))
    fig3.update_layout(
        height=420, margin=dict(l=10,r=10,t=10,b=10),
        yaxis_title="Users" if view=="Absolute" else "Share (%)"
    )
    if logy and view=="Absolute":
        fig3.update_yaxes(type="log")
    st.plotly_chart(fig3, use_container_width=True)

    insight("Single-sector casual users are the largest cohort, but multi-sector and power users contribute outsized engagement. Shares make cohort shifts clearer.")

# -----------------------------------------------------------
# 4) DEX Volume & Active Swappers (Monthly)
# -----------------------------------------------------------
draw_section(
    "4. DEX Volume & Active Swappers (Monthly)",
    "Bars show DEX volume (USD billions); line shows active swappers."
)

if not df_dex.empty:
    peak_vol = df_dex["TOTAL_VOLUME_BILLIONS"].max()
    growth = 100 * (df_dex.iloc[-1]["TOTAL_VOLUME_BILLIONS"] - df_dex.iloc[0]["TOTAL_VOLUME_BILLIONS"]) / max(df_dex.iloc[0]["TOTAL_VOLUME_BILLIONS"], 1e-9)

    c1, c2 = st.columns(2)
    kpi_inline(c1, f"<strong>Peak DEX Volume:</strong> <span class='v'>${peak_vol:,.2f}B</span>", style=KPI_STYLE["blue"])
    kpi_inline(c2, f"<strong>Volume Growth (since start):</strong> <span class='v'>{growth:,.1f}%</span>", style=KPI_STYLE["teal"])

    fig4 = make_subplots(specs=[[{"secondary_y": True}]])
    fig4.add_bar(
        x=df_dex["MONTH"], y=df_dex["TOTAL_VOLUME_BILLIONS"], name="DEX Volume (B)",
        marker_color="#1d4ed8"
    )
    fig4.add_trace(
        go.Scatter(x=df_dex["MONTH"], y=df_dex["ACTIVE_SWAPPERS"],
                   name="Active Swappers", mode="lines+markers",
                   line=dict(color="#14b8a6", width=3)),
        secondary_y=True
    )
    fig4.update_yaxes(title_text="Volume (B)", secondary_y=False)
    fig4.update_yaxes(title_text="Active Swappers", secondary_y=True, showgrid=False)
    fig4.update_layout(height=430, margin=dict(l=10,r=10,t=10,b=10), barmode="overlay")
    st.plotly_chart(fig4, use_container_width=True)

# -----------------------------------------------------------
# 5) Lending Deposits — Evolution by Platform
# -----------------------------------------------------------
draw_section(
    "5. Lending Deposits — Evolution by Platform",
    "Stacked area by platform shows concentration and migration of collateral."
)

if not df_lend.empty:
    # KPIs
    latest = df_lend["MONTH"].max()
    total_latest = df_lend[df_lend["MONTH"]==latest]["VOLUME_BILLIONS"].sum()
    leading = df_lend[df_lend["MONTH"]==latest].groupby("PLATFORM")["VOLUME_BILLIONS"].sum().sort_values(ascending=False)
    top_platform = leading.index[0] if len(leading)>0 else "—"
    c1, c2 = st.columns(2)
    kpi_inline(c1, f"<strong>Total Deposits (latest):</strong> <span class='v'>${total_latest:,.2f}B</span>", style=KPI_STYLE["green"])
    kpi_inline(c2, f"<strong>Top Platform (latest):</strong> <span class='v'>{top_platform}</span>", style=KPI_STYLE["green"])

    fig5 = go.Figure()
    for plat in sorted(df_lend["PLATFORM"].unique()):
        d = df_lend[df_lend["PLATFORM"]==plat].sort_values("MONTH")
        fig5.add_trace(go.Scatter(
            x=d["MONTH"], y=d["VOLUME_BILLIONS"], name=plat, mode="lines",
            stackgroup="one"
        ))
    fig5.update_layout(height=420, margin=dict(l=10,r=10,t=10,b=10),
                       yaxis_title="Deposit Volume (B)")
    st.plotly_chart(fig5, use_container_width=True)

    insight("Platform concentration can hint at systemic risk or liquidity incentives. Monitoring shifts helps identify where collateral is migrating.")

# -----------------------------------------------------------
# 6) Cross-Chain Connectivity — Bridge Flows (Monthly)
# -----------------------------------------------------------
draw_section(
    "6. Cross-Chain Connectivity — Bridge Flows (Monthly)",
    "Inflow and outflow (USD billions) with net flow overlay to reveal directionality of cross-chain liquidity."
)

if not df_bridge.empty:
    # Ensure numeric types (prevents “netflow = 0” due to strings)
    num_cols = ["INFLOW_BILLIONS","OUTFLOW_BILLIONS","NET_FLOW_BILLIONS","TOTAL_BRIDGE_VOLUME_BILLIONS"]
    for c in num_cols:
        if c in df_bridge.columns:
            df_bridge[c] = pd.to_numeric(df_bridge[c], errors="coerce")

    dfb = df_bridge.sort_values("MONTH").copy()

    # KPIs
    peak_total = dfb["TOTAL_BRIDGE_VOLUME_BILLIONS"].max() if "TOTAL_BRIDGE_VOLUME_BILLIONS" in dfb else np.nan
    net_latest = dfb["NET_FLOW_BILLIONS"].iloc[-1] if "NET_FLOW_BILLIONS" in dfb and len(dfb)>0 else np.nan

    c1, c2 = st.columns(2)
    kpi_inline(c1, f"<strong>Peak Total Bridge Volume:</strong> <span class='v'>${peak_total:,.2f}B</span>", style=KPI_STYLE["green"])
    kpi_inline(c2, f"<strong>Net Flow (latest):</strong> <span class='v'>{net_latest:,.2f}B</span>", style=KPI_STYLE["blue"])

    # Chart: Inflow/Outflow bars + Net Flow line (all in billions)
    fig6 = go.Figure()

    # Bars
    if "INFLOW_BILLIONS" in dfb:
        fig6.add_bar(
            x=dfb["MONTH"], y=dfb["INFLOW_BILLIONS"], name="Inflow (B)", marker_color="#10b981"  # green
        )
    if "OUTFLOW_BILLIONS" in dfb:
        fig6.add_bar(
            x=dfb["MONTH"], y=dfb["OUTFLOW_BILLIONS"], name="Outflow (B)", marker_color="#f59e0b"  # amber
        )

    # Net flow line (can be negative)
    if "NET_FLOW_BILLIONS" in dfb:
        fig6.add_trace(
            go.Scatter(
                x=dfb["MONTH"], y=dfb["NET_FLOW_BILLIONS"],
                name="Net Flow (B)", mode="lines+markers",
                line=dict(color="#1d4ed8", width=3)  # blue
            )
        )

    # Zero reference line for net flow
    fig6.add_hline(y=0, line_width=1, line_dash="dot", line_color="#94a3b8")

    fig6.update_layout(
        height=430, margin=dict(l=10, r=10, t=10, b=10),
        barmode="group",
        yaxis_title="Billions (USD)"
    )
    st.plotly_chart(fig6, use_container_width=True)

    insight("Inflow vs outflow shows where liquidity is heading; the net flow overlay highlights regime shifts (net import vs export) beyond total volume levels.")
else:
    st.info("`data/bridged_volume.csv` missing required columns.")

# -----------------------------------------------------------
# 7) ETH Price Overlay with Activity Index
# -----------------------------------------------------------
draw_section(
    "7. ETH Price Overlay with Total Activity Index",
    "Compare average ETH price (USD) with a composite activity index."
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

# -----------------------------------------------------------
# 8) User Adoption During Fee Evolution
# -----------------------------------------------------------
draw_section(
    "8. User Adoption During Fee Evolution",
    "Overlay unique users (millions) with average fee (USD) to visualize fee-sensitive adoption."
)

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

# =========================
# SECTION 8 — Activity Drivers: Fees, ETF Flows & Rates Direction
# =========================
import os
import re
import numpy as np
import pandas as pd
import altair as alt
import streamlit as st

# --- small helpers (idempotent) ---------------------------------------------
if "kpi_card" not in globals():
    def kpi_card(title: str, value: str, subtext: str | None = None, accent: str = "#2563eb"):
        st.markdown(
            f"""
<div style="
  position:relative;background:#F7FAFC;border:1px solid #E5E7EB;border-radius:12px;
  padding:14px 16px;margin-bottom:10px;">
  <div style="position:absolute;left:0;top:0;bottom:0;width:6px;background:{accent};
    border-radius:12px 0 0 12px;"></div>
  <div style="font-size:14px;color:#475467;margin-bottom:6px;"><strong>{title}</strong></div>
  <div style="font-size:28px;font-weight:800;color:#111827;line-height:1">{value}</div>
  {f'<div style="font-size:12px;color:#6B7280;margin-top:6px;">{subtext}</div>' if subtext else ''}
</div>
""",
            unsafe_allow_html=True,
        )

def _first_existing(*paths: str) -> str | None:
    for p in paths:
        if p and os.path.exists(p):
            return p
    return None

def _coerce_num(x):
    if pd.isna(x):
        return np.nan
    s = str(x)
    # strip thousands, %, M/B suffix and any stray parentheses
    s = s.replace(",", "").replace("%", "")
    s = re.sub(r"[\(\)]", "", s)
    # allow k/M/B suffixes commonly used in sheets (not required, just helpful)
    m = re.match(r"^([-+]?\d*\.?\d+)\s*([kKmMbB]?)$", s.strip())
    if not m:
        try:
            return float(s)
        except Exception:
            return np.nan
    v = float(m.group(1))
    suf = m.group(2).lower()
    if suf == "k": v *= 1e3
    if suf == "m": v *= 1e6
    if suf == "b": v *= 1e9
    return v

def _to_month(s, dayfirst=False):
    dt = pd.to_datetime(s, errors="coerce", utc=True, dayfirst=dayfirst)
    return pd.to_datetime(dt.dt.strftime("%Y-%m-01"))

def _fmt_money_m(x):
    return "—M" if pd.isna(x) else f"{x/1e6:,.0f}M"

def _fmt_pct01(x):
    return "—" if pd.isna(x) else f"{x*100:.0f}%"

# --- locate files ------------------------------------------------------------
etf_path   = _first_existing("data/etf_flows.csv", "/mnt/data/etf_flows.csv")
rates_path = _first_existing("data/rates_expectations.csv", "/mnt/data/rates_expectations.csv")
hist_path  = _first_existing("data/fedfunds_history.csv", "/mnt/data/fedfunds_history.csv")

fees_path  = _first_existing(  # try a couple of likely names you already use
    "data/fees_activity.csv", "data/fees_price.csv", "/mnt/data/fees_activity.csv", "/mnt/data/fees_price.csv"
)

# --- read ETF net flows (monthly) -------------------------------------------
etf = pd.DataFrame()
if etf_path:
    raw = pd.read_csv(etf_path)
    # accept either DATE or MONTH
    date_col = next((c for c in raw.columns if c.upper() in ("DATE","MONTH")), None)
    if date_col:
        etf = raw.copy()
        etf["MONTH"] = _to_month(etf[date_col])
        # find a numeric flow column (prefer ETF_NET_FLOW_USD_MILLIONS if present)
        flow_col = next((c for c in etf.columns if c.upper() in (
            "ETF_NET_FLOW_USD_MILLIONS","NET_FLOW_USD_MILLIONS","NET_FLOW","ETF_NET_FLOW"
        )), None)
        if flow_col:
            etf["ETF_NET_FLOW"] = pd.to_numeric(etf[flow_col].map(_coerce_num), errors="coerce")
        else:
            etf["ETF_NET_FLOW"] = np.nan
        etf = etf[["MONTH","ETF_NET_FLOW"]].dropna(subset=["MONTH"]).drop_duplicates(subset=["MONTH"])

# --- read rates expectations (monthly most-probable bucket) ------------------
rates = pd.DataFrame()
if rates_path:
    rraw = pd.read_csv(rates_path)
    date_col = next((c for c in rraw.columns if c.upper() in ("DATE","MONTH")), None)
    if date_col:
        rates = rraw.copy()
        rates["MONTH"] = _to_month(rates[date_col])
        # probability columns may look like "PROB_0.00-0.25", values like "12%" or 0.12
        prob_cols = [c for c in rates.columns if str(c).upper().startswith("PROB_")]
        # clean any % and coerce to 0..1
        for c in prob_cols:
            rates[c] = pd.to_numeric(
                rates[c].astype(str).str.replace("%","",regex=False).str.replace(",","",regex=False),
                errors="coerce"
            )
            # detect if given in 0..100 and convert to 0..1
            mx = rates[c].max(skipna=True)
            if pd.notna(mx) and mx > 1.5:  # clearly in percent
                rates[c] = rates[c] / 100.0
        # pick bucket with max probability per row
        def _pick(row):
            if not prob_cols:
                return pd.Series({"RATES_DIR":"HOLD","RATES_PROB":np.nan})
            s = row[prob_cols]
            if s.isna().all():
                return pd.Series({"RATES_DIR":"HOLD","RATES_PROB":np.nan})
            winner = s.astype(float).idxmax()
            p = float(s.max())
            # infer direction from bucket midpoint vs prior month midpoint
            # bucket name like PROB_4.75-5.00 -> midpoint
            try:
                lo, hi = winner.split("_",1)[1].split("-")
                mid = (float(lo) + float(hi)) / 2.0
            except Exception:
                mid = np.nan
            return pd.Series({"RATES_BUCKET_MID":mid, "RATES_PROB":p})
        picked = rates.apply(_pick, axis=1)
        rates = pd.concat([rates[["MONTH"]], picked], axis=1)
        # direction vs previous bucket midpoint
        rates = rates.sort_values("MONTH").reset_index(drop=True)
        prev = rates["RATES_BUCKET_MID"].shift(1)
        diff = rates["RATES_BUCKET_MID"] - prev
        rates["RATES_DIR"] = np.where(diff > 0.01, "HIKE",
                               np.where(diff < -0.01, "CUT", "HOLD"))
        rates = rates[["MONTH","RATES_DIR","RATES_PROB"]]

# --- read fees/activity (monthly) --------------------------------------------
fees = pd.DataFrame()
if fees_path:
    fraw = pd.read_csv(fees_path)
    # accept typical columns
    date_col = next((c for c in fraw.columns if c.upper() in ("DATE","MONTH")), None)
    if date_col:
        fees = fraw.copy()
        # some sources use day-first; try both, keep whichever yields more non-na
        m1 = _to_month(fees[date_col], dayfirst=False)
        m2 = _to_month(fees[date_col], dayfirst=True)
        fees["MONTH"] = m1.where(m1.notna(), m2)
        # average tx fee column candidate
        fee_col = next((c for c in fees.columns if c.upper() in ("AVG_TX_FEE_USD","AVG_TX_FEE","FEE_USD")), None)
        if fee_col:
            fees["AVG_TX_FEE"] = pd.to_numeric(fees[fee_col].map(_coerce_num), errors="coerce")
        else:
            fees["AVG_TX_FEE"] = np.nan
        # optional normalized activity index  (if your file already has one, it will be picked;
        # otherwise we just reflect fees lightly)
        act_col = next((c for c in fees.columns if c.upper() in ("ACTIVITY_INDEX","ACTIVITY","INDEX")), None)
        if act_col:
            fees["ACTIVITY_IDX"] = pd.to_numeric(fees[act_col].map(_coerce_num), errors="coerce")
        else:
            # very light transform for visualization if no index available
            fees["ACTIVITY_IDX"] = (fees["AVG_TX_FEE"] / fees["AVG_TX_FEE"].rolling(6, min_periods=1).median()).clip(lower=0.8, upper=2.0)
        fees = fees[["MONTH","AVG_TX_FEE","ACTIVITY_IDX"]].dropna(subset=["MONTH"]).drop_duplicates(subset=["MONTH"])

# --- assemble a panel (outer join on MONTH) -----------------------------------
pieces = [d for d in [fees, etf, rates] if d is not None and not d.empty]
panel = None
for d in pieces:
    panel = d if panel is None else panel.merge(d, on="MONTH", how="outer")
if panel is not None:
    panel = panel.sort_values("MONTH").reset_index(drop=True)

# --- header (no subtitle arg) -------------------------------------------------
draw_section(
    "8. Activity Drivers — Fees, ETF Flows & Rates Direction",
    ("Relates <strong>transaction costs</strong>, <strong>ETF net flows</strong> and "
     "<strong>policy direction</strong> to Ethereum’s on-chain activity. "
     "Rates direction is inferred via the <strong>most probable bucket</strong> "
     "each month vs the month’s Fed Funds level.")
)

# --- KPIs ---------------------------------------------------------------------
k1 = k2 = k3 = k4_dir = k4_p = np.nan
if panel is not None and not panel.empty:
    latest_row = panel.dropna(subset=["MONTH"]).iloc[panel["MONTH"].idxmax()]
    k1     = latest_row["ACTIVITY_IDX"] if "ACTIVITY_IDX" in latest_row else np.nan
    k2     = latest_row["AVG_TX_FEE"] if "AVG_TX_FEE" in latest_row else np.nan
    k3     = latest_row["ETF_NET_FLOW"] if "ETF_NET_FLOW" in latest_row else np.nan
    k4_dir = latest_row["RATES_DIR"] if "RATES_DIR" in latest_row else np.nan
    k4_p   = latest_row["RATES_PROB"] if "RATES_PROB" in latest_row else np.nan

col1, col2, col3, col4 = st.columns(4)
with col1: kpi_card("Activity Index (latest)", f"{k1:,.2f}" if pd.notna(k1) else "—")
with col2: kpi_card("Avg Tx Fee (USD)", f"{k2:,.2f}" if pd.notna(k2) else "—")
with col3: kpi_card("ETF Net Flow", _fmt_money_m(k3))
with col4:
    if pd.notna(k4_p):
        kpi_card("Fed Direction (mode)", f"{str(k4_dir)} ({_fmt_pct01(float(k4_p))})")
    else:
        kpi_card("Fed Direction (mode)", "—")

# --- Chart (only if we have something to draw) --------------------------------
has_fees  = panel is not None and "AVG_TX_FEE"  in panel.columns and panel["AVG_TX_FEE"].notna().any()
has_act   = panel is not None and "ACTIVITY_IDX" in panel.columns and panel["ACTIVITY_IDX"].notna().any()
has_etf   = panel is not None and "ETF_NET_FLOW" in panel.columns and panel["ETF_NET_FLOW"].notna().any()

if not (panel is not None and (has_fees or has_act or has_etf)):
    st.markdown(
        '<div style="background:#EEF4FF;border:1px solid #D1D9FF;color:#243B53; '
        'padding:14px 16px;border-radius:10px;">'
        'No chartable data for this section yet. The KPIs above will populate as soon as the CSVs are readable.'
        '</div>',
        unsafe_allow_html=True
    )
else:
    plot_df = panel.copy()
    plot_df = plot_df.dropna(subset=["MONTH"])
    # clean any lingering strings in numerics
    for c in ["AVG_TX_FEE","ACTIVITY_IDX","ETF_NET_FLOW"]:
        if c in plot_df.columns:
            plot_df[c] = pd.to_numeric(plot_df[c].map(_coerce_num), errors="coerce")

    base = alt.Chart(plot_df).encode(x=alt.X("MONTH:T", title=None))

    layers = []

    if has_act:
        layers.append(
            base.mark_line(point=True).encode(
                y=alt.Y("ACTIVITY_IDX:Q", title="Activity Index"),
                color=alt.value("#1D4ED8"),
                tooltip=[alt.Tooltip("MONTH:T", title="Month"), alt.Tooltip("ACTIVITY_IDX:Q", title="Activity Index", format=".2f")]
            )
        )

    if has_fees:
        layers.append(
            base.mark_line(strokeDash=[4,3]).encode(
                y=alt.Y("AVG_TX_FEE:Q", axis=alt.Axis(title="Fees (USD) / ETF Net Flow (M)", orient="right")),
                color=alt.value("#60A5FA"),
                tooltip=[alt.Tooltip("MONTH:T", title="Month"), alt.Tooltip("AVG_TX_FEE:Q", title="Avg Tx Fee (USD)", format=".2f")]
            )
        )

    if has_etf:
        layers.append(
            base.mark_area(opacity=0.15).encode(
                y=alt.Y("ETF_NET_FLOW:Q", axis=alt.Axis(title=None, orient="right")),
                color=alt.value("#34D399"),
                tooltip=[alt.Tooltip("MONTH:T", title="Month"), alt.Tooltip("ETF_NET_FLOW:Q", title="ETF Net Flow", format=",.0f")]
            )
        )

    chart = alt.layer(*layers).resolve_scale(y='independent').properties(height=380)
    st.altair_chart(chart, use_container_width=True)

# --- Insight ------------------------------------------------------------------
st.markdown(
    '<div style="background:#F8FAFC;border:1px solid #E5E7EB;border-radius:12px;padding:14px 16px;margin-top:12px;">'
    '<strong>Insight.</strong> Fees have eased while ETF net flows and policy expectations provide additional context '
    'for demand impulses. Mode of rate expectations offers a simple directional signal (Hike/Cut/Hold).'
    '</div>',
    unsafe_allow_html=True
)
# =========================
# END SECTION 8
# =========================


# -----------------------------------------------------------
# Footer
# -----------------------------------------------------------
st.markdown('<div class="sep"></div>', unsafe_allow_html=True)
st.caption("Built by Adrià Parcerisas • Data via Flipside/Dune exports • Code quality and metric selection optimized for panel discussion.")
























