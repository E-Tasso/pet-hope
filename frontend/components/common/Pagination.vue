<script setup lang="ts">
interface Props {
  currentPage: number
  totalPages: number
  total: number
}

interface Emits {
  (e: 'update:page', page: number): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const goToPage = (page: number) => {
  if (page >= 1 && page <= props.totalPages && page !== props.currentPage) {
    emit('update:page', page)
  }
}

// Calculate page range to show
const pageRange = computed(() => {
  const range: (number | string)[] = []
  const delta = 1 // Pages to show on each side of current

  if (props.totalPages <= 7) {
    // Show all pages if 7 or fewer
    for (let i = 1; i <= props.totalPages; i++) {
      range.push(i)
    }
  } else {
    // Always show first page
    range.push(1)

    // Calculate start and end of visible range
    let start = Math.max(2, props.currentPage - delta)
    let end = Math.min(props.totalPages - 1, props.currentPage + delta)

    // Add ellipsis after first page if needed
    if (start > 2) {
      range.push('...')
    }

    // Add visible page numbers
    for (let i = start; i <= end; i++) {
      range.push(i)
    }

    // Add ellipsis before last page if needed
    if (end < props.totalPages - 1) {
      range.push('...')
    }

    // Always show last page
    range.push(props.totalPages)
  }

  return range
})
</script>

<template>
  <div v-if="totalPages > 1" class="flex flex-col items-center gap-4 sm:flex-row sm:justify-between">
    <!-- Info -->
    <div class="text-sm text-muted-foreground">
      Página {{ currentPage }} de {{ totalPages }} ({{ total }} {{ total === 1 ? 'animal' : 'animais' }})
    </div>

    <!-- Pagination Controls -->
    <nav class="flex items-center gap-1">
      <!-- Previous Button -->
      <button
        :disabled="currentPage === 1"
        class="inline-flex h-9 w-9 items-center justify-center rounded-md border bg-background text-sm font-medium transition-colors hover:bg-accent hover:text-accent-foreground disabled:pointer-events-none disabled:opacity-50"
        @click="goToPage(currentPage - 1)"
      >
        <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
      </button>

      <!-- Page Numbers -->
      <template v-for="(page, index) in pageRange" :key="index">
        <button
          v-if="typeof page === 'number'"
          :class="[
            'inline-flex h-9 min-w-[2.25rem] items-center justify-center rounded-md border text-sm font-medium transition-colors',
            page === currentPage
              ? 'bg-primary text-primary-foreground border-primary'
              : 'bg-background hover:bg-accent hover:text-accent-foreground',
          ]"
          @click="goToPage(page)"
        >
          {{ page }}
        </button>
        <span
          v-else
          class="inline-flex h-9 w-9 items-center justify-center text-muted-foreground"
        >
          ...
        </span>
      </template>

      <!-- Next Button -->
      <button
        :disabled="currentPage === totalPages"
        class="inline-flex h-9 w-9 items-center justify-center rounded-md border bg-background text-sm font-medium transition-colors hover:bg-accent hover:text-accent-foreground disabled:pointer-events-none disabled:opacity-50"
        @click="goToPage(currentPage + 1)"
      >
        <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
        </svg>
      </button>
    </nav>
  </div>
</template>
