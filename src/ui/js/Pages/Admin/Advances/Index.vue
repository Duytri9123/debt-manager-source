<script setup>
import AdminLayout from '@/Layouts/AdminLayout.vue'
import { router } from '@inertiajs/vue3'
import { ref } from 'vue'
import { Search, Plus } from 'lucide-vue-next'

const props = defineProps({
    advances: Object,
    filters: Object,
    types: Object,
})

const search = ref(props.filters?.search ?? '')
const typeFilter = ref(props.filters?.type ?? '')
const statusFilter = ref(props.filters?.status ?? '')

function applyFilters() {
    router.get('/admin/advances', {
        search: search.value || undefined,
        type: typeFilter.value || undefined,
        status: statusFilter.value || undefined,
    }, { preserveState: true, replace: true })
}

const statusLabels = { pending: 'Chờ duyệt', approved: 'Đã duyệt', settled: 'Đã quyết toán', cancelled: 'Đã hủy' }
const statusColors = {
    pending: 'bg-amber-100 text-amber-700',
    approved: 'bg-blue-100 text-blue-700',
    settled: 'bg-emerald-100 text-emerald-700',
    cancelled: 'bg-red-100 text-red-700',
}

function formatVND(v) { return Number(v).toLocaleString('vi-VN', { style: 'currency', currency: 'VND' }) }
function formatDate(d) { return d ? new Date(d).toLocaleDateString('vi-VN') : '—' }

function typeLabel(type) {
    if (props.types && props.types[type]) return props.types[type]
    const defaults = { employee: 'Nhân viên', customer: 'Khách hàng', supplier: 'Nhà cung cấp' }
    return defaults[type] ?? type
}
</script>

<template>
    <AdminLayout>
        <div class="space-y-5">
            <div class="flex items-center justify-between flex-wrap gap-3">
                <div>
                    <h1 class="text-xl font-bold text-gray-900">Tạm ứng</h1>
                    <p class="text-sm text-gray-500 mt-0.5">Quản lý các khoản tạm ứng</p>
                </div>
                <button @click="router.visit('/admin/advances/create')"
                    class="flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 transition-colors shrink-0 whitespace-nowrap">
                    <Plus :size="16" /> Tạo tạm ứng
                </button>
            </div>

            <!-- Filters -->
            <div class="flex flex-wrap gap-3">
                <div class="relative flex-1 min-w-48">
                    <Search :size="15" class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                    <input v-model="search" @input="applyFilters" type="text" placeholder="Tìm số tạm ứng, mục đích..."
                        class="w-full rounded-lg border border-gray-300 pl-9 pr-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                </div>
                <select v-model="typeFilter" @change="applyFilters"
                    class="rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                    <option value="">Tất cả loại</option>
                    <option value="employee">Nhân viên</option>
                    <option value="customer">Khách hàng</option>
                    <option value="supplier">Nhà cung cấp</option>
                </select>
                <select v-model="statusFilter" @change="applyFilters"
                    class="rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                    <option value="">Tất cả trạng thái</option>
                    <option v-for="(label, val) in statusLabels" :key="val" :value="val">{{ label }}</option>
                </select>
            </div>

            <!-- Table -->
            <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                <table class="w-full text-sm">
                    <thead class="bg-gray-50 border-b border-gray-200">
                        <tr>
                            <th class="text-left px-4 py-3 font-medium text-gray-600">Số tạm ứng</th>
                            <th class="text-left px-4 py-3 font-medium text-gray-600">Loại</th>
                            <th class="text-left px-4 py-3 font-medium text-gray-600">Mục đích</th>
                            <th class="text-left px-4 py-3 font-medium text-gray-600">Ngày</th>
                            <th class="text-right px-4 py-3 font-medium text-gray-600">Số tiền</th>
                            <th class="text-right px-4 py-3 font-medium text-gray-600">Đã hoàn</th>
                            <th class="text-right px-4 py-3 font-medium text-gray-600">Còn lại</th>
                            <th class="text-center px-4 py-3 font-medium text-gray-600">Trạng thái</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-100">
                        <tr v-for="adv in advances.data" :key="adv.id"
                            class="hover:bg-gray-50 cursor-pointer transition-colors"
                            @click="router.visit('/admin/advances/' + adv.id)">
                            <td class="px-4 py-3 font-mono text-indigo-600 font-medium">{{ adv.advance_number }}</td>
                            <td class="px-4 py-3 text-gray-600">{{ typeLabel(adv.type) }}</td>
                            <td class="px-4 py-3 text-gray-700">{{ adv.purpose ?? '—' }}</td>
                            <td class="px-4 py-3 text-gray-500">{{ formatDate(adv.advance_date) }}</td>
                            <td class="px-4 py-3 text-right font-medium text-gray-900">{{ formatVND(adv.amount) }}</td>
                            <td class="px-4 py-3 text-right text-emerald-600">{{ formatVND(adv.returned_amount ?? 0) }}</td>
                            <td class="px-4 py-3 text-right font-medium"
                                :class="(adv.amount - (adv.returned_amount ?? 0)) > 0 ? 'text-amber-600' : 'text-gray-500'">
                                {{ formatVND(adv.amount - (adv.returned_amount ?? 0)) }}
                            </td>
                            <td class="px-4 py-3 text-center">
                                <span :class="['inline-flex rounded-full px-2 py-0.5 text-xs font-medium', statusColors[adv.status]]">
                                    {{ statusLabels[adv.status] ?? adv.status }}
                                </span>
                            </td>
                        </tr>
                        <tr v-if="!advances.data?.length">
                            <td colspan="8" class="px-4 py-8 text-center text-gray-400">Chưa có tạm ứng nào</td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <!-- Pagination -->
            <div v-if="advances.last_page > 1" class="flex justify-center gap-1">
                <button v-for="link in advances.links" :key="link.label"
                    v-html="link.label"
                    :disabled="!link.url"
                    @click="link.url && router.visit(link.url)"
                    :class="['px-3 py-1.5 rounded-lg text-sm transition-colors', link.active ? 'bg-indigo-600 text-white' : 'text-gray-600 hover:bg-gray-100 disabled:opacity-40']" />
            </div>
        </div>
    </AdminLayout>
</template>
