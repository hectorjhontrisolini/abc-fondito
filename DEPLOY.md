# Guía de publicación en Streamlit Cloud

## 1. Prerrequisitos
- Cuenta en [github.com](https://github.com) (gratis)
- Cuenta en [share.streamlit.io](https://share.streamlit.io) (gratis, usa tu GitHub)

---

## 2. Crear repositorio en GitHub

Desde la carpeta `fondito/` ejecuta estos comandos en PowerShell o Git Bash:

```bash
# Inicializar git
git init

# Agregar todos los archivos (el .gitignore excluye secrets.toml y Excel)
git add .
git commit -m "feat: primera versión FONDES Cloud"

# Crear repo en GitHub (requiere GitHub CLI - gh)
gh repo create fondito --public --source=. --push

# -- ALTERNATIVA sin GitHub CLI --
# 1. Ir a github.com → New repository → nombre: fondito → Create
# 2. Copiar la URL que te da GitHub y ejecutar:
git remote add origin https://github.com/TU_USUARIO/fondito.git
git branch -M main
git push -u origin main
```

---

## 3. Configurar Secrets en Streamlit Cloud

1. Ve a [share.streamlit.io](https://share.streamlit.io) → **New app**
2. Selecciona tu repositorio `fondito`, rama `main`, archivo `app.py`
3. Antes de desplegar, haz clic en **Advanced settings → Secrets**
4. Pega este contenido (cambia las contraseñas):

```toml
[auth]
password       = "tu_contraseña_segura"
admin_password = "tu_contraseña_admin"
```

5. Haz clic en **Deploy** — en ~2 minutos la app estará en línea.

---

## 4. URL de tu app

Streamlit Cloud te asigna una URL del estilo:
```
https://fondito.streamlit.app
```
o
```
https://tu-usuario-fondito-app-xxxxxxx.streamlit.app
```

Copia esa URL y pégala en `portfolio_snippet.html` donde dice `TU_APP_URL`.

---

## 5. Actualizar la app después de cambios

```bash
# Desde la carpeta fondito/
git add .
git commit -m "fix: descripción del cambio"
git push
```
Streamlit Cloud detecta el push y redespliega automáticamente en ~1 min.

---

## 6. Cambiar la contraseña

**Opción A — Sin tocar el código** (recomendada):
1. Streamlit Cloud → tu app → **⋮ → Settings → Secrets**
2. Cambia el valor de `password` o `admin_password`
3. Guarda — la app se reinicia con la nueva contraseña.

**Opción B — Desde `modules/auth.py`** (solo para dev local sin secrets):
```python
_FALLBACK_PASSWORDS = ["nueva_contraseña", "nueva_admin"]
```

---

## 7. Comandos Git útiles

```bash
# Ver estado actual
git status

# Ver historial
git log --oneline -10

# Crear rama de desarrollo
git checkout -b develop

# Volver a main
git checkout main

# Subir rama develop
git push -u origin develop
```

---

## 8. Estructura del repositorio

```
fondito/
├── app.py                  ← entrada principal (Streamlit apunta aquí)
├── requirements.txt        ← dependencias (Streamlit Cloud instala automáticamente)
├── .gitignore              ← excluye secrets y datos sensibles
├── .streamlit/
│   ├── config.toml         ← tema dark (se sube a GitHub - no contiene secrets)
│   └── secrets.toml        ← SOLO LOCAL - nunca subir
├── modules/
│   ├── __init__.py
│   ├── config.py           ← tokens de diseño, CSS, constantes
│   ├── auth.py             ← autenticación y login
│   ├── data_loader.py      ← carga de Excel + datos demo
│   ├── dashboard.py        ← tab 1: métricas y gráficos
│   ├── ficha_tecnica.py    ← tab 2: detalle por solicitud
│   ├── ficha_360.py        ← tab 3: vista 360° consolidada
│   ├── estadisticas.py     ← tab 4: análisis estadístico
│   └── dee.py              ← tab 5: consulta DEE
├── data/
│   └── .gitkeep            ← carpeta reservada (los xlsx no se suben)
└── portfolio_snippet.html  ← código HTML para www.hectorjhon.com
```
