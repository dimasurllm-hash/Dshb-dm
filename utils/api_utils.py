#utils\api_utils.py

import requests
import pandas as pd
import streamlit as st
from datetime import datetime
from babel.dates import format_datetime

# Tokens y base URL desde secrets
API_TOKEN = st.secrets["api"]["API_TOKEN"]
API_BASE = st.secrets["api"]["API_BASE"]

@st.cache_data(ttl=86400)
def obtener_datos_api():
    """Obtiene los datos principales desde la API y regresa un DataFrame."""
    url = f"{API_BASE}/datos"
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"Error al obtener datos de la API: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=86400)
def obtener_estado_cuenta_api():
    """Obtiene el estado de cuenta desde la API y regresa un DataFrame y la fecha de corte."""
    url = f"{API_BASE}/estado_cuenta"
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        lista_datos = data.get("datos", [])
        fecha_corte = pd.to_datetime(data.get("fecha_corte"))
        df = pd.DataFrame(lista_datos)

        if df.empty:
            return pd.DataFrame(), None
        return df, fecha_corte
    except Exception as e:
        st.error(f"Error al obtener estado de cuenta: {e}")
        return pd.DataFrame(), None
    
@st.cache_data(ttl=86400)
def obtener_edc_tipo_api():
    """Obtiene el estado de cuenta separado por tipo."""
    
    url = f"{API_BASE}/edc_tipo"
    headers = {"Authorization": f"Bearer {API_TOKEN}"}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        lista_datos = data.get("datos", [])
        fecha_corte = pd.to_datetime(data.get("fecha_corte"))

        df = pd.DataFrame(lista_datos)

        if df.empty:
            return pd.DataFrame(), None

        return df, fecha_corte

    except Exception as e:
        st.error(f"Error al obtener estado de cuenta por tipo: {e}")
        return pd.DataFrame(), None
    
@st.cache_data(ttl=86400)
def obtener_edc_maquinaria_api():
    """Obtiene el estado de cuenta de maquinaria."""

    url = f"{API_BASE}/edc_maquinaria"
    headers = {"Authorization": f"Bearer {API_TOKEN}"}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        lista_datos = data.get("datos", [])
        fecha_corte = pd.to_datetime(data.get("fecha_corte"))

        df = pd.DataFrame(lista_datos)

        if df.empty:
            return pd.DataFrame(), None

        return df, fecha_corte

    except Exception as e:
        st.error(f"Error al obtener estado de cuenta maquinaria: {e}")
        return pd.DataFrame(), None

def mostrar_fecha_actualizacion():
    """Muestra en pantalla la última fecha de actualización obtenida de la API."""
    url = f"{API_BASE}/ultima_actualizacion"
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        fecha_dt = datetime.fromisoformat(data["fecha"])

        fecha_formateada = format_datetime(
            fecha_dt,
            "d 'de' MMMM 'de' yyyy, h:mm a",
            locale="es"
        )

        st.markdown(
            f'<p style="background-color:#DFF2BF; color:#4F8A10; padding:10px; border-radius:5px;">'
            f'🕒 <b>Última actualización de datos:</b> {fecha_formateada}<br>'
            f'📋 <i>{data["descripcion"]}</i>'
            f'</p>',
            unsafe_allow_html=True
        )
    except Exception as e:
        st.error(f"Error al obtener la última actualización: {e}")
