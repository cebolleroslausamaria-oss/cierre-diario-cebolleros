import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
from datetime import datetime

# =====================================================
# CONFIGURACION
# =====================================================

SPREADSHEET_ID = "15fsCcyF6WUH1m6ax4cnadXIapL8VN7hNbo9NmLXleFA"

USUARIO = "carlos"
PASSWORD = "12345"

# =====================================================
# PAGINA
# =====================================================

st.set_page_config(
    page_title="Cierre Diario Cebolleros",
    page_icon="📊",
    layout="wide"
)

# =====================================================
# LOGIN
# =====================================================

if "login" not in st.session_state:
    st.session_state.login = False

if "usuario" not in st.session_state:
    st.session_state.usuario = ""

if not st.session_state.login:

    st.title("🔒 Cierre Diario Cebolleros")

    usuario = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")

    if st.button("Ingresar"):

        if usuario == USUARIO and password == PASSWORD:
            st.session_state.login = True
            st.session_state.usuario = usuario
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos")

    st.stop()

# =====================================================
# GOOGLE SHEETS
# =====================================================

scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scope
)

client = gspread.authorize(creds)

spreadsheet = client.open_by_key(SPREADSHEET_ID)

sheet = spreadsheet.sheet1

sheet_gastos = spreadsheet.worksheet(
    "Gastos_Adicionales"
)

# =====================================================
# TITULO
# =====================================================

st.title("📊 Cierre Diario Cebolleros")

st.success(
    f"Usuario conectado: {st.session_state.usuario}"
)

col1, col2 = st.columns([8,2])

with col2:
    if st.button("🚪 Cerrar Sesión"):
        st.session_state.login = False
        st.session_state.usuario = ""
        st.rerun()

# =====================================================
# FORMULARIO
# =====================================================

st.subheader("Registrar Cierre")

fecha = st.date_input(
    "Fecha"
)

col1, col2 = st.columns(2)

with col1:

    produccion = st.number_input(
        "Producción",
        min_value=0.0,
        step=1000.0,
        format="%.2f"
    )

    gasto_dia = st.number_input(
        "Gasto del Día",
        min_value=0.0,
        step=1000.0,
        format="%.2f"
    )

    pago_personal = st.number_input(
        "Pago Personal",
        min_value=0.0,
        step=1000.0,
        format="%.2f"
    )

    pago_pan = st.number_input(
        "Pago Pan",
        min_value=0.0,
        step=1000.0,
        format="%.2f"
    )

with col2:

    pago_marbella = st.number_input(
        "Pago Marbella",
        min_value=0.0,
        step=1000.0,
        format="%.2f"
    )

    pago_jugos = st.number_input(
        "Pago Jugos",
        min_value=0.0,
        step=1000.0,
        format="%.2f"
    )

    base = st.number_input(
        "Base",
        min_value=0.0,
        step=1000.0,
        format="%.2f"
    )

    cebolla = st.number_input(
        "Cebolla",
        min_value=0.0,
        step=1000.0,
        format="%.2f"
    )

otros = st.number_input(
    "Otros Gastos",
    min_value=0.0,
    step=1000.0,
    format="%.2f"
)

# =====================================
# GASTOS ADICIONALES
# =====================================

st.subheader("🧾 Gastos Adicionales")

if "gastos_extra" not in st.session_state:
    st.session_state.gastos_extra = []

if st.button("➕ Agregar Gasto"):

    st.session_state.gastos_extra.append(
        {
            "concepto": "",
            "valor": 0.0
        }
    )

total_gastos_extra = 0

for i in range(len(st.session_state.gastos_extra)):

    c1, c2 = st.columns([3, 1])

    with c1:
        concepto = st.text_input(
            f"Concepto {i+1}",
            key=f"concepto_{i}"
        )

    with c2:
        valor = st.number_input(
            f"Valor {i+1}",
            min_value=0.0,
            step=1000.0,
            key=f"valor_{i}"
        )

    st.session_state.gastos_extra[i]["concepto"] = concepto
    st.session_state.gastos_extra[i]["valor"] = valor

    total_gastos_extra += valor

st.info(
    f"Total Gastos Adicionales: ${total_gastos_extra:,.0f}"
)

# =====================================================
# CALCULO GANANCIA
# =====================================================

gastos_totales = (
    gasto_dia
    + pago_personal
    + pago_pan
    + pago_marbella
    + pago_jugos
    + base
    + cebolla
    + otros
)

ganancia = (
    produccion
    - gastos_totales
    - total_gastos_extra
)

st.metric(
    "Ganancia Calculada",
    f"${ganancia:,.0f}"
)

# =====================================================
# GUARDAR
# =====================================================

if st.button("Guardar Cierre"):

    try:

        # Guardar cierre principal
        sheet.append_row([
            str(fecha),
            produccion,
            gasto_dia,
            pago_personal,
            pago_pan,
            pago_marbella,
            pago_jugos,
            base,
            cebolla,
            otros,
            ganancia,
            st.session_state.usuario,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ])

        # Guardar gastos adicionales
        for gasto in st.session_state.gastos_extra:

            if gasto["concepto"] != "" and gasto["valor"] > 0:

                sheet_gastos.append_row([
                    str(fecha),
                    gasto["concepto"],
                    gasto["valor"],
                    st.session_state.usuario,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ])

        st.success("✅ Registro guardado correctamente")
        st.rerun()

        # Limpiar gastos adicionales
        st.session_state.gastos_extra = []

    except Exception as e:

        st.error(f"Error guardando registro: {e}")

# =====================================================
# DASHBOARD
# =====================================================

st.divider()

st.subheader("📈 Resumen General")

try:

    registros = sheet.get_all_records()

    if len(registros) > 0:

        df = pd.DataFrame(registros)

        total_produccion = pd.to_numeric(
            df["Produccion"],
            errors="coerce"
        ).fillna(0).sum()

        total_ganancia = pd.to_numeric(
            df["Ganancia"],
            errors="coerce"
        ).fillna(0).sum()

        total_gastos = (
            pd.to_numeric(df["Gasto_Dia"], errors="coerce").fillna(0).sum()
            + pd.to_numeric(df["Pago_Personal"], errors="coerce").fillna(0).sum()
            + pd.to_numeric(df["Pago_Pan"], errors="coerce").fillna(0).sum()
            + pd.to_numeric(df["Pago_Marbella"], errors="coerce").fillna(0).sum()
            + pd.to_numeric(df["Pago_Jugos"], errors="coerce").fillna(0).sum()
            + pd.to_numeric(df["Base"], errors="coerce").fillna(0).sum()
            + pd.to_numeric(df["Cebolla"], errors="coerce").fillna(0).sum()
            + pd.to_numeric(df["Otros"], errors="coerce").fillna(0).sum()
        )

        c1, c2, c3 = st.columns(3)

        with c1:
            st.metric(
                "Producción Total",
                f"${total_produccion:,.0f}"
            )

        with c2:
            st.metric(
                "Gastos Totales",
                f"${total_gastos:,.0f}"
            )

        with c3:
            st.metric(
                "Ganancia Total",
                f"${total_ganancia:,.0f}"
            )

        st.subheader("📋 Historial")

        st.dataframe(
            df,
            use_container_width=True
        )

    else:

        st.info(
            "No existen registros todavía."
        )

        

except Exception as e:

    st.error(
        f"Error leyendo datos: {e}"
    )

# =====================================================
# RESUMEN MENSUAL
# =====================================================

try:

    df["Fecha"] = pd.to_datetime(df["Fecha"])

    fecha_actual = datetime.now()

    mes_actual = fecha_actual.month
    anio_actual = fecha_actual.year

    df_mes = df[
        (df["Fecha"].dt.month == mes_actual)
        &
        (df["Fecha"].dt.year == anio_actual)
    ]

    produccion_mes = pd.to_numeric(
        df_mes["Produccion"],
        errors="coerce"
    ).fillna(0).sum()

    gastos_mes = (
        pd.to_numeric(df_mes["Gasto_Dia"], errors="coerce").fillna(0).sum()
        + pd.to_numeric(df_mes["Pago_Personal"], errors="coerce").fillna(0).sum()
        + pd.to_numeric(df_mes["Pago_Pan"], errors="coerce").fillna(0).sum()
        + pd.to_numeric(df_mes["Pago_Marbella"], errors="coerce").fillna(0).sum()
        + pd.to_numeric(df_mes["Pago_Jugos"], errors="coerce").fillna(0).sum()
        + pd.to_numeric(df_mes["Base"], errors="coerce").fillna(0).sum()
        + pd.to_numeric(df_mes["Cebolla"], errors="coerce").fillna(0).sum()
        + pd.to_numeric(df_mes["Otros"], errors="coerce").fillna(0).sum()
    )

    ganancia_mes = pd.to_numeric(
        df_mes["Ganancia"],
        errors="coerce"
    ).fillna(0).sum()

    st.divider()

    st.subheader("📅 Resumen del Mes")

    m1, m2, m3, m4 = st.columns(4)

    m1.metric(
        "Producción Mes",
        f"${produccion_mes:,.0f}"
    )

    m2.metric(
        "Gastos Mes",
        f"${gastos_mes:,.0f}"
    )

    m3.metric(
        "Ganancia Mes",
        f"${ganancia_mes:,.0f}"
    )

    m4.metric(
        "Cierres Registrados",
        len(df_mes)
    )

except Exception as e:
    st.warning(f"Error resumen mensual: {e}")   
st.subheader("📊 Histórico Mensual")

df_resumen = df.copy()

df_resumen["Fecha"] = pd.to_datetime(df_resumen["Fecha"])

df_resumen["Periodo"] = (
    df_resumen["Fecha"].dt.strftime("%Y-%m")
)

columnas_gasto = [
    "Gasto_Dia",
    "Pago_Personal",
    "Pago_Pan",
    "Pago_Marbella",
    "Pago_Jugos",
    "Base",
    "Cebolla",
    "Otros"
]

for col in columnas_gasto:
    df_resumen[col] = pd.to_numeric(
        df_resumen[col],
        errors="coerce"
    ).fillna(0)

df_resumen["Gastos"] = (
    df_resumen[columnas_gasto].sum(axis=1)
)

tabla_mensual = (
    df_resumen
    .groupby("Periodo")
    .agg({
        "Produccion":"sum",
        "Gastos":"sum",
        "Ganancia":"sum"
    })
    .reset_index()
)

st.dataframe(
    tabla_mensual,
    use_container_width=True
)         
