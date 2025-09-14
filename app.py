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

# ================================
# SECTION 8 — Why Activity Rose (Drivers) and Did It Feed Into Price?
# ================================
import os
import numpy as np
import pandas as pd
import altair as alt
import streamlit as st

# ---------- local helpers (namespaced with s8_) ----------
def s8_read_csv(path: str) -> pd.DataFrame:
    """Robust CSV reader: auto-detect delimiter, skip bad lines."""
    try:
        df = pd.read_csv(path, sep=None, engine="python", on_bad_lines="skip")
        if df.shape[1] == 1:
            df = pd.read_csv(path, sep=";", engine="python", on_bad_lines="skip")
        return df
    except Exception:
        return pd.DataFrame()

def s8_month_start(series_like) -> pd.Series:
    """Coerce to tz-naive first-of-month timestamps (handles strings/datetimes)."""
    s = pd.to_datetime(series_like, errors="coerce", dayfirst=True)
    # drop tz
    if hasattr(s, "dt"):
        try:
            s = s.dt.tz_convert(None)
        except Exception:
            try:
                s = s.dt.tz_localize(None)
            except Exception:
                pass
        return s.dt.to_period("M").dt.to_timestamp(how="start")
    return pd.to_datetime(pd.NaT)

def s8_num(x: pd.Series) -> pd.Series:
    """Coerce mixed strings '(1,234)' etc. to floats."""
    if pd.api.types.is_numeric_dtype(x):
        return x.astype(float)
    y = (
        x.astype(str)
         .str.replace(r"[,\s]", "", regex=True)
         .str.replace(r"^\((.*)\)$", r"-\1", regex=True)
         .str.replace(r"[^0-9.\-]", "", regex=True)
    )
    y = y.replace({"": np.nan})
    return pd.to_numeric(y, errors="coerce")

def s8_kpi(label: str, value: str, color: str = "#2c7be5"):
    st.markdown(
        f"""
        <div style="padding:0.55em 0.9em;border-radius:10px;background-color:#f7f9fc;
                    border-left:6px solid {color};display:inline-block;margin:4px 8px 8px 0;">
            <div style="font-size:0.9em;color:#667;">{label}</div>
            <div style="font-size:1.1em;font-weight:700;color:#111;">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def s8_fmt_millions(x):
    return f"{x:,.1f}M" if pd.notna(x) else "—"

# ---------- load data ----------
base = "data"
fees_df  = s8_read_csv(os.path.join(base, "fees_activity.csv"))
etf_df   = s8_read_csv(os.path.join(base, "etf_flows.csv"))
rates_df = s8_read_csv(os.path.join(base, "rates_expectations.csv"))
fed_df   = s8_read_csv(os.path.join(base, "fedfunds_history.csv"))
price_df = s8_read_csv(os.path.join(base, "eth_price.csv"))

# ---------- preprocess: fees -> monthly activity & frictions ----------
fees = pd.DataFrame()
if not fees_df.empty:
    fees = fees_df.copy()
    # MONTH
    if "MONTH" in fees.columns:
        fees["MONTH"] = s8_month_start(fees["MONTH"])
    else:
        cands = [c for c in fees.columns if c.upper() in ("DATE","DAY","DT")]
        if cands:
            fees["MONTH"] = s8_month_start(fees[cands[0]])
    # unify metric names
    ren = {}
    for c in fees.columns:
        cu = c.upper()
        if cu in ("AVG_FEE_USD","AVG_TX_FEE_USD"): ren[c] = "AVG_FEE"
        if cu in ("ACTIVITY_INDEX","ACTIVITY"):    ren[c] = "ACTIVITY_INDEX"
        if cu in ("USERS_MILLIONS","UNIQUE_USERS_MILLIONS"): ren[c] = "USERS_M"
        if cu in ("TRANSACTIONS_MILLIONS","TX_MILLIONS","TOTAL_TRANSACTIONS_MILLIONS"): ren[c] = "TX_M"
    if ren: fees = fees.rename(columns=ren)
    for c in ["AVG_FEE","ACTIVITY_INDEX","USERS_M","TX_M"]:
        if c in fees.columns: fees[c] = s8_num(fees[c])
    if "MONTH" in fees.columns:
        agg = {c: "mean" for c in ["AVG_FEE","ACTIVITY_INDEX","USERS_M","TX_M"] if c in fees.columns}
        if agg:
            fees = fees.groupby("MONTH", as_index=False).agg(agg)

# ---------- preprocess: ETF flows (prefer ETF_NET_FLOW_USD_MILLIONS) ----------
etf = pd.DataFrame()
if not etf_df.empty:
    e = etf_df.copy()
    if "MONTH" in e.columns:
        e["MONTH"] = s8_month_start(e["MONTH"])
    else:
        dcs = [c for c in e.columns if c.upper() in ("DATE","DAY")]
        if dcs: e["MONTH"] = s8_month_start(e[dcs[0]])
    flow_col = None
    for name in e.columns:
        u = name.upper()
        if "ETF_NET_FLOW_USD_MILLIONS" in u: flow_col = name; break
    if flow_col is None:
        for name in e.columns:
            u = name.upper()
            if "NET" in u and "FLOW" in u:
                flow_col = name; break
    if flow_col is not None and "MONTH" in e.columns:
        e["ETF_NET_FLOW_M"] = s8_num(e[flow_col])  # millions USD
        etf = e.groupby("MONTH", as_index=False)["ETF_NET_FLOW_M"].sum()

# ---------- preprocess: rates -> monthly mode (HIKE/HOLD/CUT) with prob ----------
rates = pd.DataFrame()
if not rates_df.empty:
    r = rates_df.copy()
    r = r.rename(columns={c: c.upper() for c in r.columns})

    # 1) DATE -> MONTH
    date_col = "DATE" if "DATE" in r.columns else next((c for c in r.columns if "DATE" in c or "DAY" in c), None)
    if date_col is None:
        # if there is no explicit date column, abort cleanly
        st.warning("rates_expectations.csv has no DATE column; skipping rates mode overlay.")
        r = pd.DataFrame()
    else:
        r["DATE"] = pd.to_datetime(r[date_col], errors="coerce", dayfirst=True)
        r["MONTH"] = s8_month_start(r["DATE"])

    if not r.empty:
        # 2) Find probability column robustly
        prob_col = None
        for c in r.columns:
            cu = c.upper()
            if "PROB" in cu:      # matches PROB, PROBABILITY, PROB_PCT, etc.
                prob_col = c
                break
        # if still none, try common alternates
        if prob_col is None:
            for alt in ("PROBABILITY", "PROBABILITY_PCT", "PROB_PCT", "PCT", "WEIGHT"):
                if alt in r.columns:
                    prob_col = alt
                    break

        # 3) Ensure rate bucket bounds exist
        # Expect LOWER_BPS / UPPER_BPS (or similar). If missing, try to infer or bail gracefully.
        lower_col = next((c for c in r.columns if c.upper() in ("LOWER_BPS","LOWER","LOWER_BOUND_BPS","LOWER_BOUND")), None)
        upper_col = next((c for c in r.columns if c.upper() in ("UPPER_BPS","UPPER","UPPER_BOUND_BPS","UPPER_BOUND")), None)

        # Coerce numerics
        if lower_col is not None: r["LOWER_BPS"] = s8_num(r[lower_col])
        if upper_col is not None: r["UPPER_BPS"] = s8_num(r[upper_col])

        # Probability → numeric [0,1]
        if prob_col is not None:
            prob_series = r[prob_col].astype(str).str.strip()
            # drop symbols like %, commas; handle parentheses
            prob_series = (prob_series
                .str.replace("%", "", regex=False)
                .str.replace(",", ".", regex=False)
                .str.replace(r"[^\d\.\-]", "", regex=True)
            )
            r["PROB"] = pd.to_numeric(prob_series, errors="coerce")
            # If looks like 0–100, scale to 0–1
            if r["PROB"].dropna().gt(1).any():
                r["PROB"] = r["PROB"] / 100.0
        else:
            # No probability column — set equal weights within month to avoid crashes
            r["PROB"] = np.nan

        # Midpoint (for mode decision)
        r["MIDPOINT"] = (r.get("LOWER_BPS", np.nan) + r.get("UPPER_BPS", np.nan)) / 2.0

        # Attach FedFunds by month (to compare midpoint vs current rate)
        if not fed_df.empty and set(["observation_date", "FEDFUNDS"]).issubset(fed_df.columns):
            f = fed_df.copy()
            f["MONTH"] = s8_month_start(f["observation_date"])
            r = r.merge(f[["MONTH", "FEDFUNDS"]], on="MONTH", how="left")

        def _pick_mode(g: pd.DataFrame) -> pd.Series:
            # If no PROB, assign equal weights
            gg = g.copy()
            if gg["PROB"].isna().all():
                gg["PROB"] = 1.0 / max(len(gg), 1)
            gg = gg.dropna(subset=["PROB"])
            if gg.empty:
                return pd.Series({"RATES_DIR": "HOLD", "RATES_PROB": np.nan})

            # pick bucket with highest probability
            peak_idx = gg["PROB"].idxmax()
            peak = gg.loc[peak_idx]
            target = peak.get("MIDPOINT", np.nan)
            current = gg["FEDFUNDS"].iloc[0] if "FEDFUNDS" in gg.columns else np.nan
            prob = peak.get("PROB", np.nan)

            if pd.isna(target) or pd.isna(current):
                return pd.Series({"RATES_DIR": "HOLD", "RATES_PROB": prob})
            if target > current:  return pd.Series({"RATES_DIR": "HIKE", "RATES_PROB": prob})
            if target < current:  return pd.Series({"RATES_DIR": "CUT",  "RATES_PROB": prob})
            return pd.Series({"RATES_DIR": "HOLD", "RATES_PROB": prob})

        if "MONTH" in r.columns:
            rates = r.groupby("MONTH").apply(_pick_mode, include_groups=False).reset_index()
        else:
            rates = pd.DataFrame()

# ---------- preprocess: price -> monthly ETH price ----------
price = pd.DataFrame()
if not price_df.empty:
    p = price_df.copy()
    if "MONTH" in p.columns:
        p["MONTH"] = s8_month_start(p["MONTH"])
    else:
        dcs = [c for c in p.columns if c.upper() in ("DATE","DAY")]
        if dcs: p["MONTH"] = s8_month_start(p[dcs[0]])
    ren = {}
    for c in p.columns:
        cu = c.upper()
        if cu == "AVG_ETH_PRICE_USD": ren[c] = "ETH_PRICE"
        if cu == "ACTIVITY_INDEX":    ren[c] = "ACTIVITY_INDEX"
    if ren: p = p.rename(columns=ren)
    for c in ["ETH_PRICE","ACTIVITY_INDEX"]:
        if c in p.columns: p[c] = s8_num(p[c])
    price = p.groupby("MONTH", as_index=False).agg({c:"mean" for c in p.columns if c != "MONTH"})

# ---------- build monthly panel ----------
frames = []
if not fees.empty:  frames.append(fees[["MONTH"] + [c for c in ["AVG_FEE","ACTIVITY_INDEX","USERS_M","TX_M"] if c in fees.columns]])
if not etf.empty:   frames.append(etf[["MONTH","ETF_NET_FLOW_M"]])
if not rates.empty: frames.append(rates[["MONTH","RATES_DIR","RATES_PROB"]])
if not price.empty: frames.append(price[["MONTH"] + [c for c in ["ETH_PRICE"] if c in price.columns]])

panel = None
for d in frames:
    panel = d if panel is None else panel.merge(d, on="MONTH", how="outer")
if panel is not None:
    panel = panel.sort_values("MONTH").reset_index(drop=True)

# ---------- header ----------
st.markdown("## 8. What Drove the Activity Spike—and Did It Feed Into Price?")
st.markdown(
    """
    <div style="padding:0.8em 1em;border-left:4px solid #2c7be5;background:#f2f6ff;border-radius:10px;">
      We decompose Ethereum’s recent on-chain traction into <strong>demand</strong> (ETF flows),
      <strong>frictions</strong> (fees), and <strong>policy regime</strong> (HIKE/HOLD/CUT).
      First we relate these drivers to <strong>Activity</strong>, then we test for <strong>price follow-through</strong>.
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------- KPIs ----------
if panel is None or panel.empty:
    st.info("Section 8: data missing. Needed files under /data: fees_activity.csv, etf_flows.csv, rates_expectations.csv, fedfunds_history.csv, eth_price.csv.")
else:
    # activity fallback: if missing, try to proxy with TX_M (scaled)
    if "ACTIVITY_INDEX" not in panel.columns and "TX_M" in panel.columns:
        panel["ACTIVITY_INDEX"] = panel["TX_M"]

    # deltas
    panel["ACT_DELTA_1M"] = panel["ACTIVITY_INDEX"].diff()
    panel["ACT_DELTA_3M"] = panel["ACTIVITY_INDEX"] - panel["ACTIVITY_INDEX"].shift(3)

    last_row = panel.dropna(subset=["MONTH"]).tail(1)
    last = last_row.iloc[0] if len(last_row) else None

    k_act   = last.get("ACTIVITY_INDEX") if last is not None else np.nan
    k_act3  = last.get("ACT_DELTA_3M")   if last is not None else np.nan
    k_fee   = last.get("AVG_FEE")        if last is not None else np.nan
    k_etf   = last.get("ETF_NET_FLOW_M") if last is not None else np.nan
    k_dir   = last.get("RATES_DIR")      if last is not None else "—"
    k_prob  = last.get("RATES_PROB")     if last is not None else np.nan
    k_price = last.get("ETH_PRICE")      if last is not None else np.nan

    c1,c2,c3,c4,c5 = st.columns(5)
    with c1: s8_kpi("Activity (latest)", f"{k_act:,.2f}" if pd.notna(k_act) else "—", "#6f42c1")
    with c2: s8_kpi("Δ Activity (3M)",   f"{k_act3:,.2f}" if pd.notna(k_act3) else "—", "#111")
    with c3: s8_kpi("Avg Fee (USD)",     f"{k_fee:,.2f}" if pd.notna(k_fee) else "—", "#2c7be5")
    with c4: s8_kpi("ETF Net Flow (M)",  s8_fmt_millions(k_etf), "#00b894")
    with c5: s8_kpi("Rates Mode",        f"{k_dir} ({k_prob:.0%})" if pd.notna(k_prob) else f"{k_dir}", "#ff7f0e")

    st.markdown("---")

    # ================================
# 8) Activity Drivers — Fees, ETF Flows & Rates
# ================================
import os
import io
import pandas as pd
import numpy as np
import altair as alt
import streamlit as st

# ---- local helpers (scoped to this section) ----
def _month_start(x: pd.Series) -> pd.Series:
    """Coerce to tz-naive month-start timestamps."""
    dt = pd.to_datetime(x, errors="coerce", utc=True)
    return pd.to_datetime(dt.dt.strftime("%Y-%m-01"))

def _read_csv_smart(path: str, expected_cols=None) -> pd.DataFrame:
    """
    Robust CSV reader:
    - detects semicolon vs comma
    - tolerates mixed date formats (dayfirst inference optional)
    - trims columns and coerces numerics where sensible
    """
    if not os.path.exists(path):
        return pd.DataFrame()
    # sniff delimiter
    with open(path, "r", encoding="utf-8") as f:
        head = f.read(4096)
    delim = ";" if head.count(";") > head.count(",") else ","
    df = pd.read_csv(path, delimiter=delim)
    # strip colnames
    df.columns = [c.strip() for c in df.columns]
    # auto-trim strings
    for c in df.select_dtypes(include="object").columns:
        df[c] = df[c].astype(str).str.strip()
    # coerce obvious numerics
    if expected_cols:
        for c in expected_cols:
            if c in df.columns:
                # try numeric (keeps NaN if fails), also handle (x) accounting & % signs
                df[c] = (
                    df[c]
                    .astype(str)
                    .str.replace("%", "", regex=False)
                    .str.replace(",", "", regex=False)
                    .str.replace("(", "-", regex=False)
                    .str.replace(")", "", regex=False)
                )
                df[c] = pd.to_numeric(df[c], errors="coerce")
    return df

def _kpi_chip(label: str, value: str, color: str = "#2563eb"):
    st.markdown(
        f"""
        <div style="
            display:flex;align-items:center;gap:10px;
            border:1px solid #e5e7eb;border-left:6px solid {color};
            border-radius:10px;padding:10px 14px;margin:4px 0;">
            <div style="font-weight:600;color:#111827;">{label}</div>
            <div style="font-weight:700;color:#111827;">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def _mini_note(msg: str):
    st.markdown(
        f"""<div style="font-size:0.875rem;color:#374151;margin:6px 0 2px 2px;">{msg}</div>""",
        unsafe_allow_html=True,
    )

def _section_rule():
    st.markdown('<hr style="margin:20px 0;border:none;border-top:1px solid #e5e7eb;">', unsafe_allow_html=True)

# ---- load core activity/price/fees (eth_price.csv) ----
df_base = _read_csv_smart(
    os.path.join("data", "eth_price.csv"),
    expected_cols=["AVG_ETH_PRICE_USD", "AVG_TX_FEE_USD", "TOTAL_TRANSACTIONS", "UNIQUE_USERS", "TOTAL_VOLUME_BILLIONS", "ACTIVITY_INDEX"]
)
# month
if "MONTH" in df_base.columns:
    df_base["MONTH"] = _month_start(df_base["MONTH"])
elif "DATE" in df_base.columns:
    df_base["MONTH"] = _month_start(df_base["DATE"])
else:
    df_base["MONTH"] = pd.NaT
df_base = df_base.dropna(subset=["MONTH"]).sort_values("MONTH").reset_index(drop=True)

# ---- ETF flows (etf_flows.csv) ----
df_etf = _read_csv_smart(os.path.join("data", "etf_flows.csv"), expected_cols=["ETF_NET_FLOW_USD_MILLIONS"])
# handle possibly different time col names
if "MONTH" in df_etf.columns:
    df_etf["MONTH"] = _month_start(df_etf["MONTH"])
elif "DATE" in df_etf.columns:
    df_etf["MONTH"] = _month_start(df_etf["DATE"])
else:
    df_etf["MONTH"] = pd.NaT
df_etf = df_etf.dropna(subset=["MONTH"])
# keep only the column we were told is populated
etf_cols = [c for c in df_etf.columns if c.upper() == "ETF_NET_FLOW_USD_MILLIONS"]
if etf_cols:
    df_etf = df_etf[["MONTH", etf_cols[0]]].rename(columns={etf_cols[0]: "ETF_NET_FLOW_USD_MILLIONS"})
else:
    df_etf["ETF_NET_FLOW_USD_MILLIONS"] = np.nan
    df_etf = df_etf[["MONTH", "ETF_NET_FLOW_USD_MILLIONS"]]

# ---- Rates expectations (rates_expectations.csv) & Fed funds history ----
df_rates = _read_csv_smart(os.path.join("data", "rates_expectations.csv"), expected_cols=["LOWER_BPS","UPPER_BPS","PROB"])
# Accept either MONTH or DATE
date_col = "MONTH" if "MONTH" in df_rates.columns else ("DATE" if "DATE" in df_rates.columns else None)
if date_col:
    df_rates["MONTH"] = _month_start(df_rates[date_col])
else:
    df_rates["MONTH"] = pd.NaT
df_rates = df_rates.dropna(subset=["MONTH"])

# Ensure required columns; if not present, try to infer
if not set(["LOWER_BPS","UPPER_BPS","PROB"]).issubset(df_rates.columns):
    # try to guess: look for columns with 'LOWER','UPPER','PROB' substrings
    cols = {k: None for k in ["LOWER_BPS","UPPER_BPS","PROB"]}
    for c in df_rates.columns:
        u = c.upper()
        if cols["LOWER_BPS"] is None and "LOWER" in u:
            cols["LOWER_BPS"] = c
        if cols["UPPER_BPS"] is None and "UPPER" in u:
            cols["UPPER_BPS"] = c
        if cols["PROB"] is None and "PROB" in u:
            cols["PROB"] = c
    # rename if found
    ren = {v: k for k, v in cols.items() if v is not None}
    df_rates = df_rates.rename(columns=ren)

# clean PROB to [0,1]
if "PROB" in df_rates.columns:
    # if values look like 0-100, scale down
    p95 = np.nanpercentile(df_rates["PROB"].dropna(), 95) if df_rates["PROB"].notna().any() else np.nan
    if pd.notna(p95) and p95 > 1.5:  # likely percent
        df_rates["PROB"] = df_rates["PROB"] / 100.0

# Midpoint in bps for the bucket
if set(["LOWER_BPS","UPPER_BPS"]).issubset(df_rates.columns):
    df_rates["MIDPOINT_BPS"] = (df_rates["LOWER_BPS"].astype(float) + df_rates["UPPER_BPS"].astype(float)) / 2.0
else:
    df_rates["MIDPOINT_BPS"] = np.nan

# Fed funds history (monthly level)
fed = _read_csv_smart(os.path.join("data", "fedfunds_history.csv"))
# expect observation_date, FEDFUNDS (effective rate)
if "observation_date" in fed.columns:
    fed["MONTH"] = _month_start(fed["observation_date"])
elif "DATE" in fed.columns:
    fed["MONTH"] = _month_start(fed["DATE"])
else:
    fed["MONTH"] = pd.NaT
# coerce FEDFUNDS
if "FEDFUNDS" in fed.columns:
    fed["FEDFUNDS"] = pd.to_numeric(fed["FEDFUNDS"], errors="coerce")
else:
    fed["FEDFUNDS"] = np.nan
fed = fed.dropna(subset=["MONTH"]).sort_values("MONTH")

# Label each rates row as cut/hold/hike vs that month’s FedFunds
if not df_rates.empty and not fed.empty:
    df_rates = df_rates.merge(fed[["MONTH","FEDFUNDS"]], on="MONTH", how="left")
    # compare midpoint (in bps) to FEDFUNDS * 100 bps
    df_rates["DIR"] = np.where(
        df_rates["MIDPOINT_BPS"] < df_rates["FEDFUNDS"] * 100 - 5, "Cut",
        np.where(df_rates["MIDPOINT_BPS"] > df_rates["FEDFUNDS"] * 100 + 5, "Hike", "Hold")
    )
    # Aggregate to monthly probability of each direction
    # (sum of probs by DIR; if PROB missing, fall back to equal-share by bucket)
    if "PROB" in df_rates.columns and df_rates["PROB"].notna().any():
        prob_by_dir = (df_rates.groupby(["MONTH","DIR"], as_index=False)["PROB"].sum())
        # normalize to 1 per month if sums > 1 because of overlaps
        prob_by_dir["sum_m"] = prob_by_dir.groupby("MONTH")["PROB"].transform("sum")
        prob_by_dir["PROB_NORM"] = np.where(prob_by_dir["sum_m"]>0, prob_by_dir["PROB"] / prob_by_dir["sum_m"], np.nan)
        monthly_dir = prob_by_dir.pivot(index="MONTH", columns="DIR", values="PROB_NORM").reset_index()
    else:
        # equal weight by bucket if PROB not present
        ct = df_rates.groupby(["MONTH","DIR"], as_index=False).size()
        ct["sum_m"] = ct.groupby("MONTH")["size"].transform("sum")
        ct["share"] = np.where(ct["sum_m"]>0, ct["size"] / ct["sum_m"], np.nan)
        monthly_dir = ct.pivot(index="MONTH", columns="DIR", values="share").reset_index()
    for c in ["Cut","Hold","Hike"]:
        if c not in monthly_dir.columns:
            monthly_dir[c] = 0.0
else:
    monthly_dir = pd.DataFrame(columns=["MONTH","Cut","Hold","Hike"])

# ---- Merge a clean panel by MONTH ----
panel = (
    df_base[["MONTH","ACTIVITY_INDEX","AVG_TX_FEE_USD","AVG_ETH_PRICE_USD"]]
    .merge(df_etf, on="MONTH", how="left")
    .merge(monthly_dir, on="MONTH", how="left")
    .sort_values("MONTH")
    .reset_index(drop=True)
)

# ---- KPIs (latest) ----
latest_row = panel.dropna(subset=["MONTH"]).tail(1)
k1 = float(latest_row["ACTIVITY_INDEX"].iloc[0]) if not latest_row.empty and "ACTIVITY_INDEX" in latest_row else np.nan
k2 = float(latest_row["AVG_TX_FEE_USD"].iloc[0]) if not latest_row.empty and "AVG_TX_FEE_USD" in latest_row else np.nan
k3 = float(latest_row["ETF_NET_FLOW_USD_MILLIONS"].iloc[0]) if not latest_row.empty and "ETF_NET_FLOW_USD_MILLIONS" in latest_row else np.nan
# pick highest prob dir
if not latest_row.empty:
    trio = latest_row[["Cut","Hold","Hike"]].astype(float).fillna(0.0).iloc[0].to_dict()
    top_dir = max(trio, key=trio.get)
    top_p   = trio[top_dir]
else:
    top_dir, top_p = "—", np.nan

# ---- Section title + context (HTML so bold/italic render) ----
st.markdown(
    """
    <h3 style="margin-bottom:0.25rem;">8) Activity Drivers — Fees, ETF Flows & Rates</h3>
    <p style="color:#374151; margin-top:0.25rem;">
      We test whether the recent <strong>activity surge</strong> on Ethereum aligns with
      <em>lower transaction costs</em>, stronger <em>ETF net inflows</em>, and <em>easier rate expectations</em>.
      Then we check whether rising activity relates to <strong>price</strong>.
    </p>
    """,
    unsafe_allow_html=True,
)
# KPIs row
c1, c2, c3, c4 = st.columns(4)
with c1: _kpi_chip("Activity Index (latest)", f"{k1:,.2f}" if pd.notna(k1) else "—", "#2563eb")
with c2: _kpi_chip("Avg Tx Fee (USD)",      f"{k2:,.2f}" if pd.notna(k2) else "—", "#059669")
with c3: _kpi_chip("ETF Net Flow (USD m)",  f"{k3:,.1f}" if pd.notna(k3) else "—", "#7c3aed")
with c4: _kpi_chip("Rates Direction",        f"{top_dir} ({top_p:.0%})" if pd.notna(top_p) else "—", "#d97706")

# =========================================
# Chart A — Activity vs Fees (dual-scale)
# =========================================
if not panel.empty:
    baseA = alt.Chart(panel).encode(x=alt.X("MONTH:T", title="Month"))
    line_activity = baseA.mark_line(strokeWidth=2).encode(
        y=alt.Y("ACTIVITY_INDEX:Q", axis=alt.Axis(title="Activity Index")),
        tooltip=[alt.Tooltip("MONTH:T"), alt.Tooltip("ACTIVITY_INDEX:Q", format=",.2f")]
    )
    line_fees = baseA.mark_line(strokeDash=[4,2], opacity=0.8).encode(
        y=alt.Y("AVG_TX_FEE_USD:Q", axis=alt.Axis(title="Avg Tx Fee (USD)")),
        color=alt.value("#059669"),
        tooltip=[alt.Tooltip("MONTH:T"), alt.Tooltip("AVG_TX_FEE_USD:Q", format=",.2f")]
    )
    chA = alt.layer(line_activity, line_fees).resolve_scale(y="independent").properties(
        title="A) Activity vs Transaction Fees", height=320
    )
    st.altair_chart(chA, use_container_width=True)
    _mini_note("Lower fees historically coincide with broader participation; the 2025 run-up pairs falling fees with rising activity.")
else:
    st.info("No data for Activity/Fee chart.")

_section_rule()

# =========================================
# Chart B — Activity vs ETF Net Flows
# =========================================
if "ETF_NET_FLOW_USD_MILLIONS" in panel.columns and panel["ETF_NET_FLOW_USD_MILLIONS"].notna().any():
    baseB = alt.Chart(panel).encode(x=alt.X("MONTH:T", title="Month"))
    bars_flow = baseB.mark_bar(opacity=0.55).encode(
        y=alt.Y("ETF_NET_FLOW_USD_MILLIONS:Q", axis=alt.Axis(title="ETF Net Flow (USD m)")),
        color=alt.condition(alt.datum.ETF_NET_FLOW_USD_MILLIONS >= 0, alt.value("#7c3aed"), alt.value("#a8a29e")),
        tooltip=[alt.Tooltip("MONTH:T"), alt.Tooltip("ETF_NET_FLOW_USD_MILLIONS:Q", format=",.1f", title="ETF Net Flow (m)")]
    )
    line_act = baseB.mark_line(stroke="#2563eb", strokeWidth=2).encode(
        y=alt.Y("ACTIVITY_INDEX:Q", axis=alt.Axis(title="Activity Index")),
        tooltip=[alt.Tooltip("MONTH:T"), alt.Tooltip("ACTIVITY_INDEX:Q", format=",.2f")]
    )
    chB = alt.layer(bars_flow, line_act).resolve_scale(y="independent").properties(
        title="B) Activity vs ETF Net Flows", height=320
    )
    st.altair_chart(chB, use_container_width=True)
    _mini_note("ETF inflows strengthened into the activity highs; sign suggests fresh demand alongside on-chain throughput.")
else:
    st.info("No ETF flow data available for Chart B.")

_section_rule()

# =========================================
# Chart C — Rates Cut/Hold/Hike Probabilities + Activity
# =========================================
if not monthly_dir.empty:
    df_rates_plot = monthly_dir.merge(panel[["MONTH","ACTIVITY_INDEX"]], on="MONTH", how="left")
    long_probs = df_rates_plot.melt(id_vars=["MONTH","ACTIVITY_INDEX"], value_vars=["Cut","Hold","Hike"],
                                    var_name="Direction", value_name="Prob")
    baseC = alt.Chart(long_probs).encode(x=alt.X("MONTH:T", title="Month"))
    area_probs = baseC.mark_area(opacity=0.5).encode(
        y=alt.Y("Prob:Q", stack="normalize", axis=alt.Axis(format="%", title="Rates Direction Probability")),
        color=alt.Color("Direction:N",
                        scale=alt.Scale(domain=["Cut","Hold","Hike"], range=["#10b981","#93c5fd","#ef4444"]),
                        legend=alt.Legend(title="Rates View")),
        tooltip=[alt.Tooltip("MONTH:T"), "Direction:N", alt.Tooltip("Prob:Q", format=".0%")]
    )
    line_act2 = alt.Chart(df_rates_plot).mark_line(stroke="#2563eb", strokeWidth=2).encode(
        x="MONTH:T",
        y=alt.Y("ACTIVITY_INDEX:Q", axis=alt.Axis(title="Activity Index")),
        tooltip=[alt.Tooltip("MONTH:T"), alt.Tooltip("ACTIVITY_INDEX:Q", format=",.2f")]
    )
    chC = alt.layer(area_probs, line_act2).resolve_scale(y="independent").properties(
        title="C) Rates Expectations vs Activity", height=340
    )
    st.altair_chart(chC, use_container_width=True)
    _mini_note("Shifts toward ‘Cut’/‘Hold’ co-move with stronger activity; easier policy tends to support throughput risk-on.")
else:
    st.info("No rates expectation data available for Chart C.")

_section_rule()

# =========================================
# Chart D — Activity vs ETH Price (scatter with trend)
# =========================================
if not panel.empty and panel[["ACTIVITY_INDEX","AVG_ETH_PRICE_USD"]].notna().all(axis=None):
    sc = alt.Chart(panel).mark_circle(size=80, opacity=0.7, color="#2563eb").encode(
        x=alt.X("ACTIVITY_INDEX:Q", title="Activity Index"),
        y=alt.Y("AVG_ETH_PRICE_USD:Q", title="ETH Price (USD)"),
        tooltip=[alt.Tooltip("MONTH:T"), alt.Tooltip("ACTIVITY_INDEX:Q", format=",.2f"),
                 alt.Tooltip("AVG_ETH_PRICE_USD:Q", format=",.0f", title="ETH Price")]
    )
    trend = sc.transform_regression("ACTIVITY_INDEX", "AVG_ETH_PRICE_USD").mark_line(color="#111827")
    chD = (sc + trend).properties(title="D) Does Higher Activity Map to Higher Price?", height=320)
    st.altair_chart(chD, use_container_width=True)
    _mini_note("Positive slope suggests price tends to be higher in high-activity regimes (correlation, not causation).")
else:
    st.info("Insufficient data for Activity–Price scatter.")

# end of Section 8


# -----------------------------------------------------------
# Footer
# -----------------------------------------------------------
st.markdown('<div class="sep"></div>', unsafe_allow_html=True)
st.caption("Built by Adrià Parcerisas • Data via Flipside/Dune exports • Code quality and metric selection optimized for panel discussion.")



























