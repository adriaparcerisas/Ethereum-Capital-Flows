# app.py
# Ethereum Capital Flows & User Dynamics — Streamlit Dashboard
# (c) Adrià Parcerisas — built for panel-grade evaluation

import os
import io
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# -----------------------------
# Page config
# -----------------------------
st.set_page_config(
    page_title="Ethereum Capital Flows & User Dynamics",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# -----------------------------
# High-contrast theme (dark)
# -----------------------------
st.markdown("""
<style>
:root{
  --bg:#0d1b2a; --card:#16233a; --subcard:#1f2f4a; --ink:#ffffff; --muted:#d2d8e1;
  --accent:#5eead4; --green:#22c55e; --red:#ef4444; --blue:#60a5fa; --amber:#f59e0b;
  --violet:#a78bfa; --teal:#2dd4bf; --rose:#fb7185; --cyan:#22d3ee;
}
html,body,[class*="css"] { color: var(--ink); background: var(--bg); }
.block { background: var(--card); border: 1px solid #0b1220; border-radius: 14px; padding: 16px 18px; }
.title { font-size: 2.1rem; font-weight: 800; margin: 0 0 .5rem 0; color: var(--ink); }
.lead  { color: var(--muted); margin-bottom: .8rem; }
.kpi { background: var(--subcard); border: 1px solid #0b1220; border-radius: 12px; padding: 12px 16px; }
.kpi .lbl { color: #f1f5f9; font-weight:600; font-size: .95rem; opacity:.95; }
.kpi .val { color: #ffffff; font-weight: 900; font-size: 1.55rem; letter-spacing:.2px; }
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

# -----------------------------
# Helpers
# -----------------------------
DATA_DIR = "data"

def load_csv(name: str) -> pd.DataFrame:
    """Robust CSV loader (handles , ; or tab separators and BOM)."""
    path = os.path.join(DATA_DIR, name)
    if not os.path.isfile(path):
        return pd.DataFrame()
    with open(path, "rb") as f:
        raw = f.read()
    df = pd.DataFrame()
    for sep in [",", ";", "\t"]:
        try:
            _df = pd.read_csv(io.BytesIO(raw), sep=sep, engine="python")
            if _df.shape[1] > 1:
                df = _df
                break
        except Exception:
            continue
    if df.empty:
        try:
            df = pd.read_csv(io.BytesIO(raw))
        except Exception:
            return pd.DataFrame()
    # Dates
    if "MONTH" in df.columns:
        df["MONTH"] = pd.to_datetime(df["MONTH"], errors="coerce")
        df = df.sort_values("MONTH")
    return df

def pct(x, digs=1):
    if pd.isna(x):
        return "—"
    return f"{x:.{digs}f}%"

def money(x, digs=2, symbol="$"):
    if pd.isna(x):
        return "—"
    return f"{symbol}{x:,.{digs}f}"

def section(title, definition=None):
    st.markdown(f'<div class="block">', unsafe_allow_html=True)
    st.markdown(f'<div class="title">{title}</div>', unsafe_allow_html=True)
    if definition:
        st.markdown(f'<div class="lead"><span class="badge">Definition</span> {definition}</div>', unsafe_allow_html=True)

def end_section():
    st.markdown("</div>", unsafe_allow_html=True)

def kpi(container, label, value, style="a"):
    with container:
        st.markdown(f'<div class="kpi {style}"><div class="lbl">{label}</div><div class="val">{value}</div></div>', unsafe_allow_html=True)

def insight(text):
    st.markdown(f'<div class="insight"><b>Insight:</b> {text}</div>', unsafe_allow_html=True)

# -----------------------------
# Executive Summary (3 paragraphs)
# -----------------------------
st.markdown("### Ethereum Capital Flows & User Dynamics Dashboard")
st.markdown(
"""
This dashboard presents a comprehensive analysis of Ethereum’s on-chain activity, offering critical insights into capital flows and user engagement. By tracking metrics across DeFi, bridges, and fees, it provides a sophisticated perspective for crypto-savvy readers to evaluate Ethereum’s overall market traction, economic vitality, and evolving user base. All metrics are derived from canonical datasets to ensure reliability for decision-making.

**August set a new all-time high for on-chain volume (~$341B)**, eclipsing the previous 2021 peak. The surge coincided with stronger corporate treasury accumulation, higher spot ETH ETF trading, and lower average fees, enabling heavier throughput. In parallel, protocols executed buybacks (~$46M in late August, Hyperliquid ~\$25M). While buybacks can stabilize prices during volatility, their long-run efficacy depends on fundamentals and sustained revenue.

The sections below track capital allocation, user dynamics, and execution costs. We highlight the mix of organic demand and macro tailwinds, with special attention to fee-sensitive adoption and to segments where capital is accumulating (DEXs, lending, bridges).
"""
)

st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

# ======================================================
# 1) Monthly On-Chain USD Volume by Category
# ======================================================
section("1. Monthly On-Chain USD Volume by Category",
        "Stacked on-chain volume (USD billions) by vertical; surfaces peak throughput and category mix.")

df_vol = load_csv("volume_category.csv")
if not df_vol.empty and all(c in df_vol.columns for c in ["MONTH", "CATEGORY", "VOLUME_USD_BILLIONS"]):
    df_vol["CATEGORY"] = df_vol["CATEGORY"].astype(str)

    # KPIs
    total_by_month = df_vol.groupby("MONTH")["VOLUME_USD_BILLIONS"].sum()
    peak = total_by_month.max()
    latest = total_by_month.index.max()

    # DEX dominance (best-effort: any category containing 'DEX')
    mask_dex = df_vol["CATEGORY"].str.contains("DEX", case=False, na=False)
    dex_share = np.nan
    if mask_dex.any():
        dex_latest = df_vol[df_vol["MONTH"] == latest]
        denom = dex_latest["VOLUME_USD_BILLIONS"].sum()
        numer = dex_latest[mask_dex]["VOLUME_USD_BILLIONS"].sum()
        dex_share = (numer / denom) * 100 if denom > 0 else np.nan

    c1, c2 = st.columns(2)
    kpi(c1, "Peak Volume", f"${peak:,.2f}B", "a")
    kpi(c2, "DEX Dominance (latest)", pct(dex_share, 1), "b")

    # Chart
    fig = px.area(df_vol, x="MONTH", y="VOLUME_USD_BILLIONS", color="CATEGORY",
                  labels={"VOLUME_USD_BILLIONS": "Volume (USD Billions)", "MONTH": "Month"})
    fig.update_layout(hovermode="x unified", legend=dict(orientation="h"))
    st.plotly_chart(fig, use_container_width=True)
    insight("DeFi lending and DEX trading typically drive the majority of on-chain volume; the mix helps contextualize risk-on phases.")
else:
    st.info("`data/volume_category.csv` missing required columns.")
end_section()

# ======================================================
# 2) Monthly Active Addresses and Transactions by Category (Toggle)
# ======================================================
section("2. Monthly Active Addresses and Transactions by Category",
        "Choose one metric at a time to isolate user base (addresses) vs. network load (transactions).")

df_act = load_csv("active_addresses.csv")
if not df_act.empty and all(c in df_act.columns for c in ["MONTH","CATEGORY","ACTIVE_ADDRESSES","TRANSACTIONS"]):
    df_act["CATEGORY"] = df_act["CATEGORY"].astype(str)

    metric = st.radio("Metric", ["Active Addresses", "Transactions"], horizontal=True, index=0, key="metric_act_tx")

    if metric == "Active Addresses":
        series = df_act.groupby("MONTH")["ACTIVE_ADDRESSES"].sum()
        peak_val = int(series.max())
        growth = (series.iloc[-1] / max(series.iloc[0], 1)) - 1
        c1, c2 = st.columns(2)
        kpi(c1, "Peak Active Addresses", f"{peak_val:,}", "c")
        kpi(c2, "Growth since start", pct(growth*100, 1), "d")

        piv = df_act.pivot_table(index="MONTH", columns="CATEGORY", values="ACTIVE_ADDRESSES", aggfunc="sum")
        fig = go.Figure()
        for col in piv.columns:
            fig.add_trace(go.Scatter(x=piv.index, y=piv[col], name=col, line=dict(width=2)))
        fig.update_layout(hovermode="x unified", xaxis_title="Month", yaxis_title="Active Addresses",
                          legend=dict(orientation="h"))
        st.plotly_chart(fig, use_container_width=True)

    else:
        series = df_act.groupby("MONTH")["TRANSACTIONS"].sum()
        peak_val = int(series.max())
        growth = (series.iloc[-1] / max(series.iloc[0], 1)) - 1
        c1, c2 = st.columns(2)
        kpi(c1, "Peak Transactions (Monthly)", f"{peak_val:,}", "c")
        kpi(c2, "Growth since start", pct(growth*100, 1), "d")

        piv = df_act.pivot_table(index="MONTH", columns="CATEGORY", values="TRANSACTIONS", aggfunc="sum")
        fig = go.Figure()
        for col in piv.columns:
            fig.add_trace(go.Scatter(x=piv.index, y=piv[col], name=col, line=dict(width=2, dash="dot")))
        fig.update_layout(hovermode="x unified", xaxis_title="Month", yaxis_title="Transactions",
                          legend=dict(orientation="h"))
        st.plotly_chart(fig, use_container_width=True)

    insight("Addresses reflect breadth; transactions reflect intensity. The toggle helps attribute changes to usage vs. throughput.")
else:
    st.info("`data/active_addresses.csv` missing required columns.")
end_section()

# ======================================================
# 3) User Cohorts by Monthly USD Volume
# ======================================================
section("3. User Cohorts by Monthly USD Volume",
        "Cohort distribution (e.g., whales vs retail) and their contribution to total monthly flow.")

df_coh = load_csv("user_cohort.csv")
if not df_coh.empty and all(c in df_coh.columns for c in ["MONTH","COHORT","UNIQUE_USERS","TOTAL_VOLUME"]):
    df_coh["COHORT"] = df_coh["COHORT"].astype(str)
    # KPIs: whale metrics if cohort name contains 'whale'
    latest = df_coh["MONTH"].max()
    latest_slice = df_coh[df_coh["MONTH"] == latest]

    whale_mask = latest_slice["COHORT"].str.contains("whale", case=False, na=False)
    whale_avg_vol = (latest_slice.loc[whale_mask, "TOTAL_VOLUME"].sum() /
                     max(latest_slice.loc[whale_mask, "UNIQUE_USERS"].sum(), 1))
    whale_share = (latest_slice.loc[whale_mask, "TOTAL_VOLUME"].sum() /
                   max(latest_slice["TOTAL_VOLUME"].sum(), 1)) * 100

    c1, c2 = st.columns(2)
    kpi(c1, "Whale Avg Vol (latest)", money(whale_avg_vol, 2), "a")
    kpi(c2, "Whale Volume Share (latest)", pct(whale_share, 1), "b")

    # Chart (stacked area of TOTAL_VOLUME by cohort)
    fig = px.area(df_coh, x="MONTH", y="TOTAL_VOLUME", color="COHORT",
                  labels={"TOTAL_VOLUME": "Total Volume (USD)", "MONTH": "Month"})
    fig.update_layout(hovermode="x unified", legend=dict(orientation="h"))
    st.plotly_chart(fig, use_container_width=True)
    insight("Whales often drive a disproportionate share of dollar volume; retail breadth still matters for resilience.")
else:
    st.info("`data/user_cohort.csv` missing required columns.")
end_section()

# ======================================================
# 4) User Typology — 100% Stacked (FIXED with transform)
# ======================================================
section("4. User Typology: Unique Users by Activity Level & Sector (100% Stacked)",
        "Share of multi-sector vs single-sector users by month; engagement via avg transactions per user.")

df_typ = load_csv("user_typology.csv")
if not df_typ.empty and all(c in df_typ.columns for c in ["MONTH","USER_TYPE","ACTIVITY_LEVEL","UNIQUE_USERS","AVG_TRANSACTIONS_PER_USER"]):
    df_typ["USER_TYPE"] = df_typ["USER_TYPE"].astype(str)
    df_typ["UNIQUE_USERS"] = pd.to_numeric(df_typ["UNIQUE_USERS"], errors="coerce")

    typ = (df_typ.groupby(["MONTH","USER_TYPE"], as_index=False)["UNIQUE_USERS"]
                 .sum()
                 .sort_values(["MONTH","USER_TYPE"]))
    typ["share"] = typ.groupby("MONTH")["UNIQUE_USERS"].transform(lambda s: (s / s.sum()) * 100)

    latest = typ["MONTH"].max()
    multi_share = typ[(typ["MONTH"]==latest) & (typ["USER_TYPE"].str.contains("multi", case=False))]["share"].sum()

    eng = df_typ.groupby("USER_TYPE")["AVG_TRANSACTIONS_PER_USER"].mean(numeric_only=True)
    if eng.index.str.contains("multi", case=False).any() and eng.index.str.contains("single", case=False).any():
        engagement_mult = eng[eng.index.str.contains("multi", case=False)].mean() / max(eng[eng.index.str.contains("single", case=False)].mean(), 1e-9)
    else:
        engagement_mult = np.nan

    c1,c2 = st.columns(2)
    kpi(c1, "Multi-Sector Users (latest)", pct(multi_share,1), "c")
    kpi(c2, "Engagement Multiplier (Multi/Single)", f"{engagement_mult:.2f}×" if not np.isnan(engagement_mult) else "—", "d")

    fig = px.bar(typ, x="MONTH", y="share", color="USER_TYPE", labels={"share":"% of Users"})
    fig.update_layout(barmode="stack", hovermode="x unified", legend=dict(orientation="h"))
    st.plotly_chart(fig, use_container_width=True)
    insight("Multi-sector users, though fewer, tend to show higher engagement (tx/user), indicating deeper ecosystem usage.")
else:
    st.info("`data/user_typology.csv` missing required columns.")
end_section()

# ======================================================
# 5) DEX Volume & Active Swappers (Monthly)
# ======================================================
section("5. DEX Volume & Active Swappers (Monthly)",
        "Bars show DEX volume (USD billions); line shows active swappers.")

df_dex = load_csv("dex_volume.csv")
if not df_dex.empty and all(c in df_dex.columns for c in ["MONTH","ACTIVE_SWAPPERS","TOTAL_VOLUME_BILLIONS"]):
    series_vol = df_dex.set_index("MONTH")["TOTAL_VOLUME_BILLIONS"]
    peak_vol = series_vol.max()
    vol_growth = (series_vol.iloc[-1] / max(series_vol.iloc[0], 1)) - 1

    c1, c2 = st.columns(2)
    kpi(c1, "Peak DEX Volume", f"${peak_vol:,.2f}B", "a")
    kpi(c2, "Volume Growth (since start)", pct(vol_growth*100,1), "b")

    fig = go.Figure()
    fig.add_trace(go.Bar(x=df_dex["MONTH"], y=df_dex["TOTAL_VOLUME_BILLIONS"], name="DEX Volume (B)"))
    fig.add_trace(go.Scatter(x=df_dex["MONTH"], y=df_dex["ACTIVE_SWAPPERS"], name="Active Swappers",
                             mode="lines", yaxis="y2", line=dict(width=2, color="#2dd4bf")))
    fig.update_layout(
        hovermode="x unified",
        yaxis=dict(title="Volume (B)"),
        yaxis2=dict(title="Active Swappers", overlaying="y", side="right"),
        legend=dict(orientation="h")
    )
    st.plotly_chart(fig, use_container_width=True)
    insight("Active swappers track risk appetite; divergences vs. volume can flag market-maker driven activity.")
else:
    st.info("`data/dex_volume.csv` missing required columns.")
end_section()

# ======================================================
# 6) Lending Deposits — Evolution per Platform
# ======================================================
section("6. Lending Deposits — Evolution per Platform",
        "Stacked deposits (USD billions) by platform; also shows top-platform share.")

df_len = load_csv("lending_deposits.csv")
if not df_len.empty and all(c in df_len.columns for c in ["MONTH","PLATFORM","VOLUME_BILLIONS","UNIQUE_DEPOSITORS"]):
    df_len["PLATFORM"] = df_len["PLATFORM"].astype(str)

    latest = df_len["MONTH"].max()
    sl = df_len[df_len["MONTH"]==latest]
    totals = sl.groupby("PLATFORM")["VOLUME_BILLIONS"].sum().sort_values(ascending=False)
    top_platform = totals.index[0] if not totals.empty else "—"
    top_share = (totals.iloc[0] / totals.sum() * 100) if totals.sum()>0 else np.nan

    dep_series = df_len.groupby("MONTH")["UNIQUE_DEPOSITORS"].sum()
    dep_growth = (dep_series.iloc[-1]/max(dep_series.iloc[0],1))-1

    c1,c2 = st.columns(2)
    kpi(c1, "Top Platform Share (latest)", pct(top_share,1), "c")
    kpi(c2, "Depositors Growth (since start)", pct(dep_growth*100,1), "d")

    fig = px.area(df_len, x="MONTH", y="VOLUME_BILLIONS", color="PLATFORM",
                  labels={"VOLUME_BILLIONS":"Deposit Volume (B)"})
    fig.update_layout(hovermode="x unified", legend=dict(orientation="h"))
    st.plotly_chart(fig, use_container_width=True)
    insight(f"Lending depth has concentrated in **{top_platform}** recently; monitoring share rotation helps track risk shifts.")
else:
    st.info("`data/lending_deposits.csv` missing required columns.")
end_section()

# ======================================================
# 7) Total Bridge Volume (Monthly)
# ======================================================
section("7. Total Bridge Volume (Monthly)",
        "Cross-chain connectivity and liquidity migration measured via total bridge volume (USD billions).")

df_bridge = load_csv("bridged_volume.csv")
if not df_bridge.empty and "TOTAL_BRIDGE_VOLUME_BILLIONS" in df_bridge.columns:
    series = df_bridge.set_index("MONTH")["TOTAL_BRIDGE_VOLUME_BILLIONS"]
    growth = (series.iloc[-1] / max(series.iloc[0], 1)) - 1
    status = "Emerging Cross-Chain Hub" if growth > 0.5 else "Stable / Mixed"

    c1, c2 = st.columns(2)
    kpi(c1, "Bridge Volume Growth", pct(growth*100,1), "a")
    kpi(c2, "Status", status, "b")

    fig = px.line(df_bridge, x="MONTH", y="TOTAL_BRIDGE_VOLUME_BILLIONS",
                  labels={"TOTAL_BRIDGE_VOLUME_BILLIONS":"Total Bridge Volume (B)"})
    fig.update_traces(line=dict(width=3))
    fig.update_layout(hovermode="x unified", legend=dict(orientation="h"))
    st.plotly_chart(fig, use_container_width=True)
    insight("Sustained bridge growth signals healthy cross-chain flows and liquidity portability.")
else:
    st.info("`data/bridged_volume.csv` missing required columns.")
end_section()

# ======================================================
# 8) ETH Price Overlay with Total Activity
# ======================================================
section("8. ETH Price Overlay with Total Activity",
        "Co-movement between ETH price and a composite activity index.")

df_price = load_csv("eth_price.csv")
if not df_price.empty and all(c in df_price.columns for c in ["MONTH","AVG_ETH_PRICE_USD","ACTIVITY_INDEX"]):
    pr = df_price["AVG_ETH_PRICE_USD"]
    corr_pa = df_price[["AVG_ETH_PRICE_USD","ACTIVITY_INDEX"]].dropna().corr().iloc[0,1]

    c1,c2 = st.columns(2)
    kpi(c1, "Price Range", money(pr.min(),0)+" – "+money(pr.max(),0), "a")
    kpi(c2, "Corr(Price, Activity)", f"{corr_pa:.2f}", "b")

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_price["MONTH"], y=df_price["AVG_ETH_PRICE_USD"],
                             name="ETH Price (USD)", line=dict(width=3, color="#60a5fa")))
    fig.add_trace(go.Scatter(x=df_price["MONTH"], y=df_price["ACTIVITY_INDEX"],
                             name="Activity Index", line=dict(width=2, dash="dot", color="#22c55e"),
                             yaxis="y2"))
    fig.update_layout(
        hovermode="x unified",
        yaxis=dict(title="ETH Price (USD)"),
        yaxis2=dict(title="Activity Index", overlaying="y", side="right"),
        legend=dict(orientation="h")
    )
    st.plotly_chart(fig, use_container_width=True)
    insight("A positive price–activity correlation suggests activity often follows price impulses (or vice-versa), but causality varies.")
else:
    st.info("`data/eth_price.csv` missing required columns.")
end_section()

# ======================================================
# 9) User Adoption During Fee Evolution (extra)
# ======================================================
section("9. User Adoption During Fee Evolution",
        "Unique users vs. average fee (USD); lower fees often coincide with stronger adoption.")

df_fee_act = load_csv("fees_activity.csv")
if df_fee_act.empty:
    # fallback to fees_price.csv if needed
    df_fee_act = load_csv("fees_price.csv").rename(columns={
        "AVG_TX_FEE_USD":"AVG_FEE_USD",
        "MONTHLY_TRANSACTIONS":"TOTAL_TRANSACTIONS",
        "TX_MILLIONS":"TRANSACTIONS_MILLIONS"
    })

if not df_fee_act.empty and "MONTH" in df_fee_act.columns:
    # Users series
    users = None
    if "USERS_MILLIONS" in df_fee_act.columns:
        users = pd.to_numeric(df_fee_act["USERS_MILLIONS"], errors="coerce") * 1e6
    elif "UNIQUE_USERS" in df_fee_act.columns:
        users = pd.to_numeric(df_fee_act["UNIQUE_USERS"], errors="coerce")

    # Fee series
    fee_usd = pd.to_numeric(df_fee_act["AVG_FEE_USD"], errors="coerce") if "AVG_FEE_USD" in df_fee_act.columns else None

    if users is not None and fee_usd is not None:
        ug = (users.iloc[-1] / max(users.iloc[0], 1) - 1) * 100
        first_fee = fee_usd.dropna().iloc[0] if fee_usd.dropna().size else np.nan
        fd = (fee_usd.dropna().iloc[-1] / first_fee - 1) * 100 if pd.notna(first_fee) else np.nan

        c1,c2 = st.columns(2)
        kpi(c1, "User Growth (since start)", pct(ug,1), "a")
        kpi(c2, "Fee Change (since start)", pct(fd,1), "b")

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
        insight("When fees soften, new users tend to accelerate — consistent with fee-sensitive onboarding.")
    else:
        st.info("Could not find `UNIQUE_USERS/USERS_MILLIONS` and `AVG_FEE_USD` in fees CSVs.")
else:
    st.info("`data/fees_activity.csv` or `data/fees_price.csv` missing `MONTH`.")
end_section()

# ======================================================
# 10) Price vs Fee — Correlation (extra)
# ======================================================
section("10. Price vs Fee — Correlation",
        "Scatter of monthly ETH price vs average transaction fee; Pearson correlation reported in KPIs.")

df_fp = load_csv("fees_price.csv")
if not df_fp.empty and all(c in df_fp.columns for c in ["MONTH","AVG_ETH_PRICE_USD","AVG_TX_FEE_USD"]):
    x = pd.to_numeric(df_fp["AVG_ETH_PRICE_USD"], errors="coerce")
    y = pd.to_numeric(df_fp["AVG_TX_FEE_USD"], errors="coerce")
    ok = x.notna() & y.notna()
    r = float(np.corrcoef(x[ok], y[ok])[0,1]) if ok.sum() >= 2 else np.nan

    last_ratio = None
    if "PRICE_TO_FEE_RATIO" in df_fp.columns:
        last_ratio = pd.to_numeric(df_fp["PRICE_TO_FEE_RATIO"], errors="coerce").iloc[-1]
    elif pd.notna(x.iloc[-1]) and pd.notna(y.iloc[-1]) and y.iloc[-1] != 0:
        last_ratio = x.iloc[-1] / y.iloc[-1]

    c1,c2 = st.columns(2)
    kpi(c1, "Correlation (Price vs Fee)", f"{r:.2f}" if pd.notna(r) else "—", "c")
    kpi(c2, "Price-to-Fee Ratio (latest)", f"{last_ratio:,.2f}" if pd.notna(last_ratio) else "—", "d")

    # Simple scatter (no trendline to avoid statsmodels dependency surprises)
    fig = px.scatter(df_fp, x="AVG_ETH_PRICE_USD", y="AVG_TX_FEE_USD",
                     labels={"AVG_ETH_PRICE_USD":"ETH Price (USD)", "AVG_TX_FEE_USD":"Avg TX Fee (USD)"},
                     title="ETH Price vs Average TX Fee — Monthly")
    fig.update_traces(marker=dict(size=8, opacity=0.85))
    st.plotly_chart(fig, use_container_width=True)
    insight("Fees tend to rise with price in aggregate, but L2 adoption and fee markets can flatten the relationship over time.")
else:
    st.info("`data/fees_price.csv` missing required columns.")
end_section()

# -----------------------------
# Footer
# -----------------------------
st.markdown(
    '<div style="text-align:center;color:#93a3b8;opacity:.8;margin-top:10px;">'
    'Built by Adrià Parcerisas • Data via Flipside/Dune-style exports • Streamlit + Plotly'
    '</div>',
    unsafe_allow_html=True
)
