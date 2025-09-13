# app.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path

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

# ===========================================================
# 8) Activity Drivers — Fees, ETF Flows & Rates Direction
# (Keep your existing "User Adoption During Fee Evolution" chart right above)
# ===========================================================
import pandas as pd, numpy as np, re
import plotly.graph_objects as go
import plotly.express as px
from io import StringIO
from pathlib import Path

# ---------- Helpers ----------
def read_csv_smart(path_rel, parse_dates=None):
    """Read CSV from data/, auto-detect ; or , separators."""
    p = Path("data") / path_rel
    if not p.exists():
        return pd.DataFrame()
    # try comma
    try:
        df = pd.read_csv(p, sep=",", parse_dates=parse_dates)
        if df.shape[1] == 1:  # likely semicolon
            df = pd.read_csv(p, sep=";", parse_dates=parse_dates)
    except Exception:
        df = pd.read_csv(p, sep=None, engine="python", parse_dates=parse_dates)
    return df

def kpi_box(col, html, style=None):
    try:
        kpi_inline(col, html, style=(style or KPI_STYLE.get("blue", {})))
    except Exception:
        col.markdown(
            f"<div style='padding:10px 12px;border-left:4px solid #2563eb;background:#f8fafc;border-radius:8px'>{html}</div>",
            unsafe_allow_html=True,
        )

def spearman_safe(x, y):
    s = pd.concat([x, y], axis=1).dropna()
    if len(s) < 3: return np.nan
    return s.corr(method="spearman").iloc[0,1]

# ---------- Load core series ----------
eth  = read_csv_smart("eth_price.csv",  parse_dates=["MONTH"])
fees = read_csv_smart("fees_price.csv", parse_dates=["MONTH"])

# ---------- ETFs: use monthly if present, otherwise derive from etf_flows.csv ----------
etf_monthly = read_csv_smart("etf_flows_monthly.csv", parse_dates=["MONTH"])
if etf_monthly.empty:
    # Try to derive monthly from etf_flows.csv (Farside-like table)
    raw = read_csv_smart("etf_flows.csv")
    if not raw.empty:
        # If it already looks monthly with MONTH + ETF_NET_FLOW_USD_MILLIONS, keep it
        if set(["MONTH"]).issubset({c.upper() for c in raw.columns}):
            # try to find the flow column
            flow_col = None
            for c in raw.columns:
                if "ETF_NET_FLOW" in c.upper():
                    flow_col = c; break
            if flow_col is not None:
                etf_monthly = raw.rename(columns={flow_col:"ETF_NET_FLOW_USD_MILLIONS"})
                # force MONTH datetime
                if "MONTH" not in etf_monthly.columns:
                    # try first col
                    first = etf_monthly.columns[0]
                    etf_monthly.rename(columns={first:"MONTH"}, inplace=True)
                etf_monthly["MONTH"] = pd.to_datetime(etf_monthly["MONTH"], errors="coerce")
                etf_monthly = etf_monthly[["MONTH","ETF_NET_FLOW_USD_MILLIONS"]].dropna(subset=["MONTH"])
        else:
            # Fallback: try to parse a wide table where row 2 has fund names, dates in one column
            # Auto-detect by re-reading with no header and semicolon
            raw2 = read_csv_smart("etf_flows.csv")
            if not raw2.empty:
                # If there is a DATE column, just aggregate by month summing numeric cols
                # (works if user provided tidy per-fund daily flows)
                date_col = None
                for c in raw2.columns:
                    if "DATE" in c.upper():
                        date_col = c; break
                if date_col:
                    df = raw2.copy()
                    df["DATE"] = pd.to_datetime(df[date_col], errors="coerce")
                    df = df.dropna(subset=["DATE"])
                    # numeric only
                    num = df.select_dtypes(include=["number"])
                    if num.shape[1] >= 1:
                        monthly = num.copy()
                        monthly["MONTH"] = df["DATE"].values.astype("datetime64[M]")
                        monthly = monthly.groupby("MONTH").sum(numeric_only=True).reset_index()
                        # sum all numeric as net flows if "Total" not explicit
                        monthly["ETF_NET_FLOW_USD_MILLIONS"] = monthly.select_dtypes(include=["number"]).sum(axis=1)
                        etf_monthly = monthly[["MONTH","ETF_NET_FLOW_USD_MILLIONS"]]

# Keep only the flow col
if not etf_monthly.empty:
    # make sure numeric
    etf_monthly["ETF_NET_FLOW_USD_MILLIONS"] = pd.to_numeric(etf_monthly.iloc[:, etf_monthly.columns.str.upper().get_indexer(["ETF_NET_FLOW_USD_MILLIONS"])[0]], errors="coerce")
    etf_monthly = etf_monthly[["MONTH","ETF_NET_FLOW_USD_MILLIONS"]].sort_values("MONTH")

# ---------- Rates: build mode-based CUT/HOLD/HIKE from expectations ----------
rates_dir = pd.DataFrame()

# Required: rates_expectations.csv (bucketed probabilities by range) 
rates_exp = read_csv_smart("rates_expectations.csv")
if not rates_exp.empty:
    # Optional: monthly Fed Funds level to classify against; if missing, fall back to constant 4.33%
    fed_hist = read_csv_smart("fedfunds_history.csv", parse_dates=["observation_date"])
    # Normalize expectations to long
    # Detect DATE column (first one)
    date_col = rates_exp.columns[0]
    # melt
    long = rates_exp.melt(id_vars=[date_col], var_name="RANGE_BPS", value_name="PROB")
    # parse date
    def parse_dt_any(s):
        for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%m/%d/%Y"):
            try: return pd.to_datetime(s, format=fmt)
            except: continue
        return pd.to_datetime(s, errors="coerce")
    long["DATE"] = long[date_col].apply(parse_dt_any)
    long = long.dropna(subset=["DATE"])
    # prob to 0..1
    def to_prob01(x):
        try:
            v = float(str(x).replace("%","").replace(",",""))
        except:
            return np.nan
        return v/100.0 if v>1.5 else v
    long["PROB"] = long["PROB"].apply(to_prob01)
    # extract bounds
    def bounds_bps(s):
        m = re.findall(r"(\d+)\s*-\s*(\d+)", str(s))
        if not m: return (np.nan, np.nan)
        a,b = map(float, m[0])
        return a,b
    lohi = long["RANGE_BPS"].apply(bounds_bps)
    long["LOWER_BPS"] = [x[0] for x in lohi]
    long["UPPER_BPS"] = [x[1] for x in lohi]
    long["MIDPOINT_BPS"] = (long["LOWER_BPS"] + long["UPPER_BPS"]) / 2.0
    long["MONTH"] = long["DATE"].values.astype("datetime64[M]")

    # attach current FedFunds per month
    if not fed_hist.empty and "observation_date" in fed_hist.columns and "FEDFUNDS" in fed_hist.columns:
        fed = fed_hist.rename(columns={"observation_date":"MONTH"})[["MONTH","FEDFUNDS"]].copy()
        fed["MONTH"] = pd.to_datetime(fed["MONTH"])
        fed["FEDFUNDS_BPS"] = fed["FEDFUNDS"] * 100.0
    else:
        # fallback constant
        fed = pd.DataFrame({"MONTH": sorted(long["MONTH"].dropna().unique()), "FEDFUNDS_BPS": 433.0})
    long = long.merge(fed[["MONTH","FEDFUNDS_BPS"]], on="MONTH", how="left")

    # classify by mode at each DATE
    MODE_THRESHOLD = 0.55
    def classify_date(df_date):
        if df_date.empty:
            return pd.Series(dtype=object)
        df_sorted = df_date.sort_values("PROB", ascending=False).reset_index(drop=True)
        top = df_sorted.iloc[0]
        top_prob = float(top["PROB"]) if pd.notna(top["PROB"]) else np.nan
        top_mid  = float(top["MIDPOINT_BPS"]) if pd.notna(top["MIDPOINT_BPS"]) else np.nan
        cur = float(df_date["FEDFUNDS_BPS"].iloc[0]) if pd.notna(df_date["FEDFUNDS_BPS"].iloc[0]) else np.nan
        second_prob = float(df_sorted.iloc[1]["PROB"]) if len(df_sorted)>1 and pd.notna(df_sorted.iloc[1]["PROB"]) else 0.0
        inside = (top["LOWER_BPS"] <= cur <= top["UPPER_BPS"]) if pd.notna(cur) else False
        raw_dir = "HOLD"
        if pd.notna(top_mid) and pd.notna(cur):
            raw_dir = "HOLD" if inside else ("CUT" if top_mid < cur else "HIKE")
        direction = "HOLD" if (pd.isna(top_prob) or top_prob < MODE_THRESHOLD) else raw_dir
        return pd.Series({
            "DIRECTION": direction,
            "MODE_PROB": top_prob,
            "CONFIDENCE": top_prob - second_prob,
            "RAW_DIRECTION": raw_dir
        })

    mode = long.groupby(["DATE","MONTH"], as_index=False).apply(classify_date).reset_index(level=0, drop=True).reset_index()
    # implied rate (informational)
    implied = (long.groupby("DATE")
                    .apply(lambda g: np.sum(g["PROB"]*g["MIDPOINT_BPS"]) if g["PROB"].sum()>0 else np.nan)
                    .rename("FFR_IMPLIED_BPS").reset_index())
    mode = mode.merge(implied, on="DATE", how="left")
    mode["FFR_IMPLIED_NEXT_3M"] = mode["FFR_IMPLIED_BPS"]/100.0

    # monthly last
    rates_dir = (mode.sort_values("DATE")
                      .groupby("MONTH")
                      .tail(1)[["MONTH","DIRECTION","MODE_PROB","CONFIDENCE","RAW_DIRECTION","FFR_IMPLIED_NEXT_3M"]]
                      .reset_index(drop=True))

# ---------- Build panel ----------
pieces = []
if not eth.empty:
    pieces.append(eth[["MONTH","ACTIVITY_INDEX","TOTAL_TRANSACTIONS","UNIQUE_USERS"]])
if not fees.empty:
    keep = [c for c in ["MONTH","AVG_TX_FEE_USD","AVG_TX_FEE_ETH","AVG_GAS_PRICE_GWEI","PRICE_TO_FEE_RATIO"] if c in fees.columns]
    pieces.append(fees[keep])
if not etf_monthly.empty:
    pieces.append(etf_monthly[["MONTH","ETF_NET_FLOW_USD_MILLIONS"]])
if not rates_dir.empty:
    # numeric direction (optional)
    rates_dir["DIRECTION_SIGN"] = rates_dir["DIRECTION"].map({"CUT":-1,"HOLD":0,"HIKE":1})
    rates_dir["DIRECTION_WEIGHTED"] = rates_dir["DIRECTION_SIGN"] * rates_dir["MODE_PROB"]
    pieces.append(rates_dir[["MONTH","DIRECTION","MODE_PROB","DIRECTION_WEIGHTED","FFR_IMPLIED_NEXT_3M"]])

panel = None
for d in pieces:
    panel = d if panel is None else panel.merge(d, on="MONTH", how="outer")
if panel is None or panel.empty:
    draw_section("8. Activity Drivers — Fees, ETF Flows & Rates Direction",
                 "Data not found. Ensure these exist under /data: eth_price.csv, fees_price.csv, etf_flows.csv (or etf_flows_monthly.csv), rates_expectations.csv (and optionally fedfunds_history.csv).")
else:
    panel = panel.sort_values("MONTH").reset_index(drop=True)

    # ---- Header ----
    draw_section(
        "8. Activity Drivers — Fees, ETF Flows & Rates Direction",
        "Relates **transaction costs**, **ETF net flows** and **policy direction** to Ethereum’s on-chain activity. The rates direction is inferred via the **most probable bucket** versus the month’s Fed Funds level."
    )

    # ---- KPIs (latest) ----
    latest = panel["MONTH"].max()
    last = panel.loc[panel["MONTH"]==latest].tail(1)

    c1,c2,c3,c4 = st.columns(4)
    if not last.empty:
        ai = last.get("ACTIVITY_INDEX", pd.Series([np.nan])).iloc[0]
        fee_usd = last.get("AVG_TX_FEE_USD", pd.Series([np.nan])).iloc[0]
        etf_m = last.get("ETF_NET_FLOW_USD_MILLIONS", pd.Series([np.nan])).iloc[0]
        dir_label = last.get("DIRECTION", pd.Series(["—"])).iloc[0]
        prob = last.get("MODE_PROB", pd.Series([np.nan])).iloc[0]

        kpi_box(c1, f"<strong>Activity Index (latest):</strong> <span class='v'>{(ai if pd.notna(ai) else 0):,.2f}</span>", style=KPI_STYLE.get("blue"))
        kpi_box(c2, f"<strong>Avg Tx Fee (USD):</strong> <span class='v'>{(fee_usd if pd.notna(fee_usd) else 0):,.2f}</span>", style=KPI_STYLE.get("teal"))
        kpi_box(c3, f"<strong>ETF Net Flow:</strong> <span class='v'>{(etf_m if pd.notna(etf_m) else 0):,.1f}M</span>", style=KPI_STYLE.get("green"))
        kpi_box(c4, f"<strong>Fed Direction (mode):</strong> <span class='v'>{dir_label}</span> {'' if pd.isna(prob) else f'({prob:.0%})'}", style=KPI_STYLE.get("violet"))

    # ---- Evolution chart ----
    fig = go.Figure()
    if "ACTIVITY_INDEX" in panel:
        fig.add_trace(go.Scatter(x=panel["MONTH"], y=panel["ACTIVITY_INDEX"],
                                 mode="lines+markers", name="Activity Index",
                                 line=dict(width=3, color="#1d4ed8")))
    if "AVG_TX_FEE_USD" in panel:
        fig.add_trace(go.Scatter(x=panel["MONTH"], y=panel["AVG_TX_FEE_USD"],
                                 mode="lines", name="Avg Tx Fee (USD)",
                                 line=dict(width=2, dash="dot", color="#0ea5e9"),
                                 yaxis="y2"))
    if "ETF_NET_FLOW_USD_MILLIONS" in panel:
        fig.add_trace(go.Bar(x=panel["MONTH"], y=panel["ETF_NET_FLOW_USD_MILLIONS"],
                             name="ETF Net Flow (M)", marker_color="#10b981",
                             opacity=0.65, yaxis="y2"))
    if "DIRECTION_WEIGHTED" in panel:
        # show as faint strip
        scale = max(1.0, np.nanmax(np.abs(panel["ETF_NET_FLOW_USD_MILLIONS"])) if "ETF_NET_FLOW_USD_MILLIONS" in panel else 1.0)
        fig.add_trace(go.Bar(x=panel["MONTH"], y=panel["DIRECTION_WEIGHTED"]*(0.15*scale),
                             name="Rates Direction (weighted)", marker_color="#7c3aed",
                             opacity=0.25, yaxis="y2"))

    fig.update_layout(
        height=460, margin=dict(l=10,r=10,t=10,b=10),
        barmode="overlay",
        yaxis=dict(title="Activity Index"),
        yaxis2=dict(title="Fees (USD) / ETF Net Flow (M)", overlaying="y", side="right"),
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, x=0)
    )
    st.plotly_chart(fig, use_container_width=True)

    # ---- Lag analysis (keep simple) ----
    st.markdown("**Lag analysis** — test if drivers lead activity (shift the driver by _k_ months).")
    lag = st.slider("Lag k (months, positive = driver leads)", min_value=-6, max_value=6, value=0, step=1, key="drivers_lag")

    lagged = panel.copy()
    if "ETF_NET_FLOW_USD_MILLIONS" in lagged: lagged["ETF_LAG"] = lagged["ETF_NET_FLOW_USD_MILLIONS"].shift(lag)
    if "AVG_TX_FEE_USD" in lagged:          lagged["FEE_LAG"] = lagged["AVG_TX_FEE_USD"].shift(lag)
    if "DIRECTION_WEIGHTED" in lagged:      lagged["RATES_LAG"] = lagged["DIRECTION_WEIGHTED"].shift(lag)

    cA, cB = st.columns(2)
    if all(c in lagged for c in ["ACTIVITY_INDEX","FEE_LAG"]):
        d = lagged[["ACTIVITY_INDEX","FEE_LAG"]].dropna()
        r = spearman_safe(d["FEE_LAG"], d["ACTIVITY_INDEX"])
        fig_s1 = px.scatter(d, x="FEE_LAG", y="ACTIVITY_INDEX",
                            title=f"Activity vs Avg Tx Fee (lag {lag}) — ρ={r:.2f}" if r==r else "Activity vs Avg Tx Fee")
        fig_s1.update_layout(height=400, margin=dict(l=10,r=10,t=40,b=10))
        cA.plotly_chart(fig_s1, use_container_width=True)

    if all(c in lagged for c in ["ACTIVITY_INDEX","ETF_LAG"]):
        d = lagged[["ACTIVITY_INDEX","ETF_LAG"]].dropna()
        r = spearman_safe(d["ETF_LAG"], d["ACTIVITY_INDEX"])
        fig_s2 = px.scatter(d, x="ETF_LAG", y="ACTIVITY_INDEX",
                            title=f"Activity vs ETF Net Flow (lag {lag}) — ρ={r:.2f}" if r==r else "Activity vs ETF Net Flow")
        fig_s2.update_layout(height=400, margin=dict(l=10,r=10,t=40,b=10))
        cB.plotly_chart(fig_s2, use_container_width=True)

    # quick caption
    bullets = []
    if 'ACTIVITY_INDEX' in panel and 'AVG_TX_FEE_USD' in panel:
        bullets.append(f"Fees corr ρ≈{spearman_safe(panel['AVG_TX_FEE_USD'], panel['ACTIVITY_INDEX']):.2f}")
    if 'ACTIVITY_INDEX' in panel and 'ETF_NET_FLOW_USD_MILLIONS' in panel:
        bullets.append(f"ETF flows corr ρ≈{spearman_safe(panel['ETF_NET_FLOW_USD_MILLIONS'], panel['ACTIVITY_INDEX']):.2f}")
    st.caption(" • ".join([b for b in bullets if "nan" not in b.lower()]))

    insight("Mode-based Fed direction, ETF net flows and fees jointly contextualize activity peaks. Try k>0 to test whether drivers lead activity.")

# -----------------------------------------------------------
# Footer
# -----------------------------------------------------------
st.markdown('<div class="sep"></div>', unsafe_allow_html=True)
st.caption("Built by Adrià Parcerisas • Data via Flipside/Dune exports • Code quality and metric selection optimized for panel discussion.")








