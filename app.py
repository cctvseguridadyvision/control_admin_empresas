import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Sistema CCTV & Prisma Net", layout="wide", page_icon="🔒")

# Conexión leyendo credenciales seguras desde Streamlit Cloud
@st.cache_resource
def conectar_google():
    creds_dict = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ])
    return gspread.authorize(creds)

try:
    client = conectar_google()
    sh = client.open("Sistema_CCTV_Compras_Inventario_Proveedores")
except Exception as e:
    st.error(f"Error de conexión con Google Drive: {e}")
    st.stop()

# Menú Lateral
st.sidebar.title("⚙️ Control Operativo")
opcion = st.sidebar.radio("Seleccione Módulo:", [
    "📦 Inventario & Productos", 
    "🏭 Directorio Proveedores", 
    "🧾 Compras & Cuentas por Pagar",
    "➕ Registrar Entrada / Abono"
])

# 1. MÓDULO INVENTARIO
if opcion == "📦 Inventario & Productos":
    st.title("📦 Inventario Maestro de Productos")
    ws = sh.worksheet("Productos_Servicios")
    df = pd.DataFrame(ws.get_all_records())
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Referencias", len(df))
    col2.metric("Productos Disponibles", len(df[df['Stock_Físico'] > 0]) if 'Stock_Físico' in df else 0)
    col3.metric("Productos Agotados", len(df[df['Stock_Físico'] == 0]) if 'Stock_Físico' in df else 0)
    
    st.markdown("---")
    st.dataframe(df, use_container_width=True)

# 2. MÓDULO PROVEEDORES
elif opcion == "🏭 Directorio Proveedores":
    st.title("🏭 Directorio de Proveedores y Distribuidores")
    ws = sh.worksheet("Proveedores")
    df = pd.DataFrame(ws.get_all_records())
    st.dataframe(df, use_container_width=True)

# 3. MÓDULO COMPRAS & CUENTAS POR PAGAR
elif opcion == "🧾 Compras & Cuentas por Pagar":
    st.title("🧾 Control de Facturas y Saldos Pendientes")
    ws = sh.worksheet("Compras_Proveedores")
    df = pd.DataFrame(ws.get_all_records())
    st.dataframe(df, use_container_width=True)

# 4. REGISTRAR ABONOS O NUEVAS COMPRAS
elif opcion == "➕ Registrar Entrada / Abono":
    st.title("➕ Registrar Transacción")
    
    tipo_trx = st.selectbox("Tipo de Transacción", ["Abono a Proveedor", "Ingresar Stock por Compra"])
    
    if tipo_trx == "Abono a Proveedor":
        with st.form("form_abono"):
            id_compra = st.text_input("ID Compra (ej: CMP-1002)")
            fecha = st.date_input("Fecha de Pago")
            monto = st.number_input("Monto Pagado ($)", min_value=0)
            medio = st.selectbox("Medio de Pago", ["Nequi", "Llave", "Efectivo", "Transferencia Bancaria"])
            comprobante = st.text_input("No. Comprobante / Voucher")
            
            submitted = st.form_submit_button("Guardar Abono en Drive")
            if submitted:
                ws_abonos = sh.worksheet("Abonos_Proveedores")
                nuevo_id = f"ABN-{len(ws_abonos.get_all_records()) + 1:03d}"
                ws_abonos.append_row([nuevo_id, id_compra, str(fecha), monto, medio, comprobante])
                st.success(f"Abono {nuevo_id} guardado correctamente en Google Drive.")
