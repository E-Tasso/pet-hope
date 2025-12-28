<script setup lang="ts">
import type { AnimalFeedItem } from '~/types'

interface Props {
  animal: AnimalFeedItem
}

const props = defineProps<Props>()

const ageDisplay = computed(() => {
  if (!props.animal.age_months) return null

  const months = props.animal.age_months
  if (months < 12) return `${months} ${months === 1 ? 'mes' : 'meses'}`

  const years = Math.floor(months / 12)
  const remainingMonths = months % 12

  if (remainingMonths === 0) return `${years} ${years === 1 ? 'ano' : 'anos'}`
  return `${years}a ${remainingMonths}m`
})

const speciesLabel = computed(() => {
  const labels: Record<string, string> = {
    dog: 'Cachorro',
    cat: 'Gato',
    bird: 'Passaro',
    rodent: 'Roedor',
    other: 'Outro',
  }
  return labels[props.animal.species] || 'Animal'
})

const genderLabel = computed(() => {
  if (props.animal.gender === 'male') return 'Macho'
  if (props.animal.gender === 'female') return 'Femea'
  return null
})

const sizeLabel = computed(() => {
  const labels: Record<string, string> = {
    small: 'Pequeno',
    medium: 'Medio',
    large: 'Grande',
  }
  return labels[props.animal.size] || null
})

const truncatedDescription = computed(() => {
  const maxLength = 120
  if (props.animal.description.length <= maxLength) {
    return props.animal.description
  }
  return props.animal.description.slice(0, maxLength).trim() + '...'
})
</script>

<template>
  <article class="overflow-hidden bg-card border-b border-border">
    <!-- Image Carousel -->
    <FeedCarousel :images="animal.images" />

    <!-- Actions -->
    <div class="flex items-center justify-between px-4 pt-3">
      <FeedShareButton :animal-id="animal.id" :animal-name="animal.name" />
    </div>

    <!-- Content -->
    <div class="px-4 pb-3">
      <!-- Line 1: Name, Location, Tags -->
      <div class="flex flex-wrap items-center gap-x-2 gap-y-1">
        <NuxtLink
          :to="`/animais/${animal.id}`"
          class="font-semibold text-foreground hover:text-primary"
        >
          {{ animal.name }}
        </NuxtLink>
        <span class="text-muted-foreground">·</span>
        <span class="text-sm text-muted-foreground">{{ animal.location }}</span>
        <span class="text-muted-foreground">·</span>
        <span class="rounded-full bg-muted px-2 py-0.5 text-xs text-muted-foreground">
          {{ speciesLabel }}
        </span>
        <span v-if="ageDisplay" class="rounded-full bg-muted px-2 py-0.5 text-xs text-muted-foreground">
          {{ ageDisplay }}
        </span>
        <span v-if="genderLabel" class="rounded-full bg-muted px-2 py-0.5 text-xs text-muted-foreground">
          {{ genderLabel }}
        </span>
        <span v-if="sizeLabel" class="rounded-full bg-muted px-2 py-0.5 text-xs text-muted-foreground">
          {{ sizeLabel }}
        </span>
      </div>

      <!-- Line 2: Description + Ver mais -->
      <p class="mt-2 text-sm text-foreground/80">
        {{ truncatedDescription }}
        <NuxtLink
          :to="`/animais/${animal.id}`"
          class="ml-1 font-medium text-primary hover:underline"
        >
          ver mais
        </NuxtLink>
      </p>
    </div>
  </article>
</template>
