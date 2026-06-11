<script setup>
import AdminLayout from '@/Layouts/AdminLayout.vue'
import { router } from '@inertiajs/vue3'
import { Edit2, Trash2, Download, FileSpreadsheet } from 'lucide-vue-next'
import { exportToExcel, exportToPDF } from '@/utils/exportInvoice.js'

const props = defineProps({ invoice: Object })

const statusLabels = { draft: 'Nháp', confirmed: 'Đã xác nhận', received: 'Đã nhận', cancelled: 'Đã hủy' }
const statusColors = { draft: 'bg-gray-100 text-gray-700', confirmed: 'bg-blue-100 text-blue-700', received: 'bg-emerald-100 text-emerald-700', cancelled: 'bg-red-100 text-red-700' }
const payColors = { unpaid: 'bg-amber-100 text-amber-700', partial: 'bg-blue-100 text-blue-700', paid: 'bg-emerald-100 text-emerald-700' }
const payLabels = { unpaid: 'Chưa thanh toán', partial: 'Thanh toán một phần', paid: 'Đã thanh toán' }

function formatVND(v) { return Number(v).toLocaleString('vi-VN', { style: 'currency', currency: 'VND' }) }
function formatDate(d) { return d ? new Date(d).toLocaleDateString('vi-VN') : '—' }

function destroy() {
    if (confirm('Xóa hóa đơn này?')) {
        router.delete('/admin/purchase-invoices/' + props.invoice.id)
    }
}
</script>

<template>
    <AdminLayout>
        <div class="space-y-6">
            <div class="flex items-center justify-between">
                <div class="flex items-center gap-3">
                    <button @click="router.visit('/admin/purchase-invoices')" class="text-gray-500 hover:text-gray-700">← Quay lại</button>
                    <h1 class="text-xl font-bold text-gray-900">{{ invoice.invoice_number }}</h1>
                    <span :class="['rounded-full px-2.5 py-0.5 text-xs font-medium', statusColors[invoice.status]]">{{ statusLabels[invoice.status] }}</span>
                    <span :class="['rounded-full px-2.5 py-0.5 text-xs font-medium', payColors[invoice.payment_status]]">{{ payLabels[invoice.payment_status] }}</span>
                </div>
                <div class="flex gap-2">
                    <button @click="exportToExcel(invoice, 'purchase')"
                        class="flex items-center gap-1.5 rounded-lg border border-emerald-300 px-3 py-1.5 text-sm text-emerald-700 hover:bg-emerald-50 transition-colors">
                        <FileSpreadsheet :size="14" /> Excel
                    </button>
                    <button @click="exportToPDF(invoice, 'purchase')"
                        class="flex items-center gap-1.5 rounded-lg border border-red-300 px-3 py-1.5 text-sm text-red-600 hover:bg-red-50 transition-colors">
                        <Download :size="14" /> PDF
                    </button>
                    <button @click="router.visit('/admin/purchase-invoices/' + invoice.id + '/edit')"
                        class="flex items-center gap-1.5 rounded-lg border border-gray-300 px-3 py-1.5 text-sm text-gray-700 hover:bg-gray-50 transition-colors">
                        <Edit2 :size="14" /> Sửa
                    </button>
                    <button @click="destroy"
                        class="flex items-center gap-1.5 rounded-lg border border-red-300 px-3 py-1.5 text-sm text-red-600 hover:bg-red-50 transition-colors">
                        <Trash2 :size="14" /> Xóa
                    </button>
                </div>
            </div>

            <!-- Info -->
            <div class="grid grid-cols-2 gap-6">
                <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-3 lg:p-5">
                    <h3 class="font-semibold text-gray-900 mb-3">Thông tin hóa đơn</h3>
                    <dl class="space-y-2 text-sm">
                        <div class="flex justify-between"><dt class="text-gray-500">Nhà cung cấp</dt><dd class="font-medium">{{ invoice.supplier?.name ?? '—' }}</dd></div>
                        <div class="flex justify-between"><dt class="text-gray-500">Ngày HĐ</dt><dd>{{ formatDate(invoice.invoice_date) }}</dd></div>
                        <div class="flex justify-between"><dt class="text-gray-500">Hạn TT</dt><dd>{{ formatDate(invoice.due_date) }}</dd></div>
                        <div class="flex justify-between"><dt class="text-gray-500">Người tạo</dt><dd>{{ invoice.creator?.name }}</dd></div>
                    </dl>
                </div>
                <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-3 lg:p-5">
                    <h3 class="font-semibold text-gray-900 mb-3">Tổng kết</h3>
                    <dl class="space-y-2 text-sm">
                        <div class="flex justify-between"><dt class="text-gray-500">Tạm tính</dt><dd>{{ formatVND(invoice.subtotal) }}</dd></div>
                        <div class="flex justify-between"><dt class="text-gray-500">Thuế</dt><dd>{{ formatVND(invoice.tax_amount) }}</dd></div>
                        <div class="flex justify-between"><dt class="text-gray-500">Chiết khấu</dt><dd>-{{ formatVND(invoice.discount_amount) }}</dd></div>
                        <div class="flex justify-between font-bold text-gray-900 border-t border-gray-200 pt-2"><dt>Tổng cộng</dt><dd class="text-indigo-600">{{ formatVND(invoice.total_amount) }}</dd></div>
                        <div class="flex justify-between"><dt class="text-gray-500">Đã thanh toán</dt><dd class="text-emerald-600">{{ formatVND(invoice.paid_amount) }}</dd></div>
                        <div class="flex justify-between font-medium"><dt class="text-gray-500">Còn lại</dt><dd class="text-red-600">{{ formatVND(invoice.total_amount - invoice.paid_amount) }}</dd></div>
                    </dl>
                </div>
            </div>

            <!-- Items -->
            <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                <div class="px-5 py-4 border-b border-gray-200">
                    <h3 class="font-semibold text-gray-900">Danh sách hàng hóa</h3>
                </div>
                <table class="w-full text-sm">
                    <thead class="bg-gray-50">
                        <tr>
                            <th class="text-left px-4 py-3 font-medium text-gray-600">Tên hàng</th>
                            <th class="text-center px-4 py-3 font-medium text-gray-600">ĐVT</th>
                            <th class="text-right px-4 py-3 font-medium text-gray-600">SL</th>
                            <th class="text-right px-4 py-3 font-medium text-gray-600">Đơn giá</th>
                            <th class="text-right px-4 py-3 font-medium text-gray-600">Thuế%</th>
                            <th class="text-right px-4 py-3 font-medium text-gray-600">Thành tiền</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-100">
                        <tr v-for="item in invoice.items" :key="item.id">
                            <td class="px-4 py-3">{{ item.product_name }}</td>
                            <td class="px-4 py-3 text-center text-gray-500">{{ item.unit ?? '—' }}</td>
                            <td class="px-4 py-3 text-right">{{ item.quantity }}</td>
                            <td class="px-4 py-3 text-right">{{ formatVND(item.unit_price) }}</td>
                            <td class="px-4 py-3 text-right text-gray-500">{{ item.tax_rate }}%</td>
                            <td class="px-4 py-3 text-right font-medium">{{ formatVND(item.total_price) }}</td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <div v-if="invoice.notes" class="bg-white rounded-xl shadow-sm border border-gray-200 p-3 lg:p-5">
                <h3 class="font-semibold text-gray-900 mb-2">Ghi chú</h3>
                <p class="text-sm text-gray-600">{{ invoice.notes }}</p>
            </div>
        </div>
    </AdminLayout>
</template>
