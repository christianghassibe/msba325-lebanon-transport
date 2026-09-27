"""
MSBA 325 - Interactive Visualizations with Streamlit
Public Transport and Road Infrastructure in Lebanon (2023)

Dataset: Public Transportation - Lebanon 2023 (Impact Open Data)
Source:  AUB PKGCubes Explorer, Social Data domain

Author: Christian Ghassibe
"""

import pandas as pd
import plotly.express as px
import streamlit as st

CSV_PATH = "Public_Transportation_Lebanon_2023.csv"

BUS_STOPS = "Existence of dedicated bus stops - exists"
INITIATIVES = (
    "Existence of initiatives and projects  in the past five years "
    "to improve infrastructure - exists"
)
ROAD_GOOD = "State of the main roads - good"
ROAD_OK = "State of the main roads - acceptable"
ROAD_BAD = "State of the main roads - bad"

TRANSPORT_COLS = {
    "Taxis": "The main means of public transport - taxis",
    "Vans": "The main means of public transport - vans",
    "Buses": "The main means of public transport - buses",
}

# Districts rolled up to their governorate, so the two levels can be linked.
AREA_PREFIX_TO_GOVERNORATE = {
    "Akkar": "Akkar",
    "Baalbek-Hermel": "Baalbek-Hermel",
    "Hermel District": "Baalbek-Hermel",
    "Beqaa": "Beqaa",
    "Zahlé": "Beqaa",
    "Western Beqaa": "Beqaa",
    "Mount Lebanon": "Mount Lebanon",
    "Matn District": "Mount Lebanon",
    "Byblos District": "Mount Lebanon",
    "Aley District": "Mount Lebanon",
    "Keserwan District": "Mount Lebanon",
    "Baabda District": "Mount Lebanon",
    "North": "North",
    "Miniyeh": "North",
    "Zgharta District": "North",
    "Batroun District": "North",
    "Bsharri District": "North",
    "Tripoli District": "North",
    "Nabatieh": "Nabatieh",
    "Bint Jbeil District": "Nabatieh",
    "Marjeyoun District": "Nabatieh",
    "Hasbaya District": "Nabatieh",
    "South": "South",
    "Sidon District": "South",
    "Tyre District": "South",
}

st.set_page_config(
    page_title="Lebanon Public Transport & Roads (2023)",
    page_icon="🚌",
    layout="wide",
)


# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------

def repair_text(value):
    """Fix names stored as UTF-8 bytes read as Latin-1 (Zahlé, Miniyeh-Danniyeh)."""
    try:
        return value.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return value


def to_governorate(area):
    for prefix, governorate in AREA_PREFIX_TO_GOVERNORATE.items():
        if area.startswith(prefix):
            return governorate
    return None


@st.cache_data
def load_data(path=CSV_PATH):
    df = pd.read_csv(path)

    area = (
        df["refArea"]
        .str.rsplit("/", n=1)
        .str[-1]
        .apply(repair_text)
        .str.replace("_Governorate", "", regex=False)
        .str.replace("_", " ", regex=False)
        .str.replace(", Lebanon", "", regex=False)
    )
    df["Area"] = area
    df["Governorate"] = area.map(to_governorate)
    df = df.dropna(subset=["Governorate"])

    # Rows whose refArea is already a governorate have no district of their own.
    df["District"] = df.apply(
        lambda row: row["Area"]
        if row["Area"] != row["Governorate"]
        else f"{row['Governorate']} (district not specified)",
        axis=1,
    )
    return df


df = load_data()

# ---------------------------------------------------------------------------
# Header and context
# ---------------------------------------------------------------------------

st.title("Public Transport and Road Infrastructure in Lebanon")
st.caption(
    "Town-level survey data, 2023. Source: Impact Open Data, "
    "published through the AUB PKGCubes Explorer."
)

st.markdown(
    """
Every row in this dataset is one Lebanese town. For each town the survey records
whether it has dedicated bus stops, what the main means of public transport is,
and the reported condition of its roads. Towns are grouped here into their
district and governorate, which lets you move from a national picture down to a
single district.
"""
)

# ---------------------------------------------------------------------------
# Two linked interaction features
# ---------------------------------------------------------------------------

st.sidebar.header("Explore the data")

ALL = "All Lebanon"
governorates = sorted(df["Governorate"].unique())

# Feature 1: the governorate drives everything below it.
governorate = st.sidebar.selectbox(
    "1. Governorate",
    [ALL] + governorates,
    help="Pick a governorate to narrow the district list underneath.",
)

# Feature 2: its options are rebuilt from the choice made in feature 1.
if governorate == ALL:
    district_pool = sorted(df["District"].unique())
else:
    district_pool = sorted(
        df.loc[df["Governorate"] == governorate, "District"].unique()
    )

districts = st.sidebar.multiselect(
    "2. Districts",
    district_pool,
    default=district_pool,
    help="Only the districts inside the governorate chosen above are listed.",
)

if not districts:
    st.warning("Select at least one district in the sidebar to see the charts.")
    st.stop()

selection = df[df["District"].isin(districts)]

# Charts break the areas down one level below whatever was selected.
group_col = "Governorate" if governorate == ALL else "District"

# ---------------------------------------------------------------------------
# Headline numbers
# ---------------------------------------------------------------------------

scope = "Lebanon" if governorate == ALL else governorate
st.subheader(f"{scope}: {len(selection)} towns in the current selection")

col1, col2, col3 = st.columns(3)
col1.metric(
    "Towns with dedicated bus stops",
    f"{selection[BUS_STOPS].mean() * 100:.1f}%",
)
col2.metric(
    "Main roads in good condition",
    f"{selection[ROAD_GOOD].mean() * 100:.1f}%",
)
col3.metric(
    "Infrastructure initiatives in the past 5 years",
    f"{selection[INITIATIVES].mean() * 100:.1f}%",
)

# ---------------------------------------------------------------------------
# Chart 1 - bus stop coverage
# ---------------------------------------------------------------------------

st.markdown("### Where do towns have dedicated bus stops?")

coverage = (
    selection.groupby(group_col)[BUS_STOPS].mean().mul(100).round(1).sort_values()
)
coverage_frame = coverage.reset_index()
coverage_frame.columns = [group_col, "Coverage"]

fig_coverage = px.bar(
    coverage_frame,
    x="Coverage",
    y=group_col,
    orientation="h",
    text="Coverage",
    color="Coverage",
    color_continuous_scale="Blues",
    labels={"Coverage": "% of towns with dedicated bus stops"},
)
fig_coverage.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
fig_coverage.update_layout(
    coloraxis_showscale=False,
    xaxis_title="% of towns with dedicated bus stops",
    yaxis_title="",
    template="plotly_white",
    height=420,
    margin=dict(l=10, r=40, t=30, b=40),
)
st.plotly_chart(fig_coverage, width="stretch")

# ---------------------------------------------------------------------------
# Chart 2 - road condition
# ---------------------------------------------------------------------------

st.markdown("### What condition are the main roads in?")

roads = (
    selection.groupby(group_col)[[ROAD_GOOD, ROAD_OK, ROAD_BAD]].mean().mul(100).round(1)
)
roads.columns = ["Good", "Acceptable", "Bad"]
roads = roads.sort_values("Good", ascending=False).reset_index()

roads_long = roads.melt(
    id_vars=group_col, var_name="Condition", value_name="Share"
)

fig_roads = px.bar(
    roads_long,
    x=group_col,
    y="Share",
    color="Condition",
    text="Share",
    category_orders={"Condition": ["Good", "Acceptable", "Bad"]},
    color_discrete_map={
        "Good": "#2E7D32",
        "Acceptable": "#F9A825",
        "Bad": "#C62828",
    },
)
fig_roads.update_traces(texttemplate="%{text:.0f}%", textposition="inside")
fig_roads.update_layout(
    barmode="stack",
    xaxis_title="",
    yaxis_title="% of towns",
    legend_title="Condition of main roads",
    template="plotly_white",
    height=440,
    margin=dict(l=10, r=40, t=30, b=40),
)
st.plotly_chart(fig_roads, width="stretch")

# ---------------------------------------------------------------------------
# Insights
# ---------------------------------------------------------------------------

st.markdown("### Two things the data shows")

top_area = coverage.idxmax()
bottom_area = coverage.idxmin()
mode_shares = {
    label: selection[col].sum() for label, col in TRANSPORT_COLS.items()
}
total_modes = sum(mode_shares.values())
taxi_share = mode_shares["Taxis"] / total_modes * 100 if total_modes else 0

st.markdown(
    f"""
**1. Bus stops are rare almost everywhere, and unevenly spread.**
In the current selection, {top_area} has the widest coverage at
{coverage.max():.1f}% of towns, while {bottom_area} sits at {coverage.min():.1f}%.
Even the best performing area leaves the large majority of its towns without a
dedicated stop, so the gap between areas is a gap between low and lower.

**2. The network runs on taxis and vans, not buses.**
Across the selected towns, taxis account for {taxi_share:.1f}% of all reported
main means of transport. Formal buses are the least reported mode. Public
transport in Lebanon is mostly an informal, road-based system, which also
explains why road condition matters more than bus infrastructure for how people
actually move.
"""
)

# ---------------------------------------------------------------------------
# Design justifications
# ---------------------------------------------------------------------------

st.markdown("### Design justifications")

with st.expander("Feature 1: the governorate dropdown"):
    st.markdown(
        """
**Which user question it answers.** "How does my region compare, and what does
the picture look like once I stop looking at all 1,137 towns at once?" The
dropdown sets the frame of reference for everything below it.

**Why a dropdown rather than an alternative.** The options are seven mutually
exclusive areas, and only one can sensibly be the frame at a time. Checkboxes
would allow combinations that make the axis labels meaningless, and a slider
implies an order that governorates do not have. A dropdown states plainly that
this is a single choice from a short, fixed list, and it collapses to one line
instead of taking up seven.

**Course concept.** Reducing clutter. Showing every district at once produces a
25-category bar chart where nothing stands out. The dropdown removes categories
the reader did not ask for, so the chart carries one comparison instead of many.
"""
    )

with st.expander("Feature 2: the district multiselect"):
    st.markdown(
        """
**Which user question it answers.** "Inside this governorate, which districts
drive the average, and what happens to the picture if I set one of them aside?"
Governorate averages hide a lot: one district with many towns can carry the
whole figure.

**Why a multiselect rather than an alternative.** The reader needs to compare
several districts at once, so a second dropdown would not work. A multiselect
also starts with everything selected, which means the default view is the full
governorate and the reader removes rather than builds. That keeps the page
useful before anyone touches it.

**Link to the first feature.** The options are rebuilt from the governorate
chosen above, so the reader can only ever select districts that exist inside the
current frame. The two widgets form a drill-down, not two filters working
against each other.

**Course concept.** Providing context and focusing attention. The narrowing is
progressive: national picture first, then one governorate, then chosen districts,
with the charts and the headline numbers updating together so each step is read
against the one before it.
"""
    )

st.caption(
    "Built with Streamlit and Plotly for MSBA 325, American University of Beirut."
)
