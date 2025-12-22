import PyPDF2
from io import BytesIO

def extraer_texto_pdf(archivo_pdf):
    try:
        archivo_pdf.seek(0)
        pdf_reader = PyPDF2.PdfReader(BytesIO(archivo_pdf.read()))
        texto_completo = ""
       
        for numero_pagina, pagina in enumerate(pdf_reader.pages,1):
           texto_pagina = pagina.extract_text()
           if texto_pagina.strip():  # Verificar si la página no está vacía
                texto_completo += f"\n--- Página {numero_pagina} ---\n"
                texto_completo += texto_pagina + "\n"
        
        texto_completo = texto_completo.strip()
        
        
        if not texto_completo:
            return "Error: El PDF parece estar vacío o contener solo imágenes."
       
        return texto_completo
    
    except Exception as e:
       return f"Error al procesar el archivo PDF: {str(e)}"
   