<script setup lang="ts">
import type { AnimalCreate } from '~/types'

useSeoMeta({
  title: 'Cadastrar Animal - PetHope',
  description: 'Cadastre um animal para adoção na plataforma PetHope.',
})

const router = useRouter()
const config = useRuntimeConfig()
const isSubmitting = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const uploadProgress = ref('')

// Steps
const currentStep = ref(1)
const totalSteps = 3

// Image handling
const selectedImages = ref<File[]>([])
const imagePreviewUrls = ref<string[]>([])
const fileInputRef = ref<HTMLInputElement | null>(null)

// Cropper state
const showCropper = ref(false)
const cropperImageUrl = ref('')
const pendingFiles = ref<File[]>([])
const currentCropIndex = ref(0)
const editingIndex = ref<number | null>(null)

const form = reactive({
  name: '',
  species: 'dog',
  size: 'medium',
  gender: 'unknown',
  location: '',
  description: '',
  contact_info: {
    whatsapp: '',
  },
  edit_key: '',
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

// Computed
const canProceedStep1 = computed(() => selectedImages.value.length > 0)
const canProceedStep2 = computed(() => form.name.trim() && form.location.trim())
const canSubmit = computed(() => form.contact_info.whatsapp.trim() && form.edit_key.length >= 6)

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

  // Store files and open cropper for the first one
  pendingFiles.value = files.slice(0, 5 - selectedImages.value.length)
  currentCropIndex.value = 0
  editingIndex.value = null

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

function editImage(index: number) {
  editingIndex.value = index
  cropperImageUrl.value = imagePreviewUrls.value[index]
  showCropper.value = true
}

function handleCropSave(blob: Blob) {
  // Create file from blob
  const file = new File([blob], `image_${Date.now()}.jpg`, { type: 'image/jpeg' })
  const previewUrl = URL.createObjectURL(blob)

  if (editingIndex.value !== null) {
    // Editing existing image
    URL.revokeObjectURL(imagePreviewUrls.value[editingIndex.value])
    selectedImages.value[editingIndex.value] = file
    imagePreviewUrls.value[editingIndex.value] = previewUrl
    editingIndex.value = null
  } else {
    // Adding new image
    selectedImages.value.push(file)
    imagePreviewUrls.value.push(previewUrl)

    // Process next pending file
    currentCropIndex.value++
    if (currentCropIndex.value < pendingFiles.value.length) {
      // Clean up previous cropper URL
      URL.revokeObjectURL(cropperImageUrl.value)
      openCropperForFile(pendingFiles.value[currentCropIndex.value])
      return
    }
  }

  closeCropper()
}

function handleCropCancel() {
  if (editingIndex.value === null) {
    // If adding new images, skip to next or close
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
  editingIndex.value = null
}

function removeImage(index: number) {
  URL.revokeObjectURL(imagePreviewUrls.value[index])
  selectedImages.value.splice(index, 1)
  imagePreviewUrls.value.splice(index, 1)
}

function nextStep() {
  if (currentStep.value < totalSteps) {
    currentStep.value++
  }
}

function prevStep() {
  if (currentStep.value > 1) {
    currentStep.value--
  }
}

async function uploadImages(animalId: string) {
  const total = selectedImages.value.length
  let uploaded = 0

  for (const file of selectedImages.value) {
    uploadProgress.value = `Enviando foto ${uploaded + 1} de ${total}...`

    const formData = new FormData()
    formData.append('file', file)

    try {
      await $fetch(`/images/animals/${animalId}/images`, {
        baseURL: config.public.apiBase as string,
        method: 'POST',
        body: formData,
      })
      uploaded++
    } catch (error) {
      console.error('Error uploading image:', error)
    }
  }

  uploadProgress.value = ''
  return uploaded
}

async function handleSubmit() {
  errorMessage.value = ''
  successMessage.value = ''
  uploadProgress.value = ''

  if (!form.contact_info.whatsapp.trim()) {
    errorMessage.value = 'Informe seu WhatsApp para contato'
    return
  }

  if (!form.edit_key || form.edit_key.length < 6) {
    errorMessage.value = 'A senha deve ter pelo menos 6 caracteres'
    return
  }

  isSubmitting.value = true

  try {
    const cleanContactInfo: Record<string, string> = {}
    if (form.contact_info.whatsapp) cleanContactInfo.whatsapp = form.contact_info.whatsapp

    const payload: AnimalCreate = {
      name: form.name,
      species: form.species as any,
      size: form.size as any,
      gender: form.gender as any,
      location: form.location,
      description: form.description || undefined,
      contact_info: cleanContactInfo,
      edit_key: form.edit_key,
    }

    const response = await $fetch<{ id: string }>('/animals', {
      baseURL: config.public.apiBase as string,
      method: 'POST',
      body: payload,
    })

    if (selectedImages.value.length > 0) {
      await uploadImages(response.id)
    }

    successMessage.value = 'Animal cadastrado com sucesso!'

    setTimeout(() => {
      router.push(`/animais/${response.id}`)
    }, 1500)

  } catch (error: any) {
    console.error('Error creating animal:', error)
    errorMessage.value = error?.data?.detail || 'Erro ao cadastrar. Tente novamente.'
  } finally {
    isSubmitting.value = false
  }
}

onUnmounted(() => {
  imagePreviewUrls.value.forEach(url => URL.revokeObjectURL(url))
  if (cropperImageUrl.value) {
    URL.revokeObjectURL(cropperImageUrl.value)
  }
})
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <div class="sticky top-0 z-10 bg-white border-b">
      <div class="container mx-auto px-4 py-4 flex items-center justify-between">
        <button
          v-if="currentStep > 1"
          @click="prevStep"
          class="p-2 -ml-2 hover:bg-gray-100 rounded-full"
        >
          <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
        </button>
        <NuxtLink v-else to="/" class="p-2 -ml-2 hover:bg-gray-100 rounded-full">
          <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </NuxtLink>

        <h1 class="font-semibold">Novo Cadastro</h1>

        <div class="w-10"></div>
      </div>

      <!-- Progress -->
      <div class="h-1 bg-gray-200">
        <div
          class="h-full bg-purple-600 transition-all duration-300"
          :style="{ width: `${(currentStep / totalSteps) * 100}%` }"
        ></div>
      </div>
    </div>

    <!-- Messages -->
    <div v-if="successMessage" class="container mx-auto px-4 pt-4">
      <div class="p-4 bg-green-50 border border-green-200 rounded-lg">
        <p class="text-green-800 font-medium text-center">{{ successMessage }}</p>
      </div>
    </div>

    <div v-if="errorMessage" class="container mx-auto px-4 pt-4">
      <div class="p-4 bg-red-50 border border-red-200 rounded-lg">
        <p class="text-red-800 font-medium text-center">{{ errorMessage }}</p>
      </div>
    </div>

    <div v-if="uploadProgress" class="container mx-auto px-4 pt-4">
      <div class="p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <p class="text-blue-800 font-medium text-center">{{ uploadProgress }}</p>
      </div>
    </div>

    <!-- Step 1: Photo -->
    <div v-if="currentStep === 1" class="container mx-auto px-4 py-8 max-w-lg">
      <div class="text-center mb-8">
        <h2 class="text-2xl font-bold text-gray-900 mb-2">Adicione uma foto</h2>
        <p class="text-gray-600">Uma boa foto aumenta as chances de adoção</p>
      </div>

      <input
        ref="fileInputRef"
        type="file"
        accept="image/jpeg,image/png,image/webp"
        multiple
        class="hidden"
        @change="handleFileSelect"
      />

      <!-- Image previews -->
      <div v-if="imagePreviewUrls.length > 0" class="space-y-4 mb-6">
        <div class="grid grid-cols-3 gap-2">
          <div
            v-for="(url, index) in imagePreviewUrls"
            :key="index"
            class="relative aspect-square rounded-xl overflow-hidden bg-gray-100 group"
            :class="{ 'col-span-2 row-span-2': index === 0 }"
          >
            <img
              :src="url"
              :alt="`Foto ${index + 1}`"
              class="w-full h-full object-cover"
            />
            <!-- Overlay with actions -->
            <div class="absolute inset-0 bg-black/0 group-hover:bg-black/30 transition-colors flex items-center justify-center gap-2 opacity-0 group-hover:opacity-100">
              <button
                type="button"
                @click="editImage(index)"
                class="w-10 h-10 bg-white/90 text-gray-700 rounded-full flex items-center justify-center hover:bg-white"
              >
                <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
              </button>
              <button
                type="button"
                @click="removeImage(index)"
                class="w-10 h-10 bg-red-500/90 text-white rounded-full flex items-center justify-center hover:bg-red-500"
              >
                <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </div>
            <span
              v-if="index === 0"
              class="absolute bottom-2 left-2 px-2 py-1 bg-purple-600 text-white text-xs rounded-full"
            >
              Principal
            </span>
          </div>
        </div>

        <button
          v-if="imagePreviewUrls.length < 5"
          type="button"
          @click="triggerFileInput"
          class="w-full py-3 border-2 border-dashed border-gray-300 rounded-xl hover:border-purple-500 hover:bg-purple-50 transition-colors flex items-center justify-center gap-2 text-gray-600"
        >
          <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          Adicionar mais fotos
        </button>
      </div>

      <!-- Empty state -->
      <button
        v-else
        type="button"
        @click="triggerFileInput"
        class="w-full aspect-square border-2 border-dashed border-gray-300 rounded-2xl hover:border-purple-500 hover:bg-purple-50 transition-colors flex flex-col items-center justify-center gap-4"
      >
        <div class="w-20 h-20 bg-purple-100 rounded-full flex items-center justify-center">
          <svg class="w-10 h-10 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
        </div>
        <div class="text-center">
          <p class="font-medium text-gray-900">Toque para adicionar fotos</p>
          <p class="text-sm text-gray-500 mt-1">JPG, PNG ou WebP (máx. 10MB)</p>
        </div>
      </button>

      <!-- Next Button -->
      <div class="mt-8">
        <button
          @click="nextStep"
          :disabled="!canProceedStep1"
          class="w-full py-4 bg-purple-600 text-white rounded-xl font-semibold hover:bg-purple-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Continuar
        </button>
      </div>
    </div>

    <!-- Step 2: Basic Info -->
    <div v-if="currentStep === 2" class="container mx-auto px-4 py-8 max-w-lg">
      <div class="text-center mb-8">
        <h2 class="text-2xl font-bold text-gray-900 mb-2">Informações básicas</h2>
        <p class="text-gray-600">Conte-nos sobre o animal</p>
      </div>

      <div class="space-y-6">
        <!-- Name -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Nome do Animal</label>
          <input
            v-model="form.name"
            type="text"
            maxlength="100"
            class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent text-lg"
            placeholder="Ex: Rex, Luna, Bob..."
          />
        </div>

        <!-- Species -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Tipo de Animal</label>
          <select
            v-model="form.species"
            class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 bg-white text-lg"
          >
            <option v-for="option in speciesOptions" :key="option.value" :value="option.value">
              {{ option.label }}
            </option>
          </select>
        </div>

        <!-- Size -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Porte</label>
          <div class="grid grid-cols-3 gap-2">
            <button
              v-for="option in sizeOptions"
              :key="option.value"
              type="button"
              @click="form.size = option.value"
              :class="[
                'py-3 rounded-xl font-medium transition-colors',
                form.size === option.value
                  ? 'bg-purple-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              ]"
            >
              {{ option.label }}
            </button>
          </div>
        </div>

        <!-- Gender -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Sexo</label>
          <div class="grid grid-cols-3 gap-2">
            <button
              v-for="option in genderOptions"
              :key="option.value"
              type="button"
              @click="form.gender = option.value"
              :class="[
                'py-3 rounded-xl font-medium transition-colors',
                form.gender === option.value
                  ? 'bg-purple-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              ]"
            >
              {{ option.label }}
            </button>
          </div>
        </div>

        <!-- Location -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Cidade</label>
          <input
            v-model="form.location"
            type="text"
            maxlength="100"
            class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            placeholder="Ex: São Paulo - SP"
          />
        </div>

        <!-- Description (optional) -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Descrição <span class="text-gray-400 font-normal">(opcional)</span>
          </label>
          <textarea
            v-model="form.description"
            rows="3"
            maxlength="5000"
            class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
            placeholder="Conte um pouco sobre a personalidade do animal..."
          ></textarea>
        </div>
      </div>

      <!-- Next Button -->
      <div class="mt-8">
        <button
          @click="nextStep"
          :disabled="!canProceedStep2"
          class="w-full py-4 bg-purple-600 text-white rounded-xl font-semibold hover:bg-purple-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Continuar
        </button>
      </div>
    </div>

    <!-- Step 3: Contact -->
    <div v-if="currentStep === 3" class="container mx-auto px-4 py-8 max-w-lg">
      <div class="text-center mb-8">
        <h2 class="text-2xl font-bold text-gray-900 mb-2">Contato</h2>
        <p class="text-gray-600">Como as pessoas podem te encontrar?</p>
      </div>

      <div class="space-y-6">
        <!-- WhatsApp -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">WhatsApp</label>
          <input
            v-model="form.contact_info.whatsapp"
            type="tel"
            class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            placeholder="(11) 99999-9999"
          />
          <p class="text-sm text-gray-500 mt-2">Interessados entrarão em contato por aqui</p>
        </div>

        <!-- Edit Key -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Crie uma senha</label>
          <input
            v-model="form.edit_key"
            type="password"
            minlength="6"
            maxlength="50"
            class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            placeholder="Mínimo 6 caracteres"
          />
          <p class="text-sm text-gray-500 mt-2">Você precisará dela para editar ou remover o cadastro</p>
        </div>
      </div>

      <!-- Submit Button -->
      <div class="mt-8">
        <button
          @click="handleSubmit"
          :disabled="!canSubmit || isSubmitting"
          class="w-full py-4 bg-purple-600 text-white rounded-xl font-semibold hover:bg-purple-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {{ isSubmitting ? 'Cadastrando...' : 'Publicar Animal' }}
        </button>
      </div>
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
