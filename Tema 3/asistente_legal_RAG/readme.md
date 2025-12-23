# ⚖️ Asistente Legal RAG - LangChain & Streamlit

Este proyecto es un **Asistente Legal inteligente** que utiliza técnicas de Generación Aumentada por Recuperación (RAG). Permite realizar consultas sobre contratos de arrendamiento de locales comerciales utilizando búsquedas semánticas avanzadas y el modelo de recuperación **MultiQueryRetriever**.


---

## 🚀 Guía de Instalación y Configuración

Sigue estos pasos para poner en marcha el proyecto en tu máquina local.

### 1. Clonar el repositorio
Primero, descarga el proyecto desde GitHub:
```Bash
git clone [https://github.com/tu-usuario/asistente_legal.git](https://github.com/tu-usuario/asistente_legal.git)
cd asistente_legal
```

### 2. Configurar el Entorno Virtual
Es fundamental usar un entorno virtual para evitar conflictos de librerías.
```Bash
# Crear el entorno virtual
python -m venv venv

# Activar el entorno (Windows)
.\venv\Scripts\activate
```


### 3. Instalar Dependencias
Instala los paquetes necesarios de LangChain, OpenAI y Streamlit:
```Bash
pip install langchain langchain-openai langchain-community chromadb streamlit python-dotenv
```

## ⚙️ Configuración de Variables y Rutas
Antes de ejecutar la aplicación, debes configurar tus credenciales y las rutas del sistema.

### 1. Variables de Entorno (API Key)
Crea un archivo llamado .env en la carpeta raíz o asegúrate de que tu archivo config.py apunte correctamente a tu clave de OpenAI:

```Python
# En config.py o archivo .env
OPENAI_API_KEY = "tu_api_key_aqui"
```


### 2. Ajuste de Rutas en config.py
Para que el sistema encuentre siempre la base de datos de vectores, el proyecto utiliza rutas dinámicas. Asegúrate de que CHROMA_DB_PATH coincida con la ubicación de tu carpeta indexada:

```Python
# Ejemplo de configuración en config.py
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHROMA_DB_PATH = os.path.join(BASE_DIR, "chroma_db")
EMBEDING_MODEL = "text-embedding-3-large" # Debe ser el mismo que usaste al indexar
```

## 🖥️ Ejecución de la Aplicación
Para iniciar el asistente, posiciona tu terminal en la carpeta raíz del curso y ejecuta el comando de Streamlit apuntando a la ruta de la aplicación.

Comando de ejecución:
```PowerShell
# Ruta absoluta donde tengas el proyecto ejecutar el siguiente comando
(venv) PS C:\Users\nombreUsuario\curso_langchain> streamlit run ".\Tema 3\asistente_legal_RAG\app.py"
```

## 🛠️ Tecnologías Utilizadas

* **LangChain:** Framework para la orquestación de la IA y manejo de flujos de trabajo.
* **OpenAI (GPT-4o / text-embedding-3-large):** Modelos de última generación para la generación de respuestas y creación de embeddings de alta dimensionalidad.
* **ChromaDB:** Base de datos vectorial persistente utilizada para el almacenamiento y búsqueda eficiente de los fragmentos de contratos.
* **Streamlit:** Framework de Python para crear la interfaz de usuario web interactiva y amigable.
* **MultiQueryRetriever:** Técnica avanzada de recuperación que genera múltiples variaciones de una pregunta para maximizar la precisión de búsqueda.



---

## 📁 Estructura del Proyecto

* **`app.py`**: Punto de entrada de la aplicación. Gestiona la interfaz de usuario con Streamlit.
* **`rag_system.py`**: Contiene la lógica central del sistema RAG, incluyendo la configuración de las cadenas (Chains) y los retrievers.
* **`config.py`**: Archivo centralizado para parámetros del modelo, rutas de archivos y constantes de configuración.
* **`prompts.py`**: Almacena las plantillas de instrucciones (Prompt Templates) utilizadas para guiar el comportamiento de la IA.
* **`chroma_db/`**: Directorio persistente donde se almacenan los vectores y metadatos del conocimiento legal indexado.

---

## ✨ Notas de Uso

> [!IMPORTANT]
> Si la IA responde que no encuentra información relevante, realiza las siguientes comprobaciones:

1. **Consistencia de Embeddings:** Verifica que el modelo definido en `EMBEDING_MODEL` dentro de `config.py` sea exactamente el mismo que se utilizó durante la fase de ingesta de documentos.
2. **Persistencia de Datos:** Comprueba que la carpeta `chroma_db` no esté vacía y contenga los archivos de persistencia (como `chroma.sqlite3` o archivos de índice `.bin`).
3. **Rutas de Acceso:** Asegúrate de que la ruta definida en `CHROMA_DB_PATH` sea accesible desde el directorio donde estás ejecutando Streamlit.