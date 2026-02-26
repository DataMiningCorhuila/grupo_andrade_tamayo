#!/usr/bin/env python3
import os
import sys
import requests
import json
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
import logging

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

load_dotenv()

log_dir = os.path.join(BASE_DIR, 'logs')
os.makedirs(log_dir, exist_ok=True)

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

        respuesta = input("\npy ¿Deseas guardar los datos en la base de datos? (s/n): ").strip().lower()
        if respuesta == 's':
            self.guardar_en_db(datos_extraidos)

        return datos_extraidos

    def guardar_en_db(self, datos):
        """Guarda los personajes extraídos en la base de datos."""
        try:
            from db.database import SessionLocal
            from db.models import Personaje

            db = SessionLocal()
            insertados = 0
            omitidos = 0

            for item in datos:
                existe = db.query(Personaje).filter(Personaje.id == item['id']).first()
                if existe:
                    omitidos += 1
                    continue
                personaje = Personaje(
                    id=item.get('id'),
                    name=item.get('name'),
                    occupation=item.get('occupation'),
                    birthdate=item.get('birthdate'),
                    portrait_path=item.get('portrait_path'),
                )
                db.add(personaje)
                insertados += 1

            db.commit()
            db.close()
            logger.info(f"Guardado en DB: {insertados} insertados, {omitidos} ya existían.")

        except Exception as e:
            logger.error(f"Error guardando en la base de datos: {str(e)}")

if __name__ == "__main__":
    try:
        extractor = SimpsonsExtractor()
        datos = extractor.ejecutar_extraccion()
        
    except Exception as e:
        logger.error(f"Error en extracción: {str(e)}")
