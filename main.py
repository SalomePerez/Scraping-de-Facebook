import sys

from scraper import FacebookScraper

from data_manager import GestorDeDatos



def ejecutar_aplicacion():

    # Los componentes a inicializar

    gestor = GestorDeDatos()

    scraper = FacebookScraper()



    print("--- Iniciando Scraping de Tendencias en Facebook ---")



    # primero el manejo de la Tendencia (Requerimiento 3.1 y 3.4)

    tendencia = gestor.obtener_tendencia_guardada()    

   

    if tendencia:

        print(f"Usando tendencia previamente guardada: {tendencia}")

    else:

        # Aquí defino una lógica para detectar tendencia

        # o pedirla por consola la primera vez

        print("No se encontró una tendencia guardada.")

        tendencia = input("Introduce el tema o hashtag a investigar: ").strip()

       

        if not tendencia:

            print("[Error] No se puede iniciar sin un tema.")

            sys.exit(1)

       

        #normalizacion rapida para evitar problemas de acentos o mayúsculas

        if tendencia.lower() == "tecnologia":

            tendencia = "tecnología"

           

        gestor.guardar_tendencia(tendencia)

        print(f"Nueva tendencia detectada y guardada: {tendencia}")

   

    # Segundo la ejecucion del manejo de errores, scraper con la tendencia y los IDs existentes

    # para evitar duplicados

    try:

        viejos= gestor.obtener_ids_existentes()

        print(f"Iniciando extraccion (ignorarndo {len(viejos)} ids ya existentes)...")

       

        # El scraper nos devuelve una lista de diccionarios

        nuevos_posts = scraper.extraer_publicaciones(tendencia, id_existente=viejos, limite=50)

       

        # Persistencia y No Duplicación (Requerimiento 3.6)

        if nuevos_posts:

            gestor.guardar_publicaciones(nuevos_posts)

            print("Proceso finalizado con éxito.")

        else:

            print("No se encontraron publicaciones nuevas.")

           

    except Exception as e:

        print(f"Error crítico durante la ejecución: {e}")



if __name__ == "__main__":

    ejecutar_aplicacion()

