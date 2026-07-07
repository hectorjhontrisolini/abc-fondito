"""
FONDES ST Panel — Streamlit Cloud
Sistema de Seguimiento de Solicitudes · INDECI · Perú
"""
import pandas as pd
import streamlit as st

from modules.config import CSS_GLOBAL, PAGE_CONFIG
from modules.auth import check_auth, render_logout_button
from modules.data_loader import cargar_datos

st.set_page_config(**PAGE_CONFIG)
# CSS debe emitirse en cada rerun (Streamlit lo limpia)
st.markdown(CSS_GLOBAL, unsafe_allow_html=True)


def main():
    # ── Autenticación ──────────────────────────────────────────────────────────
    if not check_auth():
        return

    # ── Carga de datos ─────────────────────────────────────────────────────────
    ctx = cargar_datos()

    # ── Sidebar ────────────────────────────────────────────────────────────────
    with st.sidebar:
        _render_sidebar(ctx)

    # ── Tabs principales ───────────────────────────────────────────────────────
    sol: pd.DataFrame = ctx.get("sol", pd.DataFrame())
    if sol.empty:
        st.markdown("""
<div style="text-align:center;padding:5rem 1rem;color:#6B7280;">
  <div style="font-size:3rem;">📁</div>
  <h3 style="color:#9BA8BF;">Sin datos cargados</h3>
  <p>Carga <strong>T_SOLICITUDES.xlsx</strong> en la barra lateral<br>
     o usa los datos de demostración para explorar la app.</p>
</div>""", unsafe_allow_html=True)
        return

    _render_tabs(ctx)


def _render_sidebar(ctx: dict):
    from modules.data_loader import cargar_datos  # noqa — triggers uploader UI

    sol: pd.DataFrame = ctx.get("sol", pd.DataFrame())

    st.markdown(
        "<h2 style='margin:0;color:#3B82F6;'>🏔️ ST·FONDES</h2>"
        "<p style='color:#9BA8BF;font-size:.78rem;margin:0 0 1rem;'>INDECI · Sistema de Seguimiento</p>",
        unsafe_allow_html=True,
    )

    if not sol.empty:
        total = len(sol)
        etapa_avanzada = sol[sol["_n_etapas"] >= 5].shape[0] if "_n_etapas" in sol.columns else 0
        st.markdown(
            f"<div style='background:#1E2535;border-radius:8px;padding:.7rem 1rem;margin-bottom:.5rem;'>"
            f"<span style='color:#9BA8BF;font-size:.72rem;'>SOLICITUDES</span><br>"
            f"<strong style='font-size:1.6rem;color:#3B82F6;'>{total}</strong>"
            f"<span style='color:#4ade80;font-size:.8rem;margin-left:.5rem;'>▲ {etapa_avanzada} avanzadas</span>"
            f"</div>",
            unsafe_allow_html=True,
        )
        if ctx.get("demo_mode"):
            st.info("🔵 Modo demo — datos de ejemplo")

        st.divider()

        # Búsqueda rápida
        st.markdown("**🔍 Búsqueda rápida**")
        query = st.text_input("N° o nombre de entidad", key="sb_search", label_visibility="collapsed")
        if query:
            id_col  = _fc(sol, ["N° Solicitud"])
            ent_col = _fc(sol, ["Entidad"])
            mask = pd.Series([False] * len(sol))
            if id_col:
                mask |= sol[id_col].astype(str).str.contains(query, case=False, na=False)
            if ent_col:
                mask |= sol[ent_col].astype(str).str.contains(query, case=False, na=False)
            resultados = sol[mask].head(6)
            if not resultados.empty:
                for _, r in resultados.iterrows():
                    nro = r.get(id_col, "?") if id_col else "?"
                    ent = str(r.get(ent_col, ""))[:28] if ent_col else ""
                    st.caption(f"#{nro} · {ent}")
            else:
                st.caption("Sin resultados.")

    st.divider()
    render_logout_button()
    st.caption("v2.0 · FONDES Cloud · 2026")


def _render_tabs(ctx: dict):
    from modules.dashboard      import render_dashboard
    from modules.ficha_tecnica  import render_ficha_tecnica
    from modules.ficha_360      import render_ficha_360
    from modules.estadisticas   import render_estadisticas
    from modules.dee            import render_dee

    tabs = st.tabs([
        "📊 Dashboard",
        "📋 Ficha Técnica",
        "🔁 Ficha 360°",
        "📈 Estadísticas",
        "🚨 Consulta DEE",
    ])

    with tabs[0]: render_dashboard(ctx)
    with tabs[1]: render_ficha_tecnica(ctx)
    with tabs[2]: render_ficha_360(ctx)
    with tabs[3]: render_estadisticas(ctx)
    with tabs[4]: render_dee(ctx)


def _fc(df: pd.DataFrame, candidates: list):
    for c in candidates:
        if c in df.columns:
            return c
        for col in df.columns:
            if c.lower() in col.lower():
                return col
    return None


if __name__ == "__main__":
    main()
