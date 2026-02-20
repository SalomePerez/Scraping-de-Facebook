# Scraper de Tendencias en Facebook - Prueba Técnica - Salome Perez

Este proyecto es una solución automatizada para detectar, extraer y almacenar publicaciones en tendencia de Facebook, cumpliendo con los estándares de persistencia, limpieza de datos y control de duplicados requeridos en la prueba técnica.

## 📹 Video de Ejecución
[Ver Video de Demostración en Google Drive](https://drive.google.com/file/d/1BIhhubHZj6mWFt1jD8JoNRTQHVaV_M9p/view?usp=sharing)

## 📋 Características Implementadas
- **Detección de Tendencia:** Identifica y reutiliza temas para evitar redundancia (Requerimiento 3.1 y 3.4).
- **Autenticación Persistente:** Manejo de sesiones mediante cookies (`estado_sesion.json`) para evitar logins constantes (Requerimiento 3.2).
- **Extracción Inteligente:** Scraping de hasta 50 publicaciones con scroll dinámico usando Playwright (Requerimiento 3.3).
- **Control de Duplicados:** Mecanismo basado en hashes de contenido para evitar registros repetidos (Requerimiento 3.4).
- **Normalización de Datos:** Limpieza de texto, manejo de encoding UTF-8 y formateo robusto de fechas relativas ("Hace 2h", "Ayer") y absolutas (Requerimiento 3.5).
- **Datos Extraídos:** ID, Texto, Fecha, Autor, Likes, Comentarios, URL.

## 🛠️ Tecnologías
- **Python 3.10+**
- **Playwright:** Para la navegación, manejo de DOM dinámico y cookies.
- **Pandas:** Para la gestión de datos, limpieza y exportación a CSV.
- **JSON:** Para la persistencia de configuración.

## 🚀 Instalación y Ejecución

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/SalomePerez/Scraping-de-Facebook.git
   cd Scraping-de-Facebook
   ```

2. **Crear y activar el entorno virtual:**
   ```bash
   python -m venv venv
   # En Windows:
   venv\Scripts\activate
   # En Linux/Mac:
   source venv/bin/activate
   ```

3. **Instalar Dependencias:**
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

4. **Ejecutar el Scraper:**
   ```bash
   python main.py
   ```
   *El script solicitará inicio de sesión manual la primera vez y guardará la sesión para futuras ejecuciones.*

## 🔑 Credenciales de Prueba (Opcional)
Se ha creado una cuenta de Facebook dedicada para probar este desarrollo. Puede utilizarla si no desea usar su cuenta personal.
> **Nota:** Estas credenciales son exclusivamente para evaluación de esta prueba técnica.

- **Email:** `salome.perezf@uqvirtual.edu.co`
- **Contraseña:** `MariaSalome12345`

## 📂 Estructura del Proyecto
- `main.py`: Punto de entrada, orquesta la lógica.
- `scraper.py`: Contiene la clase `FacebookScraper` con la lógica de navegación y extracción (Playwright/JS).
- `utils.py`: Funciones de limpieza de texto, parseo de fechas y conversión numérica.
- `data_manager.py`: Manejo de Pandas y persistencia en CSV/JSON.
- `test_utils.py`: Pruebas unitarias para validar la limpieza de datos.
