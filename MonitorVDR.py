import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import json

# CONFIGURACIÓN
st.set_page_config(page_title="Monitor VDR - RIOMARKET", layout="wide")

def load_data():
    # En producción, usa pd.read_csv("tu_archivo.csv")
    # Para este ejemplo, simulamos la lectura de las columnas A, B, G, H, I, Q, AA, AD, AF
    try:
        df = pd.read_csv("Reporte-Consolidado-Compras-Producto.xlsx - Sheet1.csv")
        # Renombrar según tu requerimiento de columnas
        df_mapped = pd.DataFrame({
            "sucursal": df.iloc[:, 0],    # A
            "vdr": df.iloc[:, 1],         # B
            "estatus": df.iloc[:, 6],     # G
            "odc": df.iloc[:, 7],         # H
            "tipo_odc": df.iloc[:, 8],    # I
            "producto": df.iloc[:, 16],   # Q
            "proveedor": df.iloc[:, 26],  # AA
            "esperado": pd.to_numeric(df.iloc[:, 29], errors='coerce').fillna(0), # AD
            "recibido": pd.to_numeric(df.iloc[:, 31], errors='coerce').fillna(0)  # AF
        })
        return df_mapped
    except Exception as e:
        st.error(f"Error al cargar archivo: {e}")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    # PAGINACIÓN DE 10 EN 10
    total_registros = len(df)
    paginas = (total_registros // 10) + (1 if total_registros % 10 > 0 else 0)
    
    st.sidebar.header("Control de Navegación")
    page_number = st.sidebar.number_input(f"Página (1 de {paginas})", min_value=1, max_value=paginas, step=1)
    
    start_idx = (page_number - 1) * 10
    end_idx = start_idx + 10
    subset_df = df.iloc[start_idx:end_idx]

    # Preparar JSON para el Carrusel
    vdr_list = subset_df.to_dict(orient="records")

    # HTML/JS CORREGIDO (Lógica de visualización vertical)
    carrusel_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            :root {{
                --primary: #2E7D32; --bg: #f8f9fa;
            }}
            body {{ font-family: sans-serif; background: var(--bg); }}
            .vdr-card {{
                background: white; border-radius: 10px; padding: 20px;
                margin-bottom: 20px; border: 1px solid #ddd;
                transition: all 0.3s; opacity: 0.5; transform: scale(0.9);
            }}
            .active {{ opacity: 1; transform: scale(1); border: 2px solid var(--primary); box-shadow: 0 4px 15px rgba(0,0,0,0.2); }}
            .progress-bar {{ background: #eee; border-radius: 5px; height: 10px; margin: 10px 0; }}
            .progress-fill {{ background: var(--primary); height: 100%; border-radius: 5px; }}
            .info-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 0.8em; color: #555; }}
        </style>
    </head>
    <body>
        <div id="container"></div>
        <script>
            const data = {json.dumps(vdr_list)};
            const container = document.getElementById('container');
            
            function render() {{
                container.innerHTML = data.map((item, idx) => `
                    <div class="vdr-card ${{idx === 1 ? 'active' : ''}}">
                        <div style="font-weight:bold; color:var(--primary)">${{item.sucursal}} | VDR: ${{item.vdr}}</div>
                        <div style="margin: 5px 0; font-size: 0.9em;">${{item.producto}}</div>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: ${{Math.min(100, (item.recibido/item.esperado)*100)}}%"></div>
                        </div>
                        <div class="info-grid">
                            <div>ODC: ${{item.odc}} (${{item.tipo_odc}})</div>
                            <div>Proveedor: ${{item.proveedor}}</div>
                            <div>Esperado: ${{item.esperado}}</div>
                            <div>Recibido: ${{item.recibido}}</div>
                        </div>
                        <div style="margin-top:10px; font-weight:bold">Estado: ${{item.estatus}}</div>
                    </div>
                `).join('');
            }}
            render();
        </script>
    </body>
    </html>
    """
    
    st.title("📦 Monitor de Recepciones (VDR)")
    components.html(carrusel_html, height=800)
else:
    st.warning("No se encontraron datos para mostrar.")
