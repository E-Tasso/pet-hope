<script setup lang="ts">
interface Props {
  size?: 'sm' | 'md' | 'lg'
}

const props = withDefaults(defineProps<Props>(), {
  size: 'md',
})

const sizeClasses = computed(() => {
  const sizes = {
    sm: 'h-4 w-4 border-2',
    md: 'h-8 w-8 border-3',
    lg: 'h-12 w-12 border-4',
  }
  return sizes[props.size]
})
</script>

<template>
  <div
    :class="sizeClasses"
    class="animate-spin rounded-full border-primary border-t-transparent"
    role="status"
  >
    <span class="sr-only">Carregando...</span>
  </div>
</template>
