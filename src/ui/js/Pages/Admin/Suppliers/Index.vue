<script setup>
import AdminLayout from '@/Layouts/AdminLayout.vue'
import { router } from '@inertiajs/vue3'
import { ref } from 'vue'
import { Search, Plus } from 'lucide-vue-next'

const props = defineProps({
    suppliers: Object,
    filters: Object,
})

const search = ref(props.filters?.search ?? '')
const status = ref(props.filters?.status ?? '')

function applyFilters() {
    router.get('/admin/suppliers', {
        search: search.value || undefined,
        status: status.value || undefined,
    }, { preserveState: true, replace: true })
}
</script>

<template>
    <AdminLayout>
        <div class="space-y-5">
            <div class="flex items-center justify-between flex-wrap gap-3">
                <div>
                    <h1 class="text-xl font-bold text-gray-900">Nhà cung cấp</h1>
                    <p class="text-sm text-gray-500 mt-0.5">Quản lý danh sách nhà cung cấp</p>
                </div>
                <button @click="router.visit('/admin/suppliers/create')"
                    class="flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 transition-colors shrink-0 whitespace-nowrap">
                    <Plus :size="16" /> Thêm NCC
                </button>
            </div>

            <!-- Filters -->
            <div class="flex flex-wrap gap-3">
                <div class="relative flex-1 min-w-48">
                    <Search :size="15" class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                    <input v-model="search" @input="applyFilters" type="text" placeholder="Tìm tên, mã, email..."
                        class="w-full rounded-lg border border-gray-300 pl-9 pr-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                </div>
                <select v-model="status" @change="applyFilters"
                    class="rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                    <option value="">Tất cả trạng thái</option>
                    <option value="active">Đang hoạt động</option>
                    <option value="inactive">Ngừng hoạt động</option>
                </select>
            </div>

            <!-- Table -->
            <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                <div class="overflow-x-auto">
                <table class="w-full text-sm">
                    <thead class="bg-gray-50 border-b border-gray-200">
                        <tr>
                            <th class="text-left px-4 py-3 font-medium text-gray-600 whitespace-nowrap">Mã NCC</th>
                            <th class="text-left px-4 py-3 font-medium text-gray-600 whitespace-nowrap">Tên nhà cung cấp</th>
                            <th class="text-left px-4 py-3 font-medium text-gray-600 whitespace-nowrap">Điện thoại</th>
                            <th class="text-left px-4 py-3 font-medium text-gray-600 whitespace-nowrap">Email</th>
                            <th class="text-left px-4 py-3 font-medium text-gray-600 whitespace-nowrap">Người liên hệ</th>
                            <th class="text-center px-4 py-3 font-medium text-gray-600 whitespace-nowrap">Trạng thái</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-100">
                        <tr v-for="supplier in suppliers.data" :key="supplier.id"
                            class="hover:bg-gray-50 cursor-pointer transition-colors"
                            @click="router.visit('/admin/suppliers/' + supplier.id)">
                            <td class="px-4 py-3 font-mono text-indigo-600 font-medium whitespace-nowrap">{{ supplier.code ?? '—' }}</td>
                            <td class="px-4 py-3 font-medium text-gray-900 whitespace-nowrap">{{ supplier.name }}</td>
                            <td class="px-4 py-3 text-gray-600 whitespace-nowrap">{{ supplier.phone ?? '—' }}</td>
                            <td class="px-4 py-3 text-gray-600 whitespace-nowrap">{{ supplier.email ?? '—' }}</td>
                            <td class="px-4 py-3 text-gray-600 whitespace-nowrap">{{ supplier.contact_person ?? '—' }}</td>
                            <td class="px-4 py-3 text-center whitespace-nowrap">
                                <span :class="['inline-flex rounded-full px-2 py-0.5 text-xs font-medium',
                                    supplier.is_active ? 'bg-emerald-100 text-emerald-700' : 'bg-gray-100 text-gray-600']">
                                    {{ supplier.is_active ? 'Hoạt động' : 'Ngừng HĐ' }}
                                </span>
                            </td>
                        </tr>
                        <tr v-if="!suppliers.data?.length">
                            <td colspan="6" class="px-4 py-8 text-center text-gray-400">Chưa có nhà cung cấp nào</td>
                        </tr>
                    </tbody>
                </table>
                </div>
            </div>

            <!-- Pagination -->
            <div v-if="suppliers.last_page > 1" class="flex justify-center gap-1">
                <button v-for="link in suppliers.links" :key="link.label"
                    v-html="link.label"
                    :disabled="!link.url"
                    @click="link.url && router.visit(link.url)"
                    :class="['px-3 py-1.5 rounded-lg text-sm transition-colors', link.active ? 'bg-indigo-600 text-white' : 'text-gray-600 hover:bg-gray-100 disabled:opacity-40']" />
            </div>
        </div>
    </AdminLayout>
</template>
