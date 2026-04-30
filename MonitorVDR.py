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
# CARGA DE DATOS DESDE EXCEL O DATOS DE EJEMPLO
# ------------------------------------------------------------
@st.cache_data(show_spinner=False)
def load_data():
    url = "https://raw.githubusercontent.com/juanbocanegraformacion-prog/recepcion/main/Reporte-Consolidado-Compras-Producto%2B29-04-2026_29-04-2026.xlsx"
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
        st.warning(f"No se pudo cargar el archivo Excel ({e}). Usando datos de ejemplo.")
        sample_data = [
            ["JUAN BAUTISTA ARISMENDI", "VDR-01-001-00014430", "Integrada", "ODC-01-001-00015743", "Parcial",
             "DETERGENTE EN POLVO FRAGANCIA CITRICA LAS LLAVES 900 GR", "ALIMENTOS POLAR COMERCIAL, C.A.", 50, 50],
            ["JUAN BAUTISTA ARISMENDI", "VDR-01-001-00014430", "Integrada", "ODC-01-001-00015743", "Parcial",
             "DETERGENTE EN POLVO FRAGANCIA BEBE LAS LLAVES 400GR", "ALIMENTOS POLAR COMERCIAL, C.A.", 36, 32],
            ["JUAN BAUTISTA ARISMENDI", "VDR-01-001-00014430", "Integrada", "ODC-01-001-00015743", "Parcial",
             "DETERGENTE EN POLVO FRAGANCIA BEBE LAS LLAVES 900GR", "ALIMENTOS POLAR COMERCIAL, C.A.", 10, 10],
            ["JUAN BAUTISTA ARISMENDI", "VDR-01-001-00014431", "Integrada", "ODC-01-001-00015805", "Parcial",
             "CERVEZA POLAR LIGHT RET 222ML", "CERVECERIA POLAR, C.A.", 540, 540],
            ["JUAN BAUTISTA ARISMENDI", "VDR-01-001-00014431", "Integrada", "ODC-01-001-00015805", "Parcial",
             "GAVERA DE CERVEZA POLAR", "CERVECERIA POLAR, C.A.", 15, 15],
            ["JUAN BAUTISTA ARISMENDI", "VDR-01-001-00014432", "Integrada", "ODC-01-001-00015798", "Parcial",
             "REFRESCO ZERO PEPSI 2L", "PEPSI-COLA VENEZUELA C.A.", 12, 12],
            ["JUAN BAUTISTA ARISMENDI", "VDR-01-001-00014432", "Integrada", "ODC-01-001-00015798", "Parcial",
             "REFRESCO SABOR PIÑA PET GOLDEN 2L", "PEPSI-COLA VENEZUELA C.A.", 30, 30],
            ["JUAN BAUTISTA ARISMENDI", "VDR-01-001-00014433", "Integrada", "ODC-01-001-00015798", "Parcial",
             "REFRESCO KOLITA GOLDEN 2 L", "PEPSI-COLA VENEZUELA C.A.", 54, 54],
            ["JUAN BAUTISTA ARISMENDI", "VDR-01-001-00014433", "Integrada", "ODC-01-001-00015798", "Parcial",
             "REFRESCO KOLITA GOLDEN 1.5 L", "PEPSI-COLA VENEZUELA C.A.", 60, 60],
            ["JUAN BAUTISTA ARISMENDI", "VDR-01-001-00014433", "Integrada", "ODC-01-001-00015798", "Parcial",
             "REFRESCO DE PIÑA GOLDEN 1.5 L", "PEPSI-COLA VENEZUELA C.A.", 60, 60],
            ["JUAN BAUTISTA ARISMENDI", "VDR-01-001-00014434", "En validación", "ODC-01-001-00015799", "Total",
             "MORTADELA DE POLLO SUPERIOR HERMO 1 KG.", "INDUSTRIAS ALIMENTICIAS HERMO DE VENEZUELA S.A.", 20, 15],
            ["JUAN BAUTISTA ARISMENDI", "VDR-01-001-00014435", "Pendiente por validar", "ODC-01-005-00013785", "Parcial",
             "PAÑAL ACTIVESEC DISNEY TALLA XG HUGGIES 25 UND", "DIMASSI, C.A.", 24, 8],
            ["JUAN BAUTISTA ARISMENDI", "VDR-01-001-00014436", "Anulada", "ODC-01-016-00016341", "Parcial",
             "JAMON ESPALDA AHUMADA VISKING DELGADO ALIMEX 1.6 KG", "PRODUCTOS ALIMEX, C.A.", 21, 0],
        ]
        df = pd.DataFrame(sample_data, columns=["sucursal","vdr","estatus","odc","tipo_odc","producto","proveedor","esperado","recibido"])
    df["esperado"] = pd.to_numeric(df["esperado"], errors="coerce").fillna(0).astype(int)
    df["recibido"] = pd.to_numeric(df["recibido"], errors="coerce").fillna(0).astype(int)
    return df

df = load_data()
registros = df.to_dict(orient="records")

# ------------------------------------------------------------
# PAGINACIÓN (10 registros por página)
# ------------------------------------------------------------
PAGE_SIZE = 10
total = len(registros)
total_pages = max(1, math.ceil(total / PAGE_SIZE))
pages = [registros[i:i+PAGE_SIZE] for i in range(0, total, PAGE_SIZE)]

# ------------------------------------------------------------
# HTML/CSS/JS DEL CARRUSEL PAGINADO (10 tarjetas visibles)
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
            max-width: 800px;  /* se adapta al ancho de la columna de Streamlit */
            margin: 0 auto;
            display: flex;
            flex-direction: column;
            align-items: center;
        }}
        .carousel-viewport {{
            width: 100%;
            height: 720px;          /* altura suficiente para 10 tarjetas compactas */
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
            width: 96%;
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
            padding: 6px 10px;
            display: flex;
            flex-direction: column;
            gap: 3px;
            font-size: 0.8rem;
        }}
        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.85rem;
        }}
        .sucursal-vdr {{
            font-weight: 700;
            color: #1a1a1a;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        .status-badge {{
            display: inline-block;
            padding: 1px 8px;
            border-radius: 12px;
            font-size: 0.65rem;
            font-weight: 600;
            text-transform: uppercase;
            color: white;
            white-space: nowrap;
        }}
        .status-badge.integrada {{ background: var(--color-green); }}
        .status-badge.en-validacion {{ background: var(--color-orange); }}
        .status-badge.pendiente-por-validar {{ background: var(--color-red); }}
        .status-badge.anulada {{ background: var(--color-gray); }}
        .status-badge.other {{ background: var(--color-gray); }}
        .producto {{
            font-size: 0.78rem;
            font-weight: 600;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        .odc-row, .proveedor-row {{
            display: flex;
            align-items: center;
            gap: 4px;
            font-size: 0.68rem;
            color: #555;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
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
            white-space: nowrap;
        }}
        .nav-controls {{
            display: flex;
            gap: 12px;
            margin: 10px 0;
            align-items: center;
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
        .dots {{
            display: flex;
            gap: 6px;
            margin-top: 6px;
        }}
        .dot {{
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #bbb;
            cursor: pointer;
            transition: background 0.2s;
        }}
        .dot.active-dot {{
            background: var(--color-green);
            transform: scale(1.2);
        }}
        .empty-state {{
            text-align: center;
            padding: 60px 20px;
            color: #666;
            font-size: 1.1rem;
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
        <div class="dots" id="dots"></div>
        <div aria-live="polite" id="announce" style="position:absolute;left:-9999px"></div>
    </div>

    <script>
        const pages = {json.dumps(pages)};
        const totalPages = pages.length;
        const PAGE_HEIGHT = 720;   /* igual a la altura del viewport */

        const track = document.getElementById('track');
        const viewport = document.getElementById('viewport');
        const prevBtn = document.getElementById('prevBtn');
        const nextBtn = document.getElementById('nextBtn');
        const dotsContainer = document.getElementById('dots');
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
                    <div class="producto" title="${{item.producto}}">${{item.producto.length > 50 ? item.producto.substring(0,50)+'...' : item.producto}}</div>
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
                return;
            }}
            if (totalPages === 1) {{
                track.innerHTML = `<div class="page-group active" style="top:20px;">${{renderPageGroup(pages[0])}}</div>`;
                prevBtn.style.visibility = 'hidden'; nextBtn.style.visibility = 'hidden';
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
            renderDots(currentPage);
        }}

        function renderDots(activeIdx) {{
            dotsContainer.innerHTML = '';
            for (let i = 0; i < totalPages; i++) {{
                const dot = document.createElement('div');
                dot.className = 'dot' + (i === activeIdx ? ' active-dot' : '');
                dot.onclick = () => goToPage(i);
                dotsContainer.appendChild(dot);
            }}
        }}

        function goToPage(index) {{
            if (totalPages <= 1) return;
            currentPage = index;
            const offset = -(index + 1) * PAGE_HEIGHT;
            track.style.transition = 'transform 0.4s ease-in-out';
            track.style.transform = `translateY(${{offset}}px)`;
            updateActivePage();
            renderDots(index);
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
                renderDots(0);
                track.offsetHeight;
                track.style.transition = 'transform 0.4s ease-in-out';
            }} else if (currentPage < 0) {{
                track.style.transition = 'none';
                track.style.transform = `translateY(${{-totalPages * PAGE_HEIGHT}}px)`;
                currentPage = totalPages - 1;
                updateActivePage();
                renderDots(totalPages-1);
                track.offsetHeight;
                track.style.transition = 'transform 0.4s ease-in-out';
            }}
        }}

        function next() {{
            if (totalPages <= 1) return;
            currentPage++;
            if (currentPage >= totalPages) currentPage = totalPages;
            goToPage(currentPage);
        }}

        function prev() {{
            if (totalPages <= 1) return;
            currentPage--;
            if (currentPage < 0) currentPage = -1;
            goToPage(currentPage);
        }}

        function startAuto() {{
            stopAuto();
            if (totalPages > 1) autoTimer = setInterval(next, 10000);
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
st.title("📦 Monitor de Recepciones (VDR) – Vista Paginada")
st.markdown("Cada página muestra hasta 10 recepciones. Navegue con botones, teclado o deslizando.")

components.html(carrusel_html, height=780, scrolling=False)

# ------------------------------------------------------------
# PANEL LATERAL CON CONTEO DE ESTATUS (basado en VDR únicas)
# ------------------------------------------------------------
with st.sidebar:
    st.header("ℹ️ Información")
    st.metric("Registros cargados (productos)", total)

    # Contar VDR únicas por estatus, no productos
    status_counts = df[['vdr', 'estatus']].drop_duplicates()['estatus'].value_counts()
    st.markdown("**Distribución por estatus (VDR únicas):**")
    num_status = len(status_counts)
    cols_per_row = 2
    rows = math.ceil(num_status / cols_per_row)
    for r in range(rows):
        cols = st.columns(cols_per_row)
        for c in range(cols_per_row):
            idx = r * cols_per_row + c
            if idx < num_status:
                status = status_counts.index[idx]
                count = status_counts.iloc[idx]
                cols[c].metric(label=status, value=count)
