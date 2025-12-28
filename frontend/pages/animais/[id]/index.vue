<script setup lang="ts">
const route = useRoute()
const animalId = computed(() => route.params.id as string)

// Fetch animal
const { data: animal, pending, error } = useAnimal(animalId)

// SEO - Dynamic meta tags
useSeoMeta({
  title: () => animal.value ? `${animal.value.name} - Adote | PetHope` : 'Animal - PetHope',
  description: () => {
    if (!animal.value) return 'Adote um pet'
    const species = animal.value.species === 'dog' ? 'Cão' : animal.value.species === 'cat' ? 'Gato' : 'Animal'
    return `${species} para adoção em ${animal.value.location}. ${animal.value.description.substring(0, 150)}...`
  },
  ogTitle: () => animal.value ? `Adote ${animal.value.name}` : 'Adote um pet',
  ogDescription: () => animal.value?.description.substring(0, 200),
  ogImage: () => animal.value?.images[0]?.original_url,
})
</script>

<template>
  <div class="container py-8 md:py-12">
    <!-- Loading State -->
    <div v-if="pending" class="flex min-h-[60vh] items-center justify-center">
      <div class="text-center">
        <CommonLoadingSpinner size="lg" class="mx-auto" />
        <p class="mt-4 text-sm text-muted-foreground">Carregando...</p>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error || !animal" class="flex min-h-[60vh] items-center justify-center">
      <div class="text-center">
        <div class="text-6xl mb-4">😢</div>
        <h2 class="text-2xl font-bold">Animal não encontrado</h2>
        <p class="mt-2 text-muted-foreground">
          O animal que você procura não existe ou foi removido.
        </p>
        <NuxtLink
          to="/"
          class="mt-6 inline-flex items-center justify-center rounded-md bg-primary px-6 py-3 text-sm font-medium text-primary-foreground shadow transition-colors hover:bg-primary/90"
        >
          Ver outros animais
        </NuxtLink>
      </div>
    </div>

    <!-- Animal Details -->
    <div v-else>
      <!-- Edit Button -->
      <div class="mb-4 flex justify-end">
        <NuxtLink
          :to="`/animais/${animal.id}/editar`"
          class="inline-flex items-center gap-2 rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
        >
          <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
          </svg>
          Editar cadastro
        </NuxtLink>
      </div>

      <div class="grid gap-8 lg:grid-cols-2">
        <!-- Gallery -->
        <div class="lg:sticky lg:top-20 lg:self-start">
          <AnimalGallery :images="animal.images" :animal-name="animal.name" />
        </div>

        <!-- Details -->
        <div>
          <AnimalDetails :animal="animal" />
        </div>
      </div>
    </div>
  </div>
</template>
