<script setup>
import { ref, computed } from 'vue'
import { router } from '@inertiajs/vue3'
import AdminLayout from '@/Layouts/AdminLayout.vue'
import { Search, ArrowUpDown, ArrowUp, ArrowDown, Plus, ChevronDown, Filter } from 'lucide-vue-next'

const props = defineProps({
  customers: Object,
  filters:   Object,
})

// ── Filters & Sort ────────────────────────────────────────────────────────────
const search    = ref(props.filters?.search    ?? '')
const phone       = ref(props.filters?.phone       ?? '')
const address     = ref(props.filters?.address     ?? '')
const has_debt    = ref(props.filters?.has_debt    ?? '')
const has_imports = ref(props.filters?.has_imports ?? '')
const role      = ref(props.filters?.role      ?? '')
const status    = ref(props.filters?.status    ?? '')
const sort      = ref(props.filters?.sort      ?? 'created_at')
const direction = ref(props.filters?.direction ?? 'desc')

const showFilters = ref({
  name:    !!props.filters?.search,
  phone:   !!props.filters?.phone,
  address: !!props.filters?.address,
  debt:    !!props.filters?.has_debt,
  imports: !!props.filters?.has_imports,
})

function toggleFilter(col) {
  showFilters.value[col] = !showFilters.value[col]
}

let searchTimer = null
function onSearch() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => applyFilters(), 300)
}

function applyFilters(resetPage = false) {
  router.get('/admin/customers', {
    search:    search.value    || undefined,
    phone:       phone.value       || undefined,
    address:     address.value     || undefined,
    has_debt:    has_debt.value    || undefined,
    has_imports: has_imports.value || undefined,
    role:      role.value      || undefined,
    status:    status.value    || undefined,
    sort:      sort.value      !== 'created_at' ? sort.value : undefined,
    direction: direction.value !== 'desc'       ? direction.value : undefined,
  }, { preserveState: true, replace: true })
}

function toggleSort(col) {
  if (sort.value === col) {
    direction.value = direction.value === 'asc' ? 'desc' : 'asc'
  } else {
    sort.value = col
    direction.value = 'asc'
  }
  applyFilters()
}

function resetFilters() {
  search.value = ''; phone.value = ''; address.value = ''; 
  has_debt.value = ''; has_imports.value = '';
  role.value = ''; status.value = ''
  sort.value = 'created_at'; direction.value = 'desc'
  router.get('/admin/customers', {}, { preserveState: false })
}

// ── Helpers ───────────────────────────────────────────────────────────────────
function formatDate(d) { return d ? new Date(d).toLocaleDateString('vi-VN') : '—' }
function formatVND(v)  { return Number(v || 0).toLocaleString('vi-VN', { style: 'currency', currency: 'VND' }) }
function initials(n)   { return n ? n.charAt(0).toUpperCase() : '?' }

const hasFilters = computed(() =>
  search.value || phone.value || address.value || 
  has_debt.value || has_imports.value ||
  role.value || status.value ||
  sort.value !== 'created_at' || direction.value !== 'desc'
)
</script>

<template>
  <AdminLayout>
    <div class="space-y-5">
      <!-- Header -->
      <div class="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 class="text-2xl font-bold text-gray-900">Hồ sơ Khách hàng</h1>
          <p class="mt-1 text-sm text-gray-500">
            {{ customers?.total ?? 0 }} khách hàng
          </p>
        </div>
        <button @click="router.visit('/admin/customers/create')"
          class="flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 transition-colors shrink-0 whitespace-nowrap">
          <Plus :size="16" /> Thêm khách hàng
        </button>
      </div>

      <!-- Search + Filters -->
      <div class="flex flex-wrap gap-3 items-center">
        <div class="relative flex-1 min-w-64">
          <Search :size="15" class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input v-model="search" @input="onSearch" type="text"
            placeholder="Tìm tên, SĐT, địa chỉ..."
            class="w-full rounded-lg border border-gray-300 pl-9 pr-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
        </div>

        <!-- Sort select -->
        <select v-model="sort" @change="applyFilters()"
          class="rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
          <option value="created_at">Sắp xếp: Ngày tạo</option>
          <option value="name">Sắp xếp: Tên</option>
          <option value="orders_count">Sắp xếp: Đơn hàng</option>
        </select>

        <!-- Direction -->
        <button @click="direction = direction === 'asc' ? 'desc' : 'asc'; applyFilters()"
          class="flex items-center gap-1.5 rounded-lg border border-gray-300 px-3 py-2 text-sm text-gray-600 hover:bg-gray-50 transition-colors">
          <ArrowUp v-if="direction === 'asc'" :size="14" />
          <ArrowDown v-else :size="14" />
          {{ direction === 'asc' ? 'Tăng dần' : 'Giảm dần' }}
        </button>

        <button v-if="hasFilters" @click="resetFilters"
          class="rounded-lg border border-gray-300 px-3 py-2 text-sm text-gray-500 hover:bg-gray-50 transition-colors">
          Xóa bộ lọc
        </button>
      </div>

      <!-- Table -->
      <div class="overflow-x-auto rounded-xl border border-gray-200 bg-white shadow-sm">
        <div v-if="!customers?.data?.length" class="px-6 py-12 text-center text-sm text-gray-500">
          Không có khách hàng nào
        </div>
        <table v-else class="w-full text-sm">
          <thead class="bg-gray-50 border-b border-gray-200">
            <tr>
              <!-- Tên khách hàng -->
              <th class="px-4 py-3 text-left relative whitespace-nowrap">
                <div class="flex items-center justify-between gap-1">
                  <button @click="toggleSort('name')"
                    class="flex items-center gap-1 text-xs font-semibold uppercase tracking-wide text-gray-500 hover:text-gray-800 transition-colors">
                    Khách hàng
                    <ArrowUpDown v-if="sort !== 'name'" :size="12" class="opacity-40" />
                    <ArrowUp v-else-if="direction === 'asc'" :size="12" class="text-indigo-600" />
                    <ArrowDown v-else :size="12" class="text-indigo-600" />
                  </button>
                  <button @click="toggleFilter('name')"
                    :class="['p-1 rounded hover:bg-gray-200 transition-colors', showFilters.name ? 'text-indigo-600 bg-indigo-50' : 'text-gray-400']">
                    <ChevronDown :size="14" />
                  </button>
                </div>
                <div v-if="showFilters.name" class="absolute left-0 top-full z-20 mt-1 w-48 rounded-lg border border-gray-200 bg-white p-2 shadow-xl">
                  <input v-model="search" @input="onSearch" type="text" placeholder="Tìm tên..."
                    class="w-full rounded border border-gray-300 px-2 py-1.5 text-xs focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                </div>
              </th>

              <!-- MST -->
              <th class="px-4 py-3 text-left whitespace-nowrap">
                <span class="text-xs font-semibold uppercase tracking-wide text-gray-500">MST</span>
              </th>

              <!-- Số điện thoại -->
              <th class="px-4 py-3 text-left relative whitespace-nowrap">
                <div class="flex items-center justify-between gap-1">
                  <span class="text-xs font-semibold uppercase tracking-wide text-gray-500">Số điện thoại</span>
                  <button @click="toggleFilter('phone')"
                    :class="['p-1 rounded hover:bg-gray-200 transition-colors', showFilters.phone ? 'text-indigo-600 bg-indigo-50' : 'text-gray-400']">
                    <ChevronDown :size="14" />
                  </button>
                </div>
                <div v-if="showFilters.phone" class="absolute left-0 top-full z-20 mt-1 w-40 rounded-lg border border-gray-200 bg-white p-2 shadow-xl">
                  <input v-model="phone" @input="onSearch" type="text" placeholder="Lọc SĐT..."
                    class="w-full rounded border border-gray-300 px-2 py-1.5 text-xs focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                </div>
              </th>

              <!-- Địa chỉ -->
              <th class="px-4 py-3 text-left relative whitespace-nowrap">
                <div class="flex items-center justify-between gap-1">
                  <span class="text-xs font-semibold uppercase tracking-wide text-gray-500">Địa chỉ</span>
                  <button @click="toggleFilter('address')"
                    :class="['p-1 rounded hover:bg-gray-200 transition-colors', showFilters.address ? 'text-indigo-600 bg-indigo-50' : 'text-gray-400']">
                    <ChevronDown :size="14" />
                  </button>
                </div>
                <div v-if="showFilters.address" class="absolute right-0 top-full z-20 mt-1 w-56 rounded-lg border border-gray-200 bg-white p-2 shadow-xl">
                  <input v-model="address" @input="onSearch" type="text" placeholder="Lọc địa chỉ..."
                    class="w-full rounded border border-gray-300 px-2 py-1.5 text-xs focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                </div>
              </th>

              <!-- Đơn hàng -->
              <th class="px-4 py-3 text-right whitespace-nowrap">
                <button @click="toggleSort('orders_count')"
                  class="flex items-center gap-1 text-xs font-semibold uppercase tracking-wide text-gray-500 hover:text-gray-800 transition-colors ml-auto">
                  Đơn hàng
                  <ArrowUpDown v-if="sort !== 'orders_count'" :size="12" class="opacity-40" />
                  <ArrowUp v-else-if="direction === 'asc'" :size="12" class="text-indigo-600" />
                  <ArrowDown v-else :size="12" class="text-indigo-600" />
                </button>
              </th>

              <!-- Nhập -->
              <th class="px-4 py-3 text-right relative whitespace-nowrap">
                <div class="flex items-center justify-end gap-1">
                  <span class="text-xs font-semibold uppercase tracking-wide text-gray-500">Nhập</span>
                  <button @click="toggleFilter('imports')"
                    :class="['p-1 rounded hover:bg-gray-200 transition-colors', showFilters.imports ? 'text-indigo-600 bg-indigo-50' : 'text-gray-400']">
                    <ChevronDown :size="14" />
                  </button>
                </div>
                <div v-if="showFilters.imports" class="absolute right-0 top-full z-20 mt-1 w-32 rounded-lg border border-gray-200 bg-white p-2 shadow-xl">
                  <select v-model="has_imports" @change="applyFilters()"
                    class="w-full rounded border border-gray-300 px-1 py-1.5 text-xs focus:outline-none focus:ring-2 focus:ring-indigo-500">
                    <option value="">Tất cả</option>
                    <option value="yes">Có nhập</option>
                    <option value="no">Chưa nhập</option>
                  </select>
                </div>
              </th>

              <!-- Tổng giá trị đơn hàng -->
              <th class="px-4 py-3 text-right whitespace-nowrap">
                <span class="text-xs font-semibold uppercase tracking-wide text-gray-500">Tổng ĐH</span>
              </th>

              <!-- Công nợ -->
              <th class="px-4 py-3 text-right relative whitespace-nowrap">
                <div class="flex items-center justify-end gap-1">
                  <span class="text-xs font-semibold uppercase tracking-wide text-gray-500">Công nợ</span>
                  <button @click="toggleFilter('debt')"
                    :class="['p-1 rounded hover:bg-gray-200 transition-colors', showFilters.debt ? 'text-indigo-600 bg-indigo-50' : 'text-gray-400']">
                    <ChevronDown :size="14" />
                  </button>
                </div>
                <div v-if="showFilters.debt" class="absolute right-0 top-full z-20 mt-1 w-32 rounded-lg border border-gray-200 bg-white p-2 shadow-xl">
                  <select v-model="has_debt" @change="applyFilters()"
                    class="w-full rounded border border-gray-300 px-1 py-1.5 text-xs focus:outline-none focus:ring-2 focus:ring-indigo-500">
                    <option value="">Tất cả</option>
                    <option value="yes">Còn nợ</option>
                    <option value="no">Hết nợ</option>
                  </select>
                </div>
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr v-for="c in customers.data" :key="c.id"
              @click="router.visit(`/admin/customers/${c.id}`)"
              class="cursor-pointer hover:bg-indigo-50/40 transition-colors">

              <!-- Tên -->
              <td class="px-4 py-3">
                <div class="flex items-center gap-3">
                  <div class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-indigo-100 text-xs font-bold text-indigo-600">
                    {{ initials(c.name) }}
                  </div>
                  <p class="font-medium text-gray-900 truncate max-w-[150px]">{{ c.name }}</p>
                </div>
              </td>

              <!-- MST -->
              <td class="px-4 py-3 text-gray-500 text-xs">{{ c.tax_code || '—' }}</td>

              <!-- SĐT -->
              <td class="px-4 py-3 text-gray-600 text-xs">{{ c.phone || '—' }}</td>

              <!-- Địa chỉ -->
              <td class="px-4 py-3 text-gray-500 text-xs truncate max-w-[200px]">{{ c.address || '—' }}</td>

              <!-- Đơn hàng -->
              <td class="px-4 py-3 text-right font-medium text-gray-700">
                {{ c.orders_count ?? 0 }}
              </td>

              <!-- Nhập -->
              <td class="px-4 py-3 text-right text-gray-500 text-xs">
                {{ c.purchase_invoices_count ?? '—' }}
              </td>

              <!-- Tổng giá trị đơn hàng -->
              <td class="px-4 py-3 text-right text-xs">
                <span v-if="c.total_order_value > 0" class="font-medium text-gray-700">
                  {{ formatVND(c.total_order_value) }}
                </span>
                <span v-else class="text-gray-400">—</span>
              </td>

              <!-- Công nợ -->
              <td class="px-4 py-3 text-right">
                <span v-if="c.remaining_debt > 0" class="font-semibold text-red-600 text-xs">
                  {{ formatVND(c.remaining_debt) }}
                </span>
                <span v-else class="text-gray-400 text-xs">—</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div v-if="customers?.last_page > 1" class="flex items-center justify-between text-sm text-gray-600">
        <span>
          Trang {{ customers.current_page }} / {{ customers.last_page }}
          · {{ customers.total }} khách hàng
        </span>
        <div class="flex gap-1">
          <button v-for="link in customers.links" :key="link.label"
            v-html="link.label"
            :disabled="!link.url"
            @click="link.url && router.visit(link.url)"
            :class="['px-3 py-1.5 rounded-lg text-xs transition-colors',
              link.active ? 'bg-indigo-600 text-white' : 'border border-gray-300 text-gray-600 hover:bg-gray-50 disabled:opacity-40']" />
        </div>
      </div>
    </div>
  </AdminLayout>
</template>
