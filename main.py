import sys
import random # <--- IMPORTANTE: No olvides este
from scraper import FacebookScraper
from data_manager import GestorDeDatos

def ejecutar_aplicacion():
    # Los componentes a inicializar
    gestor = GestorDeDatos()
    scraper = FacebookScraper()

    print("--- Iniciando Scraping de Tendencias en Facebook ---")

    # Primero el manejo de la Tendencia (Requerimiento 3.1 y 3.4)
    tendencia = gestor.obtener_tendencia_guardada()    

    if tendencia:
        print(f"Usando tendencia previamente guardada: {tendencia}")
    else:
        print("Detectando tema de tendencia actual...")
        # Simulación de detección automática (Requerimiento 3.1)
        temas_del_momento = ["Tecnología", "Inteligencia Artificial", "Ciberseguridad", "Innovación Digital"]
        tendencia = random.choice(temas_del_momento) 
        
        # Normalización rápida
        if tendencia.lower() == "tecnologia":
            tendencia = "tecnología"

        # Guardar y notificar
        gestor.guardar_tendencia(tendencia)
        print(f"Tema elegido automáticamente: {tendencia} !!!")

    if not tendencia:
        print("[Error] No se pudo determinar un tema de investigación.")
        sys.exit(1)

    # Segundo: ejecución del scraper con manejo de errores
    try:
        viejos = gestor.obtener_ids_existentes()
        print(f"Iniciando extracción (ignorando {len(viejos)} IDs ya existentes)...")
        
        # El scraper nos devuelve una lista de diccionarios
        nuevos_posts = scraper.extraer_publicaciones(tendencia, id_existente=viejos, limite=50)
        
        # Persistencia y No Duplicación (Requerimiento 3.6)
        if nuevos_posts:
            gestor.guardar_publicaciones(nuevos_posts)
            print(f"Proceso finalizado. Se agregaron {len(nuevos_posts)} nuevas publicaciones.")
        else:
            print("No se encontraron publicaciones nuevas o diferentes a las ya almacenadas.")
            
    except Exception as e:
        print(f"Error crítico durante la ejecución: {e}")

if __name__ == "__main__":
    ejecutar_aplicacion()