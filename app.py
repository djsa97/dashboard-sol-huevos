import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import certifi
from io import StringIO

st.set_page_config(
    page_title="Dashboard Flujo de Caja - Sol Huevos",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# CONFIG / ESTILO
# =========================================================
MESES_ORDEN = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
]

MESES_HISTORICOS = ["Enero", "Febrero", "Marzo"]

SHEET_URL = "https://docs.google.com/spreadsheets/d/107Niw43NSOXpYi7knGkemTlnYU2xkK56020mRC25Z60/gviz/tq?tqx=out:csv&sheet=Limpio"

COLOR_BG = "#0F1115"
COLOR_CARD = "#171A21"
COLOR_BORDER = "#262B36"
COLOR_TEXT = "#F3F4F6"
COLOR_TEXT_SOFT = "#AAB2C0"
COLOR_REAL = "#4C78FF"
COLOR_PROY = "#C97A2B"
COLOR_NEG = "#C84B4B"
COLOR_POS = "#2E8B57"

st.markdown(
    f"""
    <style>
        .stApp {{
            background-color: {COLOR_BG};
            color: {COLOR_TEXT};
        }}

        [data-testid="stSidebar"] {{
            background-color: #12151C;
            border-right: 1px solid {COLOR_BORDER};
        }}

        [data-testid="stSidebar"] * {{
            color: {COLOR_TEXT} !important;
        }}

        .block-container {{
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1450px;
        }}

        h1, h2, h3, h4, h5, h6 {{
            color: {COLOR_TEXT};
            letter-spacing: -0.02em;
        }}

        p, div, label, span {{
            color: {COLOR_TEXT_SOFT};
        }}

        .premium-card {{
            background: {COLOR_CARD};
            border: 1px solid {COLOR_BORDER};
            border-radius: 18px;
            padding: 20px 22px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.22);
            min-height: 122px;
        }}

        .premium-card .label {{
            font-size: 0.90rem;
            color: {COLOR_TEXT_SOFT};
            margin-bottom: 10px;
        }}

        .premium-card .value {{
            font-size: 2rem;
            font-weight: 700;
            color: {COLOR_TEXT};
            line-height: 1.1;
        }}

        .section-card {{
            background: {COLOR_CARD};
            border: 1px solid {COLOR_BORDER};
            border-radius: 20px;
            padding: 22px;
            margin-bottom: 18px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.18);
        }}

        .section-title {{
            font-size: 1.35rem;
            font-weight: 700;
            color: {COLOR_TEXT};
            margin-bottom: 6px;
        }}

        .section-subtitle {{
            font-size: 0.95rem;
            color: {COLOR_TEXT_SOFT};
            margin-bottom: 18px;
        }}

        .status-box-negative {{
            background: rgba(200, 75, 75, 0.12);
            border: 1px solid rgba(200, 75, 75, 0.35);
            border-radius: 14px;
            padding: 14px 16px;
            color: #F4B6B6;
            font-weight: 600;
            margin-top: 10px;
        }}

        .status-box-positive {{
            background: rgba(46, 139, 87, 0.12);
            border: 1px solid rgba(46, 139, 87, 0.35);
            border-radius: 14px;
            padding: 14px 16px;
            color: #A7E0BE;
            font-weight: 600;
            margin-top: 10px;
        }}

        .status-box-neutral {{
            background: rgba(80, 100, 130, 0.16);
            border: 1px solid rgba(120, 140, 170, 0.30);
            border-radius: 14px;
            padding: 14px 16px;
            color: #C9D4E5;
            font-weight: 600;
            margin-top: 10px;
        }}

        .note-box {{
            background: rgba(76, 120, 255, 0.10);
            border: 1px solid rgba(76, 120, 255, 0.22);
            border-radius: 14px;
            padding: 14px 16px;
            color: #C8D9F4;
            margin-top: 8px;
            margin-bottom: 8px;
        }}

        .warning-box {{
            background: rgba(201, 122, 43, 0.14);
            border: 1px solid rgba(201, 122, 43, 0.35);
            border-radius: 14px;
            padding: 14px 16px;
            color: #F2C188;
            margin-top: 10px;
        }}

        .small-muted {{
            color: {COLOR_TEXT_SOFT};
            font-size: 0.88rem;
        }}

        div[data-testid="stDataFrame"] {{
            border: 1px solid {COLOR_BORDER};
            border-radius: 14px;
            overflow: hidden;
        }}
    </style>
    """,
    unsafe_allow_html=True
)

# =========================================================
# FUNCIONES
# =========================================================
def format_currency(valor):
    return f"{valor:,.0f}"


def format_currency_short(valor):
    abs_val = abs(valor)

    if abs_val >= 1_000_000_000:
        return f"{valor / 1_000_000_000:.1f}B"
    if abs_val >= 1_000_000:
        return f"{valor / 1_000_000:.1f}M"
    if abs_val >= 1_000:
        return f"{valor / 1_000:.1f}K"
    return f"{valor:,.0f}"


@st.cache_data(ttl=300)
def cargar_datos():
    response = requests.get(SHEET_URL, verify=certifi.where(), timeout=30)
    response.raise_for_status()

    df = pd.read_csv(StringIO(response.text))
    df.columns = [str(col).strip() for col in df.columns]

    columnas_esperadas = [
        "Fecha", "Mes", "Tipo", "Categoria", "Subcategoria", "Monto", "Escenario"
    ]
    faltantes = [col for col in columnas_esperadas if col not in df.columns]
    if faltantes:
        raise ValueError(f"Faltan columnas: {', '.join(faltantes)}")

    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")

    df["Monto"] = (
        df["Monto"]
        .astype(str)
        .str.strip()
        .str.replace(".", "", regex=False)
        .str.replace(",", "", regex=False)
    )
    df["Monto"] = pd.to_numeric(df["Monto"], errors="coerce").fillna(0)

    for col in ["Mes", "Tipo", "Categoria", "Subcategoria", "Escenario"]:
        df[col] = df[col].astype(str).str.strip()

    df["Escenario"] = df["Escenario"].replace({
        "nan": "Sin escenario",
        "": "Sin escenario"
    })
    df["Tipo"] = df["Tipo"].replace({
        "nan": "Sin tipo",
        "": "Sin tipo"
    })
    df["Categoria"] = df["Categoria"].replace({
        "nan": "Sin categoría",
        "": "Sin categoría"
    })
    df["Subcategoria"] = df["Subcategoria"].replace({
        "nan": "Sin subcategoría",
        "": "Sin subcategoría"
    })

    df["Mes"] = pd.Categorical(df["Mes"], categories=MESES_ORDEN, ordered=True)

    return df


def aplicar_filtros(df_base, meses_sel, tipos_sel, escenarios_sel):
    out = df_base.copy()

    if meses_sel:
        out = out[out["Mes"].isin(meses_sel)]

    if tipos_sel:
        out = out[out["Tipo"].isin(tipos_sel)]

    if escenarios_sel:
        out = out[out["Escenario"].isin(escenarios_sel)]

    return out


def calcular_total(df_base, tipo, escenario):
    return df_base.loc[
        (df_base["Tipo"] == tipo) & (df_base["Escenario"] == escenario),
        "Monto"
    ].sum()


def preparar_comparacion_tipo(df_base, tipo):
    df_tipo = df_base[
        (df_base["Tipo"] == tipo) &
        (df_base["Escenario"].isin(["Real", "Proyectado"]))
    ].copy()

    if df_tipo.empty:
        return pd.DataFrame(columns=["Escenario", "Monto"])

    return df_tipo.groupby("Escenario", as_index=False)["Monto"].sum()


def preparar_desvios(df_base):
    df_comp = df_base[df_base["Escenario"].isin(["Real", "Proyectado"])].copy()

    if df_comp.empty:
        return pd.DataFrame(columns=["Subcategoria", "Real", "Proyectado", "Desvio", "AbsDesvio"])

    tabla = (
        df_comp.groupby(["Subcategoria", "Escenario"], as_index=False)["Monto"]
        .sum()
        .pivot(index="Subcategoria", columns="Escenario", values="Monto")
        .fillna(0)
        .reset_index()
    )

    if "Real" not in tabla.columns:
        tabla["Real"] = 0
    if "Proyectado" not in tabla.columns:
        tabla["Proyectado"] = 0

    tabla["Desvio"] = tabla["Real"] - tabla["Proyectado"]
    tabla["AbsDesvio"] = tabla["Desvio"].abs()

    return tabla.sort_values("AbsDesvio", ascending=False)


def construir_base_historica(df_original):
    enero_febrero = df_original[df_original["Mes"].isin(["Enero", "Febrero"])].copy()
    marzo_real = df_original[
        (df_original["Mes"] == "Marzo") &
        (df_original["Escenario"] == "Real")
    ].copy()

    base = pd.concat([enero_febrero, marzo_real], ignore_index=True)
    base["Mes"] = pd.Categorical(base["Mes"], categories=MESES_HISTORICOS, ordered=True)

    return base


def preparar_historico_flujo(base_hist):
    if base_hist.empty:
        return pd.DataFrame(columns=["Mes", "Ingreso", "Egreso", "Flujo"])

    resumen = (
        base_hist.groupby(["Mes", "Tipo"], as_index=False)["Monto"]
        .sum()
        .pivot(index="Mes", columns="Tipo", values="Monto")
        .fillna(0)
        .reset_index()
    )

    if "Ingreso" not in resumen.columns:
        resumen["Ingreso"] = 0
    if "Egreso" not in resumen.columns:
        resumen["Egreso"] = 0

    resumen["Flujo"] = resumen["Ingreso"] - resumen["Egreso"]
    resumen["Mes"] = pd.Categorical(resumen["Mes"], categories=MESES_HISTORICOS, ordered=True)

    return resumen.sort_values("Mes")


def preparar_top10_egresos_historicos(base_hist):
    egresos = base_hist[base_hist["Tipo"] == "Egreso"].copy()

    if egresos.empty:
        return pd.DataFrame(columns=["Subcategoria", "Mes", "Monto"])

    ranking = (
        egresos.groupby("Subcategoria", as_index=False)["Monto"]
        .sum()
        .sort_values("Monto", ascending=False)
        .head(10)
    )

    top10_subcats = ranking["Subcategoria"].tolist()

    comparativa = (
        egresos[egresos["Subcategoria"].isin(top10_subcats)]
        .groupby(["Subcategoria", "Mes"], as_index=False)["Monto"]
        .sum()
    )

    comparativa["Mes"] = pd.Categorical(comparativa["Mes"], categories=MESES_HISTORICOS, ordered=True)

    orden_subcats = (
        comparativa.groupby("Subcategoria")["Monto"]
        .sum()
        .sort_values(ascending=True)
        .index
        .tolist()
    )

    comparativa["Subcategoria"] = pd.Categorical(comparativa["Subcategoria"], categories=orden_subcats, ordered=True)

    return comparativa.sort_values(["Subcategoria", "Mes"])


def mensaje_variacion(variacion):
    if variacion < 0:
        return f"Estamos {format_currency_short(variacion)} por debajo de lo esperado."
    if variacion > 0:
        return f"Estamos {format_currency_short(variacion)} por encima de lo esperado."
    return "Estamos exactamente en línea con lo proyectado."


def mensaje_ingresos_egresos(ing_real, ing_proy, egr_real, egr_proy):
    delta_ing = ing_real - ing_proy
    delta_egr = egr_real - egr_proy

    lectura_ing = "ingresos por encima de lo proyectado" if delta_ing > 0 else "ingresos por debajo de lo proyectado" if delta_ing < 0 else "ingresos alineados con lo proyectado"
    lectura_egr = "gastos por encima de lo proyectado" if delta_egr > 0 else "gastos por debajo de lo proyectado" if delta_egr < 0 else "gastos alineados con lo proyectado"

    return f"La comparación general muestra {lectura_ing} y {lectura_egr}."


def mensaje_concentracion(df_desvios):
    if df_desvios.empty:
        return "No hay desvíos suficientes para analizar concentración."

    total_abs = df_desvios["AbsDesvio"].sum()

    if total_abs == 0:
        return "No hay desvíos relevantes para analizar concentración."

    top5_abs = df_desvios.head(5)["AbsDesvio"].sum()
    top2_abs = df_desvios.head(2)["AbsDesvio"].sum()

    porcentaje_top5 = (top5_abs / total_abs) * 100
    porcentaje_top2 = (top2_abs / total_abs) * 100

    return (
        f"Los 5 mayores desvíos explican {porcentaje_top5:.1f}% del desvío total. "
        f"Los 2 principales explican {porcentaje_top2:.1f}%."
    )


def mensaje_tendencia_historica(flujo_hist):
    if flujo_hist.empty:
        return "No hay suficientes datos para comparar contra meses anteriores."

    if len(flujo_hist) < 2:
        return "Todavía no hay suficientes meses para analizar tendencia."

    primero = flujo_hist.iloc[0]["Flujo"]
    ultimo = flujo_hist.iloc[-1]["Flujo"]

    if ultimo > primero:
        return "El flujo de caja muestra una mejora frente al inicio del período comparado."
    if ultimo < primero:
        return "El flujo de caja muestra un deterioro frente al inicio del período comparado."
    return "El flujo de caja se mantiene estable frente a meses anteriores."


def crear_fig_bar_simple(df_plot, x, y, color=None, orientation=None, title=""):
    fig = px.bar(
        df_plot,
        x=x,
        y=y,
        color=color,
        orientation=orientation,
        title=title,
        color_discrete_map={
            "Real": COLOR_REAL,
            "Proyectado": COLOR_PROY,
            "Enero": "#4C78FF",
            "Febrero": "#7F8A9A",
            "Marzo": "#C97A2B"
        } if color else None
    )

    fig.update_layout(
        paper_bgcolor=COLOR_CARD,
        plot_bgcolor=COLOR_CARD,
        font=dict(color=COLOR_TEXT),
        title_font=dict(size=18, color=COLOR_TEXT),
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color=COLOR_TEXT_SOFT)
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor="rgba(255,255,255,0.08)",
            zeroline=False,
            color=COLOR_TEXT_SOFT
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            color=COLOR_TEXT_SOFT
        )
    )

    return fig


def crear_fig_linea(df_plot, x, y, title=""):
    fig = px.line(
        df_plot,
        x=x,
        y=y,
        markers=True,
        title=title
    )

    fig.update_traces(line_color=COLOR_REAL, marker_color=COLOR_PROY, marker_size=10)

    fig.update_layout(
        paper_bgcolor=COLOR_CARD,
        plot_bgcolor=COLOR_CARD,
        font=dict(color=COLOR_TEXT),
        title_font=dict(size=18, color=COLOR_TEXT),
        margin=dict(l=20, r=20, t=50, b=20),
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            color=COLOR_TEXT_SOFT
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(255,255,255,0.08)",
            zeroline=False,
            color=COLOR_TEXT_SOFT
        )
    )

    return fig


def render_kpi_card(label, value):
    st.markdown(
        f"""
        <div class="premium-card">
            <div class="label">{label}</div>
            <div class="value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# =========================================================
# CARGA DE DATOS
# =========================================================
df = cargar_datos()

# =========================================================
# RESET FILTROS
# =========================================================
if st.sidebar.button("Resetear filtros"):
    st.session_state["meses_sel"] = ["Marzo"]
    st.session_state["tipos_sel"] = ["Ingreso", "Egreso"]
    st.session_state["escenarios_sel"] = ["Real", "Proyectado"]

# Defaults seguros
if "meses_sel" not in st.session_state:
    st.session_state["meses_sel"] = ["Marzo"]

if "tipos_sel" not in st.session_state:
    st.session_state["tipos_sel"] = ["Ingreso", "Egreso"]

if "escenarios_sel" not in st.session_state:
    st.session_state["escenarios_sel"] = ["Real", "Proyectado"]

# =========================================================
# TÍTULO
# =========================================================
st.markdown(
    """
    <div style="margin-bottom: 1rem;">
        <h1 style="margin-bottom: 0.15rem;">📊 Dashboard Flujo de Caja - Sol Huevos</h1>
        <div class="small-muted">Análisis de flujo de caja: resultado, desvíos y comparación histórica</div>
    </div>
    """,
    unsafe_allow_html=True
)

# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.markdown("## Filtros")

meses_disponibles = [m for m in MESES_ORDEN if m in df["Mes"].astype(str).unique()]
tipos_disponibles = ["Ingreso", "Egreso"]
escenarios_disponibles = ["Real", "Proyectado", "Sin escenario"]

meses_sel = st.sidebar.multiselect(
    "Mes",
    options=meses_disponibles,
    key="meses_sel"
)

tipos_sel = st.sidebar.multiselect(
    "Tipo",
    options=tipos_disponibles,
    key="tipos_sel"
)

escenarios_sel = st.sidebar.multiselect(
    "Escenario",
    options=escenarios_disponibles,
    key="escenarios_sel"
)

df_filtrado = aplicar_filtros(df, meses_sel, tipos_sel, escenarios_sel)

if df_filtrado.empty:
    st.warning("No hay datos con los filtros seleccionados.")
    st.stop()

# =========================================================
# CÁLCULOS PRINCIPALES
# =========================================================
ingreso_real = calcular_total(df_filtrado, "Ingreso", "Real")
ingreso_proyectado = calcular_total(df_filtrado, "Ingreso", "Proyectado")
egreso_real = calcular_total(df_filtrado, "Egreso", "Real")
egreso_proyectado = calcular_total(df_filtrado, "Egreso", "Proyectado")

flujo_real = ingreso_real - egreso_real
flujo_proyectado = ingreso_proyectado - egreso_proyectado
variacion_flujo = flujo_real - flujo_proyectado

comparacion_ingresos = preparar_comparacion_tipo(df_filtrado, "Ingreso")
comparacion_egresos = preparar_comparacion_tipo(df_filtrado, "Egreso")
df_desvios = preparar_desvios(df_filtrado)

base_hist = construir_base_historica(df)
base_hist = base_hist[base_hist["Mes"].isin([m for m in meses_sel if m in MESES_HISTORICOS])].copy()

flujo_historico = preparar_historico_flujo(base_hist)
top10_egresos_historicos = preparar_top10_egresos_historicos(base_hist)

# =========================================================
# 1) RESULTADO
# =========================================================
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">1️⃣ Resultado</div>', unsafe_allow_html=True)
st.markdown('<div class="section-subtitle">¿Cómo estamos respecto a lo esperado?</div>', unsafe_allow_html=True)

k1, k2, k3 = st.columns(3)
with k1:
    render_kpi_card("💰 Flujo Real", format_currency(flujo_real))
with k2:
    render_kpi_card("🎯 Flujo Proyectado", format_currency(flujo_proyectado))
with k3:
    render_kpi_card("📉 Variación", format_currency(variacion_flujo))

if variacion_flujo < 0:
    st.markdown(
        f'<div class="status-box-negative">{mensaje_variacion(variacion_flujo)}</div>',
        unsafe_allow_html=True
    )
elif variacion_flujo > 0:
    st.markdown(
        f'<div class="status-box-positive">{mensaje_variacion(variacion_flujo)}</div>',
        unsafe_allow_html=True
    )
else:
    st.markdown(
        f'<div class="status-box-neutral">{mensaje_variacion(variacion_flujo)}</div>',
        unsafe_allow_html=True
    )

st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# 2) COMPARACIÓN
# =========================================================
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">2️⃣ Comparación</div>', unsafe_allow_html=True)
st.markdown('<div class="section-subtitle">¿El problema viene de ingresos o de egresos?</div>', unsafe_allow_html=True)

col_a, col_b = st.columns(2)

with col_a:
    st.markdown("**Ingreso Real vs Proyectado**")
    if comparacion_ingresos.empty:
        st.info("No hay datos suficientes de ingresos.")
    else:
        fig_ing = crear_fig_bar_simple(
            comparacion_ingresos,
            x="Escenario",
            y="Monto",
            color="Escenario",
            title="Ingresos"
        )
        fig_ing.update_layout(showlegend=False)
        st.plotly_chart(fig_ing, width="stretch")

with col_b:
    st.markdown("**Egreso Real vs Proyectado**")
    if comparacion_egresos.empty:
        st.info("No hay datos suficientes de egresos.")
    else:
        fig_egr = crear_fig_bar_simple(
            comparacion_egresos,
            x="Escenario",
            y="Monto",
            color="Escenario",
            title="Egresos"
        )
        fig_egr.update_layout(showlegend=False)
        st.plotly_chart(fig_egr, width="stretch")

st.markdown(
    f'<div class="note-box">{mensaje_ingresos_egresos(ingreso_real, ingreso_proyectado, egreso_real, egreso_proyectado)}</div>',
    unsafe_allow_html=True
)
st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# 3) CAUSAS
# =========================================================
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">3️⃣ Causas</div>', unsafe_allow_html=True)
st.markdown('<div class="section-subtitle">¿Qué subcategorías explican el desvío?</div>', unsafe_allow_html=True)

if df_desvios.empty:
    st.info("No hay datos suficientes para analizar desvíos.")
else:
    top_desvios = df_desvios.head(10).copy().sort_values("Desvio")

    fig_desvios = crear_fig_bar_simple(
        top_desvios,
        x="Desvio",
        y="Subcategoria",
        orientation="h",
        title="Top desvíos por subcategoría (Real - Proyectado)"
    )
    fig_desvios.update_traces(marker_color=COLOR_REAL)
    fig_desvios.update_layout(height=520)
    st.plotly_chart(fig_desvios, width="stretch")

    principal = df_desvios.iloc[0]
    st.markdown(
        f'<div class="warning-box">El mayor desvío proviene de <b>{principal["Subcategoria"]}</b> con un desvío de <b>{format_currency(principal["Desvio"])}</b>.</div>',
        unsafe_allow_html=True
    )

st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# 4) CONCENTRACIÓN
# =========================================================
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">4️⃣ Concentración</div>', unsafe_allow_html=True)
st.markdown('<div class="section-subtitle">¿El problema está concentrado o repartido?</div>', unsafe_allow_html=True)

if df_desvios.empty:
    st.info("No hay datos suficientes para analizar concentración.")
else:
    total_abs = df_desvios["AbsDesvio"].sum()

    if total_abs == 0:
        st.info("No hay desvíos relevantes para analizar concentración.")
    else:
        top_pareto = df_desvios.head(5).copy()

        cp1, cp2 = st.columns([2, 1])

        with cp1:
            fig_pareto = crear_fig_bar_simple(
                top_pareto,
                x="Subcategoria",
                y="AbsDesvio",
                title="Top 5 desvíos por impacto"
            )
            fig_pareto.update_traces(marker_color=COLOR_REAL)
            st.plotly_chart(fig_pareto, width="stretch")

        with cp2:
            st.markdown("**Lectura de concentración**")
            st.markdown(
                f'<div class="note-box">{mensaje_concentracion(df_desvios)}</div>',
                unsafe_allow_html=True
            )

st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# 5) DETALLE
# =========================================================
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">5️⃣ Detalle</div>', unsafe_allow_html=True)
st.markdown('<div class="section-subtitle">Profundización por subcategoría.</div>', unsafe_allow_html=True)

if df_desvios.empty:
    st.info("No hay detalle para mostrar.")
else:
    detalle = df_desvios[["Subcategoria", "Proyectado", "Real", "Desvio", "AbsDesvio"]].copy()
    detalle = detalle.sort_values("AbsDesvio", ascending=False)

    st.dataframe(detalle, width="stretch")

st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# 6) COMPARACIÓN A MESES ANTERIORES
# =========================================================
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">6️⃣ ¿Cómo estamos en comparación a meses anteriores?</div>', unsafe_allow_html=True)
st.markdown('<div class="section-subtitle">Enero y febrero ignoran escenario. Marzo toma solo Real.</div>', unsafe_allow_html=True)

if flujo_historico.empty:
    st.info("No hay datos suficientes para analizar meses anteriores.")
else:
    t1, t2 = st.columns(2)

    with t1:
        fig_flujo = crear_fig_linea(
            flujo_historico,
            x="Mes",
            y="Flujo",
            title="Flujo de caja mensual"
        )
        st.plotly_chart(fig_flujo, width="stretch")

    with t2:
        st.markdown("**Lectura de tendencia**")
        st.markdown(
            f'<div class="note-box">{mensaje_tendencia_historica(flujo_historico)}</div>',
            unsafe_allow_html=True
        )

    g1, g2 = st.columns(2)

    with g1:
        fig_ingresos_hist = crear_fig_bar_simple(
            flujo_historico,
            x="Mes",
            y="Ingreso",
            title="Ingresos mensuales"
        )
        fig_ingresos_hist.update_traces(marker_color=COLOR_REAL)
        st.plotly_chart(fig_ingresos_hist, width="stretch")

    with g2:
        fig_egresos_hist = crear_fig_bar_simple(
            flujo_historico,
            x="Mes",
            y="Egreso",
            title="Egresos mensuales"
        )
        fig_egresos_hist.update_traces(marker_color=COLOR_PROY)
        st.plotly_chart(fig_egresos_hist, width="stretch")

    if top10_egresos_historicos.empty:
        st.info("No hay egresos suficientes para comparar los top 10 entre los 3 meses.")
    else:
        fig_top10 = crear_fig_bar_simple(
            top10_egresos_historicos,
            x="Monto",
            y="Subcategoria",
            color="Mes",
            orientation="h",
            title="Comparativa de los Top 10 egresos principales entre enero, febrero y marzo"
        )
        fig_top10.update_layout(height=650)
        st.plotly_chart(fig_top10, width="stretch")

st.markdown("</div>", unsafe_allow_html=True)

with st.expander("Ver datos filtrados base"):
    st.dataframe(df_filtrado, width="stretch")
