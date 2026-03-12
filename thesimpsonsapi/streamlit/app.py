import os
import sys
import requests as http_requests

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from db.database import SessionLocal, init_db
from db.models import Personaje

load_dotenv(os.path.join(BASE_DIR, '.env'))

IMAGE_BASE_URL = "https://cdn.thesimpsonsapi.com/500"
LOGO_PATH    = os.path.join(os.path.dirname(__file__), "img", "logo.webp")
HERO_PATH    = os.path.join(os.path.dirname(__file__), "img", "hero.webp")
CLOUDS_PATH  = os.path.join(os.path.dirname(__file__), "img", "clouds-bg.jpg")
CSS_PATH     = os.path.join(os.path.dirname(__file__), "styles.css")

def load_css(path: str) -> None:
    """Inyecta un archivo .css en la app de Streamlit."""
    with open(path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.set_page_config(
    page_title="The Simpsons — Personajes",
    page_icon="🍩",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Estilos: fondo dinámico (base64) + archivo CSS ──────────────────────────
import base64 as _b64_bg
_clouds_css = ""
if os.path.exists(CLOUDS_PATH):
    with open(CLOUDS_PATH, "rb") as _f:
        _clouds_b64 = _b64_bg.b64encode(_f.read()).decode()
    _clouds_css = f'url("data:image/jpeg;base64,{_clouds_b64}")'

st.markdown(f"""
<style>
[data-testid="stAppViewContainer"] {{
    background-color: #72C8E8;
    background-image: {_clouds_css};
    background-size: cover;
    background-position: center top;
    background-attachment: fixed;
    color: var(--text);
}}
</style>
""", unsafe_allow_html=True)

load_css(CSS_PATH)


# ── Carga de datos ───────────────────────────────────────────────────────────
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

# ── Header ──────────────────────────────────────────────────────────────────
import base64
hero_html = ""
if os.path.exists(HERO_PATH):
    with open(HERO_PATH, "rb") as f:
        hero_b64 = base64.b64encode(f.read()).decode()
    hero_html = f'<img src="data:image/webp;base64,{hero_b64}" alt="The Simpsons API"/>'

st.markdown(f"""
<div class="hero-block">
    <div class="hero-img">{hero_html}</div>
    <p class="hero-sub">La base de datos de personajes del universo de Springfield</p>
    <p class="hero-authors">Juan Diego Andrade Cardozo &nbsp;·&nbsp; Juan Carlos Tamayo Andrade</p>
</div>
""", unsafe_allow_html=True)

if df.empty:
    st.warning("No hay personajes en la base de datos. Ejecuta el extractor primero.")
    st.stop()

# ── Métricas ─────────────────────────────────────────────────────────────────
c1, c2, c3 = st.columns(3)
metrics = [
    ("Total de personajes",      len(df)),
    ("Con ocupación registrada", int(df['Ocupación'].notna().sum())),
    ("Sin ocupación",            int(df['Ocupación'].isna().sum())),
]
for col, (label, value) in zip([c1, c2, c3], metrics):
    with col:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{value}</div>
            <div class="metric-label">{label}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown('<div class="section-sep"></div>', unsafe_allow_html=True)

# ── Búsqueda ─────────────────────────────────────────────────────────────────
st.markdown('<p class="section-label">Explorar personajes</p>', unsafe_allow_html=True)
busqueda = st.text_input(
    label="busqueda",
    placeholder="Buscar por nombre u ocupación…",
    label_visibility="collapsed"
)

df_filtrado = df.copy()
if busqueda:
    mask = (
        df['Nombre'].str.contains(busqueda, case=False, na=False) |
        df['Ocupación'].str.contains(busqueda, case=False, na=False)
    )
    df_filtrado = df[mask]

st.markdown(
    f'<span class="results-badge">{len(df_filtrado)} resultado{"s" if len(df_filtrado) != 1 else ""}</span>',
    unsafe_allow_html=True
)

# ── Tabla ─────────────────────────────────────────────────────────────────────
cols_tabla = ['ID', 'Nombre', 'Ocupación', 'Fecha de nacimiento', 'Registrado el']
filas_html = ""
for _, row in df_filtrado[cols_tabla].iterrows():
    celdas = "".join(f"<td>{'' if pd.isna(v) else v}</td>" for v in row)
    filas_html += f"<tr>{celdas}</tr>"

encabezados = "".join(f"<th>{c}</th>" for c in cols_tabla)

st.markdown(f"""
<div class="tabla-wrap">
    <table class="tabla-personajes">
        <thead><tr>{encabezados}</tr></thead>
        <tbody>{filas_html}</tbody>
    </table>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="section-sep"></div>', unsafe_allow_html=True)

# ── Detalle ───────────────────────────────────────────────────────────────────
st.markdown('<p class="section-label">Detalle de personaje</p>', unsafe_allow_html=True)

nombres = df_filtrado['Nombre'].dropna().sort_values().tolist()
if nombres:
    seleccionado = st.selectbox(
        label="personaje",
        options=nombres,
        label_visibility="collapsed"
    )
    fila = df_filtrado[df_filtrado['Nombre'] == seleccionado].iloc[0]

    col_img, col_info = st.columns([1, 2], gap="large")

    with col_img:
        if pd.notna(fila['Retrato']) and fila['Retrato']:
            portrait_url = fila['Retrato']
            if portrait_url.startswith('/'):
                portrait_url = IMAGE_BASE_URL + portrait_url
            try:
                resp = http_requests.get(portrait_url, timeout=10)
                resp.raise_for_status()
                import base64 as _b64
                img_b64 = _b64.b64encode(resp.content).decode()
                st.markdown(f"""
                <div class="portrait-wrap">
                    <img src="data:image/jpeg;base64,{img_b64}" alt="{seleccionado}"/>
                </div>
                """, unsafe_allow_html=True)
            except Exception:
                st.markdown('<div class="portrait-wrap"><p style="color:var(--muted);font-size:0.85rem">Sin imagen disponible</p></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="portrait-wrap"><p style="color:var(--muted);font-size:0.85rem">Sin imagen disponible</p></div>', unsafe_allow_html=True)

    with col_info:
        campos = [
            ("Nombre",             fila['Nombre']),
            ("Ocupación",          fila['Ocupación'] or "—"),
            ("Fecha de nacimiento", fila['Fecha de nacimiento'] or "—"),
            ("ID",                 fila['ID']),
            ("Registrado el",      fila['Registrado el']),
        ]
        rows_html = "".join(
            f'<div class="detail-row"><span class="detail-key">{k}</span><span class="detail-val">{v}</span></div>'
            for k, v in campos
        )
        st.markdown(f'<div class="detail-card">{rows_html}</div>', unsafe_allow_html=True)
