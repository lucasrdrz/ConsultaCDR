import pandas as pd
import streamlit as st
from googleapiclient.discovery import build
from google.oauth2 import service_account

# Configuración de Google Sheets API
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
SERVICE_ACCOUNT_FILE = "credenciales.json"  # Asegúrate de tener este archivo

# ID de la hoja de cálculo
SPREADSHEET_ID = "TU_SPREADSHEET_ID"

# Autenticación con Google Sheets API
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
service = build("sheets", "v4", credentials=credentials)

def leer_stock():
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range='StockFijo!A:D').execute()
    values = result.get("values", [])

    if not values:
        return pd.DataFrame(columns=["Sitio", "Parte", "Stock Fisico", "Stock Optimo"])

    # Convertimos la primera fila en encabezados, eliminando espacios extra
    headers = [h.strip().lower() for h in values[0]]
    df = pd.DataFrame(values[1:], columns=headers)

    # Renombramos las columnas correctamente
    df.rename(
        columns={
            "sitio": "Sitio",
            "parte": "Parte",
            "stock": "Stock Fisico",
            "stock deberia": "Stock Optimo",
        },
        inplace=True,
    )

    # Convertimos las columnas numéricas correctamente
    df["Stock Fisico"] = pd.to_numeric(df["Stock Fisico"], errors="coerce").fillna(0)
    df["Stock Optimo"] = pd.to_numeric(df["Stock Optimo"], errors="coerce").fillna(0)

    return df

# Streamlit App
st.title("Consulta de Stock")

# Cargar datos desde Google Sheets
df_stock = leer_stock()

# Mostrar datos en Streamlit
st.dataframe(df_stock)




