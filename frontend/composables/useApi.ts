import type { UseFetchOptions } from 'nuxt/app'

export function getApiBase() {
  const config = useRuntimeConfig()

  // On server (SSR), use internal Docker network URL
  // On client (browser), use the public URL
  if (import.meta.server) {
    // Inside Docker, use nginx service name
    return 'http://nginx/api'
  }

  return config.public.apiBase as string
}

export function useApi<T>(
  url: string | (() => string),
  options?: UseFetchOptions<T>
) {
  return useFetch(url, {
    ...options,
    baseURL: getApiBase(),
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
  return useLazyFetch(url, {
    ...options,
    baseURL: getApiBase(),
    onResponseError({ response }) {
      console.error(`API Error: ${response.status}`, response._data)
    },
  })
}
