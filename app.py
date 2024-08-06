import os
import streamlit as st
from duckduckgo_search import DDGS
from openai import OpenAI
import pandas as pd

# Configuración de Streamlit
st.set_page_config(page_title="WebNavigatorAI", layout="wide")

# Función de búsqueda mejorada
def buscar_en_duckduckgo(consulta, num_results=5):
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(consulta, max_results=num_results))
        return results
    except Exception as e:
        st.error(f"Error al buscar en DuckDuckGo: {str(e)}")
        return []

# Función para interactuar con OpenAI
def charla_con_openai(client, consulta, contexto, modelo="gpt-4o-mini"):
    try:
        messages = [
            {"role": "system", "content": "Eres un asistente de búsqueda experto que interpreta y proporciona respuestas basadas en resultados de búsqueda web proporcionados al usuario. Proporciona respuestas concisas y relevantes."},
            {"role": "user", "content": f"Consulta: {consulta}\n\nContexto de búsqueda:\n{contexto}"}
        ]
        response = client.chat.completions.create(model=modelo, messages=messages)
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error al comunicarse con OpenAI: {str(e)}")
        return "Lo siento, ocurrió un error al procesar tu consulta."

# Configuración de OpenAI
API_KEY = os.environ.get('OPENAI_API_KEY') or st.secrets.get('OPENAI_API_KEY')
if not API_KEY:
    API_KEY = st.text_input('Ingresa tu API Key de OpenAI:', type='password')
    if not API_KEY:
        st.error("Se requiere una API Key de OpenAI para continuar.")
        st.stop()

client = OpenAI(api_key=API_KEY)

# Interfaz de usuario
st.title("WebNavigatorAI 🌐")
st.write("Tu asistente virtual especializado en búsquedas de Internet.")

consulta = st.text_input("¿Qué deseas buscar hoy?")

if consulta:
    with st.spinner('Buscando información...'):
        resultados = buscar_en_duckduckgo(consulta)
        
        if resultados:
            # Crear un DataFrame con los resultados
            df = pd.DataFrame(resultados)
            st.subheader("Resultados de la búsqueda:")
            st.dataframe(df[['title', 'body']].head())
            
            # Preparar contexto para OpenAI
            contexto = "\n".join([f"Título: {r['title']}\nResumen: {r['body']}\nURL: {r['href']}" for r in resultados[:3]])
            
            with st.spinner('Analizando resultados...'):
                respuesta_ai = charla_con_openai(client, consulta, contexto)
            
            st.subheader("Resumen de la IA:")
            st.write(respuesta_ai)
            
            # Mostrar fuentes
            st.subheader("Fuentes:")
            for r in resultados[:3]:
                st.markdown(f"- [{r['title']}]({r['href']})")
        else:
            st.warning("No se encontraron resultados. Por favor, intenta reformular tu búsqueda.")

# Footer
st.sidebar.markdown('---')
st.sidebar.subheader('Creado por:')
st.sidebar.markdown('Alexander Oviedo Fadul')
st.sidebar.markdown("[GitHub](https://github.com/bladealex9848) | [Website](https://alexander.oviedo.isabellaea.com/) | [Instagram](https://www.instagram.com/alexander.oviedo.fadul) | [Twitter](https://twitter.com/alexanderofadul) | [Facebook](https://www.facebook.com/alexanderof/) | [WhatsApp](https://api.whatsapp.com/send?phone=573015930519&text=Hola%20!Quiero%20conversar%20contigo!%20)")