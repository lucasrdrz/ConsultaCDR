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
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range='StockFijo!A:D').execute()
    values = result.get('values', [])

    if not values:
        return pd.DataFrame(columns=['Sitio', 'Parte', 'Stock', 'Stock Deberia'])

    # Convertimos la primera fila en encabezados, eliminando espacios extra
    headers = [h.strip().lower() for h in values[0]]  
    df = pd.DataFrame(values[1:], columns=headers)

    # Renombramos las columnas asegurando que coincidan
    column_map = {'sitio': 'Sitio', 'parte': 'Parte', 'stock': 'Stock', 'stock deberia': 'Stock Deberia'}
    df.rename(columns=column_map, inplace=True)

    # Convertimos las columnas numéricas correctamente
    df['Stock'] = pd.to_numeric(df['Stock'], errors='coerce').fillna(0)
    df['Stock Deberia'] = pd.to_numeric(df['Stock Deberia'], errors='coerce').fillna(0)

    return df

# **Interfaz en Streamlit**
st.title("📦 Control de Stock Fijo - Logística")

st.subheader("📍 Selecciona un sitio para ver su stock:")

# Leer el stock una vez para evitar múltiples llamadas a la API
df_stock = leer_stock()

# Obtener los sitios únicos
sitios_unicos = sorted(df_stock['Sitio'].unique())

# Crear expanders por cada sitio con solo la vista de datos
for sitio in sitios_unicos:
    with st.expander(f"📌 {sitio}", expanded=False):
        df_filtrado = df_stock[df_stock['Sitio'] == sitio]
        st.dataframe(df_filtrado, use_container_width=True)


    st.experimental_rerun()

