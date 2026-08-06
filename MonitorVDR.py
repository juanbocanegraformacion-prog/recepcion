import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import math
import json
import requests
import io

# ------------------------------------------------------------
# CONFIGURACIÓN DE PÁGINA
# ------------------------------------------------------------
st.set_page_config(page_title="Monitor VDR - RIOMARKET", layout="wide")

# ------------------------------------------------------------
# INICIALIZAR CACHE BUSTER EN SESSION STATE
# ------------------------------------------------------------
if "cache_buster" not in st.session_state:
    st.session_state.cache_buster = 0

# ------------------------------------------------------------
# CARGA DE DATOS DESDE EXCEL (CON CADUCIDAD AUTOMÁTICA Y BUSTER)
# ------------------------------------------------------------
@st.cache_data(show_spinner=False, ttl=300)
def load_data(cache_buster: int) -> pd.DataFrame:
    url_base = "https://raw.githubusercontent.com/juanbocanegraformacion-prog/recepcion/main/VDR_alerta.xlsx"
    url = f"{url_base}?t={cache_buster}" if cache_buster else url_base
    try:
        response = requests.get(url, headers={'Cache-Control': 'no-cache', 'Pragma': 'no-cache'}, timeout=10)
        response.raise_for_status()
        
        content = response.content
        
        # Diagnostic de formato
        if not content.startswith(b'PK\x03\x04'):
            if content.startswith(b"version https://git-lfs"):
                raise ValueError("GitHub está devolviendo un puntero de 'Git LFS' en lugar del archivo real.")
            elif b"<!DOCTYPE html>" in content or b"<html" in content.lower()[:100]:
                raise ValueError("GitHub devolvió una página HTML. Verifica si el repositorio es privado.")
            elif content.startswith(b'\xd0\xcf\x11\xe0'):
                raise ValueError("El archivo es un formato antiguo .xls renombrado a .xlsx.")
            else:
                raise ValueError(f"Contenido ZIP/XLSX no válido.")

        excel_data = io.BytesIO(content)
        data = pd.read_excel(excel_data, sheet_name="Sheet1", header=1, engine='openpyxl')
        
        # Mapeo exacto de columnas según el Excel VDR_alerta.xlsx
        cols_map = {
            'Sucursal': 'sucursal',
            'Número de VDR': 'vdr',
            'Estatus VDR': 'estatus',
            'Número de ODC': 'odc',
            'Estatus ODC': 'tipo_odc',
            'Producto': 'producto',
            'Proveedor de compra': 'proveedor',
            'Empaques Esperados (ODC)': 'esperado',
            'Empaques Recibidos (VDR)': 'recibido'
        }
        
        data = data[list(cols_map.keys())].rename(columns=cols_map)
        data["esperado"] = pd.to_numeric(data["esperado"], errors="coerce").fillna(0).astype(int)
        data["recibido"] = pd.to_numeric(data["recibido"], errors="coerce").fillna(0).astype(int)
