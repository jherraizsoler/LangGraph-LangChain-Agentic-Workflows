from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts  import PromptTemplate
import os
 
# 1. Modelo de datos
class AnalisisTexto(BaseModel):
    resumen: str = Field(description="Resumen breve del texto")
    sentimiento: str = Field(description="Sentimiento: Positivo, Neutro o Negativo")
    palabras_clave: list[str] = Field(description="3-5 palabras clave principales")
 
# 2. Parser
parser = PydanticOutputParser(pydantic_object=AnalisisTexto)
 
# 3. Prompt
prompt = PromptTemplate(
    template="""Analiza este texto cuidadosamente y proporciona un análisis estructurado:
 
{format_instructions}
 
TEXTO:
{texto}
 
ANÁLISIS:""",
    input_variables=["texto"],
    partial_variables={"format_instructions": parser.get_format_instructions()}
)
 
# 4. LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
 
# 5. Cadena
chain = prompt | llm | parser
 
# 6. Ejecución
if __name__ == "__main__":
    texto = "Me encantó la nueva película de acción, tiene efectos especiales increíbles."
    
    try:
        resultado = chain.invoke({"texto": texto})
        print("✅ Análisis exitoso:")
        print(resultado.model_dump_json(indent=2))
    except Exception as e:
        print(f"❌ Error: {e}")