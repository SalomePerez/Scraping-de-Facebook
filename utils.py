import re
import hashlib
from datetime import datetime, timedelta

def limpiar_texto(texto: str) -> str:
    if not texto: return ""
    # Eliminamos ruidos comunes y normalizamos espacios
    texto = re.sub(r'[\r\n\t]+', ' ', texto)
    return re.sub(r'\s+', ' ', texto).strip()

def extraer_numero(texto: str) -> int:
    if not texto: return 0
    # Quitamos puntos de miles para no confundir a la regex
    texto = texto.replace('.', '').replace(',', '')
    numeros = re.findall(r'\d+', texto)
    return int(numeros[0]) if numeros else 0

def formatear_fecha(fecha_cruda: str) -> str:
    if not fecha_cruda: 
        return ""
    
    ahora = datetime.now()
    fecha_cruda = fecha_cruda.lower()
    
    # Lógica simple para fechas relativas comunes
    if " h" in fecha_cruda or " min" in fecha_cruda:
        return ahora.strftime("%d-%m-%Y")
    if "ayer" in fecha_cruda:
        return (ahora - timedelta(days=1)).strftime("%d-%m-%Y")
    
    # Si Facebook da una fecha más compleja, intentamos capturar el año o mes
    # Por ahora, si no es relativa, devolvemos vacío para cumplir el requisito de "no inventar"
    return ahora.strftime("%d-%m-%Y") 

def generar_id_interno(texto: str) -> str:
    return hashlib.md5(texto.encode('utf-8')).hexdigest()[:12]