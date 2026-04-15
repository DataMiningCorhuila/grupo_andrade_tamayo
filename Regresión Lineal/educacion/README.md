# Regresión Lineal — Rendimiento Académico

Pipeline paralelo a `regresion_clima.ipynb` pero con datos sintéticos de
estudiantes (≈ 2 000 registros). Las variables y correlaciones siguen el
patrón de `education-regression.jsx`:

| Variable     | Descripción                          | Relación con `grade` |
|--------------|--------------------------------------|----------------------|
| `hours`      | Horas de estudio por día (1 – 10)    | + fuerte             |
| `sleep`      | Horas de sueño (4 – 9)               | + leve               |
| `attendance` | % de asistencia (50 – 100)           | + moderada           |
| `screen`     | Horas en pantalla (1 – 8)            | − fuerte             |
| `grade`      | Nota final (1.0 – 5.0)               | objetivo             |

## Estructura

```
educacion/
├── data/
│   └── educacion.csv                # generado (2 000 filas)
├── scripts/
│   ├── database.py                  # engine SQLAlchemy
│   ├── generador_datos.py           # CSV sintético
│   └── cargar_postgres.py           # crea tablas + INSERT
├── regresion_educacion.ipynb        # mismo flujo que regresion_clima
├── .env.example
└── requirements.txt
```

## Uso

```bash
# 1. Dependencias
pip install -r requirements.txt

# 2. Configurar credenciales locales de PostgreSQL
cp .env.example .env
# y crear la base:
#   createdb educacion_db    (o desde pgAdmin)

# 3. Generar el CSV
python scripts/generador_datos.py

# 4. Cargar el CSV en PostgreSQL (crea instituciones + registros_estudiantes)
python scripts/cargar_postgres.py

# 5. Abrir el notebook
jupyter notebook regresion_educacion.ipynb
```

## Esquema en PostgreSQL

```
instituciones (id, nombre)
registros_estudiantes (id, institucion_id -> instituciones.id,
                       nombre, hours, sleep, attendance, screen,
                       grade, fecha_registro)
```

El notebook hace JOIN entre ambas tablas — exactamente el mismo patrón
que `regresion_clima.ipynb` usa con `ciudades` <-> `registros_clima`.

Para la guía completa de instalación y ejecución paso a paso, ver
[`EJECUCION.md`](./EJECUCION.md).
