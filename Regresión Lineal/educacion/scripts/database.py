"""
Configuración del motor SQLAlchemy para PostgreSQL local.

Las credenciales se leen de variables de entorno (.env). Si no existen,
se asumen valores por defecto típicos de una instalación local.
"""

import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Carga .env desde la raíz del subproyecto educacion/
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))

DB_USER     = os.getenv("DB_USER",     "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_HOST     = os.getenv("DB_HOST",     "localhost")
DB_PORT     = os.getenv("DB_PORT",     "5432")
DB_NAME     = os.getenv("DB_NAME",     "educacion_db")

DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(DATABASE_URL, echo=False, future=True, pool_pre_ping=True)


def probar_conexion():
    """Devuelve True si la conexión funciona, levanta excepción si no."""
    from sqlalchemy import text
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return True


if __name__ == "__main__":
    print(f"Conectando a: postgresql://{DB_USER}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
    try:
        probar_conexion()
        print("Conexion exitosa")
    except Exception as e:
        print(f"Error de conexion: {e}")
