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

    # ======================
    # 8A — Activity vs ETF Net Flow, with policy bands
    # ======================
    plotA = panel.dropna(subset=["MONTH"])
    bands = plotA[["MONTH","RATES_DIR"]].dropna().drop_duplicates().copy()
    band = alt.LayerChart()
    if not bands.empty:
        bands["MONTH_NEXT"] = bands["MONTH"] + pd.offsets.MonthBegin(1)
        band = alt.Chart(bands).mark_rect(opacity=0.45).encode(
            x=alt.X("MONTH:T", title=None),
            x2="MONTH_NEXT:T",
            color=alt.Color("RATES_DIR:N",
                            scale=alt.Scale(domain=["HIKE","HOLD","CUT"],
                                            range=["#ffe5e5","#f5f7fb","#e8fff0"]),
                            legend=alt.Legend(title="Rates (mode)"))
        )

    layers = []
    if "ETF_NET_FLOW_M" in plotA.columns and plotA["ETF_NET_FLOW_M"].notna().any():
        bars = alt.Chart(plotA).mark_bar().encode(
            x=alt.X("MONTH:T", title=None),
            y=alt.Y("ETF_NET_FLOW_M:Q", title="ETF Net Flow (USD millions)", axis=alt.Axis(grid=True)),
            tooltip=[alt.Tooltip("MONTH:T", title="Month"),
                     alt.Tooltip("ETF_NET_FLOW_M:Q", title="ETF Net Flow (M)", format=",.1f")]
        )
        layers.append(bars)
    if "ACTIVITY_INDEX" in plotA.columns and plotA["ACTIVITY_INDEX"].notna().any():
        line = alt.Chart(plotA).mark_line(strokeWidth=2, color="#6f42c1").encode(
            x=alt.X("MONTH:T"),
            y=alt.Y("ACTIVITY_INDEX:Q", title="Activity Index", axis=alt.Axis(grid=True)),
            tooltip=[alt.Tooltip("MONTH:T", title="Month"),
                     alt.Tooltip("ACTIVITY_INDEX:Q", title="Activity", format=",.2f")]
        )
        chartA = alt.layer(band, *(layers + [line])).resolve_scale(y="independent").properties(height=380)
        st.altair_chart(chartA, use_container_width=True)
    else:
        if layers:
            st.altair_chart(alt.layer(band, *layers).properties(height=360), use_container_width=True)
        else:
            st.info("Not enough data to draw 8A.")

    st.markdown(
        """
        <div style="margin-top:6px;padding:0.6em 1em;border-left:4px solid #888;background:#f9f9f9;border-radius:8px;">
          <strong>Insight.</strong> Do <em>activity upswings</em> align with <em>ETF net inflows</em>, especially under
          <em>HOLD/CUT</em> policy bands? If yes, flows likely contributed materially to on-chain usage.
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ======================
    # 8B — Activity vs Fees (fee sensitivity)
    # ======================
    needed = {"AVG_FEE","ACTIVITY_INDEX"}
    if needed.issubset(set(panel.columns)):
        scat = panel.dropna(subset=list(needed)).copy()
        # bubble by transactions/users if available
        if "TX_M" in scat.columns:
            scat["BUBBLE"] = scat["TX_M"].clip(lower=0)*30 + 30
        elif "USERS_M" in scat.columns:
            scat["BUBBLE"] = scat["USERS_M"].clip(lower=0)*30 + 30
        else:
            scat["BUBBLE"] = 60

        scatter = alt.Chart(scat).mark_circle(opacity=0.75).encode(
            x=alt.X("AVG_FEE:Q", title="Avg Tx Fee (USD)"),
            y=alt.Y("ACTIVITY_INDEX:Q", title="Activity Index"),
            size=alt.Size("BUBBLE:Q", legend=None),
            color=alt.Color("AVG_FEE:Q", scale=alt.Scale(scheme="blues"), legend=None),
            tooltip=[
                alt.Tooltip("MONTH:T", title="Month"),
                alt.Tooltip("AVG_FEE:Q", title="Avg Fee (USD)", format=",.2f"),
                alt.Tooltip("ACTIVITY_INDEX:Q", title="Activity", format=",.2f"),
                alt.Tooltip("TX_M:Q", title="Tx (M)", format=",.2f"),
                alt.Tooltip("USERS_M:Q", title="Users (M)", format=",.2f"),
            ]
        )
        trend = alt.Chart(scat).transform_regression("AVG_FEE", "ACTIVITY_INDEX").mark_line(color="#ff7f0e")
        chartB = (scatter + trend).properties(height=360)
        st.altair_chart(chartB, use_container_width=True)

        st.markdown(
            """
            <div style="margin-top:6px;padding:0.6em 1em;border-left:4px solid #888;background:#f9f9f9;border-radius:8px;">
              <strong>Insight.</strong> A downward slope indicates fee-sensitive usage: lower fees → higher activity.
              This helps separate <em>frictions</em> from <em>demand</em> when explaining the spike.
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.info("8B needs AVG_FEE and ACTIVITY_INDEX from fees_activity.csv.")

    # ======================
    # 8C — ΔActivity by Policy Mode (HIKE/HOLD/CUT)
    # ======================
    if {"RATES_DIR","ACT_DELTA_1M"}.issubset(set(panel.columns)) and panel["ACT_DELTA_1M"].notna().any():
        boxdata = panel.dropna(subset=["RATES_DIR","ACT_DELTA_1M"]).copy()
        chartC = alt.Chart(boxdata).mark_boxplot(extent="min-max").encode(
            x=alt.X("RATES_DIR:N", title=None),
            y=alt.Y("ACT_DELTA_1M:Q", title="Δ Activity (1M)"),
            color=alt.Color("RATES_DIR:N",
                            scale=alt.Scale(domain=["HIKE","HOLD","CUT"],
                                            range=["#e74c3c","#95a5a6","#27ae60"]),
                            legend=None)
        ).properties(height=320)
        st.altair_chart(chartC, use_container_width=True)
        st.markdown(
            """
            <div style="margin-top:6px;padding:0.6em 1em;border-left:4px solid #888;background:#f9f9f9;border-radius:8px;">
              <strong>Insight.</strong> Where do monthly activity gains cluster—during <em>HOLD</em> or <em>CUT</em> regimes?
              If <em>HIKE</em> months skew negative, policy headwinds likely dampen usage.
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # ======================
    # 8D — Did Activity Lead Price? (ΔActivity → next-month ΔPrice)
    # ======================
    if "ETH_PRICE" in panel.columns and panel["ETH_PRICE"].notna().any():
        dfp = panel[["MONTH","ACTIVITY_INDEX","ETH_PRICE"]].dropna().copy()
        dfp["RET_1M"] = dfp["ETH_PRICE"].pct_change()
        dfp["DACT_1M"] = dfp["ACTIVITY_INDEX"].diff()
        # lead price by 1 month vs current ΔActivity
        dfp["RET_FWD_1M"] = dfp["RET_1M"].shift(-1)
        scat2 = dfp.dropna(subset=["DACT_1M","RET_FWD_1M"])
        chartD = alt.Chart(scat2).mark_circle(opacity=0.8).encode(
            x=alt.X("DACT_1M:Q", title="Δ Activity (1M)"),
            y=alt.Y("RET_FWD_1M:Q", title="ETH Return Next 1M", axis=alt.Axis(format="%")),
            color=alt.value("#6f42c1"),
            tooltip=[
                alt.Tooltip("MONTH:T", title="Month"),
                alt.Tooltip("DACT_1M:Q", title="Δ Activity", format=",.2f"),
                alt.Tooltip("RET_FWD_1M:Q", title="Return (next 1M)", format=".1%"),
            ]
        )
        trend2 = alt.Chart(scat2).transform_regression("DACT_1M","RET_FWD_1M").mark_line(color="#ff7f0e")
        st.altair_chart((scat2 and (scat2.shape[0] > 1) and (scat2.assign(dummy=1)) and (chartD + trend2)).properties(height=360), use_container_width=True)
        st.markdown(
            """
            <div style="margin-top:6px;padding:0.6em 1em;border-left:4px solid #888;background:#f9f9f9;border-radius:8px;">
              <strong>Insight.</strong> A positive slope suggests that stronger activity tends to precede positive price
              momentum the following month—evidence of <em>usage → value</em> transmission.
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.info("8D needs ETH_PRICE in eth_price.csv.")


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


























