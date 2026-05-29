# 🎓 Analizador de Software Académico

Web app que analiza páginas de proveedores de software y genera un reporte estructurado con licencias académicas, descripciones y carreras universitarias compatibles.

**Powered by:** Gemini 2.0 Flash + Google Search Grounding + Streamlit

---

## 🚀 Deploy en Streamlit Cloud (paso a paso)

### 1. Sube el repositorio a GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/TU_USUARIO/TU_REPO.git
git push -u origin main
```

### 2. Crea la app en Streamlit Cloud
1. Ve a [share.streamlit.io](https://share.streamlit.io) e inicia sesión con GitHub
2. Haz clic en **New app**
3. Selecciona tu repositorio y rama (`main`)
4. El archivo principal es `app.py`
5. Haz clic en **Deploy**

### 3. Configura el API Key (secreto)
En el dashboard de Streamlit Cloud, antes o después del deploy:
1. Ve a **Settings → Secrets**
2. Agrega esto:
```toml
GEMINI_API_KEY = "AIza..."
```
3. Guarda — la app se reinicia automáticamente.

> **Obtén tu API Key gratuita:** [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)

---

## 💻 Correr localmente

```bash
pip install -r requirements.txt
# Edita .streamlit/secrets.toml con tu API Key real
streamlit run app.py
```

---

## 📁 Estructura del proyecto

```
├── app.py                    # App principal
├── requirements.txt          # Dependencias
├── .gitignore                # Protege secrets
├── .streamlit/
│   └── secrets.toml          # API Key (NO subir a GitHub)
└── README.md
```

---

## ✨ ¿Qué analiza?

Para cualquier URL de proveedor de software, el reporte incluye:

1. **Número de softwares** que ofrece el sitio
2. **Nombres comerciales** de cada herramienta
3. **Licencias académicas** (gratuitas, descuento, prueba extendida)
4. **Links directos** para solicitar la licencia estudiantil
5. **Descripción** de cada software
6. **Carreras universitarias** que se benefician de cada herramienta
