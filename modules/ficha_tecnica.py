"""
Tab 2 · Ficha Técnica — detalle de una solicitud seleccionada.
"""
import pandas as pd
import streamlit as st
from modules.config import badge, card, ETAPAS_FLUJO, BADGE_ETAPA, TOKENS


def render_ficha_tecnica(ctx: dict):
    sol: pd.DataFrame = ctx.get("sol", pd.DataFrame())
    if sol.empty:
        st.info("Carga T_SOLICITUDES.xlsx para ver fichas.")
        return

    # ── Selector de solicitud ─────────────────────────────────────────────────
    col_id = _find_col(sol, ["N° Solicitud", "Nro", "ID", "id"])

    st.markdown("### 🔍 Seleccionar solicitud")
    col1, col2 = st.columns([2, 3])
    with col1:
        id_input = st.text_input("Ingresa N° de solicitud", key="ft_id_input")
    with col2:
        entidad_col = _find_col(sol, ["Entidad", "entidad", "ENTIDAD"])
        opciones = _build_options(sol, col_id, entidad_col)
        selected_label = st.selectbox("O selecciona de la lista", ["— elegir —"] + opciones, key="ft_select")

    # Resolver cuál solicitud mostrar
    sol_row = None
    if id_input.strip():
        mask = sol[col_id].astype(str).str.strip() == id_input.strip() if col_id else pd.Series([False]*len(sol))
        if mask.any():
            sol_row = sol[mask].iloc[0]
        else:
            st.warning(f"No se encontró solicitud '{id_input}'")
    elif selected_label and selected_label != "— elegir —":
        nro = selected_label.split(" · ")[0].strip()
        mask = sol[col_id].astype(str).str.strip() == nro if col_id else pd.Series([False]*len(sol))
        if mask.any():
            sol_row = sol[mask].iloc[0]

    if sol_row is None:
        st.markdown("""
<div style="text-align:center;padding:3rem;color:#4B5563;">
  📋 Selecciona una solicitud para ver su ficha técnica.
</div>""", unsafe_allow_html=True)
        return

    _render_detalle(sol_row, sol, ctx)


def _render_detalle(row: pd.Series, sol: pd.DataFrame, ctx: dict):
    etapa = row.get("ETAPA_ACTUAL", "Sin etapa")
    color = BADGE_ETAPA.get(etapa, "gray")
    nro   = row.get("N° Solicitud", "—")

    st.divider()
    st.markdown(
        f"## Solicitud #{nro} &nbsp; {badge(etapa, color)}",
        unsafe_allow_html=True,
    )

    # ── Datos generales ──────────────────────────────────────────────────────
    col_a, col_b = st.columns(2)
    with col_a:
        _card_datos_generales(row)
    with col_b:
        _card_timeline(row)

    # ── DEE vinculada ────────────────────────────────────────────────────────
    dee = ctx.get("dee")
    if dee is not None and "UBIGEO_KEY" in dee.columns and "UBIGEO_KEY" in row.index:
        dee_dist = dee[dee["UBIGEO_KEY"] == row.get("UBIGEO_KEY", "")]
        if not dee_dist.empty:
            st.markdown("#### 🚨 DEE vinculada al distrito")
            st.dataframe(dee_dist, use_container_width=True, hide_index=True)

    # ── Otras solicitudes de la entidad ─────────────────────────────────────
    entidad_col = _find_col(sol, ["Entidad", "entidad"])
    if entidad_col and entidad_col in row.index:
        otras = sol[sol[entidad_col] == row[entidad_col]]
        if len(otras) > 1:
            st.markdown(f"#### 🏛️ Todas las solicitudes de esta entidad ({len(otras)})")
            col_id = _find_col(sol, ["N° Solicitud"])
            cols_show = [c for c in [col_id, "ETAPA_ACTUAL", "Proceso GRD"] if c and c in sol.columns]
            st.dataframe(otras[cols_show], use_container_width=True, hide_index=True)


def _card_datos_generales(row: pd.Series):
    campos = [
        ("Entidad",      _get(row, ["Entidad", "entidad"])),
        ("Departamento", _get(row, ["Departamento"])),
        ("Provincia",    _get(row, ["Provincia"])),
        ("Distrito",     _get(row, ["Distrito"])),
        ("UBIGEO",       row.get("UBIGEO_KEY", "—")),
        ("Proceso",      _get(row, ["Proceso GRD", "Proceso"])),
        ("Monto",        _fmt_monto(_get(row, ["Monto Solicitado", "Monto"]))),
    ]
    body = "".join(
        f'<p><span style="color:#9BA8BF">{k}:</span> <strong style="color:#F0F4FF">{v}</strong></p>'
        for k, v in campos if v and v != "—"
    )
    st.markdown(card("📌 Datos generales", body), unsafe_allow_html=True)


def _card_timeline(row: pd.Series):
    etapa_actual = row.get("ETAPA_ACTUAL", "Sin etapa")
    items = []
    for e in reversed(ETAPAS_FLUJO):
        fecha = row.get(e)
        done = pd.notna(fecha) and str(fecha).strip() not in ("", "NaT")
        fecha_str = str(fecha)[:10] if done else "Pendiente"
        is_current = e == etapa_actual
        cls = "done" if done else ""
        curr_indicator = " ◀ actual" if is_current else ""
        items.append(
            f'<div class="tl-item {cls}">'
            f'  <strong style="color:{TOKENS["accent"] if is_current else "#D1D9EC"}">'
            f'    {e.replace("Fecha ","")}{curr_indicator}</strong>'
            f'  <div class="tl-date">{fecha_str}</div>'
            f'</div>'
        )
    body = f'<div class="tl-wrap">{"".join(items)}</div>'
    st.markdown(card("📅 Línea de tiempo", body), unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _find_col(df: pd.DataFrame, candidates: list):
    for c in candidates:
        if c in df.columns:
            return c
        for col in df.columns:
            if c.lower() in col.lower():
                return col
    return None


def _get(row: pd.Series, candidates: list) -> str:
    for c in candidates:
        if c in row.index:
            v = row[c]
            return str(v) if pd.notna(v) else "—"
        for k in row.index:
            if c.lower() in k.lower():
                v = row[k]
                return str(v) if pd.notna(v) else "—"
    return "—"


def _fmt_monto(v: str) -> str:
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
