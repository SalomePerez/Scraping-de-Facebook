# Scraper de Tendencias en Facebook - Prueba Técnica - Salome Perez

Este proyecto es una solución automatizada para detectar, extraer y almacenar publicaciones en tendencia de Facebook, cumpliendo con estándares de persistencia, limpieza de datos y control de duplicados.

## Características
- **Detección de Tendencia:** Identifica y reutiliza temas para evitar redundancia (Requerimiento 3.1 y 3.4).
- **Autenticación Persistente:** Manejo de sesiones mediante cookies/estado (Requerimiento 3.2).
- **Extracción Inteligente:** Scraping de hasta 50 publicaciones con scroll dinámico (Requerimiento 3.3).
- **Control de Duplicados:** Mecanismo basado en hashes de contenido para evitar registros repetidos (Requerimiento 3.4).
- **Normalización de Datos:** Limpieza de texto, manejo de encoding UTF-8 y formateo de fechas (Requerimiento 3.5).

## Tecnologías
- **Python 3.10+**
- **Playwright:** Para la navegación y manejo de estado de sesión.
- **Pandas:** Para la gestión de datos y generación de CSV.
- **JSON:** Para la persistencia de configuración.

## Instalación

1. **Clonar el repositorio:**
   ```bash
   git clone <tu-url-del-repo>
   cd <nombre-de-la-carpeta>

2. **Crear el enfotno virtual**
    python -m venv venv
    # En Windows:
    venv\Scripts\activate
    # En Linux/Mac:
    source venv/bin/activate

3. **Instalar Dependencias**
    pip install -r requirements.txt
    playwright install chromium

4. **Y para ejecutarlo con**
    python main.py