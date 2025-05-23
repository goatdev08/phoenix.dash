"""
Phoenix Team Analyst 🐦‍🔥
Versión 0.1.0  |  Entorno Ubuntu 24.04 LTS · Deploy en Streamlit Cloud (GitHub CI)
-------------------------------------------------------------------------------
Este archivo es el punto único de verdad de la aplicación. Cada incremento
mayor/menor/de parche deberá reflejarse en la constante `APP_VERSION` para poder
etiquetar commits y releases en GitHub.
"""

import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

APP_VERSION = "0.1.0"

# ────────────────────────────────────────────────────────────────────────────────
# 1. DETECCIÓN AUTOMÁTICA DE DISPOSITIVO (ESCRITORIO / MÓVIL)
# ────────────────────────────────────────────────────────────────────────────────
try:
    from streamlit_javascript import st_javascript
    viewport_width = st_javascript("return window.innerWidth;") or 1200
except Exception:
    viewport_width = 1200  # Fallback – escritorio

is_mobile = viewport_width < 992  # Bootstrap md breakpoint

# ────────────────────────────────────────────────────────────────────────────────
# 2. CARGA Y NORMALIZACIÓN DE DATOS
# ────────────────────────────────────────────────────────────────────────────────

@st.cache_data
def load_data(path: str = "archivo.csv") -> pd.DataFrame:
    df = pd.read_csv(path)
    df.columns = [c.strip().replace("/", "").replace(" ", "_") for c in df.columns]

    if "Cat_Prueba" in df.columns:
        df.rename(columns={"Cat_Prueba": "Fase"}, inplace=True)

    phase_map = {
        "PRE-ELIMINAR": "Preliminar", "PRELIMINAR": "Preliminar", "PRE ELIMINAR": "Preliminar",
        "SEMIFINAL": "Semifinal", "SEMI-FINAL": "Semifinal",
        "FINAL": "Final"
    }
    df["Fase"] = df["Fase"].str.upper().str.replace("Ó", "O").map(phase_map).fillna(df["Fase"])

    order_dict = {"Preliminar": 1, "Semifinal": 2, "Final": 3}
    df["Fase_Orden"] = df["Fase"].map(order_dict)

    df["Valor"] = pd.to_numeric(df["Valor"], errors="coerce")
    return df

df = load_data()

# ────────────────────────────────────────────────────────────────────────────────
# 3. CONSTANTES Y DICCIONARIOS AUXILIARES
# ────────────────────────────────────────────────────────────────────────────────

param_translation = {
    "T15 (1)": "Tiempo 15m (1)", "# de BRZ 1": "Numero de Brazadas (1)", "V1": "Velocidad (1)",
    "T25 (1)": "Tiempo 25m (1)", "# de BRZ 2": "Numero de Brazadas (2)", "V2": "Velocidad (2)",
    "T15 (2)": "Tiempo 15m (2)", "BRZ TOTAL": "Total de Brazadas", "V promedio": "Velocidad Promedio",
    "T25 (2)": "Tiempo 25m (2)", "DIST sin F": "Distancia sin Flecha", "F1": "Flechas (1)",
    "T TOTAL": "Tiempo Total", "DIST x BRZ": "Distancia por Brazada", "F2": "Flechas (2)",
    "F promedio": "Promedio Metros en Flecha"
}

param_categories = {
    "Tiempo": ["T15 (1)", "T25 (1)", "T15 (2)", "T25 (2)", "T TOTAL"],
    "Brazadas": ["# de BRZ 1", "# de BRZ 2", "BRZ TOTAL", "DIST x BRZ"],
    "Velocidad": ["V1", "V2", "V promedio"],
    "Flechas": ["F1", "F2", "F promedio", "DIST sin F"]
}

# ────────────────────────────────────────────────────────────────────────────────
# 4. HEADER Y PANEL DE FILTROS
# ────────────────────────────────────────────────────────────────────────────────

st.title("Phoenix Team Analyst 🐦‍🔥")

st.sidebar.markdown("#### Versión de app")
st.sidebar.info(APP_VERSION)

st.sidebar.markdown("### Filtros")

nadadores = st.sidebar.multiselect("Selecciona hasta 4 nadadores:", df.Nadador.unique(), max_selections=4)

estilos = (
    df.Estilo.unique().tolist() if st.sidebar.checkbox("Todos los estilos") else st.sidebar.multiselect("Estilo(s):", df.Estilo.unique())
)

pruebas = (
    df.Distancia.unique().tolist() if st.sidebar.checkbox("Todas las pruebas") else st.sidebar.multiselect("Prueba(s):", df.Distancia.unique())
)

fases = (
    df.Fase.unique().tolist() if st.sidebar.checkbox("Todas las fases") else st.sidebar.multiselect("Fase(s):", df.Fase.unique())
)

parametros = (
    df.Parametro.unique().tolist() if st.sidebar.checkbox("Todos los parámetros") else st.sidebar.multiselect("Parámetro(s):", df.Parametro.unique())
)

# ────────────────────────────────────────────────────────────────────────────────
# 5. FILTRADO DE DATAFRAME
# ────────────────────────────────────────────────────────────────────────────────

filtered_df = df[
    df.Nadador.isin(nadadores) &
    df.Estilo.isin(estilos) &
    df.Distancia.isin(pruebas) &
    df.Fase.isin(fases) &
    df.Parametro.isin(parametros)
]

# ────────────────────────────────────────────────────────────────────────────────
# 6. TABS PRINCIPALES
# ────────────────────────────────────────────────────────────────────────────────

tab1, tab2 = st.tabs(["📊 Gráficos Comparativos", "📋 Detalles por Nadador"])

# TAB 1: GRÁFICOS COMPARATIVOS
with tab1:
    for category, param_list in param_categories.items():
        selected_in_category = [p for p in param_list if p in filtered_df.Parametro.unique()]
        if not selected_in_category:
            continue
        st.markdown(f"### {category}")
        for parametro in selected_in_category:
            nombre_legible = param_translation.get(parametro, parametro)
            param_df = filtered_df[filtered_df.Parametro == parametro]
            for estilo in param_df.Estilo.unique():
                estilo_df = param_df[param_df.Estilo == estilo]
                fig = px.line(
                    estilo_df,
                    x="Fase_Orden",
                    y="Valor",
                    color="Nadador",
                    markers=True,
                    line_group="Nadador",
                    hover_data={"Fase": True, "Fase_Orden": False},
                    title=f"{nombre_legible} – Estilo: {estilo}",
                )
                fig.update_layout(
                    legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5),
                    margin=dict(t=60, b=20 if is_mobile else 60),
                    height=400 if is_mobile else 600,
                )
                fig.update_xaxes(visible=False)
                st.plotly_chart(fig, use_container_width=True)

# TAB 2: DETALLES POR NADADOR
with tab2:
    if nadadores:
        for nadador in nadadores:
            st.markdown(f"#### {nadador}")
            sub_df = filtered_df[filtered_df.Nadador == nadador].copy()
            sub_df["Parametro"] = sub_df["Parametro"].map(param_translation).fillna(sub_df["Parametro"])
            st.dataframe(sub_df, use_container_width=True, height=300 if is_mobile else 600)
    else:
        st.info("Selecciona al menos un nadador para ver los detalles.")

# RANKING GLOBAL
if not nadadores:
    st.subheader("🏆 Ranking de Nadadores por Estilo y Prueba (Tiempo Total)")
    tiempo_total_df = df[df.Parametro == "T TOTAL"].dropna(subset=["Valor"])
    grouped = tiempo_total_df.groupby(["Estilo", "Distancia", "Nadador"], as_index=False)["Valor"].min()
    if is_mobile:
        grouped["Nadador"] = grouped["Nadador"].apply(lambda x: f"{x.split()[0][0]}. {x.split()[-1]}")
    grouped_sorted = grouped.sort_values(by=["Estilo", "Distancia", "Valor"])
    for (estilo, distancia), group in grouped_sorted.groupby(["Estilo", "Distancia"]):
        st.markdown(f"### {estilo} – {distancia}m")
        fig = px.bar(
            group,
            x="Nadador", y="Valor", color="Nadador",
            title=f"Ranking – {estilo} {distancia}m (Tiempo Total)", labels={"Valor": "Tiempo Total (s)"},
        )
        fig.update_layout(showlegend=False, margin=dict(t=50, b=20 if is_mobile else

