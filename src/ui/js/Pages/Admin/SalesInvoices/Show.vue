<script setup>
import AdminLayout from '@/Layouts/AdminLayout.vue'
import { router } from '@inertiajs/vue3'
import { Download, FileSpreadsheet } from 'lucide-vue-next'
import { exportToExcel, exportToPDF } from '@/utils/exportInvoice.js'

const props = defineProps({ invoice: Object })

function formatVND(v) { return Number(v).toLocaleString('vi-VN', { style: 'currency', currency: 'VND' }) }
function formatDate(d) { return d ? new Date(d).toLocaleDateString('vi-VN') : '—' }

const statusLabels = { draft: 'Nháp', issued: 'Đã xuất', cancelled: 'Đã hủy' }
const statusColors = {
    draft: 'bg-gray-100 text-gray-700',
    issued: 'bg-blue-100 text-blue-700',
    cancelled: 'bg-red-100 text-red-700',
}
const payLabels = { unpaid: 'Chưa TT', partial: 'Một phần', paid: 'Đã TT' }
const payColors = {
    unpaid: 'bg-amber-100 text-amber-700',
    partial: 'bg-blue-100 text-blue-700',
    paid: 'bg-emerald-100 text-emerald-700',
}

function itemTotal(item) {
    const base = item.quantity * item.unit_price
    const afterDisc = base * (1 - (item.discount_rate ?? 0) / 100)
    return afterDisc * (1 + (item.tax_rate ?? 0) / 100)
}

function confirmDelete() {
    if (confirm('Bạn có chắc muốn xóa hóa đơn này?')) {
        router.delete('/admin/sales-invoices/' + props.invoice.id)
    }
}
</script>

<template>
    <AdminLayout>
        <div class="space-y-6">
            <!-- Header -->
            <div class="flex items-center justify-between">
                <div class="flex items-center gap-3">
                    <button @click="router.visit('/admin/sales-invoices')" class="text-gray-500 hover:text-gray-700 text-sm">← Quay lại</button>
                    <h1 class="text-xl font-bold text-gray-900">{{ invoice.invoice_number }}</h1>
                    <span :class="['inline-flex rounded-full px-2 py-0.5 text-xs font-medium', statusColors[invoice.status]]">
                        {{ statusLabels[invoice.status] ?? invoice.status }}
                    </span>
                    <span :class="['inline-flex rounded-full px-2 py-0.5 text-xs font-medium', payColors[invoice.payment_status]]">
                        {{ payLabels[invoice.payment_status] ?? invoice.payment_status }}
                    </span>
                </div>
                <div class="flex gap-2">
                    <button @click="exportToExcel(invoice, 'sales')"
                        class="flex items-center gap-1.5 rounded-lg border border-emerald-300 px-3 py-1.5 text-sm text-emerald-700 hover:bg-emerald-50 transition-colors">
                        <FileSpreadsheet :size="14" /> Excel
                    </button>
                    <button @click="exportToPDF(invoice, 'sales')"
                        class="flex items-center gap-1.5 rounded-lg border border-red-300 px-3 py-1.5 text-sm text-red-600 hover:bg-red-50 transition-colors">
                        <Download :size="14" /> PDF
                    </button>
                    <button @click="router.visit('/admin/sales-invoices/' + invoice.id + '/edit')"
                        class="rounded-lg border border-indigo-300 px-4 py-2 text-sm font-medium text-indigo-600 hover:bg-indigo-50 transition-colors">
                        Chỉnh sửa
                    </button>
                    <button @click="confirmDelete"
                        class="rounded-lg border border-red-300 px-4 py-2 text-sm font-medium text-red-600 hover:bg-red-50 transition-colors">
                        Xóa
                    </button>
                </div>
            </div>

            <div class="grid grid-cols-2 gap-6">
                <!-- Invoice info -->
                <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                    <h2 class="font-semibold text-gray-900 mb-4">Thông tin hóa đơn</h2>
                    <div class="space-y-2 text-sm">
                        <div class="flex justify-between">
                            <span class="text-gray-500">Ngày hóa đơn:</span>
                            <span class="font-medium">{{ formatDate(invoice.invoice_date) }}</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-gray-500">Hạn thanh toán:</span>
                            <span class="font-medium">{{ formatDate(invoice.due_date) }}</span>
                        </div>
                        <div v-if="invoice.order" class="flex justify-between">
                            <span class="text-gray-500">Đơn hàng:</span>
                            <span class="font-medium text-indigo-600">{{ invoice.order.order_number ?? '#' + invoice.order.id }}</span>
                        </div>
                        <div v-if="invoice.creator" class="flex justify-between">
                            <span class="text-gray-500">Người tạo:</span>
                            <span class="font-medium">{{ invoice.creator.name }}</span>
                        </div>
                        <div v-if="invoice.notes" class="pt-2 border-t border-gray-100">
                            <span class="text-gray-500">Ghi chú:</span>
                            <p class="mt-1 text-gray-700">{{ invoice.notes }}</p>
                        </div>
                    </div>
                </div>

                <!-- Customer info -->
                <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                    <h2 class="font-semibold text-gray-900 mb-4">Thông tin khách hàng</h2>
                    <div v-if="invoice.customer" class="space-y-2 text-sm">
                        <div class="flex justify-between">
                            <span class="text-gray-500">Tên:</span>
                            <span class="font-medium">{{ invoice.customer.name }}</span>
                        </div>
                        <div v-if="invoice.customer.email" class="flex justify-between">
                            <span class="text-gray-500">Email:</span>
                            <span class="font-medium">{{ invoice.customer.email }}</span>
                        </div>
                        <div v-if="invoice.customer.phone" class="flex justify-between">
                            <span class="text-gray-500">Điện thoại:</span>
                            <span class="font-medium">{{ invoice.customer.phone }}</span>
                        </div>
                    </div>
                    <p v-else class="text-sm text-gray-400">Không có thông tin khách hàng</p>
                </div>
            </div>

            <!-- Items table -->
            <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                <h2 class="font-semibold text-gray-900 mb-4">Danh sách hàng hóa</h2>
                <table class="w-full text-sm">
                    <thead class="bg-gray-50 border-b border-gray-200">
                        <tr>
                            <th class="text-left px-4 py-2 font-medium text-gray-600">Tên hàng</th>
                            <th class="text-left px-4 py-2 font-medium text-gray-600">ĐVT</th>
                            <th class="text-right px-4 py-2 font-medium text-gray-600">SL</th>
                            <th class="text-right px-4 py-2 font-medium text-gray-600">Đơn giá</th>
                            <th class="text-right px-4 py-2 font-medium text-gray-600">Thuế%</th>
                            <th class="text-right px-4 py-2 font-medium text-gray-600">CK%</th>
                            <th class="text-right px-4 py-2 font-medium text-gray-600">Thành tiền</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-100">
                        <tr v-for="item in invoice.items" :key="item.id">
                            <td class="px-4 py-2 text-gray-900">{{ item.product_name }}</td>
                            <td class="px-4 py-2 text-gray-500">{{ item.unit ?? '—' }}</td>
                            <td class="px-4 py-2 text-right text-gray-700">{{ item.quantity }}</td>
                            <td class="px-4 py-2 text-right text-gray-700">{{ formatVND(item.unit_price) }}</td>
                            <td class="px-4 py-2 text-right text-gray-500">{{ item.tax_rate ?? 0 }}%</td>
                            <td class="px-4 py-2 text-right text-gray-500">{{ item.discount_rate ?? 0 }}%</td>
                            <td class="px-4 py-2 text-right font-medium text-gray-900">{{ formatVND(itemTotal(item)) }}</td>
                        </tr>
                        <tr v-if="!invoice.items?.length">
                            <td colspan="7" class="px-4 py-6 text-center text-gray-400">Không có hàng hóa</td>
                        </tr>
                    </tbody>
                </table>

                <!-- Totals -->
                <div class="mt-4 flex justify-end">
                    <div class="w-64 space-y-2 text-sm border-t border-gray-200 pt-3">
                        <div class="flex justify-between font-bold text-gray-900 text-base">
                            <span>Tổng cộng:</span>
                            <span class="text-indigo-600">{{ formatVND(invoice.total_amount) }}</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </AdminLayout>
</template>
