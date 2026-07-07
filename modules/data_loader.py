"""
Carga de datos desde archivos Excel subidos por el usuario.
Si no hay archivos, ofrece datos de demostración.
"""
import io
import datetime
import random
import numpy as np
import pandas as pd
import streamlit as st
from typing import Optional, Dict
from modules.config import ETAPAS_FLUJO


# ── Normalización ──────────────────────────────────────────────────────────────

def _norm_ubigeo(series: pd.Series) -> pd.Series:
    def _n(v):
        if pd.isna(v):
            return ""
        s = str(v).strip()
        if s.endswith(".0"):
            s = s[:-2]
        return s.zfill(6) if s.isdigit() else s
    return series.apply(_n)


def _buscar_col(df: pd.DataFrame, candidates: list) -> Optional[str]:
    cols_lower = {c.lower(): c for c in df.columns}
    for c in candidates:
        if c in df.columns:
            return c
        if c.lower() in cols_lower:
            return cols_lower[c.lower()]
        for col in df.columns:
            if c.lower() in col.lower():
                return col
    return None


def _etapa_actual(row: pd.Series) -> str:
    for e in ETAPAS_FLUJO:
        if e in row.index and pd.notna(row[e]) and str(row[e]).strip() not in ("", "NaT", "nat"):
            return e
    return "Sin etapa"


# ── Carga desde bytes ──────────────────────────────────────────────────────────

@st.cache_data(show_spinner=False)
def _read_excel(file_bytes: bytes, sheet: Optional[str] = None) -> pd.DataFrame:
    try:
        kw = {"sheet_name": sheet} if sheet else {}
        return pd.read_excel(io.BytesIO(file_bytes), **kw)
    except Exception as exc:
        st.warning(f"No se pudo leer el archivo: {exc}")
        return pd.DataFrame()


def _procesar_solicitudes(df: pd.DataFrame) -> pd.DataFrame:
    ubi_col = _buscar_col(df, ["UBIGEO", "ubigeo", "Ubigeo", "UBIGEO_KEY"])
    if ubi_col:
        df["UBIGEO_KEY"] = _norm_ubigeo(df[ubi_col])
    else:
        df["UBIGEO_KEY"] = ""

    # etapas presentes en el df
    etapas_presentes = [e for e in ETAPAS_FLUJO if e in df.columns]
    df["ETAPA_ACTUAL"] = df.apply(_etapa_actual, axis=1)
    df["_n_etapas"] = df["ETAPA_ACTUAL"].apply(
        lambda e: (len(ETAPAS_FLUJO) - ETAPAS_FLUJO.index(e)) if e in ETAPAS_FLUJO else 0
    )
    return df


# ── UI de carga ────────────────────────────────────────────────────────────────

def cargar_datos() -> Dict:
    if st.session_state.get("data_loaded") and "ctx" in st.session_state:
        return st.session_state["ctx"]

    ctx: Dict = {}
    import os
    import pathlib

    # Intentar cargar desde la carpeta data/ primero (para Streamlit Cloud)
    data_dir = pathlib.Path(__file__).parent.parent / "data"

    sol_path = data_dir / "T_SOLICITUDES.xlsx"
    dee_path = data_dir / "T_DEE.xlsx"
    ubi_path = data_dir / "T_UBIGEO.xlsx"

    if sol_path.exists():
        try:
            df = _read_excel(sol_path.read_bytes())
            if not df.empty:
                ctx["sol"] = _procesar_solicitudes(df)
                st.sidebar.success("✅ T_SOLICITUDES.xlsx cargado automáticamente")
        except Exception as e:
            st.sidebar.error(f"Error cargando T_SOLICITUDES.xlsx: {e}")

    if dee_path.exists():
        try:
            df_dee = _read_excel(dee_path.read_bytes())
            if not df_dee.empty:
                ubi_col = _buscar_col(df_dee, ["UBIGEO", "ubigeo"])
                if ubi_col:
                    df_dee["UBIGEO_KEY"] = _norm_ubigeo(df_dee[ubi_col])
                ctx["dee"] = df_dee
                st.sidebar.success("✅ T_DEE.xlsx cargado automáticamente")
        except Exception as e:
            st.sidebar.warning(f"T_DEE.xlsx no disponible: {e}")

    if ubi_path.exists():
        try:
            ctx["ubi"] = _read_excel(ubi_path.read_bytes())
            st.sidebar.success("✅ T_UBIGEO.xlsx cargado automáticamente")
        except Exception as e:
            st.sidebar.warning(f"T_UBIGEO.xlsx no disponible: {e}")

    st.sidebar.divider()

    # Si no hay datos desde carpeta, mostrar uploader
    if "sol" not in ctx:
        st.sidebar.markdown("### 📁 Cargar archivos (opcional)")
        up_sol = st.sidebar.file_uploader(
            "T_SOLICITUDES.xlsx", type=["xlsx"], key="up_sol",
            help="Sube un archivo para sobrescribir el actual",
        )
        if up_sol:
            df = _read_excel(up_sol.getvalue())
            if not df.empty:
                ctx["sol"] = _procesar_solicitudes(df)

        up_dee = st.sidebar.file_uploader(
            "T_DEE.xlsx (opcional)", type=["xlsx"], key="up_dee"
        )
        if up_dee:
            df_dee = _read_excel(up_dee.getvalue())
            if not df_dee.empty:
                ubi_col = _buscar_col(df_dee, ["UBIGEO", "ubigeo"])
                if ubi_col:
                    df_dee["UBIGEO_KEY"] = _norm_ubigeo(df_dee[ubi_col])
                ctx["dee"] = df_dee

        up_ubi = st.sidebar.file_uploader(
            "T_UBIGEO.xlsx (opcional)", type=["xlsx"], key="up_ubi"
        )
        if up_ubi:
            ctx["ubi"] = _read_excel(up_ubi.getvalue())

        st.sidebar.divider()

        # Demo mode
        if st.sidebar.button("▶ Usar datos de demostración", use_container_width=True):
            ctx = _demo_ctx()
            st.session_state["demo_mode"] = True

    if ctx:
        st.session_state["ctx"] = ctx
        st.session_state["data_loaded"] = True

    return ctx


# ── Datos de demostración ──────────────────────────────────────────────────────

def _demo_ctx() -> Dict:
    random.seed(42)
    np.random.seed(42)

    depts   = ["LIMA", "CUSCO", "AREQUIPA", "PIURA", "PUNO", "LORETO", "JUNÍN"]
    provs   = ["LIMA", "CUSCO", "AREQUIPA", "PIURA", "PUNO", "MAYNAS", "HUANCAYO"]
    nombres = [
        "SANTA ROSA", "SAN JUAN", "LOS ANDES", "NUEVA ESPERANZA",
        "INDEPENDENCIA", "EL CARMEN", "SAN PEDRO", "BELLAVISTA",
    ]
    procesos = ["FONDES", "REHABILITACIÓN"]

    n = 80
    rows = []
    base = datetime.date(2024, 1, 1)

    for i in range(n):
        dept_i = i % len(depts)
        etapa_i = random.randint(0, len(ETAPAS_FLUJO) - 1)
        etapa_actual = ETAPAS_FLUJO[etapa_i]
        row = {
            "N° Solicitud": 1000 + i,
            "Entidad": f"MUNICIPALIDAD DISTRITAL DE {random.choice(nombres)} {i+1}",
            "Departamento": depts[dept_i],
            "Provincia": provs[dept_i],
            "Proceso GRD": random.choice(procesos) if random.random() > .35 else "FONDES",
            "UBIGEO_KEY": f"{100000 + i:06d}",
            "ETAPA_ACTUAL": etapa_actual,
            "_n_etapas": len(ETAPAS_FLUJO) - etapa_i,
            "Monto Solicitado": round(random.uniform(500_000, 15_000_000), 2),
        }
        # Agregar fechas acumulativas hasta la etapa actual
        for j in range(etapa_i, len(ETAPAS_FLUJO)):
            e = ETAPAS_FLUJO[j]
            row[e] = base + datetime.timedelta(days=(len(ETAPAS_FLUJO) - j - 1) * 45 + random.randint(0, 20) + i * 3)
        rows.append(row)

    df_sol = pd.DataFrame(rows)

    # DEE sample
    df_dee = pd.DataFrame({
        "El Peruano DS_N°": [f"DS-{i:03d}-2025-PCM" for i in range(1, 31)],
        "Departamento": (depts * 5)[:30],
        "Distrito": [f"Distrito {i}" for i in range(30)],
        "UBIGEO_KEY": [f"{100000+i:06d}" for i in range(30)],
        "Fecha DS": pd.date_range("2024-03-01", periods=30, freq="10D"),
        "Evento": random.choices(["Sismo", "Inundación", "Deslizamiento", "Huaico"], k=30),
    })

    return {"sol": df_sol, "dee": df_dee}
