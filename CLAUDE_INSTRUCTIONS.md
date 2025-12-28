# Instruções para Desenvolvimento - PetHope

Este documento contém instruções detalhadas para o Claude Code desenvolver a plataforma PetHope de adoção de animais.

## Contexto do Projeto

Estamos construindo uma plataforma web para divulgação de animais disponíveis para adoção. O sistema será inicialmente self-hosted em uma máquina pessoal, mas a arquitetura deve permitir fácil migração para cloud no futuro.

O desenvolvedor tem experiência com Vue, Angular, C#, Python e Java, então pode-se usar terminologia técnica sem necessidade de explicações básicas.

## Stack Obrigatória

- **Frontend**: Nuxt 3 com Vue 3 (Composition API + `<script setup>`)
- **Estilização**: Tailwind CSS + shadcn-vue
- **Backend**: FastAPI (Python 3.11+)
- **Banco de Dados**: PostgreSQL 16
- **ORM**: SQLAlchemy 2.0 com async
- **Migrations**: Alembic
- **Storage**: MinIO (S3-compatible)
- **Proxy**: Nginx
- **Orquestração**: Docker Compose

## Ordem de Desenvolvimento

Siga esta ordem para construir o projeto de forma incremental:

### Fase 1: Infraestrutura Base

1. Criar `docker-compose.yml` com todos os serviços (postgres, minio, backend, frontend, nginx)
2. Criar `docker-compose.override.yml` para desenvolvimento (hot reload, volumes)
3. Criar `.env.example` com todas as variáveis necessárias
4. Configurar Nginx como reverse proxy

### Fase 2: Backend - Estrutura Base

1. Criar estrutura de pastas do FastAPI
2. Configurar conexão async com PostgreSQL
3. Configurar cliente MinIO/S3
4. Implementar health check endpoint
5. Configurar CORS para desenvolvimento

### Fase 3: Backend - Models e Schemas

1. Criar models SQLAlchemy:
   - `Animal` (campos conforme README)
   - `Image` (relacionamento com Animal)
2. Criar schemas Pydantic para request/response
3. Configurar Alembic e criar migration inicial

### Fase 4: Backend - API Endpoints

1. CRUD completo de animais:
   - `GET /api/animals` - Listar com filtros e paginação
   - `GET /api/animals/{id}` - Detalhes de um animal
   - `POST /api/animals` - Criar animal
   - `PUT /api/animals/{id}` - Atualizar animal
   - `DELETE /api/animals/{id}` - Remover animal
   - `PATCH /api/animals/{id}/status` - Atualizar status

2. Upload de imagens:
   - `POST /api/animals/{id}/images` - Upload de imagem
   - `DELETE /api/images/{id}` - Remover imagem
   - `PATCH /api/images/{id}/primary` - Definir como principal

3. Endpoints auxiliares:
   - `GET /api/species` - Listar espécies disponíveis
   - `GET /api/locations` - Listar localizações com animais

### Fase 5: Frontend - Estrutura Base

1. Criar projeto Nuxt 3 com configurações:
   - SSR habilitado
   - Tailwind CSS configurado
   - shadcn-vue instalado e configurado
2. Criar layout principal com header e footer
3. Configurar composable para API calls (`useApi`)
4. Criar types TypeScript baseados nos schemas do backend

### Fase 6: Frontend - Páginas Públicas

1. **Home (`/`)**: 
   - Hero section com call-to-action
   - Grid de animais em destaque
   - Filtros básicos (espécie, porte, localização)
   - Paginação ou infinite scroll

2. **Lista de Animais (`/animais`)**:
   - Filtros avançados na sidebar
   - Cards dos animais com imagem principal
   - Ordenação (mais recentes, etc.)

3. **Detalhes do Animal (`/animais/[id]`)**:
   - Galeria de imagens
   - Informações completas
   - Badges de características
   - Card de contato

### Fase 7: Frontend - Área Administrativa

1. **Login (`/admin/login`)**:
   - Autenticação simples por senha (sem usuário inicialmente)
   - Armazenar token no localStorage/cookie

2. **Dashboard (`/admin`)**:
   - Contagem de animais por status
   - Lista rápida de recém-cadastrados

3. **Gerenciar Animais (`/admin/animais`)**:
   - Tabela com todos os animais
   - Ações: editar, excluir, alterar status

4. **Cadastrar/Editar Animal (`/admin/animais/novo` e `/admin/animais/[id]/editar`)**:
   - Formulário completo
   - Upload de múltiplas imagens com preview
   - Drag-and-drop para reordenar imagens

### Fase 8: Polimento e Produção

1. Criar `docker-compose.prod.yml` otimizado
2. Configurar Nginx para produção com SSL (Certbot)
3. Criar scripts de backup (banco + imagens)
4. Adicionar rate limiting no Nginx
5. Configurar logs apropriados

## Padrões de Código

### Backend (Python/FastAPI)

```python
# Usar type hints sempre
async def get_animal(animal_id: UUID) -> Animal:
    ...

# Usar Pydantic para validação
class AnimalCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    species: Species
    ...

# Injeção de dependência para DB session
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session

# Routers organizados por domínio
router = APIRouter(prefix="/animals", tags=["animals"])
```

### Frontend (Vue/Nuxt)

```vue
<!-- Usar Composition API com script setup -->
<script setup lang="ts">
// Types explícitos
interface Animal {
  id: string
  name: string
  // ...
}

// Composables para lógica reutilizável
const { data: animals, pending } = await useApi<Animal[]>('/animals')
</script>

<!-- Classes Tailwind organizadas -->
<template>
  <div class="container mx-auto px-4 py-8">
    <!-- ... -->
  </div>
</template>
```

### Commits

Usar Conventional Commits:
- `feat: add animal listing page`
- `fix: correct image upload validation`
- `chore: update dependencies`
- `docs: add API documentation`

## Variáveis de Ambiente

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/pethope

# MinIO/S3
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=pethope-images
MINIO_USE_SSL=false

# Backend
SECRET_KEY=your-secret-key-here
ADMIN_PASSWORD=your-admin-password
ALLOWED_ORIGINS=http://localhost:3000

# Frontend
NUXT_PUBLIC_API_BASE=http://localhost:8000/api
```

## Estrutura de Resposta da API

```json
// Listagem com paginação
{
  "items": [...],
  "total": 100,
  "page": 1,
  "page_size": 20,
  "pages": 5
}

// Erros
{
  "detail": "Animal not found",
  "code": "ANIMAL_NOT_FOUND"
}
```

## Componentes shadcn-vue a Utilizar

- `Button` - Botões em geral
- `Card` - Cards de animais
- `Input` - Campos de formulário
- `Select` - Dropdowns de filtro
- `Badge` - Tags de características
- `Dialog` - Modais de confirmação
- `Table` - Tabela do admin
- `Tabs` - Navegação em formulários
- `Toast` - Notificações
- `Skeleton` - Loading states

## Tratamento de Imagens

1. Aceitar: JPG, PNG, WebP
2. Limite: 5MB por imagem
3. Gerar thumbnail (400x400) no upload
4. Armazenar original e thumbnail no MinIO
5. Servir via URL pública do MinIO (ou proxy pelo Nginx)

## SEO (Importante para Adoção)

- Títulos dinâmicos: "Adote {nome} - {espécie} para adoção em {cidade}"
- Meta descriptions com informações do animal
- Open Graph tags para compartilhamento
- Sitemap.xml automático
- Schema.org markup para animais

## Testes (Opcional no MVP)

Se houver tempo, priorizar:
1. Testes de integração dos endpoints principais
2. Testes E2E do fluxo de cadastro

## Notas Importantes

1. **Não complicar demais no início** - O MVP deve funcionar primeiro, otimizações depois
2. **Mobile-first** - A maioria dos acessos será por celular
3. **Imagens são importantes** - Boas fotos aumentam chance de adoção
4. **Performance** - Lazy loading de imagens, paginação server-side
5. **Acessibilidade** - Alt text nas imagens, contraste adequado

## Perguntas para Esclarecer Durante Desenvolvimento

Antes de tomar decisões significativas, pergunte sobre:
- Preferência de tema (claro/escuro/ambos)
- Campos obrigatórios vs opcionais no cadastro
- Fluxo de contato (mostrar direto ou formulário?)
- Necessidade de múltiplos idiomas
- Integração com redes sociais

---

**Comece pela Fase 1 e avance sequencialmente. Ao concluir cada fase, valide que está funcionando antes de prosseguir.**
