<script setup lang="ts">
import { Cropper } from 'vue-advanced-cropper'
import 'vue-advanced-cropper/dist/style.css'

interface Props {
  image: string
}

interface Emits {
  (e: 'save', blob: Blob): void
  (e: 'cancel'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const cropperRef = ref<InstanceType<typeof Cropper> | null>(null)
const rotation = ref(0)

function rotate(degrees: number) {
  rotation.value = (rotation.value + degrees) % 360
}

async function save() {
  if (!cropperRef.value) return

  const { canvas } = cropperRef.value.getResult()
  if (!canvas) return

  canvas.toBlob((blob: Blob | null) => {
    if (blob) {
      emit('save', blob)
    }
  }, 'image/jpeg', 0.9)
}

function cancel() {
  emit('cancel')
}
</script>

<template>
  <div class="fixed inset-0 z-50 bg-black flex flex-col">
    <!-- Header -->
    <div class="flex items-center justify-between px-4 py-3 bg-black/90">
      <button
        @click="cancel"
        class="text-white p-2 hover:bg-white/10 rounded-full"
      >
        <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
      <span class="text-white font-medium">Ajustar foto</span>
      <button
        @click="save"
        class="text-purple-400 font-semibold p-2 hover:bg-white/10 rounded-lg"
      >
        Aplicar
      </button>
    </div>

    <!-- Cropper -->
    <div class="flex-1 relative">
      <Cropper
        ref="cropperRef"
        :src="image"
        :stencil-props="{
          aspectRatio: 1,
        }"
        :transitions="true"
        :canvas="{
          width: 1080,
          height: 1080,
        }"
        :transformations="{
          rotate: rotation,
        }"
        class="h-full"
        background-class="bg-black"
        foreground-class="bg-black/50"
      />
    </div>

    <!-- Controls -->
    <div class="bg-black/90 px-4 py-4">
      <!-- Rotation controls -->
      <div class="flex items-center justify-center gap-6">
        <button
          @click="rotate(-90)"
          class="flex flex-col items-center gap-1 text-white/80 hover:text-white p-3"
        >
          <svg class="w-7 h-7" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6" />
          </svg>
          <span class="text-xs">Girar esquerda</span>
        </button>

        <button
          @click="rotate(90)"
          class="flex flex-col items-center gap-1 text-white/80 hover:text-white p-3"
        >
          <svg class="w-7 h-7 transform scale-x-[-1]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6" />
          </svg>
          <span class="text-xs">Girar direita</span>
        </button>
      </div>

      <p class="text-center text-white/50 text-sm mt-3">
        Arraste para ajustar a posição e use pinça para zoom
      </p>
    </div>
  </div>
</template>

<style>
.vue-advanced-cropper {
  background: black !important;
}
</style>
