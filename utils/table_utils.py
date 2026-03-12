#utils\table_utils.py
import pandas as pd
import numpy as np
import streamlit as st

def tabla_totales_html(tabla_horizontal_df):
    tabla_html = tabla_horizontal_df.applymap(lambda x: f"${x:,.2f}")

    header_html = ''.join([
        f'<th style="background-color:#390570; color:white; padding:8px; text-align:left;">{col}</th>'
        for col in tabla_html.columns
    ])

    row_html = ''.join([
        f'<td style="padding:8px; text-align:left;">{val}</td>'
        for val in tabla_html.iloc[0]
    ])

    return f"""
    <div style="overflow-x:auto; width: 100%;">
    <table style="border-collapse:collapse; min-width:800px; width:100%;">
        <thead>
        <tr>
            <th style="background-color:#390570; padding:8px; color:white; text-align:left; position:sticky; left:0; z-index:1;">
            </th>
            {header_html}
        </tr>
        </thead>
        <tbody>
        <tr>
            <td style="padding:8px; text-align:right; background-color:#281436; color:white; font-weight:bold; position:sticky; left:0; z-index:1;">
            Total Comprado
            </td>
            {row_html}
        </tr>
        </tbody>
    </table>
    </div>
    """

def construir_tabla_comparativa(df_comp):
    estilos_css = """
    <style>
        .tabla-wrapper { overflow-x: auto; width: 100%; }
        .tabla-comparativa { min-width: 100%; width: max-content; border-collapse: collapse; }
        .tabla-comparativa thead th {
            background-color: #0B083D; color: white; padding: 8px;
            position: sticky; top: 0; z-index: 3;
        }
        .tabla-comparativa td, .tabla-comparativa th {
            padding: 8px; font-size: 14px; white-space: nowrap; border: 1px solid white;
        }
        .tabla-comparativa tbody td:first-child {
            position: sticky; left: 0; background-color: #0B083D; color: white; font-weight: bold;
        }
        .subida { background-color: #7D1F08; color: white; }
        .bajada { background-color: #184E08; color: white; }
        .neutra { color: white; }
    </style>
    """

    html = f"{estilos_css}<div class='tabla-wrapper'><table class='tabla-comparativa'>"
    html += "<thead><tr><th>Mes</th><th>Total Comprado</th><th>Diferencia ($)</th><th>Variación (%)</th></tr></thead><tbody>"

    for _, row in df_comp.iterrows():
        clase_color = (
            "subida" if "⬆" in row["Diferencia ($)"] else
            "bajada" if "⬇" in row["Diferencia ($)"] else
            "neutra"
        )
        html += f"<tr><td>{row['Mes']}</td>"
        html += f"<td class='{clase_color}'>{row['Total Comprado']}</td>"
        html += f"<td class='{clase_color}'>{row['Diferencia ($)']}</td>"
        html += f"<td class='{clase_color}'>{row['Variación (%)']}</td></tr>"

    html += "</tbody></table></div>"
    return html



def mostrar_tabla_matriz_html(
    df: pd.DataFrame,
    header_left: list,
    data_columns: list,
    header_right: list = None,
    footer_totals: dict = None,
    max_height: int = 600
):
    if df.empty:
        return

    header_right = header_right or []
    
    # --- CÁLCULO DE ESCALA GLOBAL PARA DEGRADADO ---
    valores = df[data_columns].values.flatten()
    valores = valores[~pd.isna(valores)].astype(float)
    min_val = valores.min() if valores.size > 0 else 0
    max_val = valores.max() if valores.size > 0 else 1

    def get_color(val):
        if pd.isna(val): return "background-color: #ffffff; color: #0B083D;"
        ratio = (float(val) - min_val) / (max_val - min_val) if max_val != min_val else 0
        r = int(227 + ratio * (21 - 227))
        g = int(242 + ratio * (101 - 242))
        b = int(253 + ratio * (192 - 253))
        text_color = "white" if ratio > 0.6 else "#0B083D"
        return f"background-color: rgb({r},{g},{b}); color: {text_color};"

    # --- CONSTRUCCIÓN DEL HTML ---
    html = f"""
    <style>
        .table-outer-wrapper {{
            width: 100%;
            background-color: transparent;
            padding-bottom: 2px;
        }}
        .table-container {{
            height: auto;
            max-height: {max_height}px;
            overflow: auto;
            border: none;
            position: relative;
            background-color: transparent;
        }}
        table {{
            border-collapse: separate;
            border-spacing: 0;
            width: 100%;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            font-size: 0.85rem;
            background-color: white;
            border: 1px solid #f0f2f6;
        }}
        thead {{
            position: sticky;
            top: 0;
            z-index: 100;
            background: white;
        }}
        /* Estilo General del Header (Blanco) */
        thead th {{
            position: sticky;
            top: 0;
            background: white;
            color: #0B083D;
            z-index: 101;
            border-bottom: 2px solid #e6e9ef;
            border-right: 1px solid #f0f2f6;
            padding: 12px 10px;
            text-align: center;
        }}
        /* Header Pinned (Izquierda y Derecha pero en Blanco) */
        thead th.pinned-header-left {{
            position: sticky;
            background-color: white !important;
            z-index: 102; /* Mayor que el resto del header */
            border-right: 2px solid #e6e9ef !important;
        }}
        thead th.pinned-header-right {{
            position: sticky;
            background-color: white !important;
            right: 0;
            z-index: 102;
            border-left: 2px solid #e6e9ef !important;
        }}
        /* offsets columnas izquierdas */
        thead th.pinned-header-left:nth-child(1),
        td.sticky-left:nth-child(1) {{
            left: 0px;
        }}
        thead th.pinned-header-left:nth-child(2),
        td.sticky-left:nth-child(2) {{
            left: 100px;
            
        }}
        thead th.pinned-header-left:nth-child(3),
        td.sticky-left:nth-child(3) {{
            left: 170px;
            
        }}
        
        /* Celdas del Cuerpo Pinned (Azules) */
        .sticky-left {{
            position: sticky;

            background-color: #0B083D !important;
            color: white !important;
            font-weight: bold;
            z-index: 10;
            border-right: 2px solid #e6e9ef !important;
            box-shadow: 4px 0 6px -4px rgba(0,0,0,0.2);
        }}
        .sticky-right {{
            position: sticky;
            right: 0;
            background-color: #0B083D !important;
            color: white !important;
            font-weight: bold;
            z-index: 10;
            border-left: 2px solid #e6e9ef !important;
            box-shadow: -4px 0 6px -4px rgba(0,0,0,0.2);
        }}

        /* Footer Fijo */
        tfoot td {{
            position: sticky;
            bottom: 0;
            background-color: #0B083D !important;
            color: white !important;
            font-weight: bold;
            z-index: 10;
            padding: 10px;
            border-top: 2px solid #e6e9ef;
        }}
        /* Esquinas del Footer */
        tfoot td.sticky-left {{ z-index: 15; }}
        tfoot td.sticky-right {{ z-index: 15; }}

        td {{
            padding: 8px 12px;
            border-left: 1px solid #e6e9ef;
            border-right: 1px solid #e6e9ef;
            white-space: nowrap;
            background-color: white;
            color: #0B083D;
        }}
        tbody td {{
            box-shadow: inset 0 -1px 0 #B7B9BC;
        }}
        /* Separadores para columnas numéricas */
        /* Separadores para columnas numéricas */
        td.data-col {{
            box-shadow: inset 1px 0 0 #B7B9BC;
        }}

        td.data-col {{
            box-shadow:
                inset 1px 0 0 #B7B9BC,
                inset 0 -1px 0 #B7B9BC;
        }}

        .table-container::-webkit-scrollbar {{ width: 7px; height: 7px; }}
        .table-container::-webkit-scrollbar-track {{ background: transparent; }}
        .table-container::-webkit-scrollbar-thumb {{ background: #d1d5db; border-radius: 10px; }}
        .table-container::-webkit-scrollbar-thumb:hover {{ background: #9ca3af; }}
    </style>
    <div class="table-outer-wrapper">
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        {"".join([
                            f'<th class="'
                            f'{"pinned-header-left" if c in header_left else "pinned-header-right" if c in header_right else ""}'
                            f'{" data-col" if c in data_columns else ""}">{c}</th>'
                            for c in df.columns
                        ])}
                    </tr>
                </thead>
                <tbody>
    """

    for _, row in df.iterrows():
        html += "<tr>"
        for col in df.columns:
            val = row[col]
            clase = ""
            if col in header_left: clase = "sticky-left"
            elif col in header_right: clase = "sticky-right"
            
            display_val = f"{val:,.2f}" if isinstance(val, (int, float)) else str(val)
            if pd.isna(val): display_val = "-"

            if col in data_columns:
                estilo_celda = get_color(val)
            else:
                estilo_celda = "background-color: white;" if clase == "" else ""

            extra_class = "data-col" if col in data_columns else ""
            html += f'<td class="{clase} {extra_class}" style="{estilo_celda}">{display_val}</td>'
        html += "</tr>"

    if footer_totals:
        html += "<tfoot><tr>"
        for col in df.columns:
            clase = ""
            if col in header_left: clase = "sticky-left"
            elif col in header_right: clase = "sticky-right"
            val = footer_totals.get(col, "")
            display_val = f"{val:,.2f}" if isinstance(val, (int, float)) else str(val)
            html += f'<td class="{clase}">{display_val}</td>'
        html += "</tr></tfoot>"

    html += "</table></div></div>"
    
    st.write(html, unsafe_allow_html=True)