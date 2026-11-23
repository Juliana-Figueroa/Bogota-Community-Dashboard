
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

# ---------- language ----------
lang_choice = st.sidebar.radio("Language / Idioma", ["English", "Español"], horizontal=True, key="lang")
L = "es" if lang_choice == "Español" else "en"

# All visible text, in English and Spanish
T = {
    # page
    "title": {
        "en": "Where does Bogotá need support most?",
        "es": "¿Dónde necesita más apoyo Bogotá?",
    },
    "subtitle": {
        "en": "This dashboard shows where people face the most barriers to finding work in Bogotá."
              "Explore relationships between high unemployment locations and services such as transportation or health. "
              "It helps decision-makers and residents see which of the city's 95 zones (UPZ) "
              "should be prioritized for new services, job programs, or transportation.",
        "es": "Este tablero muestra dónde las personas enfrentan más obstáculos para encontrar empleo en Bogotá. "
              "Explora vínculos entre zonas de alto desempleo, y distintos servicios como trasporte o salud. "
              "Ayuda a quienes toman decisiones y a los ciudadanos a ver cuáles de las 95 zonas de la ciudad (UPZ) "
              "deberían priorizarse para nuevos servicios, programas de empleo o transporte.",
    },
    "how_to": {
        "en": "**How to use it**\n"
              "1. **Look at the map.** Darker red means an area needs more support.\n"
              "2. **Tap or hover over an area** to see its details.\n"
              "3. **Open the menu** (the **»** arrow at the top left on phones) to change what the map shows, "
              "focus on specific localidades, or decide which problems matter most to you.\n"
              "4. **Scroll down** to see the 10 areas with the most need, a comparison chart, and the full data.",
        "es": "**Cómo usarlo**\n"
              "1. **Mire el mapa.** Un rojo más oscuro significa que la zona necesita más apoyo.\n"
              "2. **Toque o pase el cursor sobre una zona** para ver sus detalles.\n"
              "3. **Abra el menú** (la flecha **»** arriba a la izquierda en el celular) para cambiar lo que muestra el mapa, "
              "ver solo algunas localidades o decidir qué problemas son más importantes para usted.\n"
              "4. **Desplácese hacia abajo** para ver las 10 zonas con más necesidad, una gráfica de comparación y todos los datos.",
    },
    "finding_static": {
        "en": "**Key finding:** The south and southwest of the city (Bosa, Kennedy, Ciudad Bolívar, Usme and San Cristóbal) "
              "combine the highest unemployment, the longest trips to work, and the fewest nearby services.",
        "es": "**Hallazgo principal:** El sur y el suroccidente de la ciudad (Bosa, Kennedy, Ciudad Bolívar, Usme y San Cristóbal) "
              "combinan el mayor desempleo, los viajes más largos al trabajo y la menor cantidad de servicios cercanos.",
    },
    "finding_dynamic": {
        "en": "With your current settings, the area with the most need is **{name}** ({loc}).",
        "es": "Con sus prioridades actuales, la zona con más necesidad es **{name}** ({loc}).",
    },
    "glossary_title": {
        "en": "What do these terms mean?",
        "es": "¿Qué significan estos términos?",
    },
    "glossary": {
        "en": "- **UPZ (Unidad de Planeamiento Zonal):** a planning zone, usually a group of nearby neighborhoods. "
              "Bogotá's urban area is divided into 95 of them for this dashboard.\n"
              "- **Localidad:** one of Bogotá's 19 urban districts. Each localidad contains several UPZ.\n"
              "- **Need score:** a number from 0 to 1 that combines several problems into one. "
              "1 means the area has the most need compared with the rest of the city.\n"
              "- **Unemployment rate:** out of every 100 people who want to work, how many cannot find a job.\n"
              "- **Per 10,000 residents:** the number of places (for example, clinics) compared with how many people live there, "
              "so large and small zones can be compared fairly.\n"
              "- **Data sources:** DANE and Secretaría Distrital de Planeación, Encuesta Multipropósito 2021 (unemployment and commutes); "
              "OpenStreetMap (location of services); Datos Abiertos Bogotá (zone boundaries). "
              "OpenStreetMap is built by volunteers, so some places may be missing.",
        "es": "- **UPZ (Unidad de Planeamiento Zonal):** una zona de planeación, generalmente un grupo de barrios cercanos. "
              "En este tablero, el área urbana de Bogotá está dividida en 95 UPZ.\n"
              "- **Localidad:** una de las 19 localidades urbanas de Bogotá. Cada localidad tiene varias UPZ.\n"
              "- **Índice de necesidad:** un número de 0 a 1 que combina varios problemas en uno solo. "
              "1 significa que la zona tiene la mayor necesidad en comparación con el resto de la ciudad.\n"
              "- **Tasa de desempleo:** de cada 100 personas que quieren trabajar, cuántas no encuentran empleo.\n"
              "- **Por cada 10.000 habitantes:** la cantidad de lugares (por ejemplo, centros de salud) en relación con cuántas personas viven allí, "
              "para comparar de manera justa zonas grandes y pequeñas.\n"
              "- **Fuentes de datos:** DANE y Secretaría Distrital de Planeación, Encuesta Multipropósito 2021 (desempleo y viajes al trabajo); "
              "OpenStreetMap (ubicación de servicios); Datos Abiertos Bogotá (límites de las zonas). "
              "OpenStreetMap es construido por voluntarios, así que pueden faltar algunos lugares.",
    },

    # sidebar
    "map_options": {"en": "Map options", "es": "Opciones del mapa"},
    "layer_label": {"en": "What should the map show?", "es": "¿Qué quiere ver en el mapa?"},
    "loc_label": {
        "en": "Focus on specific localidades (optional)",
        "es": "Ver solo algunas localidades (opcional)",
    },
    "loc_placeholder": {"en": "All localidades", "es": "Todas las localidades"},
    "res_label": {
        "en": "Show places on the map (optional)",
        "es": "Mostrar lugares en el mapa (opcional)",
    },
    "res_placeholder": {"en": "None selected", "es": "Ninguno seleccionado"},
    "weights_header": {"en": "What matters most to you?", "es": "¿Qué es más importante para usted?"},
    "weights_caption": {
        "en": "Move the sliders to decide how much each problem counts when ranking areas. "
              "0 = don't count it, 5 = very important.",
        "es": "Mueva los controles para decidir cuánto cuenta cada problema al ordenar las zonas. "
              "0 = no lo tenga en cuenta, 5 = muy importante.",
    },
    "w_need_unemployment": {"en": "Unemployment", "es": "Desempleo"},
    "w_need_commute": {"en": "Long trips to work", "es": "Viajes largos al trabajo"},
    "w_need_services": {"en": "Few community services", "es": "Pocos servicios comunitarios"},
    "w_need_health": {"en": "Few health centers", "es": "Pocos centros de salud"},
    "w_need_transit": {"en": "Few TransMilenio stations", "es": "Pocas estaciones de TransMilenio"},
    "zero_warning": {
        "en": "All sliders are at 0, so every problem is counted equally.",
        "es": "Todos los controles están en 0, así que todos los problemas cuentan por igual.",
    },

    # map layers: names and short descriptions
    "name_custom_score": {
        "en": "Need score (based on your priorities)",
        "es": "Índice de necesidad (según sus prioridades)",
    },
    "desc_custom_score": {
        "en": "From 0 to 1. Darker = more need. Change what matters most to you in the menu.",
        "es": "De 0 a 1. Más oscuro = más necesidad. Cambie lo que es más importante para usted en el menú.",
    },
    "name_unemp_rate": {"en": "Unemployment rate (%)", "es": "Tasa de desempleo (%)"},
    "desc_unemp_rate": {
        "en": "Out of every 100 people who want to work, how many cannot find a job.",
        "es": "De cada 100 personas que quieren trabajar, cuántas no encuentran empleo.",
    },
    "name_avg_commute_min": {
        "en": "Average trip to work (minutes)",
        "es": "Tiempo promedio de viaje al trabajo (minutos)",
    },
    "desc_avg_commute_min": {
        "en": "How long workers who live in the area take to get to work, one way.",
        "es": "Cuánto tardan en llegar al trabajo (solo ida) las personas que viven en la zona.",
    },
    "name_pct_transmilenio": {
        "en": "Workers who use TransMilenio (%)",
        "es": "Trabajadores que usan TransMilenio (%)",
    },
    "desc_pct_transmilenio": {
        "en": "Out of every 100 workers, how many use TransMilenio to get to work.",
        "es": "De cada 100 trabajadores, cuántos usan TransMilenio para llegar al trabajo.",
    },
    "name_services_per10k": {
        "en": "Community services per 10,000 residents",
        "es": "Servicios comunitarios por cada 10.000 habitantes",
    },
    "desc_services_per10k": {
        "en": "Schools, health centers, churches, community centers and similar places, compared with how many people live there.",
        "es": "Colegios, centros de salud, iglesias, salones comunales y lugares similares, en relación con cuántas personas viven allí.",
    },
    "name_health_per10k": {
        "en": "Health centers per 10,000 residents",
        "es": "Centros de salud por cada 10.000 habitantes",
    },
    "desc_health_per10k": {
        "en": "Hospitals, clinics and doctors' offices, compared with how many people live there.",
        "es": "Hospitales, clínicas y consultorios médicos, en relación con cuántas personas viven allí.",
    },
    "name_transit_station_per10k": {
        "en": "TransMilenio stations per 10,000 residents",
        "es": "Estaciones de TransMilenio por cada 10.000 habitantes",
    },
    "desc_transit_station_per10k": {
        "en": "TransMilenio and TransMiCable stations, compared with how many people live there.",
        "es": "Estaciones de TransMilenio y TransMiCable, en relación con cuántas personas viven allí.",
    },

    # places on the map
    "res_health": {"en": "Health centers", "es": "Centros de salud"},
    "res_transit_station": {"en": "TransMilenio and TransMiCable stations", "es": "Estaciones de TransMilenio y TransMiCable"},
    "res_employment_services": {"en": "Employment offices", "es": "Oficinas de empleo"},
    "res_caja_recreation": {"en": "Caja de compensación recreation centers", "es": "Centros recreativos de cajas de compensación"},
    "res_education": {"en": "Schools and libraries", "es": "Colegios y bibliotecas"},
    "res_worship": {"en": "Places of worship", "es": "Iglesias"},
    "res_community": {"en": "Community and social services", "es": "Servicios comunitarios y sociales"},
    "res_bus_stop": {"en": "SITP bus stops", "es": "Paraderos del SITP"},
    "no_name": {"en": "(no name)", "es": "(sin nombre)"},

    # hover labels
    "h_unemp": {"en": "Unemployment (%)", "es": "Desempleo (%)"},
    "h_commute": {"en": "Trip to work (min)", "es": "Trayecto hacia el trabajo (min)"},
    "h_services": {"en": "Services per 10,000 residents", "es": "Servicios por cada 10.000 hab."},
    "h_rank": {"en": "Need rank (out of 95)", "es": "Puesto de necesidad (de 95)"},
    "h_score": {"en": "Need score", "es": "Índice de necesidad"},
    "h_pop": {"en": "Residents aged 15+", "es": "Habitantes de 15 años o más"},

    # top 10 chart
    "top_title": {"en": "The 10 areas with the most need", "es": "Las 10 zonas con más necesidad"},
    "top_caption": {
        "en": "Based on what you chose as most important. A longer bar means more need. "
              "If you focus on some localidades, only their areas appear, but the rank still compares them with all 95 areas.",
        "es": "Según lo que usted eligió como más importante. Una barra más larga significa más necesidad. "
              "Si elige algunas localidades, solo aparecen sus zonas, pero el puesto se sigue comparando con las 95 zonas.",
    },
    "bar_x": {"en": "Need score (0 to 1)", "es": "Índice de necesidad (0 a 1)"},

    # comparison chart
    "cmp_title": {
        "en": "Is unemployment higher where there are fewer services or longer trips to work?",
        "es": "¿Hay más desempleo donde hay menos servicios o viajes más largos al trabajo?",
    },
    "cmp_label": {"en": "Compare unemployment with:", "es": "Comparar el desempleo con:"},
    "cmp_caption": {
        "en": "Each circle is one area; bigger circles have more residents. Red circles are the 10 areas with the most need. "
              "**What it shows:** {strength}: {direction} (Spearman correlation: {rho:.2f}).",
        "es": "Cada círculo es una zona; los círculos más grandes tienen más habitantes. Los círculos rojos son las 10 zonas con más necesidad. "
              "**Qué muestra:** {strength}: {direction} (correlación de Spearman: {rho:.2f}).",
    },
    "cmp_too_few": {
        "en": "Each circle is one area. Select more localidades (at least 5 areas) to describe the relationship.",
        "es": "Cada círculo es una zona. Seleccione más localidades (al menos 5 zonas) para describir la relación.",
    },
    "rel_none": {"en": "Little or no relationship", "es": "Poca o ninguna relación"},
    "rel_weak": {"en": "A weak relationship", "es": "Una relación débil"},
    "rel_moderate": {"en": "A moderate relationship", "es": "Una relación moderada"},
    "rel_strong": {"en": "A strong relationship", "es": "Una relación fuerte"},
    "dir_none": {
        "en": "this factor does not clearly go up or down with unemployment",
        "es": "este factor no sube ni baja claramente con el desempleo",
    },
    "dir_less": {
        "en": "areas with more of this tend to have LESS unemployment",
        "es": "las zonas con más de esto tienden a tener MENOS desempleo",
    },
    "dir_more": {
        "en": "areas with more of this tend to have MORE unemployment",
        "es": "las zonas con más de esto tienden a tener MÁS desempleo",
    },
    "grp_top": {"en": "10 areas with the most need", "es": "10 zonas con más necesidad"},
    "grp_other": {"en": "Other areas", "es": "Otras zonas"},

    # data table
    "table_title": {"en": "See and download the data", "es": "Ver y descargar los datos"},
    "table_caption": {
        "en": "All the numbers for the areas shown above, from most to least need. Click a column name to sort. "
              "The table follows your localidad selection and priorities.",
        "es": "Todos los datos de las zonas que se muestran arriba, de mayor a menor necesidad. Haga clic en el nombre de una columna para ordenar. "
              "La tabla sigue las localidades y prioridades que usted eligió.",
    },
    "col_rank": {"en": "Need rank", "es": "Puesto de necesidad"},
    "col_upz": {"en": "Area (UPZ)", "es": "Zona (UPZ)"},
    "col_localidad": {"en": "Localidad", "es": "Localidad"},
    "col_score": {"en": "Need score", "es": "Índice de necesidad"},
    "col_unemp": {"en": "Unemployment (%)", "es": "Desempleo (%)"},
    "col_commute": {"en": "Trip to work (min)", "es": "Trayecto hacia el trabajo (min)"},
    "col_tm": {"en": "Workers using TransMilenio (%)", "es": "Trabajadores que usan TransMilenio (%)"},
    "col_services": {"en": "Services per 10,000", "es": "Servicios por cada 10.000"},
    "col_health": {"en": "Health centers per 10,000", "es": "Centros de salud por cada 10.000"},
    "col_transit": {"en": "TransMilenio stations per 10,000", "es": "Estaciones de TransMilenio por cada 10.000"},
    "col_pop": {"en": "Residents aged 15+", "es": "Habitantes de 15 años o más"},
    "download": {"en": "Download this table (CSV)", "es": "Descargar esta tabla (CSV)"},

    # footer
    "sources": {
        "en": "Sources: DANE–SDP Encuesta Multipropósito 2021; OpenStreetMap; Datos Abiertos Bogotá. "
              "Best viewed in Chrome, Firefox, or an updated Safari.",
        "es": "Fuentes: DANE–SDP Encuesta Multipropósito 2021; OpenStreetMap; Datos Abiertos Bogotá. "
              "Se ve mejor en Chrome, Firefox o una versión actualizada de Safari.",
    },
}

def tr(key, **values):
    """Return the text for `key` in the selected language."""
    text = T[key][L]
    return text.format(**values) if values else text

# ---------- settings (internal names stay the same in both languages) ----------
LAYER_KEYS = ["custom_score", "unemp_rate", "avg_commute_min", "pct_transmilenio",
              "services_per10k", "health_per10k", "transit_station_per10k"]
LAYER_SCALE = {
    "custom_score": "Reds", "unemp_rate": "Reds", "avg_commute_min": "Oranges",
    "pct_transmilenio": "Blues", "services_per10k": "Greens",
    "health_per10k": "Greens", "transit_station_per10k": "Purples",
}
RES_COLORS = {
    "health": "black", "transit_station": "gold", "employment_services": "deeppink",
    "caja_recreation": "#00b8d4", "education": "#1f4fe0", "worship": "#9467bd",
    "community": "#2ca02c", "bus_stop": "gray",
}
NEEDS = ["need_unemployment", "need_commute", "need_services", "need_health", "need_transit"]

# ---------- sidebar: map options ----------
st.sidebar.header(tr("map_options"))
layer = st.sidebar.selectbox(tr("layer_label"), LAYER_KEYS,
                             format_func=lambda k: tr("name_" + k), key="layer")
localidades = st.sidebar.multiselect(tr("loc_label"), sorted(upz["localidad"].unique()),
                                     placeholder=tr("loc_placeholder"), key="locs")
show_res = st.sidebar.multiselect(tr("res_label"), list(RES_COLORS),
                                  format_func=lambda k: tr("res_" + k),
                                  placeholder=tr("res_placeholder"), key="res")

# ---------- sidebar: priorities ----------
st.sidebar.header(tr("weights_header"))
st.sidebar.caption(tr("weights_caption"))
weights = {col: st.sidebar.slider(tr("w_" + col), 0, 5, 1, key=col) for col in NEEDS}

total = sum(weights.values())
if total == 0:
    st.sidebar.warning(tr("zero_warning"))
    weights = {col: 1 for col in weights}
    total = len(weights)

# ---------- custom need score ----------
upz["custom_score"] = sum(upz[col] * w for col, w in weights.items()) / total
upz["custom_rank"] = upz["custom_score"].rank(ascending=False, method="min").astype(int)

view = upz[upz["localidad"].isin(localidades)] if localidades else upz

# labels used in hover boxes
HOVER_LABELS = {
    "localidad": "Localidad",
    "unemp_rate": tr("h_unemp"),
    "avg_commute_min": tr("h_commute"),
    "services_per10k": tr("h_services"),
    "custom_rank": tr("h_rank"),
    "custom_score": tr("h_score"),
    "pop_15plus": tr("h_pop"),
}

# ---------- title, instructions, key finding ----------
st.title(tr("title"))
st.markdown(tr("subtitle"))
st.markdown(tr("how_to"))

top1 = upz.loc[upz["custom_rank"].idxmin()]
st.info(tr("finding_static") + "\n\n" + tr("finding_dynamic", name=top1["short_name"], loc=top1["localidad"]))

with st.expander(tr("glossary_title")):
    st.markdown(tr("glossary"))

# ---------- map ----------
st.caption(f"**{tr('name_' + layer)}:** {tr('desc_' + layer)}")

map_labels = dict(HOVER_LABELS)
map_labels[layer] = tr("name_" + layer)

fig = px.choropleth_map(
    view,
    geojson=geo,
    locations="survey_code",
    featureidkey="properties.survey_code",
    color=layer,
    color_continuous_scale=LAYER_SCALE[layer],
    range_color=(upz[layer].min(), upz[layer].quantile(0.95)),
    hover_name="short_name",
    hover_data={
        "survey_code": False,
        "localidad": True,
        "unemp_rate": ":.1f",
        "avg_commute_min": ":.0f",
        "services_per10k": ":.1f",
        "custom_rank": True,
    },
    labels=map_labels,
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

for cat in show_res:
    pts = res[res["category"] == cat]
    if localidades:
        pts = pts[pts["localidad"].isin(localidades)]
    label = tr("res_" + cat)
    fig.add_trace(go.Scattermap(
        lat=pts["lat"],
        lon=pts["lon"],
        mode="markers",
        marker=dict(size=7, color=RES_COLORS[cat]),
        name=f"{label} ({len(pts)})",
        text=pts["name"].fillna(tr("no_name")) + "<br>" + pts["upz"],
        hovertemplate="<b>%{text}</b><extra>" + label + "</extra>",
    ))
fig.update_layout(legend=dict(x=0.01, y=0.01, xanchor="left", yanchor="bottom",
                              bgcolor="rgba(255,255,255,0.85)"))

st.plotly_chart(fig, use_container_width=True)
st.markdown("<br><br>", unsafe_allow_html=True)

# ---------- top 10 bar chart ----------
st.subheader(tr("top_title"))
st.caption(tr("top_caption"))

top = view.nsmallest(10, "custom_rank").sort_values("custom_score")
bar_labels = dict(HOVER_LABELS)
bar_labels.update({"custom_score": tr("bar_x"), "short_name": ""})

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
    labels=bar_labels,
)
bar.update_traces(marker_color="#4a5d7a", textposition="inside", textfont_color="white")
bar.update_layout(height=420, margin=dict(l=0, r=0, t=10, b=0), xaxis_range=[0, 1])
st.plotly_chart(bar, use_container_width=True, config={"displayModeBar": False})

# ---------- comparison chart ----------
st.subheader(tr("cmp_title"))
COMPARE_KEYS = ["services_per10k", "health_per10k", "transit_station_per10k",
                "avg_commute_min", "pct_transmilenio"]
x_col = st.selectbox(tr("cmp_label"), COMPARE_KEYS,
                     format_func=lambda k: tr("name_" + k), key="compare")

if len(view) >= 5:
    rho = view[[x_col, "unemp_rate"]].corr(method="spearman").iloc[0, 1]
    size = abs(rho)
    if size < 0.2:
        strength, direction = tr("rel_none"), tr("dir_none")
    else:
        strength = tr("rel_weak") if size < 0.4 else tr("rel_moderate") if size < 0.6 else tr("rel_strong")
        direction = tr("dir_less") if rho < 0 else tr("dir_more")
    st.caption(tr("cmp_caption", strength=strength, direction=direction, rho=rho))
else:
    st.caption(tr("cmp_too_few"))

grp_top, grp_other = tr("grp_top"), tr("grp_other")
chart_data = view.assign(group=view["custom_rank"].le(10).map({True: grp_top, False: grp_other}))
scatter_labels = dict(HOVER_LABELS)
scatter_labels.update({x_col: tr("name_" + x_col), "unemp_rate": tr("name_unemp_rate"), "group": ""})

scatter = px.scatter(
    chart_data,
    x=x_col,
    y="unemp_rate",
    size="pop_15plus",
    size_max=25,
    color="group",
    color_discrete_map={grp_top: "#b2182b", grp_other: "#c7c7c7"},
    category_orders={"group": [grp_other, grp_top]},
    hover_name="short_name",
    hover_data={
        "localidad": True,
        x_col: ":.1f",
        "unemp_rate": ":.1f",
        "pop_15plus": ":,.0f",
        "custom_score": ":.2f",
        "group": False,
    },
    labels=scatter_labels,
)
scatter.update_layout(
    height=480,
    margin=dict(l=0, r=0, t=40, b=0),
    legend=dict(orientation="h", x=0, y=1.02, xanchor="left", yanchor="bottom",
                traceorder="reversed"),
)
st.plotly_chart(scatter, use_container_width=True, config={"displayModeBar": False})

# ---------- data table ----------
with st.expander(tr("table_title")):
    st.caption(tr("table_caption"))
    TABLE_COLS = {
        "custom_rank": tr("col_rank"),
        "short_name": tr("col_upz"),
        "localidad": tr("col_localidad"),
        "custom_score": tr("col_score"),
        "unemp_rate": tr("col_unemp"),
        "avg_commute_min": tr("col_commute"),
        "pct_transmilenio": tr("col_tm"),
        "services_per10k": tr("col_services"),
        "health_per10k": tr("col_health"),
        "transit_station_per10k": tr("col_transit"),
        "pop_15plus": tr("col_pop"),
    }
    table = view[list(TABLE_COLS)].rename(columns=TABLE_COLS).sort_values(tr("col_rank")).round(2)
    table[tr("col_pop")] = table[tr("col_pop")].round(0).astype(int)

    st.dataframe(table, hide_index=True, use_container_width=True)
    st.download_button(
        tr("download"),
        table.to_csv(index=False).encode("utf-8-sig"),
        file_name="bogota_upz_priorities.csv",
        mime="text/csv",
    )

st.caption(tr("sources"))
