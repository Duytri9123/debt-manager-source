<script setup>
import { computed } from 'vue'
import { router } from '@inertiajs/vue3'
import AdminLayout from '@/Layouts/AdminLayout.vue'
import { useFilters } from '@/composables/useFilters.js'
import { useCurrency } from '@/composables/useCurrency.js'
import { Search, Plus, AlertTriangle } from 'lucide-vue-next'

const props = defineProps({
    debts:   Object,
    filters: Object,
    stats:   Object,
})

const { formatVND } = useCurrency()
const { filters, applyFilters, resetFilters } = useFilters(
    { search: props.filters?.search ?? '', status: props.filters?.status ?? '' },
    '/admin/debts'
)

const STATUS_LABELS = {
    pending: 'Chờ thanh toán',
    partial: 'Thanh toán một phần',
    paid:    'Đã thanh toán',
}
const STATUS_CLASSES = {
    pending: 'bg-amber-50 text-amber-700 border border-amber-200',
    partial: 'bg-blue-50 text-blue-700 border border-blue-200',
    paid:    'bg-emerald-50 text-emerald-700 border border-emerald-200',
}

function goToDebt(id) { router.visit(`/admin/debts/${id}`) }

function formatDate(date) {
    if (!date) return '—'
    return new Date(date).toLocaleDateString('vi-VN')
}

// Tính remaining từ order.grand_total - paid_amount (tránh stale DB)
function debtRemaining(debt) {
    const grand = Number(debt.order?.grand_total ?? debt.original_amount ?? 0)
    const paid  = Number(debt.paid_amount ?? 0)
    return Math.max(0, grand - paid)
}

function debtOriginal(debt) {
    return Number(debt.order?.grand_total ?? debt.original_amount ?? 0)
}

function debtStatus(debt) {
    const paid = Number(debt.paid_amount ?? 0)
    const rem  = debtRemaining(debt)
    if (paid <= 0) return 'pending'
    if (rem <= 0)  return 'paid'
    return 'partial'
}

function isOverdue(debt) {
    if (!debt.due_date || debtStatus(debt) === 'paid') return false
    return new Date(debt.due_date) < new Date()
}
</script>

<template>
    <AdminLayout>
        <div class="space-y-5">
            <!-- Header -->
            <div class="flex flex-wrap items-center justify-between gap-3">
                <div>
                    <h1 class="text-xl font-bold text-gray-900">Quản lý Công Nợ</h1>
                    <p class="mt-0.5 text-sm text-gray-500">Theo dõi công nợ đơn hàng và lịch sử thanh toán</p>
                </div>
                <button @click="router.visit('/admin/debts/create')"
                    class="flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-700 transition-colors">
                    <Plus :size="16" /> Tạo công nợ
                </button>
            </div>

            <!-- Stats -->
            <div v-if="stats" class="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <div class="rounded-xl border border-gray-200 bg-white p-4 shadow-sm">
                    <p class="text-xs text-gray-400 uppercase tracking-wide">Tổng nợ gốc</p>
                    <p class="mt-1 text-lg font-bold text-gray-900">{{ formatVND(stats.total_original) }}</p>
                </div>
                <div class="rounded-xl border border-emerald-200 bg-emerald-50 p-4 shadow-sm">
                    <p class="text-xs text-emerald-600 uppercase tracking-wide">Đã thu</p>
                    <p class="mt-1 text-lg font-bold text-emerald-700">{{ formatVND(stats.total_paid) }}</p>
                </div>
                <div class="rounded-xl border border-red-200 bg-red-50 p-4 shadow-sm">
                    <p class="text-xs text-red-600 uppercase tracking-wide">Còn phải thu</p>
                    <p class="mt-1 text-lg font-bold text-red-700">{{ formatVND(stats.total_remaining) }}</p>
                </div>
                <div :class="['rounded-xl border p-4 shadow-sm', stats.count_overdue > 0 ? 'border-orange-200 bg-orange-50' : 'border-gray-200 bg-white']">
                    <p :class="['text-xs uppercase tracking-wide', stats.count_overdue > 0 ? 'text-orange-600' : 'text-gray-400']">
                        Quá hạn
                    </p>
                    <p :class="['mt-1 text-lg font-bold', stats.count_overdue > 0 ? 'text-orange-700' : 'text-gray-400']">
                        {{ stats.count_overdue }} đơn
                    </p>
                </div>
            </div>

            <!-- Filters -->
            <div class="flex flex-wrap gap-3 bg-white rounded-xl border border-gray-200 p-3">
                <div class="relative flex-1 min-w-48">
                    <Search :size="15" class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                    <input v-model="filters.search" @input="applyFilters()" type="text"
                        placeholder="Tìm mã đơn, tên khách hàng..."
                        class="w-full rounded-lg border border-gray-300 pl-9 pr-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                </div>
                <select v-model="filters.status" @change="applyFilters(true)"
                    class="rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                    <option value="">Tất cả trạng thái</option>
                    <option value="pending">⏳ Chờ thanh toán</option>
                    <option value="partial">🔄 Thanh toán một phần</option>
                    <option value="paid">✅ Đã thanh toán</option>
                </select>
                <button v-if="filters.search || filters.status" @click="resetFilters()"
                    class="rounded-lg border border-gray-300 px-3 py-2 text-sm text-gray-600 hover:bg-gray-50 transition-colors">
                    Xóa bộ lọc
                </button>
            </div>

            <!-- Table -->
            <div class="overflow-x-auto rounded-xl border border-gray-200 bg-white shadow-sm">
                <div v-if="!debts?.data?.length" class="px-6 py-12 text-center text-sm text-gray-400">
                    Không có công nợ nào
                </div>
                <table v-else class="w-full text-sm">
                    <thead class="bg-gray-50 text-left text-xs font-medium uppercase tracking-wide text-gray-500 border-b border-gray-200">
                        <tr>
                            <th class="px-4 py-3">Mã đơn hàng</th>
                            <th class="px-4 py-3">Khách hàng</th>
                            <th class="px-4 py-3 text-right">Số tiền gốc</th>
                            <th class="px-4 py-3 text-right">Đã thanh toán</th>
                            <th class="px-4 py-3 text-right">Còn lại</th>
                            <th class="px-4 py-3">Trạng thái</th>
                            <th class="px-4 py-3">Ngày tạo đơn</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-100">
                        <tr v-for="debt in debts.data" :key="debt.id"
                            @click="goToDebt(debt.id)"
                            class="cursor-pointer hover:bg-indigo-50/40 transition-colors">
                            <td class="px-4 py-3">
                                <div class="font-semibold text-gray-800 text-sm">
                                    {{ debt.order?.order_name || debt.order?.order_number || `#${debt.order_id}` }}
                                </div>
                                <div class="font-mono text-xs text-indigo-500 mt-0.5">
                                    {{ debt.order?.order_number ?? '' }}
                                </div>
                            </td>
                            <td class="px-4 py-3 text-gray-700 font-medium">
                                {{ debt.order?.customer_name ?? debt.user?.name ?? '—' }}
                            </td>
                            <td class="px-4 py-3 text-right text-gray-700">{{ formatVND(debtOriginal(debt)) }}</td>
                            <td class="px-4 py-3 text-right text-emerald-600 font-medium">{{ formatVND(debt.paid_amount) }}</td>
                            <td class="px-4 py-3 text-right font-bold"
                                :class="debtRemaining(debt) > 0 ? 'text-red-600' : 'text-gray-400'">
                                {{ formatVND(debtRemaining(debt)) }}
                            </td>
                            <td class="px-4 py-3">
                                <span :class="['inline-flex rounded-full px-2 py-0.5 text-xs font-medium', STATUS_CLASSES[debtStatus(debt)]]">
                                    {{ STATUS_LABELS[debtStatus(debt)] }}
                                </span>
                            </td>
                            <td class="px-4 py-3 text-sm text-gray-500">
                                {{ formatDate(debt.order?.created_at) }}
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <!-- Pagination -->
            <div v-if="debts?.last_page > 1" class="flex items-center justify-between text-sm text-gray-600">
                <span>Trang {{ debts.current_page }} / {{ debts.last_page }} · {{ debts.total }} công nợ</span>
                <div class="flex gap-2">
                    <button :disabled="debts.current_page === 1"
                        @click="router.visit(debts.prev_page_url)"
                        class="rounded border border-gray-300 px-3 py-1 hover:bg-gray-50 disabled:opacity-40 transition-colors">
                        Trước
                    </button>
                    <button :disabled="debts.current_page === debts.last_page"
                        @click="router.visit(debts.next_page_url)"
                        class="rounded border border-gray-300 px-3 py-1 hover:bg-gray-50 disabled:opacity-40 transition-colors">
                        Sau
                    </button>
                </div>
            </div>
        </div>
    </AdminLayout>
</template>
