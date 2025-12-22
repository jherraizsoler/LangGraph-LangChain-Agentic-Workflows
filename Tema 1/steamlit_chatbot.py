from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
import streamlit as st
# SE IMPORTA LA CLASE PARA DIFINIR PLANTILLAS
from langchain_core.prompts import PromptTemplate


prompt_template = PromptTemplate(
    input_variables=["mensaje", "historial"],
    template="""Eres un asistente útil y amigable llamado ChatBot Pro. 
 
Historial de conversación:
{historial}
 
Responde de manera clara y concisa a la siguiente pregunta: {mensaje}"""
)



# Configurar la pagina de la app
st.set_page_config(page_title="Chatbot Básico", page_icon="🤖") 
st.title("🤖 Chatbot Básico con LangChain y Streamlit desarrollado por Jorge Herraiz Soler")
st.markdown("Este es un *chatbot de ejemplo* construido con LangChain y Streamlit. \n\n¡Escribe tu mensaje abajo para comenzar!")

with st.sidebar:
    st.header("Configuración")
    temperature = st.slider("Temperatura", 0.0, 1.0, 0.5, 0.1)
    model_name = st.selectbox("Modelo", ["gpt-3.5-turbo", "gpt-4", "gpt-4o-mini"])

chat_model = ChatOpenAI(model="gpt-4o-mini", temperature=0.5)

# Inicializar el historial de mensajes en la sesión
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []
    
# Mostrar mensajes previos en la interfaz
for msg in st.session_state.mensajes:
    if isinstance(msg, SystemMessage):
        # No muestro el mensaje por pantalla
        continue
    role = "assistant" if isinstance(msg, AIMessage) else "user"
    with st.chat_message(role):
        st.markdown(msg.content)
  
if st.button("🗑️ Nueva conversación"):
    # ¿Qué necesitas limpiar?
        st.session_state.mensajes = []
        st.experimental_rerun()
    # ¿Qué función de Streamlit refresca la página?
        st.experimental_rerun()
        
# Cuadro de entrada de texto del usuario
pregunta = st.chat_input("Escribe tu mensaje:  ")
# En lugar de usar cadenas tradicionales, ahora puedes hacer:
cadena = prompt_template | chat_model


if pregunta:
    with st.chat_message("user"):
        st.markdown(pregunta)
    
    try:
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            full_response = ""
 
            # ¡Aquí está la magia del streaming!
            for chunk in cadena.stream({"mensaje": pregunta, "historial": st.session_state.mensajes}):
                full_response += chunk.content
                response_placeholder.markdown(full_response + "▌")  # El cursor parpadeante
            
            response_placeholder.markdown(full_response)
        
        # No olvides almacenar los mensajes
        st.session_state.mensajes.append(HumanMessage(content=pregunta))
        st.session_state.mensajes.append(AIMessage(content=full_response))
        
    except Exception as e:
        # ¿Qué tipo de errores podrían ocurrir aquí?
        st.error(f"Error al generar respuesta: {str(e)}")
        st.info("Verifica que tu API Key de OpenAI esté configurada correctamente.")
        