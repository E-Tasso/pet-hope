<script setup lang="ts">
import type { AnimalListItem } from '~/types'

interface Props {
  animals: AnimalListItem[]
  loading?: boolean
}

defineProps<Props>()
</script>

<template>
  <div>
    <!-- Loading State -->
    <div v-if="loading" class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
      <div
        v-for="i in 6"
        :key="i"
        class="animate-pulse overflow-hidden rounded-lg border bg-card"
      >
        <div class="aspect-square bg-muted"></div>
        <div class="p-4 space-y-3">
          <div class="h-6 bg-muted rounded"></div>
          <div class="h-4 bg-muted rounded w-3/4"></div>
          <div class="h-4 bg-muted rounded w-1/2"></div>
        </div>
      </div>
    </div>

    <!-- Animals Grid -->
    <div
      v-else-if="animals.length > 0"
      class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3"
    >
      <AnimalCard v-for="animal in animals" :key="animal.id" :animal="animal" />
    </div>

    <!-- Empty State -->
    <div v-else class="py-12 text-center">
      <div class="text-6xl mb-4">🐾</div>
      <h3 class="text-lg font-semibold text-foreground">
        Nenhum animal encontrado
      </h3>
      <p class="mt-2 text-sm text-muted-foreground">
        Tente ajustar os filtros de busca
      </p>
    </div>
  </div>
</template>
