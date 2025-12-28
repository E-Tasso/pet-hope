<script setup lang="ts">
useSeoMeta({
  title: 'Sobre - PetHope',
  description: 'Saiba mais sobre o PetHope, plataforma de adoção de animais.',
})
</script>

<template>
  <div class="container py-12 md:py-20">
    <div class="mx-auto max-w-3xl">
      <!-- Header -->
      <div class="text-center">
        <h1 class="text-3xl font-bold tracking-tight sm:text-4xl md:text-5xl">
          Sobre o PetHope
        </h1>
        <p class="mt-4 text-lg text-muted-foreground">
          Conectando animais a lares amorosos
        </p>
      </div>

      <!-- Content -->
      <div class="mt-12 space-y-8">
        <!-- Mission -->
        <section class="space-y-4">
          <h2 class="text-2xl font-semibold">Nossa Missão</h2>
          <p class="text-muted-foreground leading-relaxed">
            O PetHope é uma plataforma dedicada a facilitar a adoção responsável de animais.
            Acreditamos que todo animal merece um lar amoroso, e trabalhamos para conectar
            pets resgatados com famílias que estão prontas para oferecer amor e cuidado.
          </p>
        </section>

        <!-- How it works -->
        <section class="space-y-4">
          <h2 class="text-2xl font-semibold">Como Funciona</h2>
          <div class="space-y-4 text-muted-foreground leading-relaxed">
            <p>
              Nossa plataforma permite que abrigos, ONGs e protetores independentes cadastrem
              animais disponíveis para adoção. As pessoas interessadas podem navegar pelos
              perfis, conhecer as histórias dos pets e entrar em contato diretamente com os
              responsáveis.
            </p>
            <p>
              Priorizamos a transparência e facilitamos o processo para ambas as partes,
              tornando a adoção mais acessível e eficiente.
            </p>
          </div>
        </section>

        <!-- Adoption -->
        <section class="space-y-4">
          <h2 class="text-2xl font-semibold">Adoção Responsável</h2>
          <div class="rounded-lg border bg-card p-6">
            <p class="text-muted-foreground leading-relaxed">
              Antes de adotar, certifique-se de que está preparado para a responsabilidade.
              Um pet precisa de amor, atenção, cuidados veterinários, alimentação adequada
              e muito carinho. A adoção é um compromisso de longo prazo que mudará sua vida
              e a vida do animal para melhor.
            </p>
          </div>
        </section>

        <!-- CTA -->
        <section class="pt-8 text-center">
          <h2 class="text-2xl font-semibold mb-4">Pronto para Adotar?</h2>
          <p class="text-muted-foreground mb-6">
            Navegue pelos animais disponíveis e encontre seu novo melhor amigo
          </p>
          <NuxtLink
            to="/"
            class="inline-flex items-center justify-center rounded-md bg-primary px-8 py-3 text-base font-medium text-primary-foreground shadow transition-colors hover:bg-primary/90"
          >
            Ver Animais Disponíveis
          </NuxtLink>
        </section>
      </div>
    </div>
  </div>
</template>
