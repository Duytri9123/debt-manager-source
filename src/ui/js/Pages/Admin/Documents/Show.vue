<script setup>
import AdminLayout from '@/Layouts/AdminLayout.vue'
import { router } from '@inertiajs/vue3'

const props = defineProps({
    document: Object,
    types: Object,
})

function formatDate(d) { return d ? new Date(d).toLocaleDateString('vi-VN') : '—' }

const statusLabels = { draft: 'Nháp', confirmed: 'Đã xác nhận', cancelled: 'Đã hủy' }
const statusColors = {
    draft: 'bg-gray-100 text-gray-700',
    confirmed: 'bg-emerald-100 text-emerald-700',
    cancelled: 'bg-red-100 text-red-700',
}

function typeLabel(type) {
    if (props.types && props.types[type]) return props.types[type]
    const defaults = { delivery: 'Giao hàng', inventory: 'Kiểm kho', return: 'Trả hàng', other: 'Khác' }
    return defaults[type] ?? type
}

function confirmDelete() {
    if (confirm('Bạn có chắc muốn xóa biên bản này?')) {
        router.delete('/admin/documents/' + props.document.id)
    }
}
</script>

<template>
    <AdminLayout>
        <div class="space-y-6">
            <!-- Header -->
            <div class="flex items-center justify-between">
                <div class="flex items-center gap-3">
                    <button @click="router.visit('/admin/documents')" class="text-gray-500 hover:text-gray-700 text-sm">← Quay lại</button>
                    <h1 class="text-xl font-bold text-gray-900">{{ document.document_number }}</h1>
                    <span class="inline-flex rounded-full px-2 py-0.5 text-xs font-medium bg-indigo-100 text-indigo-700">
                        {{ typeLabel(document.type) }}
                    </span>
                    <span :class="['inline-flex rounded-full px-2 py-0.5 text-xs font-medium', statusColors[document.status]]">
                        {{ statusLabels[document.status] ?? document.status }}
                    </span>
                </div>
                <div class="flex gap-2">
                    <button @click="router.visit('/admin/documents/' + document.id + '/edit')"
                        class="rounded-lg border border-indigo-300 px-4 py-2 text-sm font-medium text-indigo-600 hover:bg-indigo-50 transition-colors">
                        Chỉnh sửa
                    </button>
                    <button @click="confirmDelete"
                        class="rounded-lg border border-red-300 px-4 py-2 text-sm font-medium text-red-600 hover:bg-red-50 transition-colors">
                        Xóa
                    </button>
                </div>
            </div>

            <!-- Document info -->
            <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                <h2 class="font-semibold text-gray-900 mb-4">Thông tin biên bản</h2>
                <div class="grid grid-cols-2 gap-4 text-sm">
                    <div>
                        <span class="text-gray-500">Tiêu đề:</span>
                        <span class="ml-2 font-medium text-gray-900">{{ document.title }}</span>
                    </div>
                    <div>
                        <span class="text-gray-500">Ngày:</span>
                        <span class="ml-2 font-medium text-gray-900">{{ formatDate(document.document_date) }}</span>
                    </div>
                    <div v-if="document.supplier">
                        <span class="text-gray-500">Nhà cung cấp:</span>
                        <span class="ml-2 font-medium text-gray-900">{{ document.supplier.name }}</span>
                    </div>
                    <div v-if="document.customer">
                        <span class="text-gray-500">Khách hàng:</span>
                        <span class="ml-2 font-medium text-gray-900">{{ document.customer.name }}</span>
                    </div>
                    <div v-if="document.creator">
                        <span class="text-gray-500">Người tạo:</span>
                        <span class="ml-2 font-medium text-gray-900">{{ document.creator.name }}</span>
                    </div>
                    <div v-if="document.content" class="col-span-2">
                        <span class="text-gray-500">Nội dung:</span>
                        <p class="mt-1 text-gray-700 whitespace-pre-wrap">{{ document.content }}</p>
                    </div>
                    <div v-if="document.notes" class="col-span-2">
                        <span class="text-gray-500">Ghi chú:</span>
                        <p class="mt-1 text-gray-700">{{ document.notes }}</p>
                    </div>
                </div>
            </div>

            <!-- Items table -->
            <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                <h2 class="font-semibold text-gray-900 mb-4">Danh sách hàng hóa</h2>
                <div v-if="!document.items?.length" class="text-sm text-gray-400 text-center py-6">
                    Không có hàng hóa
                </div>
                <table v-else class="w-full text-sm">
                    <thead class="bg-gray-50 border-b border-gray-200">
                        <tr>
                            <th class="text-left px-4 py-2 font-medium text-gray-600">Tên hàng</th>
                            <th class="text-left px-4 py-2 font-medium text-gray-600">ĐVT</th>
                            <th class="text-right px-4 py-2 font-medium text-gray-600">SL dự kiến</th>
                            <th class="text-right px-4 py-2 font-medium text-gray-600">SL thực tế</th>
                            <th class="text-left px-4 py-2 font-medium text-gray-600">Ghi chú</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-100">
                        <tr v-for="item in document.items" :key="item.id">
                            <td class="px-4 py-2 text-gray-900">{{ item.product_name }}</td>
                            <td class="px-4 py-2 text-gray-500">{{ item.unit ?? '—' }}</td>
                            <td class="px-4 py-2 text-right text-gray-700">{{ item.expected_quantity }}</td>
                            <td class="px-4 py-2 text-right font-medium"
                                :class="item.actual_quantity < item.expected_quantity ? 'text-red-600' : 'text-emerald-600'">
                                {{ item.actual_quantity }}
                            </td>
                            <td class="px-4 py-2 text-gray-500">{{ item.notes ?? '—' }}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </AdminLayout>
</template>
