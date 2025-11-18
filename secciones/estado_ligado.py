import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import datetime
from utils.api_utils import obtener_datos_api

def mostrar(df, config):

    st.title("Estado de Ligado")
    
    if df.empty:
        st.warning("No hay datos para mostrar.")
        return
    
    df = df.dropna(subset=["sucursal"])

    meses_es = {
        'January': 'Enero', 'February': 'Febrero', 'March': 'Marzo', 'April': 'Abril',
        'May': 'Mayo', 'June': 'Junio', 'July': 'Julio', 'August': 'Agosto',
        'September': 'Septiembre', 'October': 'Octubre', 'November': 'Noviembre', 'December': 'Diciembre'
    }

    df["mes_dt"] = pd.to_datetime(df["mes"])
    df["mes_nombre"] = df["mes_dt"].dt.month_name().map(meses_es) + " " + df["mes_dt"].dt.year.astype(str)
    df["mes_period"] = df["mes_dt"].dt.to_period("M")
    df = df.sort_values("mes_dt")
    # Orden ascendente (para gráficas que van de enero a diciembre)
    orden_meses_asc = (
        df.drop_duplicates(subset="mes_period")
        .sort_values("mes_period", ascending=True)["mes_nombre"]
        .tolist()
    )

    # Orden descendente (para gráficas que van de mes más reciente al más antiguo)
    orden_meses_desc = orden_meses_asc[::-1]
    orden_meses = orden_meses_asc

    # ----------- Información General - Estado de Ligado  (TARJETAS) -----------
    st.markdown("### Información general")
    # Filtramos el dataframe para obtener totales según el ligado_sistema
    monto_ligado = df[df["ligado_sistema"] == 1]["monto"].sum()
    monto_pendiente = df[df["ligado_sistema"] == 0]["monto"].sum()
    # Mostramos en tarjetas
    col1, col2 = st.columns(2)

    with col1:
        st.metric("✅ Total ligado en sistema", f"${monto_ligado:,.2f}")

    with col2:
        st.metric("🕒 Pendiente de ligar", f"${monto_pendiente:,.2f}")

    # ---------------- FILTRAR FACTURAS NO LIGADAS (GRAFICO DE LÍNEAS) ---------------------------------------------
    df_no_ligado = df[df["ligado_sistema"] == 0]

    # Agrupar por mes
    monto_mensual_no_ligado = (
        df_no_ligado.groupby("mes_nombre")["monto"]
        .sum()
        .reindex(orden_meses)
    )

    # --- GRÁFICO ---
    st.subheader("Monto mensual sin ligar")
    fig = px.line(
        x=monto_mensual_no_ligado.index,
        y=monto_mensual_no_ligado.values,
        labels={"x": "Mes", "y": "Monto sin ligar"},
        markers=True,
    )

    fig.update_traces(
        hovertemplate=(
            "<b>Mes:</b> %{x}<br>"
            "<b>Monto sin ligar:</b> $%{y:,.2f}<extra></extra>"
        )
    )

    fig.update_layout(
        xaxis_title="Mes",
        yaxis_title="Monto sin ligar",
        title="Tendencia mensual de facturas no ligadas"
    )

    st.plotly_chart(fig, use_container_width=True)

    # --- ---------CANTIDAD SIN LIGAR MENSUAL POR SUCURSAL (GRAFICO DE BARRAS APILADAS) -----------------------------------------------
    # Filtrar solo facturas sin ligar
    df_no_ligado = df[df["ligado_sistema"] == 0].copy()

    # Asegurarnos que mes_dt exista y sea datetime
    if "mes_dt" not in df_no_ligado.columns:
        df_no_ligado["mes_dt"] = pd.to_datetime(df_no_ligado["mes"].astype(str))

    # Obtener el mes actual (en formato periodo M)
    mes_actual = pd.to_datetime("today").to_period("M")

    # Agrupar monto por mes_nombre, sucursal y mes_dt (fecha)
    monto_por_mes_sucursal = df_no_ligado.groupby(
        ["mes_nombre", "sucursal", "mes_dt"]
    )["monto"].sum().reset_index()

    # Filtrar para excluir mes actual y posteriores
    monto_por_mes_sucursal = monto_por_mes_sucursal[
        monto_por_mes_sucursal["mes_dt"].dt.to_period("M") < mes_actual
    ]

    # Crear orden correcto solo con los meses filtrados
    meses_filtrados = [m for m in orden_meses if m in monto_por_mes_sucursal["mes_nombre"].unique()]
    monto_por_mes_sucursal["mes_nombre"] = pd.Categorical(
        monto_por_mes_sucursal["mes_nombre"],
        categories=meses_filtrados,
        ordered=True
    )

    # Ordenar DataFrame por fecha para que Plotly respete el orden cronológico
    monto_por_mes_sucursal = monto_por_mes_sucursal.sort_values("mes_dt")

    # Crear gráfico de barras apiladas horizontales con customdata
    fig = px.bar(
        monto_por_mes_sucursal,
        x="monto",
        y="mes_nombre",
        color="sucursal",
        orientation="h",
        title="Distribución mensual del monto sin ligar por sucursal",
        labels={"monto": "Monto sin ligar", "mes_nombre": "Mes"},
        category_orders={"mes_nombre": meses_filtrados},
        custom_data=["sucursal"]  # <-- para usar en hovertemplate
    )

    fig.update_layout(
        barmode="stack",
        xaxis_title="Monto sin ligar",
        yaxis_title="Mes"
    )

    # Hovertemplate personalizado usando customdata[0]
    fig.update_traces(
        hovertemplate=(
            "<b>Mes:</b> %{y}<br>"
            "<b>Sucursal:</b> %{customdata[0]}<br>"
            "<b>Monto sin ligar:</b> $%{x:,.2f}<extra></extra>"
        )
    )

    st.plotly_chart(fig, use_container_width=True)

    #------------- TABLA ------------------------------
    tabla_resumen = monto_por_mes_sucursal.pivot_table(
        index="mes_nombre",
        columns="sucursal",
        values="monto",
        aggfunc="sum",
        fill_value=0
    )

    # Ordenar los meses correctamente
    tabla_resumen = tabla_resumen.reindex(meses_filtrados)

    # Renombrar índice
    tabla_resumen.index.name = "Mes"

    # Función para aplicar estilo condicional
    def resaltar_valores(val):
        color = 'background-color: #BC13FE' if val != 0 else ''
        return color

    # Mostrar en Streamlit con estilo
    st.subheader("Tabla resumen del monto sin ligar por mes y sucursal")
    st.dataframe(
        tabla_resumen.style
            .applymap(resaltar_valores)
            .format("${:,.2f}")
    )

    # ---------------------- INFORME DETALLADO DE LIGADO POR SUCURSAL ----------------------

    st.markdown("---")
    st.subheader("📄 Informe detallado de ligado por sucursal")

    sucursales = [
        { "nombre": "Acayucan", "url": "https://docs.google.com/spreadsheets/d/13UHVPsiI7MejlVLFA1jePD_bgZ6T9FhwmB7bRVZnTrI/edit?usp=sharing" },
        { "nombre": "Campeche", "url": "https://docs.google.com/spreadsheets/d/15cN90A8jig7pit9ZalubhWM0wfSSXN1Udsjc9BSALrI/edit?usp=sharing" },
        { "nombre": "Cancun", "url": "https://docs.google.com/spreadsheets/d/1KXLgaNAg0Jp6IGG0YLZZLu-b-Hd5cZ2GcgNEZEJh8tE/edit?usp=sharing" },
        { "nombre": "Chetumal", "url": "https://docs.google.com/spreadsheets/d/1sP2AmsY1neNtgKcpI60UH03dVZpbhK3xOdBqYmZU6F8/edit?usp=sharing" },
        { "nombre": "Comitan", "url": "https://docs.google.com/spreadsheets/d/1B9nUT5kDhhcNQdUeGhNo96cZg6RhyJNZs-BraKUkc3k/edit?usp=sharing" },
        { "nombre": "Isla", "url": "https://docs.google.com/spreadsheets/d/1xqDNrrRSCfxGSoytnmRhD8HdEoTMTDG_NXkzpIi8JkE/edit?usp=sharing" },
        { "nombre": "Merida", "url": "https://docs.google.com/spreadsheets/d/1-oqJNdE_Fdpxveel6LgH3fuFo-OgDd0ot3AnrYlnZyc/edit?usp=sharing" },
        { "nombre": "Puebla", "url": "https://docs.google.com/spreadsheets/d/16oAlX4oqepUbdutQpChEt5RbMzJ8c_uOEUcRPhyePeE/edit?usp=sharing" },
        { "nombre": "Tapachula", "url": "https://docs.google.com/spreadsheets/d/1HpevkdoZqi3H8GAe6HJw5KpQNHIyI_hy2HGGxgfXRRM/edit?usp=sharing" },
        { "nombre": "Tierra blanca", "url": "https://docs.google.com/spreadsheets/d/1k-JlkvOJ9hemos7Sdsk1-IHa6OaB5ax-JxTO_5_T7so/edit?usp=sharing" },
        { "nombre": "Tizimin", "url": "https://docs.google.com/spreadsheets/d/18a8sSJRC260-AKXbH22pI9WwFATh-oGwtOg_4QaxUYE/edit?usp=sharing" },
        { "nombre": "Tuxtepec", "url": "https://docs.google.com/spreadsheets/d/1DlePgvlI3ruGxmidITMjyMKlcxzLXKT3yXD4-NApx2Y/edit?usp=sharing" },
        { "nombre": "Tuxtla Gtz", "url": "https://docs.google.com/spreadsheets/d/1rgnyUwWmhmSc8trMzvGqvSWHzMI375ZKZjdL3T3WSE4/edit?usp=sharing" },
        { "nombre": "Veracruz", "url": "https://docs.google.com/spreadsheets/d/1k7u7jBRqq8fhQ4dR92DgEmyyvnvx5BO8vZlsp-PVEXg/edit?usp=sharing" },
        { "nombre": "Villahermosa", "url": "https://docs.google.com/spreadsheets/d/1QMGvVzOxtQiVEpdhYnoOyjQwDqlM2P54yKd6eeQSAsk/edit?usp=sharing" },
        { "nombre": "Zapata", "url": "https://docs.google.com/spreadsheets/d/1MiGMmvPkMGk6ladmFSQZ5SwaKg0oYIdffoin5yA4HBc/edit?usp=sharing" },
    ]

    # ---- Estilo CSS para botones morados y redondos ----
    st.markdown("""
    <style>
    .button-morado {
        background-color: #A020F0; 
        color: white;
        padding: 10px 14px;
        border-radius: 30px;
        text-decoration: none;
        display: inline-block;
        width: 100%;
        text-align: center;
        font-weight: 600;
        transition: 0.2s ease-in-out;
    }
    .button-morado:hover {
        background-color: #8B00D6;
        transform: scale(1.03);
    }
    </style>
    """, unsafe_allow_html=True)

    # Distribuir 4 columnas
    cols = st.columns(4)

    for i, suc in enumerate(sucursales):
        col = cols[i % 4]
        with col:
            st.markdown(
                f'<a class="button-morado" href="{suc["url"]}" target="_blank">📄 {suc["nombre"]}</a>',
                unsafe_allow_html=True
            )
