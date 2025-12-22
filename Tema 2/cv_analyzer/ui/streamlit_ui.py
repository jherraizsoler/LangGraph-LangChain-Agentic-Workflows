import os
import json
from datetime import datetime
import streamlit as st
from models.cv_model import AnalisisCV
from services.pdf_processor import extraer_texto_pdf
from services.cv_evaluator import evaluar_candidato
# ReportLab para generar PDF
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

from datetime import datetime

hoy = datetime.today()

fecha_formato_cadena = hoy.strftime('%Y-%m-%d')

# --------------------------
# Configuración de guardado
# --------------------------
DIRECTORIO_GUARDADO = r".\resultados_cv"

def guardar_resultado(resultado: AnalisisCV):

    """Guarda el análisis en formato JSON y PDF. Devuelve rutas (ruta_json, ruta_pdf)."""
    
    # Intentar crear directorio (capturar errores de permisos)
    
    try:
        os.makedirs(DIRECTORIO_GUARDADO, exist_ok=True)
    except Exception as e:
        raise RuntimeError(f"Error creando directorio '{DIRECTORIO_GUARDADO}': {e}")

    fecha_actual = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    safe_name = (resultado.nombre_candidato or "candidate").strip().replace(" ", "_")
    nombre_archivo = f"{safe_name}_{fecha_actual}"

    # --- Guardar JSON ---
    ruta_json = os.path.join(DIRECTORIO_GUARDADO, f"{nombre_archivo}.json")
    try:
        payload = {
            "nombre": resultado.nombre_candidato,
            "porcentaje_ajuste": resultado.porcentaje_ajuste,
            "experiencia_meses": resultado.experiencia_meses,
            "educacion": resultado.education,
            "habilidades": list(resultado.habilidades_clave) if resultado.habilidades_clave else [],
            "fortalezas": list(resultado.fortalezas) if resultado.fortalezas else [],
            "areas_mejora": list(resultado.areas_mejora) if resultado.areas_mejora else [],
            "experiencia_relevante": resultado.experiencia_relevante,
            "recomendacion": "Recomendado" if resultado.porcentaje_ajuste >= 70 else "No recomendado",
            "timestamp": fecha_actual,
        }
        with open(ruta_json, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=4)
    except Exception as e:
        raise RuntimeError(f"Error al guardar JSON en '{ruta_json}': {e}")

    # --- Guardar PDF ---
    ruta_pdf = os.path.join(DIRECTORIO_GUARDADO, f"{nombre_archivo}.pdf")
    try:
        doc = SimpleDocTemplate(ruta_pdf, pagesize=letter)
        styles = getSampleStyleSheet()
        contenido = []
        contenido.append(Paragraph("<b>📄 Informe de Evaluación de Candidato</b>", styles["Title"]))
        contenido.append(Spacer(1, 8))
        contenido.append(Paragraph(f"<b>Nombre:</b> {resultado.nombre_candidato}", styles["Normal"]))
        contenido.append(Paragraph(f"<b>Porcentaje de Ajuste:</b> {resultado.porcentaje_ajuste}%", styles["Normal"]))
       
        experiencia = resultado.experiencia_meses
        variableTiempo = ""
        if(experiencia < 12):
            variableTiempo = f"{experiencia} meses"
        else:
            variableTiempo = f"{experiencia // 12} años"
        
        contenido.append(Paragraph(f"<b>Experiencia:</b> {variableTiempo}", styles["Normal"]))
        contenido.append(Paragraph(f"<b>Educación:</b> {resultado.education}", styles["Normal"]))
        contenido.append(Spacer(1, 8))

        contenido.append(Paragraph("<b>🛠️ Habilidades Clave</b>", styles["Heading2"]))
        habilidades_text = ", ".join(resultado.habilidades_clave) if resultado.habilidades_clave else "N/A"
        contenido.append(Paragraph(habilidades_text, styles["Normal"]))
        contenido.append(Spacer(1, 8))
        contenido.append(Paragraph("<b>💪 Fortalezas</b>", styles["Heading2"]))
        fortalezas_text = "<br/>".join(resultado.fortalezas) if resultado.fortalezas else "N/A"
        contenido.append(Paragraph(fortalezas_text, styles["Normal"]))
        contenido.append(Spacer(1, 8))
        contenido.append(Paragraph("<b>📈 Áreas de Mejora</b>", styles["Heading2"]))
        areas_text = "<br/>".join(resultado.areas_mejora) if resultado.areas_mejora else "N/A"
        contenido.append(Paragraph(areas_text, styles["Normal"]))
        contenido.append(Spacer(1, 8))
        contenido.append(Paragraph("<b>💼 Experiencia Relevante</b>", styles["Heading2"]))
        contenido.append(Paragraph(resultado.experiencia_relevante or "N/A", styles["Normal"]))
        contenido.append(Spacer(1, 8))
        contenido.append(Paragraph("<b>📋 Recomendación Final</b>", styles["Heading2"]))
        recomendacion = "✅ CANDIDATO RECOMENDADO" if resultado.porcentaje_ajuste >= 70 else "❌ CANDIDATO NO RECOMENDADO"
        contenido.append(Paragraph(recomendacion, styles["Normal"]))
        doc.build(contenido)

    except Exception as e:
        raise RuntimeError(f"Error al generar PDF en '{ruta_pdf}': {e}")

    return ruta_json, ruta_pdf



# --------------------------
# Interfaz Streamlit
# --------------------------

def main():

    """Función principal que define la interfaz de usuario de Streamlit"""
    st.set_page_config(

        page_title="Sistema de Evaluación de CVs",
        page_icon="📄",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.title("📄 Sistema de Evaluación de CVs con IA")
    st.markdown("""
    **Analiza currículums y evalúa candidatos de manera objetiva usando IA**

    Este sistema utiliza inteligencia artificial para:

    - Extraer información clave de currículums en PDF

    - Analizar la experiencia y habilidades del candidato

    - Evaluar el ajuste al puesto específico

    - Proporcionar recomendaciones objetivas de contratación

    """)

    st.divider()

    # Asegurar claves en session_state (persistencia entre reruns)

    if "archivo_cv" not in st.session_state:

        st.session_state["archivo_cv"] = None

    if "descripcion_puesto" not in st.session_state:

        st.session_state["descripcion_puesto"] = ""

    if "analizar" not in st.session_state:

        st.session_state["analizar"] = False

    if "resultado_analisis" not in st.session_state:

        st.session_state["resultado_analisis"] = None

    col_entrada, col_resultado = st.columns([1, 1], gap="large")

    with col_entrada:
        procesar_entrada()
   
    with col_resultado:
        mostrar_area_resultados()


def procesar_entrada():

    """Maneja la entrada de datos del usuario"""

    st.header("📋 Datos de Entrada")

    archivo_cv = st.file_uploader(

        "**1. Sube el CV del candidato (PDF)**",
        type=['pdf'],
        help="Selecciona un archivo PDF que contenga el currículum a evaluar. Asegúrate de que el texto sea legible y no esté en formato de imagen."
    )

    # Si suben un archivo, persistirlo en session_state

    if archivo_cv is not None:

        st.session_state["archivo_cv"] = archivo_cv
        st.success(f"✅ Archivo cargado: {archivo_cv.name}")
        st.info(f"📊 Tamaño: {archivo_cv.size:,} bytes")
    else:
        if st.session_state["archivo_cv"] is not None:
            st.info(f"📄 Archivo en sesión: {st.session_state['archivo_cv'].name}")
    st.markdown("---")
   
    st.markdown("**2. Descripción del puesto de trabajo**")
    descripcion_puesto = st.text_area(

        "Detalla los requisitos, responsabilidades y habilidades necesarias:",
        height=250,
        placeholder="""Ejemplo detallado:

**Puesto:** Desarrollador Frontend Senior

**Requisitos obligatorios:**

- 3+ años de experiencia en desarrollo frontend

- Dominio de React.js y JavaScript/TypeScript

- Experiencia con HTML5, CSS3 y frameworks CSS (Bootstrap, Tailwind)

- Conocimiento de herramientas de build (Webpack, Vite)



**Requisitos deseables:**

- Experiencia con Next.js o similares

- Conocimientos de testing (Jest, Cypress)

- Familiaridad con metodologías ágiles

- Inglés intermedio-avanzado



**Responsabilidades:**

- Desarrollo de interfaces de usuario responsivas

- Colaboración con equipos de diseño y backend

- Optimización de rendimiento de aplicaciones web

- Mantenimiento de código legacy""",

        help="Sé específico sobre requisitos técnicos, experiencia requerida y responsabilidades del puesto."

    )

   

    # Persistir la descripción si el usuario la escribió

    if descripcion_puesto:

        st.session_state["descripcion_puesto"] = descripcion_puesto

    else:

        if st.session_state["descripcion_puesto"]:

            st.info("Descripción en sesión cargada.")

   

    st.markdown("---")

   

    col_btn1, col_btn2 = st.columns([1, 1])

   

    with col_btn1:

        # Sólo al pulsar el botón se marca 'analizar' en el session_state

        if st.button("🔍 Analizar Candidato", type="primary", use_container_width=True):

            st.session_state["analizar"] = True



    with col_btn2:

        if st.button("🗑️ Limpiar", use_container_width=True):

            # Limpiar solo las claves relacionadas

            for k in ["archivo_cv", "descripcion_puesto", "analizar", "resultado_analisis"]:

                if k in st.session_state:

                    del st.session_state[k]

            # Forzar rerun para reflejar la limpieza

            if hasattr(st, "rerun"):

                st.rerun()

            elif hasattr(st, "experimental_rerun"):

                st.experimental_rerun()

            else:

                st.stop()

   

def mostrar_area_resultados():

    """Muestra el área de resultados del análisis"""

   

    st.header("📊 Resultado del Análisis")

   

    if st.session_state.get('analizar', False):

        archivo_cv = st.session_state.get('archivo_cv')

        descripcion_puesto = st.session_state.get('descripcion_puesto', '').strip()

       

        if archivo_cv is None:

            st.error("⚠️ Por favor sube un archivo PDF con el currículum")

            return

           

        if not descripcion_puesto:

            st.error("⚠️ Por favor proporciona una descripción detallada del puesto")

            return

       

        # Procesar análisis y persistir resultado en session_state

        procesar_analisis(archivo_cv, descripcion_puesto)

    else:

        st.info("""

        👆 **Instrucciones:**

       

        1. Sube un CV en formato PDF en la columna izquierda

        2. Describe detalladamente el puesto de trabajo

        3. Haz clic en "Analizar Candidato"

        4. Aquí aparecerá el análisis completo del candidato

       

        **Consejos para mejores resultados:**

        - Usa CVs con texto seleccionable (no imágenes escaneadas)

        - Sé específico en la descripción del puesto

        - Incluye tanto requisitos obligatorios como deseables

        """)



def procesar_analisis(archivo_cv, descripcion_puesto):

    """Procesa el análisis completo del CV"""

   

    with st.spinner("🔄 Procesando currículum..."):

        progress_bar = st.progress(0)

        status_text = st.empty()

       

        status_text.text("📄 Extrayendo texto del PDF...")

        progress_bar.progress(25)

       

        texto_cv = extraer_texto_pdf(archivo_cv)

       

        if texto_cv.startswith("Error"):

            st.error(f"❌ {texto_cv}")

            return

       

        status_text.text("🤖 Preparando análisis con IA...")

        progress_bar.progress(50)

       

        status_text.text("📊 Analizando candidato...")

        progress_bar.progress(75)

       

        # Aquí llamas a tu módulo core que devuelve AnalisisCV

        resultado = evaluar_candidato(texto_cv, descripcion_puesto,fecha_formato_cadena)

       

        status_text.text("✅ Análisis completado")

        progress_bar.progress(100)

       

        progress_bar.empty()

        status_text.empty()

       

        # Mostrar resultados y guardar en session_state

        mostrar_resultados(resultado)

        st.session_state["resultado_analisis"] = resultado



def mostrar_resultados(resultado: AnalisisCV):

    """Muestra los resultados del análisis de manera estructurada y profesional"""

   

    st.subheader("🎯 Evaluación Principal")

   

    if resultado.porcentaje_ajuste >= 80:

        color = "🟢"

        nivel = "EXCELENTE"

        mensaje = "Candidato altamente recomendado"

    elif resultado.porcentaje_ajuste >= 60:

        color = "🟡"

        nivel = "BUENO"

        mensaje = "Candidato recomendado con reservas"

    elif resultado.porcentaje_ajuste >= 40:

        color = "🟠"

        nivel = "REGULAR"

        mensaje = "Candidato requiere evaluación adicional"

    else:

        color = "🔴"

        nivel = "BAJO"

        mensaje = "Candidato no recomendado"

   

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:

        st.metric(

            label="Porcentaje de Ajuste al Puesto",

            value=f"{resultado.porcentaje_ajuste}%",

            delta=f"{color} {nivel}"

        )

        st.markdown(f"**{mensaje}**")

   

    st.divider()

   

    st.subheader("👤 Perfil del Candidato")

   

    col1, col2 = st.columns(2)

    with col1:

        st.info(f"**👨‍💼 Nombre:** {resultado.nombre_candidato}")
        
        experiencia = resultado.experiencia_meses
        variableTiempo = ""
        if(experiencia < 12):
            variableTiempo = f"{experiencia} meses"
        else:
            variableTiempo = f"{experiencia // 12} años"

        st.info(f"**⏱️ Experiencia:** {variableTiempo}")

   

    with col2:

        st.info(f"**🎓 Educación:** {resultado.education}")

   

    st.subheader("💼 Experiencia Relevante")

    st.info(f"📋 **Resumen de experiencia:**\n\n{resultado.experiencia_relevante}")

   

    st.divider()

   

    st.subheader("🛠️ Habilidades Técnicas Clave")

    if resultado.habilidades_clave:

        cols = st.columns(min(len(resultado.habilidades_clave), 4))

        for i, habilidad in enumerate(resultado.habilidades_clave):

            with cols[i % 4]:

                st.success(f"✅ {habilidad}")

    else:

        st.warning("No se identificaron habilidades técnicas específicas")

   

    st.divider()

   

    col_fortalezas, col_mejoras = st.columns(2)

   

    with col_fortalezas:

        st.subheader("💪 Fortalezas Principales")

        if resultado.fortalezas:

            for i, fortaleza in enumerate(resultado.fortalezas, 1):

                st.markdown(f"**{i}.** {fortaleza}")

        else:

            st.info("No se identificaron fortalezas específicas")

   

    with col_mejoras:

        st.subheader("📈 Áreas de Desarrollo")

        if resultado.areas_mejora:

            for i, area in enumerate(resultado.areas_mejora, 1):

                st.markdown(f"**{i}.** {area}")

        else:

            st.info("No se identificaron áreas de mejora específicas")

   

    st.divider()

   

    st.subheader("📋 Recomendación Final")

   

    if resultado.porcentaje_ajuste >= 70:

        st.success("""

        ✅ **CANDIDATO RECOMENDADO**

       

        El perfil del candidato está bien alineado con los requisitos del puesto.

        Se recomienda proceder con las siguientes etapas del proceso de selección.

        """)

    elif resultado.porcentaje_ajuste >= 50:

        st.warning("""

        ⚠️ **CANDIDATO CON POTENCIAL**

       

        El candidato muestra potencial pero requiere evaluación adicional.

        Se recomienda una entrevista técnica para validar competencias específicas.

        """)

    else:

        st.error("""

        ❌ **CANDIDATO NO RECOMENDADO**

       

        El perfil no se alinea suficientemente con los requisitos del puesto.

        Se recomienda continuar la búsqueda de candidatos más adecuados.

        """)

   

    st.markdown("---")

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:

        if st.button("💾 Guardar Análisis", use_container_width=True):

            resultado_guardado = st.session_state.get("resultado_analisis")

   

            if resultado_guardado is None:

                st.error("⚠️ No hay resultado para guardar. Ejecuta el análisis primero.")

            else:

                try:

                    ruta_json, ruta_pdf = guardar_resultado(resultado_guardado)

                    st.success("✅ Análisis guardado correctamente.")

                    st.info(f"📂 JSON: {ruta_json}")

                    st.info(f"📘 PDF: {ruta_pdf}")



                    # Ofrecer descargas directas

                    try:

                        with open(ruta_pdf, "rb") as fpdf:

                            st.download_button("📥 Descargar PDF", data=fpdf, file_name=os.path.basename(ruta_pdf))

                    except Exception as e:

                        st.warning(f"No se pudo ofrecer descarga de PDF: {e}")



                    try:

                        with open(ruta_json, "rb") as fjson:

                            st.download_button("📥 Descargar JSON", data=fjson, file_name=os.path.basename(ruta_json))

                    except Exception as e:

                        st.warning(f"No se pudo ofrecer descarga de JSON: {e}")



                except Exception as e:

                    st.error(f"❌ Error al guardar el análisis: {e}")

