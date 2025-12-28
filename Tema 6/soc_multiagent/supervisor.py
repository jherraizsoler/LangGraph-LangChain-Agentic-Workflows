from langchain_openai import ChatOpenAI
from langgraph_supervisor import create_supervisor
from agents import alert_analyzer, threat_analyzer, notification_agent
from config import config
from datetime import datetime
import json

# Inicializar el modelo para el supervisor
supervisor_model = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=config.OPENAI_API_KEY,
    temperature=0.1
)

def build_soc_workflow():

    # Crear el supervisor multiagente 
    supervisor = create_supervisor(
        agents=[alert_analyzer, threat_analyzer, notification_agent],
        model=supervisor_model,
        prompt="""Eres el supervisor del SOC que coordina EXACTAMENTE 3 pasos secuenciales.

AGENTES DISPONIBLES:
1. **alert_analyzer**: Analiza IOCs y determina VERDADERO/FALSO POSITIVO
2. **threat_analyzer**: Evalúa severidad y propone mitigación (solo para verdaderos positivos)  
3. **notification_agent**: Envía email final con resultados

FLUJO OBLIGATORIO - NO DESVIAR:
1. PASO 1: Delegar a "alert_analyzer" para análisis inicial
2. PASO 2: Si VERDADERO POSITIVO → "threat_analyzer" | Si FALSO POSITIVO → saltar a paso 3
3. PASO 3: Delegar a "notification_agent" para envío final
4. FINALIZAR: Cuando notification_agent complete, TERMINAR inmediatamente

REGLAS CRÍTICAS:
- NO HACER análisis propio - solo coordinar agentes
- NUNCA volver a un agente ya ejecutado
- TERMINAR después del notification_agent
- NO continuar después de enviar email
- Máximo 3 delegaciones por alerta

FORMATO DE DELEGACIÓN:
- "Delegando a alert_analyzer para..."
- "Delegando a threat_analyzer para..." 
- "Delegando a notification_agent para..."
- "PROCESO COMPLETADO"

Si un agente ya fue ejecutado, NO volver a ejecutarlo.""",
        add_handoff_back_messages=True,
        output_mode="full_history"
    )

    return supervisor.compile()

# Instancia global del workflow del supervisor
soc_workflow = build_soc_workflow()

def process_security_alert(alert_data: dict, incident_id: str, processing_context: dict = None) -> dict:
    if processing_context is None:
        processing_context = {}

    # Preparar el mensaje inicial/usuario para el supervisor
    initial_message = f"""ALERTA SOC PARA PROCESAMIENTO SECUENCIAL:

ID: {incident_id}
DATOS: {json.dumps(alert_data, indent=2)}
EMAIL: {processing_context.get('email_recipient', config.SOC_EMAIL_RECIPIENT)}

INSTRUCCIÓN CLARA: Ejecutar EXACTAMENTE estos 3 pasos:
1. alert_analyzer → análisis IOCs (usando VirusTotal y Threat Intel/AbuseIPDB) y determinar VERDADERO/FALSO POSITIVO
2. SI verdadero positivo → threat_analyzer → evaluación severidad y mitigación  
3. notification_agent → envío email final

TERMINAR después del paso 3. NO continuar."""
    
    print(f"🚀 Iniciando arquitectura supervisor para {incident_id}")
    print("🤖 Supervisor coordinará: alert_analyzer → threat_analyzer → notification_agent")
    print("🌐 Usando APIs reales: VirusTotal, Gmail, TavilySearch, AbuseIPDB/ThreatIntel")

    try:
        # Ejecutar el workflow del supervisor
        result = soc_workflow.invoke({
            "messages": [{"role": "user", "content": initial_message}]
        })

        # Extraer los resultados de cada agente del historial de mensajes
        analysis_result = _extract_agent_result(result, "alert_analyzer")
        threat_result = _extract_agent_result(result, "threat_analyzer")
        notification_result = _extract_agent_result(result, "notification_agent")

        # Determinar las herramientas utilizadas para los resultados
        tools_used = ["langgraph-supervisor", "create_supervisor"]

        if analysis_result and any(x in analysis_result.upper() for x in ["VIRUSTOTAL", "VT"]):
            tools_used.append("VirusTotal API")
        if analysis_result and any(x in analysis_result.upper() for x in ["ABUSEIPDB", "INTEL", "IPDB"]):
            tools_used.append("AbuseIPDB / ThreatIntel")
        if analysis_result or threat_result:
            tools_used.append("TavilySearch API")
        if notification_result and any(x in notification_result.upper() for x in ["GMAIL", "EMAIL", "ENVIADO"]):
            tools_used.append("Gmail API")

        final_result = {
            "incident_id": incident_id,
            "status": "completed", 
            "analysis_result": analysis_result or "No analysis found",
            "threat_assessment": threat_result or "No threat assessment performed",
            "notification_sent": notification_result or "No notification sent",
            "timestamp": datetime.now().isoformat(),
            "tools_used": tools_used,
            "supervisor_architecture": True,
            "apis_real": True,
            "processing_context": processing_context,
            "full_conversation": result.get("messages", [])
        }
        
        print(f"✅ Arquitectura supervisor completada para {incident_id}")
        print(f"🛠️ Herramientas utilizadas: {', '.join(tools_used)}")
        
        return final_result
        
    except Exception as e:
        print(f"❌ Error en arquitectura supervisor: {str(e)}")
        
        error_result = {
            "incident_id": incident_id,
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
            "supervisor_architecture": True,
            "apis_real": True
        }
        
        return error_result


def _extract_agent_result(workflow_result: dict, agent_name: str) -> str:
    try:
        messages = workflow_result.get("messages", [])
        
        # Buscar los mensajes de un agente especifico
        agent_messages = []
        for message in messages:
            if hasattr(message, 'content') and agent_name in str(message).lower():
                agent_messages.append(message.content)
            elif isinstance(message, dict):
                content = message.get('content', '')
                if agent_name in str(message).lower() or agent_name in content.lower():
                    agent_messages.append(content)

        # Retornar el ultimo mensaje del agente o concatenar si hay multiples
        if agent_messages:
            return agent_messages[-1] if len(agent_messages) == 1 else "\n\n".join(agent_messages)
        
        return ""
    
    except Exception as e:
        print(f"Error extrayendo el resultado del agente: {agent_name}: {str(e)}")
        return ""