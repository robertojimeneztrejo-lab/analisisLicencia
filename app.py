import streamlit as st
from google import genai
from google.genai import types
import random

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Analizador de Software y Membresías Académicas",
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
    h1 { font-size: 1.7rem !important; text-align: center; }
    p { text-align: center; }
</style>
""", unsafe_allow_html=True)

# ── Prompts ───────────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """Eres un analista experto en software académico y membresías institucionales.
Cuando el usuario te proporciona una URL, visitas esa página web y analizas su contenido en profundidad.
Siempre respondes en español con formato Markdown claro y visual, usando negritas y listas con viñetas."""

# Modo 1: Software (proveedor de herramientas)
PROMPT_SOFTWARE = """Analiza la siguiente página web: {url}

Visita el enlace anterior, analiza su contenido y genera un reporte estructurado en formato de FICHA TÉCNICA que identifique exactamente los siguientes 6 puntos:

1. **Número de softwares que ofrece:** (Cantidad total de herramientas o programas independientes que se promocionan en el sitio).
2. **Nombre de los softwares:** (Lista con los nombres comerciales de cada uno).
3. **Licencia gratuita para estudiantes/académica/universitaria:** (Indicar claramente si ofrecen este beneficio, si es 100% gratuito, de prueba extendida o con descuento. Si no se menciona, indicar "No especificado").
4. **Link para solicitar la licencia:** (Extrae el enlace directo o la sección de la página donde los estudiantes/profesores pueden postular o registrarse para obtener el beneficio).
5. **¿De qué trata cada software?:** (Una descripción breve, clara y concisa de la función principal de cada programa listado).
6. **Licenciaturas académicas que pueden usarla:** (Lista de carreras universitarias o áreas del conocimiento que le sacarían el mayor provecho a estas herramientas, basándote en sus funciones).

Presenta la información de forma muy visual, usando negritas y listas con viñetas para que sea fácil de escanear."""

# Modo 2: Membresía (asociación / organización)
PROMPT_MEMBRESIA = """Analiza la siguiente página web: {url}

Visita el enlace anterior, analiza su contenido (asumiendo que se trata de una asociación, organismo o institución que ofrece membresías) y genera un reporte estructurado en formato de FICHA TÉCNICA que identifique exactamente los siguientes puntos:

1. **Nombre de la organización/asociación.**
2. **Costo de la membresía:** (Indica el precio o rangos de precio según el tipo de membresía, en la moneda en que se publique).
3. **¿Ofrece gratuidad en la membresía?:** (Indicar claramente si existe una opción 100% gratuita para estudiantes, académicos o instituciones. Si no se menciona, indicar "No especificado").
4. **Link para solicitar la membresía:** (Extrae el enlace directo o la sección de la página donde se puede aplicar o registrar).
5. **Tipos de membresía que ofrece:** (Ej. Institucional, Individual, Estudiantil/Student, Corporativa, etc. — lista todas las que encuentres).
6. **Correo o link de contacto:** (Extrae el correo electrónico o el enlace a la página de contacto).
7. **¿De qué trata la organización?:** (Breve descripción de su propósito y a qué público sirve).
8. **Licenciaturas/áreas académicas relacionadas:** (Carreras o disciplinas que más se beneficiarían de esta membresía).

Presenta la información de forma muy visual, usando negritas y listas con viñetas para que sea fácil de escanear."""

# Modo 3: Ficha completa (12 campos, estilo Arena Simulation) — con ejemplo few-shot
PROMPT_FICHA_COMPLETA = """Eres un analista que llena fichas técnicas de software académico. Debes seguir EXACTAMENTE el mismo formato, nivel de detalle, extensión y estilo del EJEMPLO que te muestro abajo. No agregues encabezados nuevos, no cambies el orden, no resumas de más ni te extiendas de menos respecto al ejemplo.

═══════════════════════════════════════
EJEMPLO DE FICHA CORRECTA (formato a imitar):
═══════════════════════════════════════

Nombre de Software
Arena Simulation Software

Desarrollador
Rockwell Automation

Tipo SW
Software de simulación de eventos discretos (Discrete Event Simulation - DES)

Tipo Licencia
Licencia académica gratuita para estudiantes, docentes e investigadores; licencias profesionales y de investigación disponibles para instituciones y empresas.

Página web del desarrollador
https://www.rockwellautomation.com/en-us/products/software/arena-simulation/buying-options/download.html

Introducción
Arena Simulation Software es una plataforma líder de simulación de eventos discretos utilizada para modelar, analizar y optimizar procesos complejos antes de implementarlos en el mundo real. Permite representar sistemas mediante diagramas de flujo visuales, ejecutar escenarios "What-if" y evaluar el impacto de cambios operativos sin riesgo para la organización. Es ampliamente utilizada en manufactura, logística, salud, minería, cadenas de suministro y operaciones empresariales.

Gestión de la Herramienta
* Instalación local en equipos Windows
* Modelado visual mediante diagramas de flujo
* Creación de simulaciones de eventos discretos
* Gestión de recursos, colas y procesos
* Ejecución de experimentos y escenarios alternativos
* Generación de reportes estadísticos
* Integración con Excel y bases de datos
* Optimización de procesos mediante simulación avanzada

Duración del acceso
* Versión académica disponible para uso educativo y de investigación
* Licencias institucionales y de laboratorio disponibles para universidades
* Versión de prueba gratuita disponible para estudiantes y académicos.

Método de Asignación
* Registro mediante cuenta de Rockwell Automation
* Descarga desde el Product Compatibility and Download Center
* Licencia académica disponible para estudiantes, profesores e investigadores
* Las universidades pueden adquirir paquetes de laboratorio con licencias concurrentes para múltiples usuarios
* Licencia destinada exclusivamente a fines académicos y no comerciales.

Uso individual o institucional
Uso académico, institucional, investigación y empresarial.

Versión del software o herramienta
* Arena Professional Edition
* Arena Academic Lab Package
* Arena Research Edition
* Arena Student Edition
* OptQuest for Arena (optimización basada en simulación)

Requisitos técnicos
* Sistema Operativo: Windows 10/11
* Compatible con Microsoft Office
* Procesador multinúcleo recomendado
* Memoria RAM ≥ 8 GB
* Espacio libre para proyectos de simulación
* Conexión a internet para descarga y activación.

Precio
* Versión de prueba gratuita disponible
* Student Edition gratuita para fines académicos
* Academic Lab Package mediante licenciamiento institucional
* Licencias profesionales disponibles para empresas.

Contenido del Software
* Simulación de eventos discretos
* Modelado de procesos productivos
* Simulación de cadenas de suministro
* Gestión de colas y recursos
* Simulación logística
* Simulación de centros de atención (Call Centers)
* Simulación de hospitales y sistemas de salud
* Simulación minera y manufacturera
* Optimización mediante OptQuest
* Análisis estadístico de desempeño
* Generación automática de reportes
* Integración con Excel y bases de datos empresariales.

Detalles técnicos
* Basado en tecnología SIMAN
* Interfaz gráfica basada en diagramas de flujo
* No requiere programación avanzada para construir modelos
* Compatible con Visual Basic for Applications (VBA)
* Integración con Microsoft Excel, Access y Visio
* Capacidad para modelar sistemas complejos con miles de entidades
* Utilizado por empresas como General Motors, Ford, UPS, IBM y Nike
* Considerado uno de los estándares mundiales en simulación de eventos discretos.

Programas formativos relacionados con la herramienta
* Ingeniería Industrial
* Logística y Cadena de Suministro
* Administración de Operaciones
* Investigación de Operaciones
* Ingeniería Mecánica
* Ingeniería de Manufactura
* Gestión de Proyectos
* Ingeniería de Procesos
* Analítica de Negocios
* Ciencia de Datos aplicada a Operaciones
* MBA en Operaciones y Producción
* Ingeniería en Transporte y Movilidad

Contacto
https://www.rockwellautomation.com/en-us/products/software/arena-simulation/buying-options/download.html

═══════════════════════════════════════
FIN DEL EJEMPLO. Ahora genera la ficha real:
═══════════════════════════════════════

Software a investigar: {nombre_software}
URL de referencia: {url}

Visita la URL, investiga sobre "{nombre_software}" y genera SU FICHA usando exactamente los mismos 17 encabezados que viste en el ejemplo, en el mismo orden, con el mismo estilo de redacción (listas con viñetas "*" donde el ejemplo usa viñetas, párrafo corrido donde el ejemplo usa párrafo, mismo nivel de detalle — ni más breve ni más largo). Usa negritas markdown (**Encabezado**) para cada título de campo, igual que en el ejemplo.

Si para algún campo no encuentras información verificable en la página o por búsqueda, escribe "No especificado" en ese campo — nunca lo omitas y nunca inventes datos."""

# ── Random icon ───────────────────────────────────────────────────────────────
ICONS = ["🎓", "🔬", "📐", "🖥️", "📊", "🧪", "🏫", "📡", "🧬", "⚗️", "🛰️", "🔭", "📱", "🧮", "💡"]

# ── Frases rotativas para el spinner (motivacionales/curiosas, tema investigación y tecnología) ──
SPINNER_QUOTES = [
    "La tecnología es mejor cuando reúne a las personas. — Matt Mullenweg",
    "La ciencia es una forma de pensar mucho más que un cuerpo de conocimiento. — Carl Sagan",
    "El primer paso es establecer que algo es posible; después la probabilidad ocurrirá. — Elon Musk",
    "La innovación distingue a un líder de un seguidor. — Steve Jobs",
    "No hay datos como los datos. — paráfrasis del mundo de la ingeniería",
    "Cada gran avance científico empezó con una pregunta incómoda.",
    "La investigación es ver lo que todos han visto y pensar lo que nadie ha pensado. — Albert Szent-Györgyi",
    "El conocimiento se duplica cada par de años; aprender a buscarlo bien ya es una ventaja.",
    "La curiosidad es el motor de todo descubrimiento.",
    "Detrás de cada software hay una pregunta que alguien decidió resolver.",
    "Una licencia académica bien usada puede valer más que mil horas de prueba y error.",
    "La tecnología no resuelve problemas; las personas que la usan bien, sí.",
]

if "page_icon" not in st.session_state:
    st.session_state.page_icon = "🎓"
if "pending_job" not in st.session_state:
    st.session_state.pending_job = None  # dict: {type, url, nombre_software?}
if "current_quote" not in st.session_state:
    st.session_state.current_quote = random.choice(SPINNER_QUOTES)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(
    f"<div style='text-align:center; font-size: 72px; line-height: 1; margin-bottom: 8px;'>"
    f"{st.session_state.page_icon}</div>",
    unsafe_allow_html=True,
)
st.title("Analizador de Software y Membresías Académicas")
st.markdown(
    "Analiza proveedores de software, asociaciones con membresías, o genera una ficha "
    "técnica completa de un software específico."
)

# Frase persistente: se asigna una al cargar la página y se reemplaza con cada
# nueva búsqueda, quedándose visible (no desaparece al terminar el análisis).
st.markdown(
    f"<p style='text-align:center; color:#888; font-size:14px; margin-top:-6px;'>"
    f"💭 {st.session_state.current_quote}</p>",
    unsafe_allow_html=True,
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


def run_gemini(prompt_text):
    """Llama a Gemini con grounding de Google Search y devuelve el texto de respuesta."""
    client = genai.Client(api_key=api_key)
    grounding_tool = types.Tool(google_search=types.GoogleSearch())
    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        tools=[grounding_tool],
        temperature=0.3,
        max_output_tokens=3000,
    )
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt_text,
        config=config,
    )
    return response.text


def rotate_icon_and_quote():
    current_icon = st.session_state.page_icon
    st.session_state.page_icon = random.choice([i for i in ICONS if i != current_icon])

    current_quote = st.session_state.current_quote
    st.session_state.current_quote = random.choice([q for q in SPINNER_QUOTES if q != current_quote])


def render_result(result_text, url, download_name):
    st.success("✅ Análisis completado")
    st.markdown(f'<div class="url-badge">🔗 {url}</div>', unsafe_allow_html=True)
    st.markdown(result_text)
    st.divider()
    st.download_button(
        label="⬇️ Descargar reporte (.md)",
        data=result_text,
        file_name=download_name,
        mime="text/markdown",
        key=f"dl_{download_name}",
    )


def handle_error(e):
    err = str(e)
    if "API_KEY_INVALID" in err or "API key not valid" in err:
        st.error("❌ API Key inválida. Verifica tu clave en [Google AI Studio](https://aistudio.google.com/app/apikey).")
    elif "quota" in err.lower():
        st.error("❌ Cuota de API excedida. Intenta más tarde o revisa tu plan en Google AI Studio.")
    elif "404" in err and "NOT_FOUND" in err:
        st.error("❌ El modelo de Gemini usado ya no está disponible. Contacta al desarrollador para actualizar el código.")
    else:
        st.error(f"❌ Error al analizar: {err}")


# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_software, tab_membresia, tab_ficha = st.tabs(["💻 Software", "🪪 Membresía", "📋 Ficha completa"])

# ── TAB 1: Software ───────────────────────────────────────────────────────────
with tab_software:
    url_sw = st.text_input(
        "URL del proveedor de software",
        placeholder="https://www.mathworks.com",
        key="url_software",
    )
    if st.button("🔍 Analizar software", use_container_width=True, type="primary", key="btn_software"):
        url = url_sw.strip()
        if not url:
            st.warning("⚠️ Por favor ingresa una URL válida.")
        elif not url.startswith(("http://", "https://")):
            st.error("❌ La URL debe comenzar con https:// o http://")
        else:
            rotate_icon_and_quote()
            st.session_state.pending_job = {"type": "software", "url": url}
            st.rerun()

# ── TAB 2: Membresía ───────────────────────────────────────────────────────────
with tab_membresia:
    url_mem = st.text_input(
        "URL de la asociación u organización",
        placeholder="https://www.ieee.org",
        key="url_membresia",
    )
    if st.button("🔍 Analizar membresía", use_container_width=True, type="primary", key="btn_membresia"):
        url = url_mem.strip()
        if not url:
            st.warning("⚠️ Por favor ingresa una URL válida.")
        elif not url.startswith(("http://", "https://")):
            st.error("❌ La URL debe comenzar con https:// o http://")
        else:
            rotate_icon_and_quote()
            st.session_state.pending_job = {"type": "membresia", "url": url}
            st.rerun()

# ── TAB 3: Ficha completa ──────────────────────────────────────────────────────
with tab_ficha:
    nombre_sw = st.text_input(
        "Nombre del software",
        placeholder="Arena Simulation Software",
        key="nombre_ficha",
    )
    url_ficha = st.text_input(
        "URL de referencia",
        placeholder="https://www.rockwellautomation.com/...",
        key="url_ficha",
    )
    if st.button("📋 Generar ficha completa", use_container_width=True, type="primary", key="btn_ficha"):
        url = url_ficha.strip()
        nombre = nombre_sw.strip()
        if not nombre:
            st.warning("⚠️ Por favor ingresa el nombre del software.")
        elif not url:
            st.warning("⚠️ Por favor ingresa una URL de referencia.")
        elif not url.startswith(("http://", "https://")):
            st.error("❌ La URL debe comenzar con https:// o http://")
        else:
            rotate_icon_and_quote()
            st.session_state.pending_job = {"type": "ficha", "url": url, "nombre_software": nombre}
            st.rerun()

# ── Ejecutar análisis si hay un trabajo pendiente ─────────────────────────────
if st.session_state.pending_job:
    job = st.session_state.pending_job
    st.session_state.pending_job = None

    try:
        ACTION_TEXT = {
            "software": "🌐 Visitando la página y analizando software...",
            "membresia": "🌐 Visitando la página y analizando membresía...",
            "ficha": f"🌐 Generando ficha técnica de {job.get('nombre_software', '')}...",
        }

        with st.spinner(ACTION_TEXT[job["type"]]):
            if job["type"] == "software":
                result_text = run_gemini(PROMPT_SOFTWARE.format(url=job["url"]))
            elif job["type"] == "membresia":
                result_text = run_gemini(PROMPT_MEMBRESIA.format(url=job["url"]))
            elif job["type"] == "ficha":
                result_text = run_gemini(
                    PROMPT_FICHA_COMPLETA.format(url=job["url"], nombre_software=job["nombre_software"])
                )

        if job["type"] == "software":
            render_result(result_text, job["url"], "reporte_software.md")
        elif job["type"] == "membresia":
            render_result(result_text, job["url"], "reporte_membresia.md")
        elif job["type"] == "ficha":
            render_result(result_text, job["url"], f"ficha_{job['nombre_software'].replace(' ', '_')}.md")

    except Exception as e:
        handle_error(e)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<small style='color: #999;'>Powered by Gemini 2.5 Flash + Google Search · "
    "Desplegado en Streamlit Cloud</small>",
    unsafe_allow_html=True,
)
