<script setup>
import AdminLayout from '@/Layouts/AdminLayout.vue'
import { router } from '@inertiajs/vue3'
import { computed } from 'vue'

const props = defineProps({
    advance: Object,
    types: Object,
})

function formatVND(v) { return Number(v).toLocaleString('vi-VN', { style: 'currency', currency: 'VND' }) }
function formatDate(d) { return d ? new Date(d).toLocaleDateString('vi-VN') : '—' }

const statusLabels = { pending: 'Chờ duyệt', approved: 'Đã duyệt', settled: 'Đã quyết toán', cancelled: 'Đã hủy' }
const statusColors = {
    pending: 'bg-amber-100 text-amber-700',
    approved: 'bg-blue-100 text-blue-700',
    settled: 'bg-emerald-100 text-emerald-700',
    cancelled: 'bg-red-100 text-red-700',
}

function typeLabel(type) {
    if (props.types && props.types[type]) return props.types[type]
    const defaults = { employee: 'Nhân viên', customer: 'Khách hàng', supplier: 'Nhà cung cấp' }
    return defaults[type] ?? type
}

const remaining = computed(() => props.advance.amount - (props.advance.returned_amount ?? 0))

const relatedPerson = computed(() => {
    if (props.advance.employee) return { label: 'Nhân viên', name: props.advance.employee.name }
    if (props.advance.customer) return { label: 'Khách hàng', name: props.advance.customer.name }
    if (props.advance.supplier) return { label: 'Nhà cung cấp', name: props.advance.supplier.name }
    return null
})

function confirmDelete() {
    if (confirm('Bạn có chắc muốn xóa tạm ứng này?')) {
        router.delete('/admin/advances/' + props.advance.id)
    }
}
</script>

<template>
    <AdminLayout>
        <div class="space-y-6">
            <!-- Header -->
            <div class="flex items-center justify-between">
                <div class="flex items-center gap-3">
                    <button @click="router.visit('/admin/advances')" class="text-gray-500 hover:text-gray-700 text-sm">← Quay lại</button>
                    <h1 class="text-xl font-bold text-gray-900">{{ advance.advance_number }}</h1>
                    <span class="inline-flex rounded-full px-2 py-0.5 text-xs font-medium bg-indigo-100 text-indigo-700">
                        {{ typeLabel(advance.type) }}
                    </span>
                    <span :class="['inline-flex rounded-full px-2 py-0.5 text-xs font-medium', statusColors[advance.status]]">
                        {{ statusLabels[advance.status] ?? advance.status }}
                    </span>
                </div>
                <div class="flex gap-2">
                    <button @click="router.visit('/admin/advances/' + advance.id + '/edit')"
                        class="rounded-lg border border-indigo-300 px-4 py-2 text-sm font-medium text-indigo-600 hover:bg-indigo-50 transition-colors">
                        Chỉnh sửa
                    </button>
                    <button @click="confirmDelete"
                        class="rounded-lg border border-red-300 px-4 py-2 text-sm font-medium text-red-600 hover:bg-red-50 transition-colors">
                        Xóa
                    </button>
                </div>
            </div>

            <!-- Amounts summary -->
            <div class="grid grid-cols-3 gap-4">
                <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-3 lg:p-5 text-center">
                    <p class="text-xs text-gray-500 mb-1">Số tiền tạm ứng</p>
                    <p class="text-xl font-bold text-gray-900">{{ formatVND(advance.amount) }}</p>
                </div>
                <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-3 lg:p-5 text-center">
                    <p class="text-xs text-gray-500 mb-1">Đã hoàn trả</p>
                    <p class="text-xl font-bold text-emerald-600">{{ formatVND(advance.returned_amount ?? 0) }}</p>
                </div>
                <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-3 lg:p-5 text-center">
                    <p class="text-xs text-gray-500 mb-1">Còn lại</p>
                    <p class="text-xl font-bold" :class="remaining > 0 ? 'text-amber-600' : 'text-gray-400'">
                        {{ formatVND(remaining) }}
                    </p>
                </div>
            </div>

            <!-- Advance info -->
            <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                <h2 class="font-semibold text-gray-900 mb-4">Thông tin tạm ứng</h2>
                <div class="grid grid-cols-2 gap-4 text-sm">
                    <div>
                        <span class="text-gray-500">Ngày tạm ứng:</span>
                        <span class="ml-2 font-medium text-gray-900">{{ formatDate(advance.advance_date) }}</span>
                    </div>
                    <div>
                        <span class="text-gray-500">Ngày hoàn trả dự kiến:</span>
                        <span class="ml-2 font-medium text-gray-900">{{ formatDate(advance.expected_return_date) }}</span>
                    </div>
                    <div v-if="relatedPerson">
                        <span class="text-gray-500">{{ relatedPerson.label }}:</span>
                        <span class="ml-2 font-medium text-gray-900">{{ relatedPerson.name }}</span>
                    </div>
                    <div v-if="advance.creator">
                        <span class="text-gray-500">Người tạo:</span>
                        <span class="ml-2 font-medium text-gray-900">{{ advance.creator.name }}</span>
                    </div>
                    <div v-if="advance.purpose" class="col-span-2">
                        <span class="text-gray-500">Mục đích:</span>
                        <span class="ml-2 text-gray-700">{{ advance.purpose }}</span>
                    </div>
                    <div v-if="advance.notes" class="col-span-2">
                        <span class="text-gray-500">Ghi chú:</span>
                        <p class="mt-1 text-gray-700">{{ advance.notes }}</p>
                    </div>
                </div>
            </div>
        </div>
    </AdminLayout>
</template>
