<script setup lang="ts">
import type { Animal, Image } from '~/types'

const route = useRoute()
const router = useRouter()
const config = useRuntimeConfig()

const animalId = route.params.id as string

// Auth state
const isVerifying = ref(false)
const isVerified = ref(false)
const editKey = ref('')
const verifyError = ref('')

// Data state
const animal = ref<Animal | null>(null)
const isLoading = ref(true)
const isSubmitting = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

// Image handling
const existingImages = ref<Image[]>([])
const newImages = ref<File[]>([])
const newImageUrls = ref<string[]>([])
const fileInputRef = ref<HTMLInputElement | null>(null)
const isUploadingImages = ref(false)
const isDeletingImage = ref<string | null>(null)

// Cropper state
const showCropper = ref(false)
const cropperImageUrl = ref('')
const pendingFiles = ref<File[]>([])
const currentCropIndex = ref(0)
const editingNewIndex = ref<number | null>(null)

// Form data
const form = reactive({
  name: '',
  species: 'dog',
  size: 'medium',
  gender: 'unknown',
  description: '',
  location: '',
  contact_info: {
    whatsapp: '',
  },
  status: 'available',
})

const speciesOptions = [
  { value: 'dog', label: 'Cachorro' },
  { value: 'cat', label: 'Gato' },
  { value: 'rabbit', label: 'Coelho' },
  { value: 'hamster', label: 'Hamster' },
  { value: 'guinea_pig', label: 'Porquinho-da-índia' },
  { value: 'bird', label: 'Ave (calopsita, periquito, canário)' },
  { value: 'chinchilla', label: 'Chinchila' },
  { value: 'fish', label: 'Peixe' },
]

const sizeOptions = [
  { value: 'small', label: 'Pequeno' },
  { value: 'medium', label: 'Médio' },
  { value: 'large', label: 'Grande' },
]

const genderOptions = [
  { value: 'male', label: 'Macho' },
  { value: 'female', label: 'Fêmea' },
  { value: 'unknown', label: 'Não sei' },
]

const statusOptions = [
  { value: 'available', label: 'Disponível', color: 'bg-green-100 text-green-700 border-green-300' },
  { value: 'in_process', label: 'Em processo', color: 'bg-yellow-100 text-yellow-700 border-yellow-300' },
  { value: 'adopted', label: 'Adotado', color: 'bg-purple-100 text-purple-700 border-purple-300' },
]

// Total images count
const totalImages = computed(() => existingImages.value.length + newImages.value.length)

// Load animal data
async function loadAnimal() {
  isLoading.value = true
  try {
    animal.value = await $fetch<Animal>(`/animals/${animalId}`, {
      baseURL: config.public.apiBase as string,
    })

    form.name = animal.value.name
    form.species = animal.value.species
    form.size = animal.value.size
    form.gender = animal.value.gender
    form.description = animal.value.description || ''
    form.location = animal.value.location
    form.status = animal.value.status
    form.contact_info.whatsapp = animal.value.contact_info?.whatsapp || animal.value.contact_info?.phone || ''

    existingImages.value = animal.value.images || []
  } catch (error) {
    console.error('Error loading animal:', error)
    errorMessage.value = 'Erro ao carregar dados do animal'
  } finally {
    isLoading.value = false
  }
}

// Verify edit key
async function verifyEditKey() {
  if (!editKey.value) {
    verifyError.value = 'Digite a senha'
    return
  }

  isVerifying.value = true
  verifyError.value = ''

  try {
    const response = await $fetch<{ valid: boolean }>(`/animals/${animalId}/verify-key`, {
      baseURL: config.public.apiBase as string,
      method: 'POST',
      body: { edit_key: editKey.value },
    })

    if (response.valid) {
      isVerified.value = true
    } else {
      verifyError.value = 'Senha incorreta'
    }
  } catch (error) {
    console.error('Error verifying key:', error)
    verifyError.value = 'Erro ao verificar senha'
  } finally {
    isVerifying.value = false
  }
}

// Image handling functions
function triggerFileInput() {
  fileInputRef.value?.click()
}

function handleFileSelect(event: Event) {
  const input = event.target as HTMLInputElement
  if (!input.files) return

  const files = Array.from(input.files)

  for (const file of files) {
    if (!file.type.startsWith('image/')) {
      errorMessage.value = 'Apenas imagens são permitidas'
      input.value = ''
      return
    }
    if (file.size > 10 * 1024 * 1024) {
      errorMessage.value = 'Cada imagem deve ter no máximo 10MB'
      input.value = ''
      return
    }
  }

  const maxNew = 5 - totalImages.value
  pendingFiles.value = files.slice(0, maxNew)
  currentCropIndex.value = 0
  editingNewIndex.value = null

  if (pendingFiles.value.length > 0) {
    openCropperForFile(pendingFiles.value[0])
  }

  input.value = ''
  errorMessage.value = ''
}

function openCropperForFile(file: File) {
  cropperImageUrl.value = URL.createObjectURL(file)
  showCropper.value = true
}

function editNewImage(index: number) {
  editingNewIndex.value = index
  cropperImageUrl.value = newImageUrls.value[index]
  showCropper.value = true
}

async function handleCropSave(blob: Blob) {
  const file = new File([blob], `image_${Date.now()}.jpg`, { type: 'image/jpeg' })
  const previewUrl = URL.createObjectURL(blob)

  if (editingNewIndex.value !== null) {
    URL.revokeObjectURL(newImageUrls.value[editingNewIndex.value])
    newImages.value[editingNewIndex.value] = file
    newImageUrls.value[editingNewIndex.value] = previewUrl
    editingNewIndex.value = null
  } else {
    newImages.value.push(file)
    newImageUrls.value.push(previewUrl)

    currentCropIndex.value++
    if (currentCropIndex.value < pendingFiles.value.length) {
      URL.revokeObjectURL(cropperImageUrl.value)
      openCropperForFile(pendingFiles.value[currentCropIndex.value])
      return
    }
  }

  closeCropper()
}

function handleCropCancel() {
  if (editingNewIndex.value === null) {
    currentCropIndex.value++
    if (currentCropIndex.value < pendingFiles.value.length) {
      URL.revokeObjectURL(cropperImageUrl.value)
      openCropperForFile(pendingFiles.value[currentCropIndex.value])
      return
    }
  }
  closeCropper()
}

function closeCropper() {
  URL.revokeObjectURL(cropperImageUrl.value)
  showCropper.value = false
  cropperImageUrl.value = ''
  pendingFiles.value = []
  editingNewIndex.value = null
}

function removeNewImage(index: number) {
  URL.revokeObjectURL(newImageUrls.value[index])
  newImages.value.splice(index, 1)
  newImageUrls.value.splice(index, 1)
}

async function deleteExistingImage(imageId: string) {
  if (!confirm('Excluir esta foto?')) return

  isDeletingImage.value = imageId
  try {
    await $fetch(`/images/${imageId}`, {
      baseURL: config.public.apiBase as string,
      method: 'DELETE',
    })
    existingImages.value = existingImages.value.filter(img => img.id !== imageId)
  } catch (error) {
    console.error('Error deleting image:', error)
    errorMessage.value = 'Erro ao excluir imagem'
  } finally {
    isDeletingImage.value = null
  }
}

async function setAsPrimary(imageId: string) {
  try {
    await $fetch(`/images/${imageId}/primary`, {
      baseURL: config.public.apiBase as string,
      method: 'PATCH',
      body: { is_primary: true },
    })
    existingImages.value = existingImages.value.map(img => ({
      ...img,
      is_primary: img.id === imageId,
    }))
  } catch (error) {
    console.error('Error setting primary image:', error)
    errorMessage.value = 'Erro ao definir foto principal'
  }
}

async function uploadNewImages() {
  for (const file of newImages.value) {
    try {
      const formData = new FormData()
      formData.append('file', file)

      const newImage = await $fetch<Image>(`/images/animals/${animalId}/images`, {
        baseURL: config.public.apiBase as string,
        method: 'POST',
        body: formData,
      })

      existingImages.value = [...existingImages.value, newImage]
    } catch (error) {
      console.error('Error uploading image:', error)
    }
  }
}

async function handleSubmit() {
  errorMessage.value = ''
  successMessage.value = ''

  if (!form.name.trim()) {
    errorMessage.value = 'Nome é obrigatório'
    return
  }
  if (!form.location.trim()) {
    errorMessage.value = 'Cidade é obrigatória'
    return
  }
  if (!form.contact_info.whatsapp.trim()) {
    errorMessage.value = 'WhatsApp é obrigatório'
    return
  }

  isSubmitting.value = true

  try {
    // Upload new images first
    if (newImages.value.length > 0) {
      isUploadingImages.value = true
      await uploadNewImages()
      isUploadingImages.value = false
      newImages.value = []
      newImageUrls.value.forEach(url => URL.revokeObjectURL(url))
      newImageUrls.value = []
    }

    // Update animal data
    const payload = {
      name: form.name,
      species: form.species,
      size: form.size,
      gender: form.gender,
      description: form.description || undefined,
      location: form.location,
      contact_info: { whatsapp: form.contact_info.whatsapp },
      status: form.status,
      edit_key: editKey.value,
    }

    await $fetch(`/animals/${animalId}/edit`, {
      baseURL: config.public.apiBase as string,
      method: 'PUT',
      body: payload,
    })

    successMessage.value = 'Salvo com sucesso!'

    setTimeout(() => {
      router.push(`/animais/${animalId}`)
    }, 1000)
  } catch (error: any) {
    console.error('Error updating animal:', error)
    errorMessage.value = error?.data?.detail || 'Erro ao salvar'
  } finally {
    isSubmitting.value = false
  }
}

onMounted(() => {
  loadAnimal()
})

onUnmounted(() => {
  newImageUrls.value.forEach(url => URL.revokeObjectURL(url))
  if (cropperImageUrl.value) {
    URL.revokeObjectURL(cropperImageUrl.value)
  }
})

useSeoMeta({
  title: 'Editar Animal - PetHope',
})
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <div class="sticky top-0 z-10 bg-white border-b">
      <div class="container mx-auto px-4 py-3 flex items-center justify-between">
        <NuxtLink :to="`/animais/${animalId}`" class="p-2 -ml-2 hover:bg-gray-100 rounded-full">
          <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
        </NuxtLink>
        <h1 class="font-semibold">Editar</h1>
        <div class="w-9"></div>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="isLoading" class="flex justify-center py-16">
      <div class="h-8 w-8 animate-spin rounded-full border-4 border-purple-600 border-t-transparent" />
    </div>

    <!-- Key Verification -->
    <div v-else-if="!isVerified" class="container mx-auto px-4 py-8 max-w-sm">
      <div class="text-center mb-8">
        <div class="w-16 h-16 mx-auto mb-4 bg-purple-100 rounded-full flex items-center justify-center">
          <svg class="w-8 h-8 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
          </svg>
        </div>
        <h2 class="text-xl font-bold text-gray-900 mb-1">{{ animal?.name }}</h2>
        <p class="text-gray-500 text-sm">Digite a senha para editar</p>
      </div>

      <div v-if="verifyError" class="mb-4 p-3 bg-red-50 border border-red-200 rounded-xl text-center">
        <p class="text-red-700 text-sm">{{ verifyError }}</p>
      </div>

      <form @submit.prevent="verifyEditKey" class="space-y-4">
        <input
          v-model="editKey"
          type="password"
          placeholder="Senha"
          class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 text-center"
        />
        <button
          type="submit"
          :disabled="isVerifying"
          class="w-full py-3 bg-purple-600 text-white rounded-xl font-medium hover:bg-purple-700 disabled:opacity-50"
        >
          {{ isVerifying ? 'Verificando...' : 'Continuar' }}
        </button>
      </form>
    </div>

    <!-- Edit Form -->
    <div v-else class="container mx-auto px-4 py-4 max-w-lg pb-24">
      <!-- Messages -->
      <div v-if="successMessage" class="mb-4 p-3 bg-green-50 border border-green-200 rounded-xl text-center">
        <p class="text-green-700 text-sm font-medium">{{ successMessage }}</p>
      </div>
      <div v-if="errorMessage" class="mb-4 p-3 bg-red-50 border border-red-200 rounded-xl text-center">
        <p class="text-red-700 text-sm">{{ errorMessage }}</p>
      </div>

      <form @submit.prevent="handleSubmit" class="space-y-4">
        <!-- Photos Section -->
        <section>
          <div class="flex items-center justify-between mb-2">
            <h3 class="text-sm font-medium text-gray-700">Fotos</h3>
            <span class="text-xs text-gray-400">{{ totalImages }}/5</span>
          </div>

          <input
            ref="fileInputRef"
            type="file"
            accept="image/jpeg,image/png,image/webp"
            multiple
            class="hidden"
            @change="handleFileSelect"
          />

          <div class="grid grid-cols-4 gap-2">
            <!-- Existing images -->
            <div
              v-for="(image, index) in existingImages"
              :key="image.id"
              class="relative aspect-square rounded-lg overflow-hidden bg-gray-100 group"
              :class="{ 'col-span-2 row-span-2': index === 0 && existingImages.length > 0 }"
            >
              <img :src="image.thumbnail_url" :alt="form.name" class="w-full h-full object-cover" />

              <!-- Primary badge -->
              <span
                v-if="image.is_primary"
                class="absolute top-1 left-1 px-1.5 py-0.5 bg-purple-600 text-white text-[10px] rounded-full"
              >
                Principal
              </span>

              <!-- Actions overlay -->
              <div class="absolute inset-0 bg-black/0 group-hover:bg-black/40 transition-colors flex items-center justify-center gap-1 opacity-0 group-hover:opacity-100">
                <button
                  v-if="!image.is_primary"
                  type="button"
                  @click="setAsPrimary(image.id)"
                  class="w-8 h-8 bg-white/90 rounded-full flex items-center justify-center"
                  title="Definir como principal"
                >
                  <svg class="w-4 h-4 text-purple-600" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
                  </svg>
                </button>
                <button
                  type="button"
                  @click="deleteExistingImage(image.id)"
                  :disabled="isDeletingImage === image.id"
                  class="w-8 h-8 bg-red-500/90 rounded-full flex items-center justify-center disabled:opacity-50"
                  title="Excluir"
                >
                  <svg v-if="isDeletingImage === image.id" class="w-4 h-4 text-white animate-spin" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <svg v-else class="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>

            <!-- New images -->
            <div
              v-for="(url, index) in newImageUrls"
              :key="'new-' + index"
              class="relative aspect-square rounded-lg overflow-hidden bg-gray-100 group"
            >
              <img :src="url" alt="Nova foto" class="w-full h-full object-cover" />
              <span class="absolute top-1 left-1 px-1.5 py-0.5 bg-blue-500 text-white text-[10px] rounded-full">
                Nova
              </span>
              <div class="absolute inset-0 bg-black/0 group-hover:bg-black/40 transition-colors flex items-center justify-center gap-1 opacity-0 group-hover:opacity-100">
                <button
                  type="button"
                  @click="editNewImage(index)"
                  class="w-8 h-8 bg-white/90 rounded-full flex items-center justify-center"
                >
                  <svg class="w-4 h-4 text-gray-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                  </svg>
                </button>
                <button
                  type="button"
                  @click="removeNewImage(index)"
                  class="w-8 h-8 bg-red-500/90 rounded-full flex items-center justify-center"
                >
                  <svg class="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>

            <!-- Add button -->
            <button
              v-if="totalImages < 5"
              type="button"
              @click="triggerFileInput"
              class="aspect-square border-2 border-dashed border-gray-300 rounded-lg hover:border-purple-400 hover:bg-purple-50 transition-colors flex items-center justify-center"
            >
              <svg class="w-6 h-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
              </svg>
            </button>
          </div>
        </section>

        <!-- Status -->
        <section>
          <h3 class="text-sm font-medium text-gray-700 mb-2">Status</h3>
          <div class="flex gap-2">
            <button
              v-for="option in statusOptions"
              :key="option.value"
              type="button"
              @click="form.status = option.value"
              :class="[
                'flex-1 py-2 px-3 rounded-lg text-sm font-medium border transition-colors',
                form.status === option.value ? option.color : 'bg-gray-50 text-gray-500 border-gray-200'
              ]"
            >
              {{ option.label }}
            </button>
          </div>
        </section>

        <!-- Basic Info -->
        <section class="space-y-3">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Nome</label>
            <input
              v-model="form.name"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
            />
          </div>

          <!-- Species -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Tipo</label>
            <select
              v-model="form.species"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 bg-white"
            >
              <option v-for="option in speciesOptions" :key="option.value" :value="option.value">
                {{ option.label }}
              </option>
            </select>
          </div>

          <!-- Size & Gender -->
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Porte</label>
              <div class="flex gap-1">
                <button
                  v-for="option in sizeOptions"
                  :key="option.value"
                  type="button"
                  @click="form.size = option.value"
                  :class="[
                    'flex-1 py-2 rounded-lg text-xs font-medium transition-colors',
                    form.size === option.value
                      ? 'bg-purple-600 text-white'
                      : 'bg-gray-100 text-gray-600'
                  ]"
                >
                  {{ option.label }}
                </button>
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Sexo</label>
              <div class="flex gap-1">
                <button
                  v-for="option in genderOptions"
                  :key="option.value"
                  type="button"
                  @click="form.gender = option.value"
                  :class="[
                    'flex-1 py-2 rounded-lg text-xs font-medium transition-colors',
                    form.gender === option.value
                      ? 'bg-purple-600 text-white'
                      : 'bg-gray-100 text-gray-600'
                  ]"
                >
                  {{ option.label }}
                </button>
              </div>
            </div>
          </div>

          <!-- Location -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Cidade</label>
            <input
              v-model="form.location"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
              placeholder="Ex: São Paulo - SP"
            />
          </div>

          <!-- Description -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Descrição</label>
            <textarea
              v-model="form.description"
              rows="2"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 resize-none"
              placeholder="Opcional..."
            ></textarea>
          </div>

          <!-- WhatsApp -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">WhatsApp</label>
            <input
              v-model="form.contact_info.whatsapp"
              type="tel"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
              placeholder="(11) 99999-9999"
            />
          </div>
        </section>

        <!-- Submit -->
        <div class="fixed bottom-0 left-0 right-0 bg-white border-t p-4">
          <div class="container mx-auto max-w-lg flex gap-3">
            <NuxtLink
              :to="`/animais/${animalId}`"
              class="flex-1 py-3 border border-gray-300 rounded-xl text-gray-700 font-medium text-center hover:bg-gray-50"
            >
              Cancelar
            </NuxtLink>
            <button
              type="submit"
              :disabled="isSubmitting || isUploadingImages"
              class="flex-1 py-3 bg-purple-600 text-white rounded-xl font-medium hover:bg-purple-700 disabled:opacity-50"
            >
              {{ isUploadingImages ? 'Enviando fotos...' : isSubmitting ? 'Salvando...' : 'Salvar' }}
            </button>
          </div>
        </div>
      </form>
    </div>

    <!-- Image Cropper Modal -->
    <ClientOnly>
      <Teleport to="body">
        <CommonImageCropper
          v-if="showCropper"
          :image="cropperImageUrl"
          @save="handleCropSave"
          @cancel="handleCropCancel"
        />
      </Teleport>
    </ClientOnly>
  </div>
</template>
