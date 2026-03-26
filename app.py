import streamlit as st
import pandas as pd
import plotly.express as px

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

COLOR_BG = "#0F1115"
COLOR_CARD = "#171A21"
COLOR_BORDER = "#262B36"
COLOR_TEXT = "#F3F4F6"
COLOR_TEXT_SOFT = "#AAB2C0"
COLOR_REAL = "#4C78FF"
COLOR_PROY = "#C97A2B"
COLOR_NEG = "#C84B4B"
COLOR_POS = "#2E8B57"
COLOR_HIST = "#7F8A9A"

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

        div[data-testid="stFileUploader"] {{
            background: {COLOR_CARD};
            border: 1px solid {COLOR_BORDER};
            border-radius: 16px;
            padding: 8px;
        }}

        div[data-testid="stDataFrame"] {{
            border: 1px solid {COLOR_BORDER};
            border-radius: 14px;
            overflow: hidden;
        }}

        div[data-baseweb="select"] > div {{
            background-color: #1A1F29 !important;
            border-color: {COLOR_BORDER} !important;
        }}

        .stMultiSelect [data-baseweb="tag"] {{
            background-color: #202633 !important;
            border: 1px solid {COLOR_BORDER} !important;
        }}
    </style>
    """,
    unsafe_allow_html=True
)

# =========================================================
# FUNCIONES AUXILIARES
# =========================================================
def normalizar_texto(valor):
    if pd.isna(valor):
        return None
    return str(valor).strip()


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


@st.cache_data
def cargar_datos_excel(uploaded_file):
    xls = pd.ExcelFile(uploaded_file)
    hoja_a_usar = "Limpio" if "Limpio" in xls.sheet_names else xls.sheet_names[0]
    df = pd.read_excel(uploaded_file, sheet_name=hoja_a_usar)

    df.columns = [str(col).strip() for col in df.columns]

    columnas_esperadas = [
        "Fecha", "Mes", "Tipo", "Categoria", "Subcategoria", "Monto", "Escenario"
    ]
    faltantes = [col for col in columnas_esperadas if col not in df.columns]
    if faltantes:
        raise ValueError(f"Faltan columnas obligatorias: {', '.join(faltantes)}")

    df = df.copy()

    for col in ["Mes", "Tipo", "Categoria", "Subcategoria", "Escenario"]:
        df[col] = df[col].apply(normalizar_texto)

    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
    df["Monto"] = pd.to_numeric(df["Monto"], errors="coerce").fillna(0)

    df["Tipo"] = df["Tipo"].replace({
        "ingreso": "Ingreso",
        "egreso": "Egreso",
        "INGRESO": "Ingreso",
        "EGRESO": "Egreso"
    })

    df["Escenario"] = df["Escenario"].replace({
        "real": "Real",
        "proyectado": "Proyectado",
        "REAL": "Real",
        "PROYECTADO": "Proyectado"
    })

    mapa_meses_num = {
        1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
        5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
        9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
    }

    df["Mes"] = df["Mes"].fillna(df["Fecha"].dt.month.map(mapa_meses_num))
    df["Categoria"] = df["Categoria"].fillna("Sin categoría")
    df["Subcategoria"] = df["Subcategoria"].fillna("Sin subcategoría")
    df["Escenario"] = df["Escenario"].fillna("Sin escenario")
    df["Mes"] = df["Mes"].fillna("Sin mes")
    df["Tipo"] = df["Tipo"].fillna("Sin tipo")

    df["Mes"] = pd.Categorical(df["Mes"], categories=MESES_ORDEN, ordered=True)

    return df


def aplicar_filtros(df, meses_sel, tipos_sel, escenarios_sel):
    df_filtrado = df.copy()

    if meses_sel:
        df_filtrado = df_filtrado[df_filtrado["Mes"].isin(meses_sel)]

    if tipos_sel:
        df_filtrado = df_filtrado[df_filtrado["Tipo"].isin(tipos_sel)]

    if escenarios_sel:
        df_filtrado = df_filtrado[df_filtrado["Escenario"].isin(escenarios_sel)]

    return df_filtrado


def calcular_total(df, tipo, escenario):
    filtro = (df["Tipo"] == tipo) & (df["Escenario"] == escenario)
    return df.loc[filtro, "Monto"].sum()


def preparar_comparacion_tipo(df_base, tipo):
    df_tipo = df_base[
        (df_base["Tipo"] == tipo) &
        (df_base["Escenario"].isin(["Real", "Proyectado"]))
    ].copy()

    if df_tipo.empty:
        return pd.DataFrame(columns=["Escenario", "Monto"])

    return df_tipo.groupby("Escenario", as_index=False)["Monto"].sum()


def preparar_desvios(df_base):
    df_comp = df_base[
        df_base["Escenario"].isin(["Real", "Proyectado"])
    ].copy()

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
    tabla = tabla.sort_values("AbsDesvio", ascending=False)

    return tabla


def construir_base_historica(df_original):
    """
    Lógica pedida:
    - Enero y Febrero: ignorar Escenario
    - Marzo: usar solo Escenario = Real
    """
    df_hist = df_original[df_original["Mes"].isin(MESES_HISTORICOS)].copy()

    enero_febrero = df_hist[df_hist["Mes"].isin(["Enero", "Febrero"])].copy()
    marzo_real = df_hist[
        (df_hist["Mes"] == "Marzo") &
        (df_hist["Escenario"] == "Real")
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
    resumen = resumen.sort_values("Mes")

    return resumen


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
    comparativa = comparativa.sort_values(["Subcategoria", "Mes"])

    return comparativa


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
    lectura_egr = "egresos por encima de lo proyectado" if delta_egr > 0 else "egresos por debajo de lo proyectado" if delta_egr < 0 else "egresos alineados con lo proyectado"

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

uploaded_file = st.file_uploader("Subí tu archivo Excel", type=["xlsx", "xls"])

if uploaded_file is None:
    st.info("Subí tu archivo Excel para comenzar.")
    st.stop()

try:
    df = cargar_datos_excel(uploaded_file)
except Exception as e:
    st.error(f"Error al leer el archivo: {e}")
    st.stop()

if df.empty:
    st.warning("El archivo no contiene datos válidos.")
    st.stop()

# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.markdown("## Filtros")

meses_disponibles = [m for m in MESES_ORDEN if m in df["Mes"].astype(str).unique()]
tipos_disponibles = [t for t in ["Ingreso", "Egreso"] if t in df["Tipo"].dropna().unique()]
escenarios_disponibles = [e for e in ["Real", "Proyectado", "Sin escenario"] if e in df["Escenario"].dropna().unique()]

meses_sel = st.sidebar.multiselect(
    "Mes",
    options=meses_disponibles,
    default=meses_disponibles
)

tipos_sel = st.sidebar.multiselect(
    "Tipo",
    options=tipos_disponibles,
    default=tipos_disponibles
)

escenarios_sel = st.sidebar.multiselect(
    "Escenario",
    options=escenarios_disponibles,
    default=escenarios_disponibles
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

# Base histórica independiente de filtros de escenario
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
        st.plotly_chart(fig_ing, use_container_width=True)

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
        st.plotly_chart(fig_egr, use_container_width=True)

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
    st.plotly_chart(fig_desvios, use_container_width=True)

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
            st.plotly_chart(fig_pareto, use_container_width=True)

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
    detalle = df_desvios[["Subcategoria", "Real", "Proyectado", "Desvio"]].copy()
    detalle = detalle.sort_values("Desvio", ascending=False)

    st.dataframe(detalle, use_container_width=True)

st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# 6) COMPARACIÓN A MESES ANTERIORES
# =========================================================
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">6️⃣ ¿Cómo estamos en comparación a meses anteriores?</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-subtitle">Enero y febrero ignoran escenario. Marzo toma solo Real.</div>',
    unsafe_allow_html=True
)

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
        st.plotly_chart(fig_flujo, use_container_width=True)

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
        st.plotly_chart(fig_ingresos_hist, use_container_width=True)

    with g2:
        fig_egresos_hist = crear_fig_bar_simple(
            flujo_historico,
            x="Mes",
            y="Egreso",
            title="Egresos mensuales"
        )
        fig_egresos_hist.update_traces(marker_color=COLOR_PROY)
        st.plotly_chart(fig_egresos_hist, use_container_width=True)

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
        st.plotly_chart(fig_top10, use_container_width=True)

st.markdown("</div>", unsafe_allow_html=True)

with st.expander("Ver datos filtrados base"):
    st.dataframe(df_filtrado, use_container_width=True)
