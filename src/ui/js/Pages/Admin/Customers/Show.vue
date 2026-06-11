<script setup>
import { ref } from 'vue'
import { useForm, router, Link } from '@inertiajs/vue3'
import AdminLayout from '@/Layouts/AdminLayout.vue'
import { useCurrency } from '@/composables/useCurrency.js'
import {
    ArrowLeft, Edit, Ban, CheckCircle, Plus, ShoppingBag,
    FileInput, AlertCircle, Trash2, ChevronDown, ChevronRight, Package, CreditCard
} from 'lucide-vue-next'

const props = defineProps({
    customer:         Object,
    orders:           Object,
    purchaseInvoices: Object,
    debts:            Object,
    summary:          Object,
})

const { formatVND } = useCurrency()

const editMode = ref(false)
const editForm = useForm({
    name:     props.customer.name,
    phone:    props.customer.phone,
    email:    props.customer.email ?? '',
    tax_code: props.customer.tax_code ?? '',
    address:  props.customer.address ?? '',
    notes:    props.customer.notes ?? '',
})

function submitEdit() {
    editForm.patch(`/admin/customers/${props.customer.id}`, {
        onSuccess: () => { editMode.value = false },
    })
}

function toggleActive() {
    if (props.customer.is_active) {
        if (confirm('Vô hiệu hóa khách hàng này?')) {
            router.post(`/admin/customers/${props.customer.id}/deactivate`)
        }
    } else {
        if (confirm('Kích hoạt lại khách hàng này?')) {
            router.post(`/admin/customers/${props.customer.id}/activate`)
        }
    }
}

function deleteCustomer() {
    if (confirm(`Xóa khách hàng "${props.customer.name}"? Hành động này không thể hoàn tác!`)) {
        router.delete(`/admin/customers/${props.customer.id}`)
    }
}

const PAY_LABELS  = { unpaid: '⏳ Chưa TT', partial: '🔄 Một phần', paid: '✅ Đã TT' }

// ── Expandable rows ───────────────────────────────────────────────────────────
const expandedOrders      = ref(new Set())
const expandedInvoices    = ref(new Set())
const expandedDebtDetails = ref(new Set())
const expandedInvPayments = ref(new Set())

function toggleOrder(id) {
    if (expandedOrders.value.has(id)) expandedOrders.value.delete(id)
    else expandedOrders.value.add(id)
}
function toggleInvoice(id) {
    if (expandedInvoices.value.has(id)) expandedInvoices.value.delete(id)
    else expandedInvoices.value.add(id)
}
function toggleDebtDetail(id) {
    if (expandedDebtDetails.value.has(id)) expandedDebtDetails.value.delete(id)
    else expandedDebtDetails.value.add(id)
}
function toggleInvPayment(id) {
    if (expandedInvPayments.value.has(id)) expandedInvPayments.value.delete(id)
    else expandedInvPayments.value.add(id)
}

// ── Collapse sections ────────────────────────────────────────────────────────
const showOrders   = ref(true)
const showImports  = ref(false)
const showDebtPanel = ref(true)


const STATUS_LABELS = {
    pending:    'Chờ xử lý',
    processing: 'Đang xử lý',
    shipped:    'Đang giao',
    delivered:  'Đã giao',
    cancelled:  'Đã hủy',
}
const STATUS_CLASSES = {
    pending:    'bg-yellow-100 text-yellow-800 border border-yellow-300 shadow-sm',
    processing: 'bg-blue-100 text-blue-800 border border-blue-300 shadow-sm',
    shipped:    'bg-indigo-100 text-indigo-800 border border-indigo-300 shadow-sm',
    delivered:  'bg-emerald-100 text-emerald-800 border border-emerald-300 shadow-sm',
    cancelled:  'bg-red-100 text-red-700 border border-red-300 shadow-sm',
}
function orderStatusLabel(s) { return STATUS_LABELS[s] ?? s }
function orderStatusClass(s) { return STATUS_CLASSES[s] ?? 'bg-gray-100 text-gray-600' }

// Tính tổng đã thanh toán và công nợ từ debts của đơn hàng
function orderPaid(order) {
    if (order.debts?.length) {
        return order.debts.reduce((sum, d) => sum + Number(d.paid_amount ?? 0), 0)
    }
    if (order.payment_status === 'paid') return Number(order.grand_total)
    return 0
}
function orderDebt(order) {
    const grand = Number(order.grand_total ?? 0)
    if (order.debts?.length) {
        // Tính remaining = grand_total - paid_amount để tránh stale remaining_amount
        const paid = order.debts.reduce((sum, d) => sum + Number(d.paid_amount ?? 0), 0)
        return Math.max(0, grand - paid)
    }
    if (order.payment_status === 'unpaid')  return grand
    if (order.payment_status === 'paid')    return 0
    if (order.payment_status === 'partial') return grand - orderPaid(order)
    return 0
}

// Tính remaining từ order.grand_total - paid_amount (tránh stale DB)
function debtRemaining(debt) {
    const grand = Number(debt.order?.grand_total ?? debt.original_amount ?? 0)
    const paid  = Number(debt.paid_amount ?? 0)
    return Math.max(0, grand - paid)
}
function debtStatus(debt) {
    const paid = Number(debt.paid_amount ?? 0)
    const rem  = debtRemaining(debt)
    if (paid <= 0) return 'pending'
    if (rem <= 0)  return 'paid'
    return 'partial'
}
function debtOriginal(debt) {
    return Number(debt.order?.grand_total ?? debt.original_amount ?? 0)
}

function isItemCategory(item) {
    try {
        const a = typeof item.variant_attributes === 'string'
            ? JSON.parse(item.variant_attributes)
            : (item.variant_attributes ?? {})
        return a?.type === 'category'
    } catch { return false }
}

function orderItemSeqNum(items, idx) {
    let num = 0
    for (let i = 0; i <= idx; i++) {
        if (isItemCategory(items[i])) num = 0
        else num++
    }
    return num
}

function orderCategoryTotal(items, idx) {
    let total = 0
    for (let i = idx + 1; i < items.length; i++) {
        if (isItemCategory(items[i])) break
        total += Number(items[i].price ?? 0) * Number(items[i].quantity ?? 0)
    }
    return total
}

function fmtDate(d) {
    if (!d) return '—'
    return new Date(d).toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

function copyText(text) {
    navigator.clipboard?.writeText(text).catch(() => {})
}
</script>

<template>
    <AdminLayout>
        <div class="space-y-5">
            <button @click="router.visit('/admin/customers')"
                class="flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-700 transition-colors">
                <ArrowLeft :size="15" /> Quay lại danh sách
            </button>

            <!-- Profile header -->
            <div class="rounded-xl border border-gray-200 bg-white p-4 lg:p-6 shadow-sm">
                <!-- Hàng 1: Tên + nút Sửa (cả mobile lẫn desktop) -->
                <div class="flex items-center justify-between gap-2 mb-2">
                    <div class="flex items-center gap-3 min-w-0">
                        <!-- Avatar: chỉ hiện trên desktop -->
                        <div class="hidden sm:flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-indigo-100 text-lg font-bold text-indigo-600">
                            {{ customer.name?.charAt(0)?.toUpperCase() ?? '?' }}
                        </div>
                        <h1 class="text-lg font-bold text-gray-900 truncate">{{ customer.name }}</h1>
                    </div>
                    <button @click="editMode = !editMode"
                        class="shrink-0 flex items-center gap-1.5 rounded-lg border border-gray-300 px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors">
                        <Edit :size="14" /> Sửa
                    </button>
                </div>

                <!-- Thông tin: 2 cột trên mobile, 1 hàng trên desktop -->
                <div class="grid grid-cols-2 sm:flex sm:flex-wrap items-center gap-x-3 gap-y-1.5 text-sm text-gray-500">
                    <a v-if="customer.tax_code"
                        @click.prevent="copyText(customer.tax_code)"
                        href="#" title="Copy MST"
                        class="flex items-center gap-1 hover:text-indigo-600 transition-colors">
                        <span class="text-gray-400 text-xs">MST:</span> {{ customer.tax_code }}
                    </a>
                    <a v-if="customer.phone" :href="`tel:${customer.phone}`"
                        class="flex items-center gap-1 hover:text-indigo-600 transition-colors">
                        📞 {{ customer.phone }}
                    </a>
                    <a v-if="customer.email" :href="`mailto:${customer.email}`"
                        class="flex items-center gap-1 hover:text-indigo-600 transition-colors truncate">
                        ✉️ {{ customer.email }}
                    </a>
                    <a v-if="customer.address"
                        @click.prevent="copyText(customer.address)"
                        href="#" title="Copy địa chỉ"
                        class="flex items-center gap-1 hover:text-indigo-600 transition-colors truncate">
                        📍 {{ customer.address }}
                    </a>
                </div>

                <!-- Ngày tạo + badge -->
                <div class="flex items-center gap-2 mt-2">
                    <p class="text-xs text-gray-400">Ngày tạo: {{ fmtDate(customer.created_at) }}</p>
                    <span v-if="!customer.is_active" class="inline-flex rounded-full bg-red-100 px-2 py-0.5 text-xs font-medium text-red-700">Không hoạt động</span>
                    <span v-else class="inline-flex rounded-full bg-emerald-100 px-2 py-0.5 text-xs font-medium text-emerald-700">Hoạt động</span>
                </div>
            </div>

            <!-- Edit form -->
            <div v-if="editMode" class="rounded-xl border border-indigo-200 bg-indigo-50 p-3 lg:p-5 shadow-sm">
                <h2 class="font-semibold text-gray-900 mb-4">Chỉnh sửa thông tin</h2>
                <form @submit.prevent="submitEdit" class="space-y-4">
                    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">Tên *</label>
                            <input v-model="editForm.name" type="text" required
                                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                        </div>
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">Số điện thoại *</label>
                            <input v-model="editForm.phone" type="text" required
                                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                        </div>
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
                            <input v-model="editForm.email" type="email"
                                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                        </div>
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">Mã số thuế</label>
                            <input v-model="editForm.tax_code" type="text"
                                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                                placeholder="Nhập mã số thuế (tùy chọn)" />
                        </div>
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">Địa chỉ</label>
                            <input v-model="editForm.address" type="text"
                                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                        </div>
                    </div>
                    <div class="flex gap-2">
                        <button type="submit" :disabled="editForm.processing"
                            class="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-700 disabled:opacity-60 transition-colors">
                            {{ editForm.processing ? 'Đang lưu...' : 'Lưu' }}
                        </button>
                        <button type="button" @click="editMode = false"
                            class="rounded-lg border border-gray-300 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors">
                            Hủy
                        </button>
                    </div>
                </form>
            </div>

            <!-- Thống kê -->
            <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
                <div class="bg-white rounded-xl border border-gray-200 p-4 shadow-sm">
                    <div class="flex items-center gap-2 mb-1">
                        <div class="p-1.5 bg-indigo-100 rounded-lg shrink-0">
                            <ShoppingBag :size="16" class="text-indigo-600" />
                        </div>
                        <p class="text-xs text-gray-500">Đơn hàng</p>
                    </div>
                    <p class="font-bold text-gray-900 leading-tight">
                        <span class="text-xl">{{ summary?.total_orders_count ?? 0 }}</span>
                        <span class="text-xs text-gray-500 font-normal ml-1">{{ formatVND(summary?.total_orders) }}</span>
                    </p>
                </div>

                <div class="bg-white rounded-xl border border-gray-200 p-4 shadow-sm">
                    <div class="flex items-center gap-2 mb-1">
                        <div class="p-1.5 bg-emerald-100 rounded-lg shrink-0">
                            <CheckCircle :size="16" class="text-emerald-600" />
                        </div>
                        <p class="text-xs text-gray-500">Đã thanh toán</p>
                    </div>
                    <p class="text-lg font-bold text-emerald-600 leading-tight">{{ formatVND(summary?.total_paid) }}</p>
                </div>

                <div class="bg-white rounded-xl border border-gray-200 p-4 shadow-sm">
                    <div class="flex items-center gap-2 mb-1">
                        <div class="p-1.5 bg-purple-100 rounded-lg shrink-0">
                            <FileInput :size="16" class="text-purple-600" />
                        </div>
                        <p class="text-xs text-gray-500">Nhập hàng</p>
                    </div>
                    <p class="font-bold text-gray-900 leading-tight">
                        <span class="text-xl">{{ summary?.total_purchases_count ?? 0 }}</span>
                        <span class="text-xs text-gray-500 font-normal ml-1">{{ formatVND(summary?.total_purchases) }}</span>
                    </p>
                </div>

                <div :class="['rounded-xl border p-4 shadow-sm', summary?.remaining_debt > 0 ? 'bg-red-50 border-red-200' : 'bg-emerald-50 border-emerald-200']">
                    <div class="flex items-center gap-2 mb-1">
                        <div :class="['p-1.5 rounded-lg shrink-0', summary?.remaining_debt > 0 ? 'bg-red-100' : 'bg-emerald-100']">
                            <AlertCircle :size="16" :class="summary?.remaining_debt > 0 ? 'text-red-600' : 'text-emerald-600'" />
                        </div>
                        <p class="text-xs text-gray-500">Công nợ</p>
                    </div>
                    <p :class="['text-lg font-bold leading-tight', summary?.remaining_debt > 0 ? 'text-red-600' : 'text-emerald-600']">
                        {{ formatVND(summary?.remaining_debt) }}
                    </p>
                </div>
            </div>

            <!-- Layout: Đơn bán (trái) + Thông tin thanh toán (phải) -->
            <div class="grid grid-cols-1 lg:grid-cols-3 gap-5">
                <!-- Đơn hàng bán ra — chiếm 2/3 -->
                <div class="lg:col-span-2 bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
                    <div class="flex items-center justify-between px-4 py-3 border-b bg-indigo-50 cursor-pointer select-none"
                        @click="showOrders = !showOrders">
                        <div class="flex items-center gap-2">
                            <ShoppingBag :size="16" class="text-indigo-600" />
                            <h2 class="font-semibold text-indigo-900 text-sm">Đơn hàng bán ra</h2>
                            <span class="text-xs bg-indigo-200 text-indigo-700 px-2 py-0.5 rounded-full font-medium">
                                {{ summary?.total_orders_count ?? 0 }}
                            </span>
                        </div>
                        <div class="flex items-center gap-2">
                            <Link :href="`/admin/b2b-orders/create?customer_id=${customer.id}`"
                                @click.stop
                                class="flex items-center gap-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-700 active:bg-indigo-800 px-3 py-1.5 text-xs font-semibold text-white shadow-sm transition-colors">
                                <Plus :size="13" /> Thêm đơn hàng
                            </Link>
                            <ChevronDown :size="16" :class="['text-indigo-400 transition-transform duration-200', showOrders ? 'rotate-0' : '-rotate-90']" />
                        </div>
                    </div>

                    <div v-show="showOrders">

                    <div v-if="!orders?.data?.length" class="py-12 text-center text-sm text-gray-400">
                        Chưa có đơn hàng
                    </div>
                    <div v-else class="p-2 space-y-2">
                        <div v-for="order in orders.data" :key="order.id"
                            class="rounded-lg border border-indigo-100 bg-gradient-to-br from-white to-indigo-50/40 shadow-sm overflow-hidden transition-colors">
                            <!-- Row chính -->
                            <div class="px-3 py-2.5 flex items-start gap-2 hover:bg-indigo-50/60">
                                <!-- Nội dung, click để mở trang -->
                                <div class="flex-1 cursor-pointer min-w-0" @click="router.visit(`/admin/b2b-orders/${order.id}`)">
                                    <!-- Dòng 1: tên đơn hàng -->
                                    <div class="mb-0.5">
                                        <span v-if="order.order_name" class="text-sm font-bold text-gray-900">{{ order.order_name }}</span>
                                        <span v-else class="font-mono text-xs text-indigo-500">{{ order.order_number }}</span>
                                    </div>
                                    <!-- Dòng 2: mã đơn (trái) + trạng thái (phải) -->
                                    <div class="flex items-center justify-between gap-2 mb-1">
                                        <span class="font-mono text-[11px] text-indigo-400">{{ order.order_number }}</span>
                                        <span :class="['inline-flex items-center text-xs font-semibold px-2 py-0.5 rounded-full', orderStatusClass(order.status)]">
                                            {{ orderStatusLabel(order.status) }}
                                        </span>
                                    </div>
                                    <!-- Dòng 3: ngày nhập / xuất -->
                                    <div class="flex items-center justify-between mb-2">
                                        <span class="text-[11px] font-medium text-emerald-700 bg-emerald-50 border border-emerald-200 px-1.5 py-0.5 rounded">
                                            Nhập: {{ fmtDate(order.created_at) }}
                                        </span>
                                        <span v-if="order.delivery_date" class="text-[11px] font-medium text-rose-700 bg-rose-50 border border-rose-200 px-1.5 py-0.5 rounded">
                                            Xuất: {{ fmtDate(order.delivery_date) }}
                                        </span>
                                    </div>
                                    <!-- Dòng 4: Tổng ĐH | Thanh toán | Công nợ -->
                                    <div class="grid grid-cols-3 gap-x-2 text-xs border-t border-indigo-100/60 pt-1.5">
                                        <p class="font-bold text-gray-900">{{ formatVND(order.grand_total) }}</p>
                                        <p class="font-semibold text-emerald-600">{{ formatVND(orderPaid(order)) }}</p>
                                        <p :class="['font-bold', orderDebt(order) > 0 ? 'text-red-600' : 'text-gray-400']">
                                            {{ orderDebt(order) > 0 ? formatVND(orderDebt(order)) : '—' }}
                                        </p>
                                    </div>
                                </div>
                                <!-- Toggle dropdown — bên phải -->
                                <button @click.stop="toggleOrder(order.id)"
                                    class="shrink-0 self-center p-1 rounded-md text-gray-400 hover:text-indigo-600 hover:bg-indigo-100 transition-colors">
                                    <ChevronDown v-if="expandedOrders.has(order.id)" :size="15" class="text-indigo-600" />
                                    <ChevronRight v-else :size="15" />
                                </button>
                            </div>

                            <!-- Dropdown sản phẩm -->
                            <div v-if="expandedOrders.has(order.id) && order.items?.length"
                                class="bg-indigo-50/40 border-t border-indigo-100 px-4 py-2">
                                <table class="w-full text-xs table-fixed">
                                    <thead>
                                        <tr class="text-gray-500 border-b border-indigo-100">
                                            <th class="text-left py-1.5 font-medium w-[45%] sm:w-auto">Sản phẩm</th>
                                            <th class="hidden sm:table-cell text-center py-1.5 font-medium w-[80px]">Mã hàng</th>
                                            <th class="text-right py-1.5 font-medium w-[20px] sm:w-[40px]">SL</th>
                                            <th class="text-right py-1.5 font-medium w-[27%] sm:w-[88px]">Đơn giá</th>
                                            <th class="text-right py-1.5 font-medium w-[28%] sm:w-[88px]">Thành tiền</th>
                                        </tr>
                                    </thead>
                                    <tbody class="divide-y divide-indigo-100/60">
                                        <template v-for="(item, idx) in order.items" :key="item.id">
                                            <!-- Category row -->
                                            <tr v-if="isItemCategory(item)" class="bg-amber-50 border-l-2 border-amber-400">
                                                <td colspan="4" class="py-1.5 px-2">
                                                    <span class="text-xs font-bold text-amber-800">📁 {{ item.product_name }}</span>
                                                </td>
                                                <td class="py-1.5 text-right font-bold text-amber-700 text-xs">
                                                    {{ formatVND(orderCategoryTotal(order.items, idx)) }}
                                                </td>
                                            </tr>
                                            <!-- Item row -->
                                            <tr v-else class="text-gray-700">
                                                <td class="py-1.5 pr-2">
                                                    <p class="font-medium">{{ item.product_name }}</p>
                                                    <p v-if="item.origin" class="text-gray-400 text-[10px]">{{ item.origin }}</p>
                                                </td>
                                                <td class="hidden sm:table-cell py-1.5 text-center text-gray-400 font-mono text-[10px]">{{ item.variant_sku || '—' }}</td>
                                                <td class="py-1.5 text-right font-medium">{{ item.quantity }}</td>
                                                <td class="py-1.5 text-right">{{ formatVND(item.price) }}</td>
                                                <td class="py-1.5 text-right font-semibold text-gray-900">
                                                    {{ formatVND(item.line_total ?? (item.price * item.quantity)) }}
                                                </td>
                                            </tr>
                                        </template>
                                    </tbody>
                                    <tfoot class="border-t border-indigo-200 text-xs">
                                        <tr class="text-gray-500">
                                            <td colspan="3" class="sm:hidden pt-2 pb-0.5 text-right">Tổng tiền hàng:</td>
                                            <td colspan="4" class="hidden sm:table-cell pt-2 pb-0.5 text-right">Tổng tiền hàng:</td>
                                            <td class="pt-2 pb-0.5 text-right font-medium text-gray-700">{{ formatVND(order.subtotal) }}</td>
                                        </tr>
                                        <tr v-if="order.discount_amount > 0" class="text-gray-500">
                                            <td colspan="3" class="sm:hidden py-0.5 text-right">Giảm giá:</td>
                                            <td colspan="4" class="hidden sm:table-cell py-0.5 text-right">Giảm giá:</td>
                                            <td class="py-0.5 text-right font-medium text-emerald-600">- {{ formatVND(order.discount_amount) }}</td>
                                        </tr>
                                        <tr class="text-gray-500">
                                            <td colspan="3" class="sm:hidden py-0.5 text-right">
                                                Thuế VAT
                                                <span v-if="order.subtotal > 0 && (order.grand_total - order.subtotal) > 0">
                                                    ({{ Math.round((order.grand_total - order.subtotal) / order.subtotal * 100) }}%):
                                                </span>
                                                <span v-else>:</span>
                                            </td>
                                            <td colspan="4" class="hidden sm:table-cell py-0.5 text-right">
                                                Thuế VAT
                                                <span v-if="order.subtotal > 0 && (order.grand_total - order.subtotal) > 0">
                                                    ({{ Math.round((order.grand_total - order.subtotal) / order.subtotal * 100) }}%):
                                                </span>
                                                <span v-else>:</span>
                                            </td>
                                            <td class="py-0.5 text-right font-medium text-orange-600">
                                                {{ formatVND(Math.max(0, order.grand_total - order.subtotal)) }}
                                            </td>
                                        </tr>
                                        <tr class="font-semibold text-gray-800 border-t border-indigo-100">
                                            <td colspan="3" class="sm:hidden pt-1.5 text-right">Sau thuế:</td>
                                            <td colspan="4" class="hidden sm:table-cell pt-1.5 text-right">Sau thuế:</td>
                                            <td class="pt-1.5 text-right text-indigo-700">{{ formatVND(order.grand_total) }}</td>
                                        </tr>
                                    </tfoot>
                                </table>
                            </div>
                            <div v-else-if="expandedOrders.has(order.id)"
                                class="bg-indigo-50/40 border-t border-indigo-100 px-4 py-3 text-xs text-gray-400 text-center">
                                Không có sản phẩm
                            </div>
                        </div>
                    </div>
                    </div><!-- end v-show orders -->
                </div>

                <!-- Thông tin thanh toán — cột phải 1/3 -->
                <div class="lg:col-span-1">
                    <div v-if="debts?.data?.length > 0 || summary?.remaining_debt > 0" class="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
                        <!-- Header — click để toggle -->
                        <div class="flex items-center justify-between px-4 py-3 border-b bg-gray-50 cursor-pointer select-none"
                            @click="showDebtPanel = !showDebtPanel">
                            <div class="flex items-center gap-2">
                                <CreditCard :size="16" class="text-blue-600" />
                                <h2 class="font-semibold text-gray-800 text-sm">Thông tin thanh toán</h2>
                                <span class="text-xs bg-gray-200 text-gray-600 px-2 py-0.5 rounded-full font-medium">
                                    {{ debts.data.length }} đơn
                                </span>
                            </div>
                            <div class="flex items-center gap-2 text-xs">
                                <span class="text-gray-500">Còn lại:
                                    <span class="font-bold" :class="summary?.remaining_debt > 0 ? 'text-red-600' : 'text-emerald-600'">
                                        {{ formatVND(summary?.remaining_debt) }}
                                    </span>
                                </span>
                                <ChevronDown :size="15" :class="['text-gray-400 transition-transform duration-200', showDebtPanel ? 'rotate-0' : '-rotate-90']" />
                            </div>
                        </div>

                        <!-- Nội dung có thể ẩn/hiện -->
                        <div v-show="showDebtPanel">
                        <!-- Summary bar -->
                        <div class="grid grid-cols-3 divide-x divide-gray-100 bg-gray-50/50 border-b border-gray-100">
                            <div class="px-3 py-2 text-center">
                                <p class="text-xs text-gray-400 mb-0.5">Tổng</p>
                                <p class="text-xs font-semibold text-gray-700">{{ formatVND(summary?.total_debt) }}</p>
                            </div>
                            <div class="px-3 py-2 text-center">
                                <p class="text-xs text-gray-400 mb-0.5">Đã TT</p>
                                <p class="text-xs font-semibold text-emerald-600">{{ formatVND(summary?.paid_debt) }}</p>
                            </div>
                            <div class="px-3 py-2 text-center">
                                <p class="text-xs text-gray-400 mb-0.5">Còn nợ</p>
                                <p class="text-xs font-semibold" :class="summary?.remaining_debt > 0 ? 'text-red-600' : 'text-emerald-600'">
                                    {{ formatVND(summary?.remaining_debt) }}
                                </p>
                            </div>
                        </div>

                        <!-- Danh sách từng đơn -->
                        <div class="divide-y divide-gray-100">
                            <!-- Khi không có debt record nhưng có công nợ từ payment_status -->
                            <div v-if="!debts?.data?.length && summary?.remaining_debt > 0"
                                class="px-4 py-4 text-center">
                                <p class="text-xs text-gray-500 mb-1">Công nợ từ đơn hàng chưa thanh toán</p>
                                <p class="text-sm font-bold text-red-600">{{ formatVND(summary?.remaining_debt) }}</p>
                                <p class="text-xs text-gray-400 mt-1">Chưa có phiếu công nợ riêng</p>
                            </div>
                            <div v-for="debt in debts.data" :key="debt.id"
                                class="transition-colors">
                                <!-- Row chính -->
                                <div class="px-3 py-2.5 flex items-center justify-between gap-2 hover:bg-blue-50/30 cursor-pointer"
                                    @click="toggleDebtDetail(debt.id)">
                                    <div class="flex-1 min-w-0">
                                        <!-- Dòng 1: tên + badge -->
                                        <div class="flex items-center gap-1.5 mb-0.5 flex-wrap">
                                            <span class="font-semibold text-sm text-gray-900 truncate">
                                                {{ debt.order?.order_name || debt.order?.order_number || 'N/A' }}
                                            </span>
                                            <span :class="['text-[10px] px-1.5 py-0.5 rounded-full font-medium shrink-0',
                                                debtStatus(debt) === 'paid'    ? 'bg-emerald-100 text-emerald-700' :
                                                debtStatus(debt) === 'partial' ? 'bg-blue-100 text-blue-700' :
                                                                                 'bg-orange-100 text-orange-700']">
                                                {{ debtStatus(debt) === 'paid' ? '✓ Đã TT' : debtStatus(debt) === 'partial' ? '◑ Một phần' : '○ Chưa TT' }}
                                            </span>
                                        </div>
                                        <!-- Dòng 2: mã đơn hàng -->
                                        <div v-if="debt.order?.order_name" class="font-mono text-[10px] text-blue-400 mb-0.5">
                                            {{ debt.order?.order_number }}
                                        </div>
                                        <!-- Dòng 3: gốc · đã TT -->
                                        <div class="text-[11px] text-gray-600 font-medium space-x-1">
                                            <span>Gốc: {{ formatVND(debtOriginal(debt)) }}</span>
                                            <span>·</span>
                                            <span>Đã TT: <span class="text-emerald-600">{{ formatVND(debt.paid_amount) }}</span></span>
                                        </div>
                                    </div>
                                    <div class="flex items-center gap-1.5 shrink-0">
                                        <div class="text-right">
                                            <p class="text-sm font-bold" :class="debtRemaining(debt) > 0 ? 'text-red-600' : 'text-emerald-600'">
                                                {{ formatVND(debtRemaining(debt)) }}
                                            </p>
                                            <p class="text-[10px] text-gray-400">còn lại</p>
                                        </div>
                                        <ChevronDown :size="14" :class="['text-gray-400 transition-transform duration-200', expandedDebtDetails.has(debt.id) ? 'rotate-0' : '-rotate-90']" />
                                    </div>
                                </div>
                                <!-- Dropdown chi tiết -->
                                <div v-if="expandedDebtDetails.has(debt.id)" class="border-t border-blue-100">
                                    <!-- Tóm tắt -->
                                    <div class="grid grid-cols-3 divide-x divide-blue-100 bg-blue-50/30 text-xs">
                                        <div class="px-3 py-1.5 text-center">
                                            <p class="text-gray-400">Tiền gốc</p>
                                            <p class="font-semibold text-gray-700">{{ formatVND(debtOriginal(debt)) }}</p>
                                        </div>
                                        <div class="px-3 py-1.5 text-center">
                                            <p class="text-gray-400">Đã TT</p>
                                            <p class="font-semibold text-emerald-600">{{ formatVND(debt.paid_amount) }}</p>
                                        </div>
                                        <div class="px-3 py-1.5 text-center">
                                            <p class="text-gray-400">Còn lại</p>
                                            <p class="font-semibold" :class="debtRemaining(debt) > 0 ? 'text-red-600' : 'text-emerald-600'">{{ formatVND(debtRemaining(debt)) }}</p>
                                        </div>
                                    </div>

                                    <!-- Lịch sử thanh toán -->
                                    <div v-if="debt.payments?.length" class="px-3 py-2 space-y-2">
                                        <p class="text-[10px] text-gray-400 font-medium uppercase tracking-wide flex items-center justify-between">
                                            <span>Lịch sử thanh toán</span>
                                            <span class="bg-gray-100 text-gray-600 px-1.5 py-0.5 rounded-full">{{ debt.payments.length }} lần</span>
                                        </p>
                                        <div v-for="(pay, idx) in debt.payments" :key="pay.id"
                                            class="flex items-start gap-2.5">
                                            <!-- Số thứ tự -->
                                            <div class="shrink-0 w-5 h-5 rounded-full bg-emerald-100 text-emerald-700 text-[10px] font-bold flex items-center justify-center mt-0.5">
                                                {{ idx + 1 }}
                                            </div>
                                            <div class="flex-1 min-w-0">
                                                <div class="flex items-center justify-between gap-1">
                                                    <span class="text-xs font-bold text-gray-800">{{ formatVND(pay.amount) }}</span>
                                                    <span class="text-[10px] text-gray-400 shrink-0">
                                                        {{ pay.paid_at ? new Date(pay.paid_at).toLocaleString('vi-VN', {hour:'2-digit', minute:'2-digit', day:'2-digit', month:'2-digit', year:'numeric'}) : '—' }}
                                                    </span>
                                                </div>
                                                <div class="flex items-center gap-1.5 mt-0.5 flex-wrap">
                                                    <span class="text-[10px] bg-gray-100 text-gray-600 px-1.5 py-0.5 rounded">
                                                        {{ pay.payment_method === 'transfer' ? 'Chuyển khoản' : pay.payment_method === 'cash' ? 'Tiền mặt' : (pay.payment_method ?? '—') }}
                                                    </span>
                                                    <span v-if="pay.notes" class="text-[10px] text-gray-400 italic truncate">{{ pay.notes }}</span>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                    <div v-else class="px-3 py-2 text-[10px] text-gray-400 text-center">
                                        Chưa có lịch sử thanh toán
                                    </div>

                                    <div class="px-3 pb-2">
                                        <button @click.stop="router.visit(`/admin/debts/${debt.id}`)"
                                            class="w-full text-center text-[10px] text-blue-600 hover:text-blue-800 hover:underline">
                                            Xem chi tiết →
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                        </div><!-- end v-show showDebtPanel -->
                    </div>

                    <!-- Không có công nợ -->
                    <div v-else class="bg-white rounded-xl border border-gray-200 shadow-sm p-6 text-center">
                        <CreditCard :size="28" class="text-gray-300 mx-auto mb-2" />
                        <p class="text-sm text-gray-400">Không có công nợ</p>
                    </div>
                </div>
            </div>

            <!-- Nhập hàng + Thông tin thanh toán nhập hàng -->
            <div class="grid grid-cols-1 lg:grid-cols-3 gap-5">
                <!-- Nhập hàng — 2/3 -->
                <div class="lg:col-span-2 bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
                    <div class="flex items-center justify-between px-4 py-3 border-b bg-purple-50 cursor-pointer select-none"
                        @click="showImports = !showImports">
                        <div class="flex items-center gap-2">
                            <FileInput :size="16" class="text-purple-600" />
                            <h2 class="font-semibold text-purple-900 text-sm">Nhập hàng</h2>
                            <span class="text-xs bg-purple-200 text-purple-700 px-2 py-0.5 rounded-full font-medium">
                                {{ summary?.total_purchases_count ?? 0 }}
                            </span>
                        </div>
                        <div class="flex items-center gap-2">
                            <Link :href="`/admin/purchase-invoices/create?customer_id=${customer.id}`"
                                @click.stop
                                class="flex items-center gap-1.5 rounded-lg bg-purple-600 hover:bg-purple-700 active:bg-purple-800 px-3 py-1.5 text-xs font-semibold text-white shadow-sm transition-colors">
                                <Plus :size="13" /> Thêm nhập hàng
                            </Link>
                            <ChevronDown :size="16" :class="['text-purple-400 transition-transform duration-200', showImports ? 'rotate-0' : '-rotate-90']" />
                        </div>
                    </div>

                    <div v-show="showImports">

                    <div v-if="!purchaseInvoices?.data?.length" class="py-12 text-center text-sm text-gray-400">
                        Chưa có hóa đơn nhập
                    </div>
                    <div v-else class="p-2 space-y-2">
                        <div v-for="inv in purchaseInvoices.data" :key="inv.id"
                            class="rounded-lg border border-purple-100 bg-gradient-to-br from-white to-purple-50/40 shadow-sm overflow-hidden transition-colors">
                            <!-- Row chính -->
                            <div class="px-3 py-2.5 flex items-start gap-2 hover:bg-purple-50/60">
                                <!-- Nội dung, click để mở trang -->
                                <div class="flex-1 cursor-pointer min-w-0" @click="router.visit(`/admin/purchase-invoices/${inv.id}`)">
                                    <div class="flex items-start justify-between gap-2 mb-0.5">
                                        <div class="flex flex-col gap-0.5 min-w-0">
                                            <span class="font-mono text-xs font-semibold text-purple-600">{{ inv.invoice_number }}</span>
                                        </div>
                                        <div class="text-right shrink-0">
                                            <div class="flex flex-col gap-0.5 items-end">
                                                <span class="text-xs text-gray-400">
                                                    📥 {{ fmtDate(inv.invoice_date) }}
                                                </span>
                                                <span v-if="inv.due_date" class="text-xs text-gray-400">
                                                    📤 {{ fmtDate(inv.due_date) }}
                                                </span>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="flex items-center justify-between">
                                        <span class="text-sm font-bold text-gray-900">{{ formatVND(inv.total_amount) }}</span>
                                        <span :class="['text-xs px-2 py-0.5 rounded-full font-medium',
                                            inv.payment_status === 'paid' ? 'bg-emerald-100 text-emerald-700' :
                                            inv.payment_status === 'partial' ? 'bg-blue-100 text-blue-700' :
                                            'bg-orange-100 text-orange-700']">
                                            {{ PAY_LABELS[inv.payment_status] ?? inv.payment_status }}
                                        </span>
                                    </div>
                                </div>
                                <!-- Toggle dropdown — bên phải -->
                                <button @click.stop="toggleInvoice(inv.id)"
                                    class="shrink-0 self-center ml-1 p-1 rounded-md text-gray-400 hover:text-purple-600 hover:bg-purple-100 transition-colors">
                                    <ChevronDown v-if="expandedInvoices.has(inv.id)" :size="16" class="text-purple-600" />
                                    <ChevronRight v-else :size="16" />
                                </button>
                            </div>

                            <!-- Dropdown sản phẩm nhập -->
                            <div v-if="expandedInvoices.has(inv.id) && inv.items?.length"
                                class="bg-purple-50/40 border-t border-purple-100 px-4 py-2">
                                <table class="w-full text-xs table-fixed">
                                    <thead>
                                        <tr class="text-gray-500 border-b border-purple-100">
                                            <th class="text-left py-1.5 font-medium">Sản phẩm</th>
                                            <th class="hidden sm:table-cell text-center py-1.5 font-medium w-[80px]">Mã hàng</th>
                                            <th class="text-right py-1.5 font-medium w-[28px] sm:w-[40px]">SL</th>
                                            <th class="text-right py-1.5 font-medium w-[76px] sm:w-[88px]">Đơn giá</th>
                                            <th class="text-right py-1.5 font-medium w-[80px] sm:w-[88px]">Thành tiền</th>
                                        </tr>
                                    </thead>
                                    <tbody class="divide-y divide-purple-100/60">
                                        <tr v-for="item in inv.items" :key="item.id" class="text-gray-700">
                                            <td class="py-1.5 pr-2">
                                                <p class="font-medium">{{ item.product_name }}</p>
                                            </td>
                                            <td class="hidden sm:table-cell py-1.5 text-center text-gray-400 font-mono text-[10px]">
                                                {{ item.productVariant?.sku ?? item.variant_sku ?? '—' }}
                                            </td>
                                            <td class="py-1.5 text-right font-medium">{{ item.quantity }}</td>
                                            <td class="py-1.5 text-right">{{ formatVND(item.unit_price) }}</td>
                                            <td class="py-1.5 text-right font-semibold text-gray-900">
                                                {{ formatVND(item.total_price) }}
                                            </td>
                                        </tr>
                                    </tbody>
                                    <!-- Tổng kết -->
                                    <tfoot class="border-t border-purple-200 text-xs">
                                        <tr class="text-gray-500">
                                            <td colspan="3" class="sm:hidden pt-2 pb-0.5 text-right">Tổng tiền hàng:</td>
                                            <td colspan="4" class="hidden sm:table-cell pt-2 pb-0.5 text-right">Tổng tiền hàng:</td>
                                            <td class="pt-2 pb-0.5 text-right font-medium text-gray-700">{{ formatVND(inv.subtotal) }}</td>
                                        </tr>
                                        <tr v-if="inv.discount_amount > 0" class="text-gray-500">
                                            <td colspan="3" class="sm:hidden py-0.5 text-right">Giảm giá:</td>
                                            <td colspan="4" class="hidden sm:table-cell py-0.5 text-right">Giảm giá:</td>
                                            <td class="py-0.5 text-right font-medium text-emerald-600">- {{ formatVND(inv.discount_amount) }}</td>
                                        </tr>
                                        <tr class="text-gray-500">
                                            <td colspan="3" class="sm:hidden py-0.5 text-right">
                                                Thuế VAT<span v-if="inv.subtotal > 0 && inv.tax_amount > 0"> ({{ Math.round(inv.tax_amount / inv.subtotal * 100) }}%)</span>:
                                            </td>
                                            <td colspan="4" class="hidden sm:table-cell py-0.5 text-right">
                                                Thuế VAT<span v-if="inv.subtotal > 0 && inv.tax_amount > 0"> ({{ Math.round(inv.tax_amount / inv.subtotal * 100) }}%)</span>:
                                            </td>
                                            <td class="py-0.5 text-right font-medium text-orange-600">{{ formatVND(inv.tax_amount) }}</td>
                                        </tr>
                                        <tr class="font-semibold text-gray-800 border-t border-purple-100">
                                            <td colspan="3" class="sm:hidden pt-1.5 text-right">Sau thuế:</td>
                                            <td colspan="4" class="hidden sm:table-cell pt-1.5 text-right">Sau thuế:</td>
                                            <td class="pt-1.5 text-right text-purple-700">{{ formatVND(inv.total_amount) }}</td>
                                        </tr>
                                    </tfoot>
                                </table>
                            </div>
                            <div v-else-if="expandedInvoices.has(inv.id)"
                                class="bg-purple-50/40 border-t border-purple-100 px-4 py-3 text-xs text-gray-400 text-center">
                                Không có sản phẩm
                            </div>
                        </div>
                    </div>
                    </div><!-- end v-show imports -->
                </div>

                <!-- Thông tin thanh toán nhập hàng — 1/3 -->
                <div class="lg:col-span-1">
                    <div v-if="purchaseInvoices?.data?.length > 0" class="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
                        <!-- Header -->
                        <div class="flex items-center justify-between px-4 py-3 border-b bg-purple-50">
                            <div class="flex items-center gap-2">
                                <CreditCard :size="16" class="text-purple-600" />
                                <h2 class="font-semibold text-purple-800 text-sm">Thanh toán nhập hàng</h2>
                                <span class="text-xs bg-purple-200 text-purple-700 px-2 py-0.5 rounded-full font-medium">
                                    {{ purchaseInvoices.data.length }} hóa đơn
                                </span>
                            </div>
                        </div>

                        <!-- Summary bar -->
                        <div class="grid grid-cols-3 divide-x divide-gray-100 bg-purple-50/30 border-b border-gray-100">
                            <div class="px-3 py-2 text-center">
                                <p class="text-xs text-gray-400 mb-0.5">Tổng</p>
                                <p class="text-xs font-semibold text-gray-700">{{ formatVND(summary?.total_purchases) }}</p>
                            </div>
                            <div class="px-3 py-2 text-center">
                                <p class="text-xs text-gray-400 mb-0.5">Đã TT</p>
                                <p class="text-xs font-semibold text-emerald-600">
                                    {{ formatVND(purchaseInvoices.data.reduce((s, i) => s + Number(i.paid_amount || 0), 0)) }}
                                </p>
                            </div>
                            <div class="px-3 py-2 text-center">
                                <p class="text-xs text-gray-400 mb-0.5">Còn nợ</p>
                                <p class="text-xs font-semibold text-red-600">
                                    {{ formatVND(purchaseInvoices.data.reduce((s, i) => s + Math.max(0, Number(i.total_amount || 0) - Number(i.paid_amount || 0)), 0)) }}
                                </p>
                            </div>
                        </div>

                        <!-- Danh sách từng hóa đơn -->
                        <div class="divide-y divide-gray-100">
                            <div v-for="inv in purchaseInvoices.data" :key="'pay-inv-' + inv.id"
                                class="transition-colors">
                                <!-- Row chính -->
                                <div class="px-3 py-2.5 flex items-center justify-between gap-2 hover:bg-purple-50/30 cursor-pointer"
                                    @click="toggleInvPayment(inv.id)">
                                    <div class="flex-1 min-w-0">
                                        <div class="flex items-center gap-1.5 mb-0.5 flex-wrap">
                                            <span class="font-mono text-[11px] font-semibold text-purple-600 truncate">
                                                {{ inv.invoice_number }}
                                            </span>
                                            <span :class="['text-[10px] px-1.5 py-0.5 rounded-full font-medium shrink-0',
                                                inv.payment_status === 'paid'    ? 'bg-emerald-100 text-emerald-700' :
                                                inv.payment_status === 'partial' ? 'bg-blue-100 text-blue-700' :
                                                                                   'bg-orange-100 text-orange-700']">
                                                {{ inv.payment_status === 'paid' ? '✓ Đã TT' : inv.payment_status === 'partial' ? '◑ Một phần' : '○ Chưa TT' }}
                                            </span>
                                        </div>
                                        <div class="text-[10px] text-gray-400">
                                            Tổng: <span class="font-medium text-gray-700">{{ formatVND(inv.total_amount) }}</span>
                                        </div>
                                    </div>
                                    <div class="flex items-center gap-1.5 shrink-0">
                                        <div class="text-right">
                                            <p class="text-sm font-bold" :class="(inv.total_amount - inv.paid_amount) > 0 ? 'text-red-600' : 'text-emerald-600'">
                                                {{ formatVND(Math.max(0, inv.total_amount - inv.paid_amount)) }}
                                            </p>
                                            <p class="text-[10px] text-gray-400">còn lại</p>
                                        </div>
                                        <ChevronDown :size="14" :class="['text-gray-400 transition-transform duration-200', expandedInvPayments.has(inv.id) ? 'rotate-0' : '-rotate-90']" />
                                    </div>
                                </div>
                                <!-- Dropdown chi tiết -->
                                <div v-if="expandedInvPayments.has(inv.id)" class="bg-purple-50/40 border-t border-purple-100 px-3 py-2 text-xs space-y-1">
                                    <div class="flex justify-between text-gray-500">
                                        <span>Tiền hàng:</span>
                                        <span class="font-medium text-gray-700">{{ formatVND(inv.subtotal) }}</span>
                                    </div>
                                    <div v-if="inv.tax_amount > 0" class="flex justify-between text-gray-500">
                                        <span>Thuế VAT:</span>
                                        <span class="font-medium text-orange-600">{{ formatVND(inv.tax_amount) }}</span>
                                    </div>
                                    <div v-if="inv.discount_amount > 0" class="flex justify-between text-gray-500">
                                        <span>Giảm giá:</span>
                                        <span class="font-medium text-emerald-600">- {{ formatVND(inv.discount_amount) }}</span>
                                    </div>
                                    <div class="flex justify-between text-gray-500 border-t border-purple-100 pt-1">
                                        <span>Đã thanh toán:</span>
                                        <span class="font-medium text-emerald-600">{{ formatVND(inv.paid_amount) }}</span>
                                    </div>
                                    <div class="flex justify-between font-semibold">
                                        <span>Còn lại:</span>
                                        <span :class="(inv.total_amount - inv.paid_amount) > 0 ? 'text-red-600' : 'text-emerald-600'">
                                            {{ formatVND(Math.max(0, inv.total_amount - inv.paid_amount)) }}
                                        </span>
                                    </div>
                                    <div v-if="inv.invoice_date" class="text-gray-400 pt-0.5">
                                        📅 {{ fmtDate(inv.invoice_date) }}
                                        <span v-if="inv.due_date"> · Hạn: {{ fmtDate(inv.due_date) }}</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Không có nhập hàng -->
                    <div v-else class="bg-white rounded-xl border border-gray-200 shadow-sm p-6 text-center">
                        <FileInput :size="28" class="text-gray-300 mx-auto mb-2" />
                        <p class="text-sm text-gray-400">Chưa có hóa đơn nhập</p>
                    </div>
                </div>
            </div>
        </div>
    </AdminLayout>
</template>
