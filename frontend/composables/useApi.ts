import type { UseFetchOptions } from 'nuxt/app'

export function useApi<T>(
  url: string | (() => string),
  options?: UseFetchOptions<T>
) {
  const config = useRuntimeConfig()

  return useFetch(url, {
    ...options,
    baseURL: config.public.apiBase as string,
    onResponseError({ response }) {
      // Handle errors globally
      console.error(`API Error: ${response.status}`, response._data)
    },
  })
}

export function useApiLazy<T>(
  url: string | (() => string),
  options?: UseFetchOptions<T>
) {
  const config = useRuntimeConfig()

  return useLazyFetch(url, {
    ...options,
    baseURL: config.public.apiBase as string,
    onResponseError({ response }) {
      console.error(`API Error: ${response.status}`, response._data)
    },
  })
}
