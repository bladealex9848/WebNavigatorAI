import os
import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
from openai import OpenAI
from openai import OpenAIError

# Configuración de Streamlit
st.set_page_config(
    page_title="WebNavigatorAI",    
    initial_sidebar_state='collapsed'
)

# Función para manejar errores de OpenAI
def handle_openai_error(e: OpenAIError) -> str:
    error_type = type(e).__name__
    if error_type == "APITimeoutError":
        return "La solicitud a OpenAI excedió el tiempo límite. Por favor, inténtalo de nuevo."
    elif error_type == "InvalidAPIType":
        return "Error en la configuración de la API de OpenAI. Verifica tu configuración."
    elif error_type == "APIConnectionError":
        return "No se pudo conectar con OpenAI. Verifica tu conexión a internet."
    elif error_type == "APIError":
        return "Error general de la API de OpenAI. Por favor, inténtalo de nuevo más tarde."
    elif error_type == "AuthenticationError":
        return "Error de autenticación. Verifica tu API key de OpenAI."
    elif error_type == "BadRequestError":
        return "Solicitud inválida a OpenAI. Verifica los parámetros de tu solicitud."
    elif error_type == "PermissionDeniedError":
        return "No tienes permiso para realizar esta acción. Verifica tus credenciales y permisos."
    elif error_type == "RateLimitError":
        return "Has excedido el límite de solicitudes a OpenAI. Espera un momento antes de intentar de nuevo."
    elif error_type == "InternalServerError":
        return "Error interno del servidor de OpenAI. Por favor, inténtalo de nuevo más tarde."
    else:
        return f"Error inesperado: {str(e)}"

# Cargar API Key
API_KEY = os.environ.get('OPENAI_API_KEY')

if not API_KEY:
    try:
        API_KEY = st.secrets['OPENAI_API_KEY']
    except:
        API_KEY = None

if not API_KEY:
    API_KEY = st.text_input('OpenAI API Key', type='password')

if not API_KEY:
    st.error("Se requiere una API Key de OpenAI para continuar.")
    st.stop()

# Inicializar el cliente de OpenAI
try:
    client = OpenAI(api_key=API_KEY)
except Exception as e:
    st.error(f"Error al inicializar el cliente de OpenAI: {str(e)}")
    st.stop()

# Funciones
def buscar_en_duckduckgo(consulta):
    try:
        base_url = "https://duckduckgo.com/html/"
        params = {"q": consulta}
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
        response = requests.get(base_url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        resultado = soup.find("div", class_="result__body")
        if resultado:
            texto = resultado.get_text(strip=True)
            url = resultado.find("a", class_="result__url").get("href")
            return texto, url
        else:
            return None, None
    except requests.RequestException as e:
        st.error(f"Error al buscar en DuckDuckGo: {str(e)}")
        return None, None

def limpiar_texto(texto):
    texto = re.sub(r'http\S+', '', texto)
    texto = ' '.join(texto.split())
    return texto

def charla_con_openai(consulta, messages) -> str:
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )
        return response.choices[0].message.content
    except OpenAIError as e:
        error_message = handle_openai_error(e)
        st.error(error_message)
        return f"Lo siento, ocurrió un error: {error_message}"
    except Exception as e:
        st.error(f"Error inesperado: {str(e)}")
        return "Lo siento, ocurrió un error inesperado."

# Selector de idioma
languages = ["Español", "English"]
selected_language = st.sidebar.selectbox("Language", languages, index=languages.index("Español"))

if selected_language == "English":
    title = "WebNavigatorAI 🌐"
    subtitle = """
Hello! I'm **WebNavigatorAI**, your specialized virtual assistant for internet searches. 🚀

With the combination of web navigation and the power of artificial intelligence, I'm here to help you find the information you need quickly and accurately. Whether you're looking for specific data, articles, news, or any other type of information on the web, I'm here to assist you!

How can I assist you today? 🔍
"""
    input_placeholder = "Type your query:"
else:
    title = "WebNavigatorAI 🌐"
    subtitle = """
¡Hola! Soy **WebNavigatorAI**, tu asistente virtual especializado en búsquedas de Internet. 🚀

Con la combinación de navegación web y la potencia de la inteligencia artificial, estoy aquí para ayudarte a encontrar la información que necesitas de manera rápida y precisa. Ya sea que estés buscando datos específicos, artículos, noticias o cualquier otro tipo de información en la web, ¡estoy aquí para asistirte!

¿En qué puedo ayudarte hoy? 🔍
"""
    input_placeholder = "Escribe tu consulta:"

st.title(title)
st.write(subtitle)

consulta = st.text_input(input_placeholder)

if consulta:
    texto, url = buscar_en_duckduckgo(consulta)
    if texto and url:
        texto_limpio = limpiar_texto(texto)
        consulta_ampliada = f"Consulta: {consulta}\n\nURL del resultado: {url}\n\nDetalles: {texto_limpio}"
        system_message = "You are an expert search assistant who interprets and provides answers based on web search results provided to the user. You don't need to access the web, but you must process the information given to answer clearly and concisely." if selected_language == "English" else "Eres un asistente de búsqueda experto que interpreta y proporciona respuestas basadas en resultados de búsqueda web proporcionados al usuario. No necesitas acceder a la web, pero debes procesar la información dada para responder de manera clara y concisa."
        respuesta_openai = charla_con_openai(consulta_ampliada, [{"role": "system", "content": system_message}, {"role": "user", "content": consulta_ampliada}])
        
        source_word = "Source" if selected_language == "English" else "Fuente"
        
        container_md = f"""
        <div style="background-color:#e6e6e6; padding:15px; border-radius:10px; position:relative;">
            <b>WebNavigatorAI:</b> {respuesta_openai}<br><br>
            <b>{source_word}:</b> <a href="{url}" target="_blank">{url}</a>    
        </div>
        """

        st.markdown(container_md, unsafe_allow_html=True)
        
    else:
        st.warning("No se encontraron resultados para tu consulta. Intenta reformularla." if selected_language == "Español" else "No results found for your query. Try rephrasing it.")
        system_message = ("You are a helpful assistant." if selected_language == "English" 
                          else "Eres un asistente útil.")
        consulta_ampliada = consulta
        
        respuesta_openai = charla_con_openai(consulta_ampliada, [{"role": "system", "content": system_message}, {"role": "user", "content": consulta_ampliada}])
        
        fuente = "OpenAI, modelo: gpt-4o-mini"
        
        container_md = f"""
<div style="background-color:#e6e6e6; padding:15px; border-radius:10px;">
    <b>WebNavigatorAI:</b> {respuesta_openai}<br><br>
    <b>Fuente:</b> {fuente}
</div>
"""
        st.markdown(container_md, unsafe_allow_html=True)

# Footer
st.sidebar.markdown('---')
st.sidebar.subheader('Created by' if selected_language == "English" else 'Creado por:')
st.sidebar.markdown('Alexander Oviedo Fadul')
st.sidebar.markdown("[GitHub](https://github.com/bladealex9848) | [Website](https://alexander.oviedo.isabellaea.com/) | [Instagram](https://www.instagram.com/alexander.oviedo.fadul) | [Twitter](https://twitter.com/alexanderofadul) | [Facebook](https://www.facebook.com/alexanderof/) | [WhatsApp](https://api.whatsapp.com/send?phone=573015930519&text=Hola%20!Quiero%20conversar%20contigo!%20)")