"""
Tab 5 · Consulta DEE — Declaratorias de Estado de Emergencia.
"""
import pandas as pd
import plotly.express as px
import streamlit as st
from modules.config import TOKENS


def render_dee(ctx: dict):
    dee: pd.DataFrame = ctx.get("dee", pd.DataFrame())
    sol: pd.DataFrame = ctx.get("sol", pd.DataFrame())

    st.markdown("### 🚨 Declaratorias de Estado de Emergencia (DEE)")

    if dee.empty:
        st.warning(
            "No se cargó el archivo T_DEE.xlsx. "
            "Sube el archivo en la barra lateral para consultar las declaratorias."
        )
        if not sol.empty:
            st.info("💡 El T_SOLICITUDES.xlsx sí está cargado — "
                    "las fichas técnicas mostrarán DEE cuando cargues T_DEE.xlsx.")
        return

    # ── Filtros ────────────────────────────────────────────────────────────────
    col_f1, col_f2 = st.columns(2)
    dept_col = _fc(dee, ["Departamento", "departamento"])
    with col_f1:
        depts = ["Todos"] + (sorted(dee[dept_col].dropna().unique().tolist()) if dept_col else [])
        dept_sel = st.selectbox("Departamento", depts, key="dee_dept")

    evento_col = _fc(dee, ["Evento", "evento", "Tipo", "tipo"])
    with col_f2:
        eventos = ["Todos"] + (sorted(dee[evento_col].dropna().unique().tolist()) if evento_col else [])
        evento_sel = st.selectbox("Tipo de evento", eventos, key="dee_evento")

    df = dee.copy()
    if dept_sel != "Todos" and dept_col:
        df = df[df[dept_col] == dept_sel]
    if evento_sel != "Todos" and evento_col:
        df = df[df[evento_col] == evento_sel]

    # ── Métricas ───────────────────────────────────────────────────────────────
    ds_col = _fc(dee, ["El Peruano DS_N°", "DS_N°", "DS N°", "Decreto"])
    n_ds = df[ds_col].nunique() if ds_col and ds_col in df.columns else len(df)

    c1, c2, c3 = st.columns(3)
    c1.metric("Registros DEE", len(df))
    c2.metric("Decretos Supremos únicos", n_ds)
    c3.metric("Departamentos", df[dept_col].nunique() if dept_col else "—")

    st.divider()

    # ── Tabla ─────────────────────────────────────────────────────────────────
    st.markdown(f"#### Listado ({len(df)} registros)")
    st.dataframe(df, use_container_width=True, hide_index=True, height=350)

    # ── Gráfico por departamento ───────────────────────────────────────────────
    if dept_col and dept_col in df.columns:
        st.markdown("#### Distribución por departamento")
        counts = df[dept_col].value_counts().head(15)
        fig = px.bar(
            x=counts.values, y=counts.index, orientation="h",
            color=counts.values,
            color_continuous_scale=[[0, "#7f1d1d"], [1, "#ef4444"]],
            text=counts.values,
        )
        fig.update_layout(
            height=380,
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color=TOKENS["text_muted"],
            margin=dict(l=10, r=10, t=20, b=10),
            showlegend=False, coloraxis_showscale=False,
        )
        fig.update_traces(textposition="outside", textfont_color=TOKENS["text_muted"])
        st.plotly_chart(fig, use_container_width=True)

    # ── Solicitudes vinculadas ────────────────────────────────────────────────
    if not sol.empty and "UBIGEO_KEY" in dee.columns and "UBIGEO_KEY" in sol.columns:
        ubigeos_dee = set(df["UBIGEO_KEY"].dropna().unique())
        vinculadas  = sol[sol["UBIGEO_KEY"].isin(ubigeos_dee)]
        if not vinculadas.empty:
            st.divider()
            st.markdown(f"#### 📋 Solicitudes vinculadas a esta DEE ({len(vinculadas)})")
            id_col = _fc(sol, ["N° Solicitud"])
            cols   = [c for c in [id_col, "Entidad", "ETAPA_ACTUAL", "Proceso GRD"] if c and c in sol.columns]
            st.dataframe(vinculadas[cols], use_container_width=True, hide_index=True)


def _fc(df: pd.DataFrame, candidates: list):
    for c in candidates:
        if c in df.columns:
            return c
        for col in df.columns:
            if c.lower() in col.lower():
                return col
    return None
