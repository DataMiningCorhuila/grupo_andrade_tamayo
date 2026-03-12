import os
import sys
import base64
import requests as http_requests

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv
from db.database import SessionLocal
from db.models import Personaje, Episodio, Ubicacion

load_dotenv(os.path.join(BASE_DIR, '.env'))

IMAGE_BASE_URL = "https://cdn.thesimpsonsapi.com/500"
LOGO_PATH   = os.path.join(os.path.dirname(__file__), "img", "logo.webp")
HERO_PATH   = os.path.join(os.path.dirname(__file__), "img", "hero.webp")
CLOUDS_PATH = os.path.join(os.path.dirname(__file__), "img", "clouds-bg.jpg")
CSS_PATH    = os.path.join(os.path.dirname(__file__), "styles.css")

# ── Paleta de colores Simpsons ───────────────────────────────────────────────
SIMPSONS_COLORS = ["#FED90F", "#29ABE2", "#FF6B35", "#4CAF50", "#E91E63",
                   "#9C27B0", "#FF9800", "#00BCD4", "#8BC34A", "#F44336"]

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(255,255,255,0.90)",
    plot_bgcolor="rgba(255,255,255,0.70)",
    font=dict(family="Segoe UI, system-ui, sans-serif", color="#1A2E3B", size=13),
    title_font=dict(color="#1A2E3B", size=14),
    legend=dict(font=dict(color="#1A2E3B")),
    margin=dict(l=20, r=20, t=40, b=20),
    transition=dict(duration=500, easing="cubic-in-out"),
)

AXIS_STYLE = dict(tickfont=dict(color="#1A2E3B"), title_font=dict(color="#1A2E3B"), gridcolor="rgba(184,223,244,0.4)")


def load_css(path: str) -> None:
    with open(path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


st.set_page_config(
    page_title="The Simpsons — Explorer",
    page_icon="\U0001f369",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Fondo dinamico ───────────────────────────────────────────────────────────
_clouds_css = ""
if os.path.exists(CLOUDS_PATH):
    with open(CLOUDS_PATH, "rb") as _f:
        _clouds_b64 = base64.b64encode(_f.read()).decode()
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


# ═══════════════════════════════════════════════════════════════════════════════
# CARGA DE DATOS
# ═══════════════════════════════════════════════════════════════════════════════
@st.cache_data
def cargar_personajes():
    db = SessionLocal()
    try:
        personajes = db.query(Personaje).all()
        return pd.DataFrame([{
            'ID': p.id,
            'Nombre': p.name,
            'Edad': p.age,
            'Genero': p.gender,
            'Estado': p.status,
            'Ocupacion': p.occupation,
            'Fecha de nacimiento': p.birthdate,
            'Retrato': p.portrait_path,
            'Frases': p.phrases or [],
        } for p in personajes])
    finally:
        db.close()


@st.cache_data
def cargar_episodios():
    db = SessionLocal()
    try:
        episodios = db.query(Episodio).all()
        return pd.DataFrame([{
            'ID': e.id,
            'Nombre': e.name,
            'Temporada': e.season,
            'Episodio': e.episode_number,
            'Fecha': e.airdate,
            'Sinopsis': e.synopsis,
            'Imagen': e.image_path,
        } for e in episodios])
    finally:
        db.close()


@st.cache_data
def cargar_ubicaciones():
    db = SessionLocal()
    try:
        ubicaciones = db.query(Ubicacion).all()
        return pd.DataFrame([{
            'ID': u.id,
            'Nombre': u.name,
            'Imagen': u.image_path,
            'Ciudad': u.town,
            'Uso': u.use,
        } for u in ubicaciones])
    finally:
        db.close()


df_personajes = cargar_personajes()
df_episodios = cargar_episodios()
df_ubicaciones = cargar_ubicaciones()

# ═══════════════════════════════════════════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════════════════════════════════════════
hero_html = ""
if os.path.exists(HERO_PATH):
    with open(HERO_PATH, "rb") as f:
        hero_b64 = base64.b64encode(f.read()).decode()
    hero_html = f'<img src="data:image/webp;base64,{hero_b64}" alt="The Simpsons API"/>'

st.markdown(f"""
<div class="hero-block">
    <div class="hero-img">{hero_html}</div>
    <p class="hero-sub">Explora el universo de Springfield: personajes, episodios y ubicaciones</p>
    <p class="hero-authors">Juan Diego Andrade Cardozo &nbsp;&middot;&nbsp; Juan Carlos Tamayo Andrade</p>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# METRICAS
# ═══════════════════════════════════════════════════════════════════════════════
c1, c2, c3, c4, c5 = st.columns(5)
metrics = [
    ("Personajes",  len(df_personajes)),
    ("Episodios",   len(df_episodios)),
    ("Ubicaciones", len(df_ubicaciones)),
    ("Temporadas",  int(df_episodios['Temporada'].nunique()) if not df_episodios.empty else 0),
    ("Ciudades",    int(df_ubicaciones['Ciudad'].nunique()) if not df_ubicaciones.empty else 0),
]
for col, (label, value) in zip([c1, c2, c3, c4, c5], metrics):
    with col:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{value}</div>
            <div class="metric-label">{label}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown('<div class="section-sep"></div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TABS
# ═══════════════════════════════════════════════════════════════════════════════
tab_personajes, tab_episodios, tab_ubicaciones = st.tabs(
    ["\U0001f9d1 Personajes", "\U0001f4fa Episodios", "\U0001f3e0 Ubicaciones"]
)


# ─────────────────────────────────────────────────────────────────────────────
# TAB: PERSONAJES
# ─────────────────────────────────────────────────────────────────────────────
with tab_personajes:
    if df_personajes.empty:
        st.warning("No hay personajes en la base de datos. Ejecuta el extractor primero.")
    else:
        # Buscador
        st.markdown('<p class="section-label">Explorar personajes</p>', unsafe_allow_html=True)
        busqueda = st.text_input(
            label="busqueda",
            placeholder="Buscar por nombre u ocupacion...",
            label_visibility="collapsed",
            key="search_char"
        )

        df_filtrado = df_personajes.copy()
        if busqueda:
            mask = (
                df_personajes['Nombre'].str.contains(busqueda, case=False, na=False) |
                df_personajes['Ocupacion'].str.contains(busqueda, case=False, na=False)
            )
            df_filtrado = df_personajes[mask]

        st.markdown(
            f'<span class="results-badge">{len(df_filtrado)} resultado{"s" if len(df_filtrado) != 1 else ""}</span>',
            unsafe_allow_html=True
        )

        # Tabla
        cols_tabla = ['ID', 'Nombre', 'Genero', 'Edad', 'Ocupacion', 'Estado']
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

        # ── Detalle de personaje con graficos ───────────────────────────────
        st.markdown('<p class="section-label">Detalle de personaje</p>', unsafe_allow_html=True)

        nombres = df_filtrado['Nombre'].dropna().sort_values().tolist()
        if nombres:
            seleccionado = st.selectbox(
                label="personaje",
                options=nombres,
                label_visibility="collapsed",
                key="select_char"
            )
            fila = df_filtrado[df_filtrado['Nombre'] == seleccionado].iloc[0]

            # ── Portrait + Info ──
            col_img, col_info = st.columns([1, 2], gap="large")

            with col_img:
                if pd.notna(fila['Retrato']) and fila['Retrato']:
                    portrait_url = fila['Retrato']
                    if portrait_url.startswith('/'):
                        portrait_url = IMAGE_BASE_URL + portrait_url
                    try:
                        resp = http_requests.get(portrait_url, timeout=10)
                        resp.raise_for_status()
                        img_b64 = base64.b64encode(resp.content).decode()
                        st.markdown(f"""
                        <div class="portrait-wrap">
                            <img src="data:image/webp;base64,{img_b64}" alt="{seleccionado}"/>
                        </div>
                        """, unsafe_allow_html=True)
                    except Exception:
                        st.markdown('<div class="portrait-wrap"><p style="color:var(--muted)">Sin imagen</p></div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="portrait-wrap"><p style="color:var(--muted)">Sin imagen</p></div>', unsafe_allow_html=True)

            with col_info:
                # Status badge
                status = fila['Estado'] or "Desconocido"
                status_class = {
                    'Alive': 'status-alive',
                    'Deceased': 'status-deceased',
                }.get(status, 'status-unknown')
                status_label = {'Alive': 'Vivo', 'Deceased': 'Fallecido'}.get(status, status)

                campos = [
                    ("Nombre", fila['Nombre']),
                    ("Edad", f"{int(fila['Edad'])} anos" if pd.notna(fila['Edad']) else "—"),
                    ("Genero", fila['Genero'] or "—"),
                    ("Estado", f'<span class="status-badge {status_class}">{status_label}</span>'),
                    ("Ocupacion", fila['Ocupacion'] or "—"),
                    ("Nacimiento", fila['Fecha de nacimiento'] or "—"),
                ]
                rows_html = "".join(
                    f'<div class="detail-row"><span class="detail-key">{k}</span><span class="detail-val">{v}</span></div>'
                    for k, v in campos
                )
                st.markdown(f'<div class="detail-card">{rows_html}</div>', unsafe_allow_html=True)

            # ── Frases del personaje ──
            frases = fila['Frases'] if isinstance(fila['Frases'], list) else []
            if frases:
                st.markdown('<div class="section-sep"></div>', unsafe_allow_html=True)
                st.markdown('<p class="section-label">Frases celebres</p>', unsafe_allow_html=True)
                bubbles = "".join(f'<div class="phrase-bubble">&ldquo;{f}&rdquo;</div>' for f in frases)
                st.markdown(f'<div class="phrases-container">{bubbles}</div>', unsafe_allow_html=True)

            # ── Graficos interactivos ──
            st.markdown('<div class="section-sep"></div>', unsafe_allow_html=True)
            st.markdown('<p class="section-label">Analisis del personaje</p>', unsafe_allow_html=True)

            g1, g2 = st.columns(2)

            # --- Palabras mas usadas en frases del personaje ---
            with g1:
                frases_list = fila['Frases'] if isinstance(fila['Frases'], list) else []
                if frases_list:
                    import re
                    stop_words = {'the','a','an','is','are','was','were','be','been','being',
                                  'have','has','had','do','does','did','will','would','could',
                                  'should','may','might','shall','can','need','dare','ought',
                                  'i','me','my','you','your','he','him','his','she','her','it',
                                  'its','we','our','they','them','their','what','which','who',
                                  'this','that','these','those','am','to','of','in','for','on',
                                  'with','at','by','from','as','into','about','like','after',
                                  'between','out','against','during','without','before','above',
                                  'below','up','down','and','but','or','nor','not','so','very',
                                  'just','than','too','also','if','then','all','no','dont','im',
                                  'oh','get','got','go','going','thats','youre','well','let'}
                    all_words = ' '.join(frases_list).lower()
                    all_words = re.sub(r'[^a-z\s]', '', all_words)
                    words = [w for w in all_words.split() if w not in stop_words and len(w) > 2]
                    if words:
                        word_freq = pd.Series(words).value_counts().head(10).reset_index()
                        word_freq.columns = ['Palabra', 'Frecuencia']
                        word_freq = word_freq.sort_values('Frecuencia', ascending=True)
                        fig_words = go.Figure(go.Bar(
                            y=word_freq['Palabra'],
                            x=word_freq['Frecuencia'],
                            orientation='h',
                            marker=dict(
                                color=word_freq['Frecuencia'],
                                colorscale=[[0, '#C9EEFF'], [0.5, '#29ABE2'], [1, '#FED90F']],
                                line=dict(width=0),
                            ),
                            text=word_freq['Frecuencia'],
                            textposition='auto',
                            textfont=dict(color="#1A2E3B", size=11),
                        ))
                        fig_words.update_layout(
                            **PLOTLY_LAYOUT,
                            height=280,
                            title=dict(text="Palabras mas usadas en sus frases", font=dict(size=14)),
                            yaxis=dict(tickfont=dict(size=11, color="#1A2E3B"), title_font=dict(color="#1A2E3B"), gridcolor="rgba(184,223,244,0.4)"),
                            xaxis=dict(**AXIS_STYLE, showgrid=True, title="", dtick=1),
                        )
                        st.plotly_chart(fig_words, use_container_width=True)
                    else:
                        st.info("No se encontraron palabras significativas en las frases")
                else:
                    # Radar comparativo cuando no hay frases
                    df_tmp = df_personajes.copy()
                    df_tmp['Num_Frases'] = df_tmp['Frases'].apply(lambda x: len(x) if isinstance(x, list) else 0)
                    max_frases = max(df_tmp['Num_Frases'].max(), 1)
                    max_edad = max(df_tmp['Edad'].dropna().max(), 1)
                    occ_count = df_tmp['Ocupacion'].value_counts()
                    max_occ_peers = max(occ_count.max(), 1)

                    sel_frases = len(fila['Frases']) if isinstance(fila['Frases'], list) else 0
                    sel_edad = fila['Edad'] if pd.notna(fila['Edad']) else 0
                    sel_occ_peers = occ_count.get(fila['Ocupacion'], 0) if pd.notna(fila['Ocupacion']) else 0

                    cats = ['Frases', 'Edad', 'Colegas<br>(misma ocupacion)']
                    vals = [sel_frases/max_frases*100, sel_edad/max_edad*100, sel_occ_peers/max_occ_peers*100]
                    vals.append(vals[0])
                    cats.append(cats[0])

                    fig_radar = go.Figure(go.Scatterpolar(
                        r=vals, theta=cats, fill='toself',
                        fillcolor='rgba(254,217,15,0.25)',
                        line=dict(color='#FED90F', width=2),
                        marker=dict(color='#FED90F', size=6),
                    ))
                    fig_radar.update_layout(
                        **PLOTLY_LAYOUT,
                        height=280,
                        title=dict(text="Perfil comparativo", font=dict(size=14)),
                        polar=dict(
                            bgcolor='rgba(255,255,255,0.5)',
                            radialaxis=dict(visible=True, range=[0, 100], tickfont=dict(color="#1A2E3B", size=9)),
                            angularaxis=dict(tickfont=dict(color="#1A2E3B", size=11)),
                        ),
                    )
                    st.plotly_chart(fig_radar, use_container_width=True)

            # --- Distribucion de genero (donut) ---
            with g2:
                genero_counts = df_personajes['Genero'].dropna().value_counts().reset_index()
                genero_counts.columns = ['Genero', 'Cantidad']
                # Highlight del personaje seleccionado
                pull_vals = [0.1 if g == fila['Genero'] else 0 for g in genero_counts['Genero']]
                fig_gender = go.Figure(go.Pie(
                    labels=genero_counts['Genero'],
                    values=genero_counts['Cantidad'],
                    hole=0.5,
                    pull=pull_vals,
                    marker=dict(colors=SIMPSONS_COLORS[:len(genero_counts)]),
                    textinfo="label+percent",
                    textfont=dict(size=12),
                ))
                fig_gender.update_layout(
                    **PLOTLY_LAYOUT,
                    height=280,
                    title=dict(text="Distribucion por genero", font=dict(size=14)),
                    showlegend=False,
                )
                st.plotly_chart(fig_gender, use_container_width=True)

            g3, g4 = st.columns(2)

            # --- Top ocupaciones ---
            with g3:
                occ_counts = df_personajes['Ocupacion'].dropna().value_counts().head(15).reset_index()
                occ_counts.columns = ['Ocupacion', 'Cantidad']
                colors = ['#FED90F' if o == fila['Ocupacion'] else '#29ABE2' for o in occ_counts['Ocupacion']]
                fig_occ = go.Figure(go.Bar(
                    y=occ_counts['Ocupacion'],
                    x=occ_counts['Cantidad'],
                    orientation='h',
                    marker=dict(color=colors, line=dict(width=0)),
                    text=occ_counts['Cantidad'],
                    textposition='auto',
                ))
                fig_occ.update_layout(
                    **PLOTLY_LAYOUT,
                    height=420,
                    title=dict(text="Top 15 ocupaciones", font=dict(size=14)),
                    yaxis=dict(autorange="reversed", tickfont=dict(size=10, color="#1A2E3B"), title_font=dict(color="#1A2E3B"), gridcolor="rgba(184,223,244,0.4)"),
                    xaxis=dict(**AXIS_STYLE, showgrid=True),
                )
                st.plotly_chart(fig_occ, use_container_width=True)

            # --- Estado vivo/muerto ---
            with g4:
                status_counts = df_personajes['Estado'].dropna().value_counts().reset_index()
                status_counts.columns = ['Estado', 'Cantidad']
                pull_status = [0.1 if s == fila['Estado'] else 0 for s in status_counts['Estado']]
                color_map = {'Alive': '#4CAF50', 'Deceased': '#E91E63'}
                status_colors = [color_map.get(s, '#5E8DA6') for s in status_counts['Estado']]
                fig_status = go.Figure(go.Pie(
                    labels=status_counts['Estado'],
                    values=status_counts['Cantidad'],
                    hole=0.45,
                    pull=pull_status,
                    marker=dict(colors=status_colors),
                    textinfo="label+percent+value",
                    textfont=dict(size=11),
                ))
                fig_status.update_layout(
                    **PLOTLY_LAYOUT,
                    height=420,
                    title=dict(text="Estado de los personajes", font=dict(size=14)),
                    showlegend=False,
                )
                st.plotly_chart(fig_status, use_container_width=True)

            # --- Personajes con misma ocupacion ---
            if pd.notna(fila['Ocupacion']) and fila['Ocupacion']:
                misma_occ = df_personajes[
                    (df_personajes['Ocupacion'] == fila['Ocupacion']) &
                    (df_personajes['Nombre'] != seleccionado)
                ]['Nombre'].tolist()
                if misma_occ:
                    st.markdown('<div class="section-sep"></div>', unsafe_allow_html=True)
                    st.markdown(
                        f'<p class="section-label">Otros personajes con ocupacion: {fila["Ocupacion"]}</p>',
                        unsafe_allow_html=True
                    )
                    cards = "".join(f'<span class="same-occ-card">{n}</span>' for n in misma_occ[:20])
                    st.markdown(f'<div class="phrases-container">{cards}</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# TAB: EPISODIOS
# ─────────────────────────────────────────────────────────────────────────────
with tab_episodios:
    if df_episodios.empty:
        st.warning("No hay episodios en la base de datos. Ejecuta el extractor primero.")
    else:
        st.markdown('<p class="section-label">Analisis de episodios</p>', unsafe_allow_html=True)

        ge1, ge2 = st.columns(2)

        # --- Episodios por temporada ---
        with ge1:
            eps_per_season = df_episodios.groupby('Temporada').size().reset_index(name='Episodios')
            fig_eps = px.bar(
                eps_per_season, x='Temporada', y='Episodios',
                color='Episodios',
                color_continuous_scale=[[0, '#C9EEFF'], [0.5, '#29ABE2'], [1, '#FED90F']],
                text='Episodios',
            )
            fig_eps.update_layout(
                **PLOTLY_LAYOUT,
                height=380,
                title=dict(text="Episodios por temporada", font=dict(size=14)),
                xaxis=dict(**AXIS_STYLE, dtick=1, title=""),
                yaxis=dict(**AXIS_STYLE, title="", showgrid=True),
                coloraxis_showscale=False,
            )
            fig_eps.update_traces(textposition='outside')
            st.plotly_chart(fig_eps, use_container_width=True)

        # --- Timeline de temporadas por ano ---
        with ge2:
            df_ep_dates = df_episodios[df_episodios['Fecha'].notna()].copy()
            if not df_ep_dates.empty:
                df_ep_dates['Ano'] = pd.to_datetime(df_ep_dates['Fecha'], errors='coerce').dt.year
                eps_per_year = df_ep_dates.groupby('Ano').size().reset_index(name='Episodios')
                eps_per_year = eps_per_year.dropna()
                fig_timeline = px.area(
                    eps_per_year, x='Ano', y='Episodios',
                    color_discrete_sequence=['#29ABE2'],
                    line_shape='spline',
                )
                fig_timeline.update_layout(
                    **PLOTLY_LAYOUT,
                    height=380,
                    title=dict(text="Episodios por año de emision", font=dict(size=14)),
                    xaxis=dict(**AXIS_STYLE, title=""),
                    yaxis=dict(**AXIS_STYLE, title="", showgrid=True),
                )
                fig_timeline.update_traces(
                    fill='tozeroy',
                    fillcolor='rgba(41,171,226,0.15)',
                    line=dict(width=3),
                )
                st.plotly_chart(fig_timeline, use_container_width=True)

        st.markdown('<div class="section-sep"></div>', unsafe_allow_html=True)

        # --- Explorador de episodios ---
        st.markdown('<p class="section-label">Explorador de episodios</p>', unsafe_allow_html=True)

        temporadas = sorted(df_episodios['Temporada'].dropna().unique())
        temp_sel = st.selectbox("Temporada", temporadas, key="sel_season")

        df_ep_filt = df_episodios[df_episodios['Temporada'] == temp_sel]

        st.markdown(
            f'<span class="results-badge">{len(df_ep_filt)} episodio{"s" if len(df_ep_filt) != 1 else ""}</span>',
            unsafe_allow_html=True
        )

        for _, ep in df_ep_filt.iterrows():
            with st.container():
                ce1, ce2 = st.columns([1, 3])
                with ce1:
                    if pd.notna(ep['Imagen']) and ep['Imagen']:
                        img_url = ep['Imagen']
                        if img_url.startswith('/'):
                            img_url = IMAGE_BASE_URL + img_url
                        try:
                            resp = http_requests.get(img_url, timeout=10)
                            resp.raise_for_status()
                            ep_img_b64 = base64.b64encode(resp.content).decode()
                            st.markdown(f"""
                            <div class="portrait-wrap">
                                <img src="data:image/webp;base64,{ep_img_b64}" alt="{ep['Nombre']}" style="border-radius:8px;"/>
                            </div>
                            """, unsafe_allow_html=True)
                        except Exception:
                            st.markdown('<div class="portrait-wrap"><p style="color:var(--muted)">Sin imagen</p></div>', unsafe_allow_html=True)
                with ce2:
                    st.markdown(f"""
                    <div class="episode-card">
                        <div class="episode-title">S{int(ep['Temporada']):02d}E{int(ep['Episodio']):02d} — {ep['Nombre']}</div>
                        <div class="episode-meta">Fecha de emision: {ep['Fecha'] or 'Desconocida'}</div>
                        <div class="episode-synopsis">{ep['Sinopsis'] or 'Sin sinopsis disponible.'}</div>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown("", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# TAB: UBICACIONES
# ─────────────────────────────────────────────────────────────────────────────
with tab_ubicaciones:
    if df_ubicaciones.empty:
        st.warning("No hay ubicaciones en la base de datos. Ejecuta el extractor primero.")
    else:
        st.markdown('<p class="section-label">Analisis de ubicaciones</p>', unsafe_allow_html=True)

        gu1, gu2 = st.columns(2)

        # --- Treemap por uso y ciudad ---
        with gu1:
            df_tree = df_ubicaciones[df_ubicaciones['Uso'].notna() & df_ubicaciones['Ciudad'].notna()].copy()
            if not df_tree.empty:
                fig_tree = px.treemap(
                    df_tree, path=['Uso', 'Ciudad'], color='Uso',
                    color_discrete_sequence=SIMPSONS_COLORS,
                )
                fig_tree.update_layout(
                    **PLOTLY_LAYOUT,
                    height=420,
                    title=dict(text="Ubicaciones por tipo de uso", font=dict(size=14)),
                )
                fig_tree.update_traces(
                    textinfo="label+value",
                    hovertemplate="<b>%{label}</b><br>Cantidad: %{value}<extra></extra>",
                )
                st.plotly_chart(fig_tree, use_container_width=True)

        # --- Ubicaciones por ciudad ---
        with gu2:
            town_counts = df_ubicaciones['Ciudad'].dropna().value_counts().head(15).reset_index()
            town_counts.columns = ['Ciudad', 'Cantidad']
            fig_towns = go.Figure(go.Bar(
                y=town_counts['Ciudad'],
                x=town_counts['Cantidad'],
                orientation='h',
                marker=dict(
                    color=town_counts['Cantidad'],
                    colorscale=[[0, '#C9EEFF'], [0.5, '#29ABE2'], [1, '#FED90F']],
                    line=dict(width=0),
                ),
                text=town_counts['Cantidad'],
                textposition='auto',
            ))
            fig_towns.update_layout(
                **PLOTLY_LAYOUT,
                height=420,
                title=dict(text="Top 15 ciudades", font=dict(size=14)),
                yaxis=dict(autorange="reversed", tickfont=dict(size=10, color="#1A2E3B"), title_font=dict(color="#1A2E3B"), gridcolor="rgba(184,223,244,0.4)"),
                xaxis=dict(**AXIS_STYLE, showgrid=True),
            )
            st.plotly_chart(fig_towns, use_container_width=True)

        st.markdown('<div class="section-sep"></div>', unsafe_allow_html=True)

        # --- Explorador de ubicaciones ---
        st.markdown('<p class="section-label">Explorador de ubicaciones</p>', unsafe_allow_html=True)

        col_u1, col_u2 = st.columns(2)
        with col_u1:
            ciudades = ['Todas'] + sorted(df_ubicaciones['Ciudad'].dropna().unique().tolist())
            ciudad_sel = st.selectbox("Ciudad", ciudades, key="sel_city")
        with col_u2:
            usos = ['Todos'] + sorted(df_ubicaciones['Uso'].dropna().unique().tolist())
            uso_sel = st.selectbox("Tipo de uso", usos, key="sel_use")

        df_ub_filt = df_ubicaciones.copy()
        if ciudad_sel != 'Todas':
            df_ub_filt = df_ub_filt[df_ub_filt['Ciudad'] == ciudad_sel]
        if uso_sel != 'Todos':
            df_ub_filt = df_ub_filt[df_ub_filt['Uso'] == uso_sel]

        st.markdown(
            f'<span class="results-badge">{len(df_ub_filt)} ubicacion{"es" if len(df_ub_filt) != 1 else ""}</span>',
            unsafe_allow_html=True
        )

        # Grid de ubicaciones (4 columnas)
        cols_per_row = 4
        rows = [df_ub_filt.iloc[i:i+cols_per_row] for i in range(0, min(len(df_ub_filt), 40), cols_per_row)]
        for row_data in rows:
            cols = st.columns(cols_per_row)
            for idx, (_, ub) in enumerate(row_data.iterrows()):
                with cols[idx]:
                    img_html = ""
                    if pd.notna(ub['Imagen']) and ub['Imagen']:
                        ub_img_url = ub['Imagen']
                        if ub_img_url.startswith('/'):
                            ub_img_url = IMAGE_BASE_URL + ub_img_url
                        try:
                            resp = http_requests.get(ub_img_url, timeout=8)
                            resp.raise_for_status()
                            ub_img_b64 = base64.b64encode(resp.content).decode()
                            img_html = f'<img src="data:image/webp;base64,{ub_img_b64}" alt="{ub["Nombre"]}"/>'
                        except Exception:
                            img_html = '<div style="height:100px;display:flex;align-items:center;justify-content:center;color:var(--muted);font-size:0.75rem;">Sin imagen</div>'
                    else:
                        img_html = '<div style="height:100px;display:flex;align-items:center;justify-content:center;color:var(--muted);font-size:0.75rem;">Sin imagen</div>'

                    st.markdown(f"""
                    <div class="location-card">
                        {img_html}
                        <div class="location-name">{ub['Nombre']}</div>
                        <div class="location-meta">{ub['Ciudad'] or ''} &middot; {ub['Uso'] or ''}</div>
                    </div>
                    """, unsafe_allow_html=True)
