#!/usr/bin/env python3
import os
import sys
import requests
import json
import time
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

    def _extraer_paginado(self, endpoint):
        """Extrae todos los resultados de un endpoint paginado."""
        todos = []
        page = 1
        while True:
            try:
                url = f"{self.API_URL}/{endpoint}?page={page}"
                response = requests.get(url, timeout=15)
                response.raise_for_status()
                data = response.json()

                resultados = data.get('results', [])
                if not resultados:
                    break

                todos.extend(resultados)
                logger.info(f"[{endpoint}] Página {page}: {len(resultados)} registros")

                if not data.get('next'):
                    break

                page += 1
                time.sleep(0.3)

            except Exception as e:
                logger.error(f"[{endpoint}] Error en página {page}: {e}")
                break

        logger.info(f"[{endpoint}] Total extraído: {len(todos)} registros")
        return todos

    def ejecutar_extraccion(self):
        """Ejecuta la extracción de personajes, episodios y ubicaciones."""
        logger.info("Iniciando extracción completa")

        # Personajes
        personajes = self._extraer_paginado('characters')
        self._guardar_json(personajes, 'simpsons_characters.json')
        self._guardar_personajes(personajes)

        # Episodios
        episodios = self._extraer_paginado('episodes')
        self._guardar_json(episodios, 'simpsons_episodes.json')
        self._guardar_episodios(episodios)

        # Ubicaciones
        ubicaciones = self._extraer_paginado('locations')
        self._guardar_json(ubicaciones, 'simpsons_locations.json')
        self._guardar_ubicaciones(ubicaciones)

        logger.info("Extracción completa finalizada")
        return personajes, episodios, ubicaciones

    def _guardar_json(self, datos, nombre_archivo):
        """Guarda datos en un archivo JSON."""
        ruta = os.path.join(BASE_DIR, 'data', nombre_archivo)
        os.makedirs(os.path.dirname(ruta), exist_ok=True)
        with open(ruta, 'w', encoding='utf-8') as f:
            json.dump(datos, f, ensure_ascii=False, indent=4)
        logger.info(f"JSON guardado: {nombre_archivo} ({len(datos)} registros)")

    def _guardar_personajes(self, datos):
        """Guarda o actualiza personajes en la base de datos."""
        try:
            from db.database import SessionLocal
            from db.models import Personaje

            db = SessionLocal()
            insertados, actualizados = 0, 0

            for item in datos:
                existente = db.query(Personaje).filter(Personaje.id == item['id']).first()
                if existente:
                    existente.name = item.get('name')
                    existente.age = item.get('age')
                    existente.gender = item.get('gender')
                    existente.status = item.get('status')
                    existente.occupation = item.get('occupation')
                    existente.birthdate = item.get('birthdate')
                    existente.portrait_path = item.get('portrait_path')
                    existente.phrases = item.get('phrases', [])
                    actualizados += 1
                else:
                    personaje = Personaje(
                        id=item.get('id'),
                        name=item.get('name'),
                        age=item.get('age'),
                        gender=item.get('gender'),
                        status=item.get('status'),
                        occupation=item.get('occupation'),
                        birthdate=item.get('birthdate'),
                        portrait_path=item.get('portrait_path'),
                        phrases=item.get('phrases', []),
                    )
                    db.add(personaje)
                    insertados += 1

            db.commit()
            db.close()
            logger.info(f"Personajes DB: {insertados} insertados, {actualizados} actualizados")

        except Exception as e:
            logger.error(f"Error guardando personajes: {e}")

    def _guardar_episodios(self, datos):
        """Guarda o actualiza episodios en la base de datos."""
        try:
            from db.database import SessionLocal
            from db.models import Episodio

            db = SessionLocal()
            insertados, actualizados = 0, 0

            for item in datos:
                existente = db.query(Episodio).filter(Episodio.id == item['id']).first()
                if existente:
                    existente.name = item.get('name')
                    existente.season = item.get('season')
                    existente.episode_number = item.get('episode_number')
                    existente.airdate = item.get('airdate')
                    existente.synopsis = item.get('synopsis')
                    existente.image_path = item.get('image_path')
                    actualizados += 1
                else:
                    episodio = Episodio(
                        id=item.get('id'),
                        name=item.get('name'),
                        season=item.get('season'),
                        episode_number=item.get('episode_number'),
                        airdate=item.get('airdate'),
                        synopsis=item.get('synopsis'),
                        image_path=item.get('image_path'),
                    )
                    db.add(episodio)
                    insertados += 1

            db.commit()
            db.close()
            logger.info(f"Episodios DB: {insertados} insertados, {actualizados} actualizados")

        except Exception as e:
            logger.error(f"Error guardando episodios: {e}")

    def _guardar_ubicaciones(self, datos):
        """Guarda o actualiza ubicaciones en la base de datos."""
        try:
            from db.database import SessionLocal
            from db.models import Ubicacion

            db = SessionLocal()
            insertados, actualizados = 0, 0

            for item in datos:
                existente = db.query(Ubicacion).filter(Ubicacion.id == item['id']).first()
                if existente:
                    existente.name = item.get('name')
                    existente.image_path = item.get('image_path')
                    existente.town = item.get('town')
                    existente.use = item.get('use')
                    actualizados += 1
                else:
                    ubicacion = Ubicacion(
                        id=item.get('id'),
                        name=item.get('name'),
                        image_path=item.get('image_path'),
                        town=item.get('town'),
                        use=item.get('use'),
                    )
                    db.add(ubicacion)
                    insertados += 1

            db.commit()
            db.close()
            logger.info(f"Ubicaciones DB: {insertados} insertados, {actualizados} actualizados")

        except Exception as e:
            logger.error(f"Error guardando ubicaciones: {e}")


if __name__ == "__main__":
    try:
        from db.database import init_db
        logger.info("Inicializando tablas de base de datos...")
        init_db()

        extractor = SimpsonsExtractor()
        extractor.ejecutar_extraccion()

    except Exception as e:
        logger.error(f"Error en extracción: {e}")
