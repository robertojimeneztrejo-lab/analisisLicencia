import streamlit as st
from google import genai
from google.genai import types
import random

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Analizador de Software Académico",
    layout="centered",
)

# ── Styles ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { max-width: 760px; }
    .stTextInput > div > div > input { font-size: 15px; }
    .url-badge {
        display: inline-block;
        background: #e8f0fe;
        color: #1a56db;
        border-radius: 8px;
        padding: 4px 12px;
        font-size: 13px;
        margin-bottom: 1rem;
        word-break: break-all;
    }
    h1 { font-size: 1.7rem !important; }
</style>
""", unsafe_allow_html=True)

# ── Prompts ───────────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """Eres un analista experto en software académico.
Cuando el usuario te proporciona una URL, visitas esa página web y analizas su contenido en profundidad.
Siempre respondes en español con formato Markdown claro y visual."""

ANALYSIS_PROMPT = """Analiza la siguiente página web: {url}

Visita el enlace anterior, analiza su contenido y genera un reporte estructurado que identifique exactamente los siguientes 6 puntos:

1. **Número de softwares que ofrece:** (Cantidad total de herramientas o programas independientes que se promocionan en el sitio).
2. **Nombre de los softwares:** (Lista con los nombres comerciales de cada uno).
3. **Licencia gratuita para estudiantes/académica/universitaria:** (Indicar claramente si ofrecen este beneficio, si es 100% gratuito, de prueba extendida o con descuento. Si no se menciona, indicar "No especificado").
4. **Link para solicitar la licencia:** (Extrae el enlace directo o la sección de la página donde los estudiantes/profesores pueden postular o registrarse para obtener el beneficio).
5. **¿De qué trata cada software?:** (Una descripción breve, clara y concisa de la función principal de cada programa listado).
6. **Licenciaturas académicas que pueden usarla:** (Lista de carreras universitarias o áreas del conocimiento que le sacarían el mayor provecho a estas herramientas, basándote en sus funciones).

Presenta la información de forma muy visual, usando negritas y listas con viñetas para que sea fácil de escanear."""

# ── Random icon ───────────────────────────────────────────────────────────────
ICONS = ["🎓", "🔬", "📐", "🖥️", "📊", "🧪", "🏫", "📡", "🧬", "⚗️", "🛰️", "🔭", "📱", "🧮", "💡"]

if "page_icon" not in st.session_state:
    st.session_state.page_icon = "🎓"
if "pending_url" not in st.session_state:
    st.session_state.pending_url = None

# ── Header ────────────────────────────────────────────────────────────────────
st.title(f"{st.session_state.page_icon} Analizador de Software Académico")
st.markdown(
    "Pega el link de cualquier proveedor de software y obtén un reporte estructurado "
    "con licencias académicas, descripciones y carreras compatibles."
)
st.divider()

# ── API Key — solo desde secrets ──────────────────────────────────────────────
api_key = st.secrets.get("GEMINI_API_KEY", None)
if not api_key:
    st.error(
        "⚠️ Falta configurar el secret **GEMINI_API_KEY** en Streamlit Cloud.\n\n"
        "Ve a **Manage app → Settings → Secrets** y agrega:\n\n"
        "```toml\nGEMINI_API_KEY = \"AIza...\"\n```"
    )
    st.stop()

# ── Input ─────────────────────────────────────────────────────────────────────
url_input = st.text_input(
    "URL a analizar",
    placeholder="https://www.mathworks.com  |  https://www.autodesk.com  |  https://www.esri.com",
    label_visibility="collapsed",
)

col1, col2 = st.columns([3, 1])
with col2:
    analyze_btn = st.button("🔍 Analizar", use_container_width=True, type="primary")

# ── Al pulsar Analizar: validar, rotar ícono y guardar URL pendiente ──────────
if analyze_btn:
    url = url_input.strip()
    if not url:
        st.warning("⚠️ Por favor ingresa una URL válida.")
        st.stop()
    if not url.startswith(("http://", "https://")):
        st.error("❌ La URL debe comenzar con https:// o http://")
        st.stop()

    current = st.session_state.page_icon
    st.session_state.page_icon = random.choice([i for i in ICONS if i != current])
    st.session_state.pending_url = url
    st.rerun()

# ── Ejecutar análisis si hay URL pendiente ────────────────────────────────────
if st.session_state.pending_url:
    url = st.session_state.pending_url
    st.session_state.pending_url = None

    try:
        client = genai.Client(api_key=api_key)

        grounding_tool = types.Tool(
            google_search=types.GoogleSearch()
        )

        config = types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            tools=[grounding_tool],
            temperature=0.3,
            max_output_tokens=2048,
        )

        with st.spinner("🌐 Visitando la página y analizando contenido..."):
            response = client.models.generate_content(
                model="gemini-2.0-flash-001",
                contents=ANALYSIS_PROMPT.format(url=url),
                config=config,
            )

        result_text = response.text

        st.success("✅ Análisis completado")
        st.markdown(f'<div class="url-badge">🔗 {url}</div>', unsafe_allow_html=True)
        st.markdown(result_text)
        st.divider()

        st.download_button(
            label="⬇️ Descargar reporte (.md)",
            data=result_text,
            file_name="reporte_software_academico.md",
            mime="text/markdown",
        )

    except Exception as e:
        err = str(e)
        if "API_KEY_INVALID" in err or "API key not valid" in err:
            st.error("❌ API Key inválida. Verifica tu clave en [Google AI Studio](https://aistudio.google.com/app/apikey).")
        elif "quota" in err.lower():
            st.error("❌ Cuota de API excedida. Intenta más tarde o revisa tu plan en Google AI Studio.")
        else:
            st.error(f"❌ Error al analizar: {err}")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<small style='color: #999;'>Powered by Gemini 2.5 Flash + Google Search · "
    "Desplegado en Streamlit Cloud</small>",
    unsafe_allow_html=True,
)
