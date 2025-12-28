<script setup lang="ts">
import { Species, Size, Gender, type AnimalFilters } from '~/types'

interface Props {
  modelValue: AnimalFilters
}

interface Emits {
  (e: 'update:modelValue', value: AnimalFilters): void
  (e: 'close'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const speciesOptions = [
  { value: undefined, label: 'Todos' },
  { value: Species.DOG, label: 'Cachorro' },
  { value: Species.CAT, label: 'Gato' },
  { value: Species.RABBIT, label: 'Coelho' },
  { value: Species.HAMSTER, label: 'Hamster' },
  { value: Species.GUINEA_PIG, label: 'Porquinho-da-índia' },
  { value: Species.BIRD, label: 'Ave' },
  { value: Species.CHINCHILLA, label: 'Chinchila' },
  { value: Species.FISH, label: 'Peixe' },
]

const updateFilter = (key: keyof AnimalFilters, value: any) => {
  emit('update:modelValue', { ...props.modelValue, [key]: value || undefined })
}

const clearFilters = () => {
  emit('update:modelValue', {})
}

const hasActiveFilters = computed(() => {
  return Object.values(props.modelValue).some(v => v !== undefined && v !== null && v !== '')
})

const applyFilters = () => {
  emit('close')
}
</script>

<template>
  <div class="space-y-5">
    <!-- Species -->
    <div class="space-y-2">
      <label class="text-sm font-medium">Tipo de Animal</label>
      <select
        :value="modelValue.species || ''"
        class="w-full rounded-lg border border-input bg-background px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
        @change="updateFilter('species', ($event.target as HTMLSelectElement).value || undefined)"
      >
        <option v-for="option in speciesOptions" :key="option.label" :value="option.value || ''">
          {{ option.label }}
        </option>
      </select>
    </div>

    <!-- Size -->
    <div class="space-y-2">
      <label class="text-sm font-medium">Porte</label>
      <div class="flex flex-wrap gap-2">
        <button
          type="button"
          @click="updateFilter('size', undefined)"
          :class="[
            'px-4 py-2 rounded-full text-sm font-medium transition-colors',
            !modelValue.size
              ? 'bg-purple-600 text-white'
              : 'bg-muted text-foreground hover:bg-muted/80'
          ]"
        >
          Todos
        </button>
        <button
          type="button"
          @click="updateFilter('size', Size.SMALL)"
          :class="[
            'px-4 py-2 rounded-full text-sm font-medium transition-colors',
            modelValue.size === Size.SMALL
              ? 'bg-purple-600 text-white'
              : 'bg-muted text-foreground hover:bg-muted/80'
          ]"
        >
          Pequeno
        </button>
        <button
          type="button"
          @click="updateFilter('size', Size.MEDIUM)"
          :class="[
            'px-4 py-2 rounded-full text-sm font-medium transition-colors',
            modelValue.size === Size.MEDIUM
              ? 'bg-purple-600 text-white'
              : 'bg-muted text-foreground hover:bg-muted/80'
          ]"
        >
          Médio
        </button>
        <button
          type="button"
          @click="updateFilter('size', Size.LARGE)"
          :class="[
            'px-4 py-2 rounded-full text-sm font-medium transition-colors',
            modelValue.size === Size.LARGE
              ? 'bg-purple-600 text-white'
              : 'bg-muted text-foreground hover:bg-muted/80'
          ]"
        >
          Grande
        </button>
      </div>
    </div>

    <!-- Gender -->
    <div class="space-y-2">
      <label class="text-sm font-medium">Sexo</label>
      <div class="flex flex-wrap gap-2">
        <button
          type="button"
          @click="updateFilter('gender', undefined)"
          :class="[
            'px-4 py-2 rounded-full text-sm font-medium transition-colors',
            !modelValue.gender
              ? 'bg-purple-600 text-white'
              : 'bg-muted text-foreground hover:bg-muted/80'
          ]"
        >
          Todos
        </button>
        <button
          type="button"
          @click="updateFilter('gender', Gender.MALE)"
          :class="[
            'px-4 py-2 rounded-full text-sm font-medium transition-colors',
            modelValue.gender === Gender.MALE
              ? 'bg-purple-600 text-white'
              : 'bg-muted text-foreground hover:bg-muted/80'
          ]"
        >
          Macho
        </button>
        <button
          type="button"
          @click="updateFilter('gender', Gender.FEMALE)"
          :class="[
            'px-4 py-2 rounded-full text-sm font-medium transition-colors',
            modelValue.gender === Gender.FEMALE
              ? 'bg-purple-600 text-white'
              : 'bg-muted text-foreground hover:bg-muted/80'
          ]"
        >
          Fêmea
        </button>
      </div>
    </div>

    <!-- Location -->
    <div class="space-y-2">
      <label class="text-sm font-medium">Localização</label>
      <input
        :value="modelValue.location"
        type="text"
        placeholder="Cidade ou região"
        class="w-full rounded-lg border border-input bg-background px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
        @input="updateFilter('location', ($event.target as HTMLInputElement).value)"
      />
    </div>

    <!-- Action Buttons -->
    <div class="flex gap-3 pt-4 border-t">
      <button
        v-if="hasActiveFilters"
        type="button"
        @click="clearFilters"
        class="flex-1 px-4 py-3 rounded-lg border border-input font-medium hover:bg-muted transition-colors"
      >
        Limpar filtros
      </button>
      <button
        type="button"
        @click="applyFilters"
        class="flex-1 px-4 py-3 bg-purple-600 text-white rounded-lg font-medium hover:bg-purple-700 transition-colors"
      >
        Aplicar
      </button>
    </div>
  </div>
</template>
