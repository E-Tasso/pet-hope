<script setup lang="ts">
import type { Animal } from '~/types'

interface Props {
  animal: Animal
}

const props = defineProps<Props>()

// Format age
const ageDisplay = computed(() => {
  if (!props.animal.age_months) return 'Idade não informada'

  const months = props.animal.age_months
  if (months < 12) return `${months} ${months === 1 ? 'mês' : 'meses'}`

  const years = Math.floor(months / 12)
  const remainingMonths = months % 12

  if (remainingMonths === 0) return `${years} ${years === 1 ? 'ano' : 'anos'}`
  return `${years} ${years === 1 ? 'ano' : 'anos'} e ${remainingMonths} ${remainingMonths === 1 ? 'mês' : 'meses'}`
})

// Status badge
const statusConfig = computed(() => {
  const configs = {
    available: {
      label: 'Disponível para Adoção',
      color: 'bg-green-100 text-green-800 border-green-200',
      emoji: '✅',
    },
    in_process: {
      label: 'Processo de Adoção em Andamento',
      color: 'bg-yellow-100 text-yellow-800 border-yellow-200',
      emoji: '⏳',
    },
    adopted: {
      label: 'Já foi Adotado',
      color: 'bg-gray-100 text-gray-800 border-gray-200',
      emoji: '🏠',
    },
  }
  return configs[props.animal.status] || configs.available
})

// Species/Gender labels
const speciesLabel = computed(() => {
  const labels: Record<string, string> = {
    dog: 'Cão',
    cat: 'Gato',
    bird: 'Pássaro',
    rodent: 'Roedor',
    other: 'Outro',
  }
  return labels[props.animal.species] || 'Desconhecido'
})

const genderLabel = computed(() => {
  const labels: Record<string, string> = {
    male: 'Macho',
    female: 'Fêmea',
    unknown: 'Não informado',
  }
  return labels[props.animal.gender] || 'Não informado'
})

const sizeLabel = computed(() => {
  const labels: Record<string, string> = {
    small: 'Pequeno',
    medium: 'Médio',
    large: 'Grande',
  }
  return labels[props.animal.size] || 'Não informado'
})
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div>
      <h1 class="text-3xl font-bold tracking-tight sm:text-4xl">
        {{ animal.name }}
      </h1>
      <div class="mt-3 flex flex-wrap items-center gap-3">
        <!-- Status Badge -->
        <span
          :class="statusConfig.color"
          class="inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-sm font-semibold"
        >
          <span>{{ statusConfig.emoji }}</span>
          {{ statusConfig.label }}
        </span>
      </div>
    </div>

    <!-- Basic Info Grid -->
    <div class="grid gap-4 rounded-lg border bg-card p-4 sm:grid-cols-2 lg:grid-cols-4">
      <div>
        <div class="text-sm text-muted-foreground">Espécie</div>
        <div class="mt-1 font-medium">{{ speciesLabel }}</div>
      </div>
      <div>
        <div class="text-sm text-muted-foreground">Sexo</div>
        <div class="mt-1 font-medium">{{ genderLabel }}</div>
      </div>
      <div>
        <div class="text-sm text-muted-foreground">Porte</div>
        <div class="mt-1 font-medium">{{ sizeLabel }}</div>
      </div>
      <div>
        <div class="text-sm text-muted-foreground">Idade</div>
        <div class="mt-1 font-medium">{{ ageDisplay }}</div>
      </div>
      <div v-if="animal.breed">
        <div class="text-sm text-muted-foreground">Raça</div>
        <div class="mt-1 font-medium">{{ animal.breed }}</div>
      </div>
      <div>
        <div class="text-sm text-muted-foreground">Localização</div>
        <div class="mt-1 font-medium">{{ animal.location }}</div>
      </div>
    </div>

    <!-- Description -->
    <div class="space-y-3">
      <h2 class="text-xl font-semibold">Sobre {{ animal.name }}</h2>
      <p class="whitespace-pre-wrap text-muted-foreground leading-relaxed">
        {{ animal.description }}
      </p>
    </div>

    <!-- Traits -->
    <div v-if="animal.traits && animal.traits.length > 0" class="space-y-3">
      <h2 class="text-xl font-semibold">Características</h2>
      <div class="flex flex-wrap gap-2">
        <span
          v-for="trait in animal.traits"
          :key="trait"
          class="inline-flex items-center rounded-full border bg-secondary px-3 py-1 text-sm font-medium"
        >
          {{ trait }}
        </span>
      </div>
    </div>

    <!-- Special Needs -->
    <div v-if="animal.special_needs" class="space-y-3">
      <h2 class="text-xl font-semibold">Necessidades Especiais</h2>
      <div class="rounded-lg border border-yellow-200 bg-yellow-50 p-4 dark:border-yellow-800 dark:bg-yellow-950">
        <p class="text-sm text-yellow-900 dark:text-yellow-100">
          {{ animal.special_needs }}
        </p>
      </div>
    </div>

    <!-- Contact Info -->
    <div class="space-y-3">
      <h2 class="text-xl font-semibold">Informações de Contato</h2>
      <div class="rounded-lg border bg-card p-6">
        <p class="mb-4 text-sm text-muted-foreground">
          Interessado em adotar {{ animal.name }}? Entre em contato:
        </p>
        <div class="space-y-2">
          <div v-for="(value, key) in animal.contact_info" :key="key" class="flex items-start gap-3">
            <span class="text-xl">
              {{ key === 'phone' ? '📞' : key === 'email' ? '📧' : key === 'whatsapp' ? '💬' : '📱' }}
            </span>
            <div>
              <div class="text-sm font-medium capitalize">{{ key }}</div>
              <div class="text-muted-foreground">{{ value }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Back Button -->
    <div class="pt-6">
      <NuxtLink
        to="/"
        class="inline-flex items-center gap-2 text-sm font-medium text-primary hover:underline"
      >
        <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
        Voltar para o início
      </NuxtLink>
    </div>
  </div>
</template>
