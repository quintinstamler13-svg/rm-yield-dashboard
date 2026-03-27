import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SK RM Yield Dashboard | JGL Capital",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Brand colors ──────────────────────────────────────────────────────────────
GOLD    = "#f5b335"
GOLD_LT = "#ffdf87"
BLACK   = "#000000"
WHITE   = "#ffffff"
OFFWHITE= "#faf8f3"
SLATE   = "#2c2c2c"
SLATE_M = "#4a4a4a"
MUTED   = "#8a8a8a"
GREEN   = "#3d8a5e"
RED     = "#c0392b"

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600;700&family=DM+Mono:wght@400;500&display=swap');

  html, body, [class*="css"] {{
    font-family: 'Sora', sans-serif;
    background-color: {OFFWHITE};
  }}
  .stApp {{ background-color: {OFFWHITE}; }}

  /* Sidebar */
  section[data-testid="stSidebar"] {{
    background-color: {BLACK};
    border-right: 3px solid {GOLD};
  }}
  section[data-testid="stSidebar"] * {{ color: {WHITE} !important; }}
  section[data-testid="stSidebar"] .stSelectbox label,
  section[data-testid="stSidebar"] .stSlider label {{
    color: {GOLD_LT} !important;
    font-size: 0.78rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    font-weight: 600;
  }}

  /* Header bar */
  .header-bar {{
    background: {BLACK};
    padding: 1.1rem 2rem;
    border-bottom: 3px solid {GOLD};
    margin-bottom: 1.5rem;
    border-radius: 0 0 6px 6px;
  }}
  .header-bar h1 {{
    color: {GOLD};
    font-size: 1.55rem;
    font-weight: 700;
    margin: 0;
    letter-spacing: -0.02em;
  }}
  .header-bar p {{
    color: {GOLD_LT};
    font-size: 0.82rem;
    margin: 0.2rem 0 0 0;
    opacity: 0.85;
  }}

  /* KPI cards */
  .kpi-grid {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin-bottom: 1.5rem;
  }}
  .kpi-card {{
    background: {WHITE};
    border: 1px solid #e8e4d8;
    border-top: 4px solid {GOLD};
    border-radius: 6px;
    padding: 1rem 1.2rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
  }}
  .kpi-label {{
    font-size: 0.72rem;
    color: {MUTED};
    text-transform: uppercase;
    letter-spacing: 0.07em;
    font-weight: 600;
    margin-bottom: 0.25rem;
  }}
  .kpi-value {{
    font-size: 1.6rem;
    font-weight: 700;
    color: {SLATE};
    font-family: 'DM Mono', monospace;
    line-height: 1.1;
  }}
  .kpi-sub {{
    font-size: 0.75rem;
    color: {MUTED};
    margin-top: 0.2rem;
  }}
  .kpi-pos {{ color: {GREEN}; }}
  .kpi-neg {{ color: {RED}; }}

  /* Section labels */
  .section-label {{
    font-size: 0.72rem;
    color: {MUTED};
    text-transform: uppercase;
    letter-spacing: 0.1em;
    font-weight: 600;
    margin: 1.5rem 0 0.6rem 0;
    border-left: 3px solid {GOLD};
    padding-left: 0.6rem;
  }}

  /* Table */
  .dataframe {{ font-family: 'DM Mono', monospace !important; font-size: 0.82rem; }}

  /* Plotly chart containers */
  .chart-container {{
    background: {WHITE};
    border: 1px solid #e8e4d8;
    border-radius: 6px;
    padding: 1rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    margin-bottom: 1rem;
  }}

  /* Info box */
  .info-box {{
    background: #fffbf0;
    border: 1px solid {GOLD_LT};
    border-left: 4px solid {GOLD};
    border-radius: 4px;
    padding: 0.75rem 1rem;
    font-size: 0.83rem;
    color: {SLATE_M};
    margin-bottom: 1rem;
  }}

  /* Hide Streamlit branding */
  #MainMenu {{ visibility: hidden; }}
  footer {{ visibility: hidden; }}
  .stDeployButton {{ display: none; }}
</style>
""", unsafe_allow_html=True)


# ── Load data ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("rm_yields_long.csv")
    df["RM"] = df["RM"].astype(int)
    df["Year"] = df["Year"].astype(int)
    df["Yield"] = pd.to_numeric(df["Yield"], errors="coerce")
    df = df.dropna(subset=["Yield"])
    df = df[df["Yield"] > 0]
    return df

df = load_data()
all_rms   = sorted(df["RM"].unique())
all_crops = sorted(df["Crop"].unique())

# Crop display order (most common first)
CROP_ORDER = ["Canola","Spring Wheat","Barley","Oats","Durum","Lentils","Peas",
              "Flax","Fall Rye","Winter Wheat","Mustard","Canary Seed",
              "Tame Hay","Chickpeas","Sunflowers","Spring Rye"]
ordered_crops = [c for c in CROP_ORDER if c in all_crops]

# Provincial averages
@st.cache_data
def get_prov_avg():
    return df.groupby(["Year", "Crop"])["Yield"].mean().reset_index().rename(columns={"Yield": "Prov_Avg"})

prov_avg = get_prov_avg()


# ── Sidebar controls ──────────────────────────────────────────────────────────
st.sidebar.markdown(f"""
<div style="padding: 1rem 0 1.5rem 0; border-bottom: 1px solid #333; margin-bottom: 1.5rem;">
  <div style="font-size:1.3rem; font-weight:700; color:{GOLD}; letter-spacing:-0.02em;">JGL Capital</div>
  <div style="font-size:0.75rem; color:#888; margin-top:0.2rem;">RM Yield Analytics</div>
</div>
""", unsafe_allow_html=True)

selected_rm   = st.sidebar.selectbox("Select Rural Municipality (RM)", all_rms, index=0)
selected_crop = st.sidebar.selectbox("Select Crop", ordered_crops, index=0)

# Year range filter
min_year = int(df["Year"].min())
max_year = int(df["Year"].max())
year_range = st.sidebar.slider("Year Range", min_year, max_year, (1990, max_year))

# Rolling average toggle
show_rolling = st.sidebar.checkbox("Show 5-Year Rolling Average", value=True)

# Multi-RM comparison
st.sidebar.markdown(f'<div style="margin-top:1.5rem; border-top:1px solid #333; padding-top:1rem; font-size:0.72rem; color:{GOLD_LT}; text-transform:uppercase; letter-spacing:0.07em; font-weight:600;">Compare Additional RMs</div>', unsafe_allow_html=True)
compare_rms = st.sidebar.multiselect(
    "Add RMs to Compare (max 3)",
    [r for r in all_rms if r != selected_rm],
    max_selections=3,
    help="Overlay up to 3 other RMs on the time series chart"
)

st.sidebar.markdown(f"""
<div style="margin-top:2rem; padding-top:1rem; border-top:1px solid #333; font-size:0.72rem; color:#555; line-height:1.6;">
  Data: Saskatchewan Crop Insurance<br>
  {min_year} – {max_year} | {len(all_rms)} RMs
</div>
""", unsafe_allow_html=True)


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="header-bar">
  <h1>🌾 Your Local Yield vs. Saskatchewan Average</h1>
  <p>RM {selected_rm} · {selected_crop} · {year_range[0]}–{year_range[1]}</p>
</div>
""", unsafe_allow_html=True)


# ── Filter data for selection ─────────────────────────────────────────────────
def get_rm_data(rm, crop, yr_range):
    mask = (
        (df["RM"] == rm) &
        (df["Crop"] == crop) &
        (df["Year"] >= yr_range[0]) &
        (df["Year"] <= yr_range[1])
    )
    return df[mask].sort_values("Year")

def get_prov_data(crop, yr_range):
    mask = (
        (prov_avg["Crop"] == crop) &
        (prov_avg["Year"] >= yr_range[0]) &
        (prov_avg["Year"] <= yr_range[1])
    )
    return prov_avg[mask].sort_values("Year")

rm_data   = get_rm_data(selected_rm, selected_crop, year_range)
prov_data = get_prov_data(selected_crop, year_range)

merged = pd.merge(rm_data[["Year","Yield"]], prov_data, on="Year", how="inner")
merged["Diff_abs"]  = merged["Yield"] - merged["Prov_Avg"]
merged["Diff_pct"]  = (merged["Diff_abs"] / merged["Prov_Avg"]) * 100
merged["Roll5_RM"]  = merged["Yield"].rolling(5, min_periods=3).mean()
merged["Roll5_Prov"]= merged["Prov_Avg"].rolling(5, min_periods=3).mean()


# ── KPI cards ─────────────────────────────────────────────────────────────────
if len(merged) > 0:
    last = merged.iloc[-1]
    last_yr    = int(last["Year"])
    rm_yield   = last["Yield"]
    prov_yield = last["Prov_Avg"]
    diff_abs   = last["Diff_abs"]
    diff_pct   = last["Diff_pct"]
    avg_rm     = merged["Yield"].mean()
    volatility = merged["Yield"].std()

    diff_class = "kpi-pos" if diff_abs >= 0 else "kpi-neg"
    diff_arrow = "▲" if diff_abs >= 0 else "▼"
    vol_pct    = (volatility / avg_rm * 100) if avg_rm > 0 else 0

    # Percentile rank of selected RM vs all RMs for latest year
    all_rm_latest = df[(df["Crop"] == selected_crop) & (df["Year"] == last_yr)]["Yield"]
    if len(all_rm_latest) > 1:
        pctile = round(np.sum(all_rm_latest <= rm_yield) / len(all_rm_latest) * 100)
        pctile_str = f"{pctile}<span style='font-size:0.9rem'>th</span> percentile"
        rank_sub = f"vs {len(all_rm_latest)} RMs in {last_yr}"
    else:
        pctile_str = "—"
        rank_sub = ""

    st.markdown(f"""
    <div class="kpi-grid">
      <div class="kpi-card">
        <div class="kpi-label">RM {selected_rm} Yield ({last_yr})</div>
        <div class="kpi-value">{rm_yield:.1f}</div>
        <div class="kpi-sub">bu/ac · {selected_crop}</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">SK Provincial Average</div>
        <div class="kpi-value">{prov_yield:.1f}</div>
        <div class="kpi-sub">bu/ac · {last_yr}</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">vs. Provincial Average</div>
        <div class="kpi-value {diff_class}">{diff_arrow} {abs(diff_abs):.1f} bu/ac</div>
        <div class="kpi-sub {diff_class}">{diff_pct:+.1f}% above/below average</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Provincial Rank ({last_yr})</div>
        <div class="kpi-value">{pctile_str}</div>
        <div class="kpi-sub">{rank_sub}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f'<div class="info-box">⚠️ No data available for RM {selected_rm} — {selected_crop} in the selected year range. Try adjusting the filters.</div>', unsafe_allow_html=True)


# ── Chart 1: Time Series ──────────────────────────────────────────────────────
st.markdown('<div class="section-label">Historical Yield Comparison</div>', unsafe_allow_html=True)

if len(merged) > 0:
    fig_ts = go.Figure()

    # Shaded band: prov avg ± std for context
    prov_all = df[(df["Crop"] == selected_crop) & (df["Year"] >= year_range[0]) & (df["Year"] <= year_range[1])]
    prov_band = prov_all.groupby("Year")["Yield"].agg(["mean","std"]).reset_index()
    prov_band["upper"] = prov_band["mean"] + prov_band["std"]
    prov_band["lower"] = (prov_band["mean"] - prov_band["std"]).clip(lower=0)

    fig_ts.add_trace(go.Scatter(
        x=pd.concat([prov_band["Year"], prov_band["Year"][::-1]]),
        y=pd.concat([prov_band["upper"], prov_band["lower"][::-1]]),
        fill="toself",
        fillcolor="rgba(255,223,135,0.18)",
        line=dict(color="rgba(255,223,135,0)"),
        showlegend=True,
        name="SK ±1 Std Dev Band",
        hoverinfo="skip"
    ))

    # Provincial average line
    fig_ts.add_trace(go.Scatter(
        x=prov_data["Year"], y=prov_data["Prov_Avg"].round(1),
        mode="lines",
        name="SK Provincial Average",
        line=dict(color=GOLD_LT, width=2, dash="dot"),
        hovertemplate="<b>SK Avg</b><br>Year: %{x}<br>Yield: %{y:.1f} bu/ac<extra></extra>"
    ))

    # Compare RMs
    COMP_COLORS = ["#6c9ecf", "#9b7ec8", "#5dba82"]
    for i, crm in enumerate(compare_rms):
        crm_data = get_rm_data(crm, selected_crop, year_range)
        if len(crm_data) > 0:
            fig_ts.add_trace(go.Scatter(
                x=crm_data["Year"], y=crm_data["Yield"].round(1),
                mode="lines+markers",
                name=f"RM {crm}",
                line=dict(color=COMP_COLORS[i % len(COMP_COLORS)], width=1.5),
                marker=dict(size=4),
                hovertemplate=f"<b>RM {crm}</b><br>Year: %{{x}}<br>Yield: %{{y:.1f}} bu/ac<extra></extra>"
            ))

    # Rolling average for primary RM
    if show_rolling and len(merged) >= 3:
        fig_ts.add_trace(go.Scatter(
            x=merged["Year"], y=merged["Roll5_RM"].round(1),
            mode="lines",
            name=f"RM {selected_rm} – 5yr Avg",
            line=dict(color=GOLD, width=2, dash="longdash"),
            opacity=0.7,
            hovertemplate=f"<b>RM {selected_rm} 5yr Avg</b><br>Year: %{{x}}<br>Yield: %{{y:.1f}} bu/ac<extra></extra>"
        ))

    # Primary RM line (on top)
    fig_ts.add_trace(go.Scatter(
        x=merged["Year"], y=merged["Yield"].round(1),
        mode="lines+markers",
        name=f"RM {selected_rm}",
        line=dict(color=GOLD, width=3),
        marker=dict(size=5, color=GOLD, line=dict(color=BLACK, width=1)),
        hovertemplate=f"<b>RM {selected_rm}</b><br>Year: %{{x}}<br>Yield: %{{y:.1f}} bu/ac<extra></extra>"
    ))

    fig_ts.update_layout(
        title=dict(text=f"RM {selected_rm} vs. Saskatchewan Average — {selected_crop}", font=dict(size=14, color=SLATE), x=0),
        xaxis=dict(title="Year", gridcolor="#eeece6", tickfont=dict(size=11)),
        yaxis=dict(title="Yield (bu/ac)", gridcolor="#eeece6", tickfont=dict(size=11), zeroline=False),
        plot_bgcolor=WHITE,
        paper_bgcolor=WHITE,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, font=dict(size=11)),
        hovermode="x unified",
        height=400,
        margin=dict(t=60, b=40, l=60, r=20),
        font=dict(family="Sora, sans-serif")
    )

    st.plotly_chart(fig_ts, use_container_width=True)


# ── Chart 2: Relative Performance ─────────────────────────────────────────────
st.markdown('<div class="section-label">Relative Performance vs. Provincial Average</div>', unsafe_allow_html=True)

if len(merged) > 0:
    col1, col2 = st.columns([2, 1])

    with col1:
        # Bar chart of % difference
        colors = [GREEN if v >= 0 else RED for v in merged["Diff_pct"]]
        fig_diff = go.Figure()
        fig_diff.add_trace(go.Bar(
            x=merged["Year"],
            y=merged["Diff_pct"].round(1),
            marker_color=colors,
            marker_line_color="rgba(0,0,0,0.1)",
            marker_line_width=0.5,
            name="% vs SK Avg",
            hovertemplate="<b>%{x}</b><br>%{y:+.1f}% vs SK avg<extra></extra>"
        ))
        fig_diff.add_hline(y=0, line_color=BLACK, line_width=1)
        fig_diff.update_layout(
            title=dict(text="Annual % Difference from Provincial Average", font=dict(size=13, color=SLATE), x=0),
            xaxis=dict(title="Year", gridcolor="#eeece6"),
            yaxis=dict(title="% Difference", gridcolor="#eeece6", tickformat="+.0f", ticksuffix="%", zeroline=False),
            plot_bgcolor=WHITE,
            paper_bgcolor=WHITE,
            height=300,
            margin=dict(t=50, b=40, l=60, r=20),
            showlegend=False,
            font=dict(family="Sora, sans-serif")
        )
        st.plotly_chart(fig_diff, use_container_width=True)

    with col2:
        # Summary stats table
        st.markdown('<div style="margin-top:0.5rem;">', unsafe_allow_html=True)
        above = (merged["Diff_pct"] > 0).sum()
        below = (merged["Diff_pct"] <= 0).sum()
        avg_outperform = merged.loc[merged["Diff_pct"] > 0, "Diff_pct"].mean()
        avg_underperform = merged.loc[merged["Diff_pct"] <= 0, "Diff_pct"].mean()
        best_yr = merged.loc[merged["Diff_pct"].idxmax(), "Year"]
        worst_yr = merged.loc[merged["Diff_pct"].idxmin(), "Year"]
        best_val = merged["Diff_pct"].max()
        worst_val = merged["Diff_pct"].min()

        stats_md = f"""
<div class="kpi-card" style="margin-top:0.5rem;">
  <div class="kpi-label">Performance Summary</div>
  <table style="width:100%; font-size:0.8rem; color:{SLATE_M}; border-collapse:collapse; margin-top:0.5rem; font-family:'DM Mono',monospace;">
    <tr><td style="padding:3px 0; color:{MUTED};">Years above avg</td><td style="text-align:right; color:{GREEN}; font-weight:600;">{above}</td></tr>
    <tr><td style="padding:3px 0; color:{MUTED};">Years below avg</td><td style="text-align:right; color:{RED}; font-weight:600;">{below}</td></tr>
    <tr><td style="padding:3px 0; color:{MUTED};">Avg outperformance</td><td style="text-align:right; color:{GREEN};">{avg_outperform:+.1f}%</td></tr>
    <tr><td style="padding:3px 0; color:{MUTED};">Avg underperformance</td><td style="text-align:right; color:{RED};">{avg_underperform:+.1f}%</td></tr>
    <tr><td style="padding:3px 0; color:{MUTED};">Best year</td><td style="text-align:right;">{int(best_yr)} ({best_val:+.1f}%)</td></tr>
    <tr><td style="padding:3px 0; color:{MUTED};">Worst year</td><td style="text-align:right;">{int(worst_yr)} ({worst_val:+.1f}%)</td></tr>
    <tr><td style="padding:3px 0; color:{MUTED};">Yield volatility (σ)</td><td style="text-align:right;">{merged['Yield'].std():.1f} bu/ac</td></tr>
    <tr><td style="padding:3px 0; color:{MUTED};">Coeff. of variation</td><td style="text-align:right;">{merged['Yield'].std()/merged['Yield'].mean()*100:.1f}%</td></tr>
  </table>
</div>
        """
        st.markdown(stats_md, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)


# ── Chart 3: Distribution / RM Ranking ────────────────────────────────────────
st.markdown('<div class="section-label">How Does RM Rank Among All Saskatchewan RMs?</div>', unsafe_allow_html=True)

if len(merged) > 0:
    latest_year = int(merged["Year"].max())
    dist_data = df[(df["Crop"] == selected_crop) & (df["Year"] == latest_year)]["Yield"].dropna()

    if len(dist_data) > 5:
        rm_val_latest = merged.loc[merged["Year"] == latest_year, "Yield"]
        rm_val = float(rm_val_latest.values[0]) if len(rm_val_latest) > 0 else None

        fig_dist = go.Figure()
        fig_dist.add_trace(go.Histogram(
            x=dist_data,
            nbinsx=30,
            marker_color=GOLD_LT,
            marker_line_color=GOLD,
            marker_line_width=0.8,
            name="All SK RMs",
            hovertemplate="Yield range: %{x}<br>Count: %{y} RMs<extra></extra>"
        ))

        if rm_val is not None:
            fig_dist.add_vline(
                x=rm_val,
                line_color=GOLD,
                line_width=3,
                annotation_text=f"RM {selected_rm}: {rm_val:.1f} bu/ac",
                annotation_position="top right",
                annotation_font=dict(color=SLATE, size=11, family="Sora"),
                annotation_bgcolor=GOLD_LT,
                annotation_bordercolor=GOLD
            )

        prov_val_latest = prov_data.loc[prov_data["Year"] == latest_year, "Prov_Avg"]
        if len(prov_val_latest) > 0:
            fig_dist.add_vline(
                x=float(prov_val_latest.values[0]),
                line_color=SLATE_M,
                line_width=2,
                line_dash="dash",
                annotation_text=f"SK Avg: {float(prov_val_latest.values[0]):.1f} bu/ac",
                annotation_position="top left",
                annotation_font=dict(color=MUTED, size=10, family="Sora"),
            )

        fig_dist.update_layout(
            title=dict(text=f"Distribution of {selected_crop} Yields Across All SK RMs — {latest_year}", font=dict(size=13, color=SLATE), x=0),
            xaxis=dict(title="Yield (bu/ac)", gridcolor="#eeece6"),
            yaxis=dict(title="Number of RMs", gridcolor="#eeece6"),
            plot_bgcolor=WHITE,
            paper_bgcolor=WHITE,
            height=300,
            margin=dict(t=50, b=40, l=60, r=20),
            showlegend=False,
            font=dict(family="Sora, sans-serif")
        )
        st.plotly_chart(fig_dist, use_container_width=True)


# ── Data table (expandable) ───────────────────────────────────────────────────
with st.expander("📋 View Raw Data Table"):
    display_df = merged[["Year","Yield","Prov_Avg","Diff_abs","Diff_pct"]].copy()
    display_df.columns = ["Year", f"RM {selected_rm} Yield (bu/ac)", "SK Avg (bu/ac)", "Difference (bu/ac)", "% Difference"]
    display_df = display_df.sort_values("Year", ascending=False)
    display_df["Year"] = display_df["Year"].astype(int)
    for col in display_df.columns[1:4]:
        display_df[col] = display_df[col].round(1)
    display_df["% Difference"] = display_df["% Difference"].round(1)

    def color_diff(val):
        color = GREEN if val > 0 else (RED if val < 0 else MUTED)
        return f"color: {color}; font-weight: 600"

    styled = display_df.style.applymap(color_diff, subset=["% Difference", "Difference (bu/ac)"])
    st.dataframe(styled, use_container_width=True, hide_index=True)

    # CSV download
    csv = display_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇ Download Table as CSV",
        data=csv,
        file_name=f"RM{selected_rm}_{selected_crop.replace(' ','_')}_yields.csv",
        mime="text/csv"
    )

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="margin-top:2rem; padding-top:1rem; border-top:1px solid #e0ddd5; display:flex; justify-content:space-between; align-items:center;">
  <div style="font-size:0.75rem; color:{MUTED};">
    Data source: Saskatchewan Crop Insurance Corporation &nbsp;|&nbsp; JGL Capital Advisory
  </div>
  <div style="font-size:0.75rem; color:{MUTED};">
    Yields in bushels per acre (bu/ac)
  </div>
</div>
""", unsafe_allow_html=True)
