import os
import sys
import requests as http_requests

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from db.database import SessionLocal
from db.models import Personaje

load_dotenv(os.path.join(BASE_DIR, '.env'))

# Dominio base para construir URLs de imágenes
IMAGE_BASE_URL = "https://cdn.thesimpsonsapi.com/500"

st.set_page_config(
    page_title="The Simpsons - Personajes",
    page_icon="🍩",
    layout="wide"
)

st.title("🍩 The Simpsons — Personajes")
st.markdown("Datos consultados desde la base de datos local.")

@st.cache_data
def cargar_personajes():
    db = SessionLocal()
    try:
        personajes = db.query(Personaje).all()
        return pd.DataFrame([{
            'ID': p.id,
            'Nombre': p.name,
            'Ocupación': p.occupation,
            'Fecha de nacimiento': p.birthdate,
            'Retrato': p.portrait_path,
            'Registrado el': p.created_at.strftime('%Y-%m-%d'),
        } for p in personajes])
    finally:
        db.close()

df = cargar_personajes()

if df.empty:
    st.warning("No hay personajes en la base de datos. Ejecuta el extractor primero.")
    st.stop()

# --- Métricas generales ---
col1, col2, col3 = st.columns(3)
col1.metric("Total de personajes", len(df))
col2.metric("Con ocupación registrada", df['Ocupación'].notna().sum())
col3.metric("Sin ocupación", df['Ocupación'].isna().sum())

st.divider()

# --- Filtro de búsqueda ---
busqueda = st.text_input("🔍 Buscar por nombre u ocupación", placeholder="Ej: Homer, doctor...")

df_filtrado = df.copy()
if busqueda:
    mask = (
        df['Nombre'].str.contains(busqueda, case=False, na=False) |
        df['Ocupación'].str.contains(busqueda, case=False, na=False)
    )
    df_filtrado = df[mask]

st.markdown(f"**{len(df_filtrado)} resultado(s)**")

# --- Tabla de personajes ---
st.dataframe(
    df_filtrado[['ID', 'Nombre', 'Ocupación', 'Fecha de nacimiento']],
    use_container_width=True,
    hide_index=True
)

# --- Detalle de personaje ---
st.divider()
st.subheader("🔎 Detalle de personaje")

nombres = df_filtrado['Nombre'].dropna().sort_values().tolist()
if nombres:
    seleccionado = st.selectbox("Selecciona un personaje", nombres)
    fila = df_filtrado[df_filtrado['Nombre'] == seleccionado].iloc[0]

    col_img, col_info = st.columns([1, 2])

    with col_img:
        if pd.notna(fila['Retrato']) and fila['Retrato']:
            portrait_url = fila['Retrato']
            if portrait_url.startswith('/'):
                portrait_url = IMAGE_BASE_URL + portrait_url
            try:
                resp = http_requests.get(portrait_url, timeout=10)
                resp.raise_for_status()
                st.image(resp.content, width=200)
                print(f"Imagen cargada desde {portrait_url}")
            except Exception:
                st.info("No se pudo cargar la imagen")
        else:
            st.info("Sin imagen disponible")

    with col_info:
        st.markdown(f"**Nombre:** {fila['Nombre']}")
        st.markdown(f"**Ocupación:** {fila['Ocupación'] or '—'}")
        st.markdown(f"**Fecha de nacimiento:** {fila['Fecha de nacimiento'] or '—'}")
        st.markdown(f"**ID:** {fila['ID']}")
        st.markdown(f"**Registrado el:** {fila['Registrado el']}")
