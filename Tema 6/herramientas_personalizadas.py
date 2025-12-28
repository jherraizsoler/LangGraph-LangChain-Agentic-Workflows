from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from operator import attrgetter
from typing import Tuple

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)

# Opción 1.1: Con @tool se pueden crear herramientas personalizadas
@tool("user_db_tool", return_direct=True)
def herramienta_personalizada(query: str) -> str:
    """Consulta la base de datos de usuarios de la empresa y devuelve el resultado de la consulta."""
    # Código que accede a la base de datos
    return f"Respuesta a la consulta: {query}"
    
llm_with_tools = llm.bind_tools([herramienta_personalizada])
    
chain = llm_with_tools | attrgetter("tool_calls") | herramienta_personalizada.map()

#response = chain.invoke("Genera un resumen de la información que hay en la base de datos para el usuario UX341234")
#print(response[0].content)

response = llm_with_tools.invoke("Cual es la capital de España?")
#print(response.content)

# Opción 1.2: Con @tool se pueden crear herramientas personalizadas
@tool("user_db_tool", response_format="content_and_artifact")
def herramienta_personalizada(query: str) -> Tuple[str, int]:
    """Consulta la base de datos de usuarios de la empresa y devuelve el resultado de la consulta."""
    # Código que accede a la base de datos
    return f"Respuesta a la consulta: {query}", 10
    
llm_with_tools = llm.bind_tools([herramienta_personalizada])
    
chain = llm_with_tools | attrgetter("tool_calls") | herramienta_personalizada.map()

#response = chain.invoke("Genera un resumen de la información que hay en la base de datos para el usuario UX341234")
#print(response[0].content)

response = chain.invoke("Genera un resumen de la información sobre el usuario UX341234 que se encuentra en nuestra base de datos.")

print(response[0].content)
#print(response)




# Opción 2: Con StructuredTool se pueden crear herramientas personalizadas
"""
from langchain_core.tools import StructuredTool

def herramienta_personalizada2(query: str) -> str:
    # Consulta la base de datos de usuarios de la empresa.
    # Código que accede a la base de datos
    return f"Respuesta a la consulta: {query}"

mi_tool = StructuredTool.from_function(herramienta_personalizada2)

print(mi_tool.run("Consulta personalizada"))

"""

    
