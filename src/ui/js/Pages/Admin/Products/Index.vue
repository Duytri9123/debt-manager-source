<script setup>
import { ref, onMounted } from 'vue'
import { router } from '@inertiajs/vue3'
import AdminLayout from '@/Layouts/AdminLayout.vue'
import { useFilters } from '@/composables/useFilters.js'
import { useCurrency } from '@/composables/useCurrency.js'
import { Search, Grid, List, Plus, MoreVertical, Edit, Trash2, Eye } from 'lucide-vue-next'

const props = defineProps({
  products:   Object,
  categories: Array,
  filters:    Object,
})

const { formatVND } = useCurrency()
const { filters, applyFilters, resetFilters } = useFilters(
  { search: props.filters?.search ?? '', category_id: props.filters?.category_id ?? '', status: props.filters?.status ?? '' },
  '/admin/products'
)

const viewMode = ref('list')
onMounted(() => { viewMode.value = localStorage.getItem('admin-products-view') ?? 'list' })
function setView(mode) { viewMode.value = mode; localStorage.setItem('admin-products-view', mode) }

// Dropdown
const openMenuId = ref(null)
function toggleMenu(id, e) { e.stopPropagation(); openMenuId.value = openMenuId.value === id ? null : id }
function closeMenu() { openMenuId.value = null }

const STATUS_LABELS  = { active: 'Đang bán', inactive: 'Ngừng bán', draft: 'Nháp' }
const STATUS_CLASSES = { active: 'bg-emerald-100 text-emerald-700', inactive: 'bg-gray-100 text-gray-600', draft: 'bg-amber-100 text-amber-700' }

function deleteProduct(product, e) {
  e?.stopPropagation(); closeMenu()
  if (!confirm(`Xóa sản phẩm "${product.name}"?`)) return
  router.delete(`/admin/products/${product.id}`)
}

function getImageUrl(product) {
  const url = product.thumbnail_image?.url
  if (!url) return null
  return url.startsWith('http') ? url : `/storage/${url}`
}
</script>

<template>
  <AdminLayout>
    <div class="space-y-5" @click="closeMenu">

      <!-- Header -->
      <div class="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 class="text-xl font-bold text-gray-900">Sản phẩm</h1>
          <p class="mt-0.5 text-sm text-gray-500">Quản lý danh mục sản phẩm</p>
        </div>
        <div class="flex items-center gap-2">
          <div class="flex rounded-lg border border-gray-200 bg-white p-1">
            <button @click="setView('grid')" :class="['flex items-center gap-1 rounded px-2 py-1.5 text-xs font-medium transition-colors', viewMode === 'grid' ? 'bg-indigo-600 text-white' : 'text-gray-600 hover:text-gray-800']">
              <Grid :size="12" /> Lưới
            </button>
            <button @click="setView('list')" :class="['flex items-center gap-1 rounded px-2 py-1.5 text-xs font-medium transition-colors', viewMode === 'list' ? 'bg-indigo-600 text-white' : 'text-gray-600 hover:text-gray-800']">
              <List :size="12" /> Danh sách
            </button>
          </div>
          <button @click="router.visit('/admin/products/create')"
            class="flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-700 transition-colors">
            <Plus :size="16" /> Thêm sản phẩm
          </button>
        </div>
      </div>

      <!-- Filters -->
      <div class="flex flex-wrap gap-3 bg-white rounded-xl border border-gray-200 p-3">
        <div class="relative flex-1 min-w-48">
          <Search :size="15" class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input v-model="filters.search" @input="applyFilters()" type="text" placeholder="Tìm sản phẩm..."
            class="w-full rounded-lg border border-gray-200 pl-9 pr-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
        </div>
        <select v-model="filters.category_id" @change="applyFilters(true)"
          class="rounded-lg border border-gray-200 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
          <option value="">Tất cả danh mục</option>
          <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
        </select>
        <select v-model="filters.status" @change="applyFilters(true)"
          class="rounded-lg border border-gray-200 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
          <option value="">Tất cả trạng thái</option>
          <option value="active">Đang bán</option>
          <option value="inactive">Ngừng bán</option>
          <option value="draft">Nháp</option>
        </select>
        <button v-if="filters.search || filters.category_id || filters.status" @click="resetFilters()"
          class="rounded-lg border border-gray-200 px-3 py-2 text-sm text-gray-600 hover:bg-gray-50 transition-colors">
          Xóa bộ lọc
        </button>
      </div>

      <!-- Grid view -->
      <div v-if="viewMode === 'grid'" class="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5">
        <div v-if="!products?.data?.length" class="col-span-full py-12 text-center text-sm text-gray-500">Không có sản phẩm nào</div>
        <div v-for="product in products?.data" :key="product.id"
          class="group rounded-xl border border-gray-200 bg-white shadow-sm overflow-hidden hover:shadow-md transition-shadow cursor-pointer"
          @click="router.visit(`/admin/products/${product.id}`)">
          <div class="aspect-square bg-gray-100 overflow-hidden">
            <img v-if="getImageUrl(product)" :src="getImageUrl(product)" :alt="product.name"
              class="h-full w-full object-cover group-hover:scale-105 transition-transform duration-300" />
            <div v-else class="h-full w-full flex items-center justify-center text-gray-300">
              <svg class="h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
          </div>
          <div class="p-3">
            <p class="text-sm font-medium text-gray-900 truncate">{{ product.name }}</p>
            <p class="text-xs text-indigo-600 font-semibold mt-0.5">{{ formatVND(product.default_variant?.selling_price) }}</p>
            <div class="mt-2 flex items-center justify-between">
              <span :class="['inline-flex rounded-full px-1.5 py-0.5 text-xs font-medium', STATUS_CLASSES[product.status?.value ?? product.status]]">
                {{ STATUS_LABELS[product.status?.value ?? product.status] }}
              </span>
              <!-- Dropdown -->
              <div class="relative" @click.stop>
                <button @click="toggleMenu(product.id, $event)"
                  class="p-1 rounded-lg hover:bg-gray-100 text-gray-400 hover:text-gray-600 transition-colors">
                  <MoreVertical :size="14" />
                </button>
                <div v-if="openMenuId === product.id"
                  class="absolute right-0 bottom-full mb-1 z-20 w-36 bg-white rounded-xl shadow-lg border border-gray-200 py-1 text-sm">
                  <button @click="router.visit(`/admin/products/${product.id}`); closeMenu()"
                    class="w-full flex items-center gap-2 px-3 py-2 hover:bg-gray-50 text-gray-700 transition-colors">
                    <Eye :size="13" /> Xem chi tiết
                  </button>
                  <button @click="router.visit(`/admin/products/${product.id}/edit`); closeMenu()"
                    class="w-full flex items-center gap-2 px-3 py-2 hover:bg-indigo-50 text-indigo-600 transition-colors">
                    <Edit :size="13" /> Chỉnh sửa
                  </button>
                  <div class="border-t border-gray-100 my-1"></div>
                  <button @click="deleteProduct(product, $event)"
                    class="w-full flex items-center gap-2 px-3 py-2 hover:bg-red-50 text-red-600 transition-colors">
                    <Trash2 :size="13" /> Xóa sản phẩm
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- List view -->
      <div v-else class="overflow-x-auto rounded-xl border border-gray-200 bg-white shadow-sm">
        <div v-if="!products?.data?.length" class="px-6 py-12 text-center text-sm text-gray-500">Không có sản phẩm nào</div>
        <table v-else class="w-full text-sm">
          <thead class="bg-gray-50 text-left text-xs font-medium uppercase tracking-wide text-gray-500 border-b border-gray-200">
            <tr>
              <th class="px-4 py-3">Sản phẩm</th>
              <th class="px-4 py-3">Mã hàng</th>
              <th class="px-4 py-3 text-right">Giá nhập</th>
              <th class="px-4 py-3 text-right">Giá bán</th>
              <th class="px-4 py-3 text-right">Đã bán</th>
              <th class="px-4 py-3">Danh mục</th>
              <th class="px-4 py-3">Xuất xứ</th>
              <th class="px-4 py-3 text-right">Lãi/kg</th>
              <th class="px-4 py-3 w-10"></th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr v-for="product in products.data" :key="product.id"
              class="hover:bg-gray-50 cursor-pointer transition-colors"
              @click="router.visit(`/admin/products/${product.id}`)">
              <td class="px-4 py-3">
                <div class="flex items-center gap-3">
                  <div class="h-10 w-10 shrink-0 rounded-lg overflow-hidden bg-gray-100">
                    <img v-if="getImageUrl(product)" :src="getImageUrl(product)" :alt="product.name" class="h-full w-full object-cover" />
                    <div v-else class="h-full w-full flex items-center justify-center text-gray-300">
                      <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                      </svg>
                    </div>
                  </div>
                  <span class="font-medium text-gray-900 max-w-[300px] leading-snug">{{ product.name }}</span>
                </div>
              </td>
              <td class="px-4 py-3 text-gray-500 font-mono text-xs">{{ product.default_variant?.sku ?? '—' }}</td>
              <td class="px-4 py-3 text-right text-gray-500 text-xs">
                {{ product.default_variant?.cost_price ? formatVND(product.default_variant.cost_price) : '—' }}
              </td>
              <td class="px-4 py-3 text-right font-semibold text-indigo-600">{{ formatVND(product.default_variant?.selling_price) }}</td>
              <td class="px-4 py-3 text-right text-gray-600">{{ product.default_variant?.quantity ?? 0 }}</td>
              <td class="px-4 py-3 text-gray-500 text-xs">{{ product.category?.name ?? '—' }}</td>
              <td class="px-4 py-3 text-gray-500 text-xs">{{ product.default_variant?.origin ?? '—' }}</td>
              <td class="px-4 py-3 text-right text-emerald-600 font-medium text-xs">
                {{ product.default_variant?.profit_per_kg ? formatVND(product.default_variant.profit_per_kg) : '—' }}
              </td>
              <!-- 1 nút ⋯ -->
              <td class="px-4 py-3" @click.stop>
                <div class="relative flex justify-end">
                  <button @click="toggleMenu(product.id, $event)"
                    class="p-1.5 rounded-lg hover:bg-gray-100 text-gray-400 hover:text-gray-600 transition-colors">
                    <MoreVertical :size="15" />
                  </button>
                  <div v-if="openMenuId === product.id"
                    class="absolute right-0 top-full mt-1 z-20 w-40 bg-white rounded-xl shadow-lg border border-gray-200 py-1 text-sm">
                    <button @click="router.visit(`/admin/products/${product.id}`); closeMenu()"
                      class="w-full flex items-center gap-2 px-3 py-2 hover:bg-gray-50 text-gray-700 transition-colors">
                      <Eye :size="13" /> Xem chi tiết
                    </button>
                    <button @click="router.visit(`/admin/products/${product.id}/edit`); closeMenu()"
                      class="w-full flex items-center gap-2 px-3 py-2 hover:bg-indigo-50 text-indigo-600 transition-colors">
                      <Edit :size="13" /> Chỉnh sửa
                    </button>
                    <div class="border-t border-gray-100 my-1"></div>
                    <button @click="deleteProduct(product, $event)"
                      class="w-full flex items-center gap-2 px-3 py-2 hover:bg-red-50 text-red-600 transition-colors">
                      <Trash2 :size="13" /> Xóa sản phẩm
                    </button>
                  </div>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div v-if="products?.last_page > 1" class="flex items-center justify-between text-sm text-gray-600">
        <span>Trang {{ products.current_page }} / {{ products.last_page }} · {{ products.total }} sản phẩm</span>
        <div class="flex gap-2">
          <button :disabled="products.current_page === 1" @click="router.visit(products.prev_page_url)"
            class="rounded border border-gray-300 px-3 py-1 hover:bg-gray-50 disabled:opacity-40 transition-colors">Trước</button>
          <button :disabled="products.current_page === products.last_page" @click="router.visit(products.next_page_url)"
            class="rounded border border-gray-300 px-3 py-1 hover:bg-gray-50 disabled:opacity-40 transition-colors">Sau</button>
        </div>
      </div>
    </div>
  </AdminLayout>
</template>
