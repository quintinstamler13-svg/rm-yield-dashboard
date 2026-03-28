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
  /* Make selectbox container grey so white text is readable */
  section[data-testid="stSidebar"] .stSelectbox > div > div,
  section[data-testid="stSidebar"] .stMultiSelect > div > div {{
    background-color: #3a3a3a !important;
  }}
  section[data-testid="stSidebar"] .stSelectbox label,
  section[data-testid="stSidebar"] .stMultiSelect label,
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
  [data-testid="stToolbar"] {{ display: none; }}
  [data-testid="manage-app-button"] {{ display: none; }}
  header [data-testid="stHeader"] {{ display: none; }}
  button[kind="header"] {{ display: none !important; }}
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

# ── Units per crop ─────────────────────────────────────────────────────────────
CROP_UNITS = {
    "Winter Wheat":  "bu/ac",
    "Canola":        "bu/ac",
    "Spring Wheat":  "bu/ac",
    "Mustard":       "lbs/ac",
    "Durum":         "bu/ac",
    "Sunflowers":    "lbs/ac",
    "Oats":          "bu/ac",
    "Lentils":       "lbs/ac",
    "Peas":          "bu/ac",
    "Barley":        "bu/ac",
    "Fall Rye":      "bu/ac",
    "Canary Seed":   "lbs/ac",
    "Spring Rye":    "bu/ac",
    "Tame Hay":      "tons/ac",
    "Flax":          "bu/ac",
    "Chickpeas":     "lbs/ac",
}

def crop_unit(crop):
    return CROP_UNITS.get(crop, "bu/ac")

# Provincial averages
@st.cache_data
def get_prov_avg():
    return df.groupby(["Year", "Crop"])["Yield"].mean().reset_index().rename(columns={"Yield": "Prov_Avg"})

prov_avg = get_prov_avg()

# ── RM name lookup (source: Wikipedia / Government of Saskatchewan) ────────────
RM_NAMES = {
    # Source: Government of Saskatchewan Municipal Affairs map, January 2010
    1: "Argyle", 2: "Mount Pleasant", 3: "Enniskillen", 4: "Coalfields", 5: "Estevan",
    6: "Cambria", 7: "Souris Valley", 8: "Lake Alma", 9: "Surprise Valley", 10: "Happy Valley",
    11: "Hart Butte", 12: "Poplar Valley", 17: "Val Marie", 18: "Lone Tree", 19: "Frontier",
    31: "Storthoaks", 32: "Reciprocity", 33: "Moose Creek", 34: "Browning", 35: "Benson",
    36: "Cymri", 37: "Lomond", 38: "Laurier", 39: "The Gap", 40: "Bengough",
    42: "Willow Bunch", 43: "Old Post", 44: "Waverley", 45: "Mankota", 46: "Glen McPherson",
    49: "White Valley", 51: "Reno", 61: "Antler", 63: "Moose Mountain", 64: "Brock",
    65: "Tecumseh", 66: "Griffin", 67: "Weyburn", 68: "Brokenshell", 69: "Norton",
    70: "Key West", 71: "Excel", 72: "Lake of the Rivers", 73: "Stonehenge", 74: "Wood River",
    75: "Pinto Creek", 76: "Auvergne", 77: "Wise Creek", 78: "Grassy Creek", 79: "Arlington",
    91: "Maryfield", 92: "Walpole", 93: "Wawken", 94: "Hazelwood", 95: "Golden West",
    96: "Fillmore", 97: "Wellington", 98: "Scott", 99: "Caledonia", 100: "Elmsthorpe",
    101: "Terrell", 102: "Lake Johnston", 103: "Sutton", 104: "Gravelbourg", 105: "Glen Bain",
    106: "Whiska Creek", 107: "Lac Pelletier", 108: "Bone Creek", 109: "Carmichael",
    110: "Piapot", 111: "Maple Creek", 121: "Moosomin", 122: "Martin", 123: "Silverwood",
    124: "Kingsley", 125: "Chester", 126: "Montmartre", 127: "Francis", 128: "Lajord",
    129: "Bratt's Lake", 130: "Redburn", 131: "Baildon", 132: "Hillsborough", 133: "Rodgers",
    134: "Shamrock", 135: "Lawtonia", 136: "Coulee", 137: "Swift Current", 138: "Webb",
    139: "Gull Lake", 141: "Big Stick", 142: "Enterprise", 151: "Rocanville", 152: "Spy Hill",
    153: "Willowdale", 154: "Elcapo", 155: "Wolseley", 156: "Indian Head",
    157: "South Qu'Appelle", 158: "Edenwold", 159: "Sherwood", 160: "Pense",
    161: "Moose Jaw", 162: "Caron", 163: "Wheatlands", 164: "Chaplin", 165: "Morse",
    166: "Excelsior", 167: "Saskatchewan Landing", 168: "Riverside", 169: "Pittville",
    171: "Fox Valley", 181: "Langenburg", 183: "Fertile Belt", 184: "Grayson",
    185: "McLeod", 186: "Abernethy", 187: "North Qu'Appelle", 189: "Lumsden",
    190: "Dufferin", 191: "Marquis", 193: "Eyebrow", 194: "Enfield", 211: "Churchbridge",
    213: "Saltcoats", 214: "Cana", 215: "Stanley", 216: "Tullymet", 217: "Lipton",
    218: "Cupar", 219: "Longlaketon", 220: "McKillop", 221: "Sarnia", 222: "Craik",
    223: "Huron", 224: "Maple Bush", 225: "Canaan", 226: "Victory", 228: "Lacadena",
    229: "Miry Creek", 230: "Clinworth", 231: "Happyland", 232: "Deer Forks",
    241: "Calder", 243: "Wallace", 244: "Orkney", 245: "Garry", 246: "Ituna Bon Accord",
    247: "Kellross", 248: "Touchwood", 250: "Last Mountain Valley", 251: "Big Arm",
    252: "Arm River", 253: "Willner", 254: "Loreburn", 255: "Coteau", 256: "King George",
    257: "Monet", 259: "Snipe Lake", 260: "Newcombe", 261: "Chesterfield", 271: "Cote",
    273: "Sliding Hills", 274: "Good Lake", 275: "Insinger", 276: "Foam Lake",
    277: "Emerald", 279: "Mount Hope", 280: "Wreford", 281: "Wood Creek", 282: "McCraney",
    283: "Rosedale", 284: "Rudy", 285: "Fertile Valley", 286: "Milden",
    287: "St. Andrews", 288: "Pleasant Valley", 290: "Kindersley", 292: "Milton",
    301: "St. Philips", 303: "Keys", 304: "Buchanan", 305: "Invermay", 307: "Elfros",
    308: "Big Quill", 309: "Prairie Rose", 310: "Usborne", 312: "Morris", 313: "Lost River",
    314: "Dundurn", 315: "Montrose", 316: "Harris", 317: "Marriott", 318: "Mountain View",
    319: "Winslow", 320: "Oakdale", 321: "Prairiedale", 322: "Antelope Park",
    331: "Livingston", 333: "Clayton", 334: "Preeceville", 335: "Hazel Dell",
    336: "Sasman", 337: "Lakeview", 338: "Lakeside", 339: "Leroy", 340: "Wolverine",
    341: "Viscount", 342: "Colonsay", 343: "Blucher", 344: "Corman Park", 345: "Vanscoy",
    346: "Perdue", 347: "Biggar", 349: "Grandview", 350: "Mariposa", 351: "Progress",
    352: "Heart's Hill", 366: "Kelvington", 367: "Ponass Lake", 368: "Spalding",
    369: "St. Peter", 370: "Humboldt", 371: "Bayne", 372: "Grant", 373: "Aberdeen",
    376: "Eagle Creek", 377: "Glenside", 378: "Rosemount", 379: "Reford",
    380: "Tramping Lake", 381: "Grass Lake", 382: "Eye Hill", 394: "Hudson Bay",
    395: "Porcupine", 397: "Barrier Valley", 398: "Pleasantdale", 399: "Lake Lenore",
    400: "Three Lakes", 401: "Hoodoo", 402: "Fish Creek", 403: "Rosthern", 404: "Laird",
    405: "Great Bend", 406: "Mayfield", 409: "Buffalo", 410: "Round Valley", 411: "Senlac",
    426: "Bjorkdale", 427: "Tisdale", 428: "Star City", 429: "Flett's Springs",
    430: "Invergordon", 431: "St. Louis", 434: "Blaine Lake", 435: "Redberry",
    436: "Douglas", 437: "North Battleford", 438: "Battle River", 439: "Cut Knife",
    440: "Hillsdale", 442: "Manitou Lake", 456: "Arborfield", 457: "Connaught",
    458: "Willow Creek", 459: "Kinistino", 460: "Birch Hills", 461: "Prince Albert",
    463: "Duck Lake", 464: "Leask", 466: "Meeting Lake", 467: "Round Hill", 468: "Meota",
    469: "Turtle River", 470: "Paynton", 471: "Eldon", 472: "Wilton", 486: "Moose Range",
    487: "Nipawin", 488: "Torch River", 490: "Garden River", 491: "Buckland",
    493: "Shellbrook", 494: "Canwood", 496: "Spiritwood", 497: "Medstead",
    498: "Parkdale", 499: "Mervin", 501: "Frenchman Butte", 502: "Britannia",
    520: "Paddockwood", 521: "Lakeland", 555: "Big River", 561: "Loon Lake",
    588: "Meadow Lake", 622: "Beaver River",
}
def rm_label(rm_num):
    """Return 'RM 96 — Fillmore' style label."""
    name = RM_NAMES.get(rm_num, "")
    if name:
        return f"RM {rm_num} — {name}"
    return f"RM {rm_num}"

def rm_name(rm_num):
    return RM_NAMES.get(rm_num, f"RM {rm_num}")

# Build labeled RM list sorted by number
rm_labels  = [rm_label(r) for r in all_rms]
rm_label_to_num = {rm_label(r): r for r in all_rms}

# ── JGL logo embedded as base64 (no external URL dependency) ─────────────────
import base64 as _b64, pathlib as _pl
_logo_path = _pl.Path(__file__).parent / "JGL_Logo.png"
if _logo_path.exists():
    _logo_b64 = _b64.b64encode(_logo_path.read_bytes()).decode()
    LOGO_SRC = f"data:image/png;base64,{_logo_b64}"
else:
    LOGO_SRC = ""

# ── Sidebar controls ──────────────────────────────────────────────────────────
_logo_tag = f'<img src="{LOGO_SRC}" style="width:90px; margin-bottom:6px; display:block;">' if LOGO_SRC else ""
st.sidebar.markdown(f"""
<div style="padding: 1rem 0 1.5rem 0; border-bottom: 1px solid #333; margin-bottom: 1.5rem;">
  {_logo_tag}
  <div style="font-size:1.3rem; font-weight:700; color:{GOLD}; letter-spacing:-0.02em;">JGL Capital</div>
  <div style="font-size:0.75rem; color:#888; margin-top:0.2rem;">RM Yield Analytics</div>
</div>
""", unsafe_allow_html=True)

# ── RM selector ───────────────────────────────────────────────────────────────
selected_rm_label = st.sidebar.selectbox(
    "Select Rural Municipality (RM)",
    rm_labels,
    index=0,
)
selected_rm = rm_label_to_num[selected_rm_label]

# ── Crop selector ─────────────────────────────────────────────────────────────
selected_crop = st.sidebar.selectbox(
    "Select Crop",
    ordered_crops,
    index=0,
)

# Year range filter
min_year = int(df["Year"].min())
max_year = int(df["Year"].max())
year_range = st.sidebar.slider("Year Range", min_year, max_year, (1990, max_year))

# Rolling average toggle
show_rolling = st.sidebar.checkbox("Show 5-Year Rolling Average", value=True)

# Multi-RM comparison
st.sidebar.markdown(f'<div style="margin-top:1.5rem; border-top:1px solid #333; padding-top:1rem; font-size:0.72rem; color:{GOLD_LT}; text-transform:uppercase; letter-spacing:0.07em; font-weight:600;">Compare Additional RMs</div>', unsafe_allow_html=True)
compare_rm_labels = st.sidebar.multiselect(
    "Add RMs to Compare (max 3)",
    [rm_label(r) for r in all_rms if r != selected_rm],
    max_selections=3,
    help="Overlay up to 3 other RMs on the time series chart"
)
compare_rms = [rm_label_to_num[lbl] for lbl in compare_rm_labels]

# ── Sidebar footer — logo, author, address ────────────────────────────────────
_footer_logo = f'<img src="{LOGO_SRC}" style="width:80px; margin-bottom:10px; display:block;">' if LOGO_SRC else '<div style="font-size:1rem;font-weight:700;color:{GOLD};margin-bottom:8px;">JGL Capital</div>'
st.sidebar.markdown(f"""
<div style="margin-top:2rem; padding-top:1rem; border-top:1px solid #333;">
  {_footer_logo}
  <div style="font-size:0.72rem; color:#666; line-height:1.8;">
    <div style="color:{GOLD_LT}; font-weight:600; margin-bottom:2px;">Quintin Stamler</div>
    <div style="color:#888;">Futures &amp; Options Broker</div>
    <div style="margin-top:8px; color:#666;">
      RR 280 Hwy #1 West, Box 40<br>
      Moose Jaw, SK &nbsp;S6H 4N7<br>
      <a href="tel:18779071517" style="color:#888; text-decoration:none;">(877) 907-1517</a><br>
      <a href="mailto:quintinstamler@jglcapital.ca" style="color:#888; text-decoration:none; font-size:0.68rem;">quintinstamler@jglcapital.ca</a>
    </div>
    <div style="margin-top:10px; color:#444; font-size:0.65rem; line-height:1.5;">
      Data: Saskatchewan Crop Insurance<br>
      {min_year}–{max_year} &nbsp;|&nbsp; {len(all_rms)} RMs
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# Friendly display name for selected RM
selected_rm_name = rm_name(selected_rm)
selected_rm_display = f"RM {selected_rm} — {selected_rm_name}" if selected_rm_name != f"RM {selected_rm}" else f"RM {selected_rm}"

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="header-bar">
  <h1>🌾 Your Local Yield vs. Saskatchewan Average</h1>
  <p>{selected_rm_display} · {selected_crop} · {year_range[0]}–{year_range[1]}</p>
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
        <div class="kpi-label">{selected_rm_display} Yield ({last_yr})</div>
        <div class="kpi-value">{rm_yield:.1f}</div>
        <div class="kpi-sub">{crop_unit(selected_crop)} · {selected_crop}</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">SK Provincial Average</div>
        <div class="kpi-value">{prov_yield:.1f}</div>
        <div class="kpi-sub">{crop_unit(selected_crop)} · {last_yr}</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">vs. Provincial Average</div>
        <div class="kpi-value {diff_class}">{diff_arrow} {abs(diff_abs):.1f} {crop_unit(selected_crop)}</div>
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
        hovertemplate=f"<b>SK Avg</b><br>Year: %{{x}}<br>Yield: %{{y:.1f}} {crop_unit(selected_crop)}<extra></extra>"
    ))

    # Compare RMs
    COMP_COLORS = ["#6c9ecf", "#9b7ec8", "#5dba82"]
    for i, crm in enumerate(compare_rms):
        crm_data = get_rm_data(crm, selected_crop, year_range)
        crm_display = rm_label(crm)
        if len(crm_data) > 0:
            fig_ts.add_trace(go.Scatter(
                x=crm_data["Year"], y=crm_data["Yield"].round(1),
                mode="lines+markers",
                name=crm_display,
                line=dict(color=COMP_COLORS[i % len(COMP_COLORS)], width=1.5),
                marker=dict(size=4),
                hovertemplate=f"<b>{crm_display}</b><br>Year: %{{x}}<br>Yield: %{{y:.1f}} {crop_unit(selected_crop)}<extra></extra>"
            ))

    # Rolling average for primary RM
    if show_rolling and len(merged) >= 3:
        fig_ts.add_trace(go.Scatter(
            x=merged["Year"], y=merged["Roll5_RM"].round(1),
            mode="lines",
            name=f"{selected_rm_display} – 5yr Avg",
            line=dict(color=GOLD, width=2, dash="longdash"),
            opacity=0.7,
            hovertemplate=f"<b>{selected_rm_display} 5yr Avg</b><br>Year: %{{x}}<br>Yield: %{{y:.1f}} {crop_unit(selected_crop)}<extra></extra>"
        ))

    # Primary RM line (on top)
    fig_ts.add_trace(go.Scatter(
        x=merged["Year"], y=merged["Yield"].round(1),
        mode="lines+markers",
        name=selected_rm_display,
        line=dict(color=GOLD, width=3),
        marker=dict(size=5, color=GOLD, line=dict(color=BLACK, width=1)),
        hovertemplate=f"<b>{selected_rm_display}</b><br>Year: %{{x}}<br>Yield: %{{y:.1f}} {crop_unit(selected_crop)}<extra></extra>"
    ))

    fig_ts.update_layout(
        title=dict(text=f"{selected_rm_display} vs. Saskatchewan Average — {selected_crop}", font=dict(size=14, color=SLATE), x=0),
        xaxis=dict(title="Year", gridcolor="#eeece6", tickfont=dict(size=11)),
        yaxis=dict(title=f"Yield ({crop_unit(selected_crop)})", gridcolor="#eeece6", tickfont=dict(size=11), zeroline=False),
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
    <tr><td style="padding:3px 0; color:{MUTED};">Yield volatility (σ)</td><td style="text-align:right;">{merged['Yield'].std():.1f} {crop_unit(selected_crop)}</td></tr>
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
                annotation_text=f"{selected_rm_display}: {rm_val:.1f} {crop_unit(selected_crop)}",
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
                annotation_text=f"SK Avg: {float(prov_val_latest.values[0]):.1f} {crop_unit(selected_crop)}",
                annotation_position="top left",
                annotation_font=dict(color=MUTED, size=10, family="Sora"),
            )

        fig_dist.update_layout(
            title=dict(text=f"Distribution of {selected_crop} Yields Across All SK RMs — {latest_year}", font=dict(size=13, color=SLATE), x=0),
            xaxis=dict(title=f"Yield ({crop_unit(selected_crop)})", gridcolor="#eeece6"),
            yaxis=dict(title="Number of RMs", gridcolor="#eeece6"),
            plot_bgcolor=WHITE,
            paper_bgcolor=WHITE,
            height=300,
            margin=dict(t=50, b=40, l=60, r=20),
            showlegend=False,
            font=dict(family="Sora, sans-serif")
        )
        st.plotly_chart(fig_dist, use_container_width=True)


# ── All-crops summary table for selected RM ───────────────────────────────────
st.markdown(f'''<div class="section-label">{selected_rm_display} — All Crops Summary</div>''', unsafe_allow_html=True)

import numpy as _np

def _olympic_avg(values):
    """7-year olympic average: drop highest and lowest, average remaining 5."""
    vals = [v for v in values if v is not None and not _np.isnan(v)]
    if len(vals) < 5:
        return None
    s = sorted(vals)
    return _np.mean(s[1:-1])

# Build summary for all crops for the selected RM
_summary_rows = []
_all_crops_ordered = ["Canola", "Spring Wheat", "Winter Wheat", "Durum", "Barley",
                      "Oats", "Peas", "Lentils", "Flax", "Mustard", "Canary Seed",
                      "Fall Rye", "Spring Rye", "Tame Hay", "Sunflowers", "Chickpeas"]

for _crop in _all_crops_ordered:
    _crop_df = df[(df["RM"] == selected_rm) & (df["Crop"] == _crop)].sort_values("Year")
    if len(_crop_df) == 0:
        continue

    # 2025 yield
    _y2025 = _crop_df[_crop_df["Year"] == 2025]["Yield"].values
    _yield_2025 = round(float(_y2025[0]), 1) if len(_y2025) > 0 else None

    # 7-year window: 2019-2025
    _window = _crop_df[_crop_df["Year"].between(2019, 2025)]["Yield"].values
    _oly = _olympic_avg(_window)
    _oly = round(float(_oly), 1) if _oly is not None else None

    # SK provincial average 2025 for this crop
    _prov_2025 = df[(df["Crop"] == _crop) & (df["Year"] == 2025)]["Yield"].mean()
    _prov_2025 = round(float(_prov_2025), 1) if not _np.isnan(_prov_2025) else None

    # % vs prov avg (2025)
    if _yield_2025 is not None and _prov_2025 is not None and _prov_2025 > 0:
        _vs_prov = round((_yield_2025 - _prov_2025) / _prov_2025 * 100, 1)
    else:
        _vs_prov = None

    _unit = crop_unit(_crop)
    _summary_rows.append({
        "Crop": _crop,
        f"2025 Yield": f"{_yield_2025:.1f} {_unit}" if _yield_2025 is not None else "—",
        f"SK Avg 2025": f"{_prov_2025:.1f} {_unit}" if _prov_2025 is not None else "—",
        "vs SK Avg": f"{_vs_prov:+.1f}%" if _vs_prov is not None else "—",
        "7-yr Olympic Avg": f"{_oly:.1f} {_unit}" if _oly is not None else "—",
        "_vs_prov_raw": _vs_prov,
        "_yield_raw": _yield_2025,
    })

if _summary_rows:
    # Build styled HTML table
    _header_cols = ["Crop", "2025 Yield", "SK Avg 2025", "vs SK Avg", "7-yr Olympic Avg"]
    _th = "".join(
        f'<th style="padding:8px 14px;text-align:{"left" if c=="Crop" else "right"};border-bottom:2px solid {GOLD};font-size:0.72rem;text-transform:uppercase;letter-spacing:0.07em;color:{MUTED};font-weight:600;">{c}</th>'
        for c in _header_cols
    )
    _rows_html = ""
    for i, r in enumerate(_summary_rows):
        _bg = WHITE if i % 2 == 0 else "#f5f3ee"
        _vs = r["_vs_prov_raw"]
        _vs_color = GREEN if (_vs is not None and _vs > 0) else (RED if (_vs is not None and _vs < 0) else SLATE)
        _bold = "font-weight:700;" if r["Crop"] == selected_crop else ""
        _border = f"border-left:3px solid {GOLD};" if r["Crop"] == selected_crop else ""
        _row_cells = ""
        for col in _header_cols:
            _align = "left" if col == "Crop" else "right"
            _color = f"color:{_vs_color};font-weight:600;" if col == "vs SK Avg" else f"color:{SLATE};"
            _val = r[col]
            _row_cells += f'<td style="padding:7px 14px;text-align:{_align};{_color}{_bold}font-size:0.83rem;">{_val}</td>'
        _rows_html += f'<tr style="background:{_bg};{_border}">{_row_cells}</tr>'

    _table_html = f"""
<div style="background:{WHITE};border:1px solid #e8e4d8;border-radius:6px;overflow:hidden;margin-bottom:1rem;box-shadow:0 1px 4px rgba(0,0,0,0.06);">
  <table style="width:100%;border-collapse:collapse;font-family:'DM Mono',monospace;">
    <thead><tr style="background:{OFFWHITE};">{_th}</tr></thead>
    <tbody>{_rows_html}</tbody>
  </table>
  <div style="padding:6px 14px 8px;font-size:0.68rem;color:{MUTED};">
    7-yr Olympic Average uses 2019–2025 data: drops the single highest and lowest year, averages the remaining 5.
    Highlighted row = currently selected crop.
  </div>
</div>
"""
    st.markdown(_table_html, unsafe_allow_html=True)
else:
    st.markdown(f'<div style="color:{MUTED};font-size:0.85rem;padding:0.5rem 0;">No crop data available for {selected_rm_display}.</div>', unsafe_allow_html=True)


# ── Data table (expandable) ───────────────────────────────────────────────────
with st.expander("📋 View Raw Data Table"):
    display_df = merged[["Year","Yield","Prov_Avg","Diff_abs","Diff_pct"]].copy()
    display_df.columns = ["Year", f"{selected_rm_display} Yield ({crop_unit(selected_crop)})", f"SK Avg ({crop_unit(selected_crop)})", f"Difference ({crop_unit(selected_crop)})", "% Difference"]
    display_df = display_df.sort_values("Year", ascending=False)
    display_df["Year"] = display_df["Year"].astype(int)
    for col in display_df.columns[1:4]:
        display_df[col] = display_df[col].round(1)
    display_df["% Difference"] = display_df["% Difference"].round(1)

    def color_diff(val):
        color = GREEN if val > 0 else (RED if val < 0 else MUTED)
        return f"color: {color}; font-weight: 600"

    styled = display_df.style.applymap(color_diff, subset=["% Difference", f"Difference ({crop_unit(selected_crop)})"])
    st.dataframe(styled, use_container_width=True, hide_index=True)

    # CSV download
    csv = display_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇ Download Table as CSV",
        data=csv,
        file_name=f"RM{selected_rm}_{selected_rm_name.replace(' ','_')}_{selected_crop.replace(' ','_')}_yields.csv",
        mime="text/csv"
    )

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="margin-top:2rem; padding-top:1rem; border-top:1px solid #e0ddd5; display:flex; justify-content:space-between; align-items:center;">
  <div style="font-size:0.75rem; color:{MUTED};">
    Data source: Saskatchewan Crop Insurance Corporation &nbsp;|&nbsp; JGL Capital Advisory
  </div>
  <div style="font-size:0.75rem; color:{MUTED};">
    Yields in {crop_unit(selected_crop)}
  </div>
</div>
""", unsafe_allow_html=True)
