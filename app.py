# app.py
# Ethereum Capital Flows & User Dynamics — Streamlit Dashboard
# (c) Adrià Parcerisas

import os, io
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# ──────────────────────────────────────────────────────────────────────────────
# Page config
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Ethereum Capital Flows & User Dynamics",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ──────────────────────────────────────────────────────────────────────────────
# High-contrast dark theme + components
# ──────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* palette */
:root{
  --bg:#0c1220; --card:#0f172a; --deep:#0a0f1c;
  --ink:#f5f7fb; --muted:#cbd5e1; --line:#2a3755;
  --accent:#5eead4; --cyan:#22d3ee; --amber:#f59e0b;
  --green:#22c55e; --red:#ef4444; --violet:#a78bfa; --blue:#60a5fa;
}

/* base */
html, body, [class*="css"] {
  background: var(--bg) !important; color: var(--ink) !important;
}
a { color: var(--accent) !important; text-decoration: none; }

/* containers */
.section { background: var(--card); border:1px solid var(--line);
  border-radius:14px; padding:18px 18px 16px 18px; margin-bottom:18px; }
.section-title { font-size: 1.35rem; font-weight:800; letter-spacing:.2px; margin:0 0 8px 0; }
.section-def { display:flex; gap:8px; align-items:flex-start;
  border:1px solid var(--line); background: var(--deep);
  border-radius:12px; padding:8px 10px; color: var(--muted); }
.def-pill { font-size:.75rem; font-weight:700; padding:2px 8px; border-radius:999px;
  background: #111827; color:#a5b4fc; border:1px solid var(--line);}
.rule { height:1px; background:var(--line); margin:12px 0; }

/* KPI cards */
.kpi { background: #0e1a33; border:1px solid var(--line); border-radius:12px;
  padding:10px 12px; }
.kpi .lbl { font-weight:700; color:#cbd5e1; font-size:.9rem; }
.kpi .val { font-weight:900; color:#ffffff; font-size:1.5rem; letter-spacing:.1px; }
.kpi.a { border-left:6px solid var(--cyan); }
.kpi.b { border-left:6px solid var(--amber); }
.kpi.c { border-left:6px solid var(--green); }
.kpi.d { border-left:6px solid var(--violet); }

/* insight card */
.insight { border:1px solid var(--line); background:#0d152b; color:var(--muted);
  border-radius:12px; padding:10px 12px; }

/* tighten Plotly margin text color */
.js-plotly-plot .plotly .xtick text, .js-plotly-plot .plotly .ytick text,
.js-plotly-plot .plotly .legend text { fill: #e5e7eb !important; }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────
DATA_DIR = "data"

def load_csv(name: str) -> pd.DataFrame:
    """Robust CSV loader that auto-detects separators and parses MONTH."""
    path = os.path.join(DATA_DIR, name)
    if not os.path.isfile(path): return pd.DataFrame()
    with open(path, "rb") as f: raw = f.read()
    df = pd.DataFrame()
    for sep in [",",";","\t"]:
        try:
            _df = pd.read_csv(io.BytesIO(raw), sep=sep, engine="python")
            if _df.shape[1] > 1:
                df = _df
                break
        except Exception: continue
    if df.empty:
        try: df = pd.read_csv(io.BytesIO(raw))
        except Exception: return pd.DataFrame()
    if "MONTH" in df.columns:
        df["MONTH"] = pd.to_datetime(df["MONTH"], errors="coerce")
        df = df.sort_values("MONTH")
    return df

def pct(x, digs=1):
    if x is None or pd.isna(x): return "—"
    return f"{x:.{digs}f}%"

def money(x, digs=2, symbol="$"):
    if x is None or pd.isna(x): return "—"
    return f"{symbol}{x:,.{digs}f}"

def section(title:str, definition:str|None=None):
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)
    if definition:
        st.markdown(
            f'<div class="section-def"><span class="def-pill">Definition</span>'
            f'<span>{definition}</span></div>',
            unsafe_allow_html=True,
        )
        st.markdown('<div class="rule"></div>', unsafe_allow_html=True)

def end_section():
    st.markdown('</div>', unsafe_allow_html=True)

def kpi(col, label, value, style="a"):
    with col:
        st.markdown(
            f'<div class="kpi {style}"><div class="lbl">{label}</div>'
            f'<div class="val">{value}</div></div>', unsafe_allow_html=True
        )

def insight(text:str):
    st.markdown(f'<div class="insight"><strong>Insight.</strong> {text}</div>', unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# Executive summary (3 paragraphs; bold/italic via HTML to avoid markdown quirks)
# ──────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="section">
  <div class="section-title">Executive Summary: Assessing Ethereum’s Traction</div>
  <div class="section-def" style="margin-bottom:12px;">
    <span class="def-pill">Context</span>
    <span>
      This dashboard analyzes Ethereum’s on-chain capital flows and user dynamics across DeFi, bridges, and fees.
      Metrics are sourced from canonical exports and designed for a crypto-savvy audience.
    </span>
  </div>
  <p style="color:#dbe2ef">
    <strong>August set a new all-time high for on-chain volume (~$341B)</strong>, eclipsing the 2021 peak.
    Tailwinds included corporate treasury accumulation, stronger spot ETH ETF trading, and lower average fees that
    enabled higher throughput. Protocol buybacks (≈$46M late August; Hyperliquid ≈$25M) supported prices in volatility,
    though long-run impact depends on fundamentals and recurring revenue.
  </p>
  <p style="color:#dbe2ef">
    The sections below track capital allocation, breadth vs. intensity of usage, execution costs, and cross-chain flows.
    Pay particular attention to fee-sensitive adoption and to segments where capital concentration rises (DEXs, lending, bridges).
  </p>
</div>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# 1) Monthly On-Chain USD Volume by Category
# ──────────────────────────────────────────────────────────────────────────────
section("1. Monthly On-Chain USD Volume by Category",
        "Stacked on-chain volume (USD billions) by vertical; highlights peak throughput and category mix.")

df_vol = load_csv("volume_category.csv")
if not df_vol.empty and all(c in df_vol.columns for c in ["MONTH","CATEGORY","VOLUME_USD_BILLIONS"]):
    df_vol["CATEGORY"] = df_vol["CATEGORY"].astype(str)
    total_by_month = df_vol.groupby("MONTH")["VOLUME_USD_BILLIONS"].sum()
    peak = total_by_month.max()
    latest = total_by_month.idxmax() if not total_by_month.empty else None

    # DEX dominance (best effort)
    mask_dex = df_vol["CATEGORY"].str.contains("DEX", case=False, na=False)
    dex_share = np.nan
    if mask_dex.any():
        latest_month = df_vol["MONTH"].max()
        sl = df_vol[df_vol["MONTH"]==latest_month]
        denom = sl["VOLUME_USD_BILLIONS"].sum()
        numer = sl[mask_dex]["VOLUME_USD_BILLIONS"].sum()
        dex_share = (numer/denom*100) if denom>0 else np.nan

    c1,c2 = st.columns(2)
    kpi(c1, "Peak Volume", f"${peak:,.2f}B" if pd.notna(peak) else "—", "a")
    kpi(c2, "DEX Dominance (latest)", pct(dex_share,1), "b")

    fig = px.area(df_vol, x="MONTH", y="VOLUME_USD_BILLIONS", color="CATEGORY",
                  labels={"VOLUME_USD_BILLIONS":"Volume (USD Billions)", "MONTH":"Month"})
    fig.update_layout(hovermode="x unified", legend=dict(orientation="h"))
    st.plotly_chart(fig, use_container_width=True)
    insight("DeFi lending and DEX trading typically drive most on-chain flow; the mix contextualizes risk-on vs. defensive phases.")
else:
    st.info("`data/volume_category.csv` missing required columns.")
end_section()

# ──────────────────────────────────────────────────────────────────────────────
# 2) Monthly Active Addresses vs Transactions (Toggle)
# ──────────────────────────────────────────────────────────────────────────────
section("2. Monthly Active Addresses and Transactions by Category",
        "Choose one metric at a time to isolate user base (addresses) vs network load (transactions).")

df_act = load_csv("active_addresses.csv")
if not df_act.empty and all(c in df_act.columns for c in ["MONTH","CATEGORY","ACTIVE_ADDRESSES","TRANSACTIONS"]):
    df_act["CATEGORY"] = df_act["CATEGORY"].astype(str)
    metric = st.radio("Metric", ["Active Addresses", "Transactions"], horizontal=True, index=0, key="metric_act")
    if metric == "Active Addresses":
        series = df_act.groupby("MONTH")["ACTIVE_ADDRESSES"].sum()
        c1,c2 = st.columns(2)
        kpi(c1, "Peak Users (Monthly)", f"{int(series.max()):,}" if series.size else "—", "c")
        # DEX users share latest
        latest = df_act["MONTH"].max()
        sl = df_act[df_act["MONTH"]==latest]
        dex_share = (sl.loc[sl["CATEGORY"].str.contains("DEX",case=False), "ACTIVE_ADDRESSES"].sum()
                     / max(sl["ACTIVE_ADDRESSES"].sum(),1) * 100) if not sl.empty else np.nan
        kpi(c2, "DEX Users (latest)", pct(dex_share,1), "d")

        piv = df_act.pivot_table(index="MONTH", columns="CATEGORY", values="ACTIVE_ADDRESSES", aggfunc="sum")
        fig = go.Figure()
        for col in piv.columns:
            fig.add_trace(go.Scatter(x=piv.index, y=piv[col], name=col, line=dict(width=2)))
        fig.update_layout(hovermode="x unified", xaxis_title="Month", yaxis_title="Active Addresses",
                          legend=dict(orientation="h"))
        st.plotly_chart(fig, use_container_width=True)
    else:
        series = df_act.groupby("MONTH")["TRANSACTIONS"].sum()
        c1,c2 = st.columns(2)
        kpi(c1, "Peak TX (Monthly)", f"{int(series.max()):,}" if series.size else "—", "c")
        latest = df_act["MONTH"].max()
        sl = df_act[df_act["MONTH"]==latest]
        dex_share = (sl.loc[sl["CATEGORY"].str.contains("DEX",case=False), "TRANSACTIONS"].sum()
                     / max(sl["TRANSACTIONS"].sum(),1) * 100) if not sl.empty else np.nan
        kpi(c2, "DEX TX Share (latest)", pct(dex_share,1), "d")

        piv = df_act.pivot_table(index="MONTH", columns="CATEGORY", values="TRANSACTIONS", aggfunc="sum")
        fig = go.Figure()
        for col in piv.columns:
            fig.add_trace(go.Scatter(x=piv.index, y=piv[col], name=col, line=dict(width=2, dash="dot")))
        fig.update_layout(hovermode="x unified", xaxis_title="Month", yaxis_title="Transactions",
                          legend=dict(orientation="h"))
        st.plotly_chart(fig, use_container_width=True)
    insight("Addresses reflect breadth; transactions reflect intensity. Use the toggle to attribute changes to usage vs throughput.")
else:
    st.info("`data/active_addresses.csv` missing required columns.")
end_section()

# ──────────────────────────────────────────────────────────────────────────────
# 3) User Mix — Cohorts & Typology (merged)
# ──────────────────────────────────────────────────────────────────────────────
section("3. User Mix — Cohorts & Typology (Volume vs Activity)",
        "Two synchronized views per month: (A) evolution of unique users, (B) 100% stacked shares. Toggle the dimension.")

df_coh = load_csv("user_cohort.csv")       # COHORT (e.g., Whale/Large/Small…)
df_typ = load_csv("user_typology.csv")     # USER_TYPE + ACTIVITY_LEVEL (e.g., Multi-sector / Single, Casual / Power)

dim = st.radio("Dimension", ["Volume Cohorts", "Activity/Sector"], horizontal=True, index=0, key="mix_dim")

def _plot_evolution_and_share(df: pd.DataFrame, cat_col: str, count_col="UNIQUE_USERS",
                              title_a="Unique Users by Category", title_b="Category Share (100%)"):
    # A) Evolution (lines)
    piv = df.pivot_table(index="MONTH", columns=cat_col, values=count_col, aggfunc="sum").fillna(0)
    figA = go.Figure()
    for col in piv.columns:
        figA.add_trace(go.Scatter(x=piv.index, y=piv[col], name=col, line=dict(width=2)))
    figA.update_layout(hovermode="x unified", legend=dict(orientation="h"),
                       xaxis_title="Month", yaxis_title="Unique Users", title=title_a)
    st.plotly_chart(figA, use_container_width=True)

    # B) 100% stacked share
    share = piv.apply(lambda r: (r / r.sum())*100 if r.sum()>0 else r, axis=1)
    figB = px.bar(share.reset_index().melt("MONTH", var_name=cat_col, value_name="share"),
                  x="MONTH", y="share", color=cat_col, labels={"share":"% of Users"}, title=title_b)
    figB.update_layout(barmode="stack", hovermode="x unified", legend=dict(orientation="h"))
    st.plotly_chart(figB, use_container_width=True)

if dim == "Volume Cohorts" and not df_coh.empty and all(c in df_coh.columns for c in ["MONTH","COHORT","UNIQUE_USERS","TOTAL_VOLUME"]):
    df_coh["COHORT"] = df_coh["COHORT"].astype(str)
    # KPIs (latest)
    latest = df_coh["MONTH"].max()
    sl = df_coh[df_coh["MONTH"]==latest]
    whale_mask = sl["COHORT"].str.contains("whale", case=False, na=False)
    whale_share = (sl.loc[whale_mask,"UNIQUE_USERS"].sum() / max(sl["UNIQUE_USERS"].sum(),1) * 100) if not sl.empty else np.nan
    whale_avg_vol = (sl.loc[whale_mask,"TOTAL_VOLUME"].sum() /
                     max(sl.loc[whale_mask,"UNIQUE_USERS"].sum(),1)) if whale_mask.any() else np.nan

    c1,c2 = st.columns(2)
    kpi(c1, "Whale User Share (latest)", pct(whale_share,1), "a")
    kpi(c2, "Whale Avg Volume (latest)", money(whale_avg_vol,2), "b")

    _plot_evolution_and_share(df_coh, "COHORT",
                              title_a="Unique Users by Cohort",
                              title_b="Cohort Share (100%)")
    insight("Cohorts reveal who drives participation. Whale concentration can lift dollar volumes while masking retail breadth.")
elif dim == "Activity/Sector" and not df_typ.empty and all(c in df_typ.columns for c in ["MONTH","USER_TYPE","ACTIVITY_LEVEL","UNIQUE_USERS","AVG_TRANSACTIONS_PER_USER"]):
    df_typ["USER_TYPE"] = df_typ["USER_TYPE"].astype(str)
    # KPIs (latest)
    latest = df_typ["MONTH"].max()
    sl = df_typ[df_typ["MONTH"]==latest]
    multi_share = (sl.loc[sl["USER_TYPE"].str.contains("multi",case=False),"UNIQUE_USERS"].sum()
                   / max(sl["UNIQUE_USERS"].sum(),1) * 100) if not sl.empty else np.nan
    eng = df_typ.groupby("USER_TYPE")["AVG_TRANSACTIONS_PER_USER"].mean(numeric_only=True)
    if eng.index.str.contains("multi",case=False).any() and eng.index.str.contains("single",case=False).any():
        engagement_mult = eng[eng.index.str.contains("multi",case=False)].mean() / max(eng[eng.index.str.contains("single",case=False)].mean(),1e-9)
    else:
        engagement_mult = np.nan

    c1,c2 = st.columns(2)
    kpi(c1, "Multi-Sector User Share (latest)", pct(multi_share,1), "c")
    kpi(c2, "Engagement Multiplier (Multi/Single)", f"{engagement_mult:.2f}×" if pd.notna(engagement_mult) else "—", "d")

    _plot_evolution_and_share(df_typ.rename(columns={"USER_TYPE":"CATEGORY"}), "CATEGORY",
                              title_a="Unique Users by Activity/Sector",
                              title_b="Activity/Sector Share (100%)")
    insight("Multi-sector users tend to be fewer but more engaged (tx/user), signalling deeper ecosystem usage.")
else:
    st.info("Missing or incomplete `user_cohort.csv` / `user_typology.csv`.")
end_section()

# ──────────────────────────────────────────────────────────────────────────────
# 4) DEX Volume & Active Swappers
# ──────────────────────────────────────────────────────────────────────────────
section("4. DEX Volume & Active Swappers (Monthly)",
        "Bars show DEX volume (USD billions); line shows active swappers.")

df_dex = load_csv("dex_volume.csv")
if not df_dex.empty and all(c in df_dex.columns for c in ["MONTH","ACTIVE_SWAPPERS","TOTAL_VOLUME_BILLIONS"]):
    series_vol = df_dex.set_index("MONTH")["TOTAL_VOLUME_BILLIONS"]
    c1,c2 = st.columns(2)
    kpi(c1, "Peak DEX Volume", f"${series_vol.max():,.2f}B", "a")
    growth = (series_vol.iloc[-1]/max(series_vol.iloc[0],1)-1)*100 if series_vol.size>1 else np.nan
    kpi(c2, "Volume Growth (since start)", pct(growth,1), "b")

    fig = go.Figure()
    fig.add_trace(go.Bar(x=df_dex["MONTH"], y=df_dex["TOTAL_VOLUME_BILLIONS"], name="DEX Volume (B)"))
    fig.add_trace(go.Scatter(x=df_dex["MONTH"], y=df_dex["ACTIVE_SWAPPERS"], name="Active Swappers",
                             mode="lines", line=dict(width=2, color="#2dd4bf"), yaxis="y2"))
    fig.update_layout(hovermode="x unified", legend=dict(orientation="h"),
                      yaxis=dict(title="Volume (B)"),
                      yaxis2=dict(title="Active Swappers", overlaying="y", side="right"))
    st.plotly_chart(fig, use_container_width=True)
    insight("Swapper count tracks risk appetite; divergence vs volume may indicate market-maker dominated flow.")
else:
    st.info("`data/dex_volume.csv` missing required columns.")
end_section()

# ──────────────────────────────────────────────────────────────────────────────
# 5) Lending Deposits — Evolution per Platform
# ──────────────────────────────────────────────────────────────────────────────
section("5. Lending Deposits — Evolution per Platform",
        "Stacked deposits (USD billions) by platform; also reports top-platform share.")

df_len = load_csv("lending_deposits.csv")
if not df_len.empty and all(c in df_len.columns for c in ["MONTH","PLATFORM","VOLUME_BILLIONS","UNIQUE_DEPOSITORS"]):
    df_len["PLATFORM"] = df_len["PLATFORM"].astype(str)
    latest = df_len["MONTH"].max()
    sl = df_len[df_len["MONTH"]==latest]
    totals = sl.groupby("PLATFORM")["VOLUME_BILLIONS"].sum().sort_values(ascending=False)
    top_platform = totals.index[0] if not totals.empty else "—"
    top_share = (totals.iloc[0]/totals.sum()*100) if totals.sum()>0 else np.nan

    dep_series = df_len.groupby("MONTH")["UNIQUE_DEPOSITORS"].sum()
    dep_growth = (dep_series.iloc[-1]/max(dep_series.iloc[0],1)-1)*100 if dep_series.size>1 else np.nan

    c1,c2 = st.columns(2)
    kpi(c1, "Top Platform Share (latest)", pct(top_share,1), "c")
    kpi(c2, "Depositors Growth (since start)", pct(dep_growth,1), "d")

    fig = px.area(df_len, x="MONTH", y="VOLUME_BILLIONS", color="PLATFORM",
                  labels={"VOLUME_BILLIONS":"Deposit Volume (B)"})
    fig.update_layout(hovermode="x unified", legend=dict(orientation="h"))
    st.plotly_chart(fig, use_container_width=True)
    insight(f"Lending depth is recently concentrated in <strong>{top_platform}</strong>. Tracking share rotation helps assess risk migration.")
else:
    st.info("`data/lending_deposits.csv` missing required columns.")
end_section()

# ──────────────────────────────────────────────────────────────────────────────
# 6) Total Bridge Volume (Monthly)
# ──────────────────────────────────────────────────────────────────────────────
section("6. Total Bridge Volume (Monthly)",
        "Cross-chain connectivity and liquidity migration measured via total bridge volume (USD billions).")

df_bridge = load_csv("bridged_volume.csv")
if not df_bridge.empty and "TOTAL_BRIDGE_VOLUME_BILLIONS" in df_bridge.columns:
    series = df_bridge.set_index("MONTH")["TOTAL_BRIDGE_VOLUME_BILLIONS"]
    growth = (series.iloc[-1]/max(series.iloc[0],1)-1)*100 if series.size>1 else np.nan
    status = "Emerging Cross-Chain Hub" if (pd.notna(growth) and growth>50) else "Stable / Mixed"

    c1,c2 = st.columns(2)
    kpi(c1, "Bridge Volume Growth", pct(growth,1), "a")
    kpi(c2, "Status", status, "b")

    fig = px.line(df_bridge, x="MONTH", y="TOTAL_BRIDGE_VOLUME_BILLIONS",
                  labels={"TOTAL_BRIDGE_VOLUME_BILLIONS":"Total Bridge Volume (B)"})
    fig.update_traces(line=dict(width=3))
    fig.update_layout(hovermode="x unified", legend=dict(orientation="h"))
    st.plotly_chart(fig, use_container_width=True)
    insight(
        "Bridge activity trends upward, signalling stronger cross-chain liquidity mobility. "
        "Further investigation can decompose inflows/outflows by origin/destination to reveal drivers."
    )
else:
    st.info("`data/bridged_volume.csv` missing required columns.")
end_section()

# ──────────────────────────────────────────────────────────────────────────────
# 7) ETH Price Overlay with Total Activity
# ──────────────────────────────────────────────────────────────────────────────
section("7. ETH Price Overlay with Total Activity",
        "Co-movement between ETH price and a composite activity index.")

df_price = load_csv("eth_price.csv")
if not df_price.empty and all(c in df_price.columns for c in ["MONTH","AVG_ETH_PRICE_USD","ACTIVITY_INDEX"]):
    pr = df_price["AVG_ETH_PRICE_USD"]; act = df_price["ACTIVITY_INDEX"]
    corr_pa = df_price[["AVG_ETH_PRICE_USD","ACTIVITY_INDEX"]].dropna().corr().iloc[0,1]

    c1,c2 = st.columns(2)
    kpi(c1, "Price Range", f"{money(pr.min(),0)} – {money(pr.max(),0)}", "a")
    kpi(c2, "Corr(Price, Activity)", f"{corr_pa:.2f}", "b")

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_price["MONTH"], y=pr, name="ETH Price (USD)", line=dict(width=3, color="#60a5fa")))
    fig.add_trace(go.Scatter(x=df_price["MONTH"], y=act, name="Activity Index", yaxis="y2",
                             line=dict(width=2, dash="dot", color="#22c55e")))
    fig.update_layout(hovermode="x unified",
                      yaxis=dict(title="ETH Price (USD)"),
                      yaxis2=dict(title="Activity Index", overlaying="y", side="right"),
                      legend=dict(orientation="h"))
    st.plotly_chart(fig, use_container_width=True)
    insight("A positive correlation suggests activity often follows price impulses (or vice-versa), though causality varies over regimes.")
else:
    st.info("`data/eth_price.csv` missing required columns.")
end_section()

# ──────────────────────────────────────────────────────────────────────────────
# 8) User Adoption During Fee Evolution
# ──────────────────────────────────────────────────────────────────────────────
section("8. User Adoption During Fee Evolution",
        "Unique users vs average fee (USD); lower fees often coincide with stronger adoption.")

df_fee_act = load_csv("fees_activity.csv")
if df_fee_act.empty:
    # fallback
    df_fee_act = load_csv("fees_price.csv").rename(columns={
        "AVG_TX_FEE_USD":"AVG_FEE_USD",
        "MONTHLY_TRANSACTIONS":"TOTAL_TRANSACTIONS",
        "TX_MILLIONS":"TRANSACTIONS_MILLIONS"
    })

if not df_fee_act.empty and "MONTH" in df_fee_act.columns:
    users = None
    if "USERS_MILLIONS" in df_fee_act.columns:
        users = pd.to_numeric(df_fee_act["USERS_MILLIONS"], errors="coerce") * 1e6
    elif "UNIQUE_USERS" in df_fee_act.columns:
        users = pd.to_numeric(df_fee_act["UNIQUE_USERS"], errors="coerce")
    fee_usd = pd.to_numeric(df_fee_act["AVG_FEE_USD"], errors="coerce") if "AVG_FEE_USD" in df_fee_act.columns else None

    if users is not None and fee_usd is not None:
        ug = (users.iloc[-1]/max(users.iloc[0],1)-1)*100 if users.size>1 else np.nan
        first_fee = fee_usd.dropna().iloc[0] if fee_usd.dropna().size else np.nan
        fd = (fee_usd.dropna().iloc[-1]/first_fee-1)*100 if pd.notna(first_fee) else np.nan

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
        fig.update_layout(hovermode="x unified", xaxis_title="Month",
                          yaxis=dict(title="Unique Users"),
                          yaxis2=dict(title="Average Fee (USD)", overlaying="y", side="right"),
                          legend=dict(orientation="h"))
        st.plotly_chart(fig, use_container_width=True)
        insight("Fee softening tends to unlock new cohorts; fee spikes dampen marginal adoption, especially for retail flows.")
    else:
        st.info("Could not find `UNIQUE_USERS/USERS_MILLIONS` and `AVG_FEE_USD` in fees CSVs.")
else:
    st.info("`data/fees_activity.csv` or `data/fees_price.csv` missing `MONTH`.")
end_section()

# ──────────────────────────────────────────────────────────────────────────────
# 9) Price vs Fee — Correlation
# ──────────────────────────────────────────────────────────────────────────────
section("9. Price vs Fee — Correlation",
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

    fig = px.scatter(df_fp, x="AVG_ETH_PRICE_USD", y="AVG_TX_FEE_USD",
                     labels={"AVG_ETH_PRICE_USD":"ETH Price (USD)", "AVG_TX_FEE_USD":"Avg TX Fee (USD)"},
                     title="ETH Price vs Average TX Fee — Monthly")
    fig.update_traces(marker=dict(size=8, opacity=0.85))
    st.plotly_chart(fig, use_container_width=True)
    insight("While positively related on L1, L2 adoption can flatten fees for a given price regime.")
else:
    st.info("`data/fees_price.csv` missing required columns.")
end_section()

# ──────────────────────────────────────────────────────────────────────────────
# Footer
# ──────────────────────────────────────────────────────────────────────────────
st.markdown(
    '<div style="text-align:center;color:#9fb0c7;opacity:.9;margin-top:8px;">'
    'Built by Adrià Parcerisas • Data via Flipside/Dune-style exports • Streamlit + Plotly'
    '</div>', unsafe_allow_html=True
)
