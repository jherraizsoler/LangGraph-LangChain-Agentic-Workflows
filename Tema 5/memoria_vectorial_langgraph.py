from langgraph.graph import MessagesState, StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage,AIMessage, SystemMessage
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
import chromadb
import uuid

CHROMADB_PATH = "Tema 5\\chromadb"

# Configuración basica del llm
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Configuración de la base de datos vectorial (chomadb)

vectorstore = Chroma(
    collection_name="memoria_chat",
    embedding_function=OpenAIEmbeddings(model="text-embedding-3-large"),
    persist_directory=CHROMADB_PATH
)

client = chromadb.PersistentClient(path=CHROMADB_PATH)
collection = client.get_collection("memoria_chat")

def guardar_memoria(texto):
    """Guarda información levante del usuario en la base de datos vectorial."""
    try:
        collection.add(
            documents=[texto],
            ids=[str(uuid.uuid4())]
        )
        print(f"[+] Guardado en memoria:  {texto}")
    except Exception as e:
        print(f"[-] Error guardando en memoria {texto}: {e}")
        
def buscar_memoria(consulta, k=3):
    """Buscar información relevante en la memoria de chomadb."""
    
    try:
        results = collection.query(
            query_texts=[consulta],
            n_results=k
        )
        return results['documents'][0] if results['documents'] else []
    except:
        return []


def chatbot_node(state):
    """Nodo principal del grafo."""
    messages = state["messages"]
    ultimo_mensaje = messages[-1].content if messages else  ""
    
    # 1. Buscar memorias relevantes
    memorias =  buscar_memoria(ultimo_mensaje)
    
    # 2. Crear prompt con memorias
    system_content = "Eres un asistente que recuerda información importante."
    
    if memorias:
        system_content += "\n\nInformación que recuerdas:"
        for memoria in memorias:
            system_content += f"\n- {memoria}"
            
    
    # 3. Generar respuesta
    messages_con_sistema = [SystemMessage(content=system_content)] + messages
    response = llm.invoke(messages_con_sistema)
    
    # 4. Guardar información relevante del usuario en la memoria vectorial
    mensaje_lower = ultimo_mensaje.lower()
    
    if "me llamo" in mensaje_lower:
        guardar_memoria(f"El usuario se llama: {ultimo_mensaje}")
    elif any(frase in mensaje_lower for frase in ["trabajo en", "trabajo como", "soy progrmador","soy doctor","soy estudiante"]):
        guardar_memoria(f"Trabajo del usuario: {ultimo_mensaje}")
    elif "me gusta" in mensaje_lower or "me encanta" in mensaje_lower:
        guardar_memoria(f"Le gusta: {ultimo_mensaje}")
    elif "vivo en" in mensaje_lower or "soy de" in mensaje_lower:
        guardar_memoria(f"Ubicación: {ultimo_mensaje}")
    
    return {"messages": [response]}

# Crear el grafo
workflow = StateGraph(state_schema=MessagesState)
workflow.add_node("chatbot", chatbot_node)
workflow.add_edge(START, "chatbot")

# Compilar con memoria volatil de conversación
memory = MemorySaver()
app = workflow.compile(checkpointer=memory)

def chat(message, thread_id="sesion_terminal"):
    config = {"configurable": {"thread_id": thread_id}}
    result = app.invoke({"messages": [HumanMessage(content=message)]}, config)
    return result["messages"][-1].content

def mostrar_memorias():
    """Función auxiliar para ver todas las memorias guardadas del usuario."""
    try:
        all_memories = collection.get()
        if all_memories['documents']:
            print("[+] Memorias guardadas:")
            for i, memoria in enumerate(all_memories['documents'],1):
                print(f"{i}. {memoria}")
        else:
            print("[-] No hay memorias guardadas aun.")
    except Exception as e:
        print(f"Error mostrando memorias: {e}")


if __name__ == "__main__":
                        
    print("Chat en terminal (escribe 'salir' para terminar, 'memorias' para ver memoria historica)\n")

    session_id = "session_terminal"

    # Bucle de conversación
    while True:
        try:
            user_input = input("Tú: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nHasta luego!")
            break

        if not user_input:
            continue
        if user_input.lower() in {"salir", "exit", "quit"}:
            print("Hasta luego!")
            break
        if user_input.lower() == "memorias":
            mostrar_memorias()
            continue
        
        respuesta = chat(user_input, session_id)
        print("Asistente:", respuesta)
        print()