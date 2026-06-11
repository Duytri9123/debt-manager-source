<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { useForm, router } from '@inertiajs/vue3'
import AdminLayout from '@/Layouts/AdminLayout.vue'
import { ArrowLeft, Plus, Trash2 } from 'lucide-vue-next'

const props = defineProps({
  product:    Object,
  categories: Array,
  suppliers:  Array,
  attributes: Array,
})

const form = useForm({
  name:              props.product.name,
  description:       props.product.description ?? '',
  short_description: props.product.short_description ?? '',
  tax_code:          props.product.tax_code ?? '',
  category_id:       props.product.category?.id ?? '',
  supplier_id:       props.product.supplier?.id ?? '',
  origin:            props.product.origin ?? '',
  variants: props.product.variants?.length
    ? props.product.variants.map(v => ({
        id:             v.id,
        sku:            v.sku,
        selling_price:  v.selling_price,
        original_price: v.original_price,
        quantity:       v.quantity,
        is_default:     v.is_default,
      }))
    : [{ sku: '', selling_price: '', original_price: '', quantity: 0, is_default: true }],
})

// ── Undo / Redo ──────────────────────────────────────────────────────────────
const TRACKED_FIELDS = ['name', 'description', 'short_description', 'tax_code', 'category_id', 'supplier_id', 'origin', 'variants']

function snapshot() {
  return JSON.parse(JSON.stringify(
    Object.fromEntries(TRACKED_FIELDS.map(k => [k, form[k]]))
  ))
}

function applySnapshot(state) {
  for (const key of TRACKED_FIELDS) {
    if (key === 'variants') {
      form.variants.splice(0, form.variants.length, ...JSON.parse(JSON.stringify(state.variants)))
    } else {
      form[key] = state[key]
    }
  }
}

const history = ref([snapshot()])
const historyIndex = ref(0)
let isApplying = false

// Watch all tracked fields and push to history on change
watch(
  () => snapshot(),
  (newVal) => {
    if (isApplying) return
    const current = JSON.stringify(history.value[historyIndex.value])
    if (JSON.stringify(newVal) === current) return
    // Drop any redo states ahead
    history.value.splice(historyIndex.value + 1)
    history.value.push(newVal)
    historyIndex.value = history.value.length - 1
  },
  { deep: true }
)

function undo() {
  if (historyIndex.value <= 0) return
  historyIndex.value--
  isApplying = true
  applySnapshot(history.value[historyIndex.value])
  isApplying = false
}

function redo() {
  if (historyIndex.value >= history.value.length - 1) return
  historyIndex.value++
  isApplying = true
  applySnapshot(history.value[historyIndex.value])
  isApplying = false
}

function handleKeydown(e) {
  const tag = document.activeElement?.tagName
  // Let native undo/redo work inside text inputs & textareas
  if (tag === 'INPUT' || tag === 'TEXTAREA') return

  if (e.key === 'z' && (e.ctrlKey || e.metaKey)) {
    if (e.shiftKey) {
      e.preventDefault()
      redo()
    } else {
      e.preventDefault()
      undo()
    }
  }
}

onMounted(() => window.addEventListener('keydown', handleKeydown))
onUnmounted(() => window.removeEventListener('keydown', handleKeydown))
// ─────────────────────────────────────────────────────────────────────────────

function addVariant() {
  form.variants.push({ id: null, sku: '', selling_price: '', original_price: '', quantity: 0, is_default: false })
}

function removeVariant(index) {
  if (form.variants.length === 1) return
  form.variants.splice(index, 1)
  if (!form.variants.some(v => v.is_default)) {
    form.variants[0].is_default = true
  }
}

function setDefault(index) {
  form.variants.forEach((v, i) => { v.is_default = i === index })
}

function submit() {
  form.put(`/admin/products/${props.product.id}`)
}

function getImageUrl(product) {
  const url = product.thumbnail_image?.url
  if (!url) return null
  if (url.startsWith('http')) return url
  return `/storage/${url}`
}
</script>

<template>
  <AdminLayout>
    <div class="space-y-6">
      <button @click="router.visit('/admin/products')" class="flex items-center gap-2 text-sm text-gray-500 hover:text-gray-700">
        <ArrowLeft :size="16" /> Quay lại danh sách
      </button>

      <div class="flex items-center justify-between gap-4">
        <div class="flex items-center gap-4">
          <div v-if="getImageUrl(product)" class="h-12 w-12 rounded-lg overflow-hidden bg-gray-100 shrink-0">
            <img :src="getImageUrl(product)" :alt="product.name" class="h-full w-full object-cover" />
          </div>
          <h1 class="text-2xl font-bold text-gray-900">{{ product.name }}</h1>
        </div>
        <!-- Undo / Redo buttons -->
        <div class="flex items-center gap-1">
          <button
            type="button"
            @click="undo"
            :disabled="historyIndex <= 0"
            title="Hoàn tác (Ctrl+Z)"
            class="rounded-lg border border-gray-200 p-1.5 text-gray-500 hover:bg-gray-100 disabled:opacity-30 disabled:cursor-not-allowed"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 7v6h6"/><path d="M21 17a9 9 0 0 0-9-9 9 9 0 0 0-6 2.3L3 13"/></svg>
          </button>
          <button
            type="button"
            @click="redo"
            :disabled="historyIndex >= history.length - 1"
            title="Làm lại (Ctrl+Shift+Z)"
            class="rounded-lg border border-gray-200 p-1.5 text-gray-500 hover:bg-gray-100 disabled:opacity-30 disabled:cursor-not-allowed"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 7v6h-6"/><path d="M3 17a9 9 0 0 1 9-9 9 9 0 0 1 6 2.3L21 13"/></svg>
          </button>
        </div>
      </div>

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
              <label class="block text-sm font-medium text-gray-700 mb-1">Danh mục</label>
              <select v-model="form.category_id" class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                <option value="">Chọn danh mục</option>
                <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Nhà cung cấp</label>
              <select v-model="form.supplier_id" class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                <option value="">Chọn nhà cung cấp</option>
                <option v-for="supplier in suppliers" :key="supplier.id" :value="supplier.id">{{ supplier.name }}</option>
              </select>
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

          <div v-for="(variant, index) in form.variants" :key="variant.id ?? index" class="rounded-lg border border-gray-200 p-4 space-y-3">
            <div class="flex items-center justify-between">
              <span class="text-sm font-medium text-gray-700">Biến thể {{ index + 1 }}</span>
              <div class="flex items-center gap-3">
                <label class="flex items-center gap-1.5 text-xs text-gray-600 cursor-pointer">
                  <input type="radio" name="default" :checked="variant.is_default" @change="setDefault(index)" class="text-indigo-600" />
                  Mặc định
                </label>
                <button v-if="form.variants.length > 1" type="button" @click="removeVariant(index)" class="text-red-500 hover:text-red-700">
                  <Trash2 :size="14" />
                </button>
              </div>
            </div>
            <div class="grid grid-cols-2 gap-3 sm:grid-cols-4">
              <div>
                <label class="block text-xs font-medium text-gray-600 mb-1">SKU <span class="text-red-500">*</span></label>
                <input v-model="variant.sku" type="text" required :class="['w-full rounded-lg border px-2 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500', form.errors[`variants.${index}.sku`] ? 'border-red-300' : 'border-gray-300']" />
              </div>
              <div>
                <label class="block text-xs font-medium text-gray-600 mb-1">Giá bán <span class="text-red-500">*</span></label>
                <input v-model="variant.selling_price" type="number" step="1000" min="0" required :class="['w-full rounded-lg border px-2 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500', form.errors[`variants.${index}.selling_price`] ? 'border-red-300' : 'border-gray-300']" />
              </div>
              <div>
                <label class="block text-xs font-medium text-gray-600 mb-1">Giá gốc</label>
                <input v-model="variant.original_price" type="number" step="1000" min="0" class="w-full rounded-lg border border-gray-300 px-2 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500" />
              </div>
              <div>
                <label class="block text-xs font-medium text-gray-600 mb-1">Tồn kho</label>
                <input v-model="variant.quantity" type="number" min="0" class="w-full rounded-lg border border-gray-300 px-2 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500" />
              </div>
            </div>
          </div>
        </div>

        <!-- Submit -->
        <div class="flex gap-3">
          <button type="submit" :disabled="form.processing" class="rounded-lg bg-indigo-600 px-6 py-2.5 text-sm font-semibold text-white hover:bg-indigo-700 disabled:opacity-60">
            {{ form.processing ? 'Đang lưu...' : 'Lưu thay đổi' }}
          </button>
          <button type="button" @click="router.visit('/admin/products')" class="rounded-lg border border-gray-300 px-6 py-2.5 text-sm text-gray-700 hover:bg-gray-50">Hủy</button>
        </div>
      </form>
    </div>
  </AdminLayout>
</template>
