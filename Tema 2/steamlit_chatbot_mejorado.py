from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
import streamlit as st
# SE IMPORTA LA CLASE PARA DIFINIR PLANTILLAS
from langchain_core.prompts import ChatPromptTemplate


# Configurar la pagina de la app
st.set_page_config(page_title="Chatbot Básico", page_icon="🤖") 
st.title("🤖 Chatbot Básico con LangChain y Streamlit desarrollado por Jorge Herraiz Soler")
st.markdown("Este es un *chatbot de ejemplo* construido con LangChain y Streamlit. \n\n¡Escribe tu mensaje abajo para comenzar!")

with st.sidebar:
    st.header("Configuración")
    temperature = st.slider("Temperatura", 0.0, 1.0, 0.5, 0.1)
    model_name = st.selectbox("Modelo", ["gpt-3.5-turbo", "gpt-4", "gpt-4o-mini"])

    # ¡Nuevo! Personalidad configurable
    personalidad = st.selectbox(
        "Personalidad del Asistente",
        [
            "Útil y amigable",
            "Profesional y formal", 
            "Casual y relajado",
            "Experto técnico",
            "Creativo y divertido"
        ]
    )
    
    # Recrear modelo
    chat_model = ChatOpenAI(model=model_name, temperature=temperature)

    
    # Template dinámico basado en personalidad
    system_messages = {
        "Útil y amigable": "Eres un asistente útil y amigable llamado ChatBot Pro. Responde de manera clara y concisa.",
        "Profesional y formal": "Eres un asistente profesional y formal. Proporciona respuestas precisas y bien estructuradas.",
        "Casual y relajado": "Eres un asistente casual y relajado. Habla de forma natural y amigable, como un buen amigo.",
        "Experto técnico": "Eres un asistente experto técnico. Proporciona respuestas detalladas con precisión técnica.",
        "Creativo y divertido": "Eres un asistente creativo y divertido. Usa analogías, ejemplos creativos y mantén un tono alegre."
    }
    
    chat_prompt = ChatPromptTemplate.from_messages([
        ("system", system_messages[personalidad]),
        ("human", "Historial de conversación:\n{historial}\n\nPregunta actual: {mensaje}")
    ])
    
    cadena = chat_prompt | chat_model   

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



if pregunta:
    # Mostrar y almacenar mensaje del usuario
    with st.chat_message("user"):
        st.markdown(pregunta)
    
    # Preparar historial como texto
    historial_texto = ""
    for msg in st.session_state.mensajes[-10:]:  # Últimos 10 mensajes
        if isinstance(msg, HumanMessage):
            historial_texto += f"Usuario: {msg.content}\n"
        elif isinstance(msg, AIMessage):
            historial_texto += f"Asistente: {msg.content}\n"
    
    if not historial_texto:
        historial_texto = "(No hay historial previo)"
    
    # Generar y mostrar respuesta del asistente
    try:
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            full_response = ""
 
            # Streaming de la respuesta con ChatPromptTemplate
            for chunk in cadena.stream({"mensaje": pregunta, "historial": historial_texto}):
                full_response += chunk.content
                response_placeholder.markdown(full_response + "▌")
            
            response_placeholder.markdown(full_response)
        
        # Almacenar mensajes en el historial
        st.session_state.mensajes.append(HumanMessage(content=pregunta))
        st.session_state.mensajes.append(AIMessage(content=full_response))
        
    except Exception as e:
        st.error(f"Error al generar respuesta: {str(e)}")
        st.info("Verifica que tu API Key de OpenAI esté configurada correctamente.")