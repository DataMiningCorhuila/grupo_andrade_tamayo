#!/bin/bash
set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}=== The Simpsons API - Docker Setup ===${NC}"

# 1. Verificar .env
if [ ! -f .env ]; then
  echo -e "${YELLOW}No se encontró .env. Creando desde .env.example...${NC}"
  cp .env.example .env
  echo -e "${RED}IMPORTANTE: Edita .env con tus credenciales y vuelve a ejecutar.${NC}"
  exit 1
fi

# Cargar variables del .env en el shell
set -a
# shellcheck disable=SC1091
source .env
set +a

# 2. Build
echo -e "${GREEN}[1/4] Construyendo imágenes Docker...${NC}"
docker compose build

# 3. Levantar PostgreSQL y esperar healthcheck
echo -e "${GREEN}[2/4] Iniciando PostgreSQL...${NC}"
docker compose up -d postgres
echo -e "${YELLOW}Esperando a que PostgreSQL esté listo...${NC}"
until docker compose exec postgres pg_isready -U "${DB_USER}" -d "${DB_NAME}" > /dev/null 2>&1; do
  printf '.'
  sleep 2
done
echo -e "\n${GREEN}PostgreSQL listo.${NC}"

# 4. Ejecutar extractor (interactivo — pregunta si guardar en DB)
echo -e "${GREEN}[3/4] Ejecutando extractor de datos...${NC}"
docker compose run --rm -it -e DB_HOST=postgres extractor python scripts/extractor.py

# 5. Levantar Streamlit
echo -e "${GREEN}[4/4] Iniciando Streamlit...${NC}"
docker compose up -d streamlit

echo -e "${GREEN}"
echo "=========================================="
echo "  Aplicacion disponible en:"
echo "  http://localhost:8501"
echo "=========================================="
echo -e "${NC}"
