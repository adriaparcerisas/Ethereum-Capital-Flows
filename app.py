# app.py — Ethereum On-Chain Traction at New High — Capital Flows & User Dynamics
# Light-only • single thin separator between sections • KPI inline style for shares

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
    page_title="Ethereum On-Chain Traction — Capital Flows & User Dynamics",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ──────────────────────────────────────────────────────────────────────────────
# Light theme (CSS)
# ──────────────────────────────────────────────────────────────────────────────
LIGHT_CSS = """
:root{
  --bg:#f6f8fe; --card:#ffffff; --deep:#f8fbff;
  --ink:#0b1220; --muted:#2d3a55; --line:#dbe5f6;
  --accent:#2563eb; --cyan:#0891b2; --teal:#14b8a6;
  --green:#15803d; --violet:#6d28d9; --blue:#1d4ed8;
}
html, body, [class*="css"] { background:var(--bg)!important; color:var(--ink)!important; }
a { color:var(--accent)!important; text-decoration:none; }
.h1{font-weight:900;font-size:1.9rem;letter-spacing:.2px;color:#0b1220;margin:8px 0 6px 0;}
.h1-sub{color:#3a4b6e;margin:0 0 14px 0;}

/* Targeta de secció amb vora completa (el “Executive Summary” tornarà a veure’s bé) */
.section{
  background:var(--card);
  border:1px solid var(--line);      /* vora a tots els costats */
  border-radius:14px;
  padding:14px;
  margin-bottom:0;
}

/* Quan ve una targeta després del separador fi, li traiem només la vora superior
   per evitar la doble línia (el separador ja fa de línia superior). */
.sep + .section { border-top:none !important; }

.section-title{color:var(--ink);font-size:1.25rem;font-weight:900;margin:0 0 8px 0;}
.section-def{
  display:block;border:1px solid var(--line);background:var(--deep);
  border-radius:12px;padding:12px 14px;color:#1f2a44;margin-bottom:0;
}
.def-pill{font-size:.78rem;font-weight:800;padding:2px 8px;border-radius:999px;background:#eef3ff;color:#24408f;border:1px solid var(--line);margin-right:10px;}

/* ÚNIC separador fi entre seccions */
.sep{border:none;height:1px;background:var(--line);margin:12px 0;}

.kpi{background:#f5f8ff;border:1px solid var(--line);border-radius:12px;padding:10px 12px;margin-top:10px;}
.kpi .lbl{font-weight:800;color:#12203a;font-size:.9rem;}
.kpi .val{font-weight:900;color:#0b1220;font-size:1.45rem;letter-spacing:.1px;margin-top:2px;}
.kpi.a{border-left:5px solid var(--teal);} .kpi.b{border-left:5px solid var(--violet);}
.kpi.c{border-left:5px solid var(--blue);} .kpi.d{border-left:5px solid var(--green);}

/* KPI inline AMB franja de color (com els KPI grans) */
.kpi-inline{
  background:#f5f8ff;border:1px solid var(--line);border-radius:12px;padding:10px 12px;margin-top:10px;
}
.kpi-inline .txt{font-weight:700;color:#12203a;font-size:1rem;}
.kpi-inline .txt .v{font-weight:800;color:#0b1220;}
.kpi-inline.a{border-left:5px solid var(--teal);}
.kpi-inline.b{border-left:5px solid var(--violet);}
.kpi-inline.c{border-left:5px solid var(--blue);}
.kpi-inline.d{border-left:5px solid var(--green);}

.insight{border:1px solid var(--line);background:#f2f6ff;color:#223355;border-radius:12px;padding:8px 10px;margin-top:10px;}
"""

st.markdown(f"<style>{LIGHT_CSS}</style>", unsafe_allow_html=True)

PLOTLY_TEMPLATE = "plotly_white"
def apply_plotly_theme(fig: go.Figure) -> go.Figure:
    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        paper_bgcolor="#ffffff", plot_bgcolor="#ffffff",
        font=dict(color="#0b1220"),
        legend=dict(bgcolor="rgba(255,255,255,0)", orientation="h"),
        xaxis=dict(gridcolor="#e7eefc", zerolinecolor="#e7eefc", linecolor="#dbe5f6"),
        yaxis=dict(gridcolor="#e7eefc", zerolinecolor="#e7eefc", linecolor="#dbe5f6"),
        margin=dict(l=10,r=10,t=30,b=10), hovermode="x unified",
    )
    return fig

# ──────────────────────────────────────────────────────────────────────────────
# Utils
# ──────────────────────────────────────────────────────────────────────────────
DATA_DIR = "data"

def load_csv(name: str) -> pd.DataFrame:
    path = os.path.join(DATA_DIR, name)
    if not os.path.isfile(path): return pd.DataFrame()
    with open(path, "rb") as f: raw = f.read()
    df = pd.DataFrame()
    for sep in [",",";","\t"]:
        try:
            _df = pd.read_csv(io.BytesIO(raw), sep=sep, engine="python")
            if _df.shape[1] > 1:
                df = _df; break
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
        st.markdown(f'<div class="section-def">{definition}</div>', unsafe_allow_html=True)

def end_section():
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<hr class="sep">', unsafe_allow_html=True)  # separador fi únic

def kpi(col, label, value, style="a"):
    with col:
        st.markdown(
            f'<div class="kpi {style}"><div class="lbl">{label}</div>'
            f'<div class="val">{value}</div></div>', unsafe_allow_html=True
        )

def kpi_inline(col, text, style="a"):
    with col:
        st.markdown(
            f'<div class="kpi-inline {style}"><div class="txt">{text}</div></div>',
            unsafe_allow_html=True
        )

def insight(text:str):
    st.markdown(f'<div class="insight"><strong>Insight.</strong> {text}</div>', unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# Header + Executive Summary (TOT dins “Context”)
# ──────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="h1">Ethereum On-Chain Traction at New High — Capital Flows & User Dynamics</div>', unsafe_allow_html=True)
st.markdown('<div class="h1-sub">Data as of most recent month available</div>', unsafe_allow_html=True)

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

# ──────────────────────────────────────────────────────────────────────────────
# 1) Monthly On-Chain USD Volume by Category
# ──────────────────────────────────────────────────────────────────────────────
section(
    "1. Monthly On-Chain USD Volume by Category",
    "Stacked on-chain volume (USD billions) by vertical; highlights peak throughput and category mix."
)

df_vol = load_csv("volume_category.csv")
if not df_vol.empty and all(c in df_vol.columns for c in ["MONTH","CATEGORY","VOLUME_USD_BILLIONS"]):
    df_vol["CATEGORY"] = df_vol["CATEGORY"].astype(str)
    total_by_month = df_vol.groupby("MONTH")["VOLUME_USD_BILLIONS"].sum()
    peak = total_by_month.max()

    mask_dex = df_vol["CATEGORY"].str.contains("DEX", case=False, na=False)
    dex_share = np.nan
    if mask_dex.any():
        latest_month = df_vol["MONTH"].max()
        sl = df_vol[df_vol["MONTH"]==latest_month]
        denom = sl["VOLUME_USD_BILLIONS"].sum()
        numer = sl[mask_dex]["VOLUME_USD_BILLIONS"].sum()
        dex_share = (numer/denom*100) if denom>0 else np.nan

    c1,c2 = st.columns([1,1])
    kpi(c1, "Peak Volume", f"${peak:,.2f}B" if pd.notna(peak) else "—", "a")
    kpi_inline(c2, f"DEX Dominance (latest): <span class='v'>{pct(dex_share,1)}</span>")

    fig = px.area(
        df_vol, x="MONTH", y="VOLUME_USD_BILLIONS", color="CATEGORY",
        labels={"VOLUME_USD_BILLIONS":"Volume (USD Billions)", "MONTH":"Month"},
        template=PLOTLY_TEMPLATE,
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    apply_plotly_theme(fig)
    st.plotly_chart(fig, use_container_width=True)
    insight("DeFi lending and DEX trading typically drive most on-chain flow; the mix contextualizes risk-on vs defensive phases.")
else:
    st.info("`data/volume_category.csv` missing required columns.")
end_section()

# ──────────────────────────────────────────────────────────────────────────────
# 2) Monthly Active Addresses vs Transactions (Toggle)
# ──────────────────────────────────────────────────────────────────────────────
section(
    "2. Monthly Active Addresses and Transactions by Category",
    "Choose one metric at a time to isolate user base (addresses) vs network load (transactions)."
)

df_act = load_csv("active_addresses.csv")
if not df_act.empty and all(c in df_act.columns for c in ["MONTH","CATEGORY","ACTIVE_ADDRESSES","TRANSACTIONS"]):
    df_act["CATEGORY"] = df_act["CATEGORY"].astype(str)
    metric = st.radio("Metric", ["Active Addresses", "Transactions"], horizontal=True, index=0, key="metric_act")
    if metric == "Active Addresses":
        series = df_act.groupby("MONTH")["ACTIVE_ADDRESSES"].sum()
        c1,c2 = st.columns(2)
        kpi(c1, "Peak Users (Monthly)", f"{int(series.max()):,}" if series.size else "—", "c")
        latest = df_act["MONTH"].max()
        sl = df_act[df_act["MONTH"]==latest]
        dex_share = (sl.loc[sl["CATEGORY"].str.contains("DEX",case=False), "ACTIVE_ADDRESSES"].sum()
                     / max(sl["ACTIVE_ADDRESSES"].sum(),1) * 100) if not sl.empty else np.nan
        kpi_inline(c2, f"DEX Users (latest): <span class='v'>{pct(dex_share,1)}</span>")

        piv = df_act.pivot_table(index="MONTH", columns="CATEGORY", values="ACTIVE_ADDRESSES", aggfunc="sum")
        fig = go.Figure()
        palette = ["#2563eb","#10b981","#7c3aed","#0ea5e9","#f97316","#22c55e","#1d4ed8"]
        for i,col in enumerate(piv.columns):
            fig.add_trace(go.Scatter(x=piv.index, y=piv[col], name=col, line=dict(width=2, color=palette[i%len(palette)])))
        apply_plotly_theme(fig)
        fig.update_layout(xaxis_title="Month", yaxis_title="Active Addresses")
        st.plotly_chart(fig, use_container_width=True)
    else:
        series = df_act.groupby("MONTH")["TRANSACTIONS"].sum()
        c1,c2 = st.columns(2)
        kpi(c1, "Peak TX (Monthly)", f"{int(series.max()):,}" if series.size else "—", "c")
        latest = df_act["MONTH"].max()
        sl = df_act[df_act["MONTH"]==latest]
        dex_share = (sl.loc[sl["CATEGORY"].str.contains("DEX",case=False), "TRANSACTIONS"].sum()
                     / max(sl["TRANSACTIONS"].sum(),1) * 100) if not sl.empty else np.nan
        kpi_inline(c2, f"DEX TX Share (latest): <span class='v'>{pct(dex_share,1)}</span>")

        piv = df_act.pivot_table(index="MONTH", columns="CATEGORY", values="TRANSACTIONS", aggfunc="sum")
        fig = go.Figure()
        palette = ["#2563eb","#10b981","#7c3aed","#0ea5e9","#f97316","#22c55e","#1d4ed8"]
        for i,col in enumerate(piv.columns):
            fig.add_trace(go.Scatter(x=piv.index, y=piv[col], name=col,
                                     line=dict(width=2, dash="dot", color=palette[i%len(palette)])))
        apply_plotly_theme(fig)
        fig.update_layout(xaxis_title="Month", yaxis_title="Transactions")
        st.plotly_chart(fig, use_container_width=True)
    insight("Addresses reflect breadth; transactions reflect intensity. Toggle helps attribute moves to usage vs throughput.")
else:
    st.info("`data/active_addresses.csv` missing required columns.")
end_section()

# ──────────────────────────────────────────────────────────────────────────────
# 3) User Mix — Cohorts & Typology (merged)
# ──────────────────────────────────────────────────────────────────────────────
section(
    "3. User Mix — Cohorts & Typology (Volume vs Activity)",
    "Two synchronized views per month: (A) evolution of unique users, (B) 100% stacked shares. Toggle the dimension."
)

df_coh = load_csv("user_cohort.csv")
df_typ = load_csv("user_typology.csv")
dim = st.radio("Dimension", ["Volume Cohorts", "Activity/Sector"], horizontal=True, index=0, key="mix_dim")

def _plot_evolution_and_share(df: pd.DataFrame, cat_col: str, count_col="UNIQUE_USERS",
                              title_a="Unique Users by Category", title_b="Category Share (100%)",
                              use_log=False, colors=None):
    piv = df.pivot_table(index="MONTH", columns=cat_col, values=count_col, aggfunc="sum").fillna(0)
    figA = go.Figure()
    cols = list(piv.columns)
    palette = colors or ["#2563eb","#10b981","#7c3aed","#0ea5e9","#f97316","#22c55e","#1d4ed8"]
    for i,col in enumerate(cols):
        figA.add_trace(go.Scatter(x=piv.index, y=piv[col], name=col,
                                  line=dict(width=2, color=palette[i%len(palette)])))
    apply_plotly_theme(figA)
    figA.update_layout(title=title_a, xaxis_title="Month", yaxis_title="Unique Users")
    if use_log: figA.update_yaxes(type="log", dtick=1)
    st.plotly_chart(figA, use_container_width=True)

    share = piv.apply(lambda r: (r / r.sum())*100 if r.sum()>0 else r, axis=1)
    melted = share.reset_index().melt("MONTH", var_name=cat_col, value_name="share")
    figB = px.bar(melted, x="MONTH", y="share", color=cat_col,
                  labels={"share":"% of Users"}, title=title_b,
                  template=PLOTLY_TEMPLATE,
                  color_discrete_sequence=palette)
    figB.update_layout(barmode="stack")
    apply_plotly_theme(figB)
    st.plotly_chart(figB, use_container_width=True)

if dim == "Volume Cohorts" and not df_coh.empty and all(c in df_coh.columns for c in ["MONTH","COHORT","UNIQUE_USERS","TOTAL_VOLUME"]):
    df_coh["COHORT"] = df_coh["COHORT"].astype(str)
    latest = df_coh["MONTH"].max()
    sl = df_coh[df_coh["MONTH"]==latest]
    whale_mask = sl["COHORT"].str.contains("whale", case=False, na=False)
    whale_share = (sl.loc[whale_mask,"UNIQUE_USERS"].sum() / max(sl["UNIQUE_USERS"].sum(),1) * 100) if not sl.empty else np.nan
    whale_avg_vol = (sl.loc[whale_mask,"TOTAL_VOLUME"].sum() /
                     max(sl.loc[whale_mask,"UNIQUE_USERS"].sum(),1)) if whale_mask.any() else np.nan

    c1,c2 = st.columns(2)
    kpi_inline(c1, f"Whale User Share (latest): <span class='v'>{pct(whale_share,1)}</span>")
    kpi_inline(c2, f"Whale Avg Volume (latest): <span class='v'>{money(whale_avg_vol,2)}</span>")

    _plot_evolution_and_share(df_coh, "COHORT",
                              title_a="Unique Users by Cohort",
                              title_b="Cohort Share (100%)",
                              use_log=False)
    insight("Cohorts reveal who drives participation. Whale concentration can lift $ volume while masking retail breadth.")

elif dim == "Activity/Sector" and not df_typ.empty and all(c in df_typ.columns for c in ["MONTH","USER_TYPE","ACTIVITY_LEVEL","UNIQUE_USERS","AVG_TRANSACTIONS_PER_USER"]):
    df_typ = df_typ.copy()
    df_typ["USER_TYPE"] = df_typ["USER_TYPE"].astype(str)
    df_typ["ACTIVITY_LEVEL"] = df_typ["ACTIVITY_LEVEL"].astype(str)
    df_typ["CATEGORY"] = df_typ["USER_TYPE"].str.strip() + " • " + df_typ["ACTIVITY_LEVEL"].str.strip()

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
    kpi_inline(c1, f"Multi-Sector User Share (latest): <span class='v'>{pct(multi_share,1)}</span>")
    kpi_inline(c2, f"Engagement Multiplier (Multi/Single): <span class='v'>{engagement_mult:.2f}×</span>")

    soft_palette = ["#0ea5e9","#7c3aed","#10b981","#2563eb","#22c55e","#1d4ed8","#f97316"]
    _plot_evolution_and_share(
        df_typ, "CATEGORY",
        title_a="Unique Users by Activity/Sector & Level (log scale)",
        title_b="Activity/Sector & Level — Share (100%)",
        use_log=True, colors=soft_palette
    )
    insight("Log scale exposes secondary segments when one cohort dominates. Palette evita que el grup majoritari tapi la resta.")
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
    kpi_inline(c2, f"Volume Growth (since start): <span class='v'>{pct(growth,1)}</span>")

    fig = go.Figure()
    fig.add_trace(go.Bar(x=df_dex["MONTH"], y=df_dex["TOTAL_VOLUME_BILLIONS"], name="DEX Volume (B)", marker_color="#2563eb"))
    fig.add_trace(go.Scatter(x=df_dex["MONTH"], y=df_dex["ACTIVE_SWAPPERS"], name="Active Swappers",
                             mode="lines", line=dict(width=3, color="#14b8a6"), yaxis="y2"))
    fig.update_layout(yaxis=dict(title="Volume (B)"),
                      yaxis2=dict(title="Active Swappers", overlaying="y", side="right"))
    apply_plotly_theme(fig)
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
    kpi_inline(c1, f"Top Platform Share (latest): <span class='v'>{pct(top_share,1)}</span>")
    kpi_inline(c2, f"Depositors Growth (since start): <span class='v'>{pct(dep_growth,1)}</span>")

    fig = px.area(df_len, x="MONTH", y="VOLUME_BILLIONS", color="PLATFORM",
                  labels={"VOLUME_BILLIONS":"Deposit Volume (B)"},
                  template=PLOTLY_TEMPLATE,
                  color_discrete_sequence=px.colors.qualitative.Set2)
    apply_plotly_theme(fig)
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
    kpi_inline(c1, f"Bridge Volume Growth: <span class='v'>{pct(growth,1)}</span>")
    kpi_inline(c2, f"Status: <span class='v'>{status}</span>")

    fig = px.line(df_bridge, x="MONTH", y="TOTAL_BRIDGE_VOLUME_BILLIONS",
                  labels={"TOTAL_BRIDGE_VOLUME_BILLIONS":"Total Bridge Volume (B)"},
                  markers=False, template=PLOTLY_TEMPLATE)
    fig.update_traces(line=dict(width=3, color="#2563eb"))
    apply_plotly_theme(fig)
    st.plotly_chart(fig, use_container_width=True)
    insight("Bridge activity trends upward; deeper breakdown by source/destination would clarify liquidity migration patterns.")
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
    kpi_inline(c1, f"Price Range: <span class='v'>{money(pr.min(),0)} – {money(pr.max(),0)}</span>")
    kpi_inline(c2, f"Corr(Price, Activity): <span class='v'>{corr_pa:.2f}</span>")

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_price["MONTH"], y=pr, name="ETH Price (USD)", line=dict(width=3, color="#2563eb")))
    fig.add_trace(go.Scatter(x=df_price["MONTH"], y=act, name="Activity Index", yaxis="y2",
                             line=dict(width=2, dash="dot", color="#10b981")))
    fig.update_layout(yaxis=dict(title="ETH Price (USD)"),
                      yaxis2=dict(title="Activity Index", overlaying="y", side="right"))
    apply_plotly_theme(fig)
    st.plotly_chart(fig, use_container_width=True)
    insight("Activity often follows price impulses (and sometimes leads); regime shifts can flip the relationship.")
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
        kpi_inline(c1, f"User Growth (since start): <span class='v'>{pct(ug,1)}</span>")
        kpi_inline(c2, f"Fee Change (since start): <span class='v'>{pct(fd,1)}</span>")

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_fee_act["MONTH"], y=users, name="Unique Users",
                                 line=dict(width=3), mode="lines+markers",
                                 marker=dict(symbol="circle-open"),
                                 line_color="#7c3aed"))
        fig.add_trace(go.Scatter(x=df_fee_act["MONTH"], y=fee_usd, name="Average Fee (USD)",
                                 yaxis="y2", line=dict(width=3), mode="lines+markers",
                                 marker=dict(symbol="diamond"),
                                 line_color="#0ea5e9"))
        fig.update_layout(xaxis_title="Month",
                          yaxis=dict(title="Unique Users"),
                          yaxis2=dict(title="Average Fee (USD)", overlaying="y", side="right"))
        apply_plotly_theme(fig)
        st.plotly_chart(fig, use_container_width=True)
        insight("Fee softening tends to unlock new cohorts; fee spikes dampen marginal adoption, especially for retail flows.")
    else:
        st.info("Could not find `UNIQUE_USERS/USERS_MILLIONS` and `AVG_FEE_USD` in fees CSVs.")
else:
    st.info("`data/fees_activity.csv` or `data/fees_price.csv` missing `MONTH`.")
end_section()

# ──────────────────────────────────────────────────────────────────────────────
# Footer
# ──────────────────────────────────────────────────────────────────────────────
st.markdown(
    '<div style="text-align:center;opacity:.85;margin-top:6px;">'
    'Built by Adrià Parcerisas • Data via Flipside/Dune exports • Streamlit + Plotly'
    '</div>', unsafe_allow_html=True
)

