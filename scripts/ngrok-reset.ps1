# PetHope - Reset ngrok Configuration
# Este script restaura as configuracoes para desenvolvimento local
#
# Uso: .\ngrok-reset.ps1

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " PetHope - Restaurar config local" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Caminho do arquivo .env
$envPath = Join-Path $PSScriptRoot "..\.env"

if (-not (Test-Path $envPath)) {
    Write-Host "ERRO: Arquivo .env nao encontrado em $envPath" -ForegroundColor Red
    exit 1
}

# Ler conteudo atual do .env
$envContent = Get-Content $envPath -Raw

# Restaurar ALLOWED_ORIGINS
$envContent = $envContent -replace "ALLOWED_ORIGINS=.*", "ALLOWED_ORIGINS=http://localhost:3000,http://localhost"

# Restaurar NUXT_PUBLIC_API_BASE
$envContent = $envContent -replace "NUXT_PUBLIC_API_BASE=.*", "NUXT_PUBLIC_API_BASE=http://localhost/api"

# Restaurar MINIO_PUBLIC_URL
$envContent = $envContent -replace "MINIO_PUBLIC_URL=.*", "MINIO_PUBLIC_URL=http://localhost/storage"

# Salvar arquivo .env
$envContent | Set-Content $envPath -NoNewline

Write-Host "Configuracoes restauradas para desenvolvimento local!" -ForegroundColor Green
Write-Host ""
Write-Host "Valores restaurados:" -ForegroundColor White
Write-Host "  ALLOWED_ORIGINS      : http://localhost:3000,http://localhost" -ForegroundColor Gray
Write-Host "  NUXT_PUBLIC_API_BASE : http://localhost/api" -ForegroundColor Gray
Write-Host "  MINIO_PUBLIC_URL     : http://localhost/storage" -ForegroundColor Gray
Write-Host ""
Write-Host "Reinicie os containers:" -ForegroundColor Yellow
Write-Host "  docker compose down && docker compose up -d" -ForegroundColor Cyan
Write-Host ""
Write-Host "Acesse em: http://localhost" -ForegroundColor Green
Write-Host ""
