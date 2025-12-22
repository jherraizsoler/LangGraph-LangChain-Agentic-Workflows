from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.7)

pregunta = "¿En que año llegó el ser humano a la luna por primera vez?"

print( "\n\nPregunta: ", pregunta)

respuesta = llm.invoke(pregunta)
print( "\nRespuesta del modelo: ", respuesta.content,"\n")
