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

# ======================================================================
# 8. Activity Drivers — Fees, ETF Flows & Rates Direction
# ======================================================================

import os
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ---------- helpers ----------
# --- Flexible CSV loader: auto-detect delimiter & normalize dates ---
def read_csv_flex(path: str) -> pd.DataFrame:
    """
    Robust CSV reader that auto-detects delimiter (',' vs ';') and returns a DataFrame.
    """
    # Detect delimiter from a small sample
    with open(path, "rb") as fh:
        sample = fh.read(4096).decode("utf-8", errors="ignore")
    sep = ";" if sample.count(";") > sample.count(",") else ","
    # Read with detected separator
    return pd.read_csv(path, sep=sep)

def to_month_start(s: pd.Series) -> pd.Series:
    """
    Convert a date-like Series to month start (tz-naive).
    Accepts strings or datetime-like values.
    """
    dt = pd.to_datetime(s, errors="coerce", utc=False)
    return dt.dt.to_period("M").dt.to_timestamp()  # month start, tz-naive

def month_start(dt_series: pd.Series) -> pd.Series:
    """Coerce to tz-naive month-start timestamps safely (no 'MS' freq)."""
    s = pd.to_datetime(dt_series, errors="coerce", utc=True)
    s = s.dt.tz_convert("UTC").dt.tz_localize(None)
    # snap to month (numpy) then back to ns
    s = s.values.astype("datetime64[M]").astype("datetime64[ns]")
    return pd.to_datetime(s)

def kpi_inline(label: str, value: str, sub: str = ""):
    # assumes you already have a KPI helper; fallback simple renderer:
    try:
        _ = kpi  # if your app has kpi()
        kpi(label, value, subtext=sub)
    except NameError:
        st.markdown(
            f"""
            <div style="display:inline-block;padding:10px 14px;margin-right:10px;border-left:6px solid #3b82f6;background:#f1f5f9;border-radius:10px;">
              <div style="font-size:12px;color:#334155;">{label}</div>
              <div style="font-size:20px;font-weight:700;color:#0f172a;">{value}</div>
              <div style="font-size:12px;color:#475569;">{sub}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

def insight(txt: str):
    st.markdown(
        f"""
        <div style="background:#eef2ff;border:1px solid #c7d2fe;padding:12px 14px;border-radius:12px;margin-top:8px;">
          <strong>Insight.</strong> {txt}
        </div>
        """,
        unsafe_allow_html=True,
    )

# =========================
# SECTION 8 DATA LOADING
# =========================
# Paths
data_dir = os.path.join(BASE_DIR, "data")
etf_path      = os.path.join(data_dir, "etf_flows.csv")
rates_path    = os.path.join(data_dir, "rates_expectations.csv")
fed_hist_path = os.path.join(data_dir, "fedfunds_history.csv")  # the file we generated/downloaded

# --- Load ETF flows (semicolon-safe) ---
df_etf_raw = pd.DataFrame()
if os.path.exists(etf_path):
    df_etf_raw = read_csv_flex(etf_path)

df_etf = pd.DataFrame()
if not df_etf_raw.empty:
    # Accept either 'MONTH' or any date-like column; keep only net flow column
    month_col = None
    for c in df_etf_raw.columns:
        cu = c.strip().upper()
        if cu in ("MONTH", "DATE", "DAY"):
            month_col = c
            break
    val_col = None
    for c in df_etf_raw.columns:
        cu = c.strip().upper()
        if cu in ("ETF_NET_FLOW_USD_MILLIONS", "NET_FLOW_USD_MILLIONS", "NET_FLOWS_USD_MILLIONS"):
            val_col = c
            break

    if month_col and val_col:
        tmp = df_etf_raw[[month_col, val_col]].copy()
        tmp["MONTH"] = to_month_start(tmp[month_col])
        tmp["ETF_NET_FLOW_M"] = pd.to_numeric(tmp[val_col], errors="coerce")
        df_etf = tmp[["MONTH", "ETF_NET_FLOW_M"]].dropna(subset=["MONTH"])

# --- Load rates expectations (semicolon-safe) ---
df_rates_raw = pd.DataFrame()
if os.path.exists(rates_path):
    df_rates_raw = read_csv_flex(rates_path)

df_rates = pd.DataFrame()
if not df_rates_raw.empty:
    # Expected cols: DATE, LOWER_BPS, UPPER_BPS, PROB
    col_map = {}
    for c in df_rates_raw.columns:
        cu = c.strip().upper()
        if cu in ("DATE", "DAY", "MONTH") and "DATE" not in col_map:
            col_map["DATE"] = c
        elif cu in ("LOWER_BPS", "LOWER_BOUND_BPS", "LOWER") and "LOWER_BPS" not in col_map:
            col_map["LOWER_BPS"] = c
        elif cu in ("UPPER_BPS", "UPPER_BOUND_BPS", "UPPER") and "UPPER_BPS" not in col_map:
            col_map["UPPER_BPS"] = c
        elif cu in ("PROB", "PROBABILITY", "PCT") and "PROB" not in col_map:
            col_map["PROB"] = c

    needed = {"DATE", "LOWER_BPS", "UPPER_BPS", "PROB"}
    if needed.issubset(col_map.keys()):
        tmp = df_rates_raw[[col_map["DATE"], col_map["LOWER_BPS"], col_map["UPPER_BPS"], col_map["PROB"]]].copy()
        tmp.rename(columns={
            col_map["DATE"]: "DATE",
            col_map["LOWER_BPS"]: "LOWER_BPS",
            col_map["UPPER_BPS"]: "UPPER_BPS",
            col_map["PROB"]: "PROB"
        }, inplace=True)
        tmp["MONTH"] = to_month_start(tmp["DATE"])
        tmp["LOWER_BPS"] = pd.to_numeric(tmp["LOWER_BPS"], errors="coerce")
        tmp["UPPER_BPS"] = pd.to_numeric(tmp["UPPER_BPS"], errors="coerce")
        tmp["PROB"] = pd.to_numeric(tmp["PROB"], errors="coerce")
        # choose mode bucket (highest probability) per MONTH
        tmp = tmp.sort_values(["MONTH", "PROB"], ascending=[True, False])
        df_rates = tmp.loc[tmp.groupby("MONTH")["PROB"].idxmax()].reset_index(drop=True)

# --- Load fed funds history (semicolon-safe) ---
fed_hist = pd.DataFrame()
if os.path.exists(fed_hist_path):
    fed_hist = read_csv_flex(fed_hist_path)
    if set(["observation_date", "FEDFUNDS"]).issubset(set(fed_hist.columns)):
        fed_hist["MONTH"] = to_month_start(fed_hist["observation_date"])
        fed_hist["FEDFUNDS"] = pd.to_numeric(fed_hist["FEDFUNDS"], errors="coerce")
        fed_hist = fed_hist[["MONTH", "FEDFUNDS"]]

# --- Compose a merged panel (optional, if you like joining) ---
pieces = []
if not df_etf.empty:
    pieces.append(df_etf)
if not df_rates.empty:
    pieces.append(df_rates[["MONTH", "LOWER_BPS", "UPPER_BPS", "PROB"]])
if not fed_hist.empty:
    pieces.append(fed_hist)

panel8 = None
for d in pieces:
    panel8 = d if panel8 is None else panel8.merge(d, on="MONTH", how="outer")

    # ---------- KPIs ----------
    latest = panel["MONTH"].max()
    rowL   = panel.loc[panel["MONTH"]==latest].tail(1).squeeze()

    act_kpi  = f"{rowL['ACTIVITY_INDEX']:.2f}" if pd.notna(rowL.get("ACTIVITY_INDEX")) else "—"
    fee_kpi  = f"{rowL['AVG_TX_FEE_USD']:.2f}"  if pd.notna(rowL.get("AVG_TX_FEE_USD"))  else "—"
    etf_kpi  = f"{rowL['ETF_NET_FLOW_USD_MILLIONS']:.1f}M" if pd.notna(rowL.get("ETF_NET_FLOW_USD_MILLIONS")) else "—"
    dir_lbl  = str(rowL.get("DIRECTION")) if pd.notna(rowL.get("DIRECTION")) else "—"
    dir_p    = rowL.get("MODE_PROB")
    dir_sub  = f"{dir_lbl} ({dir_p:.0%})" if pd.notna(dir_p) else dir_lbl

    draw_section("8. Activity Drivers — Fees, ETF Flows & Rates Direction",
                 "Relates **transaction costs**, **ETF net flows** and **policy direction** to Ethereum’s on-chain activity. Rates direction is inferred via the **most probable bucket** vs each month’s Fed Funds level.")
    cols = st.columns(4)
    with cols[0]: kpi_inline("Activity Index (latest):", act_kpi)
    with cols[1]: kpi_inline("Avg Tx Fee (USD):",      fee_kpi)
    with cols[2]: kpi_inline("ETF Net Flow:",          etf_kpi)
    with cols[3]: kpi_inline("Fed Direction (mode):",  dir_sub)

    # ---------- main chart (Activity + Fees; secondary axis: ETF flow; shaded tiny bars: rates direction mode*prob) ----------
    plot_df = panel.copy()
    # numeric safety
    for c in ["ACTIVITY_INDEX","AVG_TX_FEE_USD","ETF_NET_FLOW_USD_MILLIONS","SIGN","MODE_PROB"]:
        if c in plot_df: plot_df[c] = pd.to_numeric(plot_df[c], errors="coerce")

    # small area for direction signal (so it's visible but unobtrusive)
    if {"SIGN","MODE_PROB"}.issubset(plot_df.columns):
        plot_df["RATES_WEIGHTED"] = plot_df["SIGN"].fillna(0) * plot_df["MODE_PROB"].fillna(0)
    else:
        plot_df["RATES_WEIGHTED"] = np.nan

    fig = go.Figure()
    if "ACTIVITY_INDEX" in plot_df:
        fig.add_trace(go.Scatter(
            x=plot_df["MONTH"], y=plot_df["ACTIVITY_INDEX"], mode="lines+markers",
            name="Activity Index", line=dict(width=3)
        ))
    if "AVG_TX_FEE_USD" in plot_df:
        fig.add_trace(go.Scatter(
            x=plot_df["MONTH"], y=plot_df["AVG_TX_FEE_USD"], mode="lines",
            name="Avg Tx Fee (USD)", line=dict(dash="dot", width=2), yaxis="y2"
        ))
    if "ETF_NET_FLOW_USD_MILLIONS" in plot_df:
        fig.add_trace(go.Bar(
            x=plot_df["MONTH"], y=plot_df["ETF_NET_FLOW_USD_MILLIONS"],
            name="ETF Net Flow (M)", opacity=0.25, yaxis="y2"
        ))
    if "RATES_WEIGHTED" in plot_df:
        fig.add_trace(go.Scatter(
            x=plot_df["MONTH"], y=plot_df["RATES_WEIGHTED"],
            name="Rates Direction (weighted)", fill="tozeroy",
            line=dict(width=0), hovertemplate="%{y:.2f}<extra></extra>", yaxis="y2",
            opacity=0.25
        ))

    fig.update_layout(
        height=420, margin=dict(l=10,r=10,t=30,b=10),
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, x=0),
        xaxis=dict(title=None),
        yaxis=dict(title="Activity Index"),
        yaxis2=dict(title="Fees (USD) / ETF Net Flow (M)", overlaying="y", side="right")
    )
    st.plotly_chart(fig, use_container_width=True)

    # ---------- Rolling 6M Spearman correlations ----------
    corr_df = pd.DataFrame()
    if "ACTIVITY_INDEX" in panel.columns:
        base = panel.set_index("MONTH").sort_index()
        def spearman_roll(a, b, win=6):
            out, idx = [], []
            for i in range(len(base)):
                sub = base.iloc[max(0, i-win+1):i+1]
                if a in sub and b in sub and sub[a].notna().sum() >= 3 and sub[b].notna().sum() >= 3:
                    out.append(sub[[a,b]].corr(method="spearman").iloc[0,1])
                else:
                    out.append(np.nan)
                idx.append(base.index[i])
            return pd.Series(out, index=idx)

        if "ETF_NET_FLOW_USD_MILLIONS" in base:
            corr_df["ρ(Activity, ETF)"]  = spearman_roll("ACTIVITY_INDEX", "ETF_NET_FLOW_USD_MILLIONS", 6)
        if "AVG_TX_FEE_USD" in base:
            corr_df["ρ(Activity, Fees)"] = spearman_roll("ACTIVITY_INDEX", "AVG_TX_FEE_USD", 6)

        if not corr_df.empty:
            figc = px.line(
                corr_df.reset_index().melt(id_vars="MONTH", var_name="Pair", value_name="Spearman ρ"),
                x="MONTH", y="Spearman ρ", color="Pair", title="Rolling 6-Month Correlation with Activity"
            )
            figc.update_layout(height=300, margin=dict(l=10,r=10,t=36,b=10),
                               legend=dict(orientation="h", yanchor="bottom", y=-0.25, x=0))
            st.plotly_chart(figc, use_container_width=True)

    # ---------- Insight ----------
    notes = []
    if not corr_df.empty:
        if "ρ(Activity, ETF)" in corr_df and corr_df["ρ(Activity, ETF)"].notna().any():
            notes.append(f"Latest ρ(Activity↔ETF) ≈ **{corr_df['ρ(Activity, ETF)'].dropna().iloc[-1]:.2f}**")
        if "ρ(Activity, Fees)" in corr_df and corr_df["ρ(Activity, Fees)"].notna().any():
            notes.append(f"Latest ρ(Activity↔Fees) ≈ **{corr_df['ρ(Activity, Fees)'].dropna().iloc[-1]:.2f}**")
    if "DIRECTION" in panel.columns and panel["DIRECTION"].notna().any():
        d = panel.loc[panel["MONTH"]==latest, "DIRECTION"]
        if not d.empty:
            notes.append(f"Rates mode most recently indicates **{d.iloc[0]}**.")
    if notes:
        insight(" • ".join(notes))

# -----------------------------------------------------------
# Footer
# -----------------------------------------------------------
st.markdown('<div class="sep"></div>', unsafe_allow_html=True)
st.caption("Built by Adrià Parcerisas • Data via Flipside/Dune exports • Code quality and metric selection optimized for panel discussion.")













