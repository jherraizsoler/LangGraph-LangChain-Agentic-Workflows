"""
Utilidades auxiliares para la aplicación
"""
from datetime import datetime
from typing import List, Dict, Any
import re

def format_timestamp(timestamp_str: str) -> str:
    """Formatea un timestamp para mostrar en la interfaz"""
    try:
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        return dt.strftime("%d/%m/%Y %H:%M")
    except:
        return timestamp_str

def truncate_text(text: str, max_length: int = 100) -> str:
    """Trunca texto para mostrar en la interfaz"""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."

def validate_user_id(user_id: str) -> bool:
    """Valida que el ID de usuario sea válido"""
    # Solo letras, números, guiones y guiones bajos, mínimo 2 caracteres
    pattern = r'^[a-zA-Z0-9_-]{2,30}$'
    return bool(re.match(pattern, user_id))

def get_memory_category_icon(category: str) -> str:
    """Devuelve un icono para cada categoría de memoria"""
    icons = {
        'personal': '👤',
        'profesional': '💼',
        'preferencias': '❤️',
        'tareas': '📝',
        'hechos_importantes': '⭐'
    }
    return icons.get(category, '📌')