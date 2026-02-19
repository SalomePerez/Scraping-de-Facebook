import pandas as pd
import os
import json

class GestorDeDatos:
    def __init__(self, archivo_csv="publicaciones_fb.csv", archivo_config="config.json"):
        self.archivo_csv = archivo_csv
        self.archivo_config = archivo_config
        # ORDEN REQUERIDO: ID, Texto, Fecha, Autor, Likes, Comentarios, URL, Extras
        self.columnas_ordenadas = [
            'id', 'texto', 'fecha', 'autor', 
            'likes', 'comentarios', 'url', 'fecha_scraping', 'tema'
        ]

    def obtener_tendencia_guardada(self) -> str:
        """Lee la tendencia desde el archivo config.json"""
        if os.path.exists(self.archivo_config):
            try:
                with open(self.archivo_config, 'r', encoding='utf-8') as f:
                    datos = json.load(f)
                    return datos.get("tendencia_actual")
            except Exception:
                return None
        return None

    def guardar_tendencia(self, tendencia: str):
        """Guarda la tendencia actual en config.json"""
        with open(self.archivo_config, 'w', encoding='utf-8') as f:
            json.dump({"tendencia_actual": tendencia}, f, ensure_ascii=False, indent=4)

    def guardar_publicaciones(self, nuevas_publicaciones: list):
        if not nuevas_publicaciones: return

        df_nuevo = pd.DataFrame(nuevas_publicaciones)
        
        # Limpieza de seguridad: solo columnas permitidas y en orden
        df_nuevo = df_nuevo[self.columnas_ordenadas]

        if os.path.exists(self.archivo_csv):
            try:
                # Leemos asegurando que no traiga columnas extra
                df_existente = pd.read_csv(self.archivo_csv, sep=';', encoding='utf-8')
                df_final = pd.concat([df_existente, df_nuevo]).drop_duplicates(subset=['id'], keep='first')
            except Exception:
                df_final = df_nuevo
        else:
            df_final = df_nuevo

        # Aseguramos que los "N/A" se conviertan en vacíos antes de guardar
        df_final = df_final.fillna("")
        
        df_final.to_csv(self.archivo_csv, index=False, encoding='utf-8', sep=';')
        print(f"[✓] CSV actualizado. Registros totales: {len(df_final)}")

    def obtener_ids_existentes(self) -> set:
        if os.path.exists(self.archivo_csv):
            try:
                df = pd.read_csv(self.archivo_csv, usecols=['id'], sep=';')
                return set(df['id'].astype(str).tolist())
            except:
                return set()
        return set()