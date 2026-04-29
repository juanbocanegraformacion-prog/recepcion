import streamlit as st
import pandas as pd

# ------------------------------------------------------------
# 1. CARGA Y PREPARACIÓN DE DATOS (Basado en tu archivo)
# ------------------------------------------------------------
def load_data():
    # Cargamos omitiendo la primera fila de metadatos si es necesario
    df = pd.read_csv('Reporte-Consolidado-Compras-Producto.xlsx - Sheet1.csv', skiprows=1)
    
    # Mapeo exacto según tu solicitud (Letras Excel -> Nombres de Columna)
    mapping = {
        'Producto': 'Producto',               # Col Q
        'Esperada': 'Empaques Esperados',     # Col AB
        'Recibida': 'Empaques Recibidos',    # Col AD
        'Estatus': 'Estatus compra (VDR)',    # Col G
        'ODC': 'Número de orden de compra',   # Col H
        'Proveedor': 'Proveedor de compra'     # Col Y
    }
    return df[list(mapping.values())].rename(columns={v: k for k, v in mapping.items()})

# ------------------------------------------------------------
# 2. ESTILOS CSS PARA JERARQUÍA VISUAL
# ------------------------------------------------------------
st.markdown("""
<style>
    .vdr-container { display: flex; flex-direction: column; align-items: center; gap: 15px; }
    
    .vdr-card {
        background: white; border-radius: 15px; padding: 20px; width: 100%;
        transition: all 0.4s ease; border-left: 8px solid #ddd;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }

    /* Recepción Actual (En Foco) */
    .vdr-active {
        transform: scale(1.05); opacity: 1;
        border-left: 8px solid #2E7D32;
        box-shadow: 0 10px 25px rgba(0,0,0,0.15);
        z-index: 2;
    }

    /* Recepciones Adyacentes (Anterior/Siguiente) */
    .vdr-dim { opacity: 0.4; transform: scale(0.9); filter: blur(1px); }

    .status-badge {
        padding: 4px 12px; border-radius: 20px; font-size: 0.8rem;
        font-weight: bold; text-transform: uppercase;
    }
    
    .progress-container {
        background: #f0f0f0; border-radius: 10px; height: 8px; margin-top: 10px;
    }
    .progress-bar { height: 100%; border-radius: 10px; transition: width 0.5s; }
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------
# 3. LÓGICA DEL COMPONENTE
# ------------------------------------------------------------
df_vdr = load_data()

if 'vdr_idx' not in st.session_state:
    st.session_state.vdr_idx = 0

def render_card(row, mode="dim"):
    # Cálculo de eficiencia
    perc = min(100, int((row['Recibida'] / row['Esperada']) * 100)) if row['Esperada'] > 0 else 0
    
    # Semáforo de color
    color = "#2E7D32" if perc >= 100 else ("#FFA000" if perc > 0 else "#D32F2F")
    bg_badge = "#E8F5E9" if perc >= 100 else ("#FFF3E0" if perc > 0 else "#FFEBEE")

    card_class = "vdr-card vdr-active" if mode == "active" else "vdr-card vdr-dim"
    
    return f"""
    <div class="{card_class}">
        <div style="display: flex; justify-content: space-between; align-items: start;">
            <span style="color: #666; font-size: 0.9rem;">ODC: <b>{row['ODC']}</b></span>
            <span class="status-badge" style="background: {bg_badge}; color: {color};">{row['Estatus']}</span>
        </div>
        <h3 style="margin: 10px 0 5px 0; color: #1B5E20;">{row['Producto']}</h3>
        <p style="margin: 0; color: #444; font-size: 1rem;">{row['Proveedor']}</p>
        <div style="margin-top: 15px; display: flex; justify-content: space-between; font-size: 0.9rem;">
            <span>Esperado: <b>{row['Esperada']}</b></span>
            <span>Recibido: <b>{row['Recibida']}</b></span>
            <span style="color: {color}; font-weight: bold;">{perc}%</span>
        </div>
        <div class="progress-container">
            <div class="progress-bar" style="width: {perc}%; background: {color};"></div>
        </div>
    </div>
    """

# ------------------------------------------------------------
# 4. RENDERIZADO DEL DASHBOARD
# ------------------------------------------------------------
st.title("📦 Monitor de Recepciones VDR")

# Contadores de cabecera (Sugerencia 5)
c1, c2, c3 = st.columns(3)
c1.metric("Total Recepciones", len(df_vdr))
c2.metric("Completadas", len(df_vdr[df_vdr['Recibida'] >= df_vdr['Esperada']]))
c3.metric("Pendientes", len(df_vdr[df_vdr['Recibida'] < df_vdr['Esperada']]))

col_nav, col_display = st.columns([1, 6])

with col_nav:
    st.write("### Navegación")
    if st.button("▲", use_container_width=True):
        st.session_state.vdr_idx = max(0, st.session_state.vdr_idx - 1)
    
    st.write(f"**{st.session_state.vdr_idx + 1} / {len(df_vdr)}**")
    
    if st.button("▼", use_container_width=True):
        st.session_state.vdr_idx = min(len(df_vdr) - 1, st.session_state.vdr_idx + 1)

with col_display:
    idx = st.session_state.vdr_idx
    
    # Lógica de "Ventana Deslizable" (Anterior, Actual, Siguiente)
    with st.container():
        # Anterior
        if idx > 0:
            st.markdown(render_card(df_vdr.iloc[idx-1], "dim"), unsafe_allow_html=True)
        else:
            st.markdown('<div style="height: 100px; opacity: 0.2; text-align: center;">--- Inicio de lista ---</div>', unsafe_allow_html=True)
            
        # Actual (Foco)
        st.markdown(render_card(df_vdr.iloc[idx], "active"), unsafe_allow_html=True)
        
        # Siguiente
        if idx < len(df_vdr) - 1:
            st.markdown(render_card(df_vdr.iloc[idx+1], "dim"), unsafe_allow_html=True)
        else:
            st.markdown('<div style="height: 100px; opacity: 0.2; text-align: center;">--- Fin de lista ---</div>', unsafe_allow_html=True)
