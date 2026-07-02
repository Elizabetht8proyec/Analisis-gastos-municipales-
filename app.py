import streamlit as st
import pandas as pd
import os

# -------------------------------------------------
# CONFIGURACIÓN DE LA PÁGINA
# -------------------------------------------------

st.set_page_config(
    page_title="Análisis de Gastos Municipales",
    layout="wide"
)

# -------------------------------------------------
# CARGA DE DATOS
# -------------------------------------------------

@st.cache_data(show_spinner="Cargando base de datos...")
def cargar_datos():
    ruta_parquet = "gastos_municipales.parquet"
    ruta_excel = "Gastos Municipales Definitivo.xlsx"

    if os.path.exists(ruta_parquet):
        df = pd.read_parquet(ruta_parquet)
    elif os.path.exists(ruta_excel):
        df = pd.read_excel(ruta_excel)
    else:
        raise FileNotFoundError(
            "No se encontró 'gastos_municipales.parquet' ni "
            "'Gastos Municipales Definitivo.xlsx' en la carpeta del proyecto."
        )

    return df

try:
    df = cargar_datos()
except Exception as e:
    st.error(f"❌ Error al cargar los datos: {e}")
    st.stop()

# -------------------------------------------------
# CÁLCULOS PESADOS CACHEADOS (todos juntos, una sola vez)
# -------------------------------------------------

@st.cache_data
def calcular_resumen_general(df):
    nulos = df.isnull().sum().reset_index()
    nulos.columns = ["Columna", "Valores nulos"]
    duplicados = int(df.duplicated().sum())
    return nulos, duplicados

resumen_nulos, resumen_duplicados = calcular_resumen_general(df)

# -------------------------------------------------
# TÍTULO
# -------------------------------------------------

st.title("📊 Análisis de Gastos Municipales")
st.write("""
Aplicativo desarrollado en Streamlit para analizar la distribución
de los registros de gastos municipales en Chile.
""")

# -------------------------------------------------
# MENÚ LATERAL
# -------------------------------------------------

st.sidebar.title("🧭 Menú de navegación")

seccion = st.sidebar.radio(
    "Selecciona una sección:",
    [
        "Inicio",
        "Base de datos",
        "Limpieza y calidad",
        "Análisis descriptivo",
        "Visualizaciones",
        "Perspectivas",
        "Propuesta de mejora"
    ]
)

# -------------------------------------------------
# FILTROS
# -------------------------------------------------

st.sidebar.header("Filtros")

df_filtrado = df

if "REGIÓN" in df.columns:
    region = st.sidebar.selectbox(
        "Filtrar por región:",
        ["Todas"] + sorted(df["REGIÓN"].dropna().unique().tolist())
    )
    if region != "Todas":
        df_filtrado = df_filtrado[df_filtrado["REGIÓN"] == region]

if "ELECCION" in df.columns:
    eleccion = st.sidebar.selectbox(
        "Filtrar por elección:",
        ["Todas"] + sorted(df["ELECCION"].dropna().unique().tolist())
    )
    if eleccion != "Todas":
        df_filtrado = df_filtrado[df_filtrado["ELECCION"] == eleccion]

# -------------------------------------------------
# INICIO
# -------------------------------------------------

if seccion == "Inicio":

    st.header("Inicio")

    st.write("""
    Esta aplicación permite explorar la base de datos de gastos municipales,
    identificando patrones relevantes según región, elección, territorio
    y candidatura.
    """)

    col1, col2, col3 = st.columns(3)
    col1.metric("Registros", f"{df_filtrado.shape[0]:,}")
    col2.metric("Columnas", df_filtrado.shape[1])

    if "REGIÓN" in df_filtrado.columns:
        col3.metric("Regiones", df_filtrado["REGIÓN"].nunique())

# -------------------------------------------------
# BASE DE DATOS
# -------------------------------------------------

elif seccion == "Base de datos":

    st.header("Base de datos")
    st.write("Vista previa de los primeros 100 registros.")
    st.dataframe(df_filtrado.head(100), use_container_width=True)

# -------------------------------------------------
# LIMPIEZA
# -------------------------------------------------

elif seccion == "Limpieza y calidad":

    st.header("Limpieza y calidad")
    st.subheader("Valores nulos")
    st.dataframe(resumen_nulos, use_container_width=True)
    st.metric("Filas duplicadas", resumen_duplicados)

# -------------------------------------------------
# ANÁLISIS DESCRIPTIVO
# -------------------------------------------------

elif seccion == "Análisis descriptivo":

    st.header("Análisis descriptivo")

    col1, col2, col3 = st.columns(3)
    col1.metric("Registros filtrados", f"{df_filtrado.shape[0]:,}")

    if "REGIÓN" in df_filtrado.columns:
        col2.metric("Regiones", df_filtrado["REGIÓN"].nunique())

    if "CANDIDATURA" in df_filtrado.columns:
        col3.metric("Candidaturas", df_filtrado["CANDIDATURA"].nunique())

    st.subheader("Resumen estadístico (columnas numéricas)")
    st.dataframe(df_filtrado.describe(), use_container_width=True)

# -------------------------------------------------
# VISUALIZACIONES
# -------------------------------------------------

elif seccion == "Visualizaciones":

    st.header("📈 Visualizaciones")

    if "REGIÓN" in df_filtrado.columns:
        st.subheader("Cantidad de registros por región")
        st.bar_chart(df_filtrado["REGIÓN"].value_counts().sort_values(ascending=True))

    if "ELECCION" in df_filtrado.columns:
        st.subheader("Cantidad de registros por elección")
        st.bar_chart(df_filtrado["ELECCION"].value_counts().sort_values(ascending=True))

    if "TERRITORIO" in df_filtrado.columns:
        st.subheader("Top 10 territorios con más registros")
        st.bar_chart(df_filtrado["TERRITORIO"].value_counts().head(10).sort_values(ascending=True))

    if "CANDIDATURA" in df_filtrado.columns:
        st.subheader("Top 10 candidaturas con más registros")
        st.bar_chart(df_filtrado["CANDIDATURA"].value_counts().head(10).sort_values(ascending=True))

# -------------------------------------------------
# PERSPECTIVAS
# -------------------------------------------------

elif seccion == "Perspectivas":

    st.header("Perspectivas del análisis")

    if "REGIÓN" in df_filtrado.columns and not df_filtrado.empty:
        region_top = df_filtrado["REGIÓN"].value_counts().idxmax()
        st.info(f"La región con mayor cantidad de registros es: {region_top}")

    if "ELECCION" in df_filtrado.columns and not df_filtrado.empty:
        eleccion_top = df_filtrado["ELECCION"].value_counts().idxmax()
        st.info(f"La elección con mayor cantidad de registros es: {eleccion_top}")

    st.write("""
    El análisis evidencia diferencias en la concentración
    de registros según región y tipo de elección, lo que
    permite identificar territorios con mayor actividad.
    """)

# -------------------------------------------------
# PROPUESTA DE MEJORA
# -------------------------------------------------

elif seccion == "Propuesta de mejora":

    st.header("Propuesta de mejora")

    st.write("""
    Como trabajo futuro, el aplicativo podría incorporar:

    - Mapas interactivos por región y comuna.
    - Indicadores monetarios sobre gastos.
    - Comparación entre candidatos.
    - Exportación automática de reportes.
    - Dashboards especializados para organismos fiscalizadores.
    """)

    st.success(
        "Estas mejoras permitirían transformar la aplicación en una "
        "herramienta de apoyo para el análisis electoral y el control "
        "del gasto público."
    )