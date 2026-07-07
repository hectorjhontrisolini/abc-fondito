"""
Design tokens, CSS global y constantes de dominio.
"""

PAGE_CONFIG = dict(
    page_title="ST-FONDES · INDECI",
    page_icon="🏔️",
    layout="wide",
    initial_sidebar_state="expanded",
)

TOKENS = {
    "primary":      "#1B5C9E",
    "secondary":    "#E8731A",
    "success":      "#16A34A",
    "warning":      "#D97706",
    "danger":       "#DC2626",
    "bg_dark":      "#0E1117",
    "bg_card":      "#1E2535",
    "bg_card2":     "#252D3D",
    "text_primary": "#F0F4FF",
    "text_muted":   "#9BA8BF",
    "border":       "#2D3748",
    "accent":       "#3B82F6",
}

PROCESOS_FONDES = ["FONDES"]
PROCESOS_REHAB  = ["REHABILITACION", "REHABILITACIÓN"]

# Etapas de flujo, de más avanzada a menos avanzada
ETAPAS_FLUJO = [
    "Fecha Liquidación",
    "Fecha Cierre",
    "Fecha Ejecución",
    "Fecha Elegibilidad",
    "Fecha Aprobación",
    "Fecha Evaluación",
    "Fecha Admisión",
    "Fecha Ingreso",
]

BADGE_ETAPA = {
    "Fecha Liquidación": "green",
    "Fecha Cierre":      "green",
    "Fecha Ejecución":   "blue",
    "Fecha Elegibilidad":"blue",
    "Fecha Aprobación":  "blue",
    "Fecha Evaluación":  "orange",
    "Fecha Admisión":    "orange",
    "Fecha Ingreso":     "gray",
    "Sin etapa":         "gray",
}

CSS_GLOBAL = """
<style>
/* ── base ── */
.stApp { background-color: #0E1117; }
.block-container { padding: 1.5rem 2rem 2rem; }
h1,h2,h3 { color: #F0F4FF !important; }

/* ── sidebar ── */
[data-testid="stSidebar"] {
    background: #141927;
    border-right: 1px solid #2D3748;
}

/* ── metric card ── */
.fnds-metric {
    background: #1E2535;
    border: 1px solid #2D3748;
    border-left: 4px solid #1B5C9E;
    border-radius: 10px;
    padding: 1rem 1.2rem;
    text-align: center;
    margin-bottom: .5rem;
}
.fnds-metric .val  { font-size:1.9rem; font-weight:700; color:#3B82F6; line-height:1.1; }
.fnds-metric .lbl  { font-size:.72rem; color:#9BA8BF; text-transform:uppercase; letter-spacing:.06em; margin-top:.3rem; }
.fnds-metric.green { border-left-color:#16A34A; }
.fnds-metric.green .val { color:#4ade80; }
.fnds-metric.orange{ border-left-color:#D97706; }
.fnds-metric.orange .val{ color:#fb923c; }
.fnds-metric.red   { border-left-color:#DC2626; }
.fnds-metric.red .val{ color:#f87171; }

/* ── card genérico ── */
.fnds-card {
    background: #1E2535;
    border: 1px solid #2D3748;
    border-radius: 10px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 1rem;
}
.fnds-card h4 { color:#9BA8BF; font-size:.78rem; text-transform:uppercase; letter-spacing:.05em; margin:0 0 .5rem; }
.fnds-card p  { color:#D1D9EC; margin:.15rem 0; font-size:.88rem; }

/* ── badges ── */
.badge {
    display:inline-block;
    padding:.18em .65em;
    border-radius:10px;
    font-size:.73rem;
    font-weight:600;
    line-height:1.4;
}
.badge-blue   { background:#1e3a5f; color:#60a5fa; }
.badge-green  { background:#14532d; color:#4ade80; }
.badge-orange { background:#431407; color:#fb923c; }
.badge-gray   { background:#1f2937; color:#9ca3af; }
.badge-red    { background:#450a0a; color:#fca5a5; }

/* ── timeline ── */
.tl-wrap { padding-left:.5rem; }
.tl-item {
    border-left:2px solid #2D3748;
    padding:.45rem 0 .45rem .9rem;
    position:relative;
    font-size:.83rem;
    color:#9BA8BF;
}
.tl-item.done { border-left-color:#3B82F6; color:#D1D9EC; }
.tl-item.done::before {
    content:'';
    position:absolute; left:-5px; top:.8rem;
    width:8px; height:8px;
    border-radius:50%; background:#3B82F6;
}
.tl-item .tl-date { font-size:.72rem; color:#6B7280; margin-top:.1rem; }

/* ── tabla ── */
.fnds-table { width:100%; border-collapse:collapse; font-size:.83rem; }
.fnds-table th {
    background:#252D3D; color:#9BA8BF;
    font-size:.7rem; text-transform:uppercase; letter-spacing:.04em;
    padding:.55rem .8rem; text-align:left; white-space:nowrap;
}
.fnds-table td { color:#D1D9EC; padding:.55rem .8rem; border-bottom:1px solid #1E2535; vertical-align:top; }
.fnds-table tr:hover td { background:#252D3D; }

/* ── acceso restringido ── */
.access-denied {
    max-width:420px; margin:4rem auto;
    background:#1E2535; border:1px solid #2D3748; border-radius:16px;
    padding:2.5rem 2rem; text-align:center;
}
.access-denied h2 { color:#F0F4FF; margin-bottom:.4rem; }
.access-denied p  { color:#9BA8BF; font-size:.9rem; }
</style>
"""


def metric_card(value, label, color="blue", suffix=""):
    return f"""
<div class="fnds-metric {color}">
  <div class="val">{value}{suffix}</div>
  <div class="lbl">{label}</div>
</div>"""


def badge(text, color="gray"):
    return f'<span class="badge badge-{color}">{text}</span>'


def card(title, body_html):
    return f'<div class="fnds-card"><h4>{title}</h4>{body_html}</div>'
