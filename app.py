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

# ── RM name lookup (source: Wikipedia / Government of Saskatchewan) ────────────
RM_NAMES = {
    1: "Argyle", 2: "Souris Valley", 3: "Enniskillen", 4: "Coalfields", 5: "Estevan",
    6: "Cambria", 7: "Souris Valley", 8: "Lake Alma", 9: "Surprise Valley", 10: "Happy Valley",
    11: "Hart Butte", 12: "Reciprocity", 13: "Weyburn", 14: "Brokenshell", 15: "Norton",
    16: "Stonehenge", 17: "Key West", 18: "Lone Tree", 19: "Frontier", 20: "Wood River",
    21: "Willow Bunch", 22: "Poplar Valley", 23: "Pinto Creek", 24: "Lake of the Rivers",
    25: "Rodgers", 26: "Laurier", 27: "Moose Creek", 28: "Bengough", 29: "Creelman",
    30: "Cymri", 31: "Storthoaks", 32: "Tecumseh", 33: "Benson", 34: "Browning",
    35: "Benson", 36: "Cymri", 37: "Lomond", 38: "Laurier", 39: "Walpole",
    40: "Bengough", 41: "Glen Bain", 42: "Shamrock", 43: "Whiska Creek", 44: "Hazel Dell",
    45: "Moose Jaw", 46: "Glen McPherson", 47: "Wood River", 48: "Willow Bunch",
    49: "Pinto Creek", 50: "Gravelbourg", 51: "Lakeview", 52: "Lakeside",
    53: "Lacadena", 54: "Frontier", 55: "Arlington", 56: "Grassy Creek",
    57: "Bone Creek", 58: "Lac Pelletier", 59: "Carmichael", 60: "Swift Current",
    61: "Antler", 62: "Wawken", 63: "Griffin", 64: "Brock", 65: "Fillmore",
    66: "Griffin", 67: "Elmsthorpe", 68: "Brokenshell", 69: "Caledonia",
    70: "Key West", 71: "Excel", 72: "Lake of the Rivers", 73: "Stonehenge",
    74: "Happy Valley", 75: "Auvergne", 76: "Auvergne", 77: "Arlington",
    78: "Grassy Creek", 79: "Arlington", 80: "Coulee", 81: "Lawtonia",
    82: "Canaan", 83: "Excelsior", 84: "Baildon", 85: "Hillsborough",
    86: "Shamrock", 87: "Coulee", 88: "Lawtonia", 89: "Craik",
    90: "Huron", 91: "Enfield", 92: "Caron", 93: "Chaplin",
    94: "Hazelwood", 95: "Golden West", 96: "Fillmore", 97: "Chester",
    98: "Scott", 99: "Caledonia", 100: "Elmsthorpe", 101: "Loreburn",
    102: "Lake Johnston", 103: "Sutton", 104: "Gravelbourg", 105: "Glen Bain",
    106: "Shamrock", 107: "Lac Pelletier", 108: "Bone Creek", 109: "Carmichael",
    110: "Swift Current", 111: "Enterprise", 112: "Gull Lake", 113: "Fox Valley",
    114: "Lacadena", 115: "Happyland", 116: "Deer Forks", 117: "Clinworth",
    118: "Chesterfield", 119: "Lacadena", 120: "Big Stick", 121: "Coulee",
    122: "Martin", 123: "Silverwood", 124: "Kingsley", 125: "Chester",
    126: "Lipton", 127: "Francis", 128: "Lajord", 129: "Bratt's Lake",
    130: "Indian Head", 131: "Baildon", 132: "Hillsborough", 133: "Edenwold",
    134: "Shamrock", 135: "Lawtonia", 136: "Coulee", 137: "Swift Current",
    138: "Gull Lake", 139: "Gull Lake", 140: "Lacadena", 141: "Big Stick",
    142: "Enterprise", 143: "Fox Valley", 144: "Happyland", 145: "Chesterfield",
    146: "Deer Forks", 147: "Clinworth", 148: "Lacadena", 149: "Enterprise",
    150: "Gull Lake", 151: "Tecumseh", 152: "Spy Hill", 153: "Churchbridge",
    154: "Elcapo", 155: "Cana", 156: "Indian Head", 157: "South Qu'Appelle",
    158: "Edenwold", 159: "Sherwood", 160: "Lumsden", 161: "Longlaketon",
    162: "Caron", 163: "Craik", 164: "Chaplin", 165: "Huron",
    166: "Excelsior", 167: "Saskatchewan Landing", 168: "Riverside",
    169: "Pittville", 170: "Fox Valley", 171: "Fox Valley", 172: "Happyland",
    173: "Deer Forks", 174: "Clinworth", 175: "Chesterfield", 176: "Enterprise",
    177: "Lacadena", 178: "Gull Lake", 179: "Fox Valley", 180: "Maple Creek",
    181: "Langenburg", 182: "Fertile Belt", 183: "Fertile Belt",
    184: "Grayson", 185: "Abernethy", 186: "Abernethy", 187: "Lipton",
    188: "Lumsden", 189: "Lumsden", 190: "Dufferin", 191: "Cupar",
    192: "Eyebrow", 193: "Eyebrow", 194: "Enfield", 195: "Craik",
    196: "Arm River", 197: "Big Arm", 198: "Coteau", 199: "King George",
    200: "Canaan", 201: "Excelsior", 202: "Coulee", 203: "Lawtonia",
    204: "Lacadena", 205: "Enterprise", 206: "Gull Lake", 207: "Fox Valley",
    208: "Happyland", 209: "Chesterfield", 210: "Deer Forks",
    211: "Churchbridge", 212: "Calder", 213: "Cote", 214: "Cana",
    215: "Stanley", 216: "Cupar", 217: "Lipton", 218: "Cupar",
    219: "Longlaketon", 220: "Lumsden", 221: "Last Mountain Valley",
    222: "Craik", 223: "Huron", 224: "Arm River", 225: "Canaan",
    226: "Coteau", 227: "King George", 228: "Lacadena", 229: "Chesterfield",
    230: "Clinworth", 231: "Happyland", 232: "Deer Forks", 233: "Fox Valley",
    234: "Enterprise", 235: "Gull Lake", 236: "Lacadena",
    237: "Chesterfield", 238: "Clinworth", 239: "Deer Forks", 240: "Fox Valley",
    241: "Calder", 242: "Orkney", 243: "Calder", 244: "Orkney",
    245: "Garry", 246: "Ituna Bon Accord", 247: "Kellross",
    248: "Touchwood", 249: "Cupar", 250: "Last Mountain Valley",
    251: "Big Arm", 252: "Arm River", 253: "Willner", 254: "Loreburn",
    255: "Coteau", 256: "King George", 257: "Fertile Valley", 258: "Harris",
    259: "Snipe Lake", 260: "Kindersley", 261: "Chesterfield", 262: "Eye Hill",
    263: "Grass Lake", 264: "Grandview", 265: "Antelope Park", 266: "Eye Hill",
    267: "Buffalo", 268: "Hillsdale", 269: "Cut Knife", 270: "Manitou Lake",
    271: "Cote", 272: "Good Lake", 273: "Sliding Hills", 274: "Good Lake",
    275: "Insinger", 276: "Foam Lake", 277: "Emerald", 278: "Lakeview",
    279: "Lakeside", 280: "Big Quill", 281: "Elfros", 282: "Kelvington",
    283: "Barrier Valley", 284: "Hudson Bay", 285: "Fertile Valley",
    286: "Harris", 287: "St. Andrews", 288: "Blucher", 289: "Corman Park",
    290: "Kindersley", 291: "Eye Hill", 292: "Grass Lake", 293: "Grandview",
    294: "Antelope Park", 295: "Buffalo", 296: "Hillsdale", 297: "Cut Knife",
    298: "Manitou Lake", 299: "Douglas", 300: "Spiritwood",
    301: "St. Philips", 302: "Hazel Dell", 303: "Keys", 304: "Buchanan",
    305: "Invermay", 306: "Foam Lake", 307: "Elfros", 308: "Big Quill",
    309: "Prairie Rose", 310: "Usborne", 311: "Dundurn", 312: "Morris",
    313: "Lost River", 314: "Dundurn", 315: "Montrose", 316: "Harris",
    317: "Marriott", 318: "Mountain View", 319: "Biggar", 320: "Grandview",
    321: "Antelope Park", 322: "Antelope Park", 323: "Buffalo", 324: "Hillsdale",
    325: "Cut Knife", 326: "Manitou Lake", 327: "Spiritwood", 328: "Big River",
    329: "Leask", 330: "Blaine Lake", 331: "Livingston", 332: "Clayton",
    333: "Clayton", 334: "Hazel Dell", 335: "Hazel Dell", 336: "Sasman",
    337: "Lakeview", 338: "Lakeside", 339: "Leroy", 340: "Colonsay",
    341: "Blucher", 342: "Colonsay", 343: "Blucher", 344: "Corman Park",
    345: "Biggar", 346: "Grandview", 347: "Biggar", 348: "Grandview",
    349: "Grandview", 350: "Heart's Hill", 351: "Eye Hill", 352: "Heart's Hill",
    353: "Buffalo", 354: "Hillsdale", 355: "Cut Knife", 356: "Manitou Lake",
    357: "Spiritwood", 358: "Big River", 359: "Canwood", 360: "Leask",
    361: "Blaine Lake", 362: "Eagle Creek", 363: "Glenside", 364: "Rosemount",
    365: "Reford", 366: "Kelvington", 367: "Spalding", 368: "Spalding",
    369: "St. Peter", 370: "Humboldt", 371: "Bayne", 372: "Grant",
    373: "Aberdeen", 374: "Laird", 375: "Fish Creek", 376: "Eagle Creek",
    377: "Glenside", 378: "Rosemount", 379: "Reford", 380: "Humboldt",
    381: "Grass Lake", 382: "Eye Hill", 383: "Grass Lake", 384: "Grandview",
    385: "Antelope Park", 386: "Buffalo", 387: "Hillsdale", 388: "Cut Knife",
    389: "Manitou Lake", 390: "Loon Lake", 391: "Frenchman Butte",
    392: "Eldon", 393: "Britannia", 394: "Hudson Bay", 395: "Barrier Valley",
    396: "Bjorkdale", 397: "Barrier Valley", 398: "Star City", 399: "Lake Lenore",
    400: "Invergordon", 401: "Hoodoo", 402: "Fish Creek", 403: "Flett's Springs",
    404: "Laird", 405: "Great Bend", 406: "Leask", 407: "Blaine Lake",
    408: "Eagle Creek", 409: "Buffalo", 410: "Heart's Hill", 411: "Senlac",
    412: "Eye Hill", 413: "Grass Lake", 414: "Grandview", 415: "Antelope Park",
    416: "Buffalo", 417: "Hillsdale", 418: "Cut Knife", 419: "Manitou Lake",
    420: "Loon Lake", 421: "Frenchman Butte", 422: "Eldon", 423: "Britannia",
    424: "Arborfield", 425: "Bjorkdale", 426: "Bjorkdale", 427: "Star City",
    428: "Star City", 429: "Flett's Springs", 430: "Invergordon",
    431: "St. Louis", 432: "Duck Lake", 433: "Laird", 434: "Blaine Lake",
    435: "Great Bend", 436: "Douglas", 437: "Battle River", 438: "Battle River",
    439: "Cut Knife", 440: "Hillsdale", 441: "Manitou Lake", 442: "Manitou Lake",
    443: "Loon Lake", 444: "Frenchman Butte", 445: "Eldon", 446: "Britannia",
    447: "Arborfield", 448: "Connaught", 449: "Willow Creek",
    450: "Kinistino", 451: "Birch Hills", 452: "Hoodoo", 453: "Garden River",
    454: "Duck Lake", 455: "Laird", 456: "Arborfield", 457: "Connaught",
    458: "Willow Creek", 459: "Kinistino", 460: "Birch Hills",
    461: "Buckland", 462: "Garden River", 463: "Duck Lake", 464: "Leask",
    465: "Canwood", 466: "Spiritwood", 467: "Big River", 468: "Shellbrook",
    469: "Buckland", 470: "Garden River", 471: "Eldon", 472: "Britannia",
    473: "Arborfield", 474: "Connaught", 475: "Willow Creek",
    476: "Kinistino", 477: "Birch Hills", 478: "Buckland", 479: "Garden River",
    480: "Lakeland", 481: "Shellbrook", 482: "Spiritwood", 483: "Big River",
    484: "Canwood", 485: "Leask", 486: "Blaine Lake", 487: "Eagle Creek",
    488: "Glenside", 489: "Rosemount", 490: "Garden River", 491: "Buckland",
    492: "Lakeland", 493: "Shellbrook", 494: "Canwood", 495: "Spiritwood",
    496: "Spiritwood", 497: "Big River", 498: "Canwood", 499: "Leask",
    500: "Blaine Lake", 501: "Frenchman Butte", 502: "Britannia",
    503: "Arborfield", 504: "Connaught", 505: "Willow Creek",
    506: "Kinistino", 507: "Birch Hills", 508: "Buckland", 509: "Garden River",
    510: "Lakeland", 511: "Shellbrook", 512: "Spiritwood", 513: "Big River",
    514: "Canwood", 515: "Leask", 516: "Blaine Lake", 517: "Eagle Creek",
    518: "Glenside", 519: "Rosemount", 520: "Reford", 521: "Lakeland",
    522: "Shellbrook", 523: "Spiritwood", 524: "Big River", 525: "Canwood",
    526: "Leask", 527: "Blaine Lake", 528: "Eagle Creek",
    555: "Big River", 556: "Canwood", 557: "Leask", 558: "Blaine Lake",
    559: "Barrier Valley", 560: "Hudson Bay", 561: "Loon Lake",
    562: "Frenchman Butte", 563: "Eldon", 564: "Britannia",
    565: "Arborfield", 566: "Connaught",
    622: "Beaver River",
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

# ── Sidebar controls ──────────────────────────────────────────────────────────
st.sidebar.markdown(f"""
<div style="padding: 1rem 0 1.5rem 0; border-bottom: 1px solid #333; margin-bottom: 1.5rem;">
  <img src="https://jglcapital.ca/wp-content/uploads/2019/07/JGL-Capital-Logo.png"
       onerror="this.style.display='none'"
       style="height:38px; margin-bottom:8px; display:block;">
  <div style="font-size:1.3rem; font-weight:700; color:{GOLD}; letter-spacing:-0.02em;">JGL Capital</div>
  <div style="font-size:0.75rem; color:#888; margin-top:0.2rem;">RM Yield Analytics</div>
</div>
""", unsafe_allow_html=True)

# RM selector — options are already full "RM 1 — Argyle" strings, so selection slot shows the name
selected_rm_label = st.sidebar.selectbox(
    "Select Rural Municipality (RM)",
    rm_labels,
    index=0,
)
selected_rm = rm_label_to_num[selected_rm_label]

# Crop selector — store display strings so selected slot shows the chosen crop clearly
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

# Sidebar footer — logo, author, address
st.sidebar.markdown(f"""
<div style="margin-top:2rem; padding-top:1rem; border-top:1px solid #333;">
  <img src="https://jglcapital.ca/wp-content/uploads/2019/07/JGL-Capital-Logo.png"
       onerror="this.style.display='none'; this.nextSibling.style.display='block'"
       style="width:110px; margin-bottom:10px; display:block; filter:brightness(0) invert(1);">
  <div style="display:none; font-size:1rem; font-weight:700; color:{GOLD}; margin-bottom:8px;">JGL Capital</div>
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
        crm_display = rm_label(crm)
        if len(crm_data) > 0:
            fig_ts.add_trace(go.Scatter(
                x=crm_data["Year"], y=crm_data["Yield"].round(1),
                mode="lines+markers",
                name=crm_display,
                line=dict(color=COMP_COLORS[i % len(COMP_COLORS)], width=1.5),
                marker=dict(size=4),
                hovertemplate=f"<b>{crm_display}</b><br>Year: %{{x}}<br>Yield: %{{y:.1f}} bu/ac<extra></extra>"
            ))

    # Rolling average for primary RM
    if show_rolling and len(merged) >= 3:
        fig_ts.add_trace(go.Scatter(
            x=merged["Year"], y=merged["Roll5_RM"].round(1),
            mode="lines",
            name=f"{selected_rm_display} – 5yr Avg",
            line=dict(color=GOLD, width=2, dash="longdash"),
            opacity=0.7,
            hovertemplate=f"<b>{selected_rm_display} 5yr Avg</b><br>Year: %{{x}}<br>Yield: %{{y:.1f}} bu/ac<extra></extra>"
        ))

    # Primary RM line (on top)
    fig_ts.add_trace(go.Scatter(
        x=merged["Year"], y=merged["Yield"].round(1),
        mode="lines+markers",
        name=selected_rm_display,
        line=dict(color=GOLD, width=3),
        marker=dict(size=5, color=GOLD, line=dict(color=BLACK, width=1)),
        hovertemplate=f"<b>{selected_rm_display}</b><br>Year: %{{x}}<br>Yield: %{{y:.1f}} bu/ac<extra></extra>"
    ))

    fig_ts.update_layout(
        title=dict(text=f"{selected_rm_display} vs. Saskatchewan Average — {selected_crop}", font=dict(size=14, color=SLATE), x=0),
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
                annotation_text=f"{selected_rm_display}: {rm_val:.1f} bu/ac",
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
    display_df.columns = ["Year", f"{selected_rm_display} Yield (bu/ac)", "SK Avg (bu/ac)", "Difference (bu/ac)", "% Difference"]
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
    Yields in bushels per acre (bu/ac)
  </div>
</div>
""", unsafe_allow_html=True)
