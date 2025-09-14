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
# 8. Activity Drivers — Fees, ETF Flows & Rates Direction
# =========================
import os
import pandas as pd
import numpy as np
import altair as alt
import streamlit as st

# ---------- helpers (local-only; safe to re-declare) ----------
def _auto_read_csv(path: str) -> pd.DataFrame:
    """Read CSV or TSV with unknown delimiter; strip headers; keep strings; no NA filtering."""
    if not os.path.exists(path):
        return pd.DataFrame()
    try:
        df = pd.read_csv(
            path,
            sep=None,               # auto-detect delimiter (comma/semicolon/tab)
            engine="python",
            dtype=str,              # keep raw; we will coerce later
            skip_blank_lines=True
        )
        # strip header whitespace
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except Exception:
        # fallback: try semicolon, then comma
        for sep in [";", ",", "\t", "|"]:
            try:
                df = pd.read_csv(path, sep=sep, dtype=str, skip_blank_lines=True)
                df.columns = [str(c).strip() for c in df.columns]
                return df
            except Exception:
                continue
    return pd.DataFrame()

def _month_start(series) -> pd.Series:
    """Normalize any date-like series to month start, tz-naive. Accepts dd/mm/yyyy."""
    dt = pd.to_datetime(series, errors="coerce", utc=True, dayfirst=True, infer_datetime_format=True)
    dt = dt.dt.tz_localize(None)
    return dt.dt.to_period("M").dt.to_timestamp()

def _clean_number_like(x: str) -> str:
    """Strip everything except digits, dot, minus, and comma; convert comma to dot."""
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return ""
    s = str(x)
    # remove percent sign and spaces
    s = s.replace("%", "").replace(" ", "")
    # parentheses usually mean negative; handle "(1.23)" -> "-1.23"
    neg = s.startswith("(") and s.endswith(")")
    # keep only digits . , and -
    import re
    s = "".join(re.findall(r"[0-9\.,\-]+", s))
    s = s.replace(",", ".")
    if neg and s and not s.startswith("-"):
        s = "-" + s
    return s

def _coerce_num(s, default=np.nan):
    """To numeric, tolerant, using _clean_number_like first."""
    if isinstance(s, (int, float, np.number)):
        return pd.to_numeric(s, errors="coerce").fillna(default)
    if isinstance(s, pd.Series):
        s2 = s.map(_clean_number_like)
        return pd.to_numeric(s2, errors="coerce").fillna(default)
    return pd.to_numeric(_clean_number_like(s), errors="coerce")

def _last_notna(series):
    """Last non-null value in a series; returns np.nan if none."""
    if series is None or series.empty:
        return np.nan
    s = series.dropna()
    return s.iloc[-1] if not s.empty else np.nan

# ---------- data loaders ----------
def load_etf_monthly(path="data/etf_flows.csv") -> pd.DataFrame:
    df = _auto_read_csv(path)
    if df.empty:
        return df
    cols = {c.upper(): c for c in df.columns}

    # We expect either MONTH or a date-like column we can use
    if "MONTH" in cols:
        month_col = cols["MONTH"]
        df["MONTH"] = _month_start(df[month_col])
    else:
        # Try any likely date column
        date_like = None
        candidates = ["DATE", "DAY", "TIMESTAMP", "OBSERVATION_DATE"]
        for c in candidates:
            if c in cols:
                date_like = cols[c]
                break
        if date_like is None:
            # If literally the first column looks like a date, try it
            date_like = df.columns[0]
        df["MONTH"] = _month_start(df[date_like])

    # Value column: prefer ETF_NET_FLOW_USD_MILLIONS; otherwise try NET_FLOW or similar
    val_col = None
    for k in ["ETF_NET_FLOW_USD_MILLIONS", "NET_FLOW_USD_MILLIONS", "NET_FLOW", "ETF_NET_FLOW"]:
        if k in cols:
            val_col = cols[k]
            break
    if val_col is None:
        # Nothing usable
        return pd.DataFrame(columns=["MONTH", "ETF_NET_FLOW_M"])

    df["ETF_NET_FLOW_M"] = _coerce_num(df[val_col])
    out = (
        df[["MONTH", "ETF_NET_FLOW_M"]]
        .dropna(subset=["MONTH"])
        .groupby("MONTH", as_index=False).sum()
        .sort_values("MONTH")
    )
    return out

def load_fed_history(path="data/fedfunds_history.csv") -> pd.DataFrame:
    df = _auto_read_csv(path)
    if df.empty:
        return df
    # Expect observation_date, FEDFUNDS
    cols = {c.upper(): c for c in df.columns}
    date_col = cols.get("OBSERVATION_DATE", None) or list(df.columns)[0]
    rate_col = cols.get("FEDFUNDS", None)
    if rate_col is None:
        # if not present, bail out
        return pd.DataFrame()

    df["MONTH"]     = _month_start(df[date_col])
    df["FEDFUNDS"]  = _coerce_num(df[rate_col])
    out = df[["MONTH", "FEDFUNDS"]].dropna().drop_duplicates("MONTH").sort_values("MONTH")
    return out

def load_rates_expectations(path="data/rates_expectations.csv") -> pd.DataFrame:
    """
    Accepts two shapes:
      1) DATE, LOWER_BPS, UPPER_BPS, PROB
      2) DATE and a set of bucket columns like '425-450','450-475', ... with probabilities.
    Produces: MONTH, DIRECTION_PROB (CUT/HOLD/HIKE) after comparing to FedFunds level for that month.
    """
    df = _auto_read_csv(path)
    if df.empty:
        return df

    # Normalize DATE -> MONTH
    possible_date = None
    for c in df.columns:
        u = c.upper()
        if u in ("DATE", "DAY", "TIMESTAMP", "OBSERVATION_DATE", "MONTH"):
            possible_date = c
            break
    if possible_date is None:
        possible_date = df.columns[0]
    df["MONTH"] = _month_start(df[possible_date])

    # Try wide format (bucket columns) first
    # Bucket names like '425-450' or '4.25-4.50' etc.
    bucket_cols = []
    for c in df.columns:
        cu = c.upper()
        if cu not in ("DATE", "DAY", "TIMESTAMP", "OBSERVATION_DATE", "MONTH"):
            # heuristic: looks like a bucket if it contains '-' and a digit
            if ("-" in c) and any(ch.isdigit() for ch in c):
                bucket_cols.append(c)

    long = None
    if bucket_cols:
        tmp = df[["MONTH"] + bucket_cols].copy()
        long = tmp.melt(id_vars="MONTH", var_name="BUCKET", value_name="PROB")
        long["PROB"] = _coerce_num(long["PROB"])
        # Parse lower/upper from the bucket label
        def _parse_bounds(label):
            """
            Parse a bucket label into (lower_bps, upper_bps).
            Accepts forms like '(0.50–0.75)', '0.50-0.75', '425-450', '4.25–4.50 %', etc.
            """
            s = str(label)
            # unify separators and strip junk
            s = s.replace("to", "-").replace("–", "-").replace("—", "-")
            # split
            parts = s.split("-")
            if len(parts) != 2:
                return np.nan, np.nan
        
            def to_bps(piece):
                cleaned = _clean_number_like(piece)
                if cleaned == "":
                    return np.nan
                val = float(cleaned)
                # if it's likely percent (<= 30), convert to bps. If it's already bps (hundreds+), keep.
                return val * 100.0 if val <= 30 else val
        
            lo = to_bps(parts[0])
            hi = to_bps(parts[1])
            return lo, hi
        bounds = long["BUCKET"].map(_parse_bounds)
        long["LOWER_BPS"] = [b[0] for b in bounds]
        long["UPPER_BPS"] = [b[1] for b in bounds]
    else:
        # assume tidy: DATE, LOWER_BPS, UPPER_BPS, PROB
        cols = {c.upper(): c for c in df.columns}
        need = all(k in cols for k in ["LOWER_BPS", "UPPER_BPS", "PROB"])
        if not need:
            return pd.DataFrame()
        long = df[[ "MONTH", cols["LOWER_BPS"], cols["UPPER_BPS"], cols["PROB"] ]].copy()
        long.columns = ["MONTH", "LOWER_BPS", "UPPER_BPS", "PROB"]
        long["PROB"]      = _coerce_num(long["PROB"])
        long["LOWER_BPS"] = _coerce_num(long["LOWER_BPS"])
        long["UPPER_BPS"] = _coerce_num(long["UPPER_BPS"])

    # clean
    long = long.dropna(subset=["MONTH", "LOWER_BPS", "UPPER_BPS", "PROB"])
    # we’ll attach FEDFUNDS later in the section

    return long[["MONTH", "LOWER_BPS", "UPPER_BPS", "PROB"]].sort_values(["MONTH", "LOWER_BPS"])

# ---------- UI section ----------
st.markdown("## 8. Activity Drivers — Fees, ETF Flows & Rates Direction")
st.markdown(
    "> **Definition**  \n"
    "Relates **transaction costs**, **ETF net flows** and **policy direction** to Ethereum’s on-chain activity. "
    "Rates direction is inferred via the **most probable bucket** vs the month’s Fed Funds level.",
)

# Load external files
etf_m   = load_etf_monthly()                 # -> MONTH, ETF_NET_FLOW_M
fed_m   = load_fed_history()                 # -> MONTH, FEDFUNDS
rates_l = load_rates_expectations()          # -> MONTH, LOWER_BPS, UPPER_BPS, PROB

# Build Rates Direction per MONTH (mode by PROB) if we have both expectations and Fed Funds
rates_dir = pd.DataFrame(columns=["MONTH", "DIRECTION", "DIR_SCORE"])
if not rates_l.empty and not fed_m.empty:
    # attach fed funds
    tmp = rates_l.merge(fed_m, on="MONTH", how="left")
    tmp["FED_BPS"] = tmp["FEDFUNDS"] * 100.0
    # bucket midpoint for tie-breaking/visuals (optional)
    tmp["MID_BPS"] = (tmp["LOWER_BPS"] + tmp["UPPER_BPS"]) / 2.0
    # classify bucket vs current rate
    tmp["BUCKET_DIR"] = np.where(
        tmp["UPPER_BPS"] + 1e-9 < tmp["FED_BPS"], "CUT",
        np.where(tmp["LOWER_BPS"] - 1e-9 > tmp["FED_BPS"], "HIKE", "HOLD")
    )
    # pick the direction with highest PROB per month
    # also keep the probability as DIR_SCORE for the KPI
    g = tmp.groupby(["MONTH", "BUCKET_DIR"], as_index=False)["PROB"].sum()
    idx = g.groupby("MONTH")["PROB"].idxmax()
    rates_dir = g.loc[idx].rename(columns={"BUCKET_DIR": "DIRECTION", "PROB": "DIR_SCORE"}).sort_values("MONTH")

# Fees / Activity Index from your existing pipeline if available
# (we don't touch your prior code; we only read what it produced)
act_line = None
fee_line = None
latest_act = np.nan
latest_fee = np.nan

# Common names seen earlier in your app — adjust only if necessary
if "df_activity_idx" in globals():
    act_line = globals()["df_activity_idx"][["MONTH", "ACTIVITY_IDX"]].dropna().sort_values("MONTH")
    latest_act = _last_notna(act_line["ACTIVITY_IDX"])
if "df_fee_monthly" in globals():
    fee_line = globals()["df_fee_monthly"][["MONTH", "AVG_FEE_USD"]].dropna().sort_values("MONTH")
    latest_fee = _last_notna(fee_line["AVG_FEE_USD"])

# KPIs (robust to missing)
kpi_cols = st.columns(4)
with kpi_cols[0]:
    st.markdown("**Activity Index (latest)**")
    st.markdown(f"{latest_act:.2f}" if pd.notna(latest_act) else "—")
with kpi_cols[1]:
    st.markdown("**Avg Tx Fee (USD)**")
    st.markdown(f"{latest_fee:.2f}" if pd.notna(latest_fee) else "—")
with kpi_cols[2]:
    last_etf = _last_notna(etf_m["ETF_NET_FLOW_M"]) if not etf_m.empty else np.nan
    st.markdown("**ETF Net Flow**")
    st.markdown(f"{last_etf:.0f}M" if pd.notna(last_etf) else "—M")
with kpi_cols[3]:
    d_lab = "—"
    if not rates_dir.empty:
        d_lab = f'{rates_dir.iloc[-1]["DIRECTION"]} ({rates_dir.iloc[-1]["DIR_SCORE"]:.0%})'
    st.markdown("**Fed Direction (mode)**")
    st.markdown(d_lab)

# Chart: show what we have (activity/fees always on left axis; etf on right axis if present)
layers = []
base = None

def _alt_date(df, x="MONTH"):
    d = df.copy()
    d[x] = pd.to_datetime(d[x])
    return d

if act_line is not None and not act_line.empty:
    base = alt.Chart(_alt_date(act_line)).encode(x=alt.X("MONTH:T", title=None))
    layers.append(
        base.mark_line(point=True, interpolate="monotone").encode(
            y=alt.Y("ACTIVITY_IDX:Q", title="Activity Index"),
            tooltip=[alt.Tooltip("MONTH:T"), alt.Tooltip("ACTIVITY_IDX:Q", format=".2f", title="Activity Index")]
        ).properties(height=360)
    )

if fee_line is not None and not fee_line.empty:
    base = base or alt.Chart(_alt_date(fee_line)).encode(x=alt.X("MONTH:T", title=None))
    layers.append(
        alt.Chart(_alt_date(fee_line)).mark_line(strokeDash=[4,3]).encode(
            x="MONTH:T",
            y=alt.Y("AVG_FEE_USD:Q", title="Fees (USD) / ETF Net Flow (M)"),
            tooltip=[alt.Tooltip("MONTH:T"), alt.Tooltip("AVG_FEE_USD:Q", format=".2f", title="Avg Fee (USD)")]
        )
    )

if not etf_m.empty:
    etf_for_chart = _alt_date(etf_m.rename(columns={"ETF_NET_FLOW_M": "ETF_M"}))
    layers.append(
        alt.Chart(etf_for_chart).mark_area(opacity=0.18).encode(
            x="MONTH:T",
            y=alt.Y("ETF_M:Q", axis=alt.Axis(title="Fees (USD) / ETF Net Flow (M)", orient="right")),
            tooltip=[alt.Tooltip("MONTH:T"), alt.Tooltip("ETF_M:Q", format=".0f", title="ETF Net Flow (M)")]
        )
    )

if layers:
    st.altair_chart(alt.layer(*layers).resolve_scale(y='independent'), use_container_width=True)
else:
    st.info("No chartable data for this section yet. The KPIs above will populate as soon as the CSVs are readable.")

# Optional insight line (renders bold correctly)
st.markdown(
    "> **Insight.** Fees have eased while ETF net flows and policy expectations provide additional context "
    "for demand impulses. Mode of rate expectations offers a simple directional signal (Hike/Cut/Hold)."
)



# -----------------------------------------------------------
# Footer
# -----------------------------------------------------------
st.markdown('<div class="sep"></div>', unsafe_allow_html=True)
st.caption("Built by Adrià Parcerisas • Data via Flipside/Dune exports • Code quality and metric selection optimized for panel discussion.")





















