<script setup lang="ts">
import { Species, Size, Gender, AnimalStatus, type AnimalFilters } from '~/types'

interface Props {
  modelValue: AnimalFilters
}

interface Emits {
  (e: 'update:modelValue', value: AnimalFilters): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const filters = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value),
})

const updateFilter = (key: keyof AnimalFilters, value: any) => {
  emit('update:modelValue', { ...props.modelValue, [key]: value || undefined })
}

const clearFilters = () => {
  emit('update:modelValue', {})
}

const hasActiveFilters = computed(() => {
  return Object.values(props.modelValue).some(v => v !== undefined && v !== null && v !== '')
})

// Mobile filter drawer
const mobileFiltersOpen = ref(false)
</script>

<template>
  <div>
    <!-- Mobile: Filter Button -->
    <button
      class="mb-4 flex w-full items-center justify-between rounded-lg border bg-card p-4 md:hidden"
      @click="mobileFiltersOpen = !mobileFiltersOpen"
    >
      <span class="font-medium">Filtros</span>
      <svg
        class="h-5 w-5 transition-transform"
        :class="{ 'rotate-180': mobileFiltersOpen }"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
      </svg>
    </button>

    <!-- Filters Container -->
    <div
      class="space-y-6 rounded-lg border bg-card p-4 md:p-6"
      :class="{ 'hidden md:block': !mobileFiltersOpen }"
    >
      <div class="flex items-center justify-between">
        <h3 class="font-semibold">Filtros</h3>
        <button
          v-if="hasActiveFilters"
          class="text-sm text-primary hover:underline"
          @click="clearFilters"
        >
          Limpar
        </button>
      </div>

      <!-- Search -->
      <div class="space-y-2">
        <label class="text-sm font-medium">Buscar</label>
        <input
          :value="filters.search"
          type="text"
          placeholder="Nome ou descrição"
          class="w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
          @input="updateFilter('search', ($event.target as HTMLInputElement).value)"
        />
      </div>

      <!-- Species -->
      <div class="space-y-2">
        <label class="text-sm font-medium">Espécie</label>
        <select
          :value="filters.species"
          class="w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
          @change="updateFilter('species', ($event.target as HTMLSelectElement).value as Species)"
        >
          <option value="">Todas</option>
          <option :value="Species.DOG">🐕 Cão</option>
          <option :value="Species.CAT">🐈 Gato</option>
          <option :value="Species.BIRD">🐦 Pássaro</option>
          <option :value="Species.RODENT">🐹 Roedor</option>
          <option :value="Species.OTHER">🐾 Outro</option>
        </select>
      </div>

      <!-- Size -->
      <div class="space-y-2">
        <label class="text-sm font-medium">Porte</label>
        <select
          :value="filters.size"
          class="w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
          @change="updateFilter('size', ($event.target as HTMLSelectElement).value as Size)"
        >
          <option value="">Todos</option>
          <option :value="Size.SMALL">Pequeno</option>
          <option :value="Size.MEDIUM">Médio</option>
          <option :value="Size.LARGE">Grande</option>
        </select>
      </div>

      <!-- Gender -->
      <div class="space-y-2">
        <label class="text-sm font-medium">Sexo</label>
        <select
          :value="filters.gender"
          class="w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
          @change="updateFilter('gender', ($event.target as HTMLSelectElement).value as Gender)"
        >
          <option value="">Todos</option>
          <option :value="Gender.MALE">♂️ Macho</option>
          <option :value="Gender.FEMALE">♀️ Fêmea</option>
          <option :value="Gender.UNKNOWN">⚪ Indefinido</option>
        </select>
      </div>

      <!-- Location -->
      <div class="space-y-2">
        <label class="text-sm font-medium">Localização</label>
        <input
          :value="filters.location"
          type="text"
          placeholder="Cidade ou região"
          class="w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
          @input="updateFilter('location', ($event.target as HTMLInputElement).value)"
        />
      </div>

      <!-- Age Range -->
      <div class="space-y-2">
        <label class="text-sm font-medium">Idade (meses)</label>
        <div class="grid grid-cols-2 gap-2">
          <input
            :value="filters.min_age_months"
            type="number"
            placeholder="Mín"
            min="0"
            class="w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
            @input="updateFilter('min_age_months', parseInt(($event.target as HTMLInputElement).value) || undefined)"
          />
          <input
            :value="filters.max_age_months"
            type="number"
            placeholder="Máx"
            min="0"
            class="w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
            @input="updateFilter('max_age_months', parseInt(($event.target as HTMLInputElement).value) || undefined)"
          />
        </div>
      </div>
    </div>
  </div>
</template>
