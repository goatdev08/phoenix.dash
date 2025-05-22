import streamlit as st
import pandas as pd
import plotly.express as px

# Cargar los datos
@st.cache_data
def load_data():
    df = pd.read_csv("archivo.csv")  # Reemplaza con el nombre real si es distinto
    df.columns = [col.strip().replace("/", "").replace(" ", "_") for col in df.columns]
    df["Valor"] = pd.to_numeric(df["Valor"], errors="coerce")
    return df

df = load_data()

st.set_page_config(layout="wide")
st.title("Dashboard de Competencia de Natación 🏊")

# Sidebar con filtros
st.sidebar.title("Filtros")
nadadores = st.sidebar.multiselect("Selecciona hasta 4 nadadores:", df.Nadador.unique(), max_selections=4)
estilos = st.sidebar.multiselect("Selecciona estilo(s):", df.Estilo.unique())
pruebas = st.sidebar.multiselect("Selecciona prueba(s):", df.Distancia.unique())
etapas = st.sidebar.multiselect("Selecciona etapa(s):", df.Cat_Prueba.unique())
parametros = st.sidebar.multiselect("Selecciona parámetro(s):", df.Parametro.unique())

# Filtrado del DataFrame
filtered_df = df[df.Nadador.isin(nadadores) &
                 df.Estilo.isin(estilos) &
                 df.Distancia.isin(pruebas) &
                 df.Cat_Prueba.isin(etapas) &
                 df.Parametro.isin(parametros)]

# Tabs para organización visual
tab1, tab2 = st.tabs(["Gráficos Comparativos", "Detalles por Nadador"])

with tab1:
    for parametro in filtered_df.Parametro.unique():
        st.subheader(f"Comparación del parámetro: {parametro}")
        param_df = filtered_df[filtered_df.Parametro == parametro]
        fig = px.line(param_df, 
                      x="Cat_Prueba", 
                      y="Valor", 
                      color="Nadador",
                      markers=True,
                      facet_col="Estilo",
                      line_group="Nadador",
                      category_orders={"Cat_Prueba": ["Preliminar", "Semifinal", "Final"]},
                      title=f"{parametro} por Etapa")
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    if nadadores:
        cols = st.columns(len(nadadores))
        for idx, nadador in enumerate(nadadores):
            with cols[idx]:
                st.markdown(f"#### {nadador}")
                sub_df = filtered_df[filtered_df.Nadador == nadador]
                st.dataframe(sub_df, use_container_width=True)
    else:
        st.write("Selecciona al menos un nadador para ver los detalles.")

# Resumen general (solo si no hay filtros)
if not nadadores:
    st.subheader("Resumen General por Estilo")
    fig = px.histogram(df, x="Estilo", color="Parametro")
    st.plotly_chart(fig, use_container_width=True)
