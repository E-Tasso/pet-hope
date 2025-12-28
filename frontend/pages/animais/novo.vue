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

// Image handling
const selectedImages = ref<File[]>([])
const imagePreviewUrls = ref<string[]>([])
const fileInputRef = ref<HTMLInputElement | null>(null)

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
  edit_key: '',
})

// Traits options
const traitOptions = [
  'Castrado',
  'Vacinado',
  'Vermifugado',
  'Microchipado',
  'Bom com crianças',
  'Bom com outros animais',
  'Bom com gatos',
  'Bom com cães',
  'Treinado',
  'Dócil',
  'Brincalhão',
  'Calmo',
  'Independente',
]

const speciesOptions = [
  { value: 'dog', label: 'Cachorro' },
  { value: 'cat', label: 'Gato' },
  { value: 'bird', label: 'Pássaro' },
  { value: 'rodent', label: 'Roedor' },
  { value: 'other', label: 'Outro' },
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

function toggleTrait(trait: string) {
  const index = form.traits?.indexOf(trait) ?? -1
  if (index === -1) {
    form.traits = [...(form.traits || []), trait]
  } else {
    form.traits = form.traits?.filter(t => t !== trait)
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

  // Validate files
  for (const file of files) {
    if (!file.type.startsWith('image/')) {
      errorMessage.value = 'Apenas imagens são permitidas (JPG, PNG, WebP)'
      return
    }
    if (file.size > 5 * 1024 * 1024) {
      errorMessage.value = 'Cada imagem deve ter no máximo 5MB'
      return
    }
  }

  // Add files to selection
  selectedImages.value = [...selectedImages.value, ...files]

  // Create preview URLs
  for (const file of files) {
    const url = URL.createObjectURL(file)
    imagePreviewUrls.value.push(url)
  }

  // Clear input to allow selecting same file again
  input.value = ''
}

function removeImage(index: number) {
  // Revoke URL to free memory
  URL.revokeObjectURL(imagePreviewUrls.value[index])

  selectedImages.value.splice(index, 1)
  imagePreviewUrls.value.splice(index, 1)
}

async function uploadImages(animalId: string) {
  const total = selectedImages.value.length
  let uploaded = 0

  for (const file of selectedImages.value) {
    uploadProgress.value = `Enviando imagem ${uploaded + 1} de ${total}...`

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
      // Continue with other images even if one fails
    }
  }

  uploadProgress.value = ''
  return uploaded
}

async function handleSubmit() {
  errorMessage.value = ''
  successMessage.value = ''
  uploadProgress.value = ''

  // Validate required fields
  if (!form.name.trim()) {
    errorMessage.value = 'Nome é obrigatório'
    return
  }
  if (!form.description.trim() || form.description.length < 10) {
    errorMessage.value = 'Descrição deve ter pelo menos 10 caracteres'
    return
  }
  if (!form.location.trim()) {
    errorMessage.value = 'Localização é obrigatória'
    return
  }

  // At least one contact method
  const hasContact = form.contact_info.phone || form.contact_info.email || form.contact_info.whatsapp
  if (!hasContact) {
    errorMessage.value = 'Informe pelo menos um meio de contato'
    return
  }

  // Validate edit key
  if (!form.edit_key || form.edit_key.length < 6) {
    errorMessage.value = 'A chave de edicao deve ter pelo menos 6 caracteres'
    return
  }

  isSubmitting.value = true

  try {
    // Clean up contact_info - remove empty fields
    const cleanContactInfo: Record<string, string> = {}
    if (form.contact_info.phone) cleanContactInfo.phone = form.contact_info.phone
    if (form.contact_info.email) cleanContactInfo.email = form.contact_info.email
    if (form.contact_info.whatsapp) cleanContactInfo.whatsapp = form.contact_info.whatsapp

    const payload: AnimalCreate = {
      ...form,
      contact_info: cleanContactInfo,
      breed: form.breed || undefined,
      age_months: form.age_months || undefined,
      special_needs: form.special_needs || undefined,
    }

    // Create animal
    const response = await $fetch<{ id: string }>('/animals', {
      baseURL: config.public.apiBase as string,
      method: 'POST',
      body: payload,
    })

    // Upload images if any
    if (selectedImages.value.length > 0) {
      const uploadedCount = await uploadImages(response.id)
      successMessage.value = `Animal cadastrado com sucesso! ${uploadedCount} imagem(ns) enviada(s).`
    } else {
      successMessage.value = 'Animal cadastrado com sucesso!'
    }

    // Redirect to the animal page after 1.5 seconds
    setTimeout(() => {
      router.push(`/animais/${response.id}`)
    }, 1500)

  } catch (error: any) {
    console.error('Error creating animal:', error)
    errorMessage.value = error?.data?.detail || 'Erro ao cadastrar animal. Tente novamente.'
  } finally {
    isSubmitting.value = false
  }
}

// Cleanup preview URLs on unmount
onUnmounted(() => {
  imagePreviewUrls.value.forEach(url => URL.revokeObjectURL(url))
})
</script>

<template>
  <div class="container mx-auto px-4 py-8 max-w-3xl">
    <h1 class="text-3xl font-bold text-gray-900 mb-2">Cadastrar Animal</h1>
    <p class="text-gray-600 mb-8">Preencha os dados do animal para adoção</p>

    <!-- Success Message -->
    <div v-if="successMessage" class="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
      <p class="text-green-800 font-medium">{{ successMessage }}</p>
    </div>

    <!-- Error Message -->
    <div v-if="errorMessage" class="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
      <p class="text-red-800 font-medium">{{ errorMessage }}</p>
    </div>

    <!-- Upload Progress -->
    <div v-if="uploadProgress" class="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
      <p class="text-blue-800 font-medium">{{ uploadProgress }}</p>
    </div>

    <form @submit.prevent="handleSubmit" class="space-y-8">
      <!-- Basic Information -->
      <section class="bg-white p-6 rounded-lg shadow-sm border">
        <h2 class="text-xl font-semibold text-gray-900 mb-4">Informações Básicas</h2>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <!-- Name -->
          <div>
            <label for="name" class="block text-sm font-medium text-gray-700 mb-1">
              Nome do Animal *
            </label>
            <input
              id="name"
              v-model="form.name"
              type="text"
              required
              maxlength="100"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              placeholder="Ex: Rex, Luna, Bob..."
            />
          </div>

          <!-- Species -->
          <div>
            <label for="species" class="block text-sm font-medium text-gray-700 mb-1">
              Espécie *
            </label>
            <select
              id="species"
              v-model="form.species"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            >
              <option v-for="option in speciesOptions" :key="option.value" :value="option.value">
                {{ option.label }}
              </option>
            </select>
          </div>

          <!-- Breed -->
          <div>
            <label for="breed" class="block text-sm font-medium text-gray-700 mb-1">
              Raça
            </label>
            <input
              id="breed"
              v-model="form.breed"
              type="text"
              maxlength="100"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              placeholder="Ex: Labrador, SRD, Siamês..."
            />
          </div>

          <!-- Age -->
          <div>
            <label for="age" class="block text-sm font-medium text-gray-700 mb-1">
              Idade (em meses)
            </label>
            <input
              id="age"
              v-model.number="form.age_months"
              type="number"
              min="0"
              max="360"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              placeholder="Ex: 12"
            />
            <p class="text-xs text-gray-500 mt-1">1 ano = 12 meses</p>
          </div>

          <!-- Size -->
          <div>
            <label for="size" class="block text-sm font-medium text-gray-700 mb-1">
              Porte *
            </label>
            <select
              id="size"
              v-model="form.size"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            >
              <option v-for="option in sizeOptions" :key="option.value" :value="option.value">
                {{ option.label }}
              </option>
            </select>
          </div>

          <!-- Gender -->
          <div>
            <label for="gender" class="block text-sm font-medium text-gray-700 mb-1">
              Sexo *
            </label>
            <select
              id="gender"
              v-model="form.gender"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            >
              <option v-for="option in genderOptions" :key="option.value" :value="option.value">
                {{ option.label }}
              </option>
            </select>
          </div>
        </div>
      </section>

      <!-- Images -->
      <section class="bg-white p-6 rounded-lg shadow-sm border">
        <h2 class="text-xl font-semibold text-gray-900 mb-4">Fotos do Animal</h2>
        <p class="text-sm text-gray-600 mb-4">Adicione fotos para aumentar as chances de adoção (máx. 5MB cada)</p>

        <!-- Hidden file input -->
        <input
          ref="fileInputRef"
          type="file"
          accept="image/jpeg,image/png,image/webp"
          multiple
          class="hidden"
          @change="handleFileSelect"
        />

        <!-- Image previews -->
        <div v-if="imagePreviewUrls.length > 0" class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
          <div
            v-for="(url, index) in imagePreviewUrls"
            :key="index"
            class="relative aspect-square rounded-lg overflow-hidden bg-gray-100"
          >
            <img
              :src="url"
              :alt="`Imagem ${index + 1}`"
              class="w-full h-full object-cover"
            />
            <button
              type="button"
              @click="removeImage(index)"
              class="absolute top-2 right-2 w-8 h-8 bg-red-500 text-white rounded-full flex items-center justify-center hover:bg-red-600 transition-colors"
            >
              X
            </button>
            <span
              v-if="index === 0"
              class="absolute bottom-2 left-2 px-2 py-1 bg-purple-600 text-white text-xs rounded"
            >
              Principal
            </span>
          </div>
        </div>

        <!-- Add image button -->
        <button
          type="button"
          @click="triggerFileInput"
          class="w-full py-8 border-2 border-dashed border-gray-300 rounded-lg hover:border-purple-500 hover:bg-purple-50 transition-colors flex flex-col items-center justify-center gap-2"
        >
          <svg class="w-10 h-10 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
          <span class="text-gray-600 font-medium">Adicionar Fotos</span>
          <span class="text-gray-400 text-sm">JPG, PNG ou WebP até 5MB</span>
        </button>
      </section>

      <!-- Description -->
      <section class="bg-white p-6 rounded-lg shadow-sm border">
        <h2 class="text-xl font-semibold text-gray-900 mb-4">Descrição</h2>

        <div>
          <label for="description" class="block text-sm font-medium text-gray-700 mb-1">
            Conte a história do animal *
          </label>
          <textarea
            id="description"
            v-model="form.description"
            required
            rows="5"
            minlength="10"
            maxlength="5000"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            placeholder="Descreva a personalidade, história e características do animal..."
          ></textarea>
          <p class="text-xs text-gray-500 mt-1">{{ form.description.length }}/5000 caracteres</p>
        </div>

        <div class="mt-4">
          <label for="special_needs" class="block text-sm font-medium text-gray-700 mb-1">
            Necessidades Especiais
          </label>
          <textarea
            id="special_needs"
            v-model="form.special_needs"
            rows="3"
            maxlength="1000"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            placeholder="Informe se o animal tem alguma necessidade especial, condição médica, etc."
          ></textarea>
        </div>
      </section>

      <!-- Traits -->
      <section class="bg-white p-6 rounded-lg shadow-sm border">
        <h2 class="text-xl font-semibold text-gray-900 mb-4">Características</h2>
        <p class="text-sm text-gray-600 mb-4">Selecione as características que se aplicam:</p>

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
          <!-- Location -->
          <div>
            <label for="location" class="block text-sm font-medium text-gray-700 mb-1">
              Cidade/Regiao *
            </label>
            <input
              id="location"
              v-model="form.location"
              type="text"
              required
              maxlength="100"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              placeholder="Ex: Sao Paulo - SP"
            />
          </div>

          <p class="text-sm text-gray-600">Informe pelo menos um meio de contato:</p>

          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <!-- Phone -->
            <div>
              <label for="phone" class="block text-sm font-medium text-gray-700 mb-1">
                Telefone
              </label>
              <input
                id="phone"
                v-model="form.contact_info.phone"
                type="tel"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                placeholder="(11) 99999-9999"
              />
            </div>

            <!-- Email -->
            <div>
              <label for="email" class="block text-sm font-medium text-gray-700 mb-1">
                E-mail
              </label>
              <input
                id="email"
                v-model="form.contact_info.email"
                type="email"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                placeholder="email@exemplo.com"
              />
            </div>

            <!-- WhatsApp -->
            <div>
              <label for="whatsapp" class="block text-sm font-medium text-gray-700 mb-1">
                WhatsApp
              </label>
              <input
                id="whatsapp"
                v-model="form.contact_info.whatsapp"
                type="tel"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                placeholder="(11) 99999-9999"
              />
            </div>
          </div>
        </div>
      </section>

      <!-- Edit Key -->
      <section class="bg-white p-6 rounded-lg shadow-sm border">
        <h2 class="text-xl font-semibold text-gray-900 mb-4">Chave de Edicao</h2>
        <p class="text-sm text-gray-600 mb-4">
          Crie uma chave secreta para poder editar este cadastro no futuro.
          Guarde essa chave em um local seguro, pois ela sera necessaria para fazer alteracoes.
        </p>

        <div>
          <label for="edit_key" class="block text-sm font-medium text-gray-700 mb-1">
            Chave de Edicao *
          </label>
          <input
            id="edit_key"
            v-model="form.edit_key"
            type="password"
            required
            minlength="6"
            maxlength="50"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            placeholder="Minimo 6 caracteres"
          />
          <p class="text-xs text-gray-500 mt-1">
            Esta chave sera criptografada e nao podera ser recuperada. Anote-a!
          </p>
        </div>
      </section>

      <!-- Submit -->
      <div class="flex justify-end gap-4">
        <NuxtLink
          to="/animais"
          class="px-6 py-3 border border-gray-300 rounded-lg text-gray-700 font-medium hover:bg-gray-50 transition-colors"
        >
          Cancelar
        </NuxtLink>
        <button
          type="submit"
          :disabled="isSubmitting"
          class="px-6 py-3 bg-purple-600 text-white rounded-lg font-medium hover:bg-purple-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {{ isSubmitting ? 'Cadastrando...' : 'Cadastrar Animal' }}
        </button>
      </div>
    </form>
  </div>
</template>
