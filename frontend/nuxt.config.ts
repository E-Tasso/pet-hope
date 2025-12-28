// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  devtools: { enabled: true },

  // SSR for better SEO (critical for adoption platform)
  ssr: true,

  // Modules
  modules: ['@nuxtjs/tailwindcss', '@nuxtjs/color-mode'],

  // Tailwind CSS
  tailwindcss: {
    cssPath: '~/assets/css/tailwind.css',
    configPath: 'tailwind.config.ts',
    exposeConfig: false,
    viewer: true,
  },

  // Color mode (optional - supports dark mode)
  colorMode: {
    classSuffix: '',
  },

  // Runtime config - API base URL
  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || 'http://localhost/api',
    },
  },

  // App config
  app: {
    head: {
      charset: 'utf-8',
      viewport: 'width=device-width, initial-scale=1',
      title: 'PetHope - Adote um Pet',
      meta: [
        { name: 'description', content: 'Plataforma de adoção de animais' },
        { name: 'format-detection', content: 'telephone=no' },
      ],
      link: [{ rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' }],
    },
  },

  // TypeScript
  typescript: {
    strict: true,
    typeCheck: false, // Enable in CI
  },

  // Compatibility
  compatibilityDate: '2024-01-01',
})
