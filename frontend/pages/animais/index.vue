<script setup lang="ts">
import type { AnimalFilters } from '~/types'

// SEO
useSeoMeta({
  title: 'Animais para Adoção - PetHope',
  description: 'Encontre seu novo pet. Veja todos os animais disponíveis para adoção.',
})

// State
const filters = ref<AnimalFilters>({})
const page = ref(1)
const pageSize = ref(12)

// Fetch animals
const { data, pending, error } = useAnimalList(filters, page, pageSize)

// Scroll to top when page changes
watch(page, () => {
  window.scrollTo({ top: 0, behavior: 'smooth' })
})

// Reset page when filters change
watch(filters, () => {
  page.value = 1
}, { deep: true })
</script>

<template>
  <div class="container py-8 md:py-12">
    <!-- Header -->
    <div class="mb-8 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h1 class="text-3xl font-bold tracking-tight sm:text-4xl">
          Animais para Adoção
        </h1>
        <p class="mt-2 text-muted-foreground">
          Encontre seu novo melhor amigo
        </p>
      </div>
      <NuxtLink
        to="/animais/novo"
        class="inline-flex items-center justify-center gap-2 px-6 py-3 bg-purple-600 text-white rounded-lg font-medium hover:bg-purple-700 transition-colors"
      >
        <span class="text-lg">+</span>
        Cadastrar Animal
      </NuxtLink>
    </div>

    <!-- Error State -->
    <div v-if="error" class="rounded-lg border border-destructive bg-destructive/10 p-6 text-center">
      <div class="text-4xl mb-3">⚠️</div>
      <h3 class="font-semibold text-destructive">Erro ao carregar animais</h3>
      <p class="mt-2 text-sm text-muted-foreground">
        Não foi possível conectar ao servidor. Tente novamente mais tarde.
      </p>
    </div>

    <!-- Main Content -->
    <div v-else class="grid gap-8 lg:grid-cols-[280px_1fr]">
      <!-- Filters Sidebar -->
      <aside class="lg:sticky lg:top-20 lg:self-start">
        <AnimalFilters v-model="filters" />
      </aside>

      <!-- Animals Grid -->
      <main>
        <!-- Results Count -->
        <div v-if="data && !pending" class="mb-6 flex items-center justify-between">
          <p class="text-sm text-muted-foreground">
            {{ data.total }} {{ data.total === 1 ? 'animal encontrado' : 'animais encontrados' }}
          </p>
        </div>

        <!-- Grid -->
        <AnimalGrid :animals="data?.items || []" :loading="pending" />

        <!-- Pagination -->
        <div v-if="data && data.pages > 1" class="mt-8">
          <CommonPagination
            :current-page="page"
            :total-pages="data.pages"
            :total="data.total"
            @update:page="page = $event"
          />
        </div>
      </main>
    </div>
  </div>
</template>
