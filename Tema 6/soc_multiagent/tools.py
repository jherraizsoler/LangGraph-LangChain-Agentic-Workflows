import vt
from langchain_tavily import TavilySearch
from langchain_community.agent_toolkits import GmailToolkit
from langchain_community.tools.gmail.utils import get_gmail_credentials, build_resource_service
from langchain.tools import tool
from config import config
from datetime import datetime
import requests
import ipaddress
from urllib.parse import urlparse

# Validar configuracion al importar
config.validate_required_config()

# 1. TavilySearch - Herramienta pre-construida
search_tool = TavilySearch(
    max_results=3,
    api_key=config.TAVILY_API_KEY
)

# 2. GmailTools - Herramienta pre-construida
creds = get_gmail_credentials(
    token_file=config.GMAIL_TOKEN_FILE,
    client_secrets_file=config.GMAIL_CREDENTIALS_FILE,
    scopes=["https://mail.google.com/"]
)

gmail_toolkit = GmailToolkit(api_resource=build_resource_service(credentials=creds))
gmail_tools = gmail_toolkit.get_tools()

# 3. Virustotal Tool
@tool
def virustotal_checker(indicator: str, indicator_type: str) -> str:
    """Analiza URLs, IPs y hashes usando la API de VirusTotal.

    Args:
        indicator: URL, IP o hash a analizar.
        indicator_type: 'url', 'ip' o 'hash'

    Returns:
        Resultado del analisis de VirusTotal
    """
    try:
        with vt.Client(config.VIRUSTOTAL_API_KEY) as client:
            if indicator_type == "url":
                url_id = vt.url_id(indicator)
                analysis = client.get_object(f"/urls/{url_id}")
            elif indicator_type == "ip":
                analysis = client.get_object(f"/ip-addresses/{indicator}")
            elif indicator_type == "hash":
                analysis = client.get_object(f"/files/{indicator}")
            else:
                return f"Tipo no soportado: {indicator_type}"
            
            stats = analysis.last_analysis_stats
            malicious = stats.get("malicious", 0)
            suspicious = stats.get("suspicious", 0)
            total = sum(stats.values())

            if malicious > 5:
                threat_level = "MALICIOSO"
            elif malicious > 0 or suspicious > 3:
                threat_level = "SOSPECHOSO"
            else:
                threat_level = "LIMPIO"

            return f"""ANALISIS VIRUSTOTAL:
Indicador: {indicator}
Detecciones: {malicious}/{total} maliciosas, {suspicious}/{total} sospechosas
Clasificacion: {threat_level}
Análisis: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
    
    except Exception as e:
        return f"Error VirusTotal: {str(e)}"


# 4. Threat Intelligence
@tool
def threat_intel_lookup(indicator: str, intel_type: str = "auto") -> str:
    """Busca threat intelligence usando APIs públicas.
    
    Args:
        indicator: IOC a investigar
        intel_type: Tipo ('ip', 'url', 'hash' o 'auto')
        
    Returns:
        Información de threat intelligence
    """
    try:
        if intel_type == "auto":
            intel_type = _detect_indicator_type(indicator)
        
        results = []
        
        # AbuseIPDB para IPs
        if intel_type == "ip" and config.ABUSEIPDB_API_KEY:
            abuse_result = _check_abuseipdb(indicator)
            results.append(f"🛡️ AbuseIPDB: {abuse_result}")
        
        # Análisis básico de URLs/dominios
        if intel_type in ["url", "domain"]:
            url_result = _analyze_url_reputation(indicator)
            results.append(f"🌐 URL Analysis: {url_result}")
        
        # OSINT básico
        osint_result = _basic_osint(indicator)
        results.append(f"🔍 OSINT: {osint_result}")
        
        return f"""🔍 THREAT INTELLIGENCE:
🎯 Indicador: {indicator} ({intel_type.upper()})
📅 Análisis: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
 
{chr(10).join(results)}"""
        
    except Exception as e:
        return f"❌ Error threat intel: {str(e)}"
 
def _detect_indicator_type(indicator: str) -> str:
    """Detecta automáticamente el tipo de indicador"""
    try:
        ipaddress.ip_address(indicator)
        return "ip"
    except ValueError:
        pass
    
    if indicator.startswith(('http://', 'https://')):
        return "url"
    elif '.' in indicator:
        return "domain"
    elif len(indicator) in [32, 40, 64]:
        return "hash"
    return "unknown"
 
def _check_abuseipdb(ip: str) -> str:
    """Consulta AbuseIPDB API"""
    try:
        headers = {'Key': config.ABUSEIPDB_API_KEY, 'Accept': 'application/json'}
        params = {'ipAddress': ip, 'maxAgeInDays': 90}
        
        response = requests.get(
            'https://api.abuseipdb.com/api/v2/check', 
            headers=headers, params=params, timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()['data']
            confidence = data.get('abuseConfidencePercentage', 0)
            country = data.get('countryCode', 'Unknown')
            
            level = "🔴 MALICIOSO" if confidence > 50 else "🟡 SOSPECHOSO" if confidence > 25 else "🟢 LIMPIO"
            return f"{level} - Confianza: {confidence}% - País: {country}"
        else:
            return f"Error {response.status_code}"
            
    except Exception as e:
        return f"Error: {str(e)}"
 
def _analyze_url_reputation(url: str) -> str:
    """Análisis básico de reputación URL"""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc or parsed.path
        
        suspicious_patterns = ['temp', 'test', 'suspicious', 'evil', 'malicious']
        
        if any(pattern in domain.lower() for pattern in suspicious_patterns):
            return "🟡 PATRONES SOSPECHOSOS detectados"
        elif len(domain) < 5 or domain.count('-') > 3:
            return "🟡 DOMINIO SOSPECHOSO por estructura"
        else:
            return "🟢 DOMINIO SIN ALERTAS evidentes"
            
    except Exception as e:
        return f"Error: {str(e)}"
 
def _basic_osint(indicator: str) -> str:
    """OSINT básico"""
    suspicious_patterns = ['temp', 'test', 'malicious', 'suspicious', 'evil', 'bad']
    
    if any(pattern in indicator.lower() for pattern in suspicious_patterns):
        return "🟡 PATRONES SOSPECHOSOS en el indicador"
    else:
        return "🟢 Sin patrones sospechosos evidentes"


# Lista de herramientas para importacion
all_tools = [search_tool, virustotal_checker, threat_intel_lookup] + gmail_tools