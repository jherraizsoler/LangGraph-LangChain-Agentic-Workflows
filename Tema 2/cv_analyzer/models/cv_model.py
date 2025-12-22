from pydantic import BaseModel, Field

class AnalisisCV(BaseModel):
    """Modelo de datos para el análisis completo de un CV."""
    
    nombre_candidato: str = Field(description="Nombre completo del candidato extraído del CV.")
    experiencia_meses: int = Field(description="Años o meses totales de experiencia laboral relevante.")
    habilidades_clave: list[str] = Field(description="Lista de las 5-7 habilidades del candidato más relevantes para el puesto.")
    education: str = Field(description="Nivel educativo más alto y especialización principal.")
    experiencia_relevante: str = Field(description="Resumen conciso de la experiencia laboral más relevante para el puesto.")
    fortalezas: list[str] = Field(description="Lista de 3-5 fortalezas principales del candidato basadas en su perfil.")
    areas_mejora: list[str] = Field(description="Lista de 2-4 áreas donde el candidato podría desarrollarse o mejorar.")
    porcentaje_ajuste: int = Field(description="Porcentaje de ajuste al puesto (0-100) basado en la experiencia, habilidades y formación", ge=0, le=100)
    
    
    
    
    