import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import json
import os

# Configuración de página
st.set_page_config(page_title="Monitor VDR - RIOMARKET", layout="wide")

# ------------------------------------------------------------
# CARGA DE DATOS (LECTURA LOCAL EN GITHUB)
# ------------------------------------------------------------
@st.cache_data
def load_data():
    # Nombre exacto del archivo que está junto al script
    file_path = "Reporte-Consolidado-Compras-Producto+29-04-2026_29-04-2026.xlsx"
    
    if not os.path.exists(file_path):
        st.error(f"No se encontró el archivo: {file_path}")
        return pd.DataFrame()
    
    try:
        df = pd.read_csv(file_path)
        
        # Mapeo de columnas solicitado:
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
        st.error(f"Error al procesar el archivo: {e}")
        return pd.DataFrame()

df_data = load_data()

# ------------------------------------------------------------
# LÓGICA DE PAGINACIÓN (10 en 10)
# ------------------------------------------------------------
if not df_data.empty:
    registros_por_pagina = 10
    total_paginas = (len(df_data) // registros_por_pagina) + (1 if len(df_data) % registros_por_pagina > 0 else 0)
    
    with st.sidebar:
        st.header("🏢 Control de Monitor")
        pagina = st.number_input(f"Página (1-{total_paginas})", min_value=1, max_value=total_paginas, value=1)
        st.markdown("---")
        st.write("**Instrucciones:**")
        st.caption("Usa las flechas ⬆️⬇️ del teclado para navegar entre las recepciones de esta página.")

    # Filtrar el bloque de 10
    start_row = (pagina - 1) * registros_por_pagina
    subset = df_data.iloc[start_row : start_row + registros_por_pagina]
    vdr_json = subset.to_dict(orient="records")

    # ------------------------------------------------------------
    # HTML / JS CON LLAVES ESCAPADAS (SOLUCIÓN AL SYNTAX ERROR)
    # ------------------------------------------------------------
    # NOTA: Usamos {{ }} para CSS/JS y { } para variables Python
    carrusel_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: 'Segoe UI', sans-serif; background: #f0f2f6; overflow: hidden; display: flex; justify-content: center; }}
            .container {{ display: flex; flex-direction: column; align-items: center; height: 100vh; justify-content: center; width: 100%; }}
            .vdr-card {{
                width: 80%; max-width: 600px; background: white; border-radius: 12px; padding: 20px;
                margin: 10px 0; transition: all 0.4s ease;
                box-shadow: 0 2px 5px rgba(0,0,0,0.05);
                opacity: 0.3; transform: scale(0.8);
            }}
            .active {{
                opacity: 1; transform: scale(1.05);
                border-left: 10px solid #2E7D32;
                box-shadow: 0 10px 25px rgba(0,0,0,0.15);
                z-index: 10;
            }}
            .badge {{ background: #2E7D32; color: white; padding: 4px 10px; border-radius: 20px; font-size: 11px; text-transform: uppercase; }}
            .progress-bg {{ background: #eee; height: 12px; border-radius: 6px; margin: 15px 0; overflow: hidden; }}
            .progress-fill {{ background: #2E7D32; height: 100%; transition: width 0.5s; }}
            .label {{ font-size: 12px; color: #666; font-weight: 600; }}
            .value {{ font-family: 'Courier New', monospace; font-weight: bold; color: #333; }}
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
                
                // Lógica de 3 tarjetas: Anterior (-1), Actual (0), Siguiente (1)
                [-1, 0, 1].forEach(offset => {{
                    const idx = currentIdx + offset;
                    if (idx >= 0 && idx < data.length) {{
                        const item = data[idx];
                        const pct = Math.min(100, (item.recibido / (item.esperado || 1)) * 100);
                        const card = document.createElement('div');
                        card.className = `vdr-card ${{offset === 0 ? 'active' : ''}}`;
                        card.innerHTML = `
                            <div style="display:flex; justify-content:space-between; align-items:center;">
                                <span class="label">SUCURSAL: <span class="value">${{item.sucursal}}</span></span>
                                <span class="badge">${{item.estatus}}</span>
                            </div>
                            <h3 style="margin:15px 0; color:#1a1a1a;">${{item.producto}}</h3>
                            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:10px;">
                                <div class="label">VDR: <span class="value">${{item.vdr}}</span></div>
                                <div class="label">ODC: <span class="value">${{item.odc}}</span></div>
                                <div class="label">TIPO: <span class="value">${{item.tipo_odc}}</span></div>
                                <div class="label">PROVEEDOR: <span class="value">${{item.proveedor}}</span></div>
                            </div>
                            <div class="progress-bg"><div class="progress-fill" style="width:${{pct}}%"></div></div>
                            <div style="display:flex; justify-content:space-between; font-size:13px">
                                <span>Esperado: <b>${{item.esperado}}</b></span>
                                <span>Recibido: <b>${{item.recibido}}</b></span>
                            </div>
                        `;
                        container.appendChild(card);
                    }}
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
    
    st.title("📦 Monitor de Recepciones (VDR) - RIOMARKET")
    components.html(carrusel_html, height=750)

else:
    st.warning("No se pudo cargar la información. Verifica que el archivo CSV esté en la raíz del repositorio.")
