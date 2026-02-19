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

class WeatherstackExtractor:
    def __init__(self):
        self.api_key = os.getenv('API_KEY')
        self.base_url = os.getenv('WEATHERSTACK_BASE_URL')
        self.ciudades = os.getenv('CIUDADES').split(',')
        
        if not self.api_key:
            raise ValueError("API_KEY no configurada en .env")
    
    def extraer_clima(self, ciudad):
        """Extrae datos de clima para una ciudad específica"""
        try:
            url = f"{self.base_url}/current"
            params = {
                'access_key': self.api_key,
                'query': ciudad.strip()
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if 'error' in data:
                logger.error(f"Error en API para {ciudad}: {data['error']['info']}")
                return None
            
            logger.info(f"Datos extraídos para {ciudad}")
            return data
            
        except Exception as e:
            logger.error(f"Error extrayendo datos para {ciudad}: {str(e)}")
            return None
    
    def procesar_respuesta(self, response_data):
        """Procesa la respuesta JSON a formato estructurado"""
        try:
            current = response_data.get('current', {})
            location = response_data.get('location', {})
            
            return {
                'ciudad': location.get('name'),
                'pais': location.get('country'),
                'latitud': location.get('lat'),
                'longitud': location.get('lon'),
                'temperatura': current.get('temperature'),
                'sensacion_termica': current.get('feelslike'),
                'humedad': current.get('humidity'),
                'velocidad_viento': current.get('wind_speed'),
                'descripcion': current.get('weather_descriptions', ['N/A'])[0],
                'fecha_extraccion': datetime.now().isoformat(),
                'codigo_tiempo': current.get('weather_code')
            }
        except Exception as e:
            logger.error(f"Error procesando respuesta: {str(e)}")
            return None
    
    def ejecutar_extraccion(self):
        """Ejecuta la extracción para todas las ciudades"""
        datos_extraidos = []
        
        logger.info(f"Iniciando extracción para {len(self.ciudades)} ciudades...")
        
        for ciudad in self.ciudades:
            response = self.extraer_clima(ciudad)
            if response:
                datos_procesados = self.procesar_respuesta(response)
                if datos_procesados:
                    datos_extraidos.append(datos_procesados)
        
        return datos_extraidos

if __name__ == "__main__":
    try:
        extractor = WeatherstackExtractor()
        datos = extractor.ejecutar_extraccion()
        
        # Crear directorio de datos si no existe
        data_dir = os.path.join(BASE_DIR, 'data')
        os.makedirs(data_dir, exist_ok=True)
        
        # Guardar como JSON
        json_path = os.path.join(data_dir, 'clima_raw.json')
        with open(json_path, 'w') as f:
            json.dump(datos, f, indent=2)
        logger.info(f"Datos guardados en {json_path}")
        
        # Guardar como CSV
        df = pd.DataFrame(datos)
        csv_path = os.path.join(data_dir, 'clima.csv')
        df.to_csv(csv_path, index=False)
        logger.info(f"Datos guardados en {csv_path}")
        
        print("\n" + "="*50)
        print("RESUMEN DE EXTRACCIÓN")
        print("="*50)
        print(df.to_string())
        print("="*50)
        
    except Exception as e:
        logger.error(f"Error en extracción: {str(e)}")
