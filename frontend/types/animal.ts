// Enums matching backend
export enum Species {
  DOG = 'dog',
  CAT = 'cat',
  BIRD = 'bird',
  RODENT = 'rodent',
  OTHER = 'other',
}

export enum Size {
  SMALL = 'small',
  MEDIUM = 'medium',
  LARGE = 'large',
}

export enum Gender {
  MALE = 'male',
  FEMALE = 'female',
  UNKNOWN = 'unknown',
}

export enum AnimalStatus {
  AVAILABLE = 'available',
  IN_PROCESS = 'in_process',
  ADOPTED = 'adopted',
}

// Image types
export interface Image {
  id: string
  original_url: string
  thumbnail_url: string
  is_primary: boolean
  order: number
}

// Animal types
export interface Animal {
  id: string
  name: string
  species: Species
  breed?: string
  age_months?: number
  size: Size
  gender: Gender
  description: string
  status: AnimalStatus
  traits: string[]
  special_needs?: string
  location: string
  contact_info: Record<string, string>
  created_at: string
  updated_at: string
  images: Image[]
}

export interface AnimalListItem {
  id: string
  name: string
  species: Species
  size: Size
  gender: Gender
  age_months?: number
  location: string
  status: AnimalStatus
  primary_image?: Image
  created_at: string
}

export interface AnimalFeedItem {
  id: string
  name: string
  species: Species
  size: Size
  gender: Gender
  age_months?: number
  description: string
  location: string
  status: AnimalStatus
  images: Image[]
  created_at: string
}

export interface AnimalCreate {
  name: string
  species: Species
  breed?: string
  age_months?: number
  size: Size
  gender: Gender
  description: string
  traits?: string[]
  special_needs?: string
  location: string
  contact_info: Record<string, string>
  status?: AnimalStatus
  edit_key: string
}

export interface AnimalUpdate {
  name?: string
  species?: Species
  breed?: string
  age_months?: number
  size?: Size
  gender?: Gender
  description?: string
  traits?: string[]
  special_needs?: string
  location?: string
  contact_info?: Record<string, string>
  status?: AnimalStatus
}

export interface AnimalFilters {
  species?: Species
  size?: Size
  gender?: Gender
  status?: AnimalStatus
  location?: string
  min_age_months?: number
  max_age_months?: number
  search?: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  pages: number
}
