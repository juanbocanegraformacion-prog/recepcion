import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import io
import requests
import json
import math

# ------------------------------------------------------------
# CONFIGURACIÓN DE PÁGINA
# ------------------------------------------------------------
st.set_page_config(page_title="Monitor VDR - RIOMARKET", layout="wide")

# ------------------------------------------------------------
# CARGA DE DATOS (desde Excel o de ejemplo)
# ------------------------------------------------------------
# En producción se usaría la URL real del archivo Excel en GitHub.
# Ejemplo: url = "https://raw.githubusercontent.com/tu_usuario/tu_repo/main/Reporte-Consolidado-Compras-Producto.xlsx"
# Aquí usamos un pequeño DataFrame de muestra con las columnas requeridas.
sample_data = [
    # Sucursal (A), VDR (B), Estatus (G), ODC (H), Tipo ODC (I), Producto (Q), Proveedor (AA), Esp. (AD), Rec. (AF)
    ["JUAN BAUTISTA ARISMENDI", "VDR-01-001-00014430", "Integrada", "ODC-01-001-00015743", "Parcial", "DETERGENTE EN POLVO FRAGANCIA CITRICA LAS LLAVES 900 GR", "ALIMENTOS POLAR COMERCIAL, C.A.", 50, 50],
    ["JUAN BAUTISTA ARISMENDI", "VDR-01-001-00014430", "Integrada", "ODC-01-001-00015743", "Parcial", "DETERGENTE EN POLVO FRAGANCIA BEBE LAS LLAVES 400GR", "ALIMENTOS POLAR COMERCIAL, C.A.", 36, 32],
    ["JUAN BAUTISTA ARISMENDI", "VDR-01-001-00014430", "Integrada", "ODC-01-001-00015743", "Parcial", "DETERGENTE EN POLVO FRAGANCIA BEBE LAS LLAVES 900GR", "ALIMENTOS POLAR COMERCIAL, C.A.", 10, 10],
    ["JUAN BAUTISTA ARISMENDI", "VDR-01-001-00014431", "Integrada", "ODC-01-001-00015805", "Parcial", "CERVEZA POLAR LIGHT RET 222ML", "CERVECERIA POLAR, C.A.", 540, 540],
    ["JUAN BAUTISTA ARISMENDI", "VDR-01-001-00014431", "Integrada", "ODC-01-001-00015805", "Parcial", "GAVERA DE CERVEZA POLAR", "CERVECERIA POLAR, C.A.", 15, 15],
    ["JUAN BAUTISTA ARISMENDI", "VDR-01-001-00014432", "Integrada", "ODC-01-001-00015798", "Parcial", "REFRESCO ZERO PEPSI 2L", "PEPSI-COLA VENEZUELA C.A.", 12, 12],
    ["JUAN BAUTISTA ARISMENDI", "VDR-01-001-00014432", "Integrada", "ODC-01-001-00015798", "Parcial", "REFRESCO SABOR PIÑA PET GOLDEN 2L", "PEPSI-COLA VENEZUELA C.A.", 30, 30],
    ["JUAN BAUTISTA ARISMENDI", "VDR-01-001-00014433", "Integrada", "ODC-01-001-00015798", "Parcial", "REFRESCO KOLITA GOLDEN 2 L", "PEPSI-COLA VENEZUELA C.A.", 54, 54],
    ["JUAN BAUTISTA ARISMENDI", "VDR-01-001-00014433", "Integrada", "ODC-01-001-00015798", "Parcial", "REFRESCO KOLITA GOLDEN 1.5 L", "PEPSI-COLA VENEZUELA C.A.", 60, 60],
    ["JUAN BAUTISTA ARISMENDI", "VDR-01-001-00014433", "Integrada", "ODC-01-001-00015798", "Parcial", "REFRESCO DE PIÑA GOLDEN 1.5 L", "PEPSI-COLA VENEZUELA C.A.", 60, 60],
    # Agregar más registros si se quiere probar más páginas
    ["JUAN BAUTISTA ARISMENDI", "VDR-01-001-00014434", "En validación", "ODC-01-001-00015799", "Total", "MORTADELA DE POLLO SUPERIOR HERMO 1 KG.", "INDUSTRIAS ALIMENTICIAS HERMO DE VENEZUELA S.A.", 20, 15],
    ["JUAN BAUTISTA ARISMENDI", "VDR-01-001-00014435", "Pendiente por validar", "ODC-01-005-00013785", "Parcial", "PAÑAL ACTIVESEC DISNEY TALLA XG HUGGIES 25 UND", "DIMASSI, C.A.", 24, 8],
    ["JUAN BAUTISTA ARISMENDI", "VDR-01-001-00014436", "Anulada", "ODC-01-016-00016341", "Parcial", "JAMON ESPALDA AHUMADA VISKING DELGADO ALIMEX 1.6 KG", "PRODUCTOS ALIMEX, C.A.", 21, 0],
]

# Convertir a estructura deseada
raw_columns = ["sucursal", "vdr", "estatus", "odc", "tipo_odc", "producto", "proveedor", "esperado", "recibido"]
df_r = pd.DataFrame(sample_data, columns=raw_columns)

# Asegurar tipos numéricos
df_r["esperado"] = pd.to_numeric(df_r["esperado"], errors="coerce").fillna(0).astype(int)
df_r["recibido"] = pd.to_numeric(df_r["recibido"], errors="coerce").fillna(0).astype(int)

vdr_data = df_r.to_dict(orient="records")

# ------------------------------------------------------------
# CONFIGURACIÓN DE PAGINACIÓN
# ------------------------------------------------------------
PAGE_SIZE = 10
total_items = len(vdr_data)
total_pages = max(1, math.ceil(total_items / PAGE_SIZE))

pages = []
for i in range(0, total_items, PAGE_SIZE):
    pages.append(vdr_data[i:i+PAGE_SIZE])

# ------------------------------------------------------------
# HTML/CSS/JS DEL CARRUSEL PAGINADO
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
            --card-border-radius: 12px;
            --shadow: 0 4px 12px rgba(0,0,0,0.1);
            --shadow-active: 0 0 20px rgba(46,125,50,0.4);
            --transition-speed: 0.4s;
            --page-width: 95%;
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
            padding: 20px;
        }}
        .carousel-wrapper {{
            position: relative;
            width: 100%;
            max-width: 700px;
            margin: 0 auto;
            display: flex;
            flex-direction: column;
            align-items: center;
        }}
        .carousel-viewport {{
            width: 100%;
            height: 700px;  /* altura suficiente para una página de 10 tarjetas */
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
            width: var(--page-width);
            display: flex;
            flex-direction: column;
            gap: 12px;
            align-items: stretch;
        }}
        .page-group.active {{
            box-shadow: var(--shadow-active);
            border: 2px solid var(--color-green);
            border-radius: var(--card-border-radius);
            padding: 10px;
            background: rgba(255,255,255,0.9);
            z-index: 2;
        }}
        .vdr-card {{
            background: var(--card-bg);
            border-radius: var(--card-border-radius);
            box-shadow: var(--shadow);
            padding: 16px;
            display: flex;
            flex-direction: column;
            gap: 6px;
        }}
        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .sucursal-vdr {{
            font-weight: 700;
            color: #1a1a1a;
        }}
        .status-badge {{
            display: inline-block;
            padding: 2px 10px;
            border-radius: 16px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            color: white;
        }}
        .status-badge.integrada {{ background: var(--color-green); }}
        .status-badge.en-validacion {{ background: var(--color-orange); }}
        .status-badge.pendiente-por-validar {{ background: var(--color-red); }}
        .status-badge.anulada {{ background: var(--color-gray); }}
        .status-badge.other {{ background: var(--color-gray); }}
        .producto {{ font-size: 0.95rem; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
        .odc-row, .proveedor-row {{ display: flex; align-items: center; gap: 6px; font-size: 0.8rem; color: #555; }}
        .progress-container {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin-top: 4px;
        }}
        .progress-bar-wrapper {{
            flex: 1;
            height: 6px;
            background: #e0e0e0;
            border-radius: 3px;
            overflow: hidden;
        }}
        .progress-fill {{
            height: 100%;
            background: var(--color-green);
            transition: width 0.3s;
            border-radius: 3px;
        }}
        .progress-fill.over {{ background: var(--color-blue); }}
        .progress-text {{
            font-family: var(--mono-font);
            font-size: 0.8rem;
            color: #333;
            white-space: nowrap;
        }}
        .nav-controls {{
            display: flex;
            gap: 12px;
            margin-top: 15px;
            align-items: center;
        }}
        .nav-btn {{
            background: #e0e0e0;
            border: none;
            border-radius: 50%;
            width: 36px;
            height: 36px;
            font-size: 1.2rem;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: background 0.2s;
        }}
        .nav-btn:hover {{ background: var(--color-green); color: white; }}
        .page-indicator {{
            font-size: 0.9rem;
            color: #333;
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
        <button class="nav-btn prev" id="prevBtn" aria-label="Página anterior" title="Anterior">▲</button>
        <div class="carousel-viewport" id="viewport">
            <div class="carousel-track" id="track"></div>
        </div>
        <button class="nav-btn next" id="nextBtn" aria-label="Página siguiente" title="Siguiente">▼</button>
        <div class="nav-controls">
            <span class="page-indicator" id="pageIndicator">Página 1 de {total_pages}</span>
        </div>
        <div aria-live="polite" id="announce" style="position:absolute;left:-9999px"></div>
    </div>

    <script>
        const pages = {json.dumps(pages)};
        const totalPages = pages.length;
        const PAGE_HEIGHT = 660; // altura estimada por página

        const track = document.getElementById('track');
        const viewport = document.getElementById('viewport');
        const prevBtn = document.getElementById('prevBtn');
        const nextBtn = document.getElementById('nextBtn');
        const pageIndicator = document.getElementById('pageIndicator');
        const announcer = document.getElementById('announce');

        let currentPageIndex = 0;
        let autoPlayTimer = null;
        let isPaused = false;

        function getStatusClass(estatus) {{
            const n = estatus.trim().toLowerCase().replace(/\\s+/g, '-');
            if (n === 'integrada') return 'integrada';
            if (n.includes('en-validacion')) return 'en-validacion';
            if (n.includes('pendiente-por-validar')) return 'pendiente-por-validar';
            if (n === 'anulada') return 'anulada';
            return 'other';
        }}

        function buildPageGroup(pageItems) {{
            // Construye el HTML interior de una página (colección de tarjetas)
            let html = '';
            pageItems.forEach(item => {{
                const progressPercent = Math.min(100, Math.round((item.recibido / (item.esperado || 1)) * 100));
                const over = item.recibido > item.esperado;
                html += `
                <div class="vdr-card">
                    <div class="card-header">
                        <span class="sucursal-vdr">${{item.sucursal}} · ${{item.vdr}}</span>
                        <span class="status-badge ${{getStatusClass(item.estatus)}}">${{item.estatus}}</span>
                    </div>
                    <div class="odc-row">
                        <span>📄 ODC:</span> ${{item.odc}} <span style="margin-left:10px;">Tipo: ${{item.tipo_odc}}</span>
                    </div>
                    <div class="producto" title="${{item.producto}}">${{item.producto.length > 45 ? item.producto.substring(0,45)+'...' : item.producto}}</div>
                    <div class="proveedor-row">
                        <span>🏭 Proveedor:</span> ${{item.proveedor}}
                    </div>
                    <div class="progress-container">
                        <div class="progress-bar-wrapper">
                            <div class="progress-fill${{over ? ' over' : ''}}" style="width: ${{progressPercent}}%;"></div>
                        </div>
                        <div class="progress-text">${{item.recibido}} / ${{item.esperado}} (${{progressPercent}}%)</div>
                    </div>
                </div>`;
            }});
            return html;
        }}

        function createTrack() {{
            if (totalPages === 0) {{
                viewport.innerHTML = '<div class="empty-state">No hay recepciones disponibles.</div>';
                prevBtn.style.display = 'none';
                nextBtn.style.display = 'none';
                return;
            }}
            if (totalPages === 1) {{
                const group = document.createElement('div');
                group.className = 'page-group active';
                group.style.top = '20px';
                group.innerHTML = buildPageGroup(pages[0]);
                track.innerHTML = '';
                track.appendChild(group);
                prevBtn.style.visibility = 'hidden';
                nextBtn.style.visibility = 'hidden';
                pageIndicator.textContent = `Página 1 de 1`;
                return;
            }}

            // Para loop infinito: clonar la última y primera página
            const lastClone = {{...pages[totalPages-1]}};
            const firstClone = {{...pages[0]}};
            const allPages = [lastClone, ...pages, firstClone];

            track.innerHTML = '';
            allPages.forEach((page, idx) => {{
                const group = document.createElement('div');
                group.className = 'page-group';
                if (idx === 1) group.classList.add('active');
                group.style.top = `${{(idx - 1) * PAGE_HEIGHT + 10}}px`;
                group.innerHTML = buildPageGroup(page);
                track.appendChild(group);
            }});

            currentPageIndex = 0;
            track.style.transform = 'translateY(0px)';
            pageIndicator.textContent = `Página 1 de ${{totalPages}}`;
        }}

        function updatePageIndicator() {{
            pageIndicator.textContent = `Página ${{currentPageIndex+1}} de ${{totalPages}}`;
            announcer.textContent = `Mostrando página ${{currentPageIndex+1}} de ${{totalPages}}`;
        }}

        function goToPage(index) {{
            if (totalPages <= 1) return;
            currentPageIndex = index;
            const offset = - (index + 1) * PAGE_HEIGHT;
            track.style.transition = 'transform 0.4s ease-in-out';
            track.style.transform = `translateY(${{offset}}px)`;
            updatePageIndicator();
            // Actualizar clase active
            const groups = track.querySelectorAll('.page-group');
            groups.forEach(g => g.classList.remove('active'));
            if (groups.length > index + 1) groups[index + 1].classList.add('active');
        }}

        function handleTransitionEnd() {{
            if (currentPageIndex === totalPages) {{ // más allá de la última
                track.style.transition = 'none';
                track.style.transform = `translateY(${{- (0 + 1) * PAGE_HEIGHT}}px)`;
                currentPageIndex = 0;
                updatePageIndicator();
                track.querySelectorAll('.page-group').forEach(g => g.classList.remove('active'));
                const groups = track.querySelectorAll('.page-group');
                if (groups.length > 1) groups[1].classList.add('active');
                track.offsetHeight;
                track.style.transition = 'transform 0.4s ease-in-out';
            }} else if (currentPageIndex === -1) {{
                track.style.transition = 'none';
                track.style.transform = `translateY(${{- (totalPages-1 + 1) * PAGE_HEIGHT}}px)`;
                currentPageIndex = totalPages - 1;
                updatePageIndicator();
                track.querySelectorAll('.page-group').forEach(g => g.classList.remove('active'));
                const groups = track.querySelectorAll('.page-group');
                if (groups.length > totalPages) groups[totalPages].classList.add('active');
                track.offsetHeight;
                track.style.transition = 'transform 0.4s ease-in-out';
            }}
        }}

        function next() {{
            if (totalPages <= 1) return;
            currentPageIndex++;
            if (currentPageIndex >= totalPages) currentPageIndex = totalPages;
            goToPage(currentPageIndex);
        }}

        function prev() {{
            if (totalPages <= 1) return;
            currentPageIndex--;
            if (currentPageIndex < 0) currentPageIndex = -1;
            goToPage(currentPageIndex);
        }}

        function startAutoPlay() {{
            stopAutoPlay();
            if (totalPages > 1) autoPlayTimer = setInterval(next, 10000);
        }}

        function stopAutoPlay() {{
            if (autoPlayTimer) clearInterval(autoPlayTimer);
        }}

        prevBtn.addEventListener('click', () => {{ prev(); stopAutoPlay(); startAutoPlay(); }});
        nextBtn.addEventListener('click', () => {{ next(); stopAutoPlay(); startAutoPlay(); }});

        viewport.addEventListener('mouseenter', stopAutoPlay);
        viewport.addEventListener('mouseleave', () => {{ if (!isPaused) startAutoPlay(); }});

        let touchStartY = 0;
        viewport.addEventListener('touchstart', e => {{
            touchStartY = e.touches[0].clientY;
            stopAutoPlay();
        }});
        viewport.addEventListener('touchend', e => {{
            if (!touchStartY) return;
            const diff = touchStartY - e.changedTouches[0].clientY;
            if (Math.abs(diff) > 40) {{
                if (diff > 0) next();
                else prev();
            }}
            startAutoPlay();
            touchStartY = 0;
        }});

        window.addEventListener('keydown', e => {{
            if (e.key === 'ArrowDown') {{ e.preventDefault(); next(); stopAutoPlay(); startAutoPlay(); }}
            else if (e.key === 'ArrowUp') {{ e.preventDefault(); prev(); stopAutoPlay(); startAutoPlay(); }}
        }});

        track.addEventListener('transitionend', handleTransitionEnd);

        createTrack();
        startAutoPlay();

        window.addEventListener('beforeunload', stopAutoPlay);
    </script>
</body>
</html>
"""

# ------------------------------------------------------------
# INTERFAZ STREAMLIT
# ------------------------------------------------------------
st.title("📦 Monitor de Recepciones (VDR) – Vista Paginada")
st.markdown("Cada página muestra hasta 10 recepciones. Navegue verticalmente entre páginas.")

components.html(carrusel_html, height=780, scrolling=False)

# Panel lateral
with st.sidebar:
    st.header("ℹ️ Información")
    st.write(f"Total de registros: {total_items}")
    st.write(f"Tamaño de página: {PAGE_SIZE} (total páginas: {total_pages})")
    st.write("Datos de muestra. En producción se cargaría el Excel del repositorio GitHub.")
