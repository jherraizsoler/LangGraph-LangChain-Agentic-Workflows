from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

pregunta = "¿En que año llegó el ser humano a la luna por primera vez?"

print( "\n\nPregunta: ", pregunta)

respuesta = llm.invoke(pregunta)
print( "\nRespuesta del modelo: ", respuesta.content,"\n")