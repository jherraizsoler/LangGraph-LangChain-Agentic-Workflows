from typing import Annotated, TypedDict, List, Union
from langchain_core.messages import BaseMessage
from operator import add

class AgentState(TypedDict):
    # Los mensajes se van acumulando (Annotated con add)
    messages: Annotated[List[BaseMessage], add]
    
    # Datos estructurados del paciente que el agente debe manejar
    patient_data: dict 
    
    # El recurso médico que se está evaluando (ej. "Quirófano 5")
    resource_focus: str
    
    # Banderas de seguridad para el Agente de Ética
    safety_check_passed: bool