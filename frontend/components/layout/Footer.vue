<template>
  <footer class="border-t bg-muted/50">
    <div class="container py-8 md:py-12">
      <div class="grid grid-cols-1 gap-8 md:grid-cols-3">
        <!-- About -->
        <div class="space-y-3">
          <div class="flex items-center gap-2">
            <img src="/pethope_logo_v3.png" alt="PetHope" class="h-8 w-8" />
            <h3 class="text-lg font-semibold">PetHope</h3>
          </div>
          <p class="text-sm text-muted-foreground">
            Plataforma de adocao de animais. Ajudando pets a encontrarem um lar
            amoroso.
          </p>
        </div>

        <!-- Quick Links -->
        <div class="space-y-3">
          <h3 class="text-lg font-semibold">Links Rápidos</h3>
          <nav class="flex flex-col space-y-2 text-sm">
            <NuxtLink
              to="/"
              class="text-muted-foreground hover:text-primary transition-colors"
            >
              Início
            </NuxtLink>
            <NuxtLink
              to="/sobre"
              class="text-muted-foreground hover:text-primary transition-colors"
            >
              Sobre Nós
            </NuxtLink>
          </nav>
        </div>

        <!-- Contact -->
        <div class="space-y-3">
          <h3 class="text-lg font-semibold">Contato</h3>
          <div class="text-sm text-muted-foreground space-y-2">
            <p>Entre em contato para mais informações sobre adoção responsável.</p>
          </div>
        </div>
      </div>

      <!-- Bottom -->
      <div class="mt-8 border-t pt-8 text-center text-sm text-muted-foreground md:text-left">
        <p>
          © {{ new Date().getFullYear() }} PetHope. Todos os direitos reservados.
        </p>
      </div>
    </div>
  </footer>
</template>
