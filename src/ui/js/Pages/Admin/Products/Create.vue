<script setup>
import { ref } from 'vue'
import { useForm, router } from '@inertiajs/vue3'
import AdminLayout from '@/Layouts/AdminLayout.vue'
import { ArrowLeft, Plus, Trash2, X } from 'lucide-vue-next'

const props = defineProps({
  categories: Array,
  suppliers:  Array,
  attributes: Array,
})

const form = useForm({
  name:              '',
  sku:               '',
  tax_code:          '',
  description:       '',
  short_description: '',
  category_name:     '',
  category_id:       '',
  supplier_name:     '',
  supplier_id:       '',
  origin:            '',
  variants: [
    { 
      sku: '', 
      unit: '',
      cost_price: '',
      selling_price: '', 
      quantity: 0, 
      is_default: true 
    }
  ],
})

// Fuzzy search helper
function removeDiacritics(str) {
    return str.normalize('NFD').replace(/[\u0300-\u036f]/g, '')
}

function fuzzyScore(search, target) {
    const searchLower = removeDiacritics(search.toLowerCase())
    const targetLower = removeDiacritics(target.toLowerCase())
    
    if (targetLower === searchLower) return 100
    if (targetLower.includes(searchLower)) return 50
    
    const searchWords = searchLower.split(/\s+/)
    const targetWords = targetLower.split(/\s+/)
    
    let score = 0
    for (const sw of searchWords) {
        for (const tw of targetWords) {
            if (tw.startsWith(sw)) score += 20
            else if (tw.includes(sw)) score += 10
        }
    }
    
    return score
}

// Autocomplete cho danh mục
const showCategorySuggestions = ref(false)
const filteredCategories = ref([])
const categoryError = ref('')
const categoryDropdownPosition = ref({ left: 0, top: 0 })
const categoryInputRef = ref(null)

function onCategoryInput(value, event) {
    categoryError.value = ''
    
    if (!value || value.length < 1) {
        showCategorySuggestions.value = false
        form.category_id = ''
        return
    }
    
    const results = props.categories?.map(c => ({
        ...c,
        score: fuzzyScore(value, c.name)
    }))
    .filter(c => c.score > 0)
    .sort((a, b) => b.score - a.score)
    .slice(0, 10) || []
    
    filteredCategories.value = results
    showCategorySuggestions.value = results.length > 0
    
    // Calculate dropdown position (to the right of input)
    if (results.length > 0 && event) {
        setTimeout(() => {
            const input = event.target
            if (input) {
                const rect = input.getBoundingClientRect()
                categoryDropdownPosition.value = {
                    left: rect.right + 8, // 8px margin
                    top: rect.top
                }
            }
        }, 0)
    }
    
    // Check if exact match exists
    const exactMatch = props.categories?.find(c => 
        removeDiacritics(c.name.toLowerCase()) === removeDiacritics(value.toLowerCase())
    )
    
    if (!exactMatch && value.length > 2) {
        form.category_id = ''
    }
}

function selectCategory(category) {
    form.category_name = category.name
    form.category_id = category.id
    categoryError.value = ''
    showCategorySuggestions.value = false
}

function closeCategoryDropdown() {
    setTimeout(() => {
        showCategorySuggestions.value = false
        
        // Validate on blur
        if (form.category_name && !form.category_id) {
            categoryError.value = 'Danh mục không tồn tại. Vui lòng chọn từ danh sách hoặc tạo mới.'
        }
    }, 200)
}

// Modal thêm danh mục mới
const showCategoryModal = ref(false)
const categoryImagePreview = ref(null)
const newCategoryForm = useForm({
    name: '',
    parent_id: null,
    img_url: null,
})

// Custom dropdown cho danh mục cha trong modal
const showParentDropdown = ref(false)
const selectedParentLabel = ref('Không có (danh mục gốc)')

function selectParentCategory(cat) {
    if (cat === null) {
        newCategoryForm.parent_id = null
        selectedParentLabel.value = 'Không có (danh mục gốc)'
    } else {
        newCategoryForm.parent_id = cat.id
        selectedParentLabel.value = cat.name.replace(/^[│├└─\s]+/, '')
    }
    showParentDropdown.value = false
}

function openCategoryModal() {
    newCategoryForm.reset()
    categoryImagePreview.value = null
    selectedParentLabel.value = 'Không có (danh mục gốc)'
    showParentDropdown.value = false
    showCategoryModal.value = true
}

function handleCategoryImageUpload(event) {
    const file = event.target.files[0]
    if (file) {
        newCategoryForm.img_url = file
        // Create preview
        const reader = new FileReader()
        reader.onload = (e) => {
            categoryImagePreview.value = e.target.result
        }
        reader.readAsDataURL(file)
    }
}

function removeCategoryImage() {
    newCategoryForm.img_url = null
    categoryImagePreview.value = null
}

function createCategory() {
    newCategoryForm.post('/admin/categories', {
        preserveScroll: true,
        onSuccess: (page) => {
            showCategoryModal.value = false
            
            // Reload the page to get updated categories list
            router.reload({
                only: ['categories'],
                onSuccess: (page) => {
                    // Get the newly created category from flash
                    const newCategory = page.props.flash?.category
                    if (newCategory) {
                        // Set as selected
                        form.category_name = newCategory.name
                        form.category_id = newCategory.id
                        categoryError.value = ''
                    }
                }
            })
        }
    })
}

// Autocomplete cho nhà cung cấp
const showSupplierSuggestions = ref(false)
const filteredSuppliers = ref([])
const supplierError = ref('')
const supplierDropdownPosition = ref({ left: 0, top: 0 })
const supplierInputRef = ref(null)

function onSupplierInput(value, event) {
    supplierError.value = ''
    
    if (!value || value.length < 1) {
        showSupplierSuggestions.value = false
        form.supplier_id = ''
        return
    }
    
    const results = props.suppliers?.map(s => ({
        ...s,
        score: fuzzyScore(value, s.name)
    }))
    .filter(s => s.score > 0)
    .sort((a, b) => b.score - a.score)
    .slice(0, 10) || []
    
    filteredSuppliers.value = results
    showSupplierSuggestions.value = results.length > 0
    
    // Calculate dropdown position (to the right of input)
    if (results.length > 0 && event) {
        setTimeout(() => {
            const input = event.target
            if (input) {
                const rect = input.getBoundingClientRect()
                supplierDropdownPosition.value = {
                    left: rect.right + 8,
                    top: rect.top
                }
            }
        }, 0)
    }
    
    // Check if exact match exists
    const exactMatch = props.suppliers?.find(s => 
        removeDiacritics(s.name.toLowerCase()) === removeDiacritics(value.toLowerCase())
    )
    
    if (!exactMatch && value.length > 2) {
        form.supplier_id = ''
    }
}

function selectSupplier(supplier) {
    form.supplier_name = supplier.name
    form.supplier_id = supplier.id
    supplierError.value = ''
    showSupplierSuggestions.value = false
}

function closeSupplierDropdown() {
    setTimeout(() => {
        showSupplierSuggestions.value = false
        
        // Validate on blur
        if (form.supplier_name && !form.supplier_id) {
            supplierError.value = 'Nhà cung cấp không tồn tại. Vui lòng chọn từ danh sách.'
        }
    }, 200)
}

function addVariant() {
  form.variants.push({ 
    sku: '', 
    unit: '',
    cost_price: '',
    selling_price: '', 
    quantity: 0, 
    is_default: false 
  })
}

function removeVariant(index) {
  if (form.variants.length === 1) return
  form.variants.splice(index, 1)
  // Ensure at least one is_default
  if (!form.variants.some(v => v.is_default)) {
    form.variants[0].is_default = true
  }
}

function setDefault(index) {
  form.variants.forEach((v, i) => { v.is_default = i === index })
}

function submit() {
  // Clear errors
  categoryError.value = ''
  supplierError.value = ''
  
  // Validate category
  if (form.category_name && !form.category_id) {
    categoryError.value = 'Danh mục không hợp lệ. Vui lòng chọn từ danh sách.'
    return
  }
  
  // Validate supplier
  if (form.supplier_name && !form.supplier_id) {
    supplierError.value = 'Nhà cung cấp không hợp lệ. Vui lòng chọn từ danh sách.'
    return
  }
  
  form.post('/admin/products')
}
</script>

<template>
  <AdminLayout>
    <div class="space-y-6">
      <button @click="router.visit('/admin/products')" class="flex items-center gap-2 text-sm text-gray-500 hover:text-gray-700">
        <ArrowLeft :size="16" /> Quay lại danh sách
      </button>

      <h1 class="text-2xl font-bold text-gray-900">Thêm sản phẩm mới</h1>

      <form @submit.prevent="submit" class="space-y-6">
        <!-- Basic info -->
        <div class="rounded-xl border border-gray-200 bg-white p-3 lg:p-5 shadow-sm space-y-4">
          <h2 class="font-semibold text-gray-900">Thông tin cơ bản</h2>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Tên sản phẩm <span class="text-red-500">*</span></label>
            <input v-model="form.name" type="text" required :class="['w-full rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500', form.errors.name ? 'border-red-300' : 'border-gray-300']" />
            <p v-if="form.errors.name" class="mt-1 text-xs text-red-600">{{ form.errors.name }}</p>
          </div>

          <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Mã sản phẩm (SKU)</label>
              <input v-model="form.sku" type="text" placeholder="VD: SP-001" class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Mã số thuế</label>
              <input v-model="form.tax_code" type="text" placeholder="VD: 0123456789" class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
            </div>
          </div>

          <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div class="relative">
              <label class="block text-sm font-medium text-gray-700 mb-1">Danh mục</label>
              <div class="flex gap-2">
                <div class="relative flex-1">
                  <input 
                    ref="categoryInputRef"
                    v-model="form.category_name" 
                    @input="onCategoryInput(form.category_name, $event)"
                    @blur="closeCategoryDropdown"
                    @focus="onCategoryInput(form.category_name, $event)"
                    type="text"
                    placeholder="Nhập tên danh mục..."
                    :class="['w-full rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500', categoryError ? 'border-red-300' : 'border-gray-300']" />
                  
                  <!-- Dropdown gợi ý danh mục - LUÔN hiển thị bên phải (dạng chữ L) -->
                  <div v-if="showCategorySuggestions" 
                    style="position: fixed; z-index: 9999;"
                    :style="{ left: categoryDropdownPosition.left + 'px', top: categoryDropdownPosition.top + 'px' }"
                    class="w-80 max-h-96 overflow-y-auto bg-white border border-gray-300 rounded-lg shadow-xl">
                    <button
                      v-for="cat in filteredCategories"
                      :key="cat.id"
                      type="button"
                      @mousedown.prevent="selectCategory(cat)"
                      class="w-full text-left px-3 py-2 text-sm hover:bg-indigo-50 border-b border-gray-100 last:border-0">
                      {{ cat.name }}
                    </button>
                  </div>
                </div>
                <button 
                  type="button"
                  @click="openCategoryModal"
                  class="flex items-center justify-center w-10 h-10 rounded-lg border border-indigo-300 text-indigo-600 hover:bg-indigo-50">
                  <Plus :size="18" />
                </button>
              </div>
              <p v-if="categoryError" class="mt-1 text-xs text-red-600">{{ categoryError }}</p>
            </div>
            <div class="relative">
              <label class="block text-sm font-medium text-gray-700 mb-1">Nhà cung cấp</label>
              <div class="flex gap-2">
                <div class="relative flex-1">
                  <input 
                    ref="supplierInputRef"
                    v-model="form.supplier_name" 
                    @input="onSupplierInput(form.supplier_name, $event)"
                    @blur="closeSupplierDropdown"
                    @focus="onSupplierInput(form.supplier_name, $event)"
                    type="text"
                    placeholder="Nhập tên nhà cung cấp..."
                    :class="['w-full rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500', supplierError ? 'border-red-300' : 'border-gray-300']" />
                  
                  <!-- Dropdown gợi ý nhà cung cấp -->
                  <div v-if="showSupplierSuggestions" 
                    style="position: fixed; z-index: 9999;"
                    :style="{ left: supplierDropdownPosition.left + 'px', top: supplierDropdownPosition.top + 'px' }"
                    class="w-80 max-h-96 overflow-y-auto bg-white border border-gray-300 rounded-lg shadow-xl">
                    <button
                      v-for="supplier in filteredSuppliers"
                      :key="supplier.id"
                      type="button"
                      @mousedown.prevent="selectSupplier(supplier)"
                      class="w-full text-left px-3 py-2 text-sm hover:bg-indigo-50 border-b border-gray-100 last:border-0">
                      {{ supplier.name }}
                    </button>
                  </div>
                </div>
              </div>
              <p v-if="supplierError" class="mt-1 text-xs text-red-600">{{ supplierError }}</p>
            </div>
          </div>

          <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Xuất xứ</label>
              <input v-model="form.origin" type="text" placeholder="VD: Việt Nam, Trung Quốc..." class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Mã số thuế</label>
              <input v-model="form.tax_code" type="text" placeholder="VD: 0123456789" class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Mô tả ngắn</label>
            <textarea v-model="form.short_description" rows="2" class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Mô tả chi tiết</label>
            <textarea v-model="form.description" rows="4" class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
          </div>
        </div>

        <!-- Variants -->
        <div class="rounded-xl border border-gray-200 bg-white p-3 lg:p-5 shadow-sm space-y-4">
          <div class="flex items-center justify-between">
            <h2 class="font-semibold text-gray-900">Biến thể sản phẩm</h2>
            <button type="button" @click="addVariant" class="flex items-center gap-1 rounded-lg border border-indigo-300 px-3 py-1.5 text-xs font-medium text-indigo-600 hover:bg-indigo-50">
              <Plus :size="12" /> Thêm biến thể
            </button>
          </div>

          <div v-for="(variant, index) in form.variants" :key="index" class="rounded-lg border border-gray-200 p-4 space-y-3">
            <div class="flex items-center justify-between">
              <span class="text-sm font-medium text-gray-700">Biến thể {{ index + 1 }}</span>
              <div class="flex items-center gap-3">
                <label class="flex items-center gap-1.5 text-xs text-gray-600 cursor-pointer">
                  <input type="radio" :name="'default'" :checked="variant.is_default" @change="setDefault(index)" class="text-indigo-600" />
                  Mặc định
                </label>
                <button v-if="form.variants.length > 1" type="button" @click="removeVariant(index)" class="text-red-500 hover:text-red-700">
                  <Trash2 :size="14" />
                </button>
              </div>
            </div>
            <div class="grid grid-cols-2 gap-3 sm:grid-cols-5">
              <div>
                <label class="block text-xs font-medium text-gray-600 mb-1">SKU <span class="text-red-500">*</span></label>
                <input v-model="variant.sku" type="text" required placeholder="VD: SP-001-XL" :class="['w-full rounded-lg border px-2 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500', form.errors[`variants.${index}.sku`] ? 'border-red-300' : 'border-gray-300']" />
              </div>
              <div>
                <label class="block text-xs font-medium text-gray-600 mb-1">Đơn vị</label>
                <input v-model="variant.unit" type="text" placeholder="Cái, Mét..." class="w-full rounded-lg border border-gray-300 px-2 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500" />
              </div>
              <div>
                <label class="block text-xs font-medium text-gray-600 mb-1">Giá nhập</label>
                <input v-model="variant.cost_price" type="number" step="1000" min="0" placeholder="0" class="w-full rounded-lg border border-gray-300 px-2 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500" />
              </div>
              <div>
                <label class="block text-xs font-medium text-gray-600 mb-1">Giá bán <span class="text-red-500">*</span></label>
                <input v-model="variant.selling_price" type="number" step="1000" min="0" required placeholder="0" :class="['w-full rounded-lg border px-2 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500', form.errors[`variants.${index}.selling_price`] ? 'border-red-300' : 'border-gray-300']" />
              </div>
              <div>
                <label class="block text-xs font-medium text-gray-600 mb-1">Tồn kho</label>
                <input v-model="variant.quantity" type="number" min="0" placeholder="0" class="w-full rounded-lg border border-gray-300 px-2 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500" />
              </div>
            </div>
          </div>
        </div>

        <!-- Submit -->
        <div class="flex gap-3">
          <button type="submit" :disabled="form.processing" class="rounded-lg bg-indigo-600 px-6 py-2.5 text-sm font-semibold text-white hover:bg-indigo-700 disabled:opacity-60">
            {{ form.processing ? 'Đang tạo...' : 'Tạo sản phẩm' }}
          </button>
          <button type="button" @click="router.visit('/admin/products')" class="rounded-lg border border-gray-300 px-6 py-2.5 text-sm text-gray-700 hover:bg-gray-50">Hủy</button>
        </div>
      </form>
    </div>

    <!-- Modal thêm danh mục -->
    <div v-if="showCategoryModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div class="bg-white rounded-xl shadow-xl w-full max-w-md mx-4">
        <div class="flex items-center justify-between p-3 lg:p-5 border-b border-gray-200">
          <h3 class="text-lg font-semibold text-gray-900">Thêm danh mục mới</h3>
          <button @click="showCategoryModal = false" class="text-gray-400 hover:text-gray-600">
            <X :size="20" />
          </button>
        </div>
        <form @submit.prevent="createCategory" class="p-3 lg:p-5 space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Tên danh mục <span class="text-red-500">*</span></label>
            <input 
              v-model="newCategoryForm.name" 
              type="text" 
              required
              autofocus
              :class="['w-full rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500', newCategoryForm.errors.name ? 'border-red-300' : 'border-gray-300']" />
            <p v-if="newCategoryForm.errors.name" class="mt-1 text-xs text-red-600">{{ newCategoryForm.errors.name }}</p>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Danh mục cha</label>
            <div class="relative">
              <button
                type="button"
                @click="showParentDropdown = !showParentDropdown"
                class="w-full flex items-center justify-between rounded-lg border border-gray-300 px-3 py-2 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500 text-left"
              >
                <span class="text-gray-700">{{ selectedParentLabel }}</span>
                <svg class="w-4 h-4 text-gray-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
              </button>
              <div
                v-if="showParentDropdown"
                class="absolute z-50 mt-1 w-full bg-white border border-gray-200 rounded-lg shadow-lg max-h-56 overflow-y-auto"
              >
                <button
                  type="button"
                  @click="selectParentCategory(null)"
                  class="w-full text-left px-3 py-2 text-sm hover:bg-indigo-50 text-gray-500 italic border-b border-gray-100"
                >Không có (danh mục gốc)</button>
                <button
                  v-for="cat in categories"
                  :key="cat.id"
                  type="button"
                  @click="selectParentCategory(cat)"
                  :style="{ paddingLeft: (12 + cat.depth * 16) + 'px' }"
                  class="w-full text-left py-2 pr-3 text-sm hover:bg-indigo-50 text-gray-700 flex items-center gap-1"
                >
                  <span v-if="cat.depth > 0" class="text-gray-300 shrink-0">
                    {{ cat.depth > 1 ? '└─' : '└─' }}
                  </span>
                  <span>{{ cat.name.replace(/^[│├└─\s]+/, '') }}</span>
                </button>
              </div>
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Hình ảnh</label>
            <div v-if="categoryImagePreview" class="relative mb-3">
              <img :src="categoryImagePreview" alt="Preview" class="w-full h-40 object-cover rounded-lg border border-gray-300" />
              <button 
                type="button"
                @click="removeCategoryImage"
                class="absolute top-2 right-2 bg-red-500 text-white rounded-full p-1 hover:bg-red-600">
                <X :size="16" />
              </button>
            </div>
            <label class="flex items-center justify-center w-full px-4 py-3 border-2 border-dashed border-gray-300 rounded-lg cursor-pointer hover:border-indigo-400 hover:bg-indigo-50 transition">
              <div class="text-center">
                <Plus :size="20" class="mx-auto text-gray-400 mb-1" />
                <span class="text-sm text-gray-600">{{ categoryImagePreview ? 'Thay đổi ảnh' : 'Chọn ảnh' }}</span>
              </div>
              <input 
                type="file" 
                accept="image/*"
                @change="handleCategoryImageUpload"
                class="hidden" />
            </label>
            <p v-if="newCategoryForm.errors.img_url" class="mt-1 text-xs text-red-600">{{ newCategoryForm.errors.img_url }}</p>
          </div>
          <div class="flex gap-3 pt-2">
            <button 
              type="submit" 
              :disabled="newCategoryForm.processing"
              class="flex-1 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-700 disabled:opacity-60">
              {{ newCategoryForm.processing ? 'Đang tạo...' : 'Tạo danh mục' }}
            </button>
            <button 
              type="button" 
              @click="showCategoryModal = false"
              class="rounded-lg border border-gray-300 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50">
              Hủy
            </button>
          </div>
        </form>
      </div>
    </div>

  </AdminLayout>
</template>
