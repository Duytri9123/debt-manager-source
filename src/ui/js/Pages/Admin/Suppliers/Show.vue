<script setup>
import AdminLayout from '@/Layouts/AdminLayout.vue'
import { router } from '@inertiajs/vue3'

const props = defineProps({
    supplier: Object,
    recentInvoices: Array,
})

function formatVND(v) { return Number(v).toLocaleString('vi-VN', { style: 'currency', currency: 'VND' }) }
function formatDate(d) { return d ? new Date(d).toLocaleDateString('vi-VN') : '—' }

const invoiceStatusLabels = { draft: 'Nháp', confirmed: 'Đã xác nhận', received: 'Đã nhận', cancelled: 'Đã hủy' }
const invoiceStatusColors = {
    draft: 'bg-gray-100 text-gray-700',
    confirmed: 'bg-blue-100 text-blue-700',
    received: 'bg-emerald-100 text-emerald-700',
    cancelled: 'bg-red-100 text-red-700',
}

function confirmDelete() {
    if (confirm('Bạn có chắc muốn xóa nhà cung cấp này?')) {
        router.delete('/admin/suppliers/' + props.supplier.id)
    }
}
</script>

<template>
    <AdminLayout>
        <div class="space-y-6">
            <!-- Header -->
            <div class="flex items-center justify-between">
                <div class="flex items-center gap-3">
                    <button @click="router.visit('/admin/suppliers')" class="text-gray-500 hover:text-gray-700 text-sm">← Quay lại</button>
                    <h1 class="text-xl font-bold text-gray-900">{{ supplier.name }}</h1>
                    <span :class="['inline-flex rounded-full px-2 py-0.5 text-xs font-medium',
                        supplier.is_active ? 'bg-emerald-100 text-emerald-700' : 'bg-gray-100 text-gray-600']">
                        {{ supplier.is_active ? 'Hoạt động' : 'Ngừng HĐ' }}
                    </span>
                </div>
                <div class="flex gap-2">
                    <button @click="router.visit('/admin/suppliers/' + supplier.id + '/edit')"
                        class="rounded-lg border border-indigo-300 px-4 py-2 text-sm font-medium text-indigo-600 hover:bg-indigo-50 transition-colors">
                        Chỉnh sửa
                    </button>
                    <button @click="confirmDelete"
                        class="rounded-lg border border-red-300 px-4 py-2 text-sm font-medium text-red-600 hover:bg-red-50 transition-colors">
                        Xóa
                    </button>
                </div>
            </div>

            <!-- Supplier info card -->
            <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                <h2 class="font-semibold text-gray-900 mb-4">Thông tin nhà cung cấp</h2>
                <div class="grid grid-cols-2 gap-4 text-sm">
                    <div>
                        <span class="text-gray-500">Mã NCC:</span>
                        <span class="ml-2 font-medium text-gray-900">{{ supplier.code ?? '—' }}</span>
                    </div>
                    <div>
                        <span class="text-gray-500">Mã số thuế:</span>
                        <span class="ml-2 font-medium text-gray-900">{{ supplier.tax_code ?? '—' }}</span>
                    </div>
                    <div>
                        <span class="text-gray-500">Điện thoại:</span>
                        <span class="ml-2 font-medium text-gray-900">{{ supplier.phone ?? '—' }}</span>
                    </div>
                    <div>
                        <span class="text-gray-500">Email:</span>
                        <span class="ml-2 font-medium text-gray-900">{{ supplier.email ?? '—' }}</span>
                    </div>
                    <div>
                        <span class="text-gray-500">Người liên hệ:</span>
                        <span class="ml-2 font-medium text-gray-900">{{ supplier.contact_person ?? '—' }}</span>
                    </div>
                    <div>
                        <span class="text-gray-500">Địa chỉ:</span>
                        <span class="ml-2 font-medium text-gray-900">{{ supplier.address ?? '—' }}</span>
                    </div>
                    <div v-if="supplier.notes" class="col-span-2">
                        <span class="text-gray-500">Ghi chú:</span>
                        <span class="ml-2 text-gray-700">{{ supplier.notes }}</span>
                    </div>
                </div>
            </div>

            <!-- Recent invoices -->
            <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                <h2 class="font-semibold text-gray-900 mb-4">Hóa đơn gần đây</h2>
                <div v-if="!recentInvoices?.length" class="text-sm text-gray-400 text-center py-6">
                    Chưa có hóa đơn nào
                </div>
                <table v-else class="w-full text-sm">
                    <thead class="bg-gray-50 border-b border-gray-200">
                        <tr>
                            <th class="text-left px-4 py-2 font-medium text-gray-600">Số HĐ</th>
                            <th class="text-left px-4 py-2 font-medium text-gray-600">Ngày</th>
                            <th class="text-right px-4 py-2 font-medium text-gray-600">Tổng tiền</th>
                            <th class="text-center px-4 py-2 font-medium text-gray-600">Trạng thái</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-100">
                        <tr v-for="inv in recentInvoices" :key="inv.id"
                            class="hover:bg-gray-50 cursor-pointer transition-colors"
                            @click="router.visit('/admin/purchase-invoices/' + inv.id)">
                            <td class="px-4 py-2 font-mono text-indigo-600 font-medium">{{ inv.invoice_number }}</td>
                            <td class="px-4 py-2 text-gray-500">{{ formatDate(inv.invoice_date) }}</td>
                            <td class="px-4 py-2 text-right font-medium text-gray-900">{{ formatVND(inv.total_amount) }}</td>
                            <td class="px-4 py-2 text-center">
                                <span :class="['inline-flex rounded-full px-2 py-0.5 text-xs font-medium', invoiceStatusColors[inv.status]]">
                                    {{ invoiceStatusLabels[inv.status] ?? inv.status }}
                                </span>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </AdminLayout>
</template>
