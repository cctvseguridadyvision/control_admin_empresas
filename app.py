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
    
    # ID de la hoja de cálculo extraído directamente de tu URL
    SPREADSHEET_ID = "1_Kqu0JXNykxvD6Pag9gvmCAYlFz0wKkp"
    sh = client.open_by_key(SPREADSHEET_ID)

except Exception as e:
    st.error(f"⚠️ Error al conectar con Google Sheets: {str(e)}")
    st.info("Verifica que hayas guardado el archivo como Hoja de Cálculo de Google y que lo hayas compartido como Editor con la cuenta de servicio.")
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
        data = ws.get_all_values()
        
        # Buscar la fila donde están los encabezados (donde dice Código_SKU o Nombre_Producto)
        header_idx = 0
        for i, row in enumerate(data):
            if "Código_SKU" in row or "Nombre_Producto" in row:
                header_idx = i
                break
                
        df = pd.DataFrame(data[header_idx + 1:], columns=data[header_idx])
        
        # Limpiar columnas vacías si las hay
        df = df.loc[:, df.columns != '']

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Referencias", len(df))
        
        if 'Stock_Fisico' in df.columns:
            # Convertir a numérico para filtros y métricas
            df['Stock_Num'] = pd.to_numeric(df['Stock_Fisico'], errors='coerce').fillna(0)
            col2.metric("Productos Disponibles", len(df[df['Stock_Num'] > 0]))
            col3.metric("Productos Agotados", len(df[df['Stock_Num'] == 0]))
            df = df.drop(columns=['Stock_Num'])
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
        data = ws.get_all_values()
        
        header_idx = 0
        for i, row in enumerate(data):
            if any(cell.strip() for cell in row):
                header_idx = i
                break
                
        df = pd.DataFrame(data[header_idx + 1:], columns=data[header_idx])
        st.dataframe(df, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error al cargar la pestaña 'Proveedores': {str(e)}")

# ------------------------------------------
# 3. MÓDULO COMPRAS Y CUENTAS POR PAGAR
# ------------------------------------------
elif opcion == "🛒 Compras & Cuentas por Pagar":
    st.title("🛒 Registro de Compras y Cuentas por Pagar")
    
    try:
        ws = sh.worksheet("Compras_Proveedores")
        data = ws.get_all_values()
        
        header_idx = 0
        for i, row in enumerate(data):
            if any(cell.strip() for cell in row):
                header_idx = i
                break
                
        df = pd.DataFrame(data[header_idx + 1:], columns=data[header_idx])
        st.dataframe(df, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error al cargar la pestaña 'Compras': {str(e)}")

# ------------------------------------------
# 4. REGISTRAR ENTRADA / ABONO
# ------------------------------------------
elif opcion == "➕ Registrar Entrada / Abono":
    st.title("➕ Registrar Nueva Entrada o Abono")
    st.info("Módulo para registro de movimientos operacionales.")
