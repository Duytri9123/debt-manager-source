<script setup>
import AdminLayout from '@/Layouts/AdminLayout.vue'
import { router } from '@inertiajs/vue3'
import { ref } from 'vue'
import { Search, Plus, Eye } from 'lucide-vue-next'

const props = defineProps({
    invoices: Object,
    filters: Object,
})

const search = ref(props.filters?.search ?? '')
const status = ref(props.filters?.status ?? '')
const payStatus = ref(props.filters?.payment_status ?? '')

function applyFilters() {
    router.get('/admin/purchase-invoices', {
        search: search.value || undefined,
        status: status.value || undefined,
        payment_status: payStatus.value || undefined,
    }, { preserveState: true, replace: true })
}

const statusLabels = { draft: 'Nháp', confirmed: 'Đã xác nhận', received: 'Đã nhận', cancelled: 'Đã hủy' }
const statusColors = { draft: 'bg-gray-100 text-gray-700', confirmed: 'bg-blue-100 text-blue-700', received: 'bg-emerald-100 text-emerald-700', cancelled: 'bg-red-100 text-red-700' }
const payColors = { unpaid: 'bg-amber-100 text-amber-700', partial: 'bg-blue-100 text-blue-700', paid: 'bg-emerald-100 text-emerald-700' }
const payLabels = { unpaid: 'Chưa TT', partial: 'Một phần', paid: 'Đã TT' }

function formatVND(v) { return Number(v).toLocaleString('vi-VN', { style: 'currency', currency: 'VND' }) }
function formatDate(d) { return d ? new Date(d).toLocaleDateString('vi-VN') : '—' }
</script>

<template>
    <AdminLayout>
        <div class="space-y-5">
            <div class="flex items-center justify-between flex-wrap gap-3">
                <div>
                    <h1 class="text-xl font-bold text-gray-900">Hóa đơn nhập hàng</h1>
                    <p class="text-sm text-gray-500 mt-0.5">Quản lý hóa đơn mua hàng từ nhà cung cấp</p>
                </div>
                <button @click="router.visit('/admin/purchase-invoices/create')"
                    class="flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 transition-colors shrink-0 whitespace-nowrap">
                    <Plus :size="16" /> Tạo hóa đơn
                </button>
            </div>

            <!-- Filters -->
            <div class="flex flex-wrap gap-3">
                <div class="relative flex-1 min-w-48">
                    <Search :size="15" class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                    <input v-model="search" @input="applyFilters" type="text" placeholder="Tìm số HĐ, nhà cung cấp..."
                        class="w-full rounded-lg border border-gray-300 pl-9 pr-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                </div>
                <select v-model="status" @change="applyFilters"
                    class="rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                    <option value="">Tất cả trạng thái</option>
                    <option v-for="(label, val) in statusLabels" :key="val" :value="val">{{ label }}</option>
                </select>
                <select v-model="payStatus" @change="applyFilters"
                    class="rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                    <option value="">Tất cả thanh toán</option>
                    <option value="unpaid">Chưa thanh toán</option>
                    <option value="partial">Một phần</option>
                    <option value="paid">Đã thanh toán</option>
                </select>
            </div>

            <!-- Table -->
            <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                <div class="overflow-x-auto">
                <table class="w-full text-sm">
                    <thead class="bg-gray-50 border-b border-gray-200">
                        <tr>
                            <th class="text-left px-4 py-3 font-medium text-gray-600 whitespace-nowrap">Số HĐ</th>
                            <th class="text-left px-4 py-3 font-medium text-gray-600 whitespace-nowrap">Nhà cung cấp</th>
                            <th class="text-left px-4 py-3 font-medium text-gray-600 whitespace-nowrap">Ngày</th>
                            <th class="text-right px-4 py-3 font-medium text-gray-600 whitespace-nowrap">Tổng tiền</th>
                            <th class="text-center px-4 py-3 font-medium text-gray-600 whitespace-nowrap">Trạng thái</th>
                            <th class="text-center px-4 py-3 font-medium text-gray-600 whitespace-nowrap">Thanh toán</th>
                            <th class="px-4 py-3"></th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-100">
                        <tr v-for="inv in invoices.data" :key="inv.id"
                            class="hover:bg-gray-50 cursor-pointer transition-colors"
                            @click="router.visit('/admin/purchase-invoices/' + inv.id)">
                            <td class="px-4 py-3 font-mono text-indigo-600 font-medium whitespace-nowrap">{{ inv.invoice_number }}</td>
                            <td class="px-4 py-3 text-gray-700 whitespace-nowrap">{{ inv.supplier?.name ?? '—' }}</td>
                            <td class="px-4 py-3 text-gray-500 whitespace-nowrap">{{ formatDate(inv.invoice_date) }}</td>
                            <td class="px-4 py-3 text-right font-medium text-gray-900 whitespace-nowrap">{{ formatVND(inv.total_amount) }}</td>
                            <td class="px-4 py-3 text-center whitespace-nowrap">
                                <span :class="['inline-flex rounded-full px-2 py-0.5 text-xs font-medium', statusColors[inv.status]]">
                                    {{ statusLabels[inv.status] }}
                                </span>
                            </td>
                            <td class="px-4 py-3 text-center whitespace-nowrap">
                                <span :class="['inline-flex rounded-full px-2 py-0.5 text-xs font-medium', payColors[inv.payment_status]]">
                                    {{ payLabels[inv.payment_status] }}
                                </span>
                            </td>
                            <td class="px-4 py-3">
                                <Eye :size="16" class="text-gray-400" />
                            </td>
                        </tr>
                        <tr v-if="!invoices.data?.length">
                            <td colspan="7" class="px-4 py-8 text-center text-gray-400">Chưa có hóa đơn nào</td>
                        </tr>
                    </tbody>
                </table>
                </div>
            </div>

            <!-- Pagination -->
            <div v-if="invoices.last_page > 1" class="flex justify-center gap-1">
                <button v-for="link in invoices.links" :key="link.label"
                    v-html="link.label"
                    :disabled="!link.url"
                    @click="link.url && router.visit(link.url)"
                    :class="['px-3 py-1.5 rounded-lg text-sm transition-colors', link.active ? 'bg-indigo-600 text-white' : 'text-gray-600 hover:bg-gray-100 disabled:opacity-40']" />
            </div>
        </div>
    </AdminLayout>
</template>
