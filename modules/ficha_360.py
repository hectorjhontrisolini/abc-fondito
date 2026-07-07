"""
Tab 3 · Ficha 360° — vista consolidada: solicitud + entidad + DEE + estadísticas.
"""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from modules.config import badge, BADGE_ETAPA, ETAPAS_FLUJO, TOKENS


def render_ficha_360(ctx: dict):
    sol: pd.DataFrame = ctx.get("sol", pd.DataFrame())
    if sol.empty:
        st.info("Carga T_SOLICITUDES.xlsx para ver la Ficha 360°.")
        return

    col_id     = _find_col(sol, ["N° Solicitud", "Nro", "ID"])
    entidad_col = _find_col(sol, ["Entidad", "entidad"])

    st.markdown("### 🔍 Selecciona solicitud para vista 360°")
    opciones = _build_options(sol, col_id, entidad_col)
    selected = st.selectbox("Solicitud", ["— elegir —"] + opciones, key="f360_sel")

    if selected == "— elegir —":
        _render_empty_state()
        return

    nro = selected.split(" · ")[0].strip()
    mask = sol[col_id].astype(str).str.strip() == nro if col_id else pd.Series([False]*len(sol))
    if not mask.any():
        st.error("Solicitud no encontrada.")
        return

    row = sol[mask].iloc[0]
    _render_360(row, sol, ctx, col_id, entidad_col)


def _render_360(row: pd.Series, sol: pd.DataFrame, ctx: dict, col_id, entidad_col):
    etapa = row.get("ETAPA_ACTUAL", "Sin etapa")
    color = BADGE_ETAPA.get(etapa, "gray")
    nro   = row.get(col_id, "—") if col_id else "—"

    st.markdown(f"## 🔁 Vista 360° · Solicitud #{nro}")
    st.markdown(
        f'{badge(etapa, color)} &nbsp; '
        f'{badge(row.get("Proceso GRD", ""), "blue") if "Proceso GRD" in row.index else ""}',
        unsafe_allow_html=True,
    )

    st.divider()

    # ── Bloque superior: datos + radar de avance ──────────────────────────────
    col_left, col_right = st.columns([2, 1])

    with col_left:
        _section("🏛️ Identidad de la entidad", [
            ("Entidad",      _g(row, ["Entidad", "entidad"])),
            ("Departamento", _g(row, ["Departamento"])),
            ("Provincia",    _g(row, ["Provincia"])),
            ("Distrito",     _g(row, ["Distrito"])),
            ("UBIGEO",       row.get("UBIGEO_KEY", "—")),
        ])
        _section("📋 Solicitud", [
            ("N° Solicitud", str(nro)),
            ("Proceso",      _g(row, ["Proceso GRD", "Proceso"])),
            ("Monto",        _fmt(_g(row, ["Monto Solicitado", "Monto"]))),
            ("Etapa actual", etapa),
        ])

    with col_right:
        _render_gauge(row)

    st.divider()

    # ── Timeline completa ─────────────────────────────────────────────────────
    _render_timeline_360(row)

    # ── DEE vinculada ─────────────────────────────────────────────────────────
    dee = ctx.get("dee")
    if dee is not None and "UBIGEO_KEY" in dee.columns:
        ubigeo = row.get("UBIGEO_KEY", "")
        dee_linked = dee[dee["UBIGEO_KEY"] == ubigeo]
        if not dee_linked.empty:
            st.markdown("#### 🚨 Declaratorias de Emergencia vinculadas")
            st.dataframe(dee_linked, use_container_width=True, hide_index=True)
        else:
            st.caption("Sin DEE vinculada a este ubigeo.")

    # ── Otras solicitudes de la entidad ───────────────────────────────────────
    if entidad_col and entidad_col in row.index:
        entidad = row[entidad_col]
        otras = sol[sol[entidad_col] == entidad]
        st.markdown(f"#### 🏛️ Historial de solicitudes de esta entidad ({len(otras)})")
        cols_show = [c for c in [col_id, "ETAPA_ACTUAL", "Proceso GRD", "Monto Solicitado"]
                     if c and c in sol.columns]
        st.dataframe(otras[cols_show], use_container_width=True, hide_index=True)


def _render_gauge(row: pd.Series):
    etapa = row.get("ETAPA_ACTUAL", "Sin etapa")
    if etapa in ETAPAS_FLUJO:
        # cuántos pasos completados (de 8)
        idx_actual = ETAPAS_FLUJO.index(etapa)
        pasos = len(ETAPAS_FLUJO) - idx_actual
    else:
        pasos = 0
    pct = round(pasos / len(ETAPAS_FLUJO) * 100)

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=pct,
        number={"suffix": "%", "font": {"color": TOKENS["text_primary"]}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": TOKENS["text_muted"]},
            "bar":  {"color": TOKENS["accent"]},
            "bgcolor": TOKENS["bg_card2"],
            "steps": [
                {"range": [0,  33], "color": "#450a0a"},
                {"range": [33, 66], "color": "#431407"},
                {"range": [66, 100],"color": "#14532d"},
            ],
        },
        title={"text": "Avance", "font": {"color": TOKENS["text_muted"]}},
    ))
    fig.update_layout(
        height=220,
        paper_bgcolor="rgba(0,0,0,0)",
        font_color=TOKENS["text_muted"],
        margin=dict(l=20, r=20, t=40, b=10),
    )
    st.plotly_chart(fig, use_container_width=True)


def _render_timeline_360(row: pd.Series):
    st.markdown("#### 📅 Línea de tiempo completa")
    etapa_actual = row.get("ETAPA_ACTUAL", "Sin etapa")
    cols = st.columns(len(ETAPAS_FLUJO))
    for i, (e, col) in enumerate(zip(reversed(ETAPAS_FLUJO), cols)):
        fecha = row.get(e)
        done  = pd.notna(fecha) and str(fecha).strip() not in ("", "NaT")
        is_current = e == etapa_actual
        icono = "✅" if done else ("🔵" if is_current else "⬜")
        col.markdown(
            f"<div style='text-align:center;font-size:.7rem;color:#9BA8BF'>"
            f"{icono}<br><strong style='color:{'#3B82F6' if is_current else '#D1D9EC'};font-size:.68rem'>"
            f"{e.replace('Fecha ','')}</strong><br>"
            f"<span style='font-size:.65rem'>{str(fecha)[:10] if done else '—'}</span>"
            f"</div>",
            unsafe_allow_html=True,
        )


# ── Helpers ───────────────────────────────────────────────────────────────────

def _section(title: str, fields: list):
    st.markdown(f"**{title}**")
    for label, value in fields:
        if value and value != "—":
            st.markdown(
                f'<p style="margin:.15rem 0;font-size:.85rem;">'
                f'<span style="color:#9BA8BF">{label}:</span> '
                f'<strong style="color:#F0F4FF">{value}</strong></p>',
                unsafe_allow_html=True,
            )
    st.markdown("")


def _render_empty_state():
    st.markdown("""
<div style="text-align:center;padding:4rem;color:#4B5563;">
  🔁 Selecciona una solicitud para ver su vista 360°.
</div>""", unsafe_allow_html=True)


def _find_col(df: pd.DataFrame, candidates: list):
    for c in candidates:
        if c in df.columns:
            return c
        for col in df.columns:
            if c.lower() in col.lower():
                return col
    return None


def _g(row: pd.Series, candidates: list) -> str:
    for c in candidates:
        if c in row.index:
            v = row[c]
            return str(v) if pd.notna(v) else "—"
        for k in row.index:
            if c.lower() in k.lower():
                v = row[k]
                return str(v) if pd.notna(v) else "—"
    return "—"


def _fmt(v: str) -> str:
    try:
        return f"S/ {float(v):,.0f}"
    except Exception:
        return v


def _build_options(sol: pd.DataFrame, col_id, entidad_col) -> list:
    if col_id is None:
        return []
    rows = sol.head(200)
    opts = []
    for _, r in rows.iterrows():
        nro = r.get(col_id, "")
        ent = str(r.get(entidad_col, ""))[:40] if entidad_col else ""
        opts.append(f"{nro} · {ent}")
    return opts
