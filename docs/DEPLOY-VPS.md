# Deploy em VPS - PetHope

Guia completo para deploy da aplicacao PetHope em um servidor VPS com dominio proprio e SSL gratuito.

## Requisitos

### VPS (Servidor)
- **Minimo**: 1 vCPU, 1GB RAM, 20GB SSD
- **Recomendado**: 2 vCPU, 2GB RAM, 40GB SSD
- **Sistema**: Ubuntu 22.04 LTS ou Debian 12

### Provedores Recomendados
| Provedor | Plano Basico | Preco/mes |
|----------|--------------|-----------|
| Hostinger | VPS 1 | ~R$20 |
| DigitalOcean | Droplet | ~$6 |
| Linode | Nanode | ~$5 |
| Vultr | Cloud Compute | ~$6 |
| Contabo | VPS S | ~€5 |

### Dominio
- Registre um dominio (~R$40/ano)
- Recomendados: Registro.br, Cloudflare, Namecheap

## Passo 1: Configurar DNS

No painel do seu dominio, adicione os registros:

```
Tipo  | Nome | Valor           | TTL
------|------|-----------------|-----
A     | @    | IP_DO_SERVIDOR  | 3600
A     | www  | IP_DO_SERVIDOR  | 3600
```

## Passo 2: Configurar o Servidor

### 2.1 Conectar via SSH
```bash
ssh root@IP_DO_SERVIDOR
```

### 2.2 Atualizar sistema
```bash
apt update && apt upgrade -y
```

### 2.3 Instalar Docker
```bash
# Instalar Docker
curl -fsSL https://get.docker.com | sh

# Instalar Docker Compose
apt install docker-compose-plugin -y

# Verificar instalacao
docker --version
docker compose version
```

### 2.4 Criar usuario para deploy
```bash
# Criar usuario
adduser pethope
usermod -aG docker pethope
usermod -aG sudo pethope

# Configurar SSH para o novo usuario
mkdir -p /home/pethope/.ssh
cp ~/.ssh/authorized_keys /home/pethope/.ssh/
chown -R pethope:pethope /home/pethope/.ssh
chmod 700 /home/pethope/.ssh
chmod 600 /home/pethope/.ssh/authorized_keys
```

### 2.5 Configurar Firewall
```bash
apt install ufw -y
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow http
ufw allow https
ufw enable
```

## Passo 3: Deploy da Aplicacao

### 3.1 Clonar repositorio
```bash
su - pethope
git clone https://github.com/E-Tasso/pet-hope.git
cd pet-hope
```

### 3.2 Configurar variaveis de ambiente
```bash
cp .env.example .env
nano .env
```

Edite o arquivo `.env`:
```bash
# Database
POSTGRES_DB=pethope
POSTGRES_USER=pethope
POSTGRES_PASSWORD=SENHA_FORTE_AQUI

# MinIO
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=SENHA_FORTE_AQUI
MINIO_BUCKET=pethope-images
MINIO_PUBLIC_URL=https://SEU_DOMINIO/storage

# Backend
SECRET_KEY=GERAR_COM_openssl_rand_hex_32
ADMIN_PASSWORD=SENHA_ADMIN_FORTE
ALLOWED_ORIGINS=https://SEU_DOMINIO,https://www.SEU_DOMINIO
ENVIRONMENT=production

# Frontend
NUXT_PUBLIC_API_BASE=https://SEU_DOMINIO/api

# Dominio
DOMAIN=SEU_DOMINIO
LETSENCRYPT_EMAIL=seu@email.com
```

Gerar SECRET_KEY:
```bash
openssl rand -hex 32
```

### 3.3 Criar arquivo de producao do nginx
```bash
nano nginx/conf.d/prod.conf
```

Cole o conteudo do arquivo `nginx/conf.d/prod.conf.example` e ajuste o dominio.

### 3.4 Iniciar em modo producao
```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## Passo 4: Configurar SSL (Let's Encrypt)

### 4.1 Instalar Certbot
```bash
apt install certbot -y
```

### 4.2 Parar nginx temporariamente
```bash
docker compose stop nginx
```

### 4.3 Gerar certificado
```bash
certbot certonly --standalone -d SEU_DOMINIO -d www.SEU_DOMINIO --email seu@email.com --agree-tos --no-eff-email
```

### 4.4 Configurar renovacao automatica
```bash
# Testar renovacao
certbot renew --dry-run

# Adicionar ao crontab
crontab -e
```

Adicione a linha:
```
0 3 * * * certbot renew --quiet && docker compose restart nginx
```

### 4.5 Reiniciar nginx com SSL
```bash
docker compose up -d nginx
```

## Passo 5: Verificar Deploy

```bash
# Verificar containers
docker compose ps

# Ver logs
docker compose logs -f

# Testar endpoints
curl https://SEU_DOMINIO/health
curl https://SEU_DOMINIO/api/animals/feed
```

## Manutencao

### Atualizar aplicacao
```bash
cd ~/pet-hope
git pull origin main
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

### Ver logs
```bash
# Todos os servicos
docker compose logs -f

# Servico especifico
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f nginx
```

### Backup do banco de dados
```bash
docker exec pethope-postgres pg_dump -U pethope pethope > backup_$(date +%Y%m%d).sql
```

### Restaurar backup
```bash
docker exec -i pethope-postgres psql -U pethope pethope < backup.sql
```

### Reiniciar servicos
```bash
docker compose restart
```

### Parar tudo
```bash
docker compose down
```

## Estrutura de Arquivos no Servidor

```
/home/pethope/
└── pet-hope/
    ├── .env                 # Configuracoes (NAO versionar!)
    ├── docker-compose.yml
    ├── docker-compose.prod.yml
    ├── backend/
    ├── frontend/
    ├── nginx/
    │   └── conf.d/
    │       └── prod.conf    # Configuracao de producao
    └── ssl/                 # Certificados (link simbolico)
        ├── fullchain.pem -> /etc/letsencrypt/live/DOMINIO/fullchain.pem
        └── privkey.pem -> /etc/letsencrypt/live/DOMINIO/privkey.pem
```

## Troubleshooting

### Erro de permissao no Docker
```bash
sudo usermod -aG docker $USER
newgrp docker
```

### Certificado SSL nao renova
```bash
# Verificar status
certbot certificates

# Renovar manualmente
certbot renew --force-renewal
```

### Container nao inicia
```bash
# Ver logs detalhados
docker compose logs --tail=100 SERVICO

# Recriar container
docker compose up -d --force-recreate SERVICO
```

### Banco de dados corrompido
```bash
# Parar servicos
docker compose down

# Remover volume do postgres
docker volume rm pethelp_postgres_data

# Reiniciar (vai criar banco novo)
docker compose up -d
```

## Monitoramento (Opcional)

### Instalar Portainer (GUI para Docker)
```bash
docker volume create portainer_data
docker run -d -p 9443:9443 --name portainer \
  --restart=always \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v portainer_data:/data \
  portainer/portainer-ce:latest
```

Acesse: `https://IP_DO_SERVIDOR:9443`

## Custos Estimados

| Item | Custo Mensal | Custo Anual |
|------|--------------|-------------|
| VPS (basico) | R$20-30 | R$240-360 |
| Dominio .com.br | - | R$40 |
| SSL | Gratuito | Gratuito |
| **Total** | **~R$25** | **~R$340** |
