# 🐾 PetHope - Plataforma de Adoção de Animais

## Visão Geral

PetHope é uma plataforma web para divulgação de animais disponíveis para adoção. O sistema permite que abrigos, ONGs e protetores independentes cadastrem animais e que pessoas interessadas encontrem seu novo companheiro.

## Objetivos

- **Facilitar a adoção responsável** conectando animais a potenciais adotantes
- **Centralizar informações** sobre animais disponíveis em uma região
- **Reduzir o abandono** aumentando a visibilidade de animais resgatados
- **Simplificar o processo** tanto para quem cadastra quanto para quem adota

## Funcionalidades Principais

### MVP (Primeira versão)

- [ ] Listagem pública de animais disponíveis para adoção
- [ ] Página de detalhes do animal com galeria de fotos
- [ ] Filtros por espécie, porte, localização e características
- [ ] Cadastro de animais com upload de múltiplas imagens
- [ ] Informações de contato para interessados
- [ ] Área administrativa básica (protegida por senha)

### Evoluções Futuras

- [ ] Cadastro de múltiplos abrigos/protetores
- [ ] Sistema de favoritos para visitantes
- [ ] Formulário de interesse em adoção
- [ ] Notificações por email/WhatsApp
- [ ] Histórico de adoções bem-sucedidas
- [ ] App mobile

## Stack Tecnológica

| Camada | Tecnologia | Justificativa |
|--------|------------|---------------|
| Frontend | Nuxt 3 + Vue 3 | SSR para SEO, DX produtiva, ecossistema maduro |
| Estilização | Tailwind CSS + shadcn-vue | Prototipação rápida, design consistente |
| Backend | FastAPI (Python) | Alta produtividade, async, documentação automática |
| Banco de Dados | PostgreSQL | Robusto, suporte a JSON, fácil migração para cloud |
| Storage | MinIO | S3-compatible, facilita migração futura |
| Proxy/SSL | Nginx + Let's Encrypt | SSL gratuito, cache, rate limiting |
| Orquestração | Docker Compose | Deploy simplificado, ambiente reproduzível |

## Arquitetura

```
                                    ┌─────────────────┐
                                    │    Internet     │
                                    └────────┬────────┘
                                             │
                                    ┌────────▼────────┐
                                    │     Nginx       │
                                    │  (SSL + Proxy)  │
                                    │    :80/:443     │
                                    └────────┬────────┘
                                             │
                       ┌─────────────────────┼─────────────────────┐
                       │                     │                     │
              ┌────────▼────────┐   ┌────────▼────────┐   ┌────────▼────────┐
              │    Frontend     │   │    Backend      │   │     MinIO       │
              │    Nuxt 3       │   │    FastAPI      │   │    Storage      │
              │     :3000       │   │     :8000       │   │     :9000       │
              └─────────────────┘   └────────┬────────┘   └─────────────────┘
                                             │
                                    ┌────────▼────────┐
                                    │   PostgreSQL    │
                                    │     :5432       │
                                    └─────────────────┘
```

## Modelo de Dados

### Animal

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | UUID | Identificador único |
| name | string | Nome do animal |
| species | enum | Espécie (cão, gato, pássaro, roedor, outro) |
| breed | string? | Raça (opcional) |
| age_months | int? | Idade estimada em meses |
| size | enum | Porte (pequeno, médio, grande) |
| gender | enum | Sexo (macho, fêmea, indefinido) |
| description | text | Descrição e história do animal |
| status | enum | Status (disponível, em processo, adotado) |
| traits | string[] | Características (castrado, vacinado, vermifugado, etc.) |
| special_needs | text? | Necessidades especiais |
| location | string | Cidade/região |
| contact_info | json | Informações de contato |
| created_at | datetime | Data de cadastro |
| updated_at | datetime | Última atualização |

### Image

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | UUID | Identificador único |
| animal_id | UUID | FK para Animal |
| url | string | URL da imagem no storage |
| is_primary | bool | Se é a imagem principal |
| order | int | Ordem na galeria |

## Estrutura de Pastas

```
pethope/
├── docker-compose.yml          # Ambiente de desenvolvimento
├── docker-compose.prod.yml     # Ambiente de produção
├── .env.example                # Template de variáveis de ambiente
├── README.md                   # Este arquivo
│
├── frontend/                   # Aplicação Nuxt 3
│   ├── pages/
│   ├── components/
│   ├── composables/
│   ├── layouts/
│   └── nuxt.config.ts
│
├── backend/                    # API FastAPI
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── routers/
│   │   └── services/
│   ├── alembic/
│   ├── tests/
│   └── requirements.txt
│
├── nginx/                      # Configuração do proxy
│   ├── nginx.conf
│   └── nginx.prod.conf
│
└── scripts/                    # Scripts utilitários
    ├── backup.sh
    ├── restore.sh
    └── setup-ssl.sh
```

## Requisitos para Rodar

### Desenvolvimento
- Docker e Docker Compose
- Node.js 20+ (opcional, para dev sem Docker)
- Python 3.11+ (opcional, para dev sem Docker)

### Produção (Self-hosted)
- Servidor Linux com Docker
- Domínio apontando para o IP do servidor
- Portas 80 e 443 liberadas

## Como Executar

### Setup Inicial

```bash
# 1. Copiar variáveis de ambiente
cp .env.example .env

# 2. Editar .env e ajustar as senhas e configurações
# IMPORTANTE: Altere SECRET_KEY, ADMIN_PASSWORD, e senhas do banco
nano .env  # ou use seu editor preferido

# 3. Subir ambiente de desenvolvimento
docker compose up -d

# 4. Verificar se todos os serviços estão rodando
docker compose ps

# 5. Ver logs em tempo real (opcional)
docker compose logs -f
```

### Acessar Serviços

- **Frontend (Site público)**: http://localhost
- **API Docs (Swagger)**: http://localhost/docs
- **MinIO Console**: http://localhost:9001
- **PostgreSQL**: localhost:5432

### Comandos Úteis

```bash
# Parar todos os serviços
docker compose down

# Parar e remover volumes (apaga dados!)
docker compose down -v

# Rebuild após mudanças no código
docker compose up -d --build

# Ver logs de um serviço específico
docker compose logs -f backend
docker compose logs -f frontend

# Acessar shell de um container
docker compose exec backend bash
docker compose exec frontend sh
docker compose exec postgres psql -U pethope

# Rodar migrations (quando backend estiver pronto)
docker compose exec backend alembic upgrade head
```

### Desenvolvimento

O ambiente está configurado com hot reload:
- **Backend**: Mudanças em `backend/` recarregam automaticamente
- **Frontend**: Mudanças em `frontend/` atualizam via HMR (Hot Module Replacement)

### Troubleshooting

**Erro de porta já em uso:**
```bash
# Verificar o que está usando a porta
netstat -ano | findstr :80    # Windows
lsof -i :80                   # Linux/Mac

# Alterar porta no .env
NGINX_HTTP_PORT=8080
```

**Containers não iniciam:**
```bash
# Ver logs detalhados
docker compose logs

# Rebuild completo
docker compose down -v
docker compose up -d --build
```

## Licença

MIT License - Sinta-se livre para usar e modificar.

---

**Desenvolvido com 💜 para ajudar animais a encontrarem um lar**
