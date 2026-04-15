# Guía de Ejecución — Regresión Lineal Educación

Pipeline completo: **Generar datos -> Cargar a PostgreSQL -> Analizar en Jupyter Notebook**.

> Esta guía asume que vas a ejecutar todo desde **WSL (Ubuntu)** sobre Windows. Si usas Windows nativo o macOS los pasos son casi iguales — solo cambia el manejador de paquetes (`apt` -> `brew`/instalador oficial).

---

## 0. Pre-requisitos del sistema

### WSL + Ubuntu

Si aún no tienes WSL:

```powershell
# Desde PowerShell de Windows (como administrador)
wsl --install -d Ubuntu
```

Reinicia y crea tu usuario al arrancar Ubuntu por primera vez.

### Paquetes del sistema (dentro de WSL)

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv python3-dev \
                    postgresql postgresql-contrib libpq-dev
```

---

## 1. Acceder al proyecto

Tu proyecto está en Windows; desde WSL se accede con `/mnt/c/...`:

```bash
cd "/mnt/c/Users/andra/OneDrive/Escritorio/grupo_andrade_tamayo/Regresión Lineal/educacion"
ls
# Debes ver: scripts/ data/ regresion_educacion.ipynb requirements.txt EJECUCION.md
```

---

## 2. Crear y activar entorno virtual

```bash
python3 -m venv venv
source venv/bin/activate
```

Tu prompt cambiará a `(venv) ...`. Para desactivar más adelante: `deactivate`.

---

## 3. Instalar dependencias Python

```bash
pip install -r requirements.txt
```

Esto instala: pandas, numpy, matplotlib, seaborn, scipy, scikit-learn, statsmodels, sqlalchemy, psycopg2-binary, python-dotenv y jupyter.

---

## 4. Levantar PostgreSQL

PostgreSQL en WSL **no arranca automáticamente** con la sesión:

```bash
sudo service postgresql start
sudo service postgresql status   # debe decir "online"
```

> **Tip:** para que arranque solo cada vez que abras WSL, agrega esta línea a tu `~/.bashrc`:
> ```bash
> echo 'sudo service postgresql start > /dev/null 2>&1' >> ~/.bashrc
> ```

---

## 5. Crear usuario y base de datos

```bash
sudo -u postgres psql <<EOF
ALTER USER postgres WITH PASSWORD 'postgres';
CREATE DATABASE educacion_db;
EOF
```

Verifica:

```bash
sudo -u postgres psql -l | grep educacion_db
```

---

## 6. Configurar variables de entorno

```bash
cp .env.example .env
```

El archivo `.env` ya viene con los valores correctos para una instalación local con el password `postgres`. Si usas otro password, edítalo:

```ini
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
DB_NAME=educacion_db
```

---

## 7. Pipeline de ejecución

Los **4 pasos** corren en este orden:

### 7.1 Generar el CSV (2 000 filas)

```bash
python scripts/generador_datos.py
```

Salida esperada:
```
Generando 2,000 registros sinteticos...
CSV guardado en: .../data/educacion.csv
Filas: 2,000

Estadisticas descriptivas:
  hours       4.94  ...
  grade       3.00  ...

Correlaciones con grade:
  grade vs hours       : +0.876
  grade vs sleep       : +0.111
  grade vs attendance  : +0.783
  grade vs screen      : -0.822
```

### 7.2 Probar conexión a PostgreSQL

```bash
python scripts/database.py
```

Salida esperada:
```
Conectando a: postgresql://postgres@localhost:5432/educacion_db
Conexion exitosa
```

### 7.3 Cargar el CSV a PostgreSQL

```bash
python scripts/cargar_postgres.py
```

Esto crea las tablas `instituciones` y `registros_estudiantes`, y carga las 2 000 filas. Salida esperada:

```
Esquema creado: instituciones, registros_estudiantes
CSV leido: 2,000 filas
   -> 5 instituciones insertadas
   -> 2,000 registros_estudiantes insertados

Verificacion:
   instituciones        : 5
   registros_estudiantes: 2,000
Carga completada
```

### 7.4 Abrir el notebook

```bash
jupyter notebook regresion_educacion.ipynb --allow-root
```

> El flag `--allow-root` solo es necesario si estás logueado como `root` en WSL. Con un usuario normal puedes omitirlo.

Te aparecerá una URL en consola tipo:
```
http://127.0.0.1:8888/tree?token=abc123...
```

Cópiala y pégala en tu navegador de Windows. WSL2 hace port-forwarding automático a `localhost`.

---

## 8. Ejecutar el notebook

Una vez abierto en el navegador:

1. Verifica el kernel **Python 3** (esquina superior derecha)
2. **Cell -> Run All** para ejecutar todo el flujo, o
3. **Shift + Enter** celda por celda

El notebook tiene 39 celdas organizadas en 6 fases:

| Fase | Celdas | Contenido                                                                       |
|------|-------:|---------------------------------------------------------------------------------|
| 1    |    1   | Importaciones                                                                   |
| 2    |  2–3   | Conexión PostgreSQL + JOIN                                                      |
| 3    |  4–10  | EDA: descriptivas, histogramas, boxplots, correlación, scatter                  |
| 4    | 11–20  | Regresión simple (`hours -> grade`) + supuestos 1 y 2                           |
| 5    | 21–34  | Regresión múltiple + VIF + Ridge + diagnósticos                                 |
| 6    | 35–38  | Comparación final + predicciones vs reales + conclusiones                       |

Las gráficas se muestran inline y también se guardan en `data/graficas/`.

---

## 9. Estructura del proyecto

```
educacion/
├── data/
│   ├── educacion.csv                # generado en paso 7.1
│   └── graficas/                    # PNGs generados por el notebook
├── scripts/
│   ├── database.py                  # motor SQLAlchemy (lee .env)
│   ├── generador_datos.py           # genera CSV sintético
│   └── cargar_postgres.py           # crea tablas + INSERT desde CSV
├── regresion_educacion.ipynb        # notebook principal (39 celdas)
├── .env                             # credenciales locales (no commitear)
├── .env.example                     # plantilla
├── requirements.txt
├── README.md                        # overview
└── EJECUCION.md                     # esta guía
```

---

## 10. Esquema de la base de datos

```sql
instituciones
├── id      SERIAL PRIMARY KEY
└── nombre  VARCHAR(120) UNIQUE NOT NULL

registros_estudiantes
├── id              SERIAL PRIMARY KEY
├── institucion_id  INTEGER -> instituciones(id)
├── nombre          VARCHAR(60)
├── hours           NUMERIC(4,1)   -- horas de estudio
├── sleep           NUMERIC(4,1)   -- horas de sueño
├── attendance      INTEGER         -- % asistencia
├── screen          NUMERIC(4,1)   -- horas en pantalla
├── grade           NUMERIC(4,2)   -- nota final 1.0–5.0
└── fecha_registro  TIMESTAMP
```

El notebook hace un JOIN entre ambas tablas — mismo patrón que `regresion_clima.ipynb` con `ciudades` <-> `registros_clima`.

---

## 11. Troubleshooting

### `Running as root is not recommended`
Estás logueado como `root` en WSL. Usa `--allow-root` o crea un usuario normal:
```bash
adduser tu_usuario && usermod -aG sudo tu_usuario
```
Luego desde PowerShell: `ubuntu config --default-user tu_usuario`.

### `psycopg2.OperationalError: could not connect to server`
PostgreSQL no está corriendo. Ejecuta:
```bash
sudo service postgresql start
```

### `python-dotenv could not parse statement`
Tu archivo `.env` tiene líneas con sintaxis que no es `KEY=VALUE`. Es **inofensivo** mientras la conexión funcione. Para limpiarlo, abre `.env` y deja solo las 5 líneas `DB_*=...`.

### `password authentication failed for user "postgres"`
El password en `.env` no coincide con el de PostgreSQL. Re-ejecuta el paso 5 para fijar el password a `postgres`, o cambia `DB_PASSWORD` en `.env` al que tengas configurado.

### `ModuleNotFoundError: No module named 'X'`
No tienes el venv activo. Activa con:
```bash
source venv/bin/activate
```

### Jupyter abre pero el navegador no responde
Cierra Jupyter (Ctrl+C) y arranca con:
```bash
jupyter notebook --no-browser --ip=0.0.0.0 --allow-root
```
Copia la URL completa con token en tu navegador de Windows.

### El venv es muy lento sobre `/mnt/c/`
NTFS desde WSL es lento. Mueve el proyecto al filesystem nativo de WSL:
```bash
cp -r "/mnt/c/Users/andra/OneDrive/Escritorio/grupo_andrade_tamayo/Regresión Lineal/educacion" ~/educacion
cd ~/educacion
```

### `FutureWarning` en seaborn boxplots
Inofensivo. Si quieres silenciarlos definitivamente, recarga el notebook desde disco (**File -> Reload Notebook from Disk**) — la celda 6 ya está actualizada con la sintaxis nueva (`hue` + `legend=False`).

---

## 12. Re-ejecutar todo desde cero

Si quieres tirar todo y empezar limpio:

```bash
# Borrar datos generados
rm -f data/educacion.csv
rm -rf data/graficas/*

# Borrar tablas de PostgreSQL
sudo -u postgres psql -d educacion_db -c "DROP TABLE IF EXISTS registros_estudiantes, instituciones CASCADE;"

# Volver al paso 7.1
python scripts/generador_datos.py
python scripts/cargar_postgres.py
jupyter notebook regresion_educacion.ipynb --allow-root
```

---

## Resumen visual

```
[ generador_datos.py ] --> data/educacion.csv (2 000 filas)
                                  |
                                  v
[ cargar_postgres.py ] --> PostgreSQL: educacion_db
                            ├── instituciones (5)
                            └── registros_estudiantes (2 000)
                                  |
                                  v
[ regresion_educacion.ipynb ] <-- SELECT ... JOIN
                                  |
                                  v
                            data/graficas/*.png
                            + visualización inline
```
