import streamlit as st
import folium
import pandas as pd
import plotly.express as px
from folium.plugins import MarkerCluster, HeatMap
from streamlit_folium import st_folium
import json
import os
from dotenv import load_dotenv
from openai import OpenAI
from supabase import create_client, Client

load_dotenv()
SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
# Configuración de Streamlit
st.set_page_config(page_title="GeoMed - Inteligencia Territorial", layout="wide", page_icon="🌍")

# Inyectar CSS Avanzado (UX/UI Premium B2B - Glassmorphism)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');
    
    html, body, [data-testid="stAppViewContainer"], [data-testid="stSidebar"] {
        font-family: 'Outfit', sans-serif;
        background-color: #FDFCF8 !important;
        color: #1B3B5A !important;
    }
    
    /* Forzar fondo claro en el Sidebar */
    [data-testid="stSidebar"] {
        background-color: #F3F4F6 !important;
        border-right: 1px solid #D1D5DB;
    }
    
    /* Fondo con gradiente sutil */
    .stApp {
        background: radial-gradient(circle at top right, #F3F4F6, #FDFCF8 80%);
    }

    /* Premium Light Cards */
    .metric-card {
        background: #FFFFFF !important;
        border: 1px solid #E5E7EB;
        padding: 1.5rem;
        border-radius: 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
        margin-bottom: 1.2rem;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    .metric-card-insights {
        background: #F0F9FF !important; /* Color azul suave informativo */
        width: 100%;
        max-width: 100%;
        box-sizing: border-box;
        border: 1px solid #BAE6FD !important;
        padding: 1rem;
        border-radius: 24px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
        margin-bottom: 1.2rem;
        margin-top: 4rem;
        text-align: center; /* Centrar contenido como solicitó el usuario */
        transition: all 0.4s ease;
        overflow: hidden;
        word-wrap: break-word;
    }
    .metric-card-insights:hover {
        background: #E0F2FE !important;
        transform: translateY(-2px);
    }
    .metric-card:hover {
        transform: translateY(-5px);
        border: 1px solid #1B3B5A;
        box-shadow: 0 10px 30px rgba(27, 59, 90, 0.1);
    }
    
    /* Forzar color en TODO el texto base */
    span, p, div, label, h1, h2, h3, h4, h5, h6 {
        color: #1B3B5A !important;
    }
    
    /* Ajustes específicos para st.metric */
    [data-testid="stMetricValue"] div {
        color: #1B3B5A !important;
        font-weight: 800 !important;
    }
    [data-testid="stMetricLabel"] div {
        color: #1B3B5A !important; /* Más oscuro para legibilidad */
        font-weight: 700 !important;
        opacity: 1 !important;
    }
    [data-testid="stMetricDelta"] {
        color: #4B6741 !important; /* Verde corporativo */
    }

    h1 { font-weight: 800 !important; letter-spacing: -1.5px !important; }
    
    /* Pestañas (Tabs) Estilizadas - Máximo Contraste */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background: #E5E7EB; /* Un poco más oscuro para separar del fondo */
        padding: 8px;
        border-radius: 16px;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        border-radius: 12px !important;
        color: #4B5563 !important; /* Gris oscuro para pestañas inactivas */
        padding: 10px 25px !important;
        border: 1px solid transparent !important;
        transition: 0.3s;
        font-weight: 600 !important;
    }
    .stTabs [aria-selected="true"] {
        background: #1B3B5A !important; /* Fondo Navy para la activa */
        color: #FFFFFF !important; /* Texto blanco para la activa */
        box-shadow: 0 4px 12px rgba(27, 59, 90, 0.2);
    }
    .stTabs [aria-selected="true"] p, .stTabs [aria-selected="true"] span {
        color: #FFFFFF !important; /* Forzar blanco en activa */
    }

    /* Botones Corporativos (Navy & Green) */
    .stButton>button {
        background: linear-gradient(90deg, #1B3B5A 0%, #4B6741 100%) !important;
        border: none !important;
        padding: 0.8rem 2rem !important;
        border-radius: 14px !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        box-shadow: 0 8px 20px rgba(27, 59, 90, 0.2) !important;
        transition: all 0.4s !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .stButton>button p {
        color: #FFFFFF !important;
    }
    .stButton>button:hover {
        box-shadow: 0 12px 30px rgba(27, 59, 90, 0.4) !important;
        transform: translateY(-2px);
    }

    /* Inputs y Selectores - Mejor Contraste */
    .stSelectbox div, .stMultiSelect div, .stTextInput div, .stTextArea div {
        color: #1B3B5A !important;
    }
    
    /* Placeholders legibles */
    ::placeholder {
        color: #6B7280 !important;
        opacity: 0.8 !important;
    }
    
    /* Scrollbars Custom */
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: #F3F4F6; }
    ::-webkit-scrollbar-thumb { background: #D1D5DB; border-radius: 10px; }
    ::-webkit-scrollbar-thumb:hover { background: #1B3B5A; }

    /* Fix para legibilidad general */
    * { line-height: 1.5; }
    
    /* Contenedor de IA con borde profesional */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: #FFFFFF !important;
        border-radius: 20px !important;
        border: 2px solid #1B3B5A !important; /* Más grueso y oscuro */
        box-shadow: 0 4px 20px rgba(27, 59, 90, 0.08) !important;
    }

    /* Forzar visibilidad en Sidebar Labels */
    [data-testid="stSidebar"] label {
        font-weight: 700 !important;
        font-size: 1.1rem !important;
        margin-bottom: 5px !important;
    }

    /* ===== HERO BANNER ===== */
    .hero-banner {
        background: linear-gradient(135deg, #1B3B5A 0%, #2D5F8A 50%, #4B6741 100%);
        border-radius: 24px;
        padding: 2.5rem 3rem;
        margin-bottom: 3rem;
        position: relative;
        overflow: hidden;
        margin-top: 3rem;
    }
    .hero-banner::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -20%;
        width: 400px;
        height: 400px;
        background: radial-gradient(circle, rgba(212,155,53,0.15) 0%, transparent 70%);
        border-radius: 50%;
    }
    .hero-banner h1, .hero-banner p, .hero-banner span {
        color: #FFFFFF !important;
    }
    .hero-banner .hero-sub {
        color: rgba(255,255,255,0.8) !important;
        font-size: 1.1rem;
    }

    /* ===== STAT TILES (Hero KPIs) ===== */
    .stat-tile {
        background: rgba(255,255,255,0.12);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.2);
        border-radius: 16px;
        padding: 1.2rem 1.5rem;
        text-align: center;
    }
    .stat-tile .stat-number {
        font-size: 1.8rem !important;
        font-weight: 800 !important;
        color: #D49B35 !important;
    }
    .stat-tile .stat-label {
        font-size: 0.85rem !important;
        color: rgba(255,255,255,0.85) !important;
        font-weight: 400 !important;
    }

    /* ===== KPI MINI CARDS ===== */
    .kpi-card {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 16px;
        padding: 1.2rem;
        text-align: center;
        box-shadow: 0 2px 10px rgba(0,0,0,0.04);
        transition: all 0.3s;
    }
    .kpi-card:hover { border-color: #D49B35; }
    .kpi-card .kpi-icon { font-size: 1.8rem; margin-bottom: 0.3rem; }
    .kpi-card .kpi-value {
        font-size: 1.4rem !important;
        font-weight: 800 !important;
        color: #1B3B5A !important;
    }
    .kpi-card .kpi-label {
        font-size: 0.8rem !important;
        color: #6B7280 !important;
        font-weight: 500 !important;
    }

    /* ===== SUGGESTION CHIPS ===== */
    .suggestion-chip {
        display: inline-block;
        background: #F3F4F6;
        border: 1px solid #E5E7EB;
        border-radius: 24px;
        padding: 0.5rem 1.2rem;
        margin: 0.3rem;
        margin-bottom: 1.2rem; /* Más espacio inferior */
        font-size: 0.85rem;
        color: #1B3B5A !important;
        cursor: pointer;
        transition: 0.2s;
    }
    .suggestion-chip:hover { background: #1B3B5A; color: #FFFFFF !important; border-color: #1B3B5A; }

    /* ===== SECTION HEADERS ===== */
    .section-header {
        display: flex;
        align-items: center;
        gap: 0.8rem;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #E5E7EB;
    }
    .section-header .section-icon {
        font-size: 1.5rem;
        background: linear-gradient(135deg, #1B3B5A, #4B6741);
        -webkit-background-clip: text;
        background-clip: text;
    }

    /* ===== SIDEBAR INFO CARD ===== */
    .sidebar-info {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 12px;
        padding: 1rem;
        margin-top: 1rem;
        font-size: 0.85rem;
    }

    /* ===== FOOTER HACK ===== */
    footer {visibility: hidden;}
    
    /* Espaciado de seguridad para que el contenido no pegue al footer */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 5rem !important;
        min-height: 100vh;
    }

    /* ===== FOOTER (Professional) ===== */
    .app-footer {
        width: 100%;
        text-align: center;
        padding: 3rem 1rem;
        margin-top: 6rem; /* Mayor despegue */
        border-top: 1px solid #E5E7EB;
        background: #FDFCF8;
        color: #9CA3AF !important;
        font-size: 0.85rem;
    }
    .app-footer span, .app-footer p { color: #9CA3AF !important; }

    /* ===== RESPONSIVE: Sidebar open adjustments ===== */
    /* Prevent fixed-width overflow in narrow containers */
    .metric-card, .metric-card-insights, .kpi-card {
        max-width: 100% !important;
        box-sizing: border-box !important;
    }

    /* When sidebar is open, the main content area shrinks */
    @media (max-width: 1200px) {
        .metric-card-insights {
            margin-top: 1.5rem;
            padding: 0.8rem;
        }
        .metric-card-insights ul {
            padding-left: 0.5rem !important;
            padding-right: 0.5rem !important;
        }
        .hero-banner {
            padding: 1.5rem 1.5rem;
        }
        .hero-banner h1 {
            font-size: 2rem !important;
        }
        .stat-tile .stat-number {
            font-size: 1.4rem !important;
        }
    }

    @media (max-width: 900px) {
        .metric-card-insights {
            margin-top: 1rem;
            padding: 0.6rem;
        }
        .hero-banner {
            padding: 1rem;
        }
        .hero-banner h1 {
            font-size: 1.6rem !important;
        }
    }

</style>
""", unsafe_allow_html=True)

api_key = os.getenv("OPENROUTER_API_KEY")

# Si no hay clave local, intentar buscar en los secretos de Streamlit (Cloud)
if not api_key:
    try:
        if "OPENROUTER_API_KEY" in st.secrets:
            api_key = st.secrets["OPENROUTER_API_KEY"]
    except Exception:
        api_key = None

# Configuración de OpenRouter (Estabilizado con Cache de Recursos)
@st.cache_resource
def get_ai_client(_api_key):
    if not _api_key:
        return None
    try:
        return OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=_api_key,
        )
    except Exception as e:
        st.error(f"Error inicializando OpenRouter: {e}")
        return None

client = get_ai_client(api_key)
# Lista de modelos para redundancia (Resiliencia en Hackathon)
MODELS = ["openrouter/free", "meta-llama/llama-3.3-70b-instruct:free", "google/gemma-3-12b-it:free"]
MODEL_NAME = MODELS[0]

        
# Función para generar contenido via OpenRouter con redundancia
def generate_ai_content(prompt, system_instruction):
    if not client: return "Error: Cliente AI no configurado."
    
    last_error = ""
    for model_id in MODELS:
        try:
            response = client.chat.completions.create(
                model=model_id,
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            last_error = str(e)
            if "429" in last_error:
                continue # Intentar con el siguiente modelo si hay rate limit
            return f"Error en generación: {last_error}"
            
    return f"Todos los modelos gratuitos están saturados. Intenta de nuevo en unos segundos. (Detalle: {last_error})"

if "messages" not in st.session_state: st.session_state.messages = []
if "radar_insight" not in st.session_state: st.session_state.radar_insight = None
if "last_sim" not in st.session_state: st.session_state.last_sim = None
if "current_user" not in st.session_state: st.session_state.current_user = None

@st.dialog("Acceso a GeoMed")
def show_auth_modal():
    t_login, t_register = st.tabs(["🔑 Iniciar Sesión", "📝 Crear Cuenta"])
    
    with t_login:
        st.markdown("<p style='font-size:0.9rem; color:#6B7280;'>Ingresa tus credenciales para acceder a tu cuenta.</p>", unsafe_allow_html=True)
        email = st.text_input("Correo Electrónico", key="login_email")
        password = st.text_input("Contraseña", type="password", key="login_pass")
        if st.button("Iniciar Sesión", use_container_width=True):
            try:
                response = supabase.auth.sign_in_with_password({"email": email, "password": password})
                user_name = response.user.user_metadata.get('name', email) if response.user else email
                st.session_state.current_user = user_name
                st.rerun()
            except Exception as e:
                err_msg = str(e)
                if "Email not confirmed" in err_msg:
                    st.error("Por favor, confirma tu correo electrónico antes de iniciar sesión.")
                elif "Invalid login credentials" in err_msg:
                    st.error("Credenciales incorrectas.")
                else:
                    st.error(f"Error al iniciar sesión: {err_msg}")
                
    with t_register:
        st.markdown("<p style='font-size:0.9rem; color:#6B7280;'>Únete a GeoMed Intelligence para guardar tus análisis.</p>", unsafe_allow_html=True)
        new_name = st.text_input("Nombre Completo", key="reg_name")
        new_email = st.text_input("Correo Electrónico", key="reg_email")
        new_password = st.text_input("Contraseña", type="password", key="reg_pass")
        if st.button("Crear Cuenta", use_container_width=True, key="btn_register"):
            if not new_email or not new_password or not new_name:
                st.warning("Por favor, llena todos los campos.")
            else:
                try:
                    response = supabase.auth.sign_up({
                        "email": new_email, 
                        "password": new_password,
                        "options": {
                            "data": {
                                "name": new_name
                            }
                        }
                    })
                    st.success("Cuenta creada exitosamente. Revisa tu correo (si aplica) o intenta iniciar sesión.")
                except Exception as e:
                    err_msg = str(e)
                    if "User already registered" in err_msg:
                        st.error("El correo ya está registrado.")
                    else:
                        st.error(f"Error al registrar cuenta: {err_msg}")


# --- CARGAS DE DATOS (REPROYECTADOS WGS84) ---
@st.cache_data
def load_comunas():
    path = "data/wgs84_limite_catastral_de_comun_simple.geojson"
    if not os.path.exists(path): return None
    with open(path, "r", encoding="utf-8") as f: return json.load(f)

@st.cache_data
def load_barrios():
    path = "data/wgs84_limite_barrio_vereda_cata_simple.geojson"
    if not os.path.exists(path): return None
    with open(path, "r", encoding="utf-8") as f: return json.load(f)

# Cargar POIs (Establecimientos) - Optimizado con Parquet (443k registros en milisegundos)
@st.cache_data
def load_poi_database():
    path = "data/pois.parquet"
    if not os.path.exists(path): return pd.DataFrame(columns=['lat', 'lon', 'nombre', 'comuna', 'sector'])
    return pd.read_parquet(path)

# Cargar GeoJSON de Metro (Local Reproyectado)
@st.cache_data
def load_metro_geojson():
    path = "data/wgs84_Estaciones_Sistema_Metro_reconciled.geojson"
    if not os.path.exists(path): return None
    with open(path, "r", encoding="utf-8") as f: return json.load(f)

# Cargar Atractivos Turísticos
@st.cache_data
def load_attractions():
    path = "data/wgs84_atractivos_turisticos.geojson"
    if not os.path.exists(path): return None
    with open(path, "r", encoding="utf-8") as f: return json.load(f)

# Cargar Puntos Info Turística
@st.cache_data
def load_tur_info():
    path = "data/wgs84_puntos_de_informacion_tur.geojson"
    if not os.path.exists(path): return None
    with open(path, "r", encoding="utf-8") as f: return json.load(f)

# Cargar Población
@st.cache_data
def load_poblacion():
    path = "data/poblacion_comunas.json"
    if not os.path.exists(path): return {}
    with open(path, "r", encoding="utf-8") as f: return json.load(f)

# Cargar Estratos (Preprocesado)
@st.cache_data
def load_estratos():
    path = "data/estratos_resumen.json"
    if not os.path.exists(path): return {}
    with open(path, "r", encoding="utf-8") as f: return json.load(f)

def filter_df_by_comuna(df, comuna_id):
    if not isinstance(df, pd.DataFrame) or df.empty or not comuna_id:
        return pd.DataFrame(columns=['lat', 'lon', 'nombre', 'comuna', 'sector'])
    
    target_id = str(comuna_id).strip().lstrip('0')
    if target_id == "": target_id = "0"
    
    mask = df['comuna'].astype(str).str.strip().str.lstrip('0') == target_id
    return df[mask].copy()

def filter_geojson_by_comuna(features, comuna_id):
    if not features or not comuna_id:
        return []
    
    target_id = str(comuna_id).strip().lstrip('0')
    if target_id == "": target_id = "0"
    
    filtered = []
    for f in features:
        props = f.get('properties', {})
        val = props.get('comuna', props.get('cod_comuna', props.get('comuna_corregimiento', '')))
        cid = str(val).strip().lstrip('0')
        if cid == target_id:
            filtered.append(f)
    return filtered

# --- LÓGICA DE ANALYTICS (Optimizado con Pandas) ---

# Mapa de códigos a nombres reales (Basado en el sistema de Industria y Comercio de Medellín)
SECTOR_MAP = {
    "01": "Industrial 🏗️",
    "02": "Comercial 🛍️",
    "03": "Servicios 🛠️",
    "04": "Otras Actividades 📋",
    "05": "Construcción 🏗️"
}

# Mapa de categorías a sectores amigables para el filtro
def get_macro_sectores(df):
    if not isinstance(df, pd.DataFrame) or df.empty or 'sector' not in df.columns: return []
    # Filtrar valores None o vacíos
    raw_sectors = [str(s) for s in df['sector'].unique() if s is not None and str(s).strip() != "" and str(s).lower() != 'none']
    # Mapear a nombres reales
    named_sectors = sorted([SECTOR_MAP.get(s, f"Sector {s}") for s in raw_sectors])
    return named_sectors

def get_comuna_stats(df_comuna):
    if not isinstance(df_comuna, pd.DataFrame) or df_comuna.empty:
        return {
            "total": 0, 
            "top_cat": "N/A", 
            "dist": {}, 
            "chart_data": pd.DataFrame(columns=['Sector', 'Cantidad']),
            "df": df_comuna
        }
    
    # Aplicar mapeo a la columna de sector para visualización
    df_viz = df_comuna.copy()
    # Filtrar registros sin sector válido antes de mapear
    df_viz = df_viz[df_viz['sector'].notna()]
    df_viz = df_viz[df_viz['sector'].astype(str).str.strip().ne('')]
    df_viz = df_viz[df_viz['sector'].astype(str).str.lower() != 'none']
    df_viz['sector_nombre'] = df_viz['sector'].map(lambda x: SECTOR_MAP.get(str(x).strip(), f"Sector {x}"))
    # Remover cualquier sector_nombre que sea genérico vacío
    df_viz = df_viz[~df_viz['sector_nombre'].isin(['Sector ', 'Sector None', 'Sector nan'])]
    
    total = len(df_comuna)  # Total original incluyendo sin sector
    top_cat = df_viz['sector_nombre'].mode().iloc[0] if not df_viz.empty else "N/A"
    
    # Preparar DataFrame para gráficos
    counts = df_viz['sector_nombre'].value_counts().head(10).reset_index()
    counts.columns = ['Sector', 'Cantidad']
    
    return {
        "total": total,
        "top_cat": top_cat,
        "dist": counts.set_index('Sector')['Cantidad'].to_dict(),
        "chart_data": counts,
        "df": df_viz
    }

# --- MOTOR DE INTELIGENCIA (Enriquecimiento de Contexto) ---
def prepare_market_snapshot(comuna_id, cnombres, poi_df, metro_data, attraction_data):
    """
    Genera un resumen estructurado para el LLM con el máximo potencial de datos.
    """
    # 1. Mix Económico
    stats = get_comuna_stats(poi_df)
    mix_text = ""
    if not stats['chart_data'].empty:
        total = stats['total']
        mix_text = "\n".join([f"- {r['Sector']}: {r['Cantidad']} ({round(r['Cantidad']/total*100, 1)}%)" for _, r in stats['chart_data'].iterrows()])
    
    # 2. ADN Comercial (Muestra de nombres para inferir 'vibe')
    vibe_sample = []
    if not poi_df.empty:
        vibe_sample = poi_df['nombre'].sample(min(len(poi_df), 15)).tolist()
    
    # 3. Infraestructura
    metro_list = []
    if metro_data:
        m_filtered = filter_geojson_by_comuna(metro_data['features'], comuna_id)
        metro_list = [f"{f['properties'].get('label')} (Línea {f['properties'].get('linea')})" for f in m_filtered]
    
    # 4. Turismo
    att_list = []
    if attraction_data:
        a_filtered = filter_geojson_by_comuna(attraction_data['features'], comuna_id)
        att_list = [f"{f['properties'].get('nombre_sitio')} ({f['properties'].get('tipo_atractivo')})" for f in a_filtered]

    # 5. Demografía y Socioeconomía
    poblacion = 0
    estrato = "N/A"
    try:
        pob_data = load_poblacion()
        est_data = load_estratos()
        if str(comuna_id) in pob_data:
            poblacion = pob_data[str(comuna_id)].get("poblacion", 0)
        if str(comuna_id) in est_data:
            estrato = est_data[str(comuna_id)].get("estrato_predominante", "N/A")
    except Exception:
        pass

    snapshot = {
        "ubicacion": {
            "comuna_id": comuna_id,
            "nombre": cnombres.get(comuna_id, "Desconocida"),
            "poblacion_habitantes": poblacion,
            "estrato_predominante": estrato
        },
        "indicadores_mercado": {
            "total_establecimientos": stats['total'],
            "mix_economico_distribucion": mix_text,
            "muestra_adn_comercial": vibe_sample
        },
        "infraestructura_y_turismo": {
            "estaciones_metro_cercanas": metro_list,
            "atractivos_turisticos": att_list
        }
    }
    return snapshot

# --- UI PRINCIPAL ---
def main():
    # Cargar datos base (ANTES del hero para usar stats)
    geojson_comunas = load_comunas()
    all_pois_df = load_poi_database()
    all_barrios = load_barrios()
    metro_data = load_metro_geojson()
    attraction_data = load_attractions()
    tur_info_data = load_tur_info()
    poblacion_data = load_poblacion()
    estratos_data = load_estratos()

    # Calcular estadísticas globales para el hero
    total_pois = len(all_pois_df) if isinstance(all_pois_df, pd.DataFrame) else 0
    total_comunas = len(geojson_comunas['features']) if geojson_comunas else 0
    total_metro = len(metro_data['features']) if metro_data else 0
    total_atractivos = len(attraction_data['features']) if attraction_data else 0

    # ===== HERO BANNER =====
    st.markdown(f"""
    <div class='hero-banner'>
        <h1 style='font-size:2.8rem; margin-bottom:0.3rem;'>🌍 GeoMed Intelligence</h1>
        <p class='hero-sub'>Plataforma de Geointeligencia y Analítica Territorial para el Ecosistema Empresarial de Medellín</p>
        <div style='display:flex; gap:1rem; margin-top:1.5rem; flex-wrap:wrap;'>
            <div class='stat-tile'>
                <div class='stat-number'>{total_pois:,}</div>
                <div class='stat-label'>Establecimientos Indexados</div>
            </div>
            <div class='stat-tile'>
                <div class='stat-number'>{total_comunas}</div>
                <div class='stat-label'>Comunas Mapeadas</div>
            </div>
            <div class='stat-tile'>
                <div class='stat-number'>{total_metro}</div>
                <div class='stat-label'>Estaciones de Metro</div>
            </div>
            <div class='stat-tile'>
                <div class='stat-number'>{sum([v.get('poblacion', 0) for v in poblacion_data.values()]):,}</div>
                <div class='stat-label'>Población Total</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar / Panel de Control
    if 'comuna_id' not in st.session_state: st.session_state.comuna_id = "10"
    
    comunas_lista = []
    cnombres = {}
    if geojson_comunas:
        for f in geojson_comunas['features']:
            props = f['properties']
            cid, cnom = str(props.get('comuna','')), props.get('nombre','...').title()
            comunas_lista.append({"id": cid, "nombre": cnom})
            cnombres[cid] = cnom
        comunas_lista = sorted(comunas_lista, key=lambda x: int(x['id']) if x['id'].isdigit() else 99)

    with st.sidebar:


        st.markdown("## ⚙️ Panel de Control")
        opciones = [c['id'] for c in comunas_lista]
        idx = opciones.index(st.session_state.comuna_id) if st.session_state.comuna_id in opciones else 0
        st.session_state.comuna_id = st.selectbox("Seleccione Comuna:", opciones, format_func=lambda x: f"C{x} - {cnombres.get(x, '')}", index=idx)
        
        # Filtro de Sectores
        all_sectors = get_macro_sectores(all_pois_df)
        selected_sectors = st.multiselect("Filtrar Sectores (POI):", all_sectors, help="Filtra los datos del mapa y analítica por categoría")
        
        if st.button("🧹 Limpiar Filtros", use_container_width=True):
            st.session_state.comuna_id = "10"
            st.rerun()     

        st.divider()

        # Fuentes de Datos
        st.markdown("### 📁 Fuentes de Datos")
        st.markdown("""
        <div class='sidebar-info'>
            <b>🏛️ Alcaldía de Medellín</b><br>
            Datos abiertos georreferenciados<br><br>
            <b>🚇 Metro de Medellín</b><br>
            Estaciones y líneas<br><br>
            <b>🤖 IA Generativa</b><br>
            OpenRouter (LLMs gratuitos)
        </div>
        """, unsafe_allow_html=True)

        st.divider()
        # --- AUTENTICACIÓN ---
        if st.session_state.current_user:
            st.markdown(f"**👤 Hola, {st.session_state.current_user}**")
            if st.button("🚪 Cerrar Sesión", use_container_width=True):
                st.session_state.current_user = None
                st.rerun()
        else:
            if st.button("🔑 Iniciar Sesión", use_container_width=True, type="primary"):
                show_auth_modal()

    # Filtrar datos de la comuna seleccionada (ULTRA RÁPIDO con Pandas)
    poi_comuna = filter_df_by_comuna(all_pois_df, st.session_state.comuna_id)
    
    # Si hay filtros de sector activados, revertir nombres a códigos para filtrar
    if selected_sectors and not poi_comuna.empty and 'sector' in poi_comuna.columns:
        REVERSE_MAP = {v: k for k, v in SECTOR_MAP.items()}
        selected_codes = [REVERSE_MAP.get(s, s) for s in selected_sectors]
        poi_comuna = poi_comuna[poi_comuna['sector'].isin(selected_codes)]
    
    # Verificar si el DataFrame resultante está vacío y loguear para debug visual
    if poi_comuna.empty and st.session_state.comuna_id and selected_sectors:
        st.sidebar.warning(f"⚠️ No hay comercios de '{', '.join(selected_sectors)}' en C{st.session_state.comuna_id}.")
        
    stats = get_comuna_stats(poi_comuna)

    # Tabs Principal (Expansión para Hackathon)
    tab1, tab2, tab3, tab4 = st.tabs(["🗺️ Radar Territorial", "📊 Análisis BI", "🧪 Simulador Éxito", "💡 Consultoría IA"])
    # TAB 1: RADAR (MAPA)
    # --------------------------
    with tab1:
        # 1. Mapa Base (Ancho completo)
        # Crear mapa base con Estilo Claro (Esri World Light Gray)
        m = folium.Map(location=[6.2442, -75.5812], zoom_start=12, tiles=None, max_zoom=20)
        folium.TileLayer(
            tiles="https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}",
            attr="Esri",
            name="⚪ Medellín Analítico (Claro)",
            max_zoom=20,
            max_native_zoom=16,
            overlay=False,
            control=True
        ).add_to(m)
        
        # Capas del Mapa
        if geojson_comunas:
            folium.GeoJson(
                geojson_comunas, 
                name="🚩 Comunas de Medellín",
                style_function=lambda x: {'fillColor': '#01FF84', 'color': '#01FF84', 'weight': 1, 'fillOpacity': 0.05}, 
                highlight_function=lambda x: {'weight': 3, 'color': '#FFFFFF', 'fillOpacity': 0.2}, 
                tooltip=folium.GeoJsonTooltip(fields=['nombre','comuna'], aliases=['Comuna:','Cod:'])
            ).add_to(m)
        
        if st.session_state.comuna_id:
            if all_barrios:
                barrios_comuna = filter_geojson_by_comuna(all_barrios['features'], st.session_state.comuna_id)
                if barrios_comuna:
                    folium.GeoJson(
                        {"type":"FeatureCollection","features":barrios_comuna}, 
                        name="🏘️ Barrios Locales",
                        style_function=lambda x: {'color':'#FBBF24', 'weight':1, 'dashArray':'5,5', 'fillOpacity':0}, 
                        tooltip=folium.GeoJsonTooltip(fields=['nombre_barrio'], aliases=['Barrio-Vereda:'])
                    ).add_to(m)
            
            if not poi_comuna.empty:
                fg_pois = folium.FeatureGroup(name="🏪 Establecimientos (POIs)")
                cluster = MarkerCluster().add_to(fg_pois)
                df_map = poi_comuna.head(500)
                for _, row in df_map.iterrows():
                    folium.CircleMarker(location=[row['lat'], row['lon']], radius=3, color="#1B3B5A", fill=True, tooltip=f"<b>{row['nombre']}</b>").add_to(cluster)
                fg_pois.add_to(m)
                
                heat_data = poi_comuna[['lat', 'lon']].values.tolist()
                HeatMap(heat_data, name="🔥 Heatmap de Saturación", radius=15, blur=10, min_opacity=0.3).add_to(m)

        if metro_data:
            folium.GeoJson(
                metro_data,
                name="🚇 Estaciones de Metro",
                marker=folium.CircleMarker(radius=7, color='#FF1493', fill=True, fillOpacity=1, fill_color='#FFFFFF', weight=2),
                tooltip=folium.GeoJsonTooltip(fields=['label', 'linea'], aliases=['🚇 Estación:', 'Línea:'])
            ).add_to(m)

        if attraction_data:
            atr_filtrados = filter_geojson_by_comuna(attraction_data['features'], st.session_state.comuna_id) if st.session_state.comuna_id else attraction_data['features']
            if atr_filtrados:
                folium.GeoJson(
                    {"type":"FeatureCollection","features":atr_filtrados},
                    name="🌟 Atractivos Turísticos",
                    marker=folium.Marker(icon=folium.Icon(color='orange', icon='star')),
                    tooltip=folium.GeoJsonTooltip(fields=['nombre_sitio', 'tipo_atractivo'], aliases=['🌟 Atractivo:', 'Tipo:'])
                ).add_to(m)

        if tur_info_data:
            folium.GeoJson(
                tur_info_data,
                name="ℹ️ Info Turística",
                show=False,
                marker=folium.Marker(icon=folium.Icon(color='blue', icon='info-sign')),
                tooltip=folium.GeoJsonTooltip(fields=['sitio', 'direccion'], aliases=['ℹ️ Punto Info:', 'Dir:'])
            ).add_to(m)
        
        folium.LayerControl(collapsed=True, position='topright').add_to(m)
            
        map_event = st_folium(
            m, 
            width="100%", 
            height=550, 
            key="radar_medellin_v3", 
            returned_objects=["last_active_drawing"]
        )
        
        if map_event and map_event.get("last_active_drawing"):
            new_cid = str(map_event["last_active_drawing"]["properties"].get("comuna")).strip()
            if new_cid != st.session_state.comuna_id:
                st.session_state.comuna_id = new_cid
                st.rerun()

        # 2. KPI Row (Mini-cards below map)
        st.divider()
        metro_cercano = filter_geojson_by_comuna(metro_data['features'], st.session_state.comuna_id) if metro_data else []
        atr_cercanos = filter_geojson_by_comuna(attraction_data['features'], st.session_state.comuna_id) if attraction_data else []
        barrios_count = len(filter_geojson_by_comuna(all_barrios['features'], st.session_state.comuna_id)) if all_barrios else 0
        
        kc1, kc2, kc3, kc4, kc5 = st.columns(5)
        with kc1:
            st.markdown(f"""<div class='kpi-card'>
                <div class='kpi-icon'>🏪</div>
                <div class='kpi-value'>{len(poi_comuna):,}</div>
                <div class='kpi-label'>Comercios</div>
            </div>""", unsafe_allow_html=True)
        with kc2:
            st.markdown(f"""<div class='kpi-card'>
                <div class='kpi-icon'>🏘️</div>
                <div class='kpi-value'>{barrios_count}</div>
                <div class='kpi-label'>Barrios</div>
            </div>""", unsafe_allow_html=True)
        with kc3:
            st.markdown(f"""<div class='kpi-card'>
                <div class='kpi-icon'>🚇</div>
                <div class='kpi-value'>{len(metro_cercano)}</div>
                <div class='kpi-label'>Est. Metro</div>
            </div>""", unsafe_allow_html=True)
        with kc4:
            st.markdown(f"""<div class='kpi-card'>
                <div class='kpi-icon'>⭐</div>
                <div class='kpi-value'>{len(atr_cercanos)}</div>
                <div class='kpi-label'>Atractivos</div>
            </div>""", unsafe_allow_html=True)
        with kc5:
            n_sectors = len(get_macro_sectores(poi_comuna))
            st.markdown(f"""<div class='kpi-card'>
                <div class='kpi-icon'>📊</div>
                <div class='kpi-value'>{n_sectors}</div>
                <div class='kpi-label'>Sectores</div>
            </div>""", unsafe_allow_html=True)

        # 3. Panel Inferior (3 columnas: Contexto, Infraestructura, IA)
        st.markdown("")
        col_info, col_infra, col_ai = st.columns([1.2, 1.2, 1.8])
        
        with col_info:
            st.markdown("### 📍 Entorno Local")
            if st.session_state.comuna_id:
                cid_str = str(st.session_state.comuna_id)
                poblacion_local = poblacion_data.get(cid_str, {}).get("poblacion", "N/A")
                if isinstance(poblacion_local, int): poblacion_local = f"{poblacion_local:,}"
                estrato_local = estratos_data.get(cid_str, {}).get("estrato_predominante", "N/A")
                
                st.markdown(f"""<div class='metric-card'>
                    <b style='font-size:1.2rem;'>Comuna {st.session_state.comuna_id}</b><br>
                    <span style='color:#6B7280 !important;'>{cnombres.get(st.session_state.comuna_id, '')}</span><br><br>
                    <span style='font-size:0.85rem; color:#4B6741 !important;'>Sector dominante:</span><br>
                    <b>{stats['top_cat'][:25] if stats['top_cat'] != 'N/A' else 'Sin datos'}</b><br><br>
                    <span style='font-size:0.85rem; color:#4B6741 !important;'>Población:</span> <b>{poblacion_local}</b> hab.<br>
                    <span style='font-size:0.85rem; color:#4B6741 !important;'>Estrato predominante:</span> <b>{estrato_local}</b>
                </div>""", unsafe_allow_html=True)
                st.info("💡 Haz clic en una comuna del mapa para cambiar el contexto.")
        
        with col_infra:
            st.markdown("""
            <div class='metric-card-insights'>
                <p style='font-size:0.95rem; font-weight:600; margin-bottom:0.5rem;'>¿Qué hace este motor?</p>
                <p style='font-size:0.85rem; line-height:1.4; color:#4B5563;'>
                    Cruza variables críticas en tiempo real:
                </p>
                <ul style='font-size:0.8rem; list-style-type: none; color:#6B7280; padding-left:0; padding-right:1rem;'>
                    <li>📍 Proximidad a estaciones de <b>Metro</b>.</li>
                    <li>🎭 Puntos de <b>interés turístico</b></li>
                    <li>🏪 Densidad de <b>comercios actuales</b>.</li>
                </ul>
                <p style='font-size:0.8rem; font-style:italic; border-top:1px solid #F3F4F6; padding-top:0.5rem; margin-top:0.5rem;'>
                    Identifica "huecos de mercado" para sugerir modelos de negocio con alta probabilidad de éxito.
                </p>
            </div>
            """, unsafe_allow_html=True)
        with col_ai:
            if st.session_state.comuna_id:
                st.markdown("### 🤖 Inteligencia Territorial")
                btn_placeholder = st.empty()
                if btn_placeholder.button("🚀 Generar Insights Estratégicos", use_container_width=True):
                    btn_placeholder.button("⏳ Analizando micro-entorno con IA...", disabled=True, use_container_width=True)
                    inf_cercanos = filter_geojson_by_comuna(tur_info_data['features'], st.session_state.comuna_id) if tur_info_data else []
                    
                    extra = {
                        "metro": [m_item['properties'].get('label') for m_item in metro_cercano],
                        "atractivos_turisticos": [a['properties'].get('nombre_sitio') for a in atr_cercanos],
                        "puntos_info": [i['properties'].get('sitio') for i in inf_cercanos],
                        "conteo_comercios_actuales": len(poi_comuna) if not poi_comuna.empty else 0
                    }
                    try:
                        with st.spinner("Procesando Inteligencia Territorial..."):
                            snapshot = prepare_market_snapshot(st.session_state.comuna_id, cnombres, poi_comuna, metro_data, attraction_data)
                            
                            SYSTEM_INSTRUCTION_RADAR = (
                                "Eres un Analista Senior de Desarrollo Económico y Estrategia Territorial en Medellín. "
                                "Tu objetivo es detectar 'Oportunidades de Oro' y 'Nichos Desatendidos' basándote en datos duros. \n\n"
                                "REGLAS DE ANÁLISIS:\n"
                                "1. Analiza el 'Mix Económico': Si un sector domina >50%, advierte sobre saturación. Si un sector es <5%, evalúa si es una oportunidad.\n"
                                "2. Cruza con Infraestructura: La cercanía al Metro aumenta el valor de negocios de conveniencia y servicios rápidos.\n"
                                "3. Vibe Check: Usa la 'Muestra ADN' (nombres de negocios) para entender si la zona es popular, industrial o premium.\n\n"
                                "ENTREGA: 3 Ideas de negocio altamente específicas para esta comuna. Justifica cada una con un dato del contexto enviado."
                            )
                            
                            user_prompt = f"<SNAPSHOT_TERRITORIAL>\n{json.dumps(snapshot, indent=2)}\n</SNAPSHOT_TERRITORIAL>\n\nGenera el análisis estratégico."
                            res = generate_ai_content(user_prompt, SYSTEM_INSTRUCTION_RADAR)
                            st.session_state.radar_insight = res
                            st.rerun()
                    except Exception as e:
                        st.warning("🏮 El motor analítico está saturado. Por favor, reintenta en unos segundos.")
                        btn_placeholder.button("🚀 Generar Insights Estratégicos", use_container_width=True, key="btn_radar_error")
                
                if st.session_state.radar_insight:
                    with st.container(height=300, border=True):
                        st.markdown(st.session_state.radar_insight)
                else:
                    st.markdown("""<div class='metric-card' style='text-align:center; padding:2rem;'>
                        <p style='font-size:2rem;'>🧠</p>
                        <p><b>Motor de Análisis Territorial</b></p>
                        <p style='color:#6B7280 !important; font-size:0.9rem;'>Presiona el botón para generar insights estratégicos basados en IA sobre esta comuna.</p>
                    </div>""", unsafe_allow_html=True)

    # --------------------------
    # TAB 2: ANALYTICS BI
    # --------------------------
    with tab2:
        if not st.session_state.comuna_id:
            st.warning("Seleccione una comuna en el Radar para ver las estadísticas.")
        elif stats:
            st.markdown(f"### 📊 Dashboard de Inteligencia — Comuna {st.session_state.comuna_id} · {cnombres.get(st.session_state.comuna_id, '')}")
            
            # 4 KPI Cards -> Change to 6 to fit Demographic data
            k1, k2, k3, k4, k5, k6 = st.columns(6)
            with k1:
                st.markdown(f"""<div class='kpi-card'>
                    <div class='kpi-icon'>🏪</div>
                    <div class='kpi-value' style='font-size:1.2rem !important;'>{stats['total']:,}</div>
                    <div class='kpi-label'>Comercios</div>
                </div>""", unsafe_allow_html=True)
            with k2:
                top_display = stats['top_cat'][:18] if stats['top_cat'] != 'N/A' else 'N/A'
                st.markdown(f"""<div class='kpi-card'>
                    <div class='kpi-icon'>🏆</div>
                    <div class='kpi-value' style='font-size:1rem !important;'>{top_display}</div>
                    <div class='kpi-label'>Sector Dominante</div>
                </div>""", unsafe_allow_html=True)
            with k3:
                n_sect = len(stats['dist'])
                st.markdown(f"""<div class='kpi-card'>
                    <div class='kpi-icon'>📂</div>
                    <div class='kpi-value' style='font-size:1.2rem !important;'>{n_sect}</div>
                    <div class='kpi-label'>Categorías</div>
                </div>""", unsafe_allow_html=True)
            with k4:
                density = round(stats['total'] / max(len(filter_geojson_by_comuna(all_barrios['features'], st.session_state.comuna_id)) if all_barrios else 1, 1))
                st.markdown(f"""<div class='kpi-card'>
                    <div class='kpi-icon'>📈</div>
                    <div class='kpi-value' style='font-size:1.2rem !important;'>{density:,}</div>
                    <div class='kpi-label'>Com./Barrio</div>
                </div>""", unsafe_allow_html=True)
            with k5:
                pob = poblacion_data.get(str(st.session_state.comuna_id), {}).get("poblacion", 0)
                st.markdown(f"""<div class='kpi-card'>
                    <div class='kpi-icon'>👥</div>
                    <div class='kpi-value' style='font-size:1.2rem !important;'>{pob:,}</div>
                    <div class='kpi-label'>Población</div>
                </div>""", unsafe_allow_html=True)
            with k6:
                est = estratos_data.get(str(st.session_state.comuna_id), {}).get("estrato_predominante", "N/A")
                st.markdown(f"""<div class='kpi-card'>
                    <div class='kpi-icon'>🏠</div>
                    <div class='kpi-value' style='font-size:1.2rem !important;'>{est}</div>
                    <div class='kpi-label'>Estrato</div>
                </div>""", unsafe_allow_html=True)
            
            st.divider()
            
            # Charts Row
            c_left, c_right = st.columns([2, 1])
            with c_left:
                if not stats['chart_data'].empty and 'Cantidad' in stats['chart_data'].columns:
                    fig = px.bar(
                        stats['chart_data'], 
                        x='Cantidad', 
                        y='Sector', 
                        orientation='h', 
                        title="Concentración por Actividad Económica", 
                        color='Cantidad', 
                        color_continuous_scale='Bluyl'
                    )
                    fig.update_layout(
                        template='plotly_white',
                        paper_bgcolor='rgba(0,0,0,0)', 
                        plot_bgcolor='rgba(0,0,0,0)', 
                        font=dict(color='#1B3B5A', size=12),
                        height=400,
                        margin=dict(l=20, r=20, t=40, b=20)
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No hay datos analíticos para los filtros seleccionados.")
            
            with c_right:
                st.markdown("#### 🍩 Mix de Mercado")
                if not stats['chart_data'].empty:
                    fig_pie = px.pie(stats['chart_data'].head(5), values='Cantidad', names='Sector', hole=0.4, color_discrete_sequence=['#1B3B5A', '#4B6741', '#D49B35', '#9CA3AF', '#E5E7EB'])
                    fig_pie.update_layout(
                        template='plotly_white',
                        paper_bgcolor='rgba(0,0,0,0)', 
                        plot_bgcolor='rgba(0,0,0,0)', 
                        font=dict(color='#1B3B5A'), 
                        showlegend=False,
                        height=350,
                        margin=dict(l=10, r=10, t=10, b=10)
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)
            
            # Bottom Row: Data Table + Insights
            st.divider()
            bi_left, bi_right = st.columns([1, 1])
            
            with bi_left:
                st.markdown("#### 📋 Distribución Detallada")
                if not stats['chart_data'].empty:
                    display_df = stats['chart_data'].copy()
                    display_df['% del Total'] = (display_df['Cantidad'] / display_df['Cantidad'].sum() * 100).round(1)
                    display_df['% del Total'] = display_df['% del Total'].astype(str) + '%'
                    st.dataframe(display_df, use_container_width=True, hide_index=True)
                else:
                    st.caption("Sin datos para mostrar.")
            
            with bi_right:
                st.markdown("#### 💡 Insights Automáticos")
                if stats['total'] > 0 and not stats['chart_data'].empty:
                    top_sector = stats['chart_data'].iloc[0]
                    top_pct = round(top_sector['Cantidad'] / stats['total'] * 100, 1)
                    st.success(f"🏆 **{top_sector['Sector']}** domina con el **{top_pct}%** del mercado local.")
                    
                    if len(stats['chart_data']) >= 2:
                        bottom_sector = stats['chart_data'].iloc[-1]
                        bottom_pct = round(bottom_sector['Cantidad'] / stats['total'] * 100, 1)
                        st.warning(f"🔍 **{bottom_sector['Sector']}** representa solo el **{bottom_pct}%** — posible nicho desatendido.")
                    
                    st.info(f"📊 La comuna tiene **{len(stats['dist'])} sectores** económicos activos con **{stats['total']:,}** establecimientos registrados.")
                else:
                    st.caption("Selecciona una comuna con datos para ver insights.")

    # --------------------------
    # TAB 3: SIMULADOR DE ÉXITO (HACKATHON POWER-UP)
    # --------------------------
    with tab3:
        st.markdown("### 🧪 Simulador de Viabilidad Predictiva")
        st.markdown("Motor de predicción impulsado por IA que evalúa tu idea contra datos reales de competencia, transporte y flujo peatonal.")
        
        # Context bar
        ctx_c1, ctx_c2, ctx_c3 = st.columns(3)
        with ctx_c1:
            st.markdown(f"""<div class='kpi-card'>
                <div class='kpi-icon'>📍</div>
                <div class='kpi-value' style='font-size:1rem !important;'>{cnombres.get(st.session_state.comuna_id, 'N/A')}</div>
                <div class='kpi-label'>Comuna Base</div>
            </div>""", unsafe_allow_html=True)
        with ctx_c2:
            st.markdown(f"""<div class='kpi-card'>
                <div class='kpi-icon'>🏪</div>
                <div class='kpi-value'>{len(poi_comuna):,}</div>
                <div class='kpi-label'>Competidores Potenciales</div>
            </div>""", unsafe_allow_html=True)
        with ctx_c3:
            metro_ct = len(filter_geojson_by_comuna(metro_data['features'], st.session_state.comuna_id)) if metro_data else 0
            st.markdown(f"""<div class='kpi-card'>
                <div class='kpi-icon'>🚇</div>
                <div class='kpi-value'>{metro_ct}</div>
                <div class='kpi-label'>Nodos de Transporte</div>
            </div>""", unsafe_allow_html=True)
        
        st.markdown("")
        c_sim1, c_sim2 = st.columns([1, 1])
        with c_sim1:
            with st.container(border=True):
                idea = st.text_area("¿Cuál es tu propuesta de negocio?", placeholder="Ej: Venta de comida saludable cerca de la estación Estadio...", height=150)
                sim_comuna = st.selectbox("Comuna de Simulación:", opciones, format_func=lambda x: f"C{x} - {cnombres.get(x, '')}", key="sim_sel", index=idx)
                
                btn_sim_placeholder = st.empty()
                if btn_sim_placeholder.button("🚀 Calcular Probabilidad de Éxito", use_container_width=True):
                    if idea:
                        btn_sim_placeholder.button("⏳ Consultando simulador de inteligencia territorial...", disabled=True, use_container_width=True)
                        p_sim = filter_df_by_comuna(all_pois_df, sim_comuna)
                        m_sim = filter_geojson_by_comuna(metro_data['features'], sim_comuna) if metro_data else []
                        
                        ctx_sim = {
                            "comuna": cnombres.get(sim_comuna, "Desconocida"),
                            "competencia_en_sector": len(p_sim),
                            "puntos_transporte": [m['properties'].get('label') for m in m_sim],
                            "top_actividades": p_sim['sector'].value_counts().head(5).to_dict() if not p_sim.empty and 'sector' in p_sim.columns else {}
                        }
                        
                        try:
                            with st.spinner("Procesando simulación predictiva..."):
                                snapshot_sim = prepare_market_snapshot(sim_comuna, cnombres, p_sim, metro_data, attraction_data)
                                
                                SYSTEM_INSTRUCTION_SIMULATOR = (
                                    "Eres el 'Motor de Viabilidad Predictiva DataMede v2.0'. Tu función es evaluar proyectos empresariales en Medellín con rigor científico. \n\n"
                                    "METODOLOGÍA:\n"
                                    "1. Competencia: Compara la idea con el 'Mix Económico' y la 'Muestra ADN'. ¿Hay demasiados negocios similares?\n"
                                    "2. Sinergia: ¿La idea aprovecha las estaciones de Metro o Atractivos Turísticos mencionados?\n"
                                    "3. Riesgo: Identifica barreras de entrada específicas de la zona.\n\n"
                                    "ESTRUCTURA DE RESPUESTA (Obligatoria):\n"
                                    "1. 📈 SCORE DE ÉXITO: [X]% (Sé honesto, no des 100% a todo)\n"
                                    "2. 🧩 ANÁLISIS DE ENTORNO: Justifica basándote en la infraestructura y comercios actuales.\n"
                                    "3. ⚠️ RIESGOS: Menciona al menos 2 riesgos reales.\n"
                                    "4. 💡 PIVOTE ESTRATÉGICO: Sugiere un ajuste a la idea para que sea más exitosa."
                                )
                                
                                sim_prompt = f"IDEA A EVALUAR: {idea}\n\n<SNAPSHOT_LOCAL>\n{json.dumps(snapshot_sim, indent=2)}\n</SNAPSHOT_LOCAL>"
                                sim_resp = generate_ai_content(sim_prompt, SYSTEM_INSTRUCTION_SIMULATOR)
                                st.session_state.last_sim = sim_resp
                                st.rerun()
                        except Exception as e:
                            st.warning("⚠️ Error de cuota: El simulador está saturado. Reintenta en breve.")
                            btn_sim_placeholder.button("🚀 Calcular Probabilidad de Éxito", use_container_width=True, key="btn_sim_error")
                    else:
                        st.warning("Por favor, describe tu idea para realizar la simulación.")
                
                # Suggestion chips
                st.markdown("**Ideas sugeridas para explorar:**")
                chip_cols = st.columns(2)
                suggestions = ["Cafetería gourmet", "Tienda de tecnología", "Restaurante vegano", "Coworking space"]
                for i, sug in enumerate(suggestions):
                    with chip_cols[i % 2]:
                        st.markdown(f"<div class='suggestion-chip'>💡 {sug}</div>", unsafe_allow_html=True)
                
                st.write("") # Espaciador final para separar del borde inferior

        with c_sim2:
            if st.session_state.get("last_sim"):
                st.markdown("### 📊 Resultado del Análisis")
                with st.container(border=True, height=450):
                    st.markdown(st.session_state.last_sim)
                st.download_button("📩 Descargar Reporte (PDF)", "Contenido del reporte...", file_name="DataMede_Reporte.pdf", disabled=True, help="Función disponible en versión Pro")
            else:
                st.markdown("""<div class='metric-card' style='text-align:center; padding:3rem;'>
                    <p style='font-size:3rem;'>🧪</p>
                    <p><b>Motor de Predicción Territorial</b></p>
                    <p style='color:#6B7280 !important; font-size:0.9rem;'>Ingresa los detalles de tu emprendimiento para activar el análisis de viabilidad con IA.</p>
                    <hr style='margin:1rem 0; border-color: rgba(27,59,90,0.1);'>
                    <p style='font-size:0.8rem; color:#9CA3AF !important;'>Powered by GeoMed Intelligence Engine</p>
                </div>""", unsafe_allow_html=True)

    # --------------------------
    # TAB 4: CONSULTORÍA IA
    # --------------------------
    with tab4:
        st.markdown("<br>", unsafe_allow_html=True) 
        st.markdown("### 💬 Consultoría Estratégica en Tiempo Real")
        st.markdown(f"*Conversando sobre **{cnombres.get(st.session_state.comuna_id, 'Medellín')}** · {len(poi_comuna):,} establecimientos en contexto*")
        
        # Suggested questions
        if not st.session_state.messages:
            st.markdown("**Preguntas sugeridas para comenzar:**")
            sq1, sq2 = st.columns(2)
            with sq1:
                st.markdown("<div class='suggestion-chip'>🏪 ¿Qué tipo de negocio falta en esta comuna?</div>", unsafe_allow_html=True)
                st.markdown("<div class='suggestion-chip'>📊 ¿Cuál es la competencia en el sector gastronómico?</div>", unsafe_allow_html=True)
            with sq2:
                st.markdown("<div class='suggestion-chip'>🚇 ¿Cómo influye el Metro en los negocios?</div>", unsafe_allow_html=True)
                st.markdown("<div class='suggestion-chip'>💰 ¿Cuánto capital necesito para emprender aquí?</div>", unsafe_allow_html=True)
        
        # Contenedor para los mensajes del chat
        chat_container = st.container()
        
        with chat_container:
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]): st.markdown(msg["content"])
        
        st.write("") # Espaciador
        
        is_processing = st.session_state.get("chat_processing", False)
        
        prompt = st.chat_input("Pregúntale a DataMede sobre el mercado...", disabled=is_processing)
        
        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.session_state.chat_processing = True
            st.rerun()
            
        if is_processing and client:
            # Añadimos el estado de carga DENTRO del contenedor de mensajes
            # para que aparezca arriba del input y no lo desplace
            with chat_container:
                with st.chat_message("assistant"):
                    with st.spinner("Analizando..."):
                        snapshot_chat = prepare_market_snapshot(st.session_state.comuna_id, cnombres, poi_comuna, metro_data, attraction_data)
                        
                        SYSTEM_INSTRUCTION_CHATBOT = (
                            "Eres el 'Consultor Senior DataMede', experto en Geointeligencia y Economía de Medellín. \n\n"
                            "TU CONOCIMIENTO ACTUAL:\n"
                            f"{json.dumps(snapshot_chat, indent=2)}\n\n"
                            "REGLAS:\n"
                            "- Responde siempre basándote en los datos del SNAPSHOT arriba si la pregunta es sobre la comuna actual.\n"
                            "- Sé ejecutivo, profesional y proactivo.\n"
                            "- Si te preguntan algo que no está en el snapshot, usa tu conocimiento general de Medellín pero aclara que es una estimación."
                        )
                        
                        messages = [{"role": "system", "content": SYSTEM_INSTRUCTION_CHATBOT}]
                        for m in st.session_state.messages:
                            messages.append({"role": m["role"], "content": m["content"]})
                        
                        res_text = "Error: No se pudo obtener respuesta."
                        for m_id in MODELS:
                            try:
                                resp = client.chat.completions.create(
                                    model=m_id,
                                    messages=messages
                                )
                                res_text = resp.choices[0].message.content
                                break
                            except Exception as e:
                                if "429" in str(e): continue
                                res_text = f"Error: {e}"
                                break
                        
                        st.session_state.messages.append({"role": "assistant", "content": res_text})
                        st.session_state.chat_processing = False
                        st.rerun()

    # ===== FOOTER =====
    st.markdown("""
    <div class='app-footer'>
        <p><b>GeoMed Intelligence</b> · Plataforma de Geointeligencia Territorial</p>
        <p>Datos: Alcaldía de Medellín · Metro de Medellín · OpenRouter AI</p>
        <p style='margin-top:0.5rem; font-size:0.75rem;'>Hackathon Edition 2026 🚀 · Desarrollado con ❤️ en Medellín, Colombia</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__": main()
