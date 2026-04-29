import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import json
import os

# Configuración de página
st.set_page_config(page_title="Monitor VDR - RIOMARKET", layout="wide")

# ------------------------------------------------------------
# CARGA DE DATOS (SOLUCIÓN AL ERROR DE TOKENIZACIÓN)
# ------------------------------------------------------------
@st.cache_data
def load_data():
    file_path = "Reporte-Consolidado-Compras-Producto.xlsx - Sheet1.csv"
    
    if not os.path.exists(file_path):
        return pd.DataFrame()
    
    try:
        # 1. Leemos el archivo saltando la primera fila de etiquetas generales
        # 2. Usamos 'on_bad_lines' para ignorar filas corruptas si existen
        # 3. 'engine=python' es más lento pero mucho más robusto para errores de tokens
        df = pd.read_csv(
            file_path, 
            skiprows=1, 
            encoding='latin-1', 
            sep=',', 
            engine='python',
            on_bad_lines='skip' 
        )
        
        # Mapeo de columnas según el esquema detectado
        # Nota: Usamos nombres de columnas si es posible, o iloc si los nombres fallan
        df_vdr = pd.DataFrame({
            "sucursal": df.iloc[:, 0],
            "vdr": df.iloc[:, 1],
            "estatus": df.iloc[:, 6],
            "odc": df.iloc[:, 7],
            "tipo_odc": df.iloc[:, 8],
            "producto": df.iloc[:, 16],
            "proveedor": df.iloc[:, 26],
            "esperado": pd.to_numeric(df.iloc[:, 27], errors='coerce').fillna(0), # Empaques Esperados
            "recibido": pd.to_numeric(df.iloc[:, 29], errors='coerce').fillna(0)  # Empaques Recibidos
        })
        return df_vdr
    except Exception as e:
        st.error(f"Error crítico al leer el CSV: {e}")
        return pd.DataFrame()

df_data = load_data()

# ------------------------------------------------------------
# COMPONENTE VISUAL DEL MONITOR
# ------------------------------------------------------------
if not df_data.empty:
    registros_por_pagina = 10
    total_paginas = (len(df_data) // registros_por_pagina) + (1 if len(df_data) % registros_por_pagina > 0 else 0)
    
    with st.sidebar:
        st.header("📊 Control")
        pagina = st.number_input(f"Página", min_value=1, max_value=total_paginas, value=1)
        st.info("Navega el carrusel con las flechas ⬆️⬇️")

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
                margin: 15px 0; transition: all 0.4s ease;
                box-shadow: 0 4px 6px rgba(0,0,0,0.05);
                opacity: 0.2; transform: scale(0.8);
            }}
            .active {{
                opacity: 1; transform: scale(1.1);
                border-left: 12px solid #1B5E20;
                box-shadow: 0 15px 35px rgba(0,0,0,0.1);
                z-index: 100;
            }}
            .progress-bg {{ background: #eee; height: 10px; border-radius: 5px; margin: 15px 0; }}
            .progress-fill {{ background: #2E7D32; height: 100%; border-radius: 5px; transition: width 0.6s; }}
            .title {{ font-size: 16px; font-weight: bold; margin: 10px 0; color: #111; }}
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
                        const d = items[i];
                        const progress = Math.min(100, (d.recibido / (d.esperado || 1)) * 100);
                        const card = document.createElement('div');
                        card.className = `card ${{pos === 0 ? 'active' : ''}}`;
                        card.innerHTML = `
                            <div style="display:flex; justify-content:space-between; font-size:11px; color:#777;">
                                <span>${{d.sucursal}}</span>
                                <b>${{d.estatus}}</b>
                            </div>
                            <div class="title">${{d.producto}}</div>
                            <div style="font-size:12px; color:#444;">
                                <b>VDR:</b> ${{d.vdr}} | <b>ODC:</b> ${{d.odc}}<br>
                                <b>PROVEEDOR:</b> ${{d.proveedor}}
                            </div>
                            <div class="progress-bg"><div class="progress-fill" style="width:${{progress}}%"></div></div>
                            <div style="display:flex; justify-content:space-between; font-size:11px;">
                                <span>Esperado: ${{d.esperado}}</span>
                                <span>Recibido: ${{d.recibido}}</span>
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
    st.title("📦 Monitor VDR")
    components.html(carrusel_html, height=800)
