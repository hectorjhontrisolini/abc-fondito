# 🏔️ ST · FONDES Panel

**Sistema de Seguimiento de Solicitudes — INDECI · Perú**

Panel de gestión para el equipo ST-FONDES: seguimiento de solicitudes de financiamiento FONDES y REHABILITACIÓN de municipios peruanos, vinculadas a Declaratorias de Estado de Emergencia.

---

## Funcionalidades

| Tab | Descripción |
|-----|-------------|
| 📊 Dashboard | Métricas clave, distribución por etapa, proceso y departamento |
| 📋 Ficha Técnica | Detalle completo de una solicitud con línea de tiempo |
| 🔁 Ficha 360° | Vista consolidada: solicitud + DEE + historial de entidad + gauge de avance |
| 📈 Estadísticas | Filtros dinámicos, gráficos de evolución, heatmap proceso × etapa |
| 🚨 Consulta DEE | Listado de declaratorias, filtros, solicitudes vinculadas |

## Stack

- **Python** + **Streamlit** — interfaz web sin HTML/CSS pesado
- **Pandas** — procesamiento de datos Excel
- **Plotly** — gráficos interactivos dark-mode
- **openpyxl** — lectura de archivos `.xlsx`

## Cómo usar

1. Ingresa la contraseña de acceso
2. Carga `T_SOLICITUDES.xlsx` en la barra lateral (o usa modo demo)
3. Opcionalmente carga `T_DEE.xlsx` y `T_UBIGEO.xlsx`
4. Navega por las pestañas

## Despliegue local

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Despliegue en Streamlit Cloud

Ver [`DEPLOY.md`](DEPLOY.md) para instrucciones paso a paso.

---

*Desarrollado para uso interno del equipo ST-FONDES · INDECI · 2026*
