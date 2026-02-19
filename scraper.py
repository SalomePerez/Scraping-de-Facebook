import os
import time
from datetime import datetime
from playwright.sync_api import sync_playwright
from utils import limpiar_texto, formatear_fecha, generar_id_interno, extraer_numero

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
            # Validación inicial de archivo de sesión
            if not os.path.exists(self.archivo_estado):
                print("[!] No hay sesión previa. Iniciando login...")
                self.iniciar_sesion_manual(p)

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
            page.wait_for_timeout(5000)

            # --- REQUERIMIENTO 3.2: Re-Login si la sesión caduca ---
            if "login" in page.url or page.query_selector('input[name="email"]'):
                print("[!] La sesión ha caducado. Re-autenticando...")
                browser.close()
                self.iniciar_sesion_manual(p)
                return self.extraer_publicaciones(tendencia, id_existente, limite)

            intentos_sin_nuevos = 0
            while len(resultados) < limite and intentos_sin_nuevos < 5:
                # Localizar artículos
                posts = page.query_selector_all('div[role="article"]')
                
                if not posts:
                    posts = page.query_selector_all('div[data-ad-comet-preview="message"]')

                nuevos_en_esta_vuelta = 0

                for post in posts:
                    try:
                        # 1. Extraer Texto
                        texto_elem = post.query_selector('div[data-ad-preview="message"]') or post
                        texto_raw = texto_elem.inner_text()

                        if len(texto_raw) < 20 or "Sugerido" in texto_raw: 
                            continue

                        # --- DEBUG: Guardar estructura del primer post válido para inspección ---
                        if not os.path.exists("debug_post.html"):
                            try:
                                with open("debug_post.html", "w", encoding="utf-8") as f:
                                    f.write(post.evaluate("el => el.outerHTML"))
                                print("[DEBUG] Estructura HTML del post guardada en 'debug_post.html'")
                            except Exception as e:
                                print(f"[DEBUG] No se pudo guardar HTML: {e}")
                        # -----------------------------------------------------------------------

                        # Generar ID único
                        p_id = generar_id_interno(texto_raw[:80])

                        if p_id not in id_existente and p_id not in [r['id'] for r in resultados]:
                            
                            # Usamos EVALUATE para extraer datos con JS directamente en el navegador
                            # Esto es mucho más robusto contra clases ofuscadas
                            datos_post = post.evaluate("""(p) => {
                               // Asegurarse de trabajar siempre con el contenedor completo del post
                               const root = p.closest('[role="article"]') || p;

                               const getText = (sel) => {
                                   const el = root.querySelector(sel);
                                   return el ? el.innerText : "";
                               };
                               
                               // INTENTO 1: Autor
                               // Generalmente en h2 o h3, o en un strong dentro de un a
                               let autor = "";
                               const autorEl = root.querySelector('h2 strong, h3 strong, h2 a, h3 a, strong > a');
                               if (autorEl) autor = autorEl.innerText;
                               if (!autor) {
                                   // Fallback: buscar el primer enlace con texto que no sea vacio
                                   const links = Array.from(root.querySelectorAll('a'));
                                   for (let l of links) {
                                       if (l.innerText.length > 2 && l.innerText.length < 50) {
                                           autor = l.innerText;
                                           break;
                                       }
                                   }
                               }

                               // INTENTO 2: Fecha
                               let fecha = "";
                               // Buscar abbr primero
                               const abbr = root.querySelector('abbr');
                               if (abbr) {
                                   if (abbr.getAttribute('data-utime')) {
                                       fecha = parseInt(abbr.getAttribute('data-utime')); // Timestamp
                                   } else {
                                       fecha = abbr.innerText; // Texto relativo
                                   }
                               }
                               if (!fecha) {
                                   // Buscar texto de fecha en enlaces (suelen estar debajo del autor)
                                   // Buscamos un enlace que tenga un tooltip o que su texto parezca fecha
                                   const dateLink = root.querySelector('a[href*="/posts/"] abbr, a[href*="permalink"] abbr, span[id*="jsc"] a');
                                   if (dateLink) fecha = dateLink.innerText;
                               }
                               
                               // INTENTO 3: URL
                               let url = "";
                               const urlEl = root.querySelector('a[href*="/posts/"], a[href*="/permalink/"], a[href*="watch"], a[href*="photo"]');
                               if (urlEl) {
                                   url = urlEl.getAttribute('href');
                               }

                               // INTENTO 4: Interacciones (Likes, Comentarios)
                               let likes = "0";
                               let comments = "0";
                               
                               // Buscar en todos los elementos con aria-label
                               const interactables = Array.from(root.querySelectorAll('[aria-label]'));
                               for (let el of interactables) {
                                   let label = el.getAttribute('aria-label').toLowerCase();
                                   if (label.includes('reacción') || label.includes('me gusta') || label.includes('like')) {
                                       likes = label;
                                   } else if (label.includes('comentario') || label.includes('comment')) {
                                       comments = label;
                                   }
                               }
                               
                               // Si no encontramos en aria-label, buscar texto visible
                               if (likes === "0" || comments === "0") {
                                   const textContent = root.innerText.toLowerCase();
                                   const lines = textContent.split('\\n');
                                   for (let line of lines) {
                                       if (line.includes('comentario') || line.includes('comments')) {
                                           comments = line;
                                       }
                                       // Es difícil distinguir likes de texto normal sin estructura, 
                                       // pero a veces aparece "20 mil" al lado del icono.
                                   }
                               }

                               return {autor, fecha, url, likes, comments};
                           }""")

                            # Procesar datos extraídos desde JS
                            
                            # Autor
                            autor = datos_post['autor'].split('\n')[0].strip() or "Desconocido"

                            # URL
                            url_final = datos_post['url']
                            if url_final and not url_final.startswith("http"):
                                url_final = self.url_base + url_final.split('?')[0]
                            
                            # Fecha
                            fecha_raw = ""
                            if isinstance(datos_post['fecha'], int):
                                fecha_raw = datetime.fromtimestamp(datos_post['fecha']).strftime("%d-%m-%Y")
                            else:
                                fecha_raw = formatear_fecha(datos_post['fecha'])

                            # Likes y Comentarios
                            likes_val = extraer_numero(datos_post['likes'])
                            coments_val = extraer_numero(datos_post['comments'])

                            resultados.append({
                                "id": p_id,
                                "texto": limpiar_texto(texto_raw),
                                "fecha": fecha_raw,
                                "autor": autor,
                                "likes": likes_val,
                                "comentarios": coments_val,
                                "url": url_final,
                                "fecha_scraping": datetime.now().strftime("%d-%m-%Y %H:%M"),
                                "tema": tendencia
                            })
                            nuevos_en_esta_vuelta += 1
                            if len(resultados) >= limite: break
                    except Exception:
                        continue

                if nuevos_en_esta_vuelta == 0:
                    intentos_sin_nuevos += 1
                    print("Buscando más contenido...")
                else:
                    intentos_sin_nuevos = 0
                    print(f"Progreso: {len(resultados)}/{limite} publicaciones.")

                # Scroll dinámico
                page.mouse.wheel(0, 1500)
                page.wait_for_timeout(4000)

            browser.close()
        return resultados