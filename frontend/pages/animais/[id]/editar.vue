<script setup lang="ts">
import type { Animal, AnimalUpdate, Image } from '~/types'

const route = useRoute()
const router = useRouter()
const config = useRuntimeConfig()

const animalId = route.params.id as string

// State
const isVerifying = ref(false)
const isVerified = ref(false)
const isSubmitting = ref(false)
const editKey = ref('')
const verifyError = ref('')
const errorMessage = ref('')
const successMessage = ref('')

// Animal data
const animal = ref<Animal | null>(null)
const isLoading = ref(true)

// Image handling
const existingImages = ref<Image[]>([])
const fileInputRef = ref<HTMLInputElement | null>(null)
const isUploadingImages = ref(false)
const isDeletingImage = ref<string | null>(null)

// Form data
const form = reactive({
  name: '',
  species: 'dog',
  breed: '',
  age_months: undefined as number | undefined,
  size: 'medium',
  gender: 'unknown',
  description: '',
  traits: [] as string[],
  special_needs: '',
  location: '',
  contact_info: {
    phone: '',
    email: '',
    whatsapp: '',
  },
  status: 'available',
})

// Options
const traitOptions = [
  'Castrado',
  'Vacinado',
  'Vermifugado',
  'Microchipado',
  'Bom com criancas',
  'Bom com outros animais',
  'Bom com gatos',
  'Bom com caes',
  'Treinado',
  'Docil',
  'Brincalhao',
  'Calmo',
  'Independente',
]

const speciesOptions = [
  { value: 'dog', label: 'Cachorro' },
  { value: 'cat', label: 'Gato' },
  { value: 'bird', label: 'Passaro' },
  { value: 'rodent', label: 'Roedor' },
  { value: 'other', label: 'Outro' },
]

const sizeOptions = [
  { value: 'small', label: 'Pequeno' },
  { value: 'medium', label: 'Medio' },
  { value: 'large', label: 'Grande' },
]

const genderOptions = [
  { value: 'male', label: 'Macho' },
  { value: 'female', label: 'Femea' },
  { value: 'unknown', label: 'Nao sei' },
]

const statusOptions = [
  { value: 'available', label: 'Disponivel' },
  { value: 'in_process', label: 'Em processo de adocao' },
  { value: 'adopted', label: 'Adotado' },
]

// Load animal data
async function loadAnimal() {
  isLoading.value = true
  try {
    animal.value = await $fetch<Animal>(`/animals/${animalId}`, {
      baseURL: config.public.apiBase as string,
    })

    // Populate form
    form.name = animal.value.name
    form.species = animal.value.species
    form.breed = animal.value.breed || ''
    form.age_months = animal.value.age_months
    form.size = animal.value.size
    form.gender = animal.value.gender
    form.description = animal.value.description
    form.traits = animal.value.traits || []
    form.special_needs = animal.value.special_needs || ''
    form.location = animal.value.location
    form.status = animal.value.status
    form.contact_info = {
      phone: animal.value.contact_info?.phone || '',
      email: animal.value.contact_info?.email || '',
      whatsapp: animal.value.contact_info?.whatsapp || '',
    }

    // Populate existing images
    existingImages.value = animal.value.images || []
  } catch (error) {
    console.error('Error loading animal:', error)
    errorMessage.value = 'Erro ao carregar dados do animal'
  } finally {
    isLoading.value = false
  }
}

// Image handling functions
function triggerFileInput() {
  fileInputRef.value?.click()
}

async function handleFileSelect(event: Event) {
  const input = event.target as HTMLInputElement
  if (!input.files) return

  const files = Array.from(input.files)

  // Validate files
  for (const file of files) {
    if (!file.type.startsWith('image/')) {
      errorMessage.value = 'Apenas imagens são permitidas'
      return
    }
    if (file.size > 5 * 1024 * 1024) {
      errorMessage.value = 'Imagens devem ter no máximo 5MB'
      return
    }
  }

  // Reset input
  input.value = ''

  // Upload images automatically
  isUploadingImages.value = true
  errorMessage.value = ''

  for (const file of files) {
    try {
      const formData = new FormData()
      formData.append('file', file)

      const newImage = await $fetch<Image>(`/images/animals/${animalId}/images`, {
        baseURL: config.public.apiBase as string,
        method: 'POST',
        body: formData,
      })

      // Add to existing images immediately
      existingImages.value = [...existingImages.value, newImage]
    } catch (error) {
      console.error('Error uploading image:', error)
      errorMessage.value = 'Erro ao enviar uma das imagens'
    }
  }

  isUploadingImages.value = false
}

async function deleteExistingImage(imageId: string) {
  if (!confirm('Tem certeza que deseja excluir esta foto?')) return

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
    // Update local state
    existingImages.value = existingImages.value.map(img => ({
      ...img,
      is_primary: img.id === imageId,
    }))
  } catch (error) {
    console.error('Error setting primary image:', error)
    errorMessage.value = 'Erro ao definir foto principal'
  }
}

// Verify edit key
async function verifyEditKey() {
  if (!editKey.value) {
    verifyError.value = 'Digite a chave de edicao'
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
      verifyError.value = 'Chave de edicao invalida'
    }
  } catch (error) {
    console.error('Error verifying key:', error)
    verifyError.value = 'Erro ao verificar chave'
  } finally {
    isVerifying.value = false
  }
}

function toggleTrait(trait: string) {
  const index = form.traits?.indexOf(trait) ?? -1
  if (index === -1) {
    form.traits = [...(form.traits || []), trait]
  } else {
    form.traits = form.traits?.filter(t => t !== trait)
  }
}

async function handleSubmit() {
  errorMessage.value = ''
  successMessage.value = ''

  // Validate
  if (!form.name.trim()) {
    errorMessage.value = 'Nome e obrigatorio'
    return
  }
  if (!form.description.trim() || form.description.length < 10) {
    errorMessage.value = 'Descricao deve ter pelo menos 10 caracteres'
    return
  }
  if (!form.location.trim()) {
    errorMessage.value = 'Localizacao e obrigatoria'
    return
  }

  const hasContact = form.contact_info.phone || form.contact_info.email || form.contact_info.whatsapp
  if (!hasContact) {
    errorMessage.value = 'Informe pelo menos um meio de contato'
    return
  }

  isSubmitting.value = true

  try {
    const cleanContactInfo: Record<string, string> = {}
    if (form.contact_info.phone) cleanContactInfo.phone = form.contact_info.phone
    if (form.contact_info.email) cleanContactInfo.email = form.contact_info.email
    if (form.contact_info.whatsapp) cleanContactInfo.whatsapp = form.contact_info.whatsapp

    const payload = {
      name: form.name,
      species: form.species,
      breed: form.breed || undefined,
      age_months: form.age_months || undefined,
      size: form.size,
      gender: form.gender,
      description: form.description,
      traits: form.traits,
      special_needs: form.special_needs || undefined,
      location: form.location,
      contact_info: cleanContactInfo,
      status: form.status,
      edit_key: editKey.value,
    }

    await $fetch(`/animals/${animalId}/edit`, {
      baseURL: config.public.apiBase as string,
      method: 'PUT',
      body: payload,
    })

    successMessage.value = 'Animal atualizado com sucesso!'

    setTimeout(() => {
      router.push(`/animais/${animalId}`)
    }, 1500)
  } catch (error: any) {
    console.error('Error updating animal:', error)
    errorMessage.value = error?.data?.detail || 'Erro ao atualizar animal'
  } finally {
    isSubmitting.value = false
  }
}

// Load animal on mount
onMounted(() => {
  loadAnimal()
})

useSeoMeta({
  title: 'Editar Animal - PetHope',
})
</script>

<template>
  <div class="container mx-auto px-4 py-8 max-w-3xl">
    <!-- Loading -->
    <div v-if="isLoading" class="flex justify-center py-12">
      <div class="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
    </div>

    <!-- Key Verification -->
    <div v-else-if="!isVerified" class="max-w-md mx-auto">
      <div class="bg-white p-8 rounded-lg shadow-sm border text-center">
        <div class="w-16 h-16 mx-auto mb-4 bg-purple-100 rounded-full flex items-center justify-center">
          <svg class="w-8 h-8 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
          </svg>
        </div>

        <h1 class="text-2xl font-bold text-gray-900 mb-2">Editar {{ animal?.name }}</h1>
        <p class="text-gray-600 mb-6">
          Digite a chave de edicao que voce criou ao cadastrar este animal.
        </p>

        <div v-if="verifyError" class="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
          <p class="text-red-800 text-sm">{{ verifyError }}</p>
        </div>

        <form @submit.prevent="verifyEditKey" class="space-y-4">
          <input
            v-model="editKey"
            type="password"
            placeholder="Chave de edicao"
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
          />

          <button
            type="submit"
            :disabled="isVerifying"
            class="w-full py-3 bg-purple-600 text-white rounded-lg font-medium hover:bg-purple-700 transition-colors disabled:opacity-50"
          >
            {{ isVerifying ? 'Verificando...' : 'Continuar' }}
          </button>
        </form>

        <NuxtLink
          :to="`/animais/${animalId}`"
          class="inline-block mt-4 text-sm text-gray-600 hover:text-purple-600"
        >
          Voltar para o animal
        </NuxtLink>
      </div>
    </div>

    <!-- Edit Form -->
    <div v-else>
      <h1 class="text-3xl font-bold text-gray-900 mb-2">Editar {{ animal?.name }}</h1>
      <p class="text-gray-600 mb-8">Atualize os dados do animal</p>

      <!-- Success Message -->
      <div v-if="successMessage" class="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
        <p class="text-green-800 font-medium">{{ successMessage }}</p>
      </div>

      <!-- Error Message -->
      <div v-if="errorMessage" class="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
        <p class="text-red-800 font-medium">{{ errorMessage }}</p>
      </div>

      <form @submit.prevent="handleSubmit" class="space-y-8">
        <!-- Basic Information -->
        <section class="bg-white p-6 rounded-lg shadow-sm border">
          <h2 class="text-xl font-semibold text-gray-900 mb-4">Informacoes Basicas</h2>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label for="name" class="block text-sm font-medium text-gray-700 mb-1">Nome *</label>
              <input
                id="name"
                v-model="form.name"
                type="text"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              />
            </div>

            <div>
              <label for="species" class="block text-sm font-medium text-gray-700 mb-1">Especie *</label>
              <select
                id="species"
                v-model="form.species"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                <option v-for="option in speciesOptions" :key="option.value" :value="option.value">
                  {{ option.label }}
                </option>
              </select>
            </div>

            <div>
              <label for="breed" class="block text-sm font-medium text-gray-700 mb-1">Raca</label>
              <input
                id="breed"
                v-model="form.breed"
                type="text"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              />
            </div>

            <div>
              <label for="age" class="block text-sm font-medium text-gray-700 mb-1">Idade (meses)</label>
              <input
                id="age"
                v-model.number="form.age_months"
                type="number"
                min="0"
                max="360"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              />
            </div>

            <div>
              <label for="size" class="block text-sm font-medium text-gray-700 mb-1">Porte *</label>
              <select
                id="size"
                v-model="form.size"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                <option v-for="option in sizeOptions" :key="option.value" :value="option.value">
                  {{ option.label }}
                </option>
              </select>
            </div>

            <div>
              <label for="gender" class="block text-sm font-medium text-gray-700 mb-1">Sexo *</label>
              <select
                id="gender"
                v-model="form.gender"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                <option v-for="option in genderOptions" :key="option.value" :value="option.value">
                  {{ option.label }}
                </option>
              </select>
            </div>

            <div>
              <label for="status" class="block text-sm font-medium text-gray-700 mb-1">Status *</label>
              <select
                id="status"
                v-model="form.status"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                <option v-for="option in statusOptions" :key="option.value" :value="option.value">
                  {{ option.label }}
                </option>
              </select>
            </div>
          </div>
        </section>

        <!-- Photos -->
        <section class="bg-white p-6 rounded-lg shadow-sm border">
          <h2 class="text-xl font-semibold text-gray-900 mb-4">Fotos</h2>

          <!-- Existing Images -->
          <div v-if="existingImages.length > 0" class="mb-6">
            <h3 class="text-sm font-medium text-gray-700 mb-3">Fotos atuais</h3>
            <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
              <div
                v-for="image in existingImages"
                :key="image.id"
                class="relative group"
              >
                <div class="aspect-square rounded-lg overflow-hidden bg-gray-100">
                  <img
                    :src="image.thumbnail_url"
                    :alt="form.name"
                    class="w-full h-full object-cover"
                  />
                </div>

                <!-- Primary badge -->
                <div
                  v-if="image.is_primary"
                  class="absolute top-2 left-2 px-2 py-1 bg-purple-600 text-white text-xs rounded-full"
                >
                  Principal
                </div>

                <!-- Action buttons overlay -->
                <div class="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity rounded-lg flex items-center justify-center gap-2">
                  <!-- Set as primary -->
                  <button
                    v-if="!image.is_primary"
                    type="button"
                    @click="setAsPrimary(image.id)"
                    class="p-2 bg-white rounded-full hover:bg-gray-100 transition-colors"
                    title="Definir como principal"
                  >
                    <svg class="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
                    </svg>
                  </button>

                  <!-- Delete -->
                  <button
                    type="button"
                    @click="deleteExistingImage(image.id)"
                    :disabled="isDeletingImage === image.id"
                    class="p-2 bg-white rounded-full hover:bg-gray-100 transition-colors disabled:opacity-50"
                    title="Excluir foto"
                  >
                    <svg v-if="isDeletingImage === image.id" class="w-5 h-5 text-red-600 animate-spin" fill="none" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    <svg v-else class="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Add Photos Button -->
          <div>
            <input
              ref="fileInputRef"
              type="file"
              accept="image/*"
              multiple
              class="hidden"
              :disabled="isUploadingImages"
              @change="handleFileSelect"
            />
            <button
              type="button"
              @click="triggerFileInput"
              :disabled="isUploadingImages"
              class="flex items-center gap-2 px-4 py-3 border-2 border-dashed border-gray-300 rounded-lg text-gray-600 hover:border-purple-500 hover:text-purple-600 transition-colors w-full justify-center disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <svg v-if="isUploadingImages" class="w-6 h-6 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <svg v-else class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
              </svg>
              {{ isUploadingImages ? 'Enviando...' : 'Adicionar fotos' }}
            </button>
            <p class="text-sm text-gray-500 text-center mt-2">
              JPG, PNG ou WebP (max 5MB cada) - Upload automatico
            </p>
          </div>
        </section>

        <!-- Description -->
        <section class="bg-white p-6 rounded-lg shadow-sm border">
          <h2 class="text-xl font-semibold text-gray-900 mb-4">Descricao</h2>

          <div>
            <label for="description" class="block text-sm font-medium text-gray-700 mb-1">
              Historia do animal *
            </label>
            <textarea
              id="description"
              v-model="form.description"
              rows="5"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
            ></textarea>
          </div>

          <div class="mt-4">
            <label for="special_needs" class="block text-sm font-medium text-gray-700 mb-1">
              Necessidades Especiais
            </label>
            <textarea
              id="special_needs"
              v-model="form.special_needs"
              rows="3"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
            ></textarea>
          </div>
        </section>

        <!-- Traits -->
        <section class="bg-white p-6 rounded-lg shadow-sm border">
          <h2 class="text-xl font-semibold text-gray-900 mb-4">Caracteristicas</h2>

          <div class="flex flex-wrap gap-2">
            <button
              v-for="trait in traitOptions"
              :key="trait"
              type="button"
              @click="toggleTrait(trait)"
              :class="[
                'px-4 py-2 rounded-full text-sm font-medium transition-colors',
                form.traits?.includes(trait)
                  ? 'bg-purple-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              ]"
            >
              {{ trait }}
            </button>
          </div>
        </section>

        <!-- Location and Contact -->
        <section class="bg-white p-6 rounded-lg shadow-sm border">
          <h2 class="text-xl font-semibold text-gray-900 mb-4">Localizacao e Contato</h2>

          <div class="space-y-4">
            <div>
              <label for="location" class="block text-sm font-medium text-gray-700 mb-1">
                Cidade/Regiao *
              </label>
              <input
                id="location"
                v-model="form.location"
                type="text"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              />
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label for="phone" class="block text-sm font-medium text-gray-700 mb-1">Telefone</label>
                <input
                  id="phone"
                  v-model="form.contact_info.phone"
                  type="tel"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
              </div>

              <div>
                <label for="email" class="block text-sm font-medium text-gray-700 mb-1">E-mail</label>
                <input
                  id="email"
                  v-model="form.contact_info.email"
                  type="email"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
              </div>

              <div>
                <label for="whatsapp" class="block text-sm font-medium text-gray-700 mb-1">WhatsApp</label>
                <input
                  id="whatsapp"
                  v-model="form.contact_info.whatsapp"
                  type="tel"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
              </div>
            </div>
          </div>
        </section>

        <!-- Submit -->
        <div class="flex justify-end gap-4">
          <NuxtLink
            :to="`/animais/${animalId}`"
            class="px-6 py-3 border border-gray-300 rounded-lg text-gray-700 font-medium hover:bg-gray-50 transition-colors"
          >
            Cancelar
          </NuxtLink>
          <button
            type="submit"
            :disabled="isSubmitting"
            class="px-6 py-3 bg-purple-600 text-white rounded-lg font-medium hover:bg-purple-700 transition-colors disabled:opacity-50"
          >
            {{ isSubmitting ? 'Salvando...' : 'Salvar Alteracoes' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>
