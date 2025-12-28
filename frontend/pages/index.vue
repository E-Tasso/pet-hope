<script setup lang="ts">
useSeoMeta({
  title: 'PetHope - Adote um Pet',
  description: 'Encontre seu novo melhor amigo. Plataforma de adocao de animais.',
})

const { animals, loading, hasMore, loadMore } = useAnimalFeed(10)

const loadMoreRef = ref<HTMLElement | null>(null)
let observer: IntersectionObserver | null = null

// Load initial data and set up infinite scroll
onMounted(async () => {
  await loadMore()

  // Set up intersection observer for infinite scroll
  if (loadMoreRef.value) {
    observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && hasMore.value && !loading.value) {
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
  <div class="min-h-screen bg-background">
    <!-- Feed Container -->
    <div class="mx-auto max-w-lg py-4">
      <!-- Feed -->
      <div class="space-y-0">
        <FeedCard
          v-for="animal in animals"
          :key="animal.id"
          :animal="animal"
        />
      </div>

      <!-- Loading Spinner -->
      <div
        v-if="loading"
        class="flex justify-center py-8"
      >
        <div class="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>

      <!-- Load More Trigger -->
      <div
        ref="loadMoreRef"
        class="h-10"
      />

      <!-- Empty State -->
      <div
        v-if="!loading && animals.length === 0"
        class="py-16 text-center"
      >
        <div class="text-6xl">🐾</div>
        <h2 class="mt-4 text-xl font-semibold text-foreground">
          Nenhum animal disponivel
        </h2>
        <p class="mt-2 text-muted-foreground">
          Volte em breve para ver novos pets
        </p>
      </div>

      <!-- End of Feed -->
      <div
        v-if="!hasMore && animals.length > 0"
        class="py-8 text-center text-sm text-muted-foreground"
      >
        Voce viu todos os animais disponiveis
      </div>
    </div>
  </div>
</template>
