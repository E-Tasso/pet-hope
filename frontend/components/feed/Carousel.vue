<script setup lang="ts">
import type { Image } from '~/types'

interface Props {
  images: Image[]
}

const props = defineProps<Props>()

const currentIndex = ref(0)
const containerRef = ref<HTMLElement | null>(null)

const hasMultipleImages = computed(() => props.images.length > 1)

function goTo(index: number) {
  if (index >= 0 && index < props.images.length) {
    currentIndex.value = index
    scrollToIndex(index)
  }
}

function next() {
  if (currentIndex.value < props.images.length - 1) {
    goTo(currentIndex.value + 1)
  }
}

function prev() {
  if (currentIndex.value > 0) {
    goTo(currentIndex.value - 1)
  }
}

function scrollToIndex(index: number) {
  if (containerRef.value) {
    const scrollAmount = containerRef.value.offsetWidth * index
    containerRef.value.scrollTo({
      left: scrollAmount,
      behavior: 'smooth',
    })
  }
}

function handleScroll() {
  if (containerRef.value) {
    const scrollLeft = containerRef.value.scrollLeft
    const width = containerRef.value.offsetWidth
    const newIndex = Math.round(scrollLeft / width)
    if (newIndex !== currentIndex.value) {
      currentIndex.value = newIndex
    }
  }
}

const speciesEmoji = computed(() => {
  return '🐾'
})
</script>

<template>
  <div class="relative aspect-square bg-muted overflow-hidden">
    <!-- Images Container -->
    <div
      v-if="images.length > 0"
      ref="containerRef"
      class="flex h-full w-full snap-x snap-mandatory overflow-x-auto scrollbar-hide"
      @scroll="handleScroll"
    >
      <div
        v-for="(image, index) in images"
        :key="image.id"
        class="h-full w-full flex-shrink-0 snap-center"
      >
        <img
          :src="image.original_url"
          :alt="`Foto ${index + 1}`"
          class="h-full w-full object-cover"
          loading="lazy"
        />
      </div>
    </div>

    <!-- Empty State -->
    <div
      v-else
      class="flex h-full w-full items-center justify-center text-6xl"
    >
      {{ speciesEmoji }}
    </div>

    <!-- Navigation Arrows -->
    <template v-if="hasMultipleImages">
      <button
        v-if="currentIndex > 0"
        type="button"
        class="absolute left-2 top-1/2 -translate-y-1/2 flex h-8 w-8 items-center justify-center rounded-full bg-black/50 text-white transition-opacity hover:bg-black/70"
        @click="prev"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clip-rule="evenodd" />
        </svg>
      </button>
      <button
        v-if="currentIndex < images.length - 1"
        type="button"
        class="absolute right-2 top-1/2 -translate-y-1/2 flex h-8 w-8 items-center justify-center rounded-full bg-black/50 text-white transition-opacity hover:bg-black/70"
        @click="next"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
        </svg>
      </button>
    </template>

    <!-- Dot Indicators -->
    <div
      v-if="hasMultipleImages"
      class="absolute bottom-3 left-1/2 flex -translate-x-1/2 gap-1.5"
    >
      <button
        v-for="(_, index) in images"
        :key="index"
        type="button"
        class="h-2 w-2 rounded-full transition-all"
        :class="index === currentIndex ? 'bg-white scale-110' : 'bg-white/50'"
        @click="goTo(index)"
      />
    </div>

    <!-- Image Counter -->
    <div
      v-if="hasMultipleImages"
      class="absolute right-3 top-3 rounded-full bg-black/50 px-2 py-0.5 text-xs font-medium text-white"
    >
      {{ currentIndex + 1 }}/{{ images.length }}
    </div>
  </div>
</template>

<style scoped>
.scrollbar-hide {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
.scrollbar-hide::-webkit-scrollbar {
  display: none;
}
</style>
