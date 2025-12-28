# PetHope Frontend

Nuxt 3 frontend for the PetHope pet adoption platform.

## Tech Stack

- **Framework**: Nuxt 3 (Vue 3 + SSR)
- **Styling**: Tailwind CSS
- **Components**: shadcn-vue (Radix Vue)
- **Icons**: Lucide Vue
- **Language**: TypeScript

## Setup

### With Docker (Recommended)

```bash
# From project root
docker compose up -d frontend
```

Visit http://localhost:3000

### Local Development

```bash
# Install dependencies
npm install

# Start dev server
npm run dev
```

## Project Structure

```
frontend/
├── assets/css/          # Global styles (Tailwind)
├── components/
│   ├── layout/          # Header, Footer
│   └── ui/              # shadcn-vue components
├── composables/         # Composables (useApi, useAnimal)
├── layouts/             # Page layouts
├── lib/                 # Utilities
├── pages/               # Routes (file-based routing)
├── public/              # Static files
└── types/               # TypeScript types
```

## Mobile-First Design

All components are built **mobile-first** using Tailwind's responsive utilities:

- Default styles apply to mobile (< 640px)
- `sm:` prefix for small tablets (≥ 640px)
- `md:` prefix for tablets (≥ 768px)
- `lg:` prefix for desktops (≥ 1024px)
- `xl:` prefix for large screens (≥ 1280px)

Example:
```vue
<!-- Mobile: full width, Desktop: half width -->
<div class="w-full lg:w-1/2">...</div>

<!-- Mobile: stacked, Desktop: grid -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3">...</div>
```

## Composables

### useApi

```typescript
// Basic fetch
const { data, error, pending } = await useApi<Animal>('/animals/123')

// With query params
const { data } = await useApi('/animals', {
  query: { species: 'dog', page: 1 }
})
```

### useAnimal

```typescript
// List animals with filters
const filters = ref({ species: Species.DOG })
const { data } = useAnimalList(filters, ref(1), ref(20))

// Get single animal
const { data: animal } = useAnimal('animal-id')

// Create/update
await createAnimal({ name: 'Rex', ... })
await updateAnimal('id', { name: 'New name' })
```

## Building for Production

```bash
npm run build
npm run preview
```

## Environment Variables

Create `.env` file:

```env
NUXT_PUBLIC_API_BASE=http://localhost/api
```

## Adding shadcn-vue Components

```bash
npx shadcn-vue@latest add button
npx shadcn-vue@latest add card
npx shadcn-vue@latest add input
```

Components will be added to `components/ui/`.

## SEO

- SSR enabled for better SEO
- Dynamic meta tags with `useSeoMeta()`
- Open Graph support for social sharing
- Semantic HTML for accessibility

## Responsive Testing

Test on multiple screen sizes:
- Mobile: 375px (iPhone SE)
- Tablet: 768px (iPad)
- Desktop: 1280px
