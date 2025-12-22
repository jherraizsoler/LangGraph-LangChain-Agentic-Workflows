# 🤖 Proyecto de Inteligencia Artificial (ChatGPT & Gemini)

Este proyecto es una implementación en **Python** para interactuar con modelos de lenguaje de **OpenAI (ChatGPT)** y **Google (Gemini)**.

---

## 📋 Requisitos Previos

Antes de comenzar, asegúrate de tener instalado:

- **Python 3.8 o superior**
- Una clave de API de [OpenAI Platform](https://platform.openai.com/)
- Una clave de API de [Google AI Studio](https://aistudio.google.com/)

---

## ⚙️ Instalación y Configuración

Sigue estos pasos para configurar el proyecto en tu máquina local:

### 1️⃣ Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/tu-nombre-de-repositorio.git
cd tu-nombre-de-repositorio
```

### 2️⃣ Clonar el repositorio

Es importante para mantener las librerías aisladas y no ensuciar tu sistema.

#### Windows
```bash
python -m venv venv
.\venv\Scripts\activate
```

#### 🐧 macOS / Linux
```bash
python3 -m venv venv
source venv/bin/activate
```


### 3️⃣ Instalar dependencias

Con el entorno virtual activado, ejecuta:
```bash
pip install -r requirements.txt
```


### 🔑 Configuración de Seguridad (Variables de Entorno)
Este proyecto utiliza un archivo .env para proteger tus claves privadas.
Nunca subas este archivo a GitHub.

#### 📄 Crear el archivo .env
Crea un archivo llamado .env en la raíz del proyecto y agrega el siguiente contenido:

```bash
# API Key para OpenAI (ChatGPT)
OPENAI_API_KEY=tu_clave_aqui_sin_comillas

# API Key para Google (Gemini)
GEMINI_API_KEY=tu_clave_aqui_sin_comillas
```

⚠️ IMPORTANTE:
El archivo .env ya está incluido en el .gitignore para evitar que se publique por error.


### 🚀 Ejecución del Proyecto

Una vez configurado todo, puedes iniciar la aplicación con:
```bash
python main.py
```

## 🛠️ Tecnologías Utilizadas

- **Python** — Lenguaje base  
- **OpenAI SDK** — Integración con GPT-4 / GPT-3.5  
- **Google Generative AI** — Integración con modelos Gemini  
- **Python-dotenv** — Gestión segura de claves de API  

---

## 📄 Licencia

© 2025 **Jorge Herraiz Soler**  
GitHub: [jherraizsoler](https://github.com/jherraizsoler)

Todos los derechos reservados.

Se permite **descargar**, **utilizar** y **consultar** este proyecto **únicamente para fines personales, educativos o no lucrativos**.

❌ **No está permitido** el uso del proyecto, total o parcial, para:
- Fines **comerciales**
- Fines **lucrativos**
- Redistribución con ánimo de lucro
- Uso en productos o servicios de pago

Cualquier otro uso distinto a los aquí descritos requiere autorización expresa del autor.

