# app.py — Ethereum Capital Flows & User Dynamics Dashboard

import os, re, math
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ---------- Page ----------
st.set_page_config(
    page_title="Ethereum Capital Flows & User Dynamics",
    layout="wide",
    page_icon="🧠",
)

# ---------- Styles ----------
st.markdown("""
<style>
:root{
  --bg:#0d1b2a; --card:#1b263b; --subcard:#24344e; --ink:#e6edf3; --muted:#94a3b8;
  --accent:#5eead4; --green:#22c55e; --red:#ef4444; --blue:#60a5fa; --amber:#f59e0b;
  --violet:#a78bfa; --teal:#2dd4bf; --rose:#fb7185; --cyan:#22d3ee;
}
html,body,[class*="css"] { color: var(--ink); background: var(--bg); }
.block { background: var(--card); border: 1px solid #0b1220; border-radius: 14px; padding: 16px 18px; }
.title { font-size: 2.1rem; font-weight: 800; margin: 0 0 .5rem 0; }
.lead  { color: var(--muted); margin-bottom: .8rem; }
.kpi { background: var(--subcard); border: 1px solid #0b1220; border-radius: 12px; padding: 10px 14px; }
.kpi .lbl { color: var(--muted); font-size: .95rem; }
.kpi .val { font-weight: 800; font-size: 1.35rem; }
.kpi.a { border-left: 6px solid var(--cyan); }
.kpi.b { border-left: 6px solid var(--amber); }
.kpi.c { border-left: 6px solid var(--green); }
.kpi.d { border-left: 6px solid var(--violet); }
.hr { height: 1px; background: #0b1220; margin: 18px 0; }
.badge { display:inline-block; padding:2px 8px; border-radius:999px; background:#0b1220; color:var(--muted); font-size:.8rem; }
.insight { background:var(--subcard); border:1px solid #0b1220; border-radius:12px; padding:12px 14px; color: var(--muted); }
a, .stMarkdown a { color: var(--accent) !important; text-decoration: none; }
</style>
""", unsafe_allow_html=True)

# ---------- Helpers ----------
DATA_DIR = "data"

@st.cache_data(show_spinner=False)
def load_csv(name: str) -> pd.DataFrame:
    p = os.path.join(DATA_DIR, name)
    if not os.path.exists(p):
        return pd.DataFrame()
    try:
        df = pd.read_csv(p, sep=None, engine="python")
    except Exception:
        df = pd.read_csv(p)
    df.columns = [c.strip().lstrip("\ufeff") for c in df.columns]
    if "MONTH" in df.columns:
        try: df["MONTH"] = pd.to_datetime(df["MONTH"])
        except: pass
    return df

def kpi(col, label, value, variant="a"):
    with col:
        st.markdown(f"""
        <div class="kpi {variant}"><div class="lbl">{label}</div>
        <div class="val">{value}</div></div>""", unsafe_allow_html=True)

def money(v, digits=2):
    try:
        return f"${float(v):,.{digits}f}"
    except:
        return "—"

def pct(v, digits=1):
    try:
        return f"{float(v):.{digits}f}%"
    except:
        return "—"

def corr(a, b):
    a = pd.to_numeric(a, errors="coerce")
    b = pd.to_numeric(b, errors="coerce")
    ok = a.notna() & b.notna()
    if ok.sum() < 2: return np.nan
    return np.corrcoef(a[ok], b[ok])[0,1]

def section(title, subtitle):
    st.markdown(f'<div class="title">{title}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="lead"><strong>Definition.</strong> {subtitle}</div>', unsafe_allow_html=True)

def insight(txt):
    st.markdown(f'<div class="insight">{txt}</div>', unsafe_allow_html=True)

st.markdown('<div class="title">Ethereum Capital Flows & User Dynamics Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="lead">Data as of latest available month</div>', unsafe_allow_html=True)

# Executive summary (3 paragraphs; you can edit freely)
st.markdown("""
<div class="block">
  <div style="font-weight:800;margin-bottom:.4rem">Executive Summary: Assessing Ethereum’s Traction</div>
  <div class="lead">
    This dashboard presents a comprehensive analysis of Ethereum’s on-chain activity, offering critical insights into capital flows and user engagement.
    By tracking metrics across DeFi, bridges, and fees, it provides a sophisticated perspective for crypto-savvy readers to evaluate Ethereum’s overall market
    traction, economic vitality, and evolving user base. All metrics are derived from canonical datasets to ensure reliability for decision-making.
  </div>
  <div class="lead">
    August set a new all-time high for on-chain volume at <strong>$341B</strong>, eclipsing the previous 2021 peak. The surge coincided with stronger corporate
    treasury accumulation, higher spot ETH ETF trading, and lower average fees, enabling heavier throughput. In parallel, protocols executed buybacks
    (~$46M in late August, with Hyperliquid ≈$25M). While buybacks can stabilize prices during volatility, their long-run efficacy depends on fundamentals
    and sustained revenue.
  </div>
  <div class="lead">
    The following sections track capital allocation, user dynamics, and execution costs. We highlight the mix of organic demand and macro tailwinds,
    with special attention to fee-sensitive adoption and to segments where capital is accumulating (DEXs, lending, bridges).
  </div>
</div>
<div class="hr"></div>
""", unsafe_allow_html=True)

# ======================================================
# 1) Monthly On-Chain USD Volume by Category (Stacked)  |
# ======================================================
section("1. Monthly On-Chain USD Volume by Category",
        "Stacked area by vertical. Peak volume and DEX dominance help quantify capital concentration.")
df_volcat = load_csv("volume_category.csv")
if not df_volcat.empty and all(c in df_volcat.columns for c in ["MONTH","CATEGORY","VOLUME_USD_BILLIONS"]):
    # KPIs
    monthly_tot = df_volcat.groupby("MONTH")["VOLUME_USD_BILLIONS"].sum()
    peak_vol = monthly_tot.max()
    latest = df_volcat["MONTH"].max()
    latest_month = df_volcat[df_volcat["MONTH"]==latest]
    dex_share = np.nan
    if "DEX" in latest_month["CATEGORY"].unique():
        dex_share = (latest_month.loc[latest_month["CATEGORY"]=="DEX","VOLUME_USD_BILLIONS"].sum() /
                     max(latest_month["VOLUME_USD_BILLIONS"].sum(),1)) * 100

    c1,c2 = st.columns(2)
    kpi(c1, "Peak Volume", money(peak_vol*1e9,0), "a")
    kpi(c2, "DEX Dominance", pct(dex_share,1), "b")

    fig = px.area(df_volcat.sort_values("MONTH"),
                  x="MONTH", y="VOLUME_USD_BILLIONS", color="CATEGORY",
                  title="Monthly On-Chain USD Volume by Category",
                  labels={"VOLUME_USD_BILLIONS":"Volume (USD Billions)","MONTH":"Month"})
    st.plotly_chart(fig, use_container_width=True, theme=None)
    insight("DeFi lending and DEX trading consistently drive most monthly on-chain volume. "
            "Peaks cluster around macro catalysts and fee drawdowns, amplifying throughput.")
else:
    st.info("`data/volume_category.csv` missing required columns.")

st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

# ======================================================
# 2) Monthly Active Addresses and Transactions by Category
# ======================================================
section("2. Monthly Active Addresses and Transactions by Category",
        "Dual-axis panel: active addresses (left) and transactions (right), split by category.")
df_act = load_csv("active_addresses.csv")
if not df_act.empty and all(c in df_act.columns for c in ["MONTH","CATEGORY","ACTIVE_ADDRESSES","TRANSACTIONS"]):
    # KPIs
    peak_users = df_act.groupby("MONTH")["ACTIVE_ADDRESSES"].sum().max()
    dau_tx_ratio = (df_act.groupby("MONTH")["TRANSACTIONS"].sum() /
                    df_act.groupby("MONTH")["ACTIVE_ADDRESSES"].sum()).iloc[-1]
    c1,c2 = st.columns(2)
    kpi(c1, "Peak Users (all categories)", f"{int(peak_users):,}", "c")
    kpi(c2, "Tx / Active Address (latest)", f"{dau_tx_ratio:.2f}", "d")

    # pivot by category
    addr_piv = df_act.pivot_table(index="MONTH", columns="CATEGORY", values="ACTIVE_ADDRESSES", aggfunc="sum")
    tx_piv   = df_act.pivot_table(index="MONTH", columns="CATEGORY", values="TRANSACTIONS", aggfunc="sum")

    fig = go.Figure()
    # left axis: addresses
    for col in addr_piv.columns:
        fig.add_trace(go.Scatter(x=addr_piv.index, y=addr_piv[col], name=f"{col} (Addresses)", line=dict(width=2)))
    # right axis: transactions
    for col in tx_piv.columns:
        fig.add_trace(go.Scatter(x=tx_piv.index, y=tx_piv[col], name=f"{col} (Tx)", yaxis="y2", line=dict(dash="dot")))
    fig.update_layout(
        hovermode="x unified",
        xaxis_title="Month",
        yaxis=dict(title="Active Addresses"),
        yaxis2=dict(title="Transactions", overlaying="y", side="right"),
        legend=dict(orientation="h")
    )
    st.plotly_chart(fig, use_container_width=True)
    insight("DEX users dominate address and transaction activity; lending and bridging remain steady contributors.")
else:
    st.info("`data/active_addresses.csv` missing required columns.")

st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

# ======================================================
# 3) User Cohorts by Monthly USD Volume
# ======================================================
section("3. User Cohorts by Monthly USD Volume",
        "Segments (e.g., Whales, Large, Medium, Small). Shows distribution of monthly on-chain volume by cohort.")
df_coh = load_csv("user_cohort.csv")
if not df_coh.empty and all(c in df_coh.columns for c in ["MONTH","COHORT","UNIQUE_USERS","TOTAL_VOLUME"]):
    # KPIs: whale avg vol & whale share latest
    last_month = df_coh["MONTH"].max()
    whales = df_coh[(df_coh["MONTH"]==last_month) & (df_coh["COHORT"].str.contains("Whale", case=False, na=False))]
    whale_avg = (whales["TOTAL_VOLUME"].sum() / max(whales["UNIQUE_USERS"].sum(),1)) if not whales.empty else np.nan
    month_tot = df_coh[df_coh["MONTH"]==last_month]["TOTAL_VOLUME"].sum()
    whale_share = (whales["TOTAL_VOLUME"].sum()/month_tot*100) if month_tot else np.nan

    c1,c2 = st.columns(2)
    kpi(c1, "Whale Avg Vol", money(whale_avg,0), "a")
    kpi(c2, "Whale Vol Share (latest)", pct(whale_share,1), "b")

    # area by cohort
    df_area = df_coh.copy()
    df_area["TOTAL_VOLUME_B"] = df_area["TOTAL_VOLUME"] / 1e9
    fig = px.area(df_area.sort_values("MONTH"), x="MONTH", y="TOTAL_VOLUME_B",
                  color="COHORT", labels={"TOTAL_VOLUME_B":"Total Volume (USD Billions)"})
    st.plotly_chart(fig, use_container_width=True)
    insight("Whale cohort drives a disproportionate share of total volume; retail remains broad but lower ticket.")
else:
    st.info("`data/user_cohort.csv` missing required columns.")

st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

# ======================================================
# 4) User Typology — 100% Stacked Users by Activity Level & Sector
# ======================================================
section("4. User Typology: Unique Users by Activity Level & Sector (100% Stacked)",
        "Share of multi-sector vs single-sector users by month; engagement via avg transactions per user.")
df_typ = load_csv("user_typology.csv")
if not df_typ.empty and all(c in df_typ.columns for c in ["MONTH","USER_TYPE","ACTIVITY_LEVEL","UNIQUE_USERS","AVG_TRANSACTIONS_PER_USER"]):
    # compute shares per month
    typ = df_typ.groupby(["MONTH","USER_TYPE"], as_index=False)["UNIQUE_USERS"].sum()
    typ["share"] = typ.groupby("MONTH")["UNIQUE_USERS"].apply(lambda s: s / s.sum() * 100)

    # KPI: multi-sector share latest; engagement multiplier (multi vs single)
    latest = typ["MONTH"].max()
    multi_share = typ[(typ["MONTH"]==latest) & (typ["USER_TYPE"].str.contains("multi", case=False))]["share"].sum()
    eng = df_typ.groupby("USER_TYPE")["AVG_TRANSACTIONS_PER_USER"].mean()
    if not eng.empty and eng.index.str.contains("multi", case=False).any() and eng.index.str.contains("single", case=False).any():
        engagement_mult = eng[eng.index.str.contains("multi", case=False)].mean() / max(eng[eng.index.str.contains("single", case=False)].mean(), 1e-9)
    else:
        engagement_mult = np.nan

    c1,c2 = st.columns(2)
    kpi(c1, "Multi-Sector Users (latest)", pct(multi_share,1), "c")
    kpi(c2, "Engagement Multiplier (Multi/Single)", f"{engagement_mult:.2f}×" if not math.isnan(engagement_mult) else "—", "d")

    # 100% stacked
    fig = px.bar(typ.sort_values("MONTH"), x="MONTH", y="share", color="USER_TYPE",
                 title="User Typology — Share of Users",
                 labels={"share":"% of Users"})
    fig.update_layout(barmode="stack")
    st.plotly_chart(fig, use_container_width=True)
    insight("Multi-sector users, though fewer, typically show higher engagement (tx/user), indicating deeper ecosystem usage.")
else:
    st.info("`data/user_typology.csv` missing required columns.")

st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

# ======================================================
# 5) DEX Volume and Active Swappers (Monthly)
# ======================================================
section("5. DEX Volume and Active Swappers (Monthly)",
        "Tracks DEX capital (USD) and active swappers (addresses).")
df_dex = load_csv("dex_volume.csv")
if not df_dex.empty and all(c in df_dex.columns for c in ["MONTH","ACTIVE_SWAPPERS","TOTAL_VOLUME_BILLIONS"]):
    # KPIs
    peak_dex = df_dex["TOTAL_VOLUME_BILLIONS"].max()
    # simple growth: first vs last month users/volume
    users_growth = (df_dex["ACTIVE_SWAPPERS"].iloc[-1] - df_dex["ACTIVE_SWAPPERS"].iloc[0]) / max(df_dex["ACTIVE_SWAPPERS"].iloc[0],1) * 100
    volume_growth = (df_dex["TOTAL_VOLUME_BILLIONS"].iloc[-1] - df_dex["TOTAL_VOLUME_BILLIONS"].iloc[0]) / max(df_dex["TOTAL_VOLUME_BILLIONS"].iloc[0],1) * 100

    c1,c2 = st.columns(2)
    kpi(c1, "Peak DEX Volume", money(peak_dex*1e9,0), "a")
    kpi(c2, "Users Growth / Vol Growth", f"{users_growth:.1f}% / {volume_growth:.1f}%", "b")

    fig = go.Figure()
    fig.add_trace(go.Bar(x=df_dex["MONTH"], y=df_dex["TOTAL_VOLUME_BILLIONS"], name="DEX Volume (B USD)",
                         marker_color="#fb7185"))
    fig.add_trace(go.Scatter(x=df_dex["MONTH"], y=df_dex["ACTIVE_SWAPPERS"], name="Active Swappers",
                             yaxis="y2", line=dict(color="#22d3ee", width=3)))
    fig.update_layout(
        hovermode="x unified",
        xaxis_title="Month",
        yaxis=dict(title="DEX Volume (USD Billions)"),
        yaxis2=dict(title="Active Swappers", overlaying="y", side="right"),
        legend=dict(orientation="h")
    )
    st.plotly_chart(fig, use_container_width=True)
    insight("Active swappers trend resilient with rising volumes through 2025, suggesting durable DEX product-market fit.")
else:
    st.info("`data/dex_volume.csv` missing required columns.")

st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

# ======================================================
# 6) Lending Deposits — Evolution per Platform
# ======================================================
section("6. Lending Deposits — Evolution per Platform",
        "Stacked deposits by platform; depositor count provides adoption depth.")
df_lend = load_csv("lending_deposits.csv")
if not df_lend.empty and all(c in df_lend.columns for c in ["MONTH","PLATFORM","VOLUME_BILLIONS","UNIQUE_DEPOSITORS"]):
    latest = df_lend["MONTH"].max()
    latest_slice = df_lend[df_lend["MONTH"]==latest]
    top_plat = latest_slice.groupby("PLATFORM")["VOLUME_BILLIONS"].sum().sort_values(ascending=False).head(1)
    top_name = top_plat.index[0] if len(top_plat)>0 else "—"
    top_share = float(top_plat.iloc[0]/max(latest_slice["VOLUME_BILLIONS"].sum(),1)*100) if len(top_plat)>0 else np.nan

    # depositor growth overall
    dep_growth = (df_lend.groupby("MONTH")["UNIQUE_DEPOSITORS"].sum().iloc[-1] -
                  df_lend.groupby("MONTH")["UNIQUE_DEPOSITORS"].sum().iloc[0])
    c1,c2 = st.columns(2)
    kpi(c1, "Top Platform Share (latest)", pct(top_share,1), "c")
    kpi(c2, "Depositors Growth (Δ)", f"{int(dep_growth):,}", "d")

    fig = px.area(df_lend.sort_values("MONTH"), x="MONTH", y="VOLUME_BILLIONS",
                  color="PLATFORM", labels={"VOLUME_BILLIONS":"Deposit Volume (USD Billions)"})
    st.plotly_chart(fig, use_container_width=True)
    insight(f"{top_name} leads current deposit share; depositor counts have {'risen' if dep_growth>=0 else 'fallen'} since the sample start.")
else:
    st.info("`data/lending_deposits.csv` missing required columns.")

st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

# ======================================================
# 7) Total Bridge Volume (Monthly)
# ======================================================
section("7. Total Bridge Volume (Monthly)",
        "Bridge activity gauges cross-chain demand; rising totals indicate growing interconnectedness.")
df_bridge = load_csv("bridged_volume.csv")
if not df_bridge.empty and all(c in df_bridge.columns for c in ["MONTH","TOTAL_BRIDGE_VOLUME_BILLIONS"]):
    growth = (df_bridge["TOTAL_BRIDGE_VOLUME_BILLIONS"].iloc[-1] /
              max(df_bridge["TOTAL_BRIDGE_VOLUME_BILLIONS"].iloc[0],1) - 1) * 100
    status = "Emerging Cross-Chain Hub" if growth > 200 else "Stable Interchange"
    c1,c2 = st.columns(2)
    kpi(c1, "Bridge Volume Growth", pct(growth,1), "a")
    kpi(c2, "Status", status, "b")

    fig = px.line(df_bridge.sort_values("MONTH"), x="MONTH", y="TOTAL_BRIDGE_VOLUME_BILLIONS",
                  labels={"TOTAL_BRIDGE_VOLUME_BILLIONS":"Total Bridge Volume (USD Billions)"})
    st.plotly_chart(fig, use_container_width=True)
    insight("Aggregate bridging has expanded materially since 2023, reinforcing Ethereum’s role as a liquidity hub.")
else:
    st.info("`data/bridged_volume.csv` missing required columns.")

st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

# ======================================================
# 8) ETH Price Overlay with Total Activity
# ======================================================
section("8. ETH Price Overlay with Total Activity",
        "Two-axis overlay of ETH price and a composite Activity Index.")
df_price = load_csv("eth_price.csv")
if not df_price.empty and all(c in df_price.columns for c in ["MONTH","AVG_ETH_PRICE_USD","ACTIVITY_INDEX"]):
    price_range = (df_price["AVG_ETH_PRICE_USD"].min(), df_price["AVG_ETH_PRICE_USD"].max())
    r = corr(df_price["AVG_ETH_PRICE_USD"], df_price["ACTIVITY_INDEX"])
    c1,c2 = st.columns(2)
    kpi(c1, "Price Range", f"{money(price_range[0],0)} – {money(price_range[1],0)}", "c")
    kpi(c2, "Corr(Price, Activity)", f"{r:.2f}" if not math.isnan(r) else "—", "d")

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_price["MONTH"], y=df_price["AVG_ETH_PRICE_USD"], name="ETH Price (USD)",
                             line=dict(color="#60a5fa", width=3)))
    fig.add_trace(go.Scatter(x=df_price["MONTH"], y=df_price["ACTIVITY_INDEX"], name="Activity Index",
                             yaxis="y2", line=dict(color="#22c55e", width=2, dash="dot")))
    fig.update_layout(
        hovermode="x unified",
        xaxis_title="Month",
        yaxis=dict(title="ETH Price (USD)"),
        yaxis2=dict(title="Activity Index", overlaying="y", side="right"),
        legend=dict(orientation="h")
    )
    st.plotly_chart(fig, use_container_width=True)
    insight("Activity generally co-moves with price; spikes often coincide with macro catalysts and fee drawdowns.")
else:
    st.info("`data/eth_price.csv` missing required columns.")

st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

# ======================================================
# 9) User Adoption During Fee Evolution (extra)
# ======================================================
section("9. User Adoption During Fee Evolution",
        "Comparing unique users (left) with average transaction fee in USD (right); lower fees often coincide with higher adoption.")
df_fee_act = load_csv("fees_activity.csv")
if df_fee_act.empty:  # fallback to fees_price.csv if needed
    df_fee_act = load_csv("fees_price.csv").rename(columns={
        "AVG_TX_FEE_USD":"AVG_FEE_USD",
        "MONTHLY_TRANSACTIONS":"TOTAL_TRANSACTIONS",
        "TX_MILLIONS":"TRANSACTIONS_MILLIONS"
    })

if not df_fee_act.empty and "MONTH" in df_fee_act.columns:
    # try to get unique users series
    users = None
    if "USERS_MILLIONS" in df_fee_act.columns:
        users = df_fee_act["USERS_MILLIONS"] * 1e6
    elif "UNIQUE_USERS" in df_fee_act.columns:
        users = df_fee_act["UNIQUE_USERS"]
    # average fee USD
    fee_usd = df_fee_act["AVG_FEE_USD"] if "AVG_FEE_USD" in df_fee_act.columns else None

    if users is not None and fee_usd is not None:
        ug = (users.iloc[-1] - users.iloc[0]) / max(users.iloc[0],1) * 100
        # find an earlier fee series to compute decline vs first non-nan
        first_fee = fee_usd.dropna().iloc[0] if fee_usd.dropna().size else np.nan
        fd = (fee_usd.dropna().iloc[-1]/first_fee - 1) * 100 if not math.isnan(first_fee) else np.nan

        c1,c2 = st.columns(2)
        kpi(c1, "User Growth", pct(ug,1), "a")
        kpi(c2, "Fee Change", pct(fd,1), "b")

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_fee_act["MONTH"], y=users, name="Unique Users",
                                 line=dict(color="#a78bfa", width=3), mode="lines+markers",
                                 marker=dict(symbol="circle-open")))
        fig.add_trace(go.Scatter(x=df_fee_act["MONTH"], y=fee_usd, name="Average Fee (USD)",
                                 yaxis="y2", line=dict(color="#f59e0b", width=3), mode="lines+markers",
                                 marker=dict(symbol="diamond")))
        fig.update_layout(
            hovermode="x unified",
            xaxis_title="Month",
            yaxis=dict(title="Unique Users"),
            yaxis2=dict(title="Average Fee (USD)", overlaying="y", side="right"),
            legend=dict(orientation="h")
        )
        st.plotly_chart(fig, use_container_width=True)
        insight("Periods of lower average fees coincide with stronger user adoption — consistent with fee-sensitive demand.")
    else:
        st.info("Could not find `UNIQUE_USERS/USERS_MILLIONS` and `AVG_FEE_USD` in fees CSVs.")
else:
    st.info("`data/fees_activity.csv` or `data/fees_price.csv` missing `MONTH`.")

st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

# ======================================================
# 10) Correlation: ETH Price vs Avg TX Fee (scatter)
# ======================================================
section("10. Price vs Fee — Correlation",
        "Scatter of monthly ETH price vs average transaction fee; includes Pearson correlation.")
df_fp = load_csv("fees_price.csv")
if not df_fp.empty and all(c in df_fp.columns for c in ["MONTH","AVG_ETH_PRICE_USD","AVG_TX_FEE_USD"]):
    r = corr(df_fp["AVG_ETH_PRICE_USD"], df_fp["AVG_TX_FEE_USD"])
    # KPI cards
    c1,c2 = st.columns(2)
    kpi(c1, "Correlation (Price vs Fee)", f"{r:.2f}" if not math.isnan(r) else "—", "c")
    last_ratio = df_fp["PRICE_TO_FEE_RATIO"].iloc[-1] if "PRICE_TO_FEE_RATIO" in df_fp.columns else (df_fp["AVG_ETH_PRICE_USD"].iloc[-1]/max(df_fp["AVG_TX_FEE_USD"].iloc[-1],1e-9))
    kpi(c2, "Price-to-Fee Ratio (latest)", f"{last_ratio:,.2f}", "d")

    fig = px.scatter(df_fp, x="AVG_ETH_PRICE_USD", y="AVG_TX_FEE_USD",
                     trendline="ols", labels={"AVG_ETH_PRICE_USD":"ETH Price (USD)", "AVG_TX_FEE_USD":"Avg TX Fee (USD)"},
                     title="ETH Price vs Average TX Fee — Monthly")
    st.plotly_chart(fig, use_container_width=True)
    insight("Fees tend to rise with price but the relationship is not perfectly linear — L2 adoption and fee markets modulate the slope.")
else:
    st.info("`data/fees_price.csv` missing required columns.")
