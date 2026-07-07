"""
Tab 4 · Estadísticas — análisis gráfico de solicitudes.
"""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from modules.config import ETAPAS_FLUJO, TOKENS


_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font_color=TOKENS["text_muted"],
    margin=dict(l=10, r=10, t=35, b=10),
)


def render_estadisticas(ctx: dict):
    sol: pd.DataFrame = ctx.get("sol", pd.DataFrame())
    if sol.empty:
        st.info("Carga T_SOLICITUDES.xlsx para ver estadísticas.")
        return

    # ── Filtros ────────────────────────────────────────────────────────────────
    st.markdown("### 📈 Estadísticas")

    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        proc_col = _fc(sol, ["Proceso GRD", "Proceso"])
        procesos = ["Todos"] + (sorted(sol[proc_col].dropna().unique().tolist()) if proc_col else [])
        proc_sel = st.selectbox("Proceso", procesos, key="est_proc")

    with col_f2:
        dept_col = _fc(sol, ["Departamento", "departamento"])
        depts = ["Todos"] + (sorted(sol[dept_col].dropna().unique().tolist()) if dept_col else [])
        dept_sel = st.selectbox("Departamento", depts, key="est_dept")

    with col_f3:
        etapas = ["Todas"] + ETAPAS_FLUJO + ["Sin etapa"]
        etapa_sel = st.selectbox("Etapa", etapas, key="est_etapa")

    # Aplicar filtros
    df = sol.copy()
    if proc_sel != "Todos" and proc_col:
        df = df[df[proc_col] == proc_sel]
    if dept_sel != "Todos" and dept_col:
        df = df[df[dept_col] == dept_sel]
    if etapa_sel != "Todas":
        df = df[df["ETAPA_ACTUAL"] == etapa_sel]

    st.caption(f"Mostrando **{len(df)}** solicitudes con los filtros seleccionados.")
    st.divider()

    # ── Distribución por etapa ─────────────────────────────────────────────────
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("##### Distribución por etapa")
        _bar_etapas(df)
    with col_b:
        st.markdown("##### Distribución por proceso")
        _pie_proceso(df, proc_col)

    st.divider()

    # ── Evolución temporal ────────────────────────────────────────────────────
    st.markdown("##### Evolución de ingresos")
    _line_ingresos(df)

    st.divider()

    # ── Departamentos ─────────────────────────────────────────────────────────
    col_c, col_d = st.columns(2)
    with col_c:
        st.markdown("##### Top 10 departamentos")
        _bar_departamentos(df, dept_col)
    with col_d:
        st.markdown("##### Matriz proceso × etapa")
        _heatmap_proceso_etapa(df, proc_col)


# ── Gráficos ───────────────────────────────────────────────────────────────────

def _bar_etapas(df: pd.DataFrame):
    counts = (
        df["ETAPA_ACTUAL"].value_counts()
        .reindex(ETAPAS_FLUJO + ["Sin etapa"], fill_value=0)
    )
    counts = counts[counts > 0]
    if counts.empty:
        st.caption("Sin datos.")
        return
    fig = go.Figure(go.Bar(
        x=counts.values,
        y=[e.replace("Fecha ", "") for e in counts.index],
        orientation="h",
        marker_color=TOKENS["accent"],
        text=counts.values,
        textposition="outside",
        textfont_color=TOKENS["text_muted"],
    ))
    fig.update_layout(**_LAYOUT, height=300, xaxis_showgrid=False)
    st.plotly_chart(fig, use_container_width=True)


def _pie_proceso(df: pd.DataFrame, proc_col):
    if not proc_col or proc_col not in df.columns:
        st.caption("Columna de proceso no encontrada.")
        return
    counts = df[proc_col].value_counts()
    fig = px.pie(
        values=counts.values, names=counts.index, hole=.4,
        color_discrete_sequence=[TOKENS["primary"], TOKENS["secondary"], TOKENS["success"]],
    )
    fig.update_layout(**_LAYOUT, height=300, legend=dict(orientation="h", y=-.15))
    fig.update_traces(textfont_color="white")
    st.plotly_chart(fig, use_container_width=True)


def _line_ingresos(df: pd.DataFrame):
    fecha_col = _fc(df, ["Fecha Ingreso", "Fecha Admisión"])
    if not fecha_col or fecha_col not in df.columns:
        st.caption("No hay columna de fecha de ingreso.")
        return
    serie = (
        pd.to_datetime(df[fecha_col], errors="coerce")
        .dropna()
        .dt.to_period("M")
        .astype(str)
        .value_counts()
        .sort_index()
    )
    if serie.empty:
        st.caption("Sin datos de fechas.")
        return
    fig = go.Figure(go.Scatter(
        x=serie.index, y=serie.values,
        mode="lines+markers",
        line=dict(color=TOKENS["accent"], width=2),
        marker=dict(color=TOKENS["accent"], size=6),
        fill="tozeroy", fillcolor="rgba(59,130,246,.15)",
    ))
    fig.update_layout(**_LAYOUT, height=250)
    st.plotly_chart(fig, use_container_width=True)


def _bar_departamentos(df: pd.DataFrame, dept_col):
    if not dept_col or dept_col not in df.columns:
        st.caption("Columna de departamento no encontrada.")
        return
    counts = df[dept_col].value_counts().head(10)
    fig = px.bar(
        x=counts.values, y=counts.index, orientation="h",
        color=counts.values,
        color_continuous_scale=[[0, "#1B5C9E"], [1, "#3B82F6"]],
        text=counts.values,
    )
    fig.update_layout(**_LAYOUT, height=320, showlegend=False, coloraxis_showscale=False, xaxis_showgrid=False)
    fig.update_traces(textposition="outside", textfont_color=TOKENS["text_muted"])
    st.plotly_chart(fig, use_container_width=True)


def _heatmap_proceso_etapa(df: pd.DataFrame, proc_col):
    if not proc_col or proc_col not in df.columns:
        st.caption("Columna de proceso no encontrada.")
        return
    pivot = pd.crosstab(df[proc_col], df["ETAPA_ACTUAL"])
    etapas_presentes = [e for e in ETAPAS_FLUJO + ["Sin etapa"] if e in pivot.columns]
    if not etapas_presentes:
        st.caption("Sin datos.")
        return
    pivot = pivot[etapas_presentes]
    fig = px.imshow(
        pivot,
        color_continuous_scale="Blues",
        text_auto=True,
        aspect="auto",
    )
    fig.update_layout(**_LAYOUT, height=320)
    fig.update_xaxes(tickangle=-30)
    st.plotly_chart(fig, use_container_width=True)


# ── helpers ────────────────────────────────────────────────────────────────────

def _fc(df: pd.DataFrame, candidates: list):
    for c in candidates:
        if c in df.columns:
            return c
        for col in df.columns:
            if c.lower() in col.lower():
                return col
    return None
