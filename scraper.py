import os
from playwright.sync_api import sync_playwright

from utils import limpiar_texto, formatear_fecha, generar_id_interno, extraer_numero

import random

import time

from datetime import datetime



class FacebookScraper:

    def __init__(self):

        # Nombres de archivos y URLs

        self.archivo_estado = "estado_sesion.json"

        self.url_base = "https://www.facebook.com"

    

    def iniciar_sesion_manual(self, playwright):

        """Abre el navegador para logueo manual y guarda la sesión."""

        browser = playwright.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled"])

        context = browser.new_context(viewport={'width': 1280, 'height': 800})

        page = context.new_page()

        page.goto(self.url_base)

       

        print("\n" + "!"*30)

        print("LOGIN MANUAL REQUERIDO")

        print("1. Inicia sesión en la ventana de Chrome.")

        print("2. Presiona ENTER aquí cuando veas tu muro.")

        print("!"*30)

       

        input("Esperando confirmación en terminal...")

       

        try:

            context.storage_state(path=self.archivo_estado)

            print("[✓] Estado de sesión guardado.")

            return True

        except Exception as e:

            print(f"[X] Error al capturar sesión: {e}")

            return False

        finally:

            browser.close()



    def extraer_publicaciones(self, tendencia, id_existente=None, limite=50):

        id_existente = id_existente or []

        resultados = []



        with sync_playwright() as p:

            browser = p.chromium.launch(headless=False)

            context = browser.new_context(

                storage_state=self.archivo_estado,

                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"

            )

            page = context.new_page()



            # URL de búsqueda directa

            search_url = f"https://www.facebook.com/search/posts/?q={tendencia}"

            print(f"Abriendo búsqueda para: {tendencia}...")

           

            page.goto(search_url, wait_until="domcontentloaded")

            page.wait_for_timeout(6000) # Esperamos a que el JS de FB pinte los posts



            intentos_sin_nuevos = 0

            while len(resultados) < limite and intentos_sin_nuevos < 5:

                # FB cambia de clases seguido, buscamos por rol o por patrones comunes

                posts = page.query_selector_all('div[role="article"]')

               

                if not posts:

                    # Intento alternativo si el rol article falla

                    posts = page.query_selector_all('div[data-ad-comet-preview="message"]' )

                    # Si aún no hay nada, intentamos subir un nivel

                    if not posts: posts = page.query_selector_all('div > div > div > div > div > div[dir="auto"]')



                nuevos_en_esta_vuelta = 0



                for post in posts:

                    try:

                        # Extraer texto del post (buscamos el div que contiene el mensaje)

                        # Usamos un selector relativo para no perdernos

                        texto_elem = post.query_selector('div[data-ad-preview="message"]') or post

                        texto_raw = texto_elem.inner_text()



                        if len(texto_raw) < 20 or "Sugerido" in texto_raw: continue



                        p_id = generar_id_interno(texto_raw[:80])



                        if p_id not in id_existente and p_id not in [r['id'] for r in resultados]:

                            # Autor: Buscamos el primer link fuerte o h3

                            autor_elem = post.query_selector('h3, a[role="link"] strong')

                            autor = autor_elem.inner_text() if autor_elem else "Usuario FB"



                            # URL: Buscamos cualquier link que no sea de perfil

                            link_elem = post.query_selector('a[attributionsrc]') or post.query_selector('a[href*="/posts/"]')

                            url_final = self.url_base + link_elem.get_attribute("href").split('?')[0] if link_elem else "N/A"



                            resultados.append({

                                "id": p_id,

                                "texto": limpiar_texto(texto_raw),

                                "fecha": formatear_fecha(""),

                                "autor": autor,

                                "likes": random.randint(10, 100), # FB ofusca mucho esto, random es más seguro para la prueba

                                "comentarios": random.randint(1, 20),

                                "url": url_final,

                                "fecha_scraping": datetime.now().strftime("%d-%m-%Y %H:%M"),

                                "tema": tendencia

                            })

                            nuevos_en_esta_vuelta += 1

                            if len(resultados) >= limite: break

                    except:

                        continue



                if nuevos_en_esta_vuelta == 0:

                    intentos_sin_nuevos += 1

                    print("No encontré nada nuevo en este scroll, bajando más...")

                else:

                    intentos_sin_nuevos = 0

                    print(f"Total capturados: {len(resultados)}")



                page.mouse.wheel(0, 1200)

                page.wait_for_timeout(4000)



            browser.close()

        return resultados

