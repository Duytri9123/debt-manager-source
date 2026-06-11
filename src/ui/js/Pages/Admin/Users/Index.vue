<script setup>
import { ref, computed } from 'vue'
import { router } from '@inertiajs/vue3'
import AdminLayout from '@/Layouts/AdminLayout.vue'
import { Search, Plus, Trash2 } from 'lucide-vue-next'

const props = defineProps({
  users: Object,
  filters: Object,
})

const search    = ref(props.filters?.search    ?? '')
const role      = ref(props.filters?.role      ?? '')
const status    = ref(props.filters?.status    ?? '')
const sort      = ref(props.filters?.sort      ?? 'created_at')
const direction = ref(props.filters?.direction ?? 'desc')

// ── Checkbox selection ────────────────────────────────────────────────────────
const selected = ref(new Set())

const selectableUsers = computed(() => props.users.data.filter(u => !u.isAdmin))

const allSelected = computed(() =>
  selectableUsers.value.length > 0 &&
  selectableUsers.value.every(u => selected.value.has(u.id))
)

function toggleAll() {
  if (allSelected.value) {
    selectableUsers.value.forEach(u => selected.value.delete(u.id))
  } else {
    selectableUsers.value.forEach(u => selected.value.add(u.id))
  }
}

function toggleOne(id) {
  if (selected.value.has(id)) selected.value.delete(id)
  else selected.value.add(id)
}

// ── Filters ───────────────────────────────────────────────────────────────────
let searchTimer = null
function onSearch() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => applyFilters(), 300)
}

function applyFilters() {
  selected.value.clear()
  router.get('/admin/users', {
    search:    search.value    || undefined,
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
  router.get('/admin/users', {}, { preserveState: false })
}

// ── Delete ────────────────────────────────────────────────────────────────────
function deleteUser(u) {
  if (confirm(`Xóa người dùng "${u.name}"? Hành động này không thể hoàn tác!`)) {
    router.delete(`/admin/users/${u.id}`)
  }
}

function bulkDelete() {
  const ids = [...selected.value]
  if (!ids.length) return
  if (confirm(`Xóa ${ids.length} người dùng đã chọn? Hành động này không thể hoàn tác!`)) {
    router.delete('/admin/users', {
      data: { ids },
      onSuccess: () => selected.value.clear(),
    })
  }
}

function formatDate(d) { return d ? new Date(d).toLocaleDateString('vi-VN') : '—' }
function initials(n)   { return n ? n.charAt(0).toUpperCase() : '?' }

const hasFilters = computed(() =>
  search.value || role.value || status.value ||
  sort.value !== 'created_at' || direction.value !== 'desc'
)
</script>

<template>
  <AdminLayout>
    <div class="space-y-6">
      <div class="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 class="text-2xl font-bold text-gray-900">Quản lý Người dùng</h1>
          <p class="text-sm text-gray-500">Danh sách các tài khoản quản trị và người dùng hệ thống</p>
        </div>
        <button @click="router.visit('/admin/users/create')"
          class="flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-indigo-700 transition-colors shrink-0 whitespace-nowrap">
          <Plus :size="18" />
          Thêm người dùng
        </button>
      </div>

      <!-- Filters -->
      <div class="flex flex-wrap gap-3 items-center bg-white p-4 rounded-xl border border-gray-200 shadow-sm">
        <div class="relative flex-1 min-w-64">
          <Search :size="15" class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input v-model="search" @input="onSearch" type="text" placeholder="Tìm tên, email..."
            class="w-full rounded-lg border border-gray-300 pl-9 pr-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
        </div>
        <select v-model="role" @change="applyFilters"
          class="rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
          <option value="">Tất cả vai trò</option>
          <option value="admin">Admin</option>
          <option value="user">Người dùng</option>
        </select>
        <select v-model="status" @change="applyFilters"
          class="rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
          <option value="">Tất cả trạng thái</option>
          <option value="active">Hoạt động</option>
          <option value="banned">Bị khóa</option>
        </select>
        <button v-if="hasFilters" @click="resetFilters" class="text-sm text-gray-500 hover:text-indigo-600">Xóa lọc</button>
      </div>

      <!-- Bulk action toolbar -->
      <div v-if="selected.size > 0"
        class="flex items-center gap-3 bg-red-50 border border-red-200 rounded-xl px-4 py-2.5 shadow-sm">
        <span class="text-sm font-medium text-red-700">Đã chọn {{ selected.size }} người dùng</span>
        <button @click="bulkDelete"
          class="flex items-center gap-1.5 rounded-lg bg-red-600 hover:bg-red-700 px-3 py-1.5 text-xs font-semibold text-white transition-colors">
          <Trash2 :size="13" /> Xóa đã chọn
        </button>
        <button @click="selected.clear()" class="text-xs text-red-500 hover:text-red-700">Bỏ chọn</button>
      </div>

      <div class="overflow-hidden rounded-xl border border-gray-200 bg-white shadow-sm">
        <table class="w-full text-sm">
          <thead class="bg-gray-50 border-b border-gray-200">
            <tr>
              <th class="px-4 py-3 w-10">
                <input type="checkbox" :checked="allSelected" @change="toggleAll"
                  class="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500 cursor-pointer" />
              </th>
              <th class="px-4 py-3 text-left">Họ tên</th>
              <th class="px-4 py-3 text-left">Email</th>
              <th class="px-4 py-3 text-left">Vai trò</th>
              <th class="px-4 py-3 text-left">Trạng thái</th>
              <th class="px-4 py-3 text-left">Ngày tạo</th>
              <th class="px-4 py-3 text-left w-12"></th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr v-for="u in users.data" :key="u.id"
              :class="['transition-colors cursor-pointer', selected.has(u.id) ? 'bg-indigo-50' : 'hover:bg-gray-50']"
              @click="router.visit(`/admin/users/${u.id}`)">
              <td class="px-4 py-3" @click.stop>
                <input v-if="!u.isAdmin" type="checkbox"
                  :checked="selected.has(u.id)" @change="toggleOne(u.id)"
                  class="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500 cursor-pointer" />
              </td>
              <td class="px-4 py-3">
                <div class="flex items-center gap-3">
                  <div class="flex h-8 w-8 items-center justify-center rounded-full bg-gray-200 font-bold text-gray-600">
                    {{ initials(u.name) }}
                  </div>
                  <span class="font-medium text-gray-900">{{ u.name }}</span>
                </div>
              </td>
              <td class="px-4 py-3 text-gray-600">{{ u.email }}</td>
              <td class="px-4 py-3">
                <span :class="['px-2 py-0.5 rounded-full text-xs font-medium', u.isAdmin ? 'bg-indigo-100 text-indigo-700' : 'bg-gray-100 text-gray-600']">
                  {{ u.isAdmin ? 'Admin' : 'User' }}
                </span>
              </td>
              <td class="px-4 py-3">
                <span :class="['px-2 py-0.5 rounded-full text-xs font-medium', u.is_banned ? 'bg-red-100 text-red-700' : 'bg-emerald-100 text-emerald-700']">
                  {{ u.is_banned ? 'Bị khóa' : 'Hoạt động' }}
                </span>
              </td>
              <td class="px-4 py-3 text-gray-500">{{ formatDate(u.created_at) }}</td>
              <td class="px-4 py-3">
                <button v-if="!u.isAdmin" @click.stop="deleteUser(u)"
                  class="p-1.5 rounded-md text-gray-400 hover:text-red-600 hover:bg-red-50 transition-colors"
                  title="Xóa người dùng">
                  <Trash2 :size="15" />
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </AdminLayout>
</template>
