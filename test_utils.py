import unittest
from datetime import datetime, timedelta
from utils import extraer_numero, formatear_fecha

class TestUtils(unittest.TestCase):

    def test_extraer_numero(self):
        # Casos básicos
        self.assertEqual(extraer_numero("10"), 10)
        self.assertEqual(extraer_numero("0"), 0)
        self.assertEqual(extraer_numero(""), 0)
        
        # Casos con texto
        self.assertEqual(extraer_numero("10 comentarios"), 10)
        self.assertEqual(extraer_numero("5 me gusta"), 5)
        
        # Casos con miles (K)
        self.assertEqual(extraer_numero("1.5k"), 1500)
        self.assertEqual(extraer_numero("1.2K"), 1200)
        self.assertEqual(extraer_numero("100K"), 100000)
        
        # Casos con miles (Mil)
        self.assertEqual(extraer_numero("2 mil"), 2000)
        self.assertEqual(extraer_numero("1.5 mil"), 1500)
        
        # Casos con decimales
        self.assertEqual(extraer_numero("1,5 mil"), 1500) # Formato español
        self.assertEqual(extraer_numero("1.5 mil"), 1500)
        
        # Millones (opcional pero bueno tener)
        self.assertEqual(extraer_numero("1m"), 1000000)

    def test_formatear_fecha(self):
        ahora = datetime.now()
        hoy_str = ahora.strftime("%d-%m-%Y")
        ayer_str = (ahora - timedelta(days=1)).strftime("%d-%m-%Y")
        
        # Relativos Hoy
        self.assertEqual(formatear_fecha("hace 5 min"), hoy_str)
        self.assertEqual(formatear_fecha("Hace 2 horas"), hoy_str)
        self.assertEqual(formatear_fecha("Just now"), hoy_str)
        
        # Relativos Ayer
        self.assertEqual(formatear_fecha("Ayer a las 10:00"), ayer_str)
        self.assertEqual(formatear_fecha("Yesterday"), ayer_str)
        
        # Absolutos (Meses) - Asumimos año actual
        # Nota: Esto es dinámico, si hoy es Feb, "19 de Enero" puede ser este año o el pasado
        # Para el test, usaremos un mes fijo que sepamos que funciona
        self.assertRegex(formatear_fecha("19 de Enero"), r"\d{2}-01-\d{4}")
        self.assertRegex(formatear_fecha("Feb 15"), r"\d{2}-02-\d{4}")

if __name__ == '__main__':
    unittest.main()
