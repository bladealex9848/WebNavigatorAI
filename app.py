import os
import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import openai

# Configuración de Streamlit
st.set_page_config(
    page_title="WebNavigatorAI",    
    initial_sidebar_state='collapsed'  # Esto debería funcionar, pero hay un problema en algunas versiones de Streamlit
)

# Cargar API Key
# Intenta cargar la API Key desde la variable de entorno
API_KEY = os.environ.get('OPENAI_API_KEY')

# Si no está en la variable de entorno, intenta cargar desde st.secrets
if not API_KEY:
    try:
        API_KEY = st.secrets['OPENAI_API_KEY']
    except:
        API_KEY = None

# Si aún no la tienes, pide al usuario que la introduzca
if not API_KEY:
    API_KEY = st.text_input('OpenAI API Key', type='password')

# Si no se proporciona la API Key, detener la ejecución
if not API_KEY:
    st.stop()

openai.api_key = API_KEY

# Funciones
def buscar_en_duckduckgo(consulta):
    base_url = "https://duckduckgo.com/html/"
    params = {"q": consulta}
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
    response = requests.get(base_url, params=params, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    resultado = soup.find("div", class_="result__body")
    if resultado:
        texto = resultado.get_text(strip=True)
        url = resultado.find("a", class_="result__url").get("href")
        return texto, url
    else:
        return None, None

def limpiar_texto(texto):
    texto = re.sub(r'http\S+', '', texto)
    texto = ' '.join(texto.split())
    return texto

def charla_con_openai(consulta, messages):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    return response.choices[0].message["content"]

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
        text_to_copy = f"WebNavigatorAI: {respuesta_openai}\n\n{source_word}: {url}" 

        container_md = f"""
        <div style="background-color:#e6e6e6; padding:15px; border-radius:10px; position:relative;">
            <b>WebNavigatorAI:</b> {respuesta_openai}<br><br>
            <b>{source_word}:</b> <a href="{url}" target="_blank">{url}</a>    
        </div>
        """

        st.markdown(container_md, unsafe_allow_html=True)
        
    else:
        error_message = "Sorry, I couldn't find any relevant information for your query." if selected_language == "English" else "Lo siento, no pude encontrar información relevante para tu consulta."
        st.write(f"**WebNavigatorAI**: {error_message}")

# Footer
st.sidebar.markdown('---')
st.sidebar.subheader('Created by' if selected_language == "English" else 'Creado por:')
st.sidebar.markdown('Alexander Oviedo Fadul')
st.sidebar.markdown("[GitHub](https://github.com/bladealex9848) | [Website](https://alexander.oviedo.isabellaea.com/) | [Instagram](https://www.instagram.com/alexander.oviedo.fadul) | [Twitter](https://twitter.com/alexanderofadul) | [Facebook](https://www.facebook.com/alexanderof/) | [WhatsApp](https://api.whatsapp.com/send?phone=573015930519&text=Hola%20!Quiero%20conversar%20contigo!%20)")