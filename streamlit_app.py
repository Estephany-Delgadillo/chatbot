import streamlit as st
import PyPDF2
import google.generativeai as genai
import os

st.set_page_config(page_title="Asistente del Manual", page_icon="📚")
st.title("📚 Asistente del Manual")
st.write("Haz preguntas sobre el manual de usuario")

try:
    api_key = st.secrets["google"]["api_key"]
    genai.configure(api_key=api_key)
    
    PDF_PATH = "manual.pdf"
    
    if os.path.exists(PDF_PATH):
        with st.spinner("Cargando el manual..."):
            lector_pdf = PyPDF2.PdfReader(PDF_PATH)
            texto_completo = ""
            
            for pagina in lector_pdf.pages:
                texto_completo += pagina.extract_text()
            
            st.success(f"✅ Manual cargado: {len(texto_completo)} caracteres")
            
            # USAR ESTE NOMBRE EXACTO DEL MODELO
            modelo = genai.GenerativeModel('models/gemini-pro')
            
            if "mensajes" not in st.session_state:
                st.session_state.mensajes = []
            
            for mensaje in st.session_state.mensajes:
                with st.chat_message(mensaje["role"]):
                    st.markdown(mensaje["content"])
            
            if pregunta := st.chat_input("¿Qué necesitas saber del manual?"):
                st.session_state.mensajes.append({"role": "user", "content": pregunta})
                with st.chat_message("user"):
                    st.markdown(pregunta)
                
                with st.chat_message("assistant"):
                    with st.spinner("Buscando en el manual..."):
                        try:
                            prompt = f"""
                            Basándote SOLO en el siguiente manual, responde la pregunta.
                            Si la respuesta no está en el manual, di "Esta información no está en el manual".
                            
                            MANUAL:
                            {texto_completo[:8000]}
                            
                            PREGUNTA: {pregunta}
                            
                            RESPUESTA:
                            """
                            
                            respuesta = modelo.generate_content(prompt)
                            st.markdown(respuesta.text)
                            st.session_state.mensajes.append({"role": "assistant", "content": respuesta.text})
                            
                        except Exception as e:
                            st.error(f"Error: {e}")
                            # Mostrar modelos disponibles
                            try:
                                modelos = genai.list_models()
                                st.write("Modelos disponibles:")
                                for m in modelos:
                                    if 'generateContent' in m.supported_generation_methods:
                                        st.write(f"- {m.name}")
                            except:
                                pass
                            
    else:
        st.error(f"❌ No se encontró '{PDF_PATH}'")

except Exception as e:
    st.error(f"Error de configuración: {e}")