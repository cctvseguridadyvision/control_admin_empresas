import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# Configuración de la página
st.set_page_config(
    page_title="Sistema CCTV & Prisma Net", 
    layout="wide", 
    page_icon="🔒"
)

# Función con caché para conectar a Google Drive y Google Sheets
@st.cache_resource
def conectar_google():
    # Leer las credenciales desde los Secrets de Streamlit Cloud
    creds_dict = st.secrets["gcp_service_account"]
    
    # Definir los alcances (scopes) de la API
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    return gspread.authorize(creds)

# Intentar abrir la conexión y el libro de Google Sheets
try:
    client = conectar_google()
    
    # OPCIÓN 1: Abrir por el NOMBRE EXACTO de la hoja en Google Drive
    sh = client.open("Sistema_CCTV_Compras_Inventario_Proveedores")
    
    # OPCIÓN 2 (Recomendada si la Opción 1 falla por el nombre):
    # Descomenta la siguiente línea y pega la clave de tu URL de Google Sheets
    # sh = client.open_by_key("ID_DE_TU_HOJA_DE_CALCULO")

except Exception as e:
    st.error(f"⚠️ Error de conexión con Google Drive / Sheets: {str(e)}")
    st.info("Asegúrate de que la cuenta de servicio tenga permisos de Editor en la hoja de Google Sheets y que las credenciales en Secrets estén bien configuradas.")
    st.stop()

# ==========================================
# MENÚ LATERAL Y NAVEGACIÓN DE LA APP
# ==========================================
st.sidebar.title("⚙️ Control Operativo")
opcion = st.sidebar.radio(
    "Seleccione Módulo:", [
        "📦 Inventario & Productos",
        "🏢 Directorio Proveedores",
        "🛒 Compras & Cuentas por Pagar",
        "➕ Registrar Entrada / Abono"
    ]
)

# ------------------------------------------
# 1. MÓDULO INVENTARIO
# ------------------------------------------
if opcion == "📦 Inventario & Productos":
    st.title("📦 Inventario Maestro de Productos")
    
    try:
        ws = sh.worksheet("Productos_Servicios")
        df = pd.DataFrame(ws.get_all_records())

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Referencias", len(df))
        
        if 'Stock_Fisico' in df.columns:
            col2.metric("Productos Disponibles", len(df[df['Stock_Fisico'] > 0]))
            col3.metric("Productos Agotados", len(df[df['Stock_Fisico'] == 0]))
        else:
            col2.metric("Productos Disponibles", "N/A")
            col3.metric("Productos Agotados", "N/A")

        st.markdown("---")
        st.dataframe(df, use_container_width=True)

    except Exception as e:
        st.error(f"Error al cargar la pestaña 'Productos_Servicios': {str(e)}")

# ------------------------------------------
# 2. MÓDULO PROVEEDORES
# ------------------------------------------
elif opcion == "🏢 Directorio Proveedores":
    st.title("🏢 Directorio de Proveedores y Distribuidores")
    
    try:
        ws = sh.worksheet("Proveedores")
        df = pd.DataFrame(ws.get_all_records())
        st.dataframe(df, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error al cargar la pestaña 'Proveedores': {str(e)}")

# ------------------------------------------
# 3. MÓDULO COMPRAS Y CUENTAS POR PAGAR
# ------------------------------------------
elif opcion == "🛒 Compras & Cuentas por Pagar":
    st.title("🛒 Registro de Compras y Cuentas por Pagar")
    
    try:
        ws = sh.worksheet("Compras")
        df = pd.DataFrame(ws.get_all_records())
        st.dataframe(df, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error al cargar la pestaña 'Compras': {str(e)}")

# ------------------------------------------
# 4. REGISTRAR ENTRADA / ABONO
# ------------------------------------------
elif opcion == "➕ Registrar Entrada / Abono":
    st.title("➕ Registrar Nueva Entrada o Abono")
    st.info("Módulo para registro de movimientos.")
