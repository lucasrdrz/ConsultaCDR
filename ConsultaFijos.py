import streamlit as st
import pandas as pd
from googleapiclient.discovery import build
from google.oauth2 import service_account
import json

# Configurar las credenciales y el servicio de la API de Google Sheets
def load_credentials():
    try:
        SERVICE_ACCOUNT_INFO = st.secrets["GCP_KEY_JSON"]
        info = json.loads(SERVICE_ACCOUNT_INFO)
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        credentials = service_account.Credentials.from_service_account_info(info, scopes=SCOPES)
        return build('sheets', 'v4', credentials=credentials)
    except Exception as e:
        st.error(f"Error al configurar las credenciales: {e}")
        st.stop()

service = load_credentials()

SPREADSHEET_ID = '1uC3qyYAmThXMfJ9Pwkompbf9Zs6MWhuTqT8jTVLYdr0'

# Función para leer el stock desde Google Sheets
def leer_stock():
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range='StockFijo!A:E').execute()
    values = result.get('values', [])

    if not values:
        return pd.DataFrame(columns=['Sitio', 'Parte', 'Descripción', 'Stock Físico', 'Stock Óptimo'])

    # Convertimos la primera fila en encabezados, eliminando espacios extra y pasando a minúsculas
    headers = [h.strip().lower() for h in values[0]]  
    print("Encabezados originales desde Google Sheets:", headers)

    df = pd.DataFrame(values[1:], columns=headers)

    # Mapear nombres de columnas correctamente
    column_map = {
        'sitio': 'Sitio', 
        'parte': 'Parte', 
        'descripción': 'Descripción',  
        'stock físico': 'Stock Físico',  
        'stock óptimo': 'Stock Óptimo'  
    }

    # Verificar si todas las claves están en df antes de renombrar
    columnas_actuales = df.columns.tolist()
    print("Columnas originales del DataFrame:", columnas_actuales)

    for col in column_map.keys():
        if col not in columnas_actuales:
            st.error(f"La columna esperada '{col}' no se encontró en los datos de Google Sheets.")
            return pd.DataFrame()  # Devuelve un DataFrame vacío si faltan columnas

    df.rename(columns=column_map, inplace=True)
    print("Columnas después del renombrado:", df.columns.tolist())

    # Convertir columnas numéricas
    try:
        df['Stock Físico'] = pd.to_numeric(df['Stock Físico'], errors='coerce').fillna(0)
        df['Stock Óptimo'] = pd.to_numeric(df['Stock Óptimo'], errors='coerce').fillna(0)
    except KeyError as e:
        st.error(f"Error: No se encontró la columna {e} después del renombrado.")
        return pd.DataFrame()  # Devuelve un DataFrame vacío si falla

    return df

# **Interfaz en Streamlit**
st.title("📦 Control de Stock Fijo - Logística")

st.subheader("📍 Selecciona un sitio para ver su stock:")

# Leer el stock una vez para evitar múltiples llamadas a la API
df_stock = leer_stock()

if not df_stock.empty:
    # Obtener los sitios únicos
    sitios_unicos = sorted(df_stock['Sitio'].unique())

    # Crear expanders por cada sitio con solo la vista de datos
    for sitio in sitios_unicos:
        with st.expander(f"📌 {sitio}", expanded=False):
            df_filtrado = df_stock[df_stock['Sitio'] == sitio]
            st.dataframe(df_filtrado, use_container_width=True)
else:
    st.error("No se pudo cargar el stock. Verifica los nombres de las columnas en Google Sheets.")



