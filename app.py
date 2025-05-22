import streamlit as st
import pandas as pd
import plotly.express as px

# Cargar los datos
@st.cache_data
def load_data():
    df = pd.read_csv("archivo.csv")
    df.columns = [col.strip().replace("/", "").replace(" ", "_") for col in df.columns]
    df["Valor"] = pd.to_numeric(df["Valor"], errors="coerce")
    return df

df = load_data()

# Diccionario de nombres legibles para los parámetros
param_translation = {
    "T15 (1)": "Tiempo 15m (1)",
    "# de BRZ 1": "Numero de Brazadas (1)",
    "V1": "Velocidad (1)",
    "T25 (1)": "Tiempo 25m (1)",
    "# de BRZ 2": "Numero de Brazadas (2)",
    "V2": "Velocidad (2)",
    "T15 (2)": "Tiempo 15m (2)",
    "BRZ TOTAL": "Total de Brazadas",
    "V promedio": "Velocidad Promedio",
    "T25 (2)": "Tiempo 25m (2)",
    "DIST sin F": "Distancia sin Flecha",
    "F1": "Flechas (1)",
    "T TOTAL": "Tiempo Total",
    "DIST x BRZ": "Distancia por Brazada",
    "F2": "Flechas (2)",
    "F promedio": "Promedio Metros en Flecha"
}

# Categorías de parámetros
param_categories = {
    "Tiempo": ["T15 (1)", "T25 (1)", "T15 (2)", "T25 (2)", "T TOTAL"],
    "Brazadas": ["# de BRZ 1", "# de BRZ 2", "BRZ TOTAL", "DIST x BRZ"],
    "Velocidad": ["V1", "V2", "V promedio"],
    "Flechas": ["F1", "F2", "F promedio", "DIST sin F"]
}

st.set_page_config(layout="wide")
st.title("Dashboard de Competencia de Natación 🏊")

# Sidebar con filtros
with st.sidebar:
    st.title("Filtros")
    nadadores = st.multiselect("Selecciona hasta 4 nadadores:", df.Nadador.unique(), max_selections=4)

    if st.checkbox("Seleccionar todos los estilos"):
        estilos = df.Estilo.unique().tolist()
    else:
        estilos = st.multiselect("Selecciona estilo(s):", df.Estilo.unique())

    if st.checkbox("Seleccionar todas las pruebas"):
        pruebas = df.Distancia.unique().tolist()
    else:
        pruebas = st.multiselect("Selecciona prueba(s):", df.Distancia.unique())

    if st.checkbox("Seleccionar todas las etapas"):
        etapas = df.Cat_Prueba.unique().tolist()
    else:
        etapas = st.multiselect("Selecciona etapa(s):", df.Cat_Prueba.unique())

    if st.checkbox("Seleccionar todos los parámetros"):
        parametros = df.Parametro.unique().tolist()
    else:
        parametros = st.multiselect("Selecciona parámetro(s):", df.Parametro.unique())

# Filtrado del DataFrame
filtered_df = df[df.Nadador.isin(nadadores) &
                 df.Estilo.isin(estilos) &
                 df.Distancia.isin(pruebas) &
                 df.Cat_Prueba.isin(etapas) &
                 df.Parametro.isin(parametros)]

# Tabs para organización visual
tab1, tab2 = st.tabs(["📊 Gráficos Comparativos", "📋 Detalles por Nadador"])

with tab1:
    for category, param_list in param_categories.items():
        selected_in_category = [p for p in param_list if p in filtered_df.Parametro.unique()]
        if selected_in_category:
            with st.container():
                st.markdown(f"### {category}")
                for parametro in selected_in_category:
                    nombre_legible = param_translation.get(parametro, parametro)
                    param_df = filtered_df[filtered_df.Parametro == parametro]
                    fig = px.line(param_df,
                                  x="Cat_Prueba",
                                  y="Valor",
                                  color="Nadador",
                                  markers=True,
                                  facet_col="Estilo",
                                  line_group="Nadador",
                                  category_orders={"Cat_Prueba": ["Preliminar", "Semifinal", "Final"]},
                                  title=f"{nombre_legible} por Etapa")
                    st.plotly_chart(fig, use_container_width=True)

with tab2:
    if nadadores:
        for nadador in nadadores:
            st.markdown(f"#### {nadador}")
            sub_df = filtered_df[filtered_df.Nadador == nadador].copy()
            sub_df["Parametro"] = sub_df["Parametro"].map(param_translation).fillna(sub_df["Parametro"])
            st.dataframe(sub_df, use_container_width=True)
    else:
        st.write("Selecciona al menos un nadador para ver los detalles.")

# Ranking general por estilo y prueba basado en Tiempo Total
if not nadadores:
    st.subheader("🏆 Ranking de Nadadores por Estilo y Prueba (Tiempo Total)")
    tiempo_total_df = df[df.Parametro == "T TOTAL"].copy()
    tiempo_total_df = tiempo_total_df.dropna(subset=["Valor"])
    grouped = tiempo_total_df.groupby(["Estilo", "Distancia", "Nadador"], as_index=False)["Valor"].min()
    grouped_sorted = grouped.sort_values(by=["Estilo", "Distancia", "Valor"])

    for (estilo, distancia), group in grouped_sorted.groupby(["Estilo", "Distancia"]):
        st.markdown(f"### {estilo} - {distancia}m")
        fig = px.bar(group,
                     x="Nadador",
                     y="Valor",
                     color="Nadador",
                     title=f"Ranking por Tiempo Total - {estilo} {distancia}m",
                     labels={"Valor": "Tiempo Total (seg)"})
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(group, use_container_width=True)



