<script setup>
import AdminLayout from '@/Layouts/AdminLayout.vue'
import { router } from '@inertiajs/vue3'
import { ref } from 'vue'
import { Search, Plus } from 'lucide-vue-next'

const props = defineProps({
    documents: Object,
    filters: Object,
    types: Object,
})

const search = ref(props.filters?.search ?? '')
const typeFilter = ref(props.filters?.type ?? '')
const statusFilter = ref(props.filters?.status ?? '')

function applyFilters() {
    router.get('/admin/documents', {
        search: search.value || undefined,
        type: typeFilter.value || undefined,
        status: statusFilter.value || undefined,
    }, { preserveState: true, replace: true })
}

const statusLabels = { draft: 'Nháp', confirmed: 'Đã xác nhận', cancelled: 'Đã hủy' }
const statusColors = {
    draft: 'bg-gray-100 text-gray-700',
    confirmed: 'bg-emerald-100 text-emerald-700',
    cancelled: 'bg-red-100 text-red-700',
}

function formatDate(d) { return d ? new Date(d).toLocaleDateString('vi-VN') : '—' }

function typeLabel(type) {
    if (props.types && props.types[type]) return props.types[type]
    const defaults = { delivery: 'Giao hàng', inventory: 'Kiểm kho', return: 'Trả hàng', other: 'Khác' }
    return defaults[type] ?? type
}
</script>

<template>
    <AdminLayout>
        <div class="space-y-5">
            <div class="flex items-center justify-between flex-wrap gap-3">
                <div>
                    <h1 class="text-xl font-bold text-gray-900">Biên bản</h1>
                    <p class="text-sm text-gray-500 mt-0.5">Quản lý biên bản giao nhận, kiểm kho, trả hàng</p>
                </div>
                <button @click="router.visit('/admin/documents/create')"
                    class="flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 transition-colors shrink-0 whitespace-nowrap">
                    <Plus :size="16" /> Tạo biên bản
                </button>
            </div>

            <!-- Filters -->
            <div class="flex flex-wrap gap-3">
                <div class="relative flex-1 min-w-48">
                    <Search :size="15" class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                    <input v-model="search" @input="applyFilters" type="text" placeholder="Tìm số biên bản, tiêu đề..."
                        class="w-full rounded-lg border border-gray-300 pl-9 pr-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                </div>
                <select v-model="typeFilter" @change="applyFilters"
                    class="rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                    <option value="">Tất cả loại</option>
                    <option value="delivery">Giao hàng</option>
                    <option value="inventory">Kiểm kho</option>
                    <option value="return">Trả hàng</option>
                    <option value="other">Khác</option>
                </select>
                <select v-model="statusFilter" @change="applyFilters"
                    class="rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                    <option value="">Tất cả trạng thái</option>
                    <option value="draft">Nháp</option>
                    <option value="confirmed">Đã xác nhận</option>
                    <option value="cancelled">Đã hủy</option>
                </select>
            </div>

            <!-- Table -->
            <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                <table class="w-full text-sm">
                    <thead class="bg-gray-50 border-b border-gray-200">
                        <tr>
                            <th class="text-left px-4 py-3 font-medium text-gray-600">Số biên bản</th>
                            <th class="text-left px-4 py-3 font-medium text-gray-600">Loại</th>
                            <th class="text-left px-4 py-3 font-medium text-gray-600">Tiêu đề</th>
                            <th class="text-left px-4 py-3 font-medium text-gray-600">Ngày</th>
                            <th class="text-center px-4 py-3 font-medium text-gray-600">Trạng thái</th>
                            <th class="text-left px-4 py-3 font-medium text-gray-600">Người tạo</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-100">
                        <tr v-for="doc in documents.data" :key="doc.id"
                            class="hover:bg-gray-50 cursor-pointer transition-colors"
                            @click="router.visit('/admin/documents/' + doc.id)">
                            <td class="px-4 py-3 font-mono text-indigo-600 font-medium">{{ doc.document_number }}</td>
                            <td class="px-4 py-3 text-gray-600">{{ typeLabel(doc.type) }}</td>
                            <td class="px-4 py-3 text-gray-900">{{ doc.title }}</td>
                            <td class="px-4 py-3 text-gray-500">{{ formatDate(doc.document_date) }}</td>
                            <td class="px-4 py-3 text-center">
                                <span :class="['inline-flex rounded-full px-2 py-0.5 text-xs font-medium', statusColors[doc.status]]">
                                    {{ statusLabels[doc.status] ?? doc.status }}
                                </span>
                            </td>
                            <td class="px-4 py-3 text-gray-600">{{ doc.creator?.name ?? '—' }}</td>
                        </tr>
                        <tr v-if="!documents.data?.length">
                            <td colspan="6" class="px-4 py-8 text-center text-gray-400">Chưa có biên bản nào</td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <!-- Pagination -->
            <div v-if="documents.last_page > 1" class="flex justify-center gap-1">
                <button v-for="link in documents.links" :key="link.label"
                    v-html="link.label"
                    :disabled="!link.url"
                    @click="link.url && router.visit(link.url)"
                    :class="['px-3 py-1.5 rounded-lg text-sm transition-colors', link.active ? 'bg-indigo-600 text-white' : 'text-gray-600 hover:bg-gray-100 disabled:opacity-40']" />
            </div>
        </div>
    </AdminLayout>
</template>
