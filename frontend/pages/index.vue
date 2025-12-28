<script setup lang="ts">
import type { AnimalFilters, AnimalFeedItem, PaginatedResponse } from '~/types'

useSeoMeta({
  title: 'PetHope - Adote um Pet',
  description: 'Encontre seu novo melhor amigo. Plataforma de adocao de animais.',
})

// Filters
const filters = ref<AnimalFilters>({})
const showFilters = ref(false)

// Pagination state
const page = ref(1)
const pageSize = 10
const additionalAnimals = ref<AnimalFeedItem[]>([])
const isLoadingMore = ref(false)

// Build query params for filters
function buildQueryParams() {
  const params: Record<string, any> = {
    page: 1,
    page_size: pageSize,
  }
  Object.entries(filters.value).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      params[key] = value
    }
  })
  return params
}

// Initial fetch using useAsyncData with fixed key for SSR
const { data, pending, error, refresh } = await useAsyncData(
  'animals-feed',
  () => $fetch<PaginatedResponse<AnimalFeedItem>>('/animals/feed', {
    baseURL: getApiBase(),
    query: buildQueryParams(),
  }),
  {
    watch: [filters],
    deep: true,
  }
)

// Track if there are more pages
const hasMore = computed(() => {
  if (!data.value) return true
  const totalPages = data.value.pages
  const loadedPages = 1 + Math.floor(additionalAnimals.value.length / pageSize)
  return loadedPages < totalPages
})

// Reset additional animals when filters change
watch(filters, () => {
  page.value = 1
  additionalAnimals.value = []
}, { deep: true })

// Load more function
async function loadMore() {
  if (isLoadingMore.value || !hasMore.value || pending.value) return

  isLoadingMore.value = true
  const nextPage = page.value + 1

  try {
    const response = await $fetch<PaginatedResponse<AnimalFeedItem>>('/animals/feed', {
      baseURL: getApiBase(),
      query: {
        page: nextPage,
        page_size: pageSize,
        ...Object.fromEntries(
          Object.entries(filters.value).filter(([_, v]) => v !== undefined && v !== null && v !== '')
        ),
      },
    })

    if (response.items.length > 0) {
      additionalAnimals.value = [...additionalAnimals.value, ...response.items]
      page.value = nextPage
    }
  } catch (e) {
    console.error('Error loading more animals:', e)
  } finally {
    isLoadingMore.value = false
  }
}

// Count active filters
const activeFiltersCount = computed(() => {
  return Object.values(filters.value).filter(v => v !== undefined && v !== null && v !== '').length
})

// Infinite scroll
const loadMoreRef = ref<HTMLElement | null>(null)
let observer: IntersectionObserver | null = null

onMounted(() => {
  if (loadMoreRef.value) {
    observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && hasMore.value && !pending.value && !isLoadingMore.value) {
          loadMore()
        }
      },
      { threshold: 0.1 }
    )
    observer.observe(loadMoreRef.value)
  }
})

onUnmounted(() => {
  observer?.disconnect()
})
</script>

<template>
  <div class="min-h-screen bg-background pb-24">
    <!-- Feed Container -->
    <div class="mx-auto max-w-lg py-4">
      <!-- Error State -->
      <div v-if="error" class="mx-4 rounded-lg border border-destructive bg-destructive/10 p-6 text-center">
        <div class="text-4xl mb-3">⚠️</div>
        <h3 class="font-semibold text-destructive">Erro ao carregar animais</h3>
        <p class="mt-2 text-sm text-muted-foreground">
          Não foi possível conectar ao servidor. Tente novamente mais tarde.
        </p>
      </div>

      <!-- Feed -->
      <div v-else class="space-y-0">
        <!-- First page from SSR data -->
        <FeedCard
          v-for="animal in (data?.items || [])"
          :key="animal.id"
          :animal="animal"
        />
        <!-- Additional pages from infinite scroll -->
        <FeedCard
          v-for="animal in additionalAnimals"
          :key="'extra-' + animal.id"
          :animal="animal"
        />
      </div>

      <!-- Loading Spinner -->
      <div v-if="pending || isLoadingMore" class="flex justify-center py-8">
        <div class="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>

      <!-- Load More Trigger -->
      <div ref="loadMoreRef" class="h-10" />

      <!-- Empty State -->
      <div v-if="!pending && (data?.items?.length || 0) === 0" class="py-16 text-center">
        <div class="text-6xl">🐾</div>
        <h2 class="mt-4 text-xl font-semibold text-foreground">
          Nenhum animal disponível
        </h2>
        <p class="mt-2 text-muted-foreground">
          {{ activeFiltersCount > 0 ? 'Tente ajustar os filtros' : 'Volte em breve para ver novos pets' }}
        </p>
      </div>

      <!-- End of Feed -->
      <div v-if="!hasMore && (data?.items?.length || 0) > 0" class="py-8 text-center text-sm text-muted-foreground">
        Você viu todos os animais disponíveis
      </div>
    </div>

    <!-- Filter Sheet/Modal (client-only to avoid hydration mismatch) -->
    <ClientOnly>
      <Teleport to="body">
        <Transition name="fade">
          <div
            v-if="showFilters"
            class="fixed inset-0 bg-black/50 z-40"
            @click="showFilters = false"
          />
        </Transition>
        <Transition name="slide-up">
          <div
            v-if="showFilters"
            class="fixed bottom-0 left-0 right-0 bg-background rounded-t-2xl z-50 max-h-[80vh] overflow-y-auto"
          >
            <div class="sticky top-0 bg-background p-4 border-b flex items-center justify-between">
              <h3 class="font-semibold text-lg">Filtros</h3>
              <button
                @click="showFilters = false"
                class="p-2 hover:bg-muted rounded-full"
              >
                <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div class="p-4">
              <AnimalFiltersSheet v-model="filters" @close="showFilters = false" />
            </div>
          </div>
        </Transition>
      </Teleport>

      <!-- Floating Menu -->
      <div class="fixed bottom-6 left-1/2 -translate-x-1/2 z-30">
        <div class="flex items-center gap-3 bg-background/70 backdrop-blur-lg rounded-full px-2 py-2 shadow-lg border border-border/40">
          <!-- Filter Button -->
          <button
            @click="showFilters = true"
            class="relative flex items-center gap-2 px-4 py-2.5 rounded-full hover:bg-muted/60 transition-colors"
          >
            <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
            </svg>
            <span class="font-medium">Filtros</span>
            <span
              v-if="activeFiltersCount > 0"
              class="absolute -top-1 -right-1 w-5 h-5 bg-purple-600 text-white text-xs rounded-full flex items-center justify-center"
            >
              {{ activeFiltersCount }}
            </span>
          </button>

          <!-- Divider -->
          <div class="w-px h-8 bg-border/40"></div>

          <!-- Add Button -->
          <NuxtLink
            to="/animais/novo"
            class="flex items-center gap-2 px-4 py-2.5 bg-purple-600 text-white rounded-full font-medium hover:bg-purple-700 transition-colors"
          >
            <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            <span>Adicionar</span>
          </NuxtLink>
        </div>
      </div>
    </ClientOnly>
  </div>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-up-enter-active,
.slide-up-leave-active {
  transition: transform 0.3s ease;
}

.slide-up-enter-from,
.slide-up-leave-to {
  transform: translateY(100%);
}
</style>
