import streamlit as st
import pandas as pd
import plotly.express as px

# Cargar los datos
@st.cache_data
def load_data():
    df = pd.read_csv("archivo.csv")  # Reemplaza con el nombre real si es distinto
    df.columns = [col.strip().replace("/", "").replace(" ", "_") for col in df.columns]
    return df

df = load_data()

st.title("Dashboard de Competencia de Natación 🏊")

# Filtros
nadadores = st.multiselect("Selecciona hasta 4 nadadores:", df.Nadador.unique(), max_selections=4)
estilos = st.multiselect("Selecciona estilo(s):", df.Estilo.unique())
pruebas = st.multiselect("Selecciona prueba(s):", df.Distancia.unique())
etapas = st.multiselect("Selecciona etapa(s):", df.Cat_Prueba.unique())
parametros = st.multiselect("Selecciona parámetro(s):", df.Parametro.unique())

# Filtrado del DataFrame
filtered_df = df[df.Nadador.isin(nadadores) &
                 df.Estilo.isin(estilos) &
                 df.Distancia.isin(pruebas) &
                 df.Cat_Prueba.isin(etapas) &
                 df.Parametro.isin(parametros)]

# Mostrar tabla
st.subheader("Datos Filtrados")
st.dataframe(filtered_df)

# Gráficos por parámetro
for parametro in parametros:
    st.subheader(f"Comparación del parámetro: {parametro}")
    param_df = filtered_df[filtered_df.Parametro == parametro]
    fig = px.line(param_df, 
                  x="Cat_Prueba", 
                  y="Valor", 
                  color="Nadador",
                  markers=True,
                  title=f"{parametro} por Etapa")
    st.plotly_chart(fig, use_container_width=True)

# Resumen general (solo si no hay filtros para diversión)
if not nadadores:
    st.subheader("Resumen General por Estilo")
    fig = px.histogram(df, x="Estilo", color="Parametro")
    st.plotly_chart(fig, use_container_width=True)
