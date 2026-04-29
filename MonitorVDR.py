import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import json
import os

# Configuración de página
st.set_page_config(page_title="Monitor VDR - RIOMARKET", layout="wide")

# ------------------------------------------------------------
# CARGA DE DATOS (CORRECCIÓN DE CODIFICACIÓN)
# ------------------------------------------------------------
@st.cache_data
def load_data():
    file_path = "Reporte-Consolidado-Compras-Producto+29-04-2026_29-04-2026.xlsx"
    
    if not os.path.exists(file_path):
        archivos_en_directorio = os.listdir('.')
        st.error(f"Archivo no encontrado: {file_path}")
        st.write("Archivos en raíz:", archivos_en_directorio)
        return pd.DataFrame()
    
    try:
        # Se añade 'encoding' para soportar caracteres especiales (N°, tildes, etc.)
        # 'latin-1' suele ser la solución para archivos exportados de Excel
        df = pd.read_csv(file_path, skiprows=1, encoding='latin-1')
        
        # Mapeo de columnas según el esquema del archivo
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
    except UnicodeDecodeError:
        # Fallback en caso de que latin-1 no funcione, probar con ISO-8859-1
        return pd.read_csv(file_path, skiprows=1, encoding='ISO-8859-1')
    except Exception as e:
        st.error(f"Error al procesar el archivo: {e}")
        return pd.DataFrame()

df_data = load_data()

# ------------------------------------------------------------
# COMPONENTE VISUAL
# ------------------------------------------------------------
if not df_data.empty:
    registros_por_pagina = 10
    total_paginas = (len(df_data) // registros_por_pagina) + (1 if len(df_data) % registros_por_pagina > 0 else 0)
    
    with st.sidebar:
        st.header("📊 Filtros")
        pagina = st.number_input(f"Página (1-{total_paginas})", min_value=1, max_value=total_paginas, value=1)
        st.divider()
        st.caption("Usa las flechas ⬆️⬇️ del teclado para navegar.")

    start_row = (pagina - 1) * registros_por_pagina
    subset = df_data.iloc[start_row : start_row + registros_por_pagina]
    vdr_json = subset.to_dict(orient="records")

    carrusel_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: 'Segoe UI', sans-serif; background: #f4f7f9; display: flex; justify-content: center; overflow: hidden; }}
            .container {{ display: flex; flex-direction: column; align-items: center; height: 100vh; justify-content: center; width: 100%; }}
            .card {{
                width: 550px; background: white; border-radius: 15px; padding: 25px;
                margin: 15px 0; transition: all 0.5s ease;
                box-shadow: 0 4px 6px rgba(0,0,0,0.05);
                opacity: 0.2; transform: scale(0.8);
            }}
            .active {{
                opacity: 1; transform: scale(1.1);
                border-left: 12px solid #1B5E20;
                box-shadow: 0 15px 35px rgba(0,0,0,0.1);
                z-index: 100;
            }}
            .status {{ background: #E8F5E9; color: #2E7D32; padding: 5px 12px; border-radius: 20px; font-size: 12px; font-weight: bold; }}
            .progress-bg {{ background: #eee; height: 10px; border-radius: 5px; margin: 15px 0; }}
            .progress-fill {{ background: #2E7D32; height: 100%; border-radius: 5px; transition: width 0.6s; }}
            .title {{ font-size: 18px; font-weight: bold; margin: 10px 0; color: #111; }}
        </style>
    </head>
    <body>
        <div class="container" id="display"></div>
        <script>
            const items = {json.dumps(vdr_json)};
            let index = 0;

            function update() {{
                const display = document.getElementById('display');
                display.innerHTML = '';
                
                [-1, 0, 1].forEach(pos => {{
                    const i = index + pos;
                    if (i >= 0 && i < items.length) {{
                        const data = items[i];
                        const progress = Math.min(100, (data.recibido / (data.esperado || 1)) * 100);
                        const card = document.createElement('div');
                        card.className = `card ${{pos === 0 ? 'active' : ''}}`;
                        card.innerHTML = `
                            <div style="display:flex; justify-content:space-between; align-items:center;">
                                <span style="font-size:12px; color:#777;">${{data.sucursal}}</span>
                                <span class="status">${{data.estatus}}</span>
                            </div>
                            <div class="title">${{data.producto}}</div>
                            <div style="display:grid; grid-template-columns: 1fr 1fr; gap: 5px; font-size: 13px;">
                                <div><b>VDR:</b> ${{data.vdr}}</div>
                                <div><b>PROVEEDOR:</b> ${{data.proveedor}}</div>
                            </div>
                            <div class="progress-bg"><div class="progress-fill" style="width:${{progress}}%"></div></div>
                            <div style="display:flex; justify-content:space-between; font-size:12px;">
                                <span>Esperado: ${{data.esperado}}</span>
                                <span>Recibido: ${{data.recibido}}</span>
                            </div>
                        `;
                        display.appendChild(card);
                    }}
                }});
            }}

            window.onkeydown = (e) => {{
                if (e.key === "ArrowDown" && index < items.length - 1) index++;
                if (e.key === "ArrowUp" && index > 0) index--;
                update();
            }};
            update();
        </script>
    </body>
    </html>
    """
    
    st.title("📦 Monitor de Recepciones VDR")
    components.html(carrusel_html, height=800)
