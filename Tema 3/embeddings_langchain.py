from langchain_openai import OpenAIEmbeddings
import numpy as np

embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

texto1 = "La capital de Francia es París."
texto2 = "París es la ciudad capital de Francia."

vec1 = embeddings.embed_query(texto1)
vec2 = embeddings.embed_query(texto2)

print(f"Dimensión de los vectores: {len(vec1)} y {len(vec2)}")

cos_sim = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
print(f"Similitud coseno entre los textos vec1 y vec2: {cos_sim:.3f}")

texto3 = "Me gusta mucho comer pizza los viernes por la noche."
vec3 = embeddings.embed_query(texto3)

# Compara texto1 con texto3
cos_sim_opuesto = np.dot(vec1, vec3) / (np.linalg.norm(vec1) * np.linalg.norm(vec3))
print(f"Similitud con algo irrelevante: {cos_sim_opuesto:.3f}")