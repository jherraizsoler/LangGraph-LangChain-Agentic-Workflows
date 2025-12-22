#------------------------- CONSULTA CON PLANTILLAS DE PROMPTS -------------------
from langchain_openai import ChatOpenAI

# SE IMPORTA LA CLASE PARA DIFINIR PLANTILLAS
from langchain_core.prompts import PromptTemplate
#from langchain.chains import LLMChain

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

# SE DEFINE LA PLANTILLA  con la clase PromptTemplate  en donde:
# input_variables = Se ponen en una lista las variables que van a ser utilizadas
# template = Se pone el prompt con las variables a sustituir en {}
plantilla = PromptTemplate(
    input_variables=["nombre"],
    template="Saluda al usuario con su nombre. \nNombre del usuario: {nombre}\nAsistente:"
)

# IMPLEMENTACION DE CADENAS CON |
chain = plantilla | llm
resultado = chain.invoke({"nombre": "Jorge"})
print(resultado.content)


