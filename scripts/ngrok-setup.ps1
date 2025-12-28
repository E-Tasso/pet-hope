# PetHope - ngrok Setup Script
# Este script configura a aplicacao para funcionar com ngrok
#
# Uso: .\ngrok-setup.ps1 -NgrokUrl "https://abc123.ngrok.io"

param(
    [Parameter(Mandatory=$true)]
    [string]$NgrokUrl
)

# Remove trailing slash se existir
$NgrokUrl = $NgrokUrl.TrimEnd('/')

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " PetHope - Configuracao ngrok" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "URL do ngrok: $NgrokUrl" -ForegroundColor Yellow

# Caminho do arquivo .env
$envPath = Join-Path $PSScriptRoot "..\.env"

if (-not (Test-Path $envPath)) {
    Write-Host "ERRO: Arquivo .env nao encontrado em $envPath" -ForegroundColor Red
    exit 1
}

# Ler conteudo atual do .env
$envContent = Get-Content $envPath -Raw

# Atualizar ALLOWED_ORIGINS (adiciona ngrok URL)
$envContent = $envContent -replace "ALLOWED_ORIGINS=.*", "ALLOWED_ORIGINS=http://localhost:3000,http://localhost,$NgrokUrl"

# Atualizar NUXT_PUBLIC_API_BASE
$envContent = $envContent -replace "NUXT_PUBLIC_API_BASE=.*", "NUXT_PUBLIC_API_BASE=$NgrokUrl/api"

# Atualizar MINIO_PUBLIC_URL
$envContent = $envContent -replace "MINIO_PUBLIC_URL=.*", "MINIO_PUBLIC_URL=$NgrokUrl/storage"

# Salvar arquivo .env
$envContent | Set-Content $envPath -NoNewline

Write-Host ""
Write-Host "Arquivo .env atualizado!" -ForegroundColor Green
Write-Host ""
Write-Host "Configuracoes aplicadas:" -ForegroundColor White
Write-Host "  ALLOWED_ORIGINS      : ..., $NgrokUrl" -ForegroundColor Gray
Write-Host "  NUXT_PUBLIC_API_BASE : $NgrokUrl/api" -ForegroundColor Gray
Write-Host "  MINIO_PUBLIC_URL     : $NgrokUrl/storage" -ForegroundColor Gray
Write-Host ""
Write-Host "========================================" -ForegroundColor Yellow
Write-Host " PROXIMOS PASSOS:" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Reinicie os containers:" -ForegroundColor White
Write-Host "   docker compose down" -ForegroundColor Cyan
Write-Host "   docker compose up -d" -ForegroundColor Cyan
Write-Host ""
Write-Host "2. Inicie o ngrok apontando para porta 80:" -ForegroundColor White
Write-Host "   ngrok http 80" -ForegroundColor Cyan
Write-Host ""
Write-Host "3. Acesse a aplicacao em:" -ForegroundColor White
Write-Host "   $NgrokUrl" -ForegroundColor Green
Write-Host ""
Write-Host "Para restaurar configuracoes locais:" -ForegroundColor Gray
Write-Host "   .\ngrok-reset.ps1" -ForegroundColor Gray
Write-Host ""
