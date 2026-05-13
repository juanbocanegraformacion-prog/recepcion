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
def load_data(cache_buster: int):
    url_base = "https://raw.githubusercontent.com/juanbocanegraformacion-prog/recepcion/main/VDR_alerta.xlsx"
    url = f"{url_base}?t={cache_buster}" if cache_buster else url_base
    try:
        response = requests.get(url, headers={'Cache-Control': 'no-cache'}, timeout=10)
        response.raise_for_status()  # Lanza excepción si status no es 200

        # --- Validación adicional: el contenido debe ser un archivo ZIP/Excel ---
        content = response.content
        # Un archivo Excel (.xlsx) comienza con los bytes 'PK' (0x50, 0x4B)
        if not content.startswith(b'PK'):
            # Intentamos decodificar los primeros 200 caracteres para ver si es HTML
            preview = content[:200].decode('utf-8', errors='ignore')
            if '<!DOCTYPE html>' in preview or '<html' in preview:
                raise ValueError(
                    "El enlace no devuelve un archivo Excel. Parece ser una página HTML.\n"
                    "Verifica que el archivo exista en el repositorio y que la rama y ruta sean correctas."
                )
            else:
                raise ValueError(
                    "El archivo descargado no es un Excel válido (no tiene formato ZIP).\n"
                    "Posiblemente la URL apunte a un archivo corrupto o de otro tipo."
                )

        excel_data = io.BytesIO(content)
        df = pd.read_excel(excel_data, sheet_name="Sheet1", header=1, engine='openpyxl')

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
        # Verificar que todas las columnas necesarias existan
        df = df[list(cols_map.keys())].rename(columns=cols_map)
        df["esperado"] = pd.to_numeric(df["esperado"], errors="coerce").fillna(0).astype(int)
        df["recibido"] = pd.to_numeric(df["recibido"], errors="coerce").fillna(0).astype(int)
        return df
    except Exception as e:
        st.error(f"Error al cargar datos: {e}")
        # Retorna DataFrame vacío con las columnas esperadas
        return pd.DataFrame(columns=[
            "sucursal", "vdr", "estatus", "odc", "tipo_odc",
            "producto", "proveedor", "esperado", "recibido"
        ])

# Cargar datos (siempre asigna df, aunque sea vacío)
df = load_data(st.session_state.cache_buster)

# Si por algún motivo df no es DataFrame (ej. None), forzamos vacío
if not isinstance(df, pd.DataFrame):
    df = pd.DataFrame(columns=[
        "sucursal", "vdr", "estatus", "odc", "tipo_odc",
        "producto", "proveedor", "esperado", "recibido"
    ])


# ------------------------------------------------------------
# FILTROS EN SIDEBAR (SUCURSAL + ESTATUS) Y MÉTRICAS
# ------------------------------------------------------------
with st.sidebar:
    st.header("🔎 Filtros")
    
    sucursales = df['sucursal'].unique().tolist()
    sucursal_seleccionada = st.selectbox(
        "Sucursal",
        options=["Todas"] + sorted(sucursales),
        index=0,
        help="Selecciona una sucursal para filtrar los datos, o 'Todas' para ver el consolidado."
    )
    
    if sucursal_seleccionada == "Todas":
        df_temp = df.copy()
    else:
        df_temp = df[df['sucursal'] == sucursal_seleccionada].copy()
    
    estatus_unicos = sorted(df_temp['estatus'].unique().tolist())
    estatus_seleccionado = st.selectbox(
        "Estatus VDR",
        options=["Todas"] + estatus_unicos,
        index=0,
        help="Filtrar por el estatus de compra de la VDR."
    )
    
    if estatus_seleccionado == "Todas":
        df_final = df_temp.copy()
    else:
        df_final = df_temp[df_temp['estatus'] == estatus_seleccionado].copy()
    
    df_final.reset_index(drop=True, inplace=True)
    
    st.markdown("---")
    st.header("ℹ️ Información")
    total_vdr = df_final['vdr'].nunique()
    st.metric("VDR únicas cargadas", total_vdr)
    
    status_counts = df_final[['vdr', 'estatus']].drop_duplicates()['estatus'].value_counts()
    st.markdown("**Distribución por estatus (VDR únicas):**")
    num_status = len(status_counts)
    for r in range(math.ceil(num_status/2)):
        cols = st.columns(2)
        for c in range(2):
            idx = r*2 + c
            if idx < num_status:
                status = status_counts.index[idx]
                count = status_counts.iloc[idx]
                cols[c].metric(label=status, value=count)

    st.markdown("---")
    if st.button("🔄 Refrescar datos", help="Descarga de nuevo el archivo Excel actualizado"):
        st.session_state.cache_buster += 1
        st.rerun()

# ------------------------------------------------------------
# DATOS PARA EL CARRUSEL
# ------------------------------------------------------------
registros = df_final.to_dict(orient="records")

PAGE_SIZE = 10
total = len(registros)
total_pages = max(1, math.ceil(total / PAGE_SIZE))
pages = [registros[i:i+PAGE_SIZE] for i in range(0, total, PAGE_SIZE)]

# ------------------------------------------------------------
# HTML/CSS/JS DEL CARRUSEL (ROTACIÓN CADA 6 SEGUNDOS, SIN AUTO-REFRESCO DE PÁGINA)
# ------------------------------------------------------------
carrusel_html = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        :root {{
            --color-green: #2E7D32;
            --color-orange: #F57C00;
            --color-red: #D32F2F;
            --color-gray: #757575;
            --color-blue: #1976D2;
            --card-bg: #FFFFFF;
            --card-border-radius: 8px;
            --shadow: 0 2px 6px rgba(0,0,0,0.08);
            --shadow-active: 0 0 16px rgba(46,125,50,0.4);
            --transition-speed: 0.4s;
            --font-stack: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            --mono-font: 'Cascadia Code', 'Fira Code', 'Consolas', monospace;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: var(--font-stack);
            background: #f0f4f8;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 10px;
        }}
        .carousel-wrapper {{
            position: relative;
            width: 100%;
            max-width: 95vw;
            margin: 0 auto;
            display: flex;
            flex-direction: column;
            align-items: center;
        }}
        .carousel-viewport {{
            width: 100%;
            height: clamp(800px, 80vh, 1100px);
            overflow: hidden;
            position: relative;
            border-radius: var(--card-border-radius);
        }}
        .carousel-track {{
            position: relative;
            width: 100%;
            height: 100%;
            transition: transform var(--transition-speed) ease-in-out;
            will-change: transform;
        }}
        .page-group {{
            position: absolute;
            left: 50%;
            transform: translateX(-50%);
            width: 100%;
            display: flex;
            flex-direction: column;
            gap: 6px;
            align-items: stretch;
            padding: 8px;
            background: rgba(255,255,255,0.85);
            border-radius: var(--card-border-radius);
            box-shadow: var(--shadow);
            opacity: 0.8;
            filter: brightness(0.97);
        }}
        .page-group.active {{
            box-shadow: var(--shadow-active);
            border: 2px solid var(--color-green);
            opacity: 1;
            filter: brightness(1);
            z-index: 2;
        }}
        .vdr-card {{
            background: var(--card-bg);
            border-radius: var(--card-border-radius);
            box-shadow: 0 1px 3px rgba(0,0,0,0.08);
            padding: clamp(4px, 1vw, 8px) clamp(6px, 2vw, 12px);
            display: flex;
            flex-direction: column;
            gap: 3px;
            font-size: clamp(0.7rem, 1.5vw, 0.85rem);
            font-weight: bold;
        }}
        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            font-size: clamp(0.75rem, 1.6vw, 0.9rem);
        }}
        .sucursal-vdr {{
            font-weight: 700;
            color: #1a1a1a;
            white-space: normal;
            overflow: visible;
            word-break: break-word;
        }}
        .status-badge {{
            display: inline-block;
            padding: 1px 6px;
            border-radius: 12px;
            font-size: 0.6rem;
            font-weight: 600;
            text-transform: uppercase;
            color: white;
            white-space: nowrap;
            flex-shrink: 0;
            margin-left: 8px;
        }}
        .status-badge.integrada {{ background: var(--color-green); }}
        .status-badge.en-validacion {{ background: var(--color-orange); }}
        .status-badge.pendiente-por-validar {{ background: var(--color-red); }}
        .status-badge.anulada {{ background: var(--color-gray); }}
        .status-badge.other {{ background: var(--color-gray); }}
        .producto {{
            font-size: clamp(0.7rem, 1.4vw, 0.8rem);
            font-weight: 600;
            white-space: normal;
            overflow: visible;
        }}
        .odc-row, .proveedor-row {{
            display: flex;
            align-items: center;
            gap: 4px;
            font-size: clamp(0.6rem, 1.2vw, 0.7rem);
            color: #555;
            white-space: normal;
            overflow: visible;
        }}
        .progress-container {{
            display: flex;
            align-items: center;
            gap: 8px;
            margin-top: 2px;
        }}
        .progress-bar-wrapper {{
            flex: 1;
            height: 4px;
            background: #e0e0e0;
            border-radius: 2px;
            overflow: hidden;
        }}
        .progress-fill {{
            height: 100%;
            background: var(--color-green);
            transition: width 0.3s;
            border-radius: 2px;
        }}
        .progress-fill.over {{ background: var(--color-blue); }}
        .progress-text {{
            font-family: var(--mono-font);
            font-size: 0.7rem;
            color: #333;
            font-weight: bold;
            white-space: nowrap;
        }}
        .nav-btn {{
            background: #e0e0e0;
            border: none;
            border-radius: 50%;
            width: 32px;
            height: 32px;
            font-size: 1.1rem;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: background 0.2s;
        }}
        .nav-btn:hover {{ background: var(--color-green); color: white; }}

        /* PAGINACIÓN NUMÉRICA (BLOQUES DE 10) */
        .pagination-container {{
            display: flex;
            align-items: center;
            gap: 4px;
            margin-top: 8px;
            flex-wrap: wrap;
            justify-content: center;
        }}
        .page-number {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            min-width: 28px;
            height: 28px;
            padding: 0 4px;
            border-radius: 4px;
            background: #e0e0e0;
            color: #333;
            font-size: 0.75rem;
            font-weight: bold;
            cursor: pointer;
            transition: background 0.2s, color 0.2s;
        }}
        .page-number:hover {{ background: #bdbdbd; }}
        .page-number.active {{
            background: var(--color-green);
            color: white;
            box-shadow: 0 0 0 2px rgba(46,125,50,0.3);
        }}
        .dots-arrow {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            min-width: 28px;
            height: 28px;
            padding: 0 4px;
            border-radius: 4px;
            background: transparent;
            color: #555;
            font-size: 0.9rem;
            font-weight: bold;
            cursor: pointer;
            user-select: none;
        }}
        .dots-arrow:hover {{ background: #e0e0e0; }}
        .empty-state {{
            text-align: center;
            padding: 60px 20px;
            color: #666;
            font-size: 1.1rem;
            font-weight: bold;
        }}

        @media (max-width: 600px) {{
            .carousel-viewport {{
                height: clamp(600px, 70vh, 800px);
            }}
            .vdr-card {{
                padding: 4px 6px;
                font-size: 0.7rem;
            }}
            .page-number, .dots-arrow {{
                min-width: 24px;
                height: 24px;
                font-size: 0.65rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="carousel-wrapper" role="region" aria-label="Carrusel vertical de recepciones por página">
        <button class="nav-btn prev" id="prevBtn" title="Página anterior">▲</button>
        <div class="carousel-viewport" id="viewport">
            <div class="carousel-track" id="track"></div>
        </div>
        <button class="nav-btn next" id="nextBtn" title="Página siguiente">▼</button>
        <div class="pagination-container" id="pagination"></div>
        <div aria-live="polite" id="announce" style="position:absolute;left:-9999px"></div>
    </div>

    <script>
        const pages = {json.dumps(pages)};
        const totalPages = pages.length;
        const PAGE_HEIGHT = document.querySelector('.carousel-viewport').clientHeight;

        const track = document.getElementById('track');
        const viewport = document.getElementById('viewport');
        const prevBtn = document.getElementById('prevBtn');
        const nextBtn = document.getElementById('nextBtn');
        const paginationContainer = document.getElementById('pagination');
        const announcer = document.getElementById('announce');

        let currentPage = 0;
        let autoTimer = null;
        let paused = false;

        function getStatusClass(estatus) {{
            const n = estatus.trim().toLowerCase().replace(/\s+/g, '-');
            if (n === 'integrada') return 'integrada';
            if (n.includes('en-validacion')) return 'en-validacion';
            if (n.includes('pendiente-por-validar')) return 'pendiente-por-validar';
            if (n === 'anulada') return 'anulada';
            return 'other';
        }}

        function renderPageGroup(pageItems) {{
            let html = '';
            pageItems.forEach(item => {{
                const pct = Math.min(100, Math.round((item.recibido / (item.esperado || 1)) * 100));
                const over = item.recibido > item.esperado;
                html += `
                <div class="vdr-card">
                    <div class="card-header">
                        <span class="sucursal-vdr" title="${{item.sucursal}} · ${{item.vdr}}">${{item.sucursal}} · ${{item.vdr}}</span>
                        <span class="status-badge ${{getStatusClass(item.estatus)}}">${{item.estatus}}</span>
                    </div>
                    <div class="odc-row">
                        <span>📄 ODC:</span> ${{item.odc}} <span style="margin-left:8px;">Tipo: ${{item.tipo_odc}}</span>
                    </div>
                    <div class="producto" title="${{item.producto}}">${{item.producto}}</div>
                    <div class="proveedor-row">
                        <span>🏭 Proveedor:</span> ${{item.proveedor}}
                    </div>
                    <div class="progress-container">
                        <div class="progress-bar-wrapper">
                            <div class="progress-fill${{over ? ' over' : ''}}" style="width: ${{pct}}%;"></div>
                        </div>
                        <div class="progress-text">${{item.recibido}} / ${{item.esperado}} (${{pct}}%)</div>
                    </div>
                </div>`;
            }});
            return html;
        }}

        function buildCarousel() {{
            if (totalPages === 0) {{
                viewport.innerHTML = '<div class="empty-state">No hay recepciones disponibles.</div>';
                prevBtn.style.display = 'none'; nextBtn.style.display = 'none';
                paginationContainer.innerHTML = '';
                return;
            }}
            if (totalPages === 1) {{
                track.innerHTML = `<div class="page-group active" style="top:20px;">${{renderPageGroup(pages[0])}}</div>`;
                prevBtn.style.visibility = 'hidden'; nextBtn.style.visibility = 'hidden';
                paginationContainer.innerHTML = '';
                return;
            }}

            const cloneLast = pages[totalPages-1];
            const cloneFirst = pages[0];
            const allPages = [cloneLast, ...pages, cloneFirst];

            track.innerHTML = '';
            allPages.forEach((page, idx) => {{
                const group = document.createElement('div');
                group.className = 'page-group' + (idx === 1 ? ' active' : '');
                group.style.top = (idx * PAGE_HEIGHT) + 'px';
                group.innerHTML = renderPageGroup(page);
                track.appendChild(group);
            }});

            currentPage = 0;
            track.style.transform = `translateY(${{-1 * PAGE_HEIGHT}}px)`;
            renderPagination(currentPage);
        }}

        function renderPagination(activeIdx) {{
            if (totalPages <= 1) {{
                paginationContainer.innerHTML = '';
                return;
            }}
            
            const BLOCK_SIZE = 10;
            const blockStart = Math.floor(activeIdx / BLOCK_SIZE) * BLOCK_SIZE;
            const blockEnd = Math.min(blockStart + BLOCK_SIZE, totalPages);
            
            let html = '';
            
            if (blockStart > 0) {{
                html += `<span class="dots-arrow" onclick="goToPage(${{blockStart - 1}})" title="Anterior ${{BLOCK_SIZE}} páginas">«</span>`;
            }}
            
            for (let i = blockStart; i < blockEnd; i++) {{
                const pageNumber = i + 1;
                html += `<span class="page-number${{i === activeIdx ? ' active' : ''}}" onclick="goToPage(${{i}})">${{pageNumber}}</span>`;
            }}
            
            if (blockEnd < totalPages) {{
                html += `<span class="dots-arrow" onclick="goToPage(${{blockEnd}})" title="Siguiente ${{BLOCK_SIZE}} páginas">»</span>`;
            }}
            
            paginationContainer.innerHTML = html;
        }}

        function goToPage(index) {{
            if (totalPages <= 1) return;
            if (index < 0) index = 0;
            if (index >= totalPages) index = totalPages - 1;
            
            currentPage = index;
            const offset = -(index + 1) * PAGE_HEIGHT;
            track.style.transition = 'transform 0.4s ease-in-out';
            track.style.transform = `translateY(${{offset}}px)`;
            updateActivePage();
            renderPagination(index);
            announcer.textContent = `Página ${{index+1}} de ${{totalPages}}`;
        }}

        function updateActivePage() {{
            const groups = track.querySelectorAll('.page-group');
            groups.forEach((g, i) => {{
                g.classList.remove('active');
                if (i === currentPage + 1) g.classList.add('active');
            }});
        }}

        function handleTransitionEnd() {{
            if (currentPage >= totalPages) {{
                track.style.transition = 'none';
                track.style.transform = `translateY(${{-1 * PAGE_HEIGHT}}px)`;
                currentPage = 0;
                updateActivePage();
                renderPagination(0);
                track.offsetHeight;
                track.style.transition = 'transform 0.4s ease-in-out';
            }} else if (currentPage < 0) {{
                track.style.transition = 'none';
                track.style.transform = `translateY(${{-totalPages * PAGE_HEIGHT}}px)`;
                currentPage = totalPages - 1;
                updateActivePage();
                renderPagination(totalPages - 1);
                track.offsetHeight;
                track.style.transition = 'transform 0.4s ease-in-out';
            }}
        }}

        function next() {{
            if (totalPages <= 1) return;
            let newPage = currentPage + 1;
            if (newPage >= totalPages) newPage = 0;
            goToPage(newPage);
        }}

        function prev() {{
            if (totalPages <= 1) return;
            let newPage = currentPage - 1;
            if (newPage < 0) newPage = totalPages - 1;
            goToPage(newPage);
        }}

        function startAuto() {{
            stopAuto();
            if (totalPages > 1) autoTimer = setInterval(next, 6000);  // ← CAMBIO: de 10000 a 6000 ms
        }}
        function stopAuto() {{ if (autoTimer) clearInterval(autoTimer); }}

        prevBtn.onclick = () => {{ prev(); stopAuto(); startAuto(); }};
        nextBtn.onclick = () => {{ next(); stopAuto(); startAuto(); }};

        viewport.addEventListener('mouseenter', stopAuto);
        viewport.addEventListener('mouseleave', () => {{ if (!paused) startAuto(); }});

        let touchY = 0;
        viewport.addEventListener('touchstart', e => {{ touchY = e.touches[0].clientY; stopAuto(); }});
        viewport.addEventListener('touchend', e => {{
            const diff = touchY - e.changedTouches[0].clientY;
            if (Math.abs(diff) > 40) {{ diff > 0 ? next() : prev(); }}
            startAuto();
        }});

        window.addEventListener('keydown', e => {{
            if (e.key === 'ArrowDown') {{ e.preventDefault(); next(); stopAuto(); startAuto(); }}
            else if (e.key === 'ArrowUp') {{ e.preventDefault(); prev(); stopAuto(); startAuto(); }}
        }});

        window.addEventListener('resize', () => {{
            const newHeight = viewport.clientHeight;
            if (newHeight !== PAGE_HEIGHT) {{
                const oldPage = currentPage;
                const groups = track.querySelectorAll('.page-group');
                groups.forEach((g, idx) => {{
                    g.style.top = (idx * PAGE_HEIGHT) + 'px';
                }});
                PAGE_HEIGHT = newHeight;
                goToPage(oldPage);
            }}
        }});

        track.addEventListener('transitionend', handleTransitionEnd);

        buildCarousel();
        startAuto();
    </script>
</body>
</html>
"""

# ------------------------------------------------------------
# INTERFAZ STREAMLIT
# ------------------------------------------------------------
titulo = "📦 Monitor de Recepciones (VDR)"
if sucursal_seleccionada != "Todas" or estatus_seleccionado != "Todas":
    filtros_activos = []
    if sucursal_seleccionada != "Todas":
        filtros_activos.append(f"Sucursal: {sucursal_seleccionada}")
    if estatus_seleccionado != "Todas":
        filtros_activos.append(f"Estatus: {estatus_seleccionado}")
    titulo += " – " + " | ".join(filtros_activos)
st.title(titulo)
st.markdown("Cada página muestra hasta 10 recepciones. Navegue con botones, teclado o deslizando.")

components.html(carrusel_html, height=1150, scrolling=False)
