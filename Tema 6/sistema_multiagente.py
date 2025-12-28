from langgraph.prebuilt import create_react_agent
from langgraph_supervisor import create_supervisor
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Definir herramientas personalizadas
@tool
def buscar_web(query: str) -> str:
    """Buscar información en la web."""
    return f"Resultados de búsqueda para: {query}"

@tool
def calcular(expresion: str) -> str:
    """Realizar cálculos matemáticos."""
    return f"Resultado: {eval(expresion)}"

# Crear agentes especializados
agente_investigacion = create_react_agent(
    model=model,
    tools=[buscar_web],
    prompt="Eres un especialista en investigación web.",
    name="investigador"
)

agente_matematicas = create_react_agent(
    model=model,
    tools=[calcular],
    prompt="Eres un especialista en cálculos matemáticos.",
    name="matematico"
)

# Crear supervisor que coordina los agentes
supervisor_graph = create_supervisor(
    [agente_matematicas, agente_investigacion],
    model=model,
    prompt="Eres un supervisor que delega tareas a especialistas según el tipo de consulta."
)

supervisor = supervisor_graph.compile()

# Uso del sistema multi-agente
response = supervisor.invoke({
    "messages": [{
        "role": "user",
        #"content": "Busca información sobre las ultimas tendencias en inteligencia artificial generativa."
        "content": "Busca información sobre pi y calcula su valor multiplicativo por 2."
    }]
})

for msg in response['messages']:
    print(msg.content)