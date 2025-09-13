# app.py — Liquid Staking on Aptos: stAPT (Amnis Finance)
# Panel-ready dashboard (<= 8 charts)

import os, re
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

# -------------------
# Page / theme / CSS
# -------------------
st.set_page_config(page_title="Liquid Staking on Aptos — stAPT (Amnis Finance)", layout="wide", page_icon="💧")

st.markdown("""
<style>
:root{--ink:#0f172a; --muted:#6b7280; --card:#f8fafc; --line:#e5e7eb;}
* {font-family: Inter, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif;}
h1,h2,h3 {color: var(--ink);}
.block-title{font-size:2rem;font-weight:800;margin:.25rem 0 .15rem}
.block-sub{color:var(--muted);margin:0 0 .8rem}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:14px 16px}
.metric{background:#ffffff;border:1px solid var(--line);border-radius:14px;padding:14px 16px;margin:4px;
        box-shadow:0 1px 0 rgba(15,23,42,.04)}
.metric .label{font-size:.9rem;color:var(--muted)}
.metric .value{font-size:1.4rem;font-weight:800;line-height:1.1;color:#0f172a}
.metric.border-a{border-left:6px solid #277DA1}
.metric.border-b{border-left:6px solid #43AA8B}
.metric.border-c{border-left:6px solid #F8961E}
.metric.border-d{border-left:6px solid #3A86FF}
.metric.border-e{border-left:6px solid #E63946}
.metric.border-f{border-left:6px solid #9C27B0}
hr.soft{border:none;border-top:1px solid var(--line);margin:12px 0 18px}
.caption{color:var(--muted);font-size:.92rem}
.small{font-size:.9rem}
</style>
""", unsafe_allow_html=True)

# -------------------
# Files
# -------------------
FILES = {
    "price": "APT vs stAPT Price Performance.csv",
    "cap":   "capital_efficiency.csv",
    "liq":   "Liquidity Depth vs Slippage Curve.csv",
    "rev":   "Revenue Sustainability Ratio.csv",
    "risk":  "Systemic Risk.csv",
    "prot":  "Protocol Health Score Dashboard.csv",
    "lend":  "Lending protocols Health Score.csv",
    "eng":   "User Engagement.csv",
    "beh":   "User Behavior Distribution.csv",
}

# -------------------
# Helpers
# -------------------
@st.cache_data(show_spinner=False)
def load_csv(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        return pd.DataFrame()
    try:
        df = pd.read_csv(path, sep=None, engine="python")
    except Exception:
        df = pd.read_csv(path)
    df.columns = [c.strip().lstrip("\ufeff") for c in df.columns]
    for c in df.columns:
        if re.search(r"(date|day|timestamp)", c, re.I):
            try:
                df[c] = pd.to_datetime(df[c], errors="coerce")
            except Exception:
                pass
    return df

def safe_num(x):
    try:
        return pd.to_numeric(x, errors="coerce")
    except Exception:
        return pd.Series([np.nan]*len(x))

def to_percent_number(series_like):
    """Accepts numbers or strings like '6.12%' / '6,12 %' and returns numeric (float)."""
    s = pd.Series(series_like)
    s = s.astype(str).str.replace(r"[,%\s]", "", regex=True)
    return pd.to_numeric(s, errors="coerce")

def metric_box(label: str, value: str, border_class=""):
    st.markdown(f"""
    <div class="metric {border_class}">
      <div class="label">{label}</div>
      <div class="value">{value}</div>
    </div>
    """, unsafe_allow_html=True)

# -------------------
# Intro / brief
# -------------------
st.markdown('<div class="block-title">💧 Liquid Staking on Aptos — stAPT (Amnis Finance)</div>', unsafe_allow_html=True)
st.markdown("""
<div class="block-sub">
This dashboard evaluates <strong>stAPT</strong> (Amnis Finance) on Aptos across peg stability, capital efficiency, liquidity depth,
revenue sustainability, systemic risk, global health, and user behavior. It is intentionally concise with ≤ 8 charts for panel review.
</div>
""", unsafe_allow_html=True)

st.markdown("""
**Why this topic (2–3 paragraphs).** Liquid staking is foundational DeFi infrastructure: it unlocks staked assets to be used as collateral and liquidity while maintaining staking rewards.
On Aptos, **stAPT** aims to become the base yield-bearing asset that flows through DEXes, money markets, and structured products. Evaluating stAPT across *peg behavior*, *execution quality*,
*revenue sustainability*, and *risk posture* reveals whether the asset is maturing into safe, efficient collateral.

In today’s multi-chain market, protocols that maintain tight pegs, deep liquidity, and sustainable flywheels (fees ≥ incentives) endure beyond mercenary flows. The analysis below highlights stAPT’s peg,
trading depth and slippage, efficiency of capital, sustainability of revenues, and systemic risk where stAPT concentrates as collateral.
""")

st.markdown("<hr class='soft'/>", unsafe_allow_html=True)

# =======================================================
# 1) Peg Stability — Chart 1
# =======================================================
st.markdown('<div class="block-title">1. Peg Stability — APT vs stAPT</div>', unsafe_allow_html=True)
st.markdown('<div class="block-sub"><strong>Definition:</strong> stAPT should track APT; deviations (premium/discount) reflect confidence and market depth.</div>', unsafe_allow_html=True)

dfp = load_csv(FILES["price"])
if not dfp.empty and all(c in dfp.columns for c in ["DAY","APT_PRICE_USD","STAPT_PRICE_USD"]):
    dfp = dfp.sort_values("DAY")
    apt   = safe_num(dfp["APT_PRICE_USD"])
    stapt = safe_num(dfp["STAPT_PRICE_USD"])
    prem  = safe_num(dfp["STAPT_PREMIUM_PCT"]) if "STAPT_PREMIUM_PCT" in dfp.columns else (stapt/apt - 1)*100

    k1,k2,k3 = st.columns(3)
    with k1: metric_box("APT Price", f"${apt.iloc[-1]:.2f}", "border-a")
    with k2: metric_box("stAPT Price", f"${stapt.iloc[-1]:.2f}", "border-b")
    with k3: metric_box("stAPT Premium", f"{prem.iloc[-1]:.2f}%", "border-c")

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dfp["DAY"], y=apt,   name="APT",   line=dict(color="#1F77B4", width=2)))
    fig.add_trace(go.Scatter(x=dfp["DAY"], y=stapt, name="stAPT", line=dict(color="#2CA02C", width=2)))
    fig.add_trace(go.Scatter(x=dfp["DAY"], y=prem,  name="Premium/Discount (%)", yaxis="y2",
                             line=dict(color="#2ECC71", dash="dot", width=2)))
    fig.update_layout(
        hovermode="x unified",
        xaxis_title="Date",
        yaxis=dict(title="Price (USD)"),
        yaxis2=dict(title="Premium/Discount (%)", overlaying="y", side="right"),
        legend=dict(orientation="h")
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Price CSV missing required columns (DAY, APT_PRICE_USD, STAPT_PRICE_USD).")

st.markdown("<hr class='soft'/>", unsafe_allow_html=True)

# =======================================================
# 2) Capital Efficiency — Chart 2 (fixed NaNs & styling)
# =======================================================
st.markdown('<div class="block-title">2. Capital Efficiency Ratios</div>', unsafe_allow_html=True)
st.markdown('<div class="block-sub"><strong>Definition:</strong> Volume/TVL shows turnover; Fees/TVL shows revenue intensity. Both are % (already in CSV).</div>', unsafe_allow_html=True)

dfce = load_csv(FILES["cap"])
if not dfce.empty and all(c in dfce.columns for c in ["Date","Volume/TVL%","Fees/TVL%"]):
    dfce = dfce.sort_values("Date")
    # robust parse: handle "6.12%" strings
    vol = to_percent_number(dfce["Volume/TVL%"])
    fee = to_percent_number(dfce["Fees/TVL%"])

    k1,k2 = st.columns(2)
    with k1: metric_box("Current Volume/TVL", f"{vol.dropna().iloc[-1]:.2f}%", "border-d")
    with k2: metric_box("Current Fees/TVL",   f"{fee.dropna().iloc[-1]:.2f}%", "border-f")

    vol_ma = vol.rolling(7, min_periods=1).mean()
    fee_ma = fee.rolling(7, min_periods=1).mean()

    fig = go.Figure()
    # bars for Volume/TVL
    fig.add_trace(go.Bar(x=dfce["Date"], y=vol, name="Volume/TVL (%)", marker_color="#1F78B4", opacity=0.65))
    # dashed line for Fees/TVL on y2
    fig.add_trace(go.Scatter(x=dfce["Date"], y=fee, name="Fees/TVL (%)", yaxis="y2",
                             line=dict(color="#9C27B0", dash="dot", width=2)))
    # smoothing overlays
    fig.add_trace(go.Scatter(x=dfce["Date"], y=vol_ma, name="Volume/TVL 7d MA", line=dict(color="#0E4C92")))
    fig.add_trace(go.Scatter(x=dfce["Date"], y=fee_ma, name="Fees/TVL 7d MA", yaxis="y2", line=dict(color="#6A1B9A")))
    fig.update_layout(
        hovermode="x unified", barmode="overlay",
        xaxis_title="Date",
        yaxis=dict(title="Volume/TVL (%)"),
        yaxis2=dict(title="Fees/TVL (%)", overlaying="y", side="right"),
        legend=dict(orientation="h")
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Capital Efficiency CSV missing columns (Date, Volume/TVL%, Fees/TVL%).")

st.markdown("<hr class='soft'/>", unsafe_allow_html=True)

# =======================================================
# 3) Liquidity Depth vs Slippage — Chart 3 (volume-ordered, table & insights)
# =======================================================
st.markdown('<div class="block-title">3. Liquidity Depth vs Slippage</div>', unsafe_allow_html=True)
st.markdown('<div class="block-sub"><strong>Definition:</strong> Execution quality by trade size: bars = trade count (volume proxy), line = average absolute slippage (bps). Lower is better.</div>', unsafe_allow_html=True)

dfld_raw = load_csv(FILES["liq"])

def _norm(s: str): return re.sub(r'[^a-z0-9]+','_', str(s).strip().lower())
def _pick(colmap: dict, *cands):
    for c in cands:
        if c in colmap.values():
            for orig, norm in colmap.items():
                if norm == c: return orig
    return None

if dfld_raw.empty:
    st.info("Liquidity CSV not found or empty.")
else:
    colmap = {c:_norm(c) for c in dfld_raw.columns}
    c_size   = _pick(colmap, "size_bucket","swap_size_bucket")
    c_count  = _pick(colmap, "trade_count","swap_count","trades")
    c_avg_bps= _pick(colmap, "avg_abs_slippage_bps","avg_slippage_bps")
    c_avg_pct= _pick(colmap, "avg_abs_slippage_pct","avg_slippage_pct")

    miss=[]
    if not c_size: miss.append("SIZE_BUCKET/SWAP_SIZE_BUCKET")
    if not c_count: miss.append("TRADE_COUNT/SWAP_COUNT")
    if not (c_avg_bps or c_avg_pct): miss.append("AVG_ABS_SLIPPAGE_[BPS|PCT]")
    if miss:
        st.error("Liquidity CSV missing: " + ", ".join(miss))
    else:
        size  = dfld_raw[c_size].astype(str)
        count = safe_num(dfld_raw[c_count])
        slip_bps = safe_num(dfld_raw[c_avg_bps]) if c_avg_bps else safe_num(dfld_raw[c_avg_pct])*100.0

        df = pd.DataFrame({"SIZE_BUCKET": size, "TRADE_COUNT": count, "AVG_ABS_SLIPPAGE_BPS": slip_bps})

        # Aggregate duplicates with weights
        agg = (
            df.groupby("SIZE_BUCKET", as_index=False)
              .apply(lambda g: pd.Series({
                  "TRADE_COUNT": safe_num(g["TRADE_COUNT"]).sum(),
                  "AVG_ABS_SLIPPAGE_BPS": np.average(
                      safe_num(g["AVG_ABS_SLIPPAGE_BPS"]),
                      weights=np.clip(safe_num(g["TRADE_COUNT"]),1,None)
                  )
              }))
              .reset_index(drop=True)
        )

        agg = agg.sort_values("TRADE_COUNT", ascending=False)
        bucket_order = agg["SIZE_BUCKET"].tolist()

        total_trades = int(agg["TRADE_COUNT"].sum())
        wavg_slip = float(np.average(agg["AVG_ABS_SLIPPAGE_BPS"], weights=np.clip(agg["TRADE_COUNT"],1,None)))
        k1,k2 = st.columns(2)
        with k1: metric_box("Total Trades (30d)", f"{total_trades:,}", "border-d")
        with k2: metric_box("Weighted Avg Slippage", f"{wavg_slip:.2f} bps", "border-e")
        st.markdown("<hr class='soft'/>", unsafe_allow_html=True)

        fig = go.Figure()
        fig.add_trace(go.Bar(x=agg["SIZE_BUCKET"], y=agg["TRADE_COUNT"], name="Trade Count",
                             marker_color="#3A86FF", yaxis="y2", opacity=0.9))
        fig.add_trace(go.Scatter(x=agg["SIZE_BUCKET"], y=agg["AVG_ABS_SLIPPAGE_BPS"], name="Avg. Slippage (bps)",
                                 mode="lines+markers", line=dict(color="#E63946", width=2), marker=dict(size=6)))
        fig.update_layout(
            title="Liquidity Depth vs Slippage (ordered by volume)",
            hovermode="x unified", bargap=0.25, bargroupgap=0.18,
            xaxis=dict(title="Trade Size Buckets", categoryorder="array", categoryarray=bucket_order),
            yaxis=dict(title="Avg. Slippage (bps)", tickformat=".2f", color="#E63946"),
            yaxis2=dict(title="Trade Count", overlaying="y", side="right", showgrid=False, color="#3A86FF"),
            legend=dict(orientation="h", y=1.08)
        )
        st.plotly_chart(fig, use_container_width=True)

        # Optional compact table (Avg + P90/P95 if present)
        c_p90_bps = _pick(colmap,"p90_abs_slippage_bps"); c_p90_pct = _pick(colmap,"p90_abs_slippage_pct")
        c_p95_bps = _pick(colmap,"p95_abs_slippage_bps"); c_p95_pct = _pick(colmap,"p95_abs_slippage_pct")
        tbl = agg[["SIZE_BUCKET","AVG_ABS_SLIPPAGE_BPS","TRADE_COUNT"]].copy()
        tbl.rename(columns={"SIZE_BUCKET":"Trade Size","AVG_ABS_SLIPPAGE_BPS":"Avg (bps)","TRADE_COUNT":"Trades"}, inplace=True)

        def weighted(series, weights):
            return np.average(series, weights=np.clip(weights,1,None)) if len(series) else np.nan

        if c_p90_bps or c_p90_pct:
            s = safe_num(dfld_raw[c_p90_bps]) if c_p90_bps else safe_num(dfld_raw[c_p90_pct])*100.0
            p90 = dfld_raw.assign(_size=size, _w=count).groupby("_size").apply(lambda g: weighted(s.loc[g.index], count.loc[g.index])).reset_index()
            p90.columns = ["Trade Size","P90 (bps)"]; tbl = tbl.merge(p90, on="Trade Size", how="left")
        if c_p95_bps or c_p95_pct:
            s = safe_num(dfld_raw[c_p95_bps]) if c_p95_bps else safe_num(dfld_raw[c_p95_pct])*100.0
            p95 = dfld_raw.assign(_size=size, _w=count).groupby("_size").apply(lambda g: weighted(s.loc[g.index], count.loc[g.index])).reset_index()
            p95.columns = ["Trade Size","P95 (bps)"]; tbl = tbl.merge(p95, on="Trade Size", how="left")

        for col in tbl.columns:
            if "bps" in col.lower() or "avg" in col.lower():
                tbl[col] = pd.to_numeric(tbl[col], errors="coerce").map(lambda v: f"{v:.2f}" if pd.notna(v) else "—")
        tbl["Trades"] = pd.to_numeric(tbl["Trades"], errors="coerce").map(lambda v: f"{int(v):,}" if pd.notna(v) else "—")
        st.markdown("**🎯 Slippage Performance by Trade Size**")
        st.dataframe(tbl, use_container_width=True, hide_index=True)

        st.markdown(
            f"<div class='card'><strong>Key Insights.</strong> Weighted slippage ≈ <strong>{wavg_slip:.2f} bps</strong>. "
            "Depth is solid for small–medium swaps; larger sizes rise but remain contained. Retail-size buckets dominate volume.</div>",
            unsafe_allow_html=True
        )

st.markdown("<hr class='soft'/>", unsafe_allow_html=True)

# =======================================================
# 4) Revenue Sustainability — Chart 4 (bars + net line)
# =======================================================
st.markdown('<div class="block-title">4. Revenue Sustainability</div>', unsafe_allow_html=True)
st.markdown('<div class="block-sub"><strong>Definition:</strong> Do protocol revenues (trading + staking fees) cover incentives? RSR &gt; 1 indicates sustainability.</div>', unsafe_allow_html=True)

dfr = load_csv(FILES["rev"])
if not dfr.empty and all(c in dfr.columns for c in ["DATE","TRADING_FEE_REVENUE_USD","STAKING_FEE_REVENUE_USD","NET_REVENUE_USD","LIQUIDITY_INCENTIVES_USD"]):
    dfr = dfr.sort_values("DATE")
    trading = safe_num(dfr["TRADING_FEE_REVENUE_USD"])
    staking = safe_num(dfr["STAKING_FEE_REVENUE_USD"])
    incent  = safe_num(dfr["LIQUIDITY_INCENTIVES_USD"])
    netrev  = safe_num(dfr["NET_REVENUE_USD"])

    total_rev = trading.sum() + staking.sum()
    total_inc = incent.sum()
    rsr = (total_rev/total_inc) if total_inc else np.nan
    k1,k2,k3 = st.columns(3)
    with k1: metric_box("Total Protocol Revenue", f"${total_rev:,.0f}", "border-b")
    with k2: metric_box("Total Incentives Paid", f"${total_inc:,.0f}", "border-e")
    with k3: metric_box("Revenue / Incentives", f"{rsr:.2f}" if pd.notna(rsr) else "—", "border-a")

    fig = go.Figure()
    # three BARS
    fig.add_trace(go.Bar(x=dfr["DATE"], y=trading, name="Trading Fees", marker_color="#43AA8B"))
    fig.add_trace(go.Bar(x=dfr["DATE"], y=staking, name="Staking Fees", marker_color="#1B5E20"))
    fig.add_trace(go.Bar(x=dfr["DATE"], y=incent,  name="Liquidity Incentives", marker_color="#F94144"))
    # net revenue LINE on y2
    fig.add_trace(go.Scatter(x=dfr["DATE"], y=netrev, name="Net Revenue", yaxis="y2",
                             line=dict(color="#277DA1", dash="dot", width=3)))
    fig.update_layout(
        title="Daily Revenue vs Incentives and Net Revenue",
        hovermode="x unified",
        barmode="group",
        xaxis_title="Date",
        yaxis=dict(title="Fees/Incentives (USD)"),
        yaxis2=dict(title="Net Revenue (USD)", overlaying="y", side="right", showgrid=False),
        legend=dict(orientation="h")
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Revenue CSV missing required columns.")

st.markdown("<hr class='soft'/>", unsafe_allow_html=True)

# =======================================================
# 5) Systemic Risk — Charts 5 & 6 (order flipped)
# =======================================================
st.markdown('<div class="block-title">5. Systemic Risk — Liquidation Exposure</div>', unsafe_allow_html=True)
st.markdown('<div class="block-sub"><strong>Definition:</strong> Current LTV profile and stress (% loans liquidated) under APT price shocks.</div>', unsafe_allow_html=True)

dfs = load_csv(FILES["risk"])
if not dfs.empty:
    # (a) Current LTV distribution — show FIRST
    if "LTV_BUCKET" in dfs.columns and "POSITION_COUNT" in dfs.columns:
        by_bucket = dfs.groupby("LTV_BUCKET")["POSITION_COUNT"].sum().reset_index()
        dist = px.bar(by_bucket, x="LTV_BUCKET", y="POSITION_COUNT",
                      labels={"POSITION_COUNT":"# Loans"}, title="Current LTV Distribution")
        dist.update_traces(marker_color=["#8BC34A","#FFEB3B","#FF9800","#E57373"])
        st.plotly_chart(dist, use_container_width=True)

    # (b) Stress test bar — SECOND
    if all(c in dfs.columns for c in ["PCT_LIQUIDATED_15PCT","PCT_LIQUIDATED_30PCT"]):
        stress = pd.DataFrame({
            "Scenario": ["-15% APT Drop","-30% APT Drop"],
            "Pct": [safe_num(dfs["PCT_LIQUIDATED_15PCT"]).mean(),
                    safe_num(dfs["PCT_LIQUIDATED_30PCT"]).mean()]
        })
        bar = px.bar(stress, y="Scenario", x="Pct", orientation="h",
                     labels={"Pct":"% Loans Liquidated"},
                     title="Stress Test: % Loans Liquidated")
        bar.update_traces(text=stress["Pct"].map(lambda v: f"{v:.1f}%"),
                          textposition="outside",
                          marker_color=["#FBC02D","#D81B60"])
        st.plotly_chart(bar, use_container_width=True)

st.markdown("<hr class='soft'/>", unsafe_allow_html=True)

# =======================================================
# 6) Global Health vs Lending Protocols — Chart 7 (single radar)
# =======================================================
st.markdown('<div class="block-title">6. Global Health (Radar) — with Lending Overlays</div>', unsafe_allow_html=True)
st.markdown('<div class="block-sub"><strong>Definition:</strong> Composite across Efficiency, Liquidity, User Growth, and Risk Management. Overlays two lending protocols for context.</div>', unsafe_allow_html=True)

df_global = load_csv(FILES["prot"])
df_lend   = load_csv(FILES["lend"])

have_global = (not df_global.empty and all(c in df_global.columns for c in
                  ["EFFICIENCY_SCORE","LIQUIDITY_SCORE","USER_GROWTH_SCORE","RISK_MANAGEMENT_SCORE"]))
have_lend = (not df_lend.empty and all(c in df_lend.columns for c in
                ["PROTOCOL_NAME","EFFICIENCY_SCORE","LIQUIDITY_SCORE","USER_GROWTH_SCORE","RISK_MANAGEMENT_SCORE"]))

if have_global:
    categories = ["Efficiency","Liquidity","User Growth","Risk Mgmt"]
    overall = [
        safe_num(df_global["EFFICIENCY_SCORE"]).mean(),
        safe_num(df_global["LIQUIDITY_SCORE"]).mean(),
        safe_num(df_global["USER_GROWTH_SCORE"]).mean(),
        safe_num(df_global["RISK_MANAGEMENT_SCORE"]).mean(),
    ]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=overall+[overall[0]], theta=categories+[categories[0]],
                                  fill="toself", name="Global", line=dict(color="#42A5F5"), opacity=0.6))
    if have_lend:
        # choose Aries & Echelon if present, else top-2 by STAPT_TVL_USD or OVERALL_HEALTH_SCORE
        names = df_lend["PROTOCOL_NAME"].str.lower()
        pick = []
        for target in ["aries","echelon"]:
            m = df_lend[names==target]
            if not m.empty: pick.append(m.iloc[0])
        if len(pick) < 2:
            key = "STAPT_TVL_USD" if "STAPT_TVL_USD" in df_lend.columns else "OVERALL_HEALTH_SCORE"
            df2 = df_lend.sort_values(key, ascending=False).head(2)
            for _,row in df2.iterrows():
                if row not in pick: pick.append(row)
        # add two overlays
        for row in pick[:2]:
            row = pd.Series(row)
            vals = [row["EFFICIENCY_SCORE"],row["LIQUIDITY_SCORE"],row["USER_GROWTH_SCORE"],row["RISK_MANAGEMENT_SCORE"]]
            fig.add_trace(go.Scatterpolar(r=vals+[vals[0]], theta=categories+[categories[0]],
                                          name=str(row["PROTOCOL_NAME"]).title()))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0,100])),
                      legend=dict(orientation="h"))
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Global health CSV missing expected score columns.")

st.markdown("<hr class='soft'/>", unsafe_allow_html=True)

# =======================================================
# 8) User Behavior — Chart 8 (+ KPIs)
# =======================================================
st.markdown('<div class="block-title">7. User Behavior Distribution</div>', unsafe_allow_html=True)
st.markdown('<div class="block-sub"><strong>Definition:</strong> Mix of balanced traders vs net buyers/sellers indicates stability and organic demand.</div>', unsafe_allow_html=True)

dfb = load_csv(FILES["beh"])
if not dfb.empty and all(c in dfb.columns for c in ["BEHAVIOR_TYPE","USER_COUNT_BY_TYPE"]):
    # KPIs (no extra chart)
    total_users = int(safe_num(dfb["USER_COUNT_BY_TYPE"]).sum())
    dominant = dfb.loc[safe_num(dfb["USER_COUNT_BY_TYPE"]).idxmax(), "BEHAVIOR_TYPE"]
    # Shannon evenness (0..1) – how balanced the distribution is
    p = safe_num(dfb["USER_COUNT_BY_TYPE"]) / max(total_users,1)
    entropy = -np.nansum([pi*np.log(pi) for pi in p if pi>0])
    evenness = float(entropy/np.log(len(p))) if len(p)>1 else 1.0
    k1,k2,k3 = st.columns(3)
    with k1: metric_box("Total Users (segmented)", f"{total_users:,}", "border-a")
    with k2: metric_box("Dominant Cohort", str(dominant), "border-b")
    with k3: metric_box("Evenness Score (0–1)", f"{evenness:.2f}", "border-c")

    pie = px.pie(dfb, names="BEHAVIOR_TYPE", values="USER_COUNT_BY_TYPE", hole=0.45, title="Behavior Split")
    st.plotly_chart(pie, use_container_width=True)
else:
    st.info("User behavior CSV missing required columns.")

st.markdown("<hr class='soft'/>", unsafe_allow_html=True)

# -------------------
# Conclusion
# -------------------
st.subheader("🔑 Key Findings & Closing")
st.markdown("""
- **Peg & Liquidity:** stAPT tracks APT with a modest premium; execution quality is strong for small–medium trades (low bps slippage).  
- **Efficiency:** Volume/TVL improving; Fees/TVL thin — the flywheel depends on organic usage growth.  
- **Sustainability:** Incentives remain meaningful; monitor RSR trend for durability as fees scale.  
- **Risk:** High-LTV bands carry liquidation risk under shocks; lending diversification helps.  
- **Global Health vs Protocols:** Global profile is strong on Liquidity/Efficiency; selected lending protocols cluster near the global envelope.

**Takeaway:** stAPT is maturing into a credible base asset on Aptos. Deepening depth at larger sizes and steadily improving revenue coverage are the next milestones to cement sustainability.
""")
st.caption("Built by Adrià Parcerisas • Data via Flipside/Dune CSV exports • 8 charts total.")
