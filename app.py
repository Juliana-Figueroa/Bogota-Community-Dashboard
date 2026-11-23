
import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ---------- page setup ----------
st.set_page_config(page_title="Bogotá Community Development Dashboard", layout="wide")

# ---------- load data ----------
HERE = Path(__file__).parent

@st.cache_data
def load_data():
    with open(HERE / "upz_dashboard.geojson", encoding="utf-8") as f:
        geo = json.load(f)
    upz = pd.read_csv(HERE / "upz_data.csv")
    res = pd.read_csv(HERE / "resources_dashboard.csv")
    return geo, upz, res

geo, upz, res = load_data()

# ---------- map layers the user can choose ----------
LAYERS = {
    "Priority score (your weights)":           ("custom_score",           "Reds",    "0 to 1. Higher = more need. Change the weights in the sidebar."),
    "Unemployment rate (%)":                   ("unemp_rate",             "Reds",    "Share of the labor force that is unemployed."),
    "Average commute to work (minutes)":       ("avg_commute_min",        "Oranges", "Average one-way commute of employed residents."),
    "Workers using TransMilenio (%)":          ("pct_transmilenio",       "Blues",   "Share of workers who use TransMilenio to get to work."),
    "Community services per 10,000 residents": ("services_per10k",        "Greens",  "All mapped services except bus stops, per 10,000 residents aged 15+."),
    "Health facilities per 10,000 residents":  ("health_per10k",          "Greens",  "Hospitals, clinics and doctors per 10,000 residents aged 15+."),
    "Transit stations per 10,000 residents":   ("transit_station_per10k", "Purples", "TransMilenio and TransMiCable stations per 10,000 residents aged 15+."),
}

# ---------- sidebar: map options ----------
st.sidebar.header("Map options")
layer = st.sidebar.selectbox("Map layer", list(LAYERS))
localidades = st.sidebar.multiselect("Filter by localidad (leave empty for all)",
                                     sorted(upz["localidad"].unique()))

# ---------- sidebar: resource points ----------
RES_STYLE = {
    "Health facilities":             ("health",              "black"),
    "Transit stations":              ("transit_station",     "gold"),
    "Employment services":           ("employment_services", "deeppink"),
    "Caja recreation centers":       ("caja_recreation",     "#00b8d4"),
    "Schools and libraries":         ("education",           "#1f4fe0"),
    "Places of worship":             ("worship",             "#9467bd"),
    "Community and social services": ("community",           "#2ca02c"),
    "Bus stops (SITP)":              ("bus_stop",            "gray"),
}
show_res = st.sidebar.multiselect("Show community resources on the map", list(RES_STYLE))

# ---------- sidebar: priority weights ----------
st.sidebar.header("Priority weights")
st.sidebar.caption("How much should each factor count in the priority score? "
                   "0 = ignore it, 5 = very important.")
NEEDS = {
    "Unemployment":            "need_unemployment",
    "Long commutes":           "need_commute",
    "Few community services":  "need_services",
    "Few health facilities":   "need_health",
    "Few transit stations":    "need_transit",
}
weights = {col: st.sidebar.slider(label, 0, 5, 1) for label, col in NEEDS.items()}

total = sum(weights.values())
if total == 0:
    st.sidebar.warning("All weights are 0, so equal weights are used instead.")
    weights = {col: 1 for col in weights}
    total = len(weights)

# ---------- calculate the custom priority score ----------
upz["custom_score"] = sum(upz[col] * w for col, w in weights.items()) / total
upz["custom_rank"] = upz["custom_score"].rank(ascending=False, method="min").astype(int)

view = upz[upz["localidad"].isin(localidades)] if localidades else upz

# ---------- title and guidance ----------
st.title("Community Development Priorities in Bogotá")
st.markdown(
    "Explore unemployment, access to community resources, and commute times across "
    "Bogotá's 95 UPZ (zonal planning units). **Choose a layer** in the sidebar, "
    "**hover** over a UPZ to see its details, and **zoom or drag** to move around the map. "
    "Use the **priority weights** to decide which factors matter most to you."
)

# ---------- map ----------
col, scale, description = LAYERS[layer]
st.caption(f"**{layer}:** {description}")

fig = px.choropleth_map(
    view,
    geojson=geo,
    locations="survey_code",
    featureidkey="properties.survey_code",
    color=col,
    color_continuous_scale=scale,
    range_color=(upz[col].min(), upz[col].quantile(0.95)),
    hover_name="short_name",
    hover_data={
        "survey_code": False,
        "localidad": True,
        "unemp_rate": ":.1f",
        "avg_commute_min": ":.0f",
        "services_per10k": ":.1f",
        "custom_rank": True,
    },
    labels={
        col: layer,
        "localidad": "Localidad",
        "unemp_rate": "Unemployment (%)",
        "avg_commute_min": "Avg. commute (min)",
        "services_per10k": "Services per 10k",
        "custom_rank": "Priority rank (of 95)",
    },
    center={"lat": 4.63, "lon": -74.11},
    zoom=10.4,
    opacity=0.75,
    map_style="carto-positron",
)
fig.update_layout(margin=dict(l=0, r=0, t=70, b=40), height=620)
fig.update_layout(map_center={"lat": 4.63, "lon": -74.11}, map_zoom=10.4)
fig.update_layout(coloraxis_colorbar=dict(
    orientation="h", x=0.5, xanchor="center", y=1.02, yanchor="bottom",
    len=0.9, thickness=12, title=dict(side="top"),
))
for label in show_res:
    cat, color = RES_STYLE[label]
    pts = res[res["category"] == cat]
    if localidades:
        pts = pts[pts["localidad"].isin(localidades)]
    fig.add_trace(go.Scattermap(
        lat=pts["lat"],
        lon=pts["lon"],
        mode="markers",
        marker=dict(size=7, color=color),
        name=f"{label} ({len(pts)})",
        text=pts["name"].fillna("(no name)") + "<br>" + pts["upz"],
        hovertemplate="<b>%{text}</b><extra>" + label + "</extra>",
    ))
fig.update_layout(legend=dict(x=0.01, y=0.01, xanchor="left", yanchor="bottom",
                              bgcolor="rgba(255,255,255,0.85)"))
st.plotly_chart(fig, use_container_width=True)
st.markdown("<br><br>", unsafe_allow_html=True)

# ---------- top 10 bar chart ----------
st.subheader("Top 10 priority UPZ")
st.caption("Ranked by the priority score using your weights. "
           "If you filter by localidad, only UPZ in those localidades are shown; "
           "the rank is still out of all 95 UPZ.")

top = view.nsmallest(10, "custom_rank").sort_values("custom_score")
bar = px.bar(
    top,
    x="custom_score",
    y="short_name",
    orientation="h",
    text=top["custom_score"].round(2),
    hover_data={
        "localidad": True,
        "unemp_rate": ":.1f",
        "avg_commute_min": ":.0f",
        "services_per10k": ":.1f",
        "custom_rank": True,
        "short_name": False,
    },
    labels={
        "custom_score": "Priority score (0–1)",
        "short_name": "",
        "localidad": "Localidad",
        "unemp_rate": "Unemployment (%)",
        "avg_commute_min": "Avg. commute (min)",
        "services_per10k": "Services per 10k",
        "custom_rank": "Priority rank (of 95)",
    },
)
bar.update_traces(marker_color="#2c3e50", textposition="inside", textfont_color="white")
bar.update_layout(height=420, margin=dict(l=0, r=0, t=10, b=0), xaxis_range=[0, 1])
st.plotly_chart(bar, use_container_width=True, config={"displayModeBar": False})

# ---------- comparison chart ----------
st.subheader("How does unemployment relate to access and commutes?")
COMPARE = {
    "Community services per 10,000 residents": "services_per10k",
    "Health facilities per 10,000 residents":  "health_per10k",
    "Transit stations per 10,000 residents":   "transit_station_per10k",
    "Average commute to work (minutes)":       "avg_commute_min",
    "Workers using TransMilenio (%)":          "pct_transmilenio",
}
x_label = st.selectbox("Compare unemployment with:", list(COMPARE))
x_col = COMPARE[x_label]

if len(view) >= 5:
    rho = view[[x_col, "unemp_rate"]].corr(method="spearman").iloc[0, 1]
    st.caption(f"Each dot is one UPZ. Spearman correlation: **{rho:.2f}**. "
               "A negative value means UPZ with more of this tend to have lower unemployment; "
               "a positive value means they tend to have higher unemployment.")
else:
    st.caption("Each dot is one UPZ. Select more localidades (at least 5 UPZ) to calculate a correlation.")

chart_data = view.assign(group=view["custom_rank"].le(10).map({True: "Top 10 priority", False: "Other UPZ"}))
scatter = px.scatter(
    chart_data,
    x=x_col,
    y="unemp_rate",
    size="pop_15plus",
    size_max=25,
    color="group",
    color_discrete_map={"Top 10 priority": "#b2182b", "Other UPZ": "#c7c7c7"},
    category_orders={"group": ["Other UPZ", "Top 10 priority"]},
    hover_name="short_name",
    hover_data={
        "localidad": True,
        x_col: ":.1f",
        "unemp_rate": ":.1f",
        "pop_15plus": ":,.0f",
        "custom_score": ":.2f",
    },
    labels={
        x_col: x_label,
        "unemp_rate": "Unemployment rate (%)",
        "pop_15plus": "Residents aged 15+",
        "custom_score": "Priority score",
        "group": "",
        "localidad": "Localidad",
    },
)
scatter.update_layout(height=480, margin=dict(l=0, r=0, t=40, b=0),
                     legend=dict(orientation="h", x=0, y=1.02, xanchor="left", yanchor="bottom",
                traceorder="reversed"),
)
st.plotly_chart(scatter, use_container_width=True, config={"displayModeBar": False})

# ---------- data table ----------
st.subheader("Explore the data")
st.caption("All indicators for the UPZ shown above, sorted by priority. Click a column header to sort. "
           "The table follows your localidad filter and priority weights.")

TABLE_COLS = {
    "custom_rank":            "Priority rank",
    "short_name":             "UPZ",
    "localidad":              "Localidad",
    "custom_score":           "Priority score",
    "unemp_rate":             "Unemployment (%)",
    "avg_commute_min":        "Avg. commute (min)",
    "pct_transmilenio":       "Workers using TransMilenio (%)",
    "services_per10k":        "Services per 10k",
    "health_per10k":          "Health facilities per 10k",
    "transit_station_per10k": "Transit stations per 10k",
    "pop_15plus":             "Residents aged 15+",
}
table = view[list(TABLE_COLS)].rename(columns=TABLE_COLS).sort_values("Priority rank").round(2)
table["Residents aged 15+"] = table["Residents aged 15+"].round(0).astype(int)

st.dataframe(table, hide_index=True, use_container_width=True)
st.download_button(
    "Download this table (CSV)",
    table.to_csv(index=False).encode("utf-8-sig"),
    file_name="bogota_upz_priorities.csv",
    mime="text/csv",
)

st.caption("Sources: DANE–SDP Encuesta Multipropósito 2021; OpenStreetMap; Datos Abiertos Bogotá.")
