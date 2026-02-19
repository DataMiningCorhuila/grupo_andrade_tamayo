#!/usr/bin/env python3
import os
import requests
import json
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
import logging

# Obtener el directorio base del proyecto (parent del directorio scripts)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Cargar variables de entorno
load_dotenv()

# Crear directorio de logs si no existe
log_dir = os.path.join(BASE_DIR, 'logs')
os.makedirs(log_dir, exist_ok=True)

# Configurar logging
log_file = os.path.join(log_dir, 'etl.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SimpsonsExtractor:
    def __init__(self):
        self.API_URL = os.getenv('API_URL')
        
        if not self.API_URL:
            raise ValueError("API_URL no configurada en .env")
    
    def extraer_personajes(self, page):
        """Extrae datos de personajes de The Simpsons"""
        try:
            url = f"{self.API_URL}/characters?page={page}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()

            logger.info(f"Datos extraídos de página {page}")
            return data
            
        except Exception as e:
            logger.error(f"Error extrayendo datos de página {page}: {str(e)}")
            return None
    
    def ejecutar_extraccion(self):
        """Ejecuta la extracción para todas las ciudades"""
        datos_extraidos = []
        
        logger.info(f"Iniciando extracción")
        
        page = 1
        while True:
            datos_personajes = self.extraer_personajes(page)
            if datos_personajes is None or 'results' not in datos_personajes or len(datos_personajes['results']) == 0:
                logger.info(f"No hay más datos para extraer en la página {page}. Finalizando extracción.")
                break
            resultados = datos_personajes.get('results', [])
            for personaje in resultados:
                datos_extraidos.append({
                    'id': personaje.get('id'),
                    'name': personaje.get('name'),
                    'occupation': personaje.get('occupation'),
                    'birthdate': personaje.get('birthdate'),
                    'portrait_path': personaje.get('portrait_path')
                
            })       
            page += 1
        
        
        with open(os.path.join(BASE_DIR, 'data', 'simpsons_characters.json'), 'w', encoding='utf-8') as f:
            json.dump(datos_extraidos, f, ensure_ascii=False, indent=4)
            
        logger.info(f"Extracción finalizada con {len(datos_extraidos)} registros")
        return datos_extraidos

if __name__ == "__main__":
    try:
        extractor = SimpsonsExtractor()
        datos = extractor.ejecutar_extraccion()
        
    except Exception as e:
        logger.error(f"Error en extracción: {str(e)}")
