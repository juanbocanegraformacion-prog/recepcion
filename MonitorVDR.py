import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import json

# Configuración de página
st.set_page_config(page_title="Monitor VDR - RIOMARKET", layout="wide")

# ------------------------------------------------------------
# CARGA DE DATOS DESDE GITHUB (CORRECCIÓN DE ERROR)
# ------------------------------------------------------------
@st.cache_data
def load_data_from_github():
    # URL RAW correcta del archivo CSV en GitHub
    url_csv = "https://raw.githubusercontent.com/juanbocanegraformacion-prog/recepcion/main/Reporte-Consolidado-Compras-Producto.xlsx%20-%20Sheet1.csv"
    
    try:
        # Se lee el CSV directamente desde la URL
        df = pd.read_csv(url_csv)
        
        # Mapeo de columnas solicitado (basado en índices de letra a número)
        # A=0, B=1, G=6, H=7, I=8, Q=16, AA=26, AD=29, AF=31
        df_vdr = pd.DataFrame({
            "sucursal": df.iloc[:, 0],
            "vdr": df.iloc[:, 1],
            "estatus": df.iloc[:, 6],
            "odc": df.iloc[:, 7],
            "tipo_odc": df.iloc[:, 8],
            "producto": df.iloc[:, 16],
            "proveedor": df.iloc[:, 26],
            "esperado": pd.to_numeric(df.iloc[:, 29], errors='coerce').fillna(0),
            "recibido": pd.to_numeric(df.iloc[:, 31], errors='coerce').fillna(0)
        })
        return df_vdr
    except Exception as e:
        st.error(f"Error al conectar con GitHub o procesar el archivo: {e}")
        return pd.DataFrame()

df_data = load_data_from_github()

# ------------------------------------------------------------
# LÓGICA DE PAGINACIÓN Y PREPARACIÓN DE JSON
# ------------------------------------------------------------
if not df_data.empty:
    registros_por_pagina = 10
    total_paginas = (len(df_data) // registros_por_pagina) + 1
    
    with st.sidebar:
        st.header("Navegación")
        pagina = st.number_input("Página", min_value=1, max_value=total_paginas, value=1)
        st.info(f"Mostrando registros del {(pagina-1)*10} al {pagina*10}")

    # Filtrar 10 registros
    start_row = (pagina - 1) * registros_por_pagina
    subset = df_data.iloc[start_row : start_row + registros_por_pagina]
    vdr_json = subset.to_dict(orient="records")

    # ------------------------------------------------------------
    # HTML / CSS / JS PARA EL CARRUSEL "PASADO-ACTUAL-FUTURO"
    # ------------------------------------------------------------
    carrusel_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: 'Segoe UI', sans-serif; background: #f0f2f6; overflow: hidden; }}
            .container {{ display: flex; flex-direction: column; align-items: center; height: 100vh; justify-content: center; }}
            .vdr-card {{
                width: 500px; background: white; border-radius: 12px; padding: 20px;
                margin: 10px 0; transition: all 0.4s ease;
                box-shadow: 0 2px 5px rgba(0,0,0,0.05);
                opacity: 0.4; transform: scale(0.85);
            }}
            .active {{
                opacity: 1; transform: scale(1.05);
                border-left: 8px solid #2E7D32;
                box-shadow: 0 10px 25px rgba(0,0,0,0.1);
                z-index: 10;
            }}
            .badge {{ background: #2E7D32; color: white; padding: 4px 8px; border-radius: 4px; font-size: 11px; }}
            .progress-bg {{ background: #eee; height: 8px; border-radius: 4px; margin: 10px 0; }}
            .progress-fill {{ background: #2E7D32; height: 100%; border-radius: 4px; }}
            .label {{ font-size: 12px; color: #666; }}
            .value {{ font-family: monospace; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="container" id="carousel"></div>
        <script>
            const data = {json.dumps(vdr_json)};
            let currentIdx = 0;

            function render() {{
                const container = document.getElementById('carousel');
                container.innerHTML = '';
                
                // Mostrar anterior, actual y siguiente
                [-1, 0, 1].forEach(offset => {{
                    const idx = currentIdx + offset;
                    if (idx >= 0 && idx < data.length) {{
                        const item = data[idx];
                        const pct = Math.min(100, (item.recibido / (item.esperado || 1)) * 100);
                        const card = document.createElement('div');
                        card.className = `vdr-card ${{offset === 0 ? 'active' : ''}}`;
                        card.innerHTML = `
                            <div style="display:flex; justify-content:space-between">
                                <span class="badge">${{item.estatus}}</span>
                                <span class="label">VDR: <span class="value">${{item.vdr}}</span></span>
                            </div>
                            <h4 style="margin:10px 0">${{item.producto}}</h4>
                            <div class="label">Proveedor: ${{item.proveedor}}</div>
                            <div class="progress-bg"><div class="progress-fill" style="width:${{pct}}%"></div></div>
                            <div style="display:flex; justify-content:space-between; font-size:12px">
                                <span>Esperado: ${{item.esperado}}</span>
                                <span>Recibido: ${{item.recibido}}</span>
                            </div>
                        `;
                        container.appendChild(card);
                    }
                }});
            }}

            window.addEventListener('keydown', (e) => {{
                if (e.key === "ArrowDown" && currentIdx < data.length - 1) currentIdx++;
                if (e.key === "ArrowUp" && currentIdx > 0) currentIdx--;
                render();
            }});

            render();
        </script>
    </body>
    </html>
    """
    
    st.title("📦 Monitor de Recepciones (VDR)")
    components.html(carrusel_html, height=700)

else:
    st.info("Cargando datos o archivo no encontrado.")
