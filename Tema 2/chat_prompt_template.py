from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

chat = ChatOpenAI(model="gpt-4o-mini", temperature=0.6)

chat_prompt = ChatPromptTemplate.from_messages([
    ("system", "Eres un traductor del español al inglés muy preciso."), 
    ("human", "{texto}") 
])

mensajes =  chat_prompt.invoke({"texto":"Hola mundo, ¿cómo estás?"})

respuesta = chat.invoke(mensajes)

print(respuesta.content)