import re
import hashlib
from datetime import datetime, timedelta

def limpiar_texto(texto: str) -> str:
    """Limpia el texto para que no rompa el formato CSV."""
    if not texto: 
        return ""
    # Eliminamos saltos de línea, tabulaciones y retornos de carro
    texto = re.sub(r'[\r\n\t]+', ' ', texto)
    # Eliminamos el punto y coma para evitar conflictos con el separador del CSV
    texto = texto.replace(';', ',')
    # Normalizamos espacios múltiples
    return re.sub(r'\s+', ' ', texto).strip()

def extraer_numero(texto: str) -> int:
    """Convierte textos como '1.5 mil', '10 reaccion', '1.2K' en enteros."""
    if not texto: 
        return 0
    
    texto = texto.lower().strip()
    
    # 1. Limpieza: eliminamos palabras que no sean multiplicadores clave
    # Mantenemos 'k', 'm', 'mil' que son multiplicadores.
    # Eliminamos 'reaccion', 'comentarios', etc.
    palabras_basura = [
        'reaccion', 'comentario', 'me gusta', 'like', 'comment', 'share', 'compartido', 
        'veces', 'comments', 'likes', 'shares', 'reacciones', 'vistas', 'views'
    ]
    for p in palabras_basura:
        texto = texto.replace(p, '')
    
    texto = texto.strip()
    if not texto: return 0

    # 2. Detectar multiplicador y limpiar sufijo
    multiplicador = 1
    
    # 'k' (miles)
    if 'k' in texto:
        multiplicador = 1000
        texto = texto.replace('k', '')
        
    # 'mil' (miles) - Cuidado de no confundir con 'million' si existiera, pero en español 'mil' es 1000.
    elif 'mil' in texto:
        multiplicador = 1000
        texto = texto.replace('mil', '')
        
    # 'm' (millones) - Solo si no es parte de 'mil' o 'min' (minutos no debería llegar aquí si filtramos bien antes)
    elif 'm' in texto and 'mil' not in texto and 'min' not in texto:
        multiplicador = 1000000
        texto = texto.replace('m', '')

    # 3. Normalizar decimales (coma a punto)
    texto = texto.replace(',', '.')
    
    # 4. Extraer el primer número válido
    # Buscamos algo que parezca un número: dígitos, opcionalmente punto y más dígitos.
    match = re.search(r"(\d+(\.\d+)?)", texto)
    if match:
        try:
            valor = float(match.group(1))
            return int(valor * multiplicador)
        except ValueError:
            return 0
            
    return 0

def formatear_fecha(fecha_cruda: str) -> str:
    """
    Intenta normalizar fechas.
    Orden de prioridad:
    1. Fechas relativas inmediatas (Just now, Ahora) -> HOY
    2. Ayer/Yesterday -> AYER
    3. Fechas relativas con tiempo (hace X h, X min) -> HOY (aprox)
    4. Fechas absolutas (19 de Febrero) -> FECHA ESPECIFICA
    5. Días de la semana (Lunes) -> FECHA RELATIVA SEMANAL
    """
    if not fecha_cruda: 
        return ""
    
    ahora = datetime.now()
    fecha_cruda = fecha_cruda.lower().strip()
    
    # --- 1. "Justo ahora" / "Momento" ---
    if any(x in fecha_cruda for x in ["momento", "ahora", "just now", "justo ahora"]):
        return ahora.strftime("%d-%m-%Y")

    # --- 2. Ayer / Yesterday ---
    # Chequeo explícito de palabra completa o inicio fuerte para evitar falsos positivos
    if "ayer" in fecha_cruda or "yesterday" in fecha_cruda:
        return (ahora - timedelta(days=1)).strftime("%d-%m-%Y")

    # --- 3. Tiempo Relativo (h / min / s) ---
    # Usamos regex para asegurar que sea "5 h" o "5h" y no la "h" de "hoy"
    # Buscamos estructuras tipo: digito + espacio? + (h|min|s|seg)
    if re.search(r'\d+\s*(h|hr|hrs|hora|min|m\b|seg|s\b)', fecha_cruda):
        # Asumimos HOY para simplificar (Facebook a veces pone "20 h" que podría ser ayer, pero...)
        # Si es > 24h suele poner "Ayer" o la fecha. Así que "20 h" sigue siendo técnicamente "hace poco".
        # Podríamos refinar si es "23 h" restando, pero para el ejercicio HOY suele bastar o AYER si pasamos medianoche.
        # Mantendremos HOY por simplicidad y consistencia con el requerimiento de fecha actual.
        return ahora.strftime("%d-%m-%Y")

    # --- 4. Fechas Absolutas (Día + Mes) ---
    meses = {
        "enero": 1, "feb": 2, "marzo": 3, "abr": 4, "may": 5, "jun": 6,
        "jul": 7, "ago": 8, "sep": 9, "oct": 10, "nov": 11, "dic": 12,
        "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
        "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12
    }
    
    for nombre_mes, num_mes in meses.items():
        if nombre_mes in fecha_cruda:
            dia_match = re.search(r'\b(\d{1,2})\b', fecha_cruda)
            if dia_match:
                dia = int(dia_match.group(1))
                anio = ahora.year
                # Lógica de cambio de año
                if num_mes > ahora.month + 1: 
                    anio -= 1
                try:
                    return datetime(anio, num_mes, dia).strftime("%d-%m-%Y")
                except ValueError:
                    pass

    # --- 5. Días de la semana ---
    dias = {"lunes": 0, "martes": 1, "miércoles": 2, "miercoles": 2, 
            "jueves": 3, "viernes": 4, "sábado": 5, "sabado": 5, "domingo": 6,
            "mon": 0, "tue": 1, "wed": 2, "thu": 3, "fri": 4, "sat": 5, "sun": 6}
    
    for dia, valor in dias.items():
        if dia in fecha_cruda:
            diferencia = (ahora.weekday() - valor) % 7
            if diferencia == 0: diferencia = 7
            return (ahora - timedelta(days=diferencia)).strftime("%d-%m-%Y")

    return "" 

def generar_id_interno(texto: str) -> str:
    """Genera un hash único basado en el contenido del post."""
    if not texto:
        texto = str(datetime.now().timestamp())
    return hashlib.md5(texto.encode('utf-8')).hexdigest()[:12]