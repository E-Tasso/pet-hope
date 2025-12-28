<script setup lang="ts">
import type { Image } from '~/types'

interface Props {
  images: Image[]
  animalName: string
}

const props = defineProps<Props>()

const selectedImage = ref(0)

const selectImage = (index: number) => {
  selectedImage.value = index
}

const nextImage = () => {
  selectedImage.value = (selectedImage.value + 1) % props.images.length
}

const prevImage = () => {
  selectedImage.value = (selectedImage.value - 1 + props.images.length) % props.images.length
}

// Sort images (primary first, then by order)
const sortedImages = computed(() => {
  return [...props.images].sort((a, b) => {
    if (a.is_primary && !b.is_primary) return -1
    if (!a.is_primary && b.is_primary) return 1
    return a.order - b.order
  })
})
</script>

<template>
  <div v-if="sortedImages.length > 0" class="space-y-4">
    <!-- Main Image -->
    <div class="relative aspect-square overflow-hidden rounded-lg border bg-muted md:aspect-video">
      <img
        :src="sortedImages[selectedImage].original_url"
        :alt="`${animalName} - Imagem ${selectedImage + 1}`"
        class="h-full w-full object-cover"
      />

      <!-- Navigation Arrows (desktop) -->
      <div v-if="sortedImages.length > 1" class="absolute inset-0 flex items-center justify-between p-4">
        <button
          class="hidden rounded-full bg-black/50 p-2 text-white backdrop-blur transition-colors hover:bg-black/70 md:block"
          @click="prevImage"
        >
          <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
        </button>
        <button
          class="hidden rounded-full bg-black/50 p-2 text-white backdrop-blur transition-colors hover:bg-black/70 md:block"
          @click="nextImage"
        >
          <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
        </button>
      </div>

      <!-- Image Counter -->
      <div class="absolute bottom-4 right-4 rounded-full bg-black/50 px-3 py-1 text-sm text-white backdrop-blur">
        {{ selectedImage + 1 }} / {{ sortedImages.length }}
      </div>
    </div>

    <!-- Thumbnails -->
    <div v-if="sortedImages.length > 1" class="grid grid-cols-4 gap-2 sm:grid-cols-6 md:grid-cols-8">
      <button
        v-for="(image, index) in sortedImages"
        :key="image.id"
        class="relative aspect-square overflow-hidden rounded-md border-2 transition-all"
        :class="[
          selectedImage === index
            ? 'border-primary ring-2 ring-primary ring-offset-2'
            : 'border-transparent hover:border-muted-foreground/50',
        ]"
        @click="selectImage(index)"
      >
        <img
          :src="image.thumbnail_url"
          :alt="`${animalName} - Miniatura ${index + 1}`"
          class="h-full w-full object-cover"
        />
        <div
          v-if="image.is_primary"
          class="absolute right-1 top-1 rounded-full bg-primary px-1.5 py-0.5 text-[10px] font-semibold text-primary-foreground"
        >
          Principal
        </div>
      </button>
    </div>
  </div>

  <!-- No Images Placeholder -->
  <div v-else class="flex aspect-square items-center justify-center rounded-lg border bg-muted md:aspect-video">
    <div class="text-center">
      <div class="text-6xl mb-3">🐾</div>
      <p class="text-sm text-muted-foreground">Sem imagens disponíveis</p>
    </div>
  </div>
</template>
