# Deploy com ngrok - PetHope

Este documento descreve como expor a aplicação PetHope para acesso externo usando ngrok.

## Pré-requisitos

- Docker Desktop instalado e rodando
- ngrok instalado ([download](https://ngrok.com/download))
- Conta no ngrok (gratuita)

## Configuração Inicial

### 1. Configurar authtoken do ngrok

Obtenha seu authtoken em https://dashboard.ngrok.com/get-started/your-authtoken

```powershell
ngrok config add-authtoken SEU_AUTHTOKEN_AQUI
```

### 2. Iniciar os containers

```powershell
docker compose up -d
```

### 3. Iniciar o ngrok

```powershell
ngrok http 80
```

O ngrok exibirá uma URL pública como `https://abc123.ngrok-free.app`

### 4. Configurar a aplicação

Execute o script de configuração com a URL do ngrok:

```powershell
cd scripts
.\ngrok-setup.ps1 -NgrokUrl "https://abc123.ngrok-free.app"
```

### 5. Reiniciar os containers

```powershell
docker compose down
docker compose up -d
```

### 6. Atualizar URLs das imagens existentes (se necessário)

Se você já tem imagens cadastradas no banco, execute:

```powershell
docker exec pethope-postgres psql -U pethope -d pethope -c "UPDATE images SET original_url = REPLACE(original_url, 'http://localhost:9000/pethope-images/', 'https://SUA-URL.ngrok-free.app/pethope-images/'), thumbnail_url = REPLACE(thumbnail_url, 'http://localhost:9000/pethope-images/', 'https://SUA-URL.ngrok-free.app/pethope-images/');"
```

## Arquitetura

```
[Internet]
     |
     v
[ngrok tunnel] ──> https://xxx.ngrok-free.app
     |
     v
[Nginx :80]
     |
     ├── /api/*          ──> [Backend :8000]
     │                            |
     │                            ├── PostgreSQL :5432
     │                            └── MinIO :9000
     │
     ├── /pethope-images/* ──> [MinIO :9000]
     │
     ├── /storage/*      ──> [MinIO :9000]
     │
     └── /*               ──> [Frontend :3000]
```

## Variáveis de Ambiente

O script `ngrok-setup.ps1` atualiza as seguintes variáveis no `.env`:

| Variável | Descrição | Exemplo |
|----------|-----------|---------|
| `ALLOWED_ORIGINS` | Origens permitidas para CORS | `...,https://xxx.ngrok-free.app` |
| `NUXT_PUBLIC_API_BASE` | URL base da API para o frontend | `https://xxx.ngrok-free.app/api` |
| `MINIO_PUBLIC_URL` | URL pública para imagens | `https://xxx.ngrok-free.app/storage` |

## Endpoints Disponíveis

| Endpoint | Descrição |
|----------|-----------|
| `/` | Aplicação frontend (Nuxt) |
| `/api/animals` | API de animais |
| `/api/animals/feed` | Feed de animais |
| `/docs` | Documentação Swagger |
| `/redoc` | Documentação ReDoc |
| `/health` | Health check |
| `/pethope-images/*` | Imagens armazenadas |

## Scripts Disponíveis

### ngrok-setup.ps1

Configura a aplicação para usar ngrok:

```powershell
.\scripts\ngrok-setup.ps1 -NgrokUrl "https://xxx.ngrok-free.app"
```

### ngrok-reset.ps1

Restaura as configurações para desenvolvimento local:

```powershell
.\scripts\ngrok-reset.ps1
```

## Restaurar Configuração Local

Para voltar ao desenvolvimento local:

```powershell
# 1. Parar o ngrok (Ctrl+C no terminal do ngrok)

# 2. Restaurar configurações
cd scripts
.\ngrok-reset.ps1

# 3. Atualizar URLs das imagens no banco (opcional)
docker exec pethope-postgres psql -U pethope -d pethope -c "UPDATE images SET original_url = REPLACE(original_url, 'https://xxx.ngrok-free.app/pethope-images/', 'http://localhost/storage/'), thumbnail_url = REPLACE(thumbnail_url, 'https://xxx.ngrok-free.app/pethope-images/', 'http://localhost/storage/');"

# 4. Reiniciar containers
docker compose down
docker compose up -d
```

## Troubleshooting

### Porta 8000 em uso

Se aparecer erro de porta em uso:

```powershell
net stop winnat
net start winnat
docker compose up -d
```

### Imagens não carregam

Verifique se as URLs no banco estão corretas:

```powershell
docker exec pethope-postgres psql -U pethope -d pethope -c "SELECT original_url FROM images LIMIT 5;"
```

### Nginx não inicia

Verifique os logs:

```powershell
docker logs pethope-nginx
```

### CORS bloqueando requisições

Verifique se a URL do ngrok está em `ALLOWED_ORIGINS` no `.env`:

```powershell
grep ALLOWED_ORIGINS .env
```

## Limitações do ngrok Free

- URLs mudam a cada reinício do ngrok
- Limite de conexões simultâneas
- Banner de aviso do ngrok em navegadores
- Rate limiting em requisições

## Dicas

1. **URL estável**: Use ngrok com plano pago para ter um subdomínio fixo
2. **Webhook testing**: Ideal para testar integrações com serviços externos
3. **Mobile testing**: Acesse a URL do ngrok pelo celular na mesma rede
4. **Inspeção**: Acesse http://127.0.0.1:4040 para ver todas as requisições

## Referências

- [ngrok Documentation](https://ngrok.com/docs)
- [ngrok Dashboard](https://dashboard.ngrok.com)
