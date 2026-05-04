import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import math
import json
import requests
import io

# ------------------------------------------------------------
# 1. CONFIGURACIÓN DE PÁGINA (PANTALLA COMPLETA)
# ------------------------------------------------------------
st.set_page_config(
    page_title="Monitor VDR - RIOMARKET", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# Inyección de CSS para eliminar márgenes laterales de Streamlit y aprovechar el ancho
st.markdown("""
    <style>
        .block-container {
            padding-top: 1rem;
            padding-bottom: 0rem;
            padding-left: 2rem;
            padding-right: 2rem;
        }
        iframe {
            width: 100%;
        }
    </style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------
# CARGA DE DATOS
# ------------------------------------------------------------
@st.cache_data(show_spinner=False)
def load_data():
    url = "https://raw.githubusercontent.com/juanbocanegraformacion-prog/recepcion/main/VDR_alerta.xlsx"
    try:
        res = requests.get(url)
        df = pd.read_excel(io.BytesIO(res.content), sheet_name="Sheet1", header=1)
        cols_map = {
            'Sucursal': 'sucursal',
            'N° Doc.Compra (VDR)': 'vdr',
            'Estatus compra (VDR)': 'estatus',
            'Número de orden de compra': 'odc',
            'Tipo ODC': 'tipo_odc',
            'Producto': 'producto',
            'Proveedor de transacción': 'proveedor',
            'Empaques Esperados': 'esperado',
            'Empaques Recibidos': 'recibido'
        }
        df = df[list(cols_map.keys())].rename(columns=cols_map)
    except Exception as e:
        st.error(f"No se pudo cargar el archivo Excel: {e}")
        df = pd.DataFrame(columns=["sucursal","vdr","estatus","odc","tipo_odc","producto","proveedor","esperado","recibido"])
    
    df["esperado"] = pd.to_numeric(df["esperado"], errors="coerce").fillna(0).astype(int)
    df["recibido"] = pd.to_numeric(df["recibido"], errors="coerce").fillna(0).astype(int)
    return df

df = load_data()

# ------------------------------------------------------------
# FILTROS EN SIDEBAR
# ------------------------------------------------------------
with st.sidebar:
    st.header("🔎 Filtros")
    
    sucursales = df['sucursal'].unique().tolist()
    sucursal_seleccionada = st.selectbox(
        "Sucursal",
        options=["Todas"] + sorted(sucursales),
        index=0
    )
    
    if sucursal_seleccionada == "Todas":
        df_temp = df.copy()
    else:
        df_temp = df[df['sucursal'] == sucursal_seleccionada].copy()
    
    estatus_unicos = sorted(df_temp['estatus'].unique().tolist())
    estatus_seleccionado = st.selectbox(
        "Estatus VDR",
        options=["Todas"] + estatus_unicos,
        index=0
    )
    
    if estatus_seleccionado == "Todas":
        df_final = df_temp.copy()
    else:
        df_final = df_temp[df_temp['estatus'] == estatus_seleccionado].copy()
    
    df_final.reset_index(drop=True, inplace=True)
    
    st.markdown("---")
    st.header("ℹ️ Información")
    total_vdr = df_final['vdr'].nunique()
    st.metric("VDR únicas", total_vdr)
    
    status_counts = df_final[['vdr', 'estatus']].drop_duplicates()['estatus'].value_counts()
    for status, count in status_counts.items():
        st.write(f"**{status}:** {count}")

# ------------------------------------------------------------
# PREPARAR DATOS Y PAGINACIÓN
# ------------------------------------------------------------
registros = df_final.to_dict(orient="records")
PAGE_SIZE = 10
total = len(registros)
total_pages = max(1, math.ceil(total / PAGE_SIZE))
pages = [registros[i:i+PAGE_SIZE] for i in range(0, total, PAGE_SIZE)]

# ------------------------------------------------------------
# HTML/CSS/JS DEL CARRUSEL (Actualizado para ocupar ancho)
# ------------------------------------------------------------
carrusel_html = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <style>
        :root {{
            --color-green: #2E7D32; --color-orange: #F57C00; --color-red: #D32F2F;
            --color-gray: #757575; --color-blue: #1976D2; --card-bg: #FFFFFF;
        }}
        body {{ font-family: 'Segoe UI', sans-serif; background: #f0f4f8; margin: 0; padding: 10px; overflow: hidden; }}
        .carousel-wrapper {{ width: 100%; display: flex; flex-direction: column; align-items: center; }}
        .carousel-viewport {{ width: 100%; max-width: 1200px; height: 920px; overflow: hidden; position: relative; }}
        .carousel-track {{ position: relative; width: 100%; height: 100%; transition: transform 0.4s ease-in-out; }}
        .page-group {{
            position: absolute; width: 100%; display: flex; flex-direction: column; 
            gap: 8px; padding: 10px; box-sizing: border-box;
        }}
        .page-group.active {{ z-index: 2; }}
        .vdr-card {{
            background: var(--card-bg); border-radius: 8px; padding: 10px 15px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1); display: flex; flex-direction: column; gap: 4px;
        }}
        .card-header {{ display: flex; justify-content: space-between; align-items: center; font-weight: bold; }}
        .status-badge {{ padding: 2px 10px; border-radius: 12px; font-size: 0.7rem; color: white; text-transform: uppercase; }}
        .status-badge.integrada {{ background: var(--color-green); }}
        .status-badge.en-validacion {{ background: var(--color-orange); }}
        .status-badge.pendiente-por-validar {{ background: var(--color-red); }}
        .status-badge.anulada {{ background: var(--color-gray); }}
        .status-badge.other {{ background: var(--color-gray); }}
        .producto {{ font-weight: 600; color: #333; }}
        .info-row {{ font-size: 0.75rem; color: #666; }}
        .progress-container {{ display: flex; align-items: center; gap: 10px; margin-top: 5px; }}
        .progress-bar {{ flex: 1; height: 6px; background: #eee; border-radius: 3px; overflow: hidden; }}
        .progress-fill {{ height: 100%; background: var(--color-green); transition: width 0.3s; }}
        .progress-text {{ font-family: monospace; font-weight: bold; font-size: 0.8rem; min-width: 120px; }}
        .nav-controls {{ display: flex; gap: 20px; margin-top: 10px; }}
        .nav-btn {{ 
            background: white; border: 1px solid #ccc; border-radius: 50%; width: 40px; height: 40px; 
            cursor: pointer; font-size: 1.2rem; transition: 0.2s;
        }}
        .nav-btn:hover {{ background: var(--color-green); color: white; border-color: var(--color-green); }}
        .dots {{ display: flex; gap: 8px; margin-top: 10px; }}
        .dot {{ width: 10px; height: 10px; border-radius: 50%; background: #ccc; cursor: pointer; }}
        .dot.active-dot {{ background: var(--color-green); transform: scale(1.2); }}
    </style>
</head>
<body>
    <div class="carousel-wrapper">
        <div class="carousel-viewport" id="viewport">
            <div class="carousel-track" id="track"></div>
        </div>
        <div class="nav-controls">
            <button class="nav-btn" id="prevBtn">▲</button>
            <div class="dots" id="dots"></div>
            <button class="nav-btn" id="nextBtn">▼</button>
        </div>
    </div>

    <script>
        const pages = {json.dumps(pages)};
        const totalPages = pages.length;
        const PAGE_HEIGHT = 920;
        let currentPage = 0;

        const track = document.getElementById('track');
        const dotsContainer = document.getElementById('dots');

        function getStatusClass(s) {{
            const n = s.toLowerCase();
            if (n.includes('integrada')) return 'integrada';
            if (n.includes('en-validacion')) return 'en-validacion';
            if (n.includes('pendiente')) return 'pendiente-por-validar';
            return 'other';
        }}

        function renderPages() {{
            track.innerHTML = '';
            pages.forEach((page, i) => {{
                const group = document.createElement('div');
                group.className = 'page-group' + (i === 0 ? ' active' : '');
                group.style.top = (i * PAGE_HEIGHT) + 'px';
                group.innerHTML = page.map(item => {{
                    const pct = Math.min(100, Math.round((item.recibido / (item.esperado || 1)) * 100));
                    return `
                        <div class="vdr-card">
                            <div class="card-header">
                                <span>${{item.sucursal}} · ${{item.vdr}}</span>
                                <span class="status-badge ${{getStatusClass(item.estatus)}}">${{item.estatus}}</span>
                            </div>
                            <div class="info-row">📄 ODC: ${{item.odc}} | Tipo: ${{item.tipo_odc}}</div>
                            <div class="producto">${{item.producto}}</div>
                            <div class="info-row">🏭 ${{item.proveedor}}</div>
                            <div class="progress-container">
                                <div class="progress-bar"><div class="progress-fill" style="width:${{pct}}%"></div></div>
                                <div class="progress-text">${{item.recibido}} / ${{item.esperado}} (${{pct}}%)</div>
                            </div>
                        </div>`;
                }}).join('');
                track.appendChild(group);
            }});
        }}

        function updateCarousel() {{
            track.style.transform = `translateY(${{-currentPage * PAGE_HEIGHT}}px)`;
            document.querySelectorAll('.dot').forEach((d, i) => d.className = 'dot' + (i === currentPage ? ' active-dot' : ''));
        }}

        function renderDots() {{
            dotsContainer.innerHTML = '';
            for(let i=0; i<totalPages; i++) {{
                const d = document.createElement('div');
                d.className = 'dot' + (i===0?' active-dot':'');
                d.onclick = () => {{ currentPage = i; updateCarousel(); }};
                dotsContainer.appendChild(d);
            }}
        }}

        document.getElementById('nextBtn').onclick = () => {{ currentPage = (currentPage + 1) % totalPages; updateCarousel(); }};
        document.getElementById('prevBtn').onclick = () => {{ currentPage = (currentPage - 1 + totalPages) % totalPages; updateCarousel(); }};
        
        window.addEventListener('keydown', e => {{
            if (e.key === 'ArrowDown') {{ currentPage = (currentPage + 1) % totalPages; updateCarousel(); }}
            if (e.key === 'ArrowUp') {{ currentPage = (currentPage - 1 + totalPages) % totalPages; updateCarousel(); }}
        }});

        renderPages();
        renderDots();
        setInterval(() => {{ currentPage = (currentPage + 1) % totalPages; updateCarousel(); }}, 15000);
    </script>
</body>
</html>
"""

# ------------------------------------------------------------
# 2. INTERFAZ STREAMLIT (TÍTULO Y RENDERIZADO)
# ------------------------------------------------------------
# Lógica de título optimizada
filtros_lista = []
if sucursal_seleccionada != "Todas": filtros_lista.append(sucursal_seleccionada)
if estatus_seleccionado != "Todas": filtros_lista.append(estatus_seleccionado)

titulo_display = "📦 Monitor de Recepciones (VDR)"
if filtros_lista:
    titulo_display += " • " + " | ".join(filtros_lista)

st.title(titulo_display)
st.caption("Modo pantalla completa activo. Use las flechas o el control inferior para navegar.")

# Renderizado con altura suficiente para las 10 tarjetas y controles
components.html(carrusel_html, height=1050, scrolling=False)
