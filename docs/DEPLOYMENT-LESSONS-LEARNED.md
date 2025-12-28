# PetHope - Deployment Lessons Learned

Este documento resume as lições aprendidas durante o deploy da aplicação PetHope em um VPS Hostinger com Coolify.

---

## Sumário

1. [Infraestrutura Escolhida](#infraestrutura-escolhida)
2. [Problemas Encontrados e Soluções](#problemas-encontrados-e-soluções)
3. [Configurações Importantes](#configurações-importantes)
4. [Checklist para Futuros Deploys](#checklist-para-futuros-deploys)

---

## Infraestrutura Escolhida

| Componente | Escolha | Motivo |
|------------|---------|--------|
| VPS | Hostinger KVM 2 | 4 vCPU, 8GB RAM, custo-benefício |
| Orquestrador | Coolify | Interface web, deploy automático via Git |
| Proxy Reverso | Traefik (via Coolify) | SSL automático com Let's Encrypt |
| Banco de Dados | PostgreSQL 16 Alpine | Leve e performático |
| Storage | MinIO | S3-compatible, self-hosted |
| Frontend | Nuxt 3 (SSR) | SEO e performance |
| Backend | FastAPI | Async, alta performance |

---

## Problemas Encontrados e Soluções

### 1. Docker Compose como Override vs Standalone

**Problema:** O arquivo `docker-compose.prod.yml` foi criado como override do `docker-compose.yml`, mas o Coolify precisa de um arquivo standalone completo.

**Sintoma:** Serviços não iniciavam corretamente, faltavam definições.

**Solução:** Criar `docker-compose.prod.yml` como arquivo completo e independente, contendo todas as definições de serviços, volumes e networks.

```yaml
# ERRADO - Override file
services:
  backend:
    environment:
      - ENVIRONMENT=production

# CORRETO - Standalone file
services:
  postgres:
    image: postgres:16-alpine
    # ... definição completa
  backend:
    build:
      context: ./backend
    # ... definição completa
```

---

### 2. npm ci --only=production Deprecated

**Problema:** Flag `--only=production` foi removida nas versões recentes do npm.

**Sintoma:** Build do frontend falhava com erro de flag desconhecida.

**Solução:** Usar `npm install` sem flags ou `npm ci` (requer package-lock.json).

```dockerfile
# ERRADO
RUN npm ci --only=production

# CORRETO
RUN npm install
```

---

### 3. Volume Mounts no Coolify

**Problema:** O Coolify não consegue montar volumes de arquivos locais da mesma forma que o Docker Compose local.

**Sintoma:** Nginx não encontrava os arquivos de configuração.

**Solução:** Criar um Dockerfile para o Nginx que copia os arquivos de configuração para dentro da imagem (bake-in).

```dockerfile
# nginx/Dockerfile
FROM nginx:alpine
RUN apk add --no-cache curl
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/nginx.conf
COPY conf.d/default.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/health || exit 1
```

---

### 4. Health Check com wget vs curl

**Problema:** O nginx:alpine não tem wget instalado por padrão (apenas em algumas versões).

**Sintoma:** Container ficava "unhealthy" e Traefik não roteava tráfego para ele.

**Solução:** Instalar curl e usar `curl -f` no health check.

```dockerfile
# ERRADO
HEALTHCHECK CMD wget -q --spider http://localhost/health || exit 1

# CORRETO
RUN apk add --no-cache curl
HEALTHCHECK CMD curl -f http://localhost/health || exit 1
```

---

### 5. Conflito de Porta 80 com Traefik

**Problema:** Traefik do Coolify já ocupa a porta 80. Tentar expor porta 80 no nginx causa conflito.

**Sintoma:** Erro de bind na porta 80, ou site inacessível.

**Solução:** Usar `expose` em vez de `ports` e deixar o Traefik rotear o tráfego.

```yaml
# ERRADO
nginx:
  ports:
    - "80:80"

# CORRETO
nginx:
  expose:
    - "80"
```

---

### 6. Coolify Gerando Regras Traefik Malformadas

**Problema:** O Coolify gerava regras Traefik inválidas como `Host(\`\`) && PathPrefix(\`pethope.life\`)` em vez de `Host(\`pethope.life\`)`.

**Sintoma:** Erros constantes nos logs do Traefik, ACME challenge falhando com erro 500.

**Solução:** Adicionar labels do Traefik diretamente no docker-compose.prod.yml para sobrescrever as labels automáticas do Coolify.

```yaml
nginx:
  labels:
    - "traefik.enable=true"
    # HTTP Router
    - "traefik.http.routers.pethope-http.rule=Host(`pethope.life`) || Host(`www.pethope.life`)"
    - "traefik.http.routers.pethope-http.entrypoints=http"
    - "traefik.http.routers.pethope-http.service=pethope"
    # HTTPS Router
    - "traefik.http.routers.pethope-https.rule=Host(`pethope.life`) || Host(`www.pethope.life`)"
    - "traefik.http.routers.pethope-https.entrypoints=https"
    - "traefik.http.routers.pethope-https.tls=true"
    - "traefik.http.routers.pethope-https.tls.certresolver=letsencrypt"
    - "traefik.http.routers.pethope-https.service=pethope"
    # Service
    - "traefik.http.services.pethope.loadbalancer.server.port=80"
```

**Importante:** Após modificar o docker-compose.yaml gerado pelo Coolify em `/data/coolify/applications/<id>/`, é necessário remover as labels malformadas que o Coolify adiciona automaticamente.

---

### 7. Labels Duplicadas do Coolify

**Problema:** Mesmo definindo labels corretas no docker-compose.prod.yml, o Coolify adiciona suas próprias labels (malformadas) no arquivo gerado.

**Sintoma:** Duas rotas conflitantes no Traefik.

**Solução:** Editar manualmente o arquivo `/data/coolify/applications/<id>/docker-compose.yaml` no VPS para remover as labels problemáticas:

```bash
# No VPS
sed -i '/http-0-q80kkccg8kocck8kc0gc004g-nginx/d' /data/coolify/applications/<id>/docker-compose.yaml
sed -i '/caddy_/d' /data/coolify/applications/<id>/docker-compose.yaml

# Recriar container
cd /data/coolify/applications/<id>
docker compose stop nginx && docker compose rm -f nginx && docker compose up -d nginx
```

---

### 8. DNS com Múltiplos Registros A

**Problema:** Domínio apontando para dois IPs - o VPS e a página de parking do Hostinger.

**Sintoma:** Site às vezes funciona, às vezes mostra página de "domínio registrado no Hostinger".

**Solução:** No painel de DNS do Hostinger, remover o registro A que aponta para o IP da página de parking (geralmente algo como 84.32.84.32) e manter apenas o registro A para o IP do VPS.

```
# DNS Correto
Tipo: A    Host: @    Valor: 31.97.245.229
Tipo: A    Host: www  Valor: 31.97.245.229
```

---

### 9. Migração de Dados (PostgreSQL e MinIO)

**Processo de migração:**

```bash
# 1. Exportar banco local
docker exec postgres pg_dump -U pethope pethope > backup.sql

# 2. Copiar para VPS
scp backup.sql hostinger:/tmp/

# 3. Importar no VPS
ssh hostinger "cat /tmp/backup.sql | docker exec -i <postgres-container> psql -U pethope pethope"

# 4. Atualizar URLs das imagens no banco
ssh hostinger "docker exec -i <postgres-container> psql -U pethope pethope -c \"UPDATE images SET url = REPLACE(url, 'http://old-url', 'http://new-url');\""

# 5. Copiar imagens do MinIO
# - Acessar MinIO Console local (localhost:9001)
# - Baixar imagens
# - Acessar MinIO Console remoto (vps-ip:9001)
# - Fazer upload das imagens
```

---

### 10. SSL/HTTPS com Let's Encrypt

**Problema:** ACME challenge falhando com erro 500.

**Causa:** Labels malformadas do Traefik impediam o roteamento correto do challenge.

**Solução:** Corrigir as labels do Traefik (ver item 6 e 7) e garantir que:
1. A porta 80 está acessível externamente (para HTTP challenge)
2. O DNS aponta corretamente para o VPS
3. Não há redirect HTTP→HTTPS durante a geração inicial do certificado

**Verificar certificado:**
```bash
ssh hostinger "docker exec coolify-proxy cat /traefik/acme.json | python3 -c 'import json,sys; d=json.load(sys.stdin); print(d.get(\"letsencrypt\",{}).get(\"Certificates\",[]))'"
```

---

## Configurações Importantes

### Variáveis de Ambiente (Produção)

```env
# Database
POSTGRES_DB=pethope
POSTGRES_USER=pethope
POSTGRES_PASSWORD=<senha-segura>

# MinIO
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=<senha-segura>
MINIO_BUCKET=pethope-images

# Backend
SECRET_KEY=<chave-256-bits>
ADMIN_PASSWORD=<senha-admin>
ALLOWED_ORIGINS=https://pethope.life,https://www.pethope.life

# URLs (usar HTTPS em produção)
MINIO_PUBLIC_URL=https://pethope.life/storage
NUXT_PUBLIC_API_BASE=https://pethope.life/api
```

### Estrutura de Arquivos Necessários

```
projeto/
├── docker-compose.prod.yml    # Standalone, completo
├── backend/
│   └── Dockerfile
├── frontend/
│   └── Dockerfile
├── nginx/
│   ├── Dockerfile             # Copia configs para imagem
│   ├── nginx.conf
│   └── conf.d/
│       └── default.conf
└── PRODUCTION-CREDENTIALS.txt  # NÃO versionar!
```

---

## Checklist para Futuros Deploys

### Antes do Deploy

- [ ] Verificar se `docker-compose.prod.yml` é standalone (não override)
- [ ] Verificar se Dockerfiles usam `npm install` (não `npm ci --only=production`)
- [ ] Verificar se nginx/Dockerfile existe e copia as configs
- [ ] Verificar se health checks usam curl (não wget)
- [ ] Gerar senhas seguras para produção
- [ ] Criar arquivo de credenciais (não versionar!)

### Configuração do VPS

- [ ] Criar chave SSH específica para o servidor
- [ ] Adicionar chave pública no servidor
- [ ] Configurar alias SSH no `~/.ssh/config`
- [ ] Verificar se Coolify está acessível (porta 8000)

### Configuração do DNS

- [ ] Remover registros A de parking/placeholder
- [ ] Adicionar registro A para @ apontando para IP do VPS
- [ ] Adicionar registro A para www apontando para IP do VPS
- [ ] Aguardar propagação DNS (até 24h, geralmente minutos)

### Deploy no Coolify

- [ ] Conectar repositório Git
- [ ] Selecionar `docker-compose.prod.yml` como arquivo de compose
- [ ] Configurar variáveis de ambiente
- [ ] Fazer primeiro deploy
- [ ] Verificar logs se houver erro
- [ ] Se labels Traefik estiverem erradas, corrigir manualmente

### Pós-Deploy

- [ ] Verificar health de todos os containers
- [ ] Testar acesso HTTP (deve funcionar ou redirecionar)
- [ ] Testar acesso HTTPS (certificado válido)
- [ ] Testar API (`/api/health`, `/api/animals`)
- [ ] Testar upload de imagens
- [ ] Migrar dados do ambiente anterior (se aplicável)

### Manutenção

- [ ] Monitorar logs: `docker logs <container>`
- [ ] Verificar espaço em disco: `df -h`
- [ ] Backup periódico do banco de dados
- [ ] Atualizar containers periodicamente

---

## Comandos Úteis

```bash
# Conectar ao VPS
ssh hostinger

# Ver containers
docker ps

# Ver logs de um container
docker logs -f <container-name>

# Ver logs do Traefik
docker logs coolify-proxy 2>&1 | tail -100

# Acessar shell do container
docker exec -it <container-name> sh

# Backup do banco
docker exec <postgres-container> pg_dump -U pethope pethope > backup.sql

# Reiniciar container
docker restart <container-name>

# Ver uso de recursos
docker stats

# Limpar imagens não utilizadas
docker image prune -a
```

---

## Recursos e Referências

- [Coolify Documentation](https://coolify.io/docs)
- [Traefik Documentation](https://doc.traefik.io/traefik/)
- [Let's Encrypt](https://letsencrypt.org/)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)

---

*Documento criado em: 28/12/2025*
*Última atualização: 28/12/2025*
