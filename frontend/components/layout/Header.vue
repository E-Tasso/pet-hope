<script setup lang="ts">
const mobileMenuOpen = ref(false)

const toggleMobileMenu = () => {
  mobileMenuOpen.value = !mobileMenuOpen.value
}

const closeMobileMenu = () => {
  mobileMenuOpen.value = false
}
</script>

<template>
  <header class="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
    <div class="container flex h-16 items-center justify-between">
      <!-- Logo -->
      <NuxtLink to="/" class="flex items-center gap-2" @click="closeMobileMenu">
        <img src="/pethope_logo_v3.png" alt="PetHope" class="h-9 w-9" />
        <span class="text-xl font-bold text-primary md:text-2xl">PetHope</span>
      </NuxtLink>

      <!-- Desktop Navigation -->
      <nav class="hidden md:flex md:items-center md:space-x-6">
        <NuxtLink
          to="/"
          class="text-sm font-medium transition-colors hover:text-primary"
        >
          Início
        </NuxtLink>
        <NuxtLink
          to="/animais"
          class="text-sm font-medium transition-colors hover:text-primary"
        >
          Animais
        </NuxtLink>
        <NuxtLink
          to="/sobre"
          class="text-sm font-medium transition-colors hover:text-primary"
        >
          Sobre
        </NuxtLink>
      </nav>

      <!-- Mobile Menu Button -->
      <button
        class="md:hidden inline-flex items-center justify-center rounded-md p-2 text-foreground hover:bg-accent hover:text-accent-foreground focus:outline-none focus:ring-2 focus:ring-inset focus:ring-primary"
        @click="toggleMobileMenu"
      >
        <span class="sr-only">Abrir menu</span>
        <svg
          v-if="!mobileMenuOpen"
          class="h-6 w-6"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M4 6h16M4 12h16M4 18h16"
          />
        </svg>
        <svg
          v-else
          class="h-6 w-6"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M6 18L18 6M6 6l12 12"
          />
        </svg>
      </button>
    </div>

    <!-- Mobile Menu -->
    <Transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="transform opacity-0 scale-95"
      enter-to-class="transform opacity-100 scale-100"
      leave-active-class="transition duration-100 ease-in"
      leave-from-class="transform opacity-100 scale-100"
      leave-to-class="transform opacity-0 scale-95"
    >
      <div v-if="mobileMenuOpen" class="md:hidden border-t">
        <nav class="space-y-1 px-4 py-4">
          <NuxtLink
            to="/"
            class="block rounded-md px-3 py-2 text-base font-medium hover:bg-accent hover:text-accent-foreground"
            @click="closeMobileMenu"
          >
            Início
          </NuxtLink>
          <NuxtLink
            to="/animais"
            class="block rounded-md px-3 py-2 text-base font-medium hover:bg-accent hover:text-accent-foreground"
            @click="closeMobileMenu"
          >
            Animais
          </NuxtLink>
          <NuxtLink
            to="/sobre"
            class="block rounded-md px-3 py-2 text-base font-medium hover:bg-accent hover:text-accent-foreground"
            @click="closeMobileMenu"
          >
            Sobre
          </NuxtLink>
        </nav>
      </div>
    </Transition>
  </header>
</template>
