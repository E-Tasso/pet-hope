import type {
  Animal,
  AnimalListItem,
  AnimalFeedItem,
  AnimalFilters,
  PaginatedResponse,
  AnimalCreate,
  AnimalUpdate,
} from '~/types'

export function useAnimalList(filters?: Ref<AnimalFilters>, page = ref(1), pageSize = ref(20)) {
  const queryParams = computed(() => {
    const params: Record<string, string> = {
      page: page.value.toString(),
      page_size: pageSize.value.toString(),
    }

    if (filters?.value) {
      Object.entries(filters.value).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          params[key] = value.toString()
        }
      })
    }

    return params
  })

  return useApi<PaginatedResponse<AnimalListItem>>('/animals', {
    query: queryParams,
    watch: [queryParams],
  })
}

export function useAnimal(id: Ref<string> | string) {
  const animalId = typeof id === 'string' ? ref(id) : id

  return useApi<Animal>(() => `/animals/${animalId.value}`, {
    watch: [animalId],
  })
}

export async function createAnimal(data: AnimalCreate) {
  const config = useRuntimeConfig()

  return $fetch<Animal>('/animals', {
    method: 'POST',
    baseURL: config.public.apiBase as string,
    body: data,
  })
}

export async function updateAnimal(id: string, data: AnimalUpdate) {
  const config = useRuntimeConfig()

  return $fetch<Animal>(`/animals/${id}`, {
    method: 'PUT',
    baseURL: config.public.apiBase as string,
    body: data,
  })
}

export async function deleteAnimal(id: string) {
  const config = useRuntimeConfig()

  return $fetch(`/animals/${id}`, {
    method: 'DELETE',
    baseURL: config.public.apiBase as string,
  })
}

export async function uploadAnimalImage(animalId: string, file: File) {
  const config = useRuntimeConfig()
  const formData = new FormData()
  formData.append('file', file)

  return $fetch(`/images/animals/${animalId}/images`, {
    method: 'POST',
    baseURL: config.public.apiBase as string,
    body: formData,
  })
}

export function useAnimalFeed(pageSize = 10) {
  const config = useRuntimeConfig()

  const animals = ref<AnimalFeedItem[]>([])
  const page = ref(1)
  const hasMore = ref(true)
  const loading = ref(false)
  const error = ref<Error | null>(null)
  const total = ref(0)

  async function loadMore() {
    if (loading.value || !hasMore.value) return

    loading.value = true
    error.value = null

    try {
      const response = await $fetch<PaginatedResponse<AnimalFeedItem>>('/animals/feed', {
        baseURL: config.public.apiBase as string,
        query: {
          page: page.value,
          page_size: pageSize,
        },
      })

      animals.value = [...animals.value, ...response.items]
      total.value = response.total
      hasMore.value = page.value < response.pages
      page.value++
    } catch (e) {
      error.value = e as Error
    } finally {
      loading.value = false
    }
  }

  function reset() {
    animals.value = []
    page.value = 1
    hasMore.value = true
    error.value = null
    total.value = 0
  }

  return {
    animals,
    loading,
    error,
    hasMore,
    total,
    loadMore,
    reset,
  }
}
