import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import json
import os

# ------------------------------------------------------------
# CONFIGURACIÓN DE PÁGINA
# ------------------------------------------------------------
st.set_page_config(page_title="Monitor VDR - RIOMARKET", layout="wide")

# ------------------------------------------------------------
# CARGA Y PROCESAMIENTO DE DATOS
# ------------------------------------------------------------
@st.cache_data(ttl=600) # Caché de 10 minutos
def load_data_from_github():
    # URL RAW corregida (sustituyendo /blob/ por /raw/ y quitando el '+' si es necesario)
    url = "https://raw.githubusercontent.com/juanbocanegraformacion-prog/recepcion/main/Reporte-Consolidado-Compras-Producto%2B29-04-2026_29-04-2026.xlsx"
    
    # Nota: Si el archivo en GitHub termina en .xlsx pero es un CSV, usamos read_csv.
    # Si es un Excel real, usamos read_excel. Según tus errores previos, es un CSV con encoding latin-1.
    try:
        # Intentamos leer como CSV (basado en tus interacciones previas)
        df = pd.read_csv(url, skiprows=1, encoding='latin-1', on_bad_lines='skip', engine='python')
        
        # Mapeo según tus especificaciones de columnas (A=0, B=1, G=6...)
        df_vdr = pd.DataFrame({
            "sucursal": df.iloc[:, 0],    # Columna A
            "vdr": df.iloc[:, 1],         # Columna B
            "estatus": df.iloc[:, 6],     # Columna G
            "odc": df.iloc[:, 7],         # Columna H
            "tipo_odc": df.iloc[:, 8],    # Columna I
            "producto": df.iloc[:, 16],   # Columna Q
            "proveedor": df.iloc[:, 26],  # Columna AA
            "esperado": pd.to_numeric(df.iloc[:, 29], errors='coerce').fillna(0), # Columna AD
            "recibido": pd.to_numeric(df.iloc[:, 31], errors='coerce').fillna(0)  # Columna AF
        })
        return df_vdr.dropna(subset=['vdr']) # Limpiar filas vacías
    except Exception as e:
        st.error(f"Error al conectar con GitHub: {e}")
        # Retorno de datos de respaldo en caso de error de conexión
        return pd.DataFrame([
            {"sucursal": "Sede Central", "vdr": "VDR-001", "estatus": "Integrada", "odc": "ODC-100", "tipo_odc": "Total", "producto": "PRODUCTO DE PRUEBA", "proveedor": "PROVEEDOR S.A", "esperado": 100, "recibido": 80}
        ])

df_raw = load_data_from_github()

# ------------------------------------------------------------
# LOGICA DE PAGINACIÓN (10 en 10)
# ------------------------------------------------------------
items_per_page = 10
total_pages = max(1, len(df_raw) // items_per_page + (1 if len(df_raw) % items_per_page > 0 else 0))

with st.sidebar:
    st.header("📊 Control de Monitor")
    page = st.number_input("Página", min_value=1, max_value=total_pages, value=1)
    st.divider()
    st.info("El monitor muestra la recepción previa, la actual (centro) y la siguiente.")

# Filtrar datos de la página actual
start_idx = (page - 1) * items_per_page
df_page = df_raw.iloc[start_idx : start_idx + items_per_page]
vdr_json = df_page.to_dict(orient="records")

# ------------------------------------------------------------
# DISEÑO DEL CARRUSEL (HTML/JS/CSS)
# ------------------------------------------------------------
carrusel_html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ 
            font-family: 'Segoe UI', Tahoma, sans-serif; 
            background: #f0f2f6; 
            margin: 0; 
            display: flex; 
            justify-content: center; 
            overflow: hidden; 
        }}
        .monitor-container {{
            display: flex;
            flex-direction: column;
            align-items: center;
            height: 100vh;
            width: 100%;
            justify-content: center;
        }}
        .vdr-card {{
            width: 600px;
            background: white;
            border-radius: 12px;
            padding: 20px;
            margin: 10px 0;
            transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            opacity: 0.4;
            transform: scale(0.85);
            border-left: 5px solid #ccc;
        }}
        .active {{
            opacity: 1;
            transform: scale(1.05);
            box-shadow: 0 10px 25px rgba(0,0,0,0.2);
            border-left: 15px solid #2E7D32;
            z-index: 10;
        }}
        .header-row {{ display: flex; justify-content: space-between; font-size: 12px; color: #666; font-weight: bold; }}
        .status-tag {{ 
            padding: 4px 10px; border-radius: 15px; font-size: 11px; 
            background: #e8f5e9; color: #2e7d32; text-transform: uppercase;
        }}
        .prod-name {{ font-size: 18px; font-weight: bold; margin: 10px 0; color: #1a1a1a; }}
        .data-grid {{ 
            display: grid; grid-template-columns: 1fr 1fr; gap: 10px; 
            font-size: 13px; color: #444; border-top: 1px solid #eee; padding-top: 10px;
        }}
        .progress-container {{ background: #eee; height: 12px; border-radius: 6px; margin-top: 15px; overflow: hidden; }}
        .progress-bar {{ background: #2E7D32; height: 100%; transition: width 0.8s ease; }}
    </style>
</head>
<body>
    <div class="monitor-container" id="monitor"></div>

    <script>
        const data = {json.dumps(vdr_json)};
        let currentIndex = 0;

        function render() {{
            const container = document.getElementById('monitor');
            container.innerHTML = '';

            // Mostrar 3 tarjetas: anterior, actual, siguiente
            [-1, 0, 1].forEach(offset => {{
                const idx = currentIndex + offset;
                if (idx >= 0 && idx < data.length) {{
                    const item = data[idx];
                    const percent = Math.min(100, (item.recibido / (item.esperado || 1)) * 100);
                    
                    const card = document.createElement('div');
                    card.className = `vdr-card ${{offset === 0 ? 'active' : ''}}`;
                    card.innerHTML = `
                        <div class="header-row">
                            <span>${{item.sucursal}}</span>
                            <span class="status-tag">${{item.estatus}}</span>
                        </div>
                        <div class="prod-name">${{item.producto}}</div>
                        <div class="data-grid">
                            <div><b>VDR:</b> ${{item.vdr}}</div>
                            <div><b>ODC:</b> ${{item.odc}} (${{item.tipo_odc}})</div>
                            <div><b>PROVEEDOR:</b> ${{item.proveedor}}</div>
                            <div><b>CANTIDADES:</b> ${{item.recibido}} / ${{item.esperado}}</div>
                        </div>
                        <div class="progress-container">
                            <div class="progress-bar" style="width: ${{percent}}%"></div>
                        </div>
                    `;
                    container.appendChild(card);
                }}
            }});
        }}

        // Control por teclado
        window.onkeydown = (e) => {{
            if (e.key === "ArrowDown" && currentIndex < data.length - 1) currentIndex++;
            if (e.key === "ArrowUp" && currentIndex > 0) currentIndex--;
            render();
        }};

        render();
    </script>
</body>
</html>
"""

# Renderizar Monitor
st.title("📦 Monitor de Recepciones Logísticas")
components.html(carrusel_html, height=700)

# Sugerencias adicionales de visualización
with st.expander("💡 Sugerencias de visualización para estos datos"):
    st.markdown("""
    1. **Alertas de Diferencia:** Podríamos resaltar en rojo las tarjetas donde la `cantidad recibida` sea menor al 90% de la `esperada`.
    2. **Filtro por Estatus:** Añadir un multiselect en el sidebar para ver solo las "Pendientes" o "En Validación".
    3. **Auto-Scroll:** Implementar un temporizador (ej. cada 10 segundos) para que el monitor avance solo sin intervención del usuario.
    4. **KPIs de Página:** Mostrar el total de unidades esperadas vs recibidas de los 10 productos en pantalla.
    """)
