<script setup lang="ts">
import type { AnimalListItem } from '~/types'

interface Props {
  animal: AnimalListItem
}

const props = defineProps<Props>()

// Format age display
const ageDisplay = computed(() => {
  if (!props.animal.age_months) return 'Idade não informada'

  const months = props.animal.age_months
  if (months < 12) return `${months} ${months === 1 ? 'mês' : 'meses'}`

  const years = Math.floor(months / 12)
  const remainingMonths = months % 12

  if (remainingMonths === 0) return `${years} ${years === 1 ? 'ano' : 'anos'}`
  return `${years}a ${remainingMonths}m`
})

// Species emoji
const speciesEmoji = computed(() => {
  const emojis: Record<string, string> = {
    dog: '🐕',
    cat: '🐈',
    bird: '🐦',
    rodent: '🐹',
    other: '🐾',
  }
  return emojis[props.animal.species] || '🐾'
})

// Status badge color
const statusColor = computed(() => {
  const colors: Record<string, string> = {
    available: 'bg-green-100 text-green-800 border-green-200',
    in_process: 'bg-yellow-100 text-yellow-800 border-yellow-200',
    adopted: 'bg-gray-100 text-gray-800 border-gray-200',
  }
  return colors[props.animal.status] || colors.available
})

const statusLabel = computed(() => {
  const labels: Record<string, string> = {
    available: 'Disponível',
    in_process: 'Em processo',
    adopted: 'Adotado',
  }
  return labels[props.animal.status] || 'Disponível'
})
</script>

<template>
  <NuxtLink
    :to="`/animais/${animal.id}`"
    class="group block overflow-hidden rounded-lg border bg-card shadow-sm transition-all hover:shadow-md"
  >
    <!-- Image -->
    <div class="relative aspect-square overflow-hidden bg-muted">
      <img
        v-if="animal.primary_image"
        :src="animal.primary_image.thumbnail_url"
        :alt="animal.name"
        class="h-full w-full object-cover transition-transform group-hover:scale-105"
        loading="lazy"
      />
      <div
        v-else
        class="flex h-full w-full items-center justify-center text-6xl"
      >
        {{ speciesEmoji }}
      </div>

      <!-- Status Badge -->
      <div class="absolute right-2 top-2">
        <span
          :class="statusColor"
          class="inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold"
        >
          {{ statusLabel }}
        </span>
      </div>
    </div>

    <!-- Content -->
    <div class="p-4">
      <!-- Name -->
      <h3 class="text-lg font-semibold group-hover:text-primary">
        {{ animal.name }}
      </h3>

      <!-- Info -->
      <div class="mt-2 space-y-1 text-sm text-muted-foreground">
        <div class="flex items-center gap-2">
          <span>{{ speciesEmoji }}</span>
          <span class="capitalize">{{ animal.species }}</span>
        </div>
        <div class="flex items-center gap-2">
          <span>📍</span>
          <span>{{ animal.location }}</span>
        </div>
        <div class="flex items-center gap-2">
          <span>🎂</span>
          <span>{{ ageDisplay }}</span>
        </div>
        <div class="flex items-center gap-2">
          <span v-if="animal.gender === 'male'">♂️</span>
          <span v-else-if="animal.gender === 'female'">♀️</span>
          <span v-else>⚪</span>
          <span class="capitalize">{{ animal.gender === 'male' ? 'Macho' : animal.gender === 'female' ? 'Fêmea' : 'Indefinido' }}</span>
        </div>
      </div>
    </div>
  </NuxtLink>
</template>
