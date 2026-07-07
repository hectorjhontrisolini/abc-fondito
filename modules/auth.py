"""
Autenticación por contraseña con st.secrets.

Para Streamlit Cloud, en el panel Settings → Secrets agrega:
    [auth]
    password = "tu_contraseña"
    admin_password = "tu_contraseña_admin"

Para desarrollo local crea .streamlit/secrets.toml con el mismo contenido.
"""
import time
import streamlit as st


# ── Contraseñas de respaldo sólo para desarrollo sin secrets ──────────────────
_FALLBACK_PASSWORDS = ["fondes2026", "admin2026"]


def _valid_password(pwd: str) -> bool:
    try:
        auth = st.secrets.get("auth", {})
        valid = [auth.get("password", ""), auth.get("admin_password", "")]
        return pwd in valid
    except Exception:
        return pwd in _FALLBACK_PASSWORDS


def check_auth() -> bool:
    """
    Muestra el login si el usuario no está autenticado.
    Retorna True cuando la sesión está autenticada.
    """
    if st.session_state.get("authenticated"):
        return True

    _render_login()
    return False


def _render_login():
    st.markdown("""
<div class="access-denied">
  <div style="font-size:3rem;line-height:1;">🏔️</div>
  <h2>ST · FONDES</h2>
  <p>Sistema de Seguimiento de Solicitudes<br>
     <strong style="color:#3B82F6;">INDECI · Perú</strong></p>
</div>
""", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        pwd = st.text_input("Contraseña de acceso", type="password", key="_login_pwd")

        if st.button("🔐 Ingresar al sistema", use_container_width=True, type="primary"):
            if _valid_password(pwd):
                st.session_state["authenticated"] = True
                st.session_state["login_ts"] = time.time()
                st.rerun()
            else:
                _show_access_denied()

        st.markdown(
            "<p style='text-align:center;color:#4B5563;font-size:.75rem;margin-top:1rem;'>"
            "Acceso exclusivo · Equipo ST-FONDES</p>",
            unsafe_allow_html=True,
        )


def _show_access_denied():
    st.markdown("""
<div style="background:#450a0a;border:1px solid #7f1d1d;border-radius:8px;padding:.9rem 1rem;margin-top:.5rem;">
  <p style="color:#fca5a5;margin:0;font-size:.85rem;">
    🔒 <strong>Acceso restringido.</strong> Contraseña incorrecta.<br>
    <span style="color:#f87171;">Este panel es de uso exclusivo para el equipo ST-FONDES / INDECI.<br>
    Si necesitas acceso, contacta al administrador.</span>
  </p>
</div>
""", unsafe_allow_html=True)


def logout():
    for key in ["authenticated", "login_ts", "ctx", "data_loaded", "demo_mode", "selected_sol"]:
        st.session_state.pop(key, None)
    st.rerun()


def render_logout_button():
    if st.button("🚪 Cerrar sesión", use_container_width=True):
        logout()
