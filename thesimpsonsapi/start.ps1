$ErrorActionPreference = "Stop"

Write-Host "=== The Simpsons API - Docker Setup ===" -ForegroundColor Green

# 1. Verificar .env
if (-not (Test-Path ".env")) {
    Write-Host "No se encontró .env. Creando desde .env.example..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "IMPORTANTE: Edita .env con tus datos y vuelve a ejecutar." -ForegroundColor Red
    exit 1
}

# Cargar variables del .env
Get-Content ".env" | ForEach-Object {
    if ($_ -match '^\s*([^#][^=]+)=(.*)$') {
        [System.Environment]::SetEnvironmentVariable($matches[1].Trim(), $matches[2].Trim(), "Process")
    }
}

$DB_USER = $env:DB_USER
$DB_NAME = $env:DB_NAME

# 2. Build
Write-Host "[1/4] Construyendo imagenes Docker..." -ForegroundColor Green
docker compose build

# 3. Levantar PostgreSQL y esperar
Write-Host "[2/4] Iniciando PostgreSQL..." -ForegroundColor Green
docker compose up -d postgres

Write-Host "Esperando a que PostgreSQL este listo..." -ForegroundColor Yellow
$ready = $false
while (-not $ready) {
    docker compose exec postgres pg_isready -U $DB_USER -d $DB_NAME 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        $ready = $true
    } else {
        Write-Host "." -NoNewline
        Start-Sleep -Seconds 2
    }
}
Write-Host "`nPostgreSQL listo." -ForegroundColor Green

# 4. Ejecutar extractor (interactivo)
Write-Host "[3/4] Ejecutando extractor de datos..." -ForegroundColor Green
docker compose run --rm -it -e DB_HOST=postgres extractor python scripts/extractor.py

# 5. Levantar Streamlit
Write-Host "[4/4] Iniciando Streamlit..." -ForegroundColor Green
docker compose up -d streamlit

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "  Aplicacion disponible en:"              -ForegroundColor Green
Write-Host "  http://localhost:8501"                   -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
