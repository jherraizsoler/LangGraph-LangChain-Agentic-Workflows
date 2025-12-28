from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import uvicorn
import uuid
from datetime import datetime
from supervisor import process_security_alert
from config import config

# Validar configuración al iniciar
try:  
    config.validate_required_config()
    print("✅ Configuración de APIs validada correctamente")
except ValueError as e:
    print(f"❌ Error de configuración: {e}")
    print("💡 Revisa tu archivo .env y asegúrate de tener todas las API keys requeridas")

app = FastAPI(title="SOC Webhook Server - PRODUCCIÓN", version="1.0.0")

class SecurityAlert(BaseModel):
    source: str
    alert_type: str
    severity: str
    message: str
    source_ip: Optional[str] = None
    destination_ip: Optional[str] = None
    url: Optional[str] = None
    file_hash: Optional[str] = None
    timestamp: Optional[str] = None
    email_recipient: Optional[str] = None  # Email específico para notificación
    real_apis: Optional[bool] = True  # Flag para indicar uso de APIs reales

# Storage simple para el demo
incidents_db = []

@app.post("/webhook/alert")
async def receive_alert(alert: SecurityAlert):
    """Recibe alertas de seguridad y las procesa con agentes REALES usando APIs externas"""
    try:
        # Generar ID de incidente único
        incident_id = f"INC-{datetime.now().strftime('%Y%m%d%H%M%S')}-{str(uuid.uuid4())[:6]}"
        
        # Convertir a dict y agregar metadatos
        alert_data = alert.model_dump()
        alert_data["timestamp"] = alert_data.get("timestamp") or datetime.now().isoformat()
        alert_data["incident_id"] = incident_id
        
        print(f"🚨 Procesando alerta REAL: {incident_id}")
        print(f"📊 Datos: {alert_data}")
        print(f"🌐 APIs reales: {alert_data.get('real_apis', True)}")
        
        # Agregar información de destinatario de email si se especifica
        processing_context = {
            "email_recipient": alert_data.get("email_recipient"),
            "use_real_apis": alert_data.get("real_apis", True)
        }
        
        print("🤖 Iniciando procesamiento con agentes multiagente...")
        print("⏱️  Tiempo estimado: 45-90 segundos (APIs reales)")
        
        # Procesar con agentes - esto usará APIs REALES
        result = process_security_alert(alert_data, incident_id, processing_context)
        
        # Guardar en "base de datos"
        incidents_db.append(result)
        
        print(f"✅ Alerta procesada exitosamente: {incident_id}")
        print(f"📊 Herramientas utilizadas: {result.get('tools_used', [])}")
        
        return {
            "status": "success",
            "incident_id": incident_id,
            "message": "Alerta procesada por agentes SOC con APIs reales",
            "processing_time": "45-90 segundos",
            "apis_used": result.get('tools_used', []),
            "result": result
        }
        
    except Exception as e:
        print(f"❌ Error procesando alerta: {str(e)}")
        
        # Log detallado del error para debugging
        import traceback
        print("🔍 Traceback completo:")
        print(traceback.format_exc())
        
        # Determinar tipo de error para mejor respuesta
        error_message = str(e)
        if "API" in error_message:
            error_type = "api_error"
            suggestion = "Verifica que todas las API keys estén configuradas correctamente"
        elif "timeout" in error_message.lower():
            error_type = "timeout_error"  
            suggestion = "Las APIs externas están tardando más de lo esperado. Intenta de nuevo."
        elif "gmail" in error_message.lower():
            error_type = "gmail_error"
            suggestion = "Gmail no está configurado. Consulta el README para setup de Google Console."
        else:
            error_type = "unknown_error"
            suggestion = "Error inesperado en el procesamiento"
        
        raise HTTPException(
            status_code=500, 
            detail={
                "error": error_message,
                "error_type": error_type,
                "suggestion": suggestion,
                "timestamp": datetime.now().isoformat()
            }
        )

@app.get("/incidents")
async def get_incidents():
    """Obtiene lista de incidentes procesados con información de APIs reales"""
    return {
        "incidents": incidents_db,
        "total_incidents": len(incidents_db),
        "real_apis_used": True,
        "last_updated": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check del sistema con estado de APIs"""
    
    # Verificar estado básico de configuración
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "total_incidents_processed": len(incidents_db),
        "api_configuration": {
            "openai": "✅ Configurada" if config.OPENAI_API_KEY else "❌ Falta",
            "tavily": "✅ Configurada" if config.TAVILY_API_KEY else "❌ Falta", 
            "virustotal": "✅ Configurada" if config.VIRUSTOTAL_API_KEY else "❌ Falta",
            "abuseipdb": "✅ Configurada" if config.ABUSEIPDB_API_KEY else "❌ Falta",
            "gmail_credentials": "✅ Configurada" if config.GMAIL_CREDENTIALS_FILE else "❌ Falta"
        }
    }
    
    # Determinar estado general
    missing_apis = [k for k, v in health_status["api_configuration"].items() if "❌" in v]
    
    if missing_apis:
        health_status["status"] = "degraded"
        health_status["warnings"] = f"APIs faltantes: {', '.join(missing_apis)}"
    
    return health_status

@app.get("/api-status")
async def api_status():
    """Estado detallado de todas las APIs externas"""
    
    status = {
        "timestamp": datetime.now().isoformat(),
        "apis": {
            "openai": {
                "configured": bool(config.OPENAI_API_KEY),
                "description": "LLM para agentes multiagente",
                "required": True
            },
            "tavily": {
                "configured": bool(config.TAVILY_API_KEY),
                "description": "Búsqueda web para AI agents",
                "required": True,
                "free_tier": "1000 búsquedas/mes"
            },
            "virustotal": {
                "configured": bool(config.VIRUSTOTAL_API_KEY), 
                "description": "Análisis de IOCs real",
                "required": True,
                "rate_limits": "4 requests/min (gratis)"
            },
            "gmail": {
                "configured": bool(config.GMAIL_CREDENTIALS_FILE),
                "description": "Envío real de notificaciones",
                "required": False,
                "setup_required": "Google Cloud Console + OAuth2"
            },
            "abuseipdb": {
                "configured": bool(config.ABUSEIPDB_API_KEY),
                "description": "Threat intelligence de IPs",
                "required": False,
                "free_tier": "1000 requests/día"
            }
        }
    }
    
    return status

if __name__ == "__main__":
    print("🛡️ Iniciando servidor webhook SOC con APIs REALES...")
    print(f"🌐 Puerto: {config.WEBHOOK_PORT}")
    print("🔧 Verificando configuración...")
    
    # Mostrar estado de APIs al iniciar
    print(f"✅ OpenAI: {'Configurada' if config.OPENAI_API_KEY else 'FALTA'}")
    print(f"✅ Tavily: {'Configurada' if config.TAVILY_API_KEY else 'FALTA'}")
    print(f"✅ VirusTotal: {'Configurada' if config.VIRUSTOTAL_API_KEY else 'FALTA'}")
    print(f"✅ AbuseIPDB (Threat Intel): {'Configurada' if config.ABUSEIPDB_API_KEY else 'FALTA'}")
    print(f"✅ Gmail: {'Configurada' if config.GMAIL_CREDENTIALS_FILE else 'FALTA (opcional)'}")
    
    print("\n🚀 Servidor listo para procesar alertas reales!")
    print("📊 Dashboard: http://localhost:8501")
    print("🌐 API Health: http://localhost:8000/health")
    
    uvicorn.run(app, host="0.0.0.0", port=config.WEBHOOK_PORT)