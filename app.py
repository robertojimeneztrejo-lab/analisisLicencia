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
Tienes dos herramientas: una para leer directamente el contenido de la URL que te da el usuario (url_context),
y otra de búsqueda web (google_search) para complementar con información adicional si la página
no tiene todo el detalle necesario (por ejemplo, búscando el nombre de la organización + "membership types",
"pricing", "join", etc.).

Usa SIEMPRE primero la lectura directa de la URL proporcionada. Si esa página no contiene algún dato
específico, usa la búsqueda web para completarlo en vez de rendirte. Solo si después de ambos intentos
no encuentras un dato, indica "No especificado" en ESE campo puntual — nunca abandones el reporte completo
por no encontrar uno o dos datos. Siempre entrega los 6-8 puntos solicitados con el formato pedido,
aunque algunos campos queden como "No especificado".

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

# ── Iconos SVG estilo cartoon: temática de superpoderes (diseño original) ───
SVG_ICONS = {
    "rayo": '''<svg viewBox="0 0 100 100" width="110" height="110">
        <path d="M58 8 L26 56 L46 56 L40 92 L76 42 L54 42Z" fill="#FFD43B"/>
        <path d="M58 8 L46 56 L40 92 L76 42 L54 42Z" fill="#FFB84D"/>
    </svg>''',
    "escudo": '''<svg viewBox="0 0 100 100" width="110" height="110">
        <circle cx="50" cy="50" r="36" fill="#74C0FC"/>
        <circle cx="50" cy="50" r="26" fill="#FFFFFF"/>
        <circle cx="50" cy="50" r="16" fill="#FF6B6B"/>
        <circle cx="50" cy="50" r="6" fill="#FFD43B"/>
    </svg>''',
    "alas": '''<svg viewBox="0 0 100 100" width="110" height="110">
        <path d="M50 90 C30 75 18 58 18 40 C18 22 32 12 50 22 C68 12 82 22 82 40 C82 58 70 75 50 90Z" fill="#74C0FC"/>
        <path d="M50 90 C50 75 50 50 50 22" stroke="#FFFFFF" stroke-width="3" fill="none"/>
        <path d="M30 35 C36 30 42 30 46 35 M54 35 C58 30 64 30 70 35" stroke="#FFFFFF" stroke-width="3" fill="none" stroke-linecap="round"/>
    </svg>''',
    "portal": '''<svg viewBox="0 0 100 100" width="110" height="110">
        <ellipse cx="50" cy="50" rx="30" ry="38" fill="#A5D8FF"/>
        <ellipse cx="50" cy="50" rx="22" ry="30" fill="#74C0FC"/>
        <ellipse cx="50" cy="50" rx="13" ry="20" fill="#FFFFFF" opacity="0.7"/>
        <rect x="44" y="84" width="12" height="10" rx="3" fill="#868E96"/>
    </svg>''',
    "explosion": '''<svg viewBox="0 0 100 100" width="110" height="110">
        <path d="M50 10 L62 38 L92 42 L68 62 L76 90 L50 74 L24 90 L32 62 L8 42 L38 38Z" fill="#FFD43B"/>
        <path d="M50 10 L62 38 L92 42 L68 62 L76 90 L50 74Z" fill="#FF6B6B" opacity="0.8"/>
    </svg>''',
    "fuego": '''<svg viewBox="0 0 100 100" width="110" height="110">
        <path d="M50 90 C30 75 26 55 32 38 C36 26 44 18 50 10 C56 18 64 26 68 38 C74 55 70 75 50 90Z" fill="#FF6B6B"/>
        <path d="M50 78 C40 68 38 54 42 42 C44 36 47 30 50 24 C53 30 56 36 58 42 C62 54 60 68 50 78Z" fill="#FFB84D"/>
        <path d="M50 64 C46 58 45 50 48 44 C49 41 50 38 50 38 C50 38 51 41 52 44 C55 50 54 58 50 64Z" fill="#FFD43B"/>
    </svg>''',
    "martillo": '''<svg viewBox="0 0 100 100" width="110" height="110">
        <rect x="42" y="14" width="16" height="34" rx="4" fill="#868E96"/>
        <rect x="22" y="14" width="56" height="20" rx="6" fill="#74C0FC"/>
        <rect x="44" y="48" width="12" height="38" rx="3" fill="#A05A2C"/>
    </svg>''',
    "fuerza": '''<svg viewBox="0 0 100 100" width="110" height="110">
        <circle cx="32" cy="32" r="18" fill="#FFC078"/>
        <rect x="22" y="44" width="20" height="12" rx="4" fill="#495057"/>
        <circle cx="68" cy="32" r="18" fill="#FFC078"/>
        <rect x="58" y="44" width="20" height="12" rx="4" fill="#495057"/>
        <path d="M40 38 L60 38" stroke="#FFD43B" stroke-width="5" stroke-linecap="round"/>
    </svg>''',
    "arco": '''<svg viewBox="0 0 100 100" width="110" height="110">
        <path d="M30 20 Q24 50 30 80" fill="none" stroke="#74C0FC" stroke-width="6" stroke-linecap="round"/>
        <path d="M30 20 L78 50 L30 80" fill="none" stroke="#495057" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
        <line x1="30" y1="50" x2="84" y2="50" stroke="#FF6B6B" stroke-width="3"/>
        <path d="M84 50 L74 44 L74 56Z" fill="#FF6B6B"/>
    </svg>''',
    "telarana": '''<svg viewBox="0 0 100 100" width="110" height="110">
        <circle cx="50" cy="50" r="36" fill="none" stroke="#868E96" stroke-width="2"/>
        <circle cx="50" cy="50" r="24" fill="none" stroke="#868E96" stroke-width="2"/>
        <circle cx="50" cy="50" r="12" fill="none" stroke="#868E96" stroke-width="2"/>
        <line x1="50" y1="14" x2="50" y2="86" stroke="#868E96" stroke-width="2"/>
        <line x1="14" y1="50" x2="86" y2="50" stroke="#868E96" stroke-width="2"/>
        <line x1="24" y1="24" x2="76" y2="76" stroke="#868E96" stroke-width="2"/>
        <line x1="76" y1="24" x2="24" y2="76" stroke="#868E96" stroke-width="2"/>
    </svg>''',
    "tridente": '''<svg viewBox="0 0 100 100" width="110" height="110">
        <rect x="46" y="40" width="8" height="46" rx="3" fill="#A05A2C"/>
        <path d="M50 12 L40 40 L60 40Z" fill="#74C0FC"/>
        <path d="M50 12 L30 30 L40 40Z" fill="#A5D8FF"/>
        <path d="M50 12 L70 30 L60 40Z" fill="#A5D8FF"/>
    </svg>''',
    "flecha": '''<svg viewBox="0 0 100 100" width="110" height="110">
        <line x1="20" y1="80" x2="76" y2="24" stroke="#495057" stroke-width="5" stroke-linecap="round"/>
        <path d="M76 24 L62 26 L74 38Z" fill="#FF6B6B"/>
        <path d="M28 72 L20 80 L28 80Z" fill="#FFB84D"/>
        <path d="M20 80 L20 72Z" fill="#FFB84D"/>
    </svg>''',
    "torbellino": '''<svg viewBox="0 0 100 100" width="110" height="110">
        <path d="M50 14 C66 14 78 26 78 38 C78 48 70 52 60 50 C68 56 70 66 64 74 C58 66 50 64 44 68 C46 76 40 84 30 84 C36 76 32 68 24 66 C28 58 36 56 44 60 C32 56 26 46 30 36 C36 40 44 42 50 38 C42 32 40 22 50 14Z" fill="#74C0FC" opacity="0.85"/>
    </svg>''',
    "comunicador": '''<svg viewBox="0 0 100 100" width="110" height="110">
        <rect x="32" y="36" width="36" height="44" rx="8" fill="#74C0FC"/>
        <rect x="40" y="46" width="20" height="16" rx="3" fill="#FFFFFF"/>
        <circle cx="50" cy="54" r="5" fill="#A5D8FF"/>
        <path d="M50 30 C46 24 46 16 50 10 C54 16 54 24 50 30Z" fill="#868E96"/>
        <path d="M38 26 Q50 14 62 26" fill="none" stroke="#FFD43B" stroke-width="3" stroke-linecap="round"/>
        <path d="M34 32 Q50 14 66 32" fill="none" stroke="#FFD43B" stroke-width="3" stroke-linecap="round" opacity="0.6"/>
    </svg>''',
}

ICON_KEYS = list(SVG_ICONS.keys())

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

if "page_icon" not in st.session_state or st.session_state.page_icon not in SVG_ICONS:
    st.session_state.page_icon = "escudo"
if "pending_job" not in st.session_state:
    st.session_state.pending_job = None  # dict: {type, url, nombre_software?}
if "current_quote" not in st.session_state:
    st.session_state.current_quote = random.choice(SPINNER_QUOTES)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(
    f"<div style='text-align:center; margin-bottom: 8px;'>"
    f"{SVG_ICONS[st.session_state.page_icon]}</div>",
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


def _call_gemini_once(prompt_text, thinking_budget=1024):
    """Hace una sola llamada a Gemini con grounding + url_context.
    Devuelve (texto_extraido, finish_reason, num_parts, part_types).
    texto_extraido puede ser "" si la llamada no produjo contenido (caso conocido
    e intermitente de Gemini 2.5 Flash con herramientas de grounding activas)."""
    client = genai.Client(api_key=api_key)
    grounding_tool = types.Tool(google_search=types.GoogleSearch())
    url_context_tool = types.Tool(url_context=types.UrlContext())
    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        tools=[url_context_tool, grounding_tool],
        temperature=0.3,
        max_output_tokens=8000,
        thinking_config=types.ThinkingConfig(thinking_budget=thinking_budget),
    )
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt_text,
        config=config,
    )

    if not response.candidates:
        return "", None, 0, []

    candidate = response.candidates[0]
    finish_reason = getattr(candidate, "finish_reason", None)

    extracted_text = ""
    num_parts = 0
    part_types = []
    if candidate.content and candidate.content.parts:
        num_parts = len(candidate.content.parts)
        for part in candidate.content.parts:
            if getattr(part, "text", None):
                extracted_text += part.text
                part_types.append("text")
            elif getattr(part, "function_call", None):
                part_types.append("function_call")
            elif getattr(part, "executable_code", None):
                part_types.append("executable_code")
            else:
                part_types.append("other")

    if not extracted_text:
        extracted_text = response.text or ""

    return extracted_text, finish_reason, num_parts, part_types


def run_gemini(prompt_text, max_retries=2):
    """Llama a Gemini con grounding de Google Search + url_context, con reintentos automáticos.

    Gemini 2.5 Flash con herramientas de grounding activas tiene un bug conocido e
    intermitente: a veces devuelve finish_reason=STOP con 0 partes de contenido,
    sin ningún motivo de bloqueo (no es SAFETY, ni MAX_TOKENS, ni RECITATION).
    Es un fallo aleatorio del lado de la API, así que la mitigación estándar es
    reintentar la misma petición — casi siempre se resuelve en el 2do o 3er intento.
    """
    last_finish_reason = None
    last_num_parts = 0
    last_part_types = []

    for attempt in range(1, max_retries + 2):  # intento inicial + reintentos
        extracted_text, finish_reason, num_parts, part_types = _call_gemini_once(prompt_text)
        last_finish_reason, last_num_parts, last_part_types = finish_reason, num_parts, part_types

        if extracted_text:
            return extracted_text

        # Si fue un bloqueo real (no el bug de respuesta vacía), no tiene sentido reintentar igual.
        if finish_reason and any(r in str(finish_reason) for r in ("SAFETY", "RECITATION")):
            break

    # Se agotaron los intentos sin obtener texto.
    debug_info = f"(finish_reason: {last_finish_reason}, partes: {last_num_parts} {last_part_types}, intentos: {attempt})"
    if last_finish_reason and "SAFETY" in str(last_finish_reason):
        raise ValueError(f"La respuesta fue bloqueada por los filtros de seguridad de Gemini. {debug_info}")
    elif last_finish_reason and "MAX_TOKENS" in str(last_finish_reason):
        raise ValueError(f"La respuesta se cortó por exceder el límite de tokens. {debug_info}")
    elif last_finish_reason and "RECITATION" in str(last_finish_reason):
        raise ValueError(f"Gemini detectó posible contenido protegido en la página. {debug_info}")
    else:
        raise ValueError(
            f"Gemini no devolvió texto tras {attempt} intento(s) — es un fallo intermitente conocido "
            f"de la API con búsqueda activada. {debug_info} Vuelve a intentarlo en unos segundos."
        )


def rotate_icon_and_quote():
    current_icon = st.session_state.page_icon
    st.session_state.page_icon = random.choice([k for k in ICON_KEYS if k != current_icon])

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
    elif "bloqueada por los filtros de seguridad" in err:
        st.error("❌ La página no pudo analizarse: Gemini bloqueó la respuesta por sus filtros de seguridad. Intenta con otra URL.")
    elif "se cortó por exceder el límite" in err:
        st.error("❌ La respuesta fue demasiado larga y se cortó. Vuelve a intentarlo — a veces Gemini la genera más corta en el siguiente intento.")
    elif "contenido protegido" in err:
        st.error("❌ Gemini no pudo generar el reporte porque detectó posible contenido protegido en la página. Intenta con otra URL.")
    elif "no devolvió" in err.lower() or "sin candidatos" in err.lower():
        st.error(f"❌ {err} Vuelve a intentarlo — a veces es un fallo temporal de la API.")
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
