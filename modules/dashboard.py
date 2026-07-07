"""
Tab 1 · Dashboard principal con métricas y gráficos.
"""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from modules.config import metric_card, ETAPAS_FLUJO, BADGE_ETAPA, TOKENS


_PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font_color=TOKENS["text_muted"],
    margin=dict(l=10, r=10, t=30, b=10),
)


def render_dashboard(ctx: dict):
    sol: pd.DataFrame = ctx.get("sol", pd.DataFrame())
    if sol.empty:
        st.info("Carga el archivo T_SOLICITUDES.xlsx para ver el dashboard.")
        return

    if ctx.get("demo_mode"):
        st.info("🔵 **Modo demostración** — datos sintéticos de ejemplo.")

    # ── Métricas principales ─────────────────────────────────────────────────
    total    = len(sol)
    avanzadas = sol[sol["_n_etapas"] >= 4].shape[0] if "_n_etapas" in sol.columns else 0
    en_eval  = sol[sol["ETAPA_ACTUAL"].isin(["Fecha Evaluación", "Fecha Admisión"])].shape[0]
    aprobadas= sol[sol["ETAPA_ACTUAL"].isin(["Fecha Aprobación", "Fecha Ejecución", "Fecha Cierre", "Fecha Liquidación"])].shape[0]

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(metric_card(total,     "Total solicitudes"), unsafe_allow_html=True)
    c2.markdown(metric_card(aprobadas, "Aprobadas / Ejecución", "green"), unsafe_allow_html=True)
    c3.markdown(metric_card(en_eval,   "En evaluación",    "orange"), unsafe_allow_html=True)
    c4.markdown(metric_card(total - avanzadas, "Etapas tempranas", "red"), unsafe_allow_html=True)

    st.divider()

    # ── Gráficos ─────────────────────────────────────────────────────────────
    col_a, col_b = st.columns([3, 2])

    with col_a:
        st.markdown("#### Por etapa de flujo")
        etapa_counts = (
            sol["ETAPA_ACTUAL"]
            .value_counts()
            .reindex(ETAPAS_FLUJO + ["Sin etapa"], fill_value=0)
        )
        etapa_counts = etapa_counts[etapa_counts > 0]
        colors = [
            TOKENS["success"] if BADGE_ETAPA.get(e) == "green"
            else TOKENS["primary"] if BADGE_ETAPA.get(e) == "blue"
            else TOKENS["warning"] if BADGE_ETAPA.get(e) == "orange"
            else "#4B5563"
            for e in etapa_counts.index
        ]
        fig_etapa = go.Figure(go.Bar(
            x=etapa_counts.values,
            y=[e.replace("Fecha ", "") for e in etapa_counts.index],
            orientation="h",
            marker_color=colors,
            text=etapa_counts.values,
            textposition="outside",
            textfont_color=TOKENS["text_muted"],
        ))
        fig_etapa.update_layout(**_PLOTLY_LAYOUT, height=320, xaxis_showgrid=False)
        st.plotly_chart(fig_etapa, use_container_width=True)

    with col_b:
        st.markdown("#### Por proceso")
        proc_col = _find_col(sol, ["Proceso GRD", "Proceso", "proceso"])
        if proc_col:
            proc_counts = sol[proc_col].value_counts()
            fig_proc = px.pie(
                values=proc_counts.values,
                names=proc_counts.index,
                color_discrete_sequence=[TOKENS["primary"], TOKENS["secondary"], TOKENS["success"]],
                hole=.45,
            )
            fig_proc.update_layout(**_PLOTLY_LAYOUT, height=320,
                                   legend=dict(orientation="h", y=-.1))
            fig_proc.update_traces(textfont_color="white")
            st.plotly_chart(fig_proc, use_container_width=True)
        else:
            st.caption("Columna de proceso no encontrada.")

    # ── Por departamento ─────────────────────────────────────────────────────
    dept_col = _find_col(sol, ["Departamento", "departamento", "DEPARTAMENTO"])
    if dept_col:
        st.markdown("#### Por departamento")
        dept_counts = sol[dept_col].value_counts().head(15)
        fig_dept = px.bar(
            x=dept_counts.values,
            y=dept_counts.index,
            orientation="h",
            color=dept_counts.values,
            color_continuous_scale=[[0, "#1B5C9E"], [1, "#3B82F6"]],
            text=dept_counts.values,
        )
        fig_dept.update_layout(
            **_PLOTLY_LAYOUT, height=380,
            showlegend=False, coloraxis_showscale=False,
            xaxis_showgrid=False,
        )
        fig_dept.update_traces(textposition="outside", textfont_color=TOKENS["text_muted"])
        st.plotly_chart(fig_dept, use_container_width=True)

    # ── Tabla resumen reciente ───────────────────────────────────────────────
    st.markdown("#### Últimas solicitudes ingresadas")
    cols_show = [c for c in ["N° Solicitud", "Entidad", "Departamento", "Proceso GRD", "ETAPA_ACTUAL"]
                 if c in sol.columns]
    if cols_show:
        st.dataframe(
            sol[cols_show].head(20),
            use_container_width=True,
            hide_index=True,
        )


def _find_col(df: pd.DataFrame, candidates: list):
    for c in candidates:
        if c in df.columns:
            return c
        for col in df.columns:
            if c.lower() in col.lower():
                return col
    return None
