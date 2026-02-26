import streamlit as st
import PyPDF2
import google.generativeai as genai
import os

# Configurar página
st.set_page_config(page_title="Asistente del Manual", page_icon="📚")
st.title("📚 Asistente del Manual")
st.write("Haz preguntas sobre el manual de usuario")

# Configurar API Key desde Secrets de Streamlit
try:
    api_key = st.secrets["google"]["api_key"]
    genai.configure(api_key=api_key)
    
    # Cargar el PDF automáticamente
    PDF_PATH = "manual.pdf"
    
    if os.path.exists(PDF_PATH):
        with st.spinner("Cargando el manual..."):
            try:
                lector_pdf = PyPDF2.PdfReader(PDF_PATH)
                texto_completo = ""
                
                for pagina in lector_pdf.pages:
                    texto_completo += pagina.extract_text()
                
                st.success(f"✅ Manual cargado: {len(texto_completo)} caracteres")
                
                # Crear modelo
                modelo = genai.GenerativeModel('gemini-pro')
                
                # Historial
                if "mensajes" not in st.session_state:
                    st.session_state.mensajes = []
                
                # Mostrar historial
                for mensaje in st.session_state.mensajes:
                    with st.chat_message(mensaje["role"]):
                        st.markdown(mensaje["content"])
                
                # Input
                if pregunta := st.chat_input("¿Qué necesitas saber del manual?"):
                    st.session_state.mensajes.append({"role": "user", "content": pregunta})
                    with st.chat_message("user"):
                        st.markdown(pregunta)
                    
                    with st.chat_message("assistant"):
                        with st.spinner("Buscando en el manual..."):
                            prompt = f"""
                            Basándote SOLO en el siguiente manual, responde la pregunta.
                            Si la respuesta no está en el manual, di "Esta información no está en el manual".
                            
                            MANUAL:
                            {texto_completo[:10000]}
                            
                            PREGUNTA: {pregunta}
                            
                            RESPUESTA:
                            """
                            
                            respuesta = modelo.generate_content(prompt)
                            st.markdown(respuesta.text)
                            st.session_state.mensajes.append({"role": "assistant", "content": respuesta.text})
                            
            except Exception as e:
                st.error(f"Error al leer el PDF: {e}")
    else:
        st.error(f"❌ No se encontró el archivo '{PDF_PATH}'. Contacta al administrador.")

except Exception as e:
    st.error(f"Error de configuración: {e}")
    st.info("Contacta al administrador para configurar la API Key")