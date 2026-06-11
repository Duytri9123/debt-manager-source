<script setup>
import { computed, ref } from 'vue'
import { useForm, router } from '@inertiajs/vue3'
import AdminLayout from '@/Layouts/AdminLayout.vue'
import { useCurrency } from '@/composables/useCurrency.js'
import { ArrowLeft, CreditCard, CheckCircle, Phone, Mail, Calendar, FileText, Banknote, Edit2, Trash2, AlertTriangle, X } from 'lucide-vue-next'

const props = defineProps({ debt: Object })

const { formatVND } = useCurrency()

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
const PAYMENT_METHOD_LABELS = {
    cash:          '💵 Tiền mặt',
    bank_transfer: '🏦 Chuyển khoản',
    momo:          '📱 MoMo',
    other:         '💳 Khác',
}

const progressPercent = computed(() => {
    const orig = parseFloat(props.debt.original_amount)
    const paid = parseFloat(props.debt.paid_amount)
    if (!orig) return 0
    return Math.min(100, Math.round((paid / orig) * 100))
})

const isOverdue = computed(() => {
    if (!props.debt.due_date || props.debt.status === 'paid') return false
    return new Date(props.debt.due_date) < new Date()
})

const now = new Date().toISOString().slice(0, 16)
const form = useForm({
    amount:         '',
    payment_method: '',
    notes:          '',
    paid_at:        now,
})

// ── Payment modal ─────────────────────────────────────────────────────────────
const showPaymentModal = ref(false)
const paymentMode = ref('partial') // 'full' | 'partial'
const amountDisplay = ref('')

// Tính remaining từ order.grand_total - paid_amount (tránh stale)
const debtRemaining = computed(() => {
    const grand = Number(props.debt.order?.grand_total ?? props.debt.original_amount ?? 0)
    const paid  = Number(props.debt.paid_amount ?? 0)
    return Math.max(0, grand - paid)
})

function onAmountInput(e) {
    const raw = e.target.value.replace(/\./g, '').replace(/[^0-9]/g, '')
    form.amount = raw ? Number(raw) : ''
    amountDisplay.value = raw ? Number(raw).toLocaleString('vi-VN') : ''
}

function setPaymentMode(mode) {
    paymentMode.value = mode
    if (mode === 'full') {
        form.amount = debtRemaining.value
        amountDisplay.value = debtRemaining.value ? Number(debtRemaining.value).toLocaleString('vi-VN') : ''
    } else {
        form.amount = ''
        amountDisplay.value = ''
    }
}

function openPaymentModal() {
    paymentMode.value = 'partial'
    amountDisplay.value = ''
    form.reset()
    form.payment_method = 'Tiền mặt'
    form.paid_at = new Date().toISOString().slice(0, 16)
    showPaymentModal.value = true
}
function closePaymentModal() {
    showPaymentModal.value = false
    paymentMode.value = 'partial'
    amountDisplay.value = ''
    form.reset()
}

function submitPayment() {
    form.post(`/admin/debts/${props.debt.id}/payments`, {
        onSuccess: () => closePaymentModal(),
    })
}

// ── Edit payment ──────────────────────────────────────────────────────────────
const editingPayment = ref(null)
const editForm = useForm({ amount: '', payment_method: '', notes: '', paid_at: '' })

function openEdit(payment) {
    editingPayment.value = payment
    editForm.amount         = payment.amount
    editForm.payment_method = payment.payment_method ?? ''
    editForm.notes          = payment.notes ?? ''
    editForm.paid_at        = payment.paid_at ? new Date(payment.paid_at).toISOString().slice(0, 16) : now
}

function closeEdit() {
    editingPayment.value = null
    editForm.reset()
}

function submitEdit() {
    editForm.patch(`/admin/debts/${props.debt.id}/payments/${editingPayment.value.id}`, {
        preserveScroll: true,
        onSuccess: () => closeEdit(),
    })
}

function deletePayment(payment) {
    if (!confirm(`Xóa khoản thanh toán ${formatVND(payment.amount)}? Hành động này không thể hoàn tác.`)) return
    router.delete(`/admin/debts/${props.debt.id}/payments/${payment.id}`, { preserveScroll: true })
}

function isItemCategory(item) {
    try {
        const a = typeof item.variant_attributes === 'string'
            ? JSON.parse(item.variant_attributes)
            : (item.variant_attributes ?? {})
        return a?.type === 'category'
    } catch { return false }
}

function itemCategoryTotal(items, idx) {
    let total = 0
    for (let i = idx + 1; i < items.length; i++) {
        if (isItemCategory(items[i])) break
        total += Number(items[i].price ?? 0) * Number(items[i].quantity ?? 0)
    }
    return total
}

function formatDate(date) {
    if (!date) return '—'
    return new Date(date).toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit', year: 'numeric' })
}
function formatDateTime(date) {
    if (!date) return '—'
    return new Date(date).toLocaleString('vi-VN', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}
</script>

<template>
    <AdminLayout>
        <div class="space-y-5">

            <!-- Back -->
            <button @click="router.visit('/admin/debts')"
                class="flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-700 transition-colors">
                <ArrowLeft :size="15" /> Quay lại danh sách
            </button>

            <!-- Header -->
            <div class="flex flex-wrap items-start justify-between gap-3">
                <div>
                    <h1 class="text-xl font-bold text-gray-900">
                        Công nợ — {{ debt.order?.order_number ?? `#${debt.order_id}` }}
                    </h1>
                    <p class="mt-0.5 text-sm text-gray-500">{{ debt.order?.customer_name }}</p>
                </div>
                <div class="flex items-center gap-2">
                    <span v-if="isOverdue"
                        class="inline-flex items-center gap-1 rounded-full bg-red-100 px-2.5 py-1 text-xs font-medium text-red-700 border border-red-200">
                        ⚠️ Quá hạn
                    </span>
                    <span :class="['inline-flex rounded-full px-3 py-1 text-sm font-medium', STATUS_CLASSES[debt.status]]">
                        {{ STATUS_LABELS[debt.status] }}
                    </span>
                </div>
            </div>

            <!-- Summary cards -->
            <div class="grid grid-cols-3 gap-4">
                <div class="rounded-xl border border-gray-200 bg-white p-4 shadow-sm">
                    <p class="text-xs font-medium uppercase tracking-wide text-gray-400">Số tiền gốc</p>
                    <p class="mt-1 text-2xl font-bold text-gray-900">{{ formatVND(debt.original_amount) }}</p>
                </div>
                <div class="rounded-xl border border-emerald-200 bg-emerald-50 p-4 shadow-sm">
                    <p class="text-xs font-medium uppercase tracking-wide text-emerald-600">Đã thanh toán</p>
                    <p class="mt-1 text-2xl font-bold text-emerald-700">{{ formatVND(debt.paid_amount) }}</p>
                </div>
                <div :class="['rounded-xl border p-4 shadow-sm', debt.remaining_amount > 0 ? 'border-red-200 bg-red-50' : 'border-gray-200 bg-gray-50']">
                    <p :class="['text-xs font-medium uppercase tracking-wide', debt.remaining_amount > 0 ? 'text-red-600' : 'text-gray-400']">Còn lại</p>
                    <p :class="['mt-1 text-2xl font-bold', debt.remaining_amount > 0 ? 'text-red-700' : 'text-gray-400']">
                        {{ formatVND(debt.remaining_amount) }}
                    </p>
                </div>
            </div>

            <!-- Progress bar -->
            <div class="rounded-xl border border-gray-200 bg-white px-5 py-4 shadow-sm">
                <div class="flex items-center justify-between mb-2">
                    <span class="text-sm font-medium text-gray-700">Tiến độ thanh toán</span>
                    <span class="text-sm font-bold text-indigo-600">{{ progressPercent }}%</span>
                </div>
                <div class="h-2.5 w-full rounded-full bg-gray-200">
                    <div class="h-2.5 rounded-full transition-all duration-500"
                        :class="progressPercent >= 100 ? 'bg-emerald-500' : 'bg-indigo-600'"
                        :style="{ width: progressPercent + '%' }" />
                </div>
            </div>

            <!-- Main 2-column layout: left = info/form/products, right = payment history -->
            <div class="grid grid-cols-1 gap-5 lg:grid-cols-3">

                <!-- LEFT COLUMN (2/3): Order info + Order items table -->
                <div class="lg:col-span-2 space-y-5">

                    <!-- Order info -->
                    <div class="rounded-xl border border-gray-200 bg-white p-4 shadow-sm space-y-3">
                        <div class="flex items-center justify-between">
                            <h2 class="font-semibold text-gray-900 flex items-center gap-2">
                                <FileText :size="16" class="text-indigo-500" /> Thông tin đơn hàng
                            </h2>
                            <button v-if="debt.status !== 'paid'" @click="openPaymentModal"
                                class="flex items-center gap-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-700 px-3 py-1.5 text-xs font-semibold text-white shadow-sm transition-colors">
                                <Banknote :size="13" /> Tạo thanh toán
                            </button>
                            <span v-else class="inline-flex items-center gap-1 rounded-full bg-emerald-100 px-2.5 py-1 text-xs font-medium text-emerald-700">
                                <CheckCircle :size="12" /> Đã thanh toán đủ
                            </span>
                        </div>
                        <dl class="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-2 text-sm">
                            <!-- Cột trái -->
                            <div class="flex justify-between items-center">
                                <dt class="text-gray-600 shrink-0">Mã đơn:</dt>
                                <dd class="font-mono font-semibold text-indigo-600 text-right">{{ debt.order?.order_number }}</dd>
                            </div>
                            <div v-if="debt.order?.order_name" class="flex justify-between items-center">
                                <dt class="text-gray-600 shrink-0">Tên đơn hàng:</dt>
                                <dd class="font-semibold text-gray-900 text-right">{{ debt.order.order_name }}</dd>
                            </div>

                            <div class="flex justify-between items-center">
                                <dt class="text-gray-600 shrink-0">Khách hàng:</dt>
                                <dd class="font-medium text-gray-900 text-right">{{ debt.order?.customer_name }}</dd>
                            </div>
                            <div v-if="debt.order?.customer?.tax_code" class="flex justify-between items-center">
                                <dt class="text-gray-600 shrink-0">Mã số thuế:</dt>
                                <dd class="text-gray-700 font-mono text-right">{{ debt.order.customer.tax_code }}</dd>
                            </div>

                            <div v-if="debt.order?.customer_phone" class="flex justify-between items-center">
                                <dt class="text-gray-600 flex items-center gap-1 shrink-0"><Phone :size="12" /> SĐT:</dt>
                                <dd class="text-gray-700 text-right">{{ debt.order.customer_phone }}</dd>
                            </div>
                            <div v-if="debt.order?.customer_email" class="flex justify-between items-center">
                                <dt class="text-gray-600 flex items-center gap-1 shrink-0"><Mail :size="12" /> Email:</dt>
                                <dd class="text-gray-700 truncate max-w-[180px] text-right">{{ debt.order.customer_email }}</dd>
                            </div>

                            <div v-if="debt.order?.shipping_address" class="flex justify-between items-center sm:col-span-2">
                                <dt class="text-gray-600 shrink-0">Địa chỉ:</dt>
                                <dd class="text-gray-700 text-right truncate max-w-[70%]">{{ debt.order.shipping_address }}</dd>
                            </div>

                            <div class="flex justify-between items-center">
                                <dt class="text-gray-600 flex items-center gap-1 shrink-0"><Calendar :size="12" /> Ngày tạo đơn:</dt>
                                <dd class="text-gray-700 text-right">{{ formatDate(debt.order?.created_at) }}</dd>
                            </div>
                            <div v-if="debt.order?.delivery_date" class="flex justify-between items-center">
                                <dt class="text-gray-600 flex items-center gap-1 shrink-0"><Calendar :size="12" /> Ngày xuất:</dt>
                                <dd class="text-gray-700 text-right">{{ formatDate(debt.order.delivery_date) }}</dd>
                            </div>

                            <div class="flex justify-between items-center">
                                <dt class="text-gray-600 shrink-0">Tổng đơn hàng:</dt>
                                <dd class="font-semibold text-gray-900 text-right">{{ formatVND(debt.order?.grand_total) }}</dd>
                            </div>
                            <div class="flex justify-between items-center">
                                <dt class="text-gray-600 shrink-0">Trạng thái đơn:</dt>
                                <dd class="text-right">
                                    <span :class="[
                                        'inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium',
                                        debt.order?.status === 'delivered'  ? 'bg-emerald-100 text-emerald-700' :
                                        debt.order?.status === 'shipped'    ? 'bg-indigo-100 text-indigo-700' :
                                        debt.order?.status === 'processing' ? 'bg-blue-100 text-blue-700' :
                                        debt.order?.status === 'cancelled'  ? 'bg-red-100 text-red-700' :
                                                                              'bg-yellow-100 text-yellow-700'
                                    ]">
                                        {{
                                            debt.order?.status === 'delivered'  ? '✅ Đã giao' :
                                            debt.order?.status === 'shipped'    ? '🚚 Đang giao' :
                                            debt.order?.status === 'processing' ? '🔄 Đang xử lý' :
                                            debt.order?.status === 'cancelled'  ? '❌ Đã hủy' : '⏳ Chờ xử lý'
                                        }}
                                    </span>
                                </dd>
                            </div>
                        </dl>
                        <div v-if="debt.notes" class="rounded-lg bg-amber-50 border border-amber-200 p-3 text-sm text-amber-800">
                            <p class="font-medium mb-0.5">📝 Ghi chú:</p>
                            {{ debt.notes }}
                        </div>
                    </div>

                    <!-- Order items table (giống B2BOrders/Show) -->
                    <div class="rounded-xl border border-gray-200 bg-white shadow-sm overflow-hidden">
                        <div class="px-4 py-3 border-b border-gray-100 bg-gray-50 flex items-center justify-between">
                            <h2 class="font-semibold text-gray-800 text-sm">Chi tiết sản phẩm</h2>
                            <span class="text-xs text-gray-400">{{ debt.order?.items?.filter(i => !isItemCategory(i)).length ?? 0 }} dòng</span>
                        </div>
                        <div v-if="!debt.order?.items?.length" class="text-center py-10 text-gray-400 text-sm">
                            Không có sản phẩm nào
                        </div>
                        <div v-else class="overflow-x-auto">
                            <table class="w-full text-xs border-collapse">
                                <thead class="bg-yellow-50 border-b-2 border-yellow-300">
                                    <tr>
                                        <th class="px-2 py-2 text-center font-semibold text-gray-700 border border-yellow-200 w-8">TT</th>
                                        <th class="px-2 py-2 text-left font-semibold text-gray-700 border border-yellow-200">Mô tả chi tiết</th>
                                        <th class="px-2 py-2 text-left font-semibold text-gray-700 border border-yellow-200 w-28">Mã hàng</th>
                                        <th class="px-2 py-2 text-center font-semibold text-gray-700 border border-yellow-200 w-10">SL</th>
                                        <th class="px-2 py-2 text-right font-semibold text-gray-700 border border-yellow-200 w-24">Đơn giá</th>
                                        <th class="px-2 py-2 text-right font-semibold text-gray-700 border border-yellow-200 w-24">Thành tiền</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <template v-for="(item, idx) in debt.order.items" :key="item.id">
                                        <!-- Category row -->
                                        <tr v-if="isItemCategory(item)" class="bg-amber-50 border-l-4 border-amber-400">
                                            <td class="px-2 py-2 text-center text-amber-400 border border-amber-200">📁</td>
                                            <td colspan="4" class="px-2 py-2 border border-amber-200">
                                                <span class="font-bold text-amber-800">{{ item.product_name }}</span>
                                            </td>
                                            <td class="px-2 py-2 text-right font-bold text-amber-700 border border-amber-200">
                                                {{ formatVND(itemCategoryTotal(debt.order.items, idx)) }}
                                            </td>
                                        </tr>
                                        <!-- Item row -->
                                        <tr v-else :class="idx % 2 === 0 ? 'bg-white' : 'bg-gray-50/50'">
                                            <td class="px-2 py-2 text-center text-gray-400 border border-gray-200">{{ idx + 1 }}</td>
                                            <td class="px-2 py-2 border border-gray-200">
                                                <div class="font-medium text-gray-800 whitespace-pre-wrap leading-relaxed">{{ item.product_name }}</div>
                                                <div v-if="item.origin" class="text-gray-400 text-[10px]">{{ item.origin }}</div>
                                            </td>
                                            <td class="px-2 py-2 text-gray-500 font-mono border border-gray-200">{{ item.variant_sku || '—' }}</td>
                                            <td class="px-2 py-2 text-center text-gray-700 font-medium border border-gray-200">{{ item.quantity }}</td>
                                            <td class="px-2 py-2 text-right text-gray-700 border border-gray-200">{{ formatVND(item.price) }}</td>
                                            <td class="px-2 py-2 text-right font-semibold text-gray-900 border border-gray-200">
                                                {{ formatVND(Number(item.price) * Number(item.quantity)) }}
                                            </td>
                                        </tr>
                                    </template>
                                </tbody>
                                <tfoot class="border-t-2 border-gray-300 bg-gray-50">
                                    <tr>
                                        <td colspan="5" class="px-3 py-2 text-right text-gray-500 text-xs border border-gray-200">Tổng tiền hàng:</td>
                                        <td class="px-3 py-2 text-right font-medium text-gray-700 text-xs border border-gray-200">
                                            {{ formatVND(debt.order?.subtotal) }}
                                        </td>
                                    </tr>
                                    <tr>
                                        <td colspan="5" class="px-3 py-1.5 text-right text-gray-400 text-xs border border-gray-200">
                                            Thuế VAT
                                            <span v-if="debt.order?.subtotal > 0 && (debt.order?.grand_total - debt.order?.subtotal) > 0">
                                                ({{ Math.round((debt.order.grand_total - debt.order.subtotal) / debt.order.subtotal * 100) }}%)
                                            </span>:
                                        </td>
                                        <td class="px-3 py-1.5 text-right text-orange-600 text-xs border border-gray-200">
                                            {{ formatVND(Math.max(0, (debt.order?.grand_total ?? 0) - (debt.order?.subtotal ?? 0))) }}
                                        </td>
                                    </tr>
                                    <tr class="bg-indigo-50">
                                        <td colspan="5" class="px-3 py-2 text-right font-bold text-indigo-700 text-xs border border-indigo-200">Sau thuế:</td>
                                        <td class="px-3 py-2 text-right font-bold text-indigo-700 text-sm border border-indigo-200">
                                            {{ formatVND(debt.order?.grand_total) }}
                                        </td>
                                    </tr>
                                </tfoot>
                            </table>
                        </div>
                    </div>

                </div>

                <!-- RIGHT COLUMN (1/3): Payment history -->
                <div class="lg:col-span-1">
                    <div class="sticky top-4 rounded-xl border border-gray-200 bg-white shadow-sm overflow-hidden">
                        <div class="px-5 py-3.5 border-b border-gray-100 flex items-center justify-between bg-gray-50">
                            <h2 class="font-semibold text-gray-900">Thông tin thanh toán</h2>
                            <span class="text-xs text-gray-400 bg-white border border-gray-200 rounded-full px-2 py-0.5">
                                {{ debt.payments?.length ?? 0 }} lần
                            </span>
                        </div>
                        <div v-if="!debt.payments?.length" class="px-5 py-8 text-center text-sm text-gray-400">
                            Chưa có thanh toán nào
                        </div>
                        <div v-else class="divide-y divide-gray-100 max-h-[70vh] overflow-y-auto">
                            <div v-for="(payment, idx) in debt.payments" :key="payment.id"
                                class="px-4 py-3 hover:bg-gray-50 transition-colors">
                                <div class="flex items-start gap-3">
                                    <div class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-emerald-100 text-emerald-600 font-bold text-xs">
                                        {{ idx + 1 }}
                                    </div>
                                    <div class="flex-1 min-w-0">
                                        <div class="flex items-center justify-between gap-2">
                                            <span class="text-base font-bold text-emerald-700">{{ formatVND(payment.amount) }}</span>
                                            <span class="text-xs text-gray-400 shrink-0">{{ formatDateTime(payment.paid_at) }}</span>
                                        </div>
                                        <div class="mt-1 flex flex-wrap gap-1.5 text-xs">
                                            <span v-if="payment.payment_method"
                                                class="inline-flex items-center rounded-full bg-gray-100 px-2 py-0.5 text-gray-600">
                                                {{ PAYMENT_METHOD_LABELS[payment.payment_method] ?? payment.payment_method }}
                                            </span>
                                            <span v-if="payment.notes" class="text-gray-400 italic truncate max-w-[140px]">{{ payment.notes }}</span>
                                        </div>
                                    </div>
                                    <!-- Actions -->
                                    <div class="flex items-center gap-1 shrink-0">
                                        <button @click="openEdit(payment)"
                                            class="p-1.5 rounded-lg text-gray-400 hover:text-indigo-600 hover:bg-indigo-50 transition-colors"
                                            title="Chỉnh sửa">
                                            <Edit2 :size="13" />
                                        </button>
                                        <button @click="deletePayment(payment)"
                                            class="p-1.5 rounded-lg text-gray-400 hover:text-red-600 hover:bg-red-50 transition-colors"
                                            title="Xóa">
                                            <Trash2 :size="13" />
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

            </div>

        </div>

        <!-- Edit Payment Modal -->
        <Teleport to="body">
            <!-- New Payment Modal -->
            <div v-if="showPaymentModal"
                class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm"
                @click.self="closePaymentModal">
                <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md">
                    <!-- Header -->
                    <div class="flex items-center justify-between px-5 py-4 border-b border-gray-100">
                        <div class="flex items-center gap-2">
                            <CreditCard :size="16" class="text-emerald-600" />
                            <h2 class="font-semibold text-gray-900">Tạo thanh toán</h2>
                        </div>
                        <button @click="closePaymentModal" class="p-1 rounded-lg hover:bg-gray-100 transition-colors">
                            <X :size="18" class="text-gray-500" />
                        </button>
                    </div>
                    <!-- Summary -->
                    <div class="grid grid-cols-2 gap-2 px-5 pt-4 text-xs">
                        <div class="bg-gray-50 rounded-lg p-2.5">
                            <p class="text-gray-400 mb-0.5">Tổng đơn</p>
                            <p class="font-bold text-gray-900">{{ formatVND(debt.order?.grand_total) }}</p>
                        </div>
                        <div :class="['rounded-lg p-2.5', debtRemaining > 0 ? 'bg-red-50' : 'bg-emerald-50']">
                            <p class="text-gray-400 mb-0.5">Còn lại</p>
                            <p :class="['font-bold', debtRemaining > 0 ? 'text-red-600' : 'text-emerald-600']">
                                {{ formatVND(debtRemaining) }}
                            </p>
                        </div>
                    </div>
                    <div class="p-5 space-y-4">
                        <!-- Radio mode -->
                        <div class="flex gap-2">
                            <button type="button" @click="setPaymentMode('full')"
                                :class="[
                                    'flex-1 flex items-center gap-2 rounded-lg border px-3 py-2.5 text-xs font-medium transition-colors',
                                    paymentMode === 'full'
                                        ? 'border-emerald-500 bg-emerald-50 text-emerald-700'
                                        : 'border-gray-200 bg-white text-gray-600 hover:border-gray-300 hover:bg-gray-50'
                                ]">
                                <span :class="['flex h-4 w-4 shrink-0 items-center justify-center rounded-full border-2 transition-colors',
                                    paymentMode === 'full' ? 'border-emerald-500' : 'border-gray-300']">
                                    <span v-if="paymentMode === 'full'" class="h-2 w-2 rounded-full bg-emerald-500" />
                                </span>
                                Thanh toán tất cả
                            </button>
                            <button type="button" @click="setPaymentMode('partial')"
                                :class="[
                                    'flex-1 flex items-center gap-2 rounded-lg border px-3 py-2.5 text-xs font-medium transition-colors',
                                    paymentMode === 'partial'
                                        ? 'border-indigo-500 bg-indigo-50 text-indigo-700'
                                        : 'border-gray-200 bg-white text-gray-600 hover:border-gray-300 hover:bg-gray-50'
                                ]">
                                <span :class="['flex h-4 w-4 shrink-0 items-center justify-center rounded-full border-2 transition-colors',
                                    paymentMode === 'partial' ? 'border-indigo-500' : 'border-gray-300']">
                                    <span v-if="paymentMode === 'partial'" class="h-2 w-2 rounded-full bg-indigo-500" />
                                </span>
                                Từng phần
                            </button>
                        </div>
                        <!-- Amount -->
                        <div>
                            <label class="block text-xs font-medium text-gray-700 mb-1">Số tiền thanh toán *</label>
                            <input
                                :value="amountDisplay"
                                @input="onAmountInput"
                                type="text" inputmode="numeric"
                                :placeholder="`Tối đa ${formatVND(debtRemaining)}`"
                                :disabled="paymentMode === 'full'"
                                :class="[
                                    'w-full rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500',
                                    paymentMode === 'full' ? 'border-gray-200 bg-gray-50 text-gray-500 cursor-not-allowed' : 'border-gray-300'
                                ]" />
                            <p v-if="form.errors.amount" class="text-xs text-red-500 mt-1">{{ form.errors.amount }}</p>
                        </div>
                        <!-- Method -->
                        <div>
                            <label class="block text-xs font-medium text-gray-700 mb-1">Phương thức</label>
                            <select v-model="form.payment_method"
                                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500">
                                <option>Tiền mặt</option>
                                <option>Chuyển khoản</option>
                                <option>Thẻ ngân hàng</option>
                                <option>Khác</option>
                            </select>
                        </div>
                        <!-- Date -->
                        <div>
                            <label class="block text-xs font-medium text-gray-700 mb-1">Thời gian thanh toán</label>
                            <input v-model="form.paid_at" type="datetime-local"
                                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500" />
                        </div>
                        <!-- Notes -->
                        <div>
                            <label class="block text-xs font-medium text-gray-700 mb-1">Ghi chú</label>
                            <input v-model="form.notes" type="text" placeholder="Tuỳ chọn..."
                                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500" />
                        </div>
                    </div>
                    <div class="flex gap-2 px-5 pb-5">
                        <button @click="closePaymentModal"
                            class="flex-1 rounded-lg border border-gray-300 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors">
                            Hủy
                        </button>
                        <button @click="submitPayment" :disabled="form.processing || !form.amount"
                            class="flex-1 rounded-lg bg-emerald-600 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-700 disabled:opacity-60 transition-colors">
                            {{ form.processing ? 'Đang lưu...' : 'Xác nhận thanh toán' }}
                        </button>
                    </div>
                </div>
            </div>

            <!-- Edit Payment Modal -->
            <div v-if="editingPayment"
                class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm"
                @click.self="closeEdit">
                <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md">
                    <!-- Header -->
                    <div class="flex items-center justify-between px-5 py-4 border-b border-gray-100">
                        <div class="flex items-center gap-2">
                            <Edit2 :size="16" class="text-indigo-600" />
                            <h2 class="font-semibold text-gray-900">Chỉnh sửa thanh toán</h2>
                        </div>
                        <button @click="closeEdit" class="p-1 rounded-lg hover:bg-gray-100 transition-colors">
                            <X :size="18" class="text-gray-500" />
                        </button>
                    </div>
                    <!-- Warning -->
                    <div class="mx-5 mt-4 flex items-start gap-2 rounded-lg bg-amber-50 border border-amber-200 px-3 py-2.5 text-xs text-amber-800">
                        <AlertTriangle :size="14" class="shrink-0 mt-0.5 text-amber-500" />
                        <span>Chỉnh sửa thanh toán sẽ tự động tính lại số dư công nợ. Hãy kiểm tra kỹ trước khi lưu.</span>
                    </div>
                    <!-- Body -->
                    <div class="p-5 space-y-4">
                        <div>
                            <label class="block text-xs font-medium text-gray-700 mb-1">Số tiền *</label>
                            <input v-model="editForm.amount" type="number" min="0.01" step="1000" required
                                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                            <p v-if="editForm.errors.amount" class="text-xs text-red-500 mt-1">{{ editForm.errors.amount }}</p>
                        </div>
                        <div>
                            <label class="block text-xs font-medium text-gray-700 mb-1">Phương thức</label>
                            <select v-model="editForm.payment_method"
                                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                                <option value="">Chọn phương thức</option>
                                <option value="cash">💵 Tiền mặt</option>
                                <option value="bank_transfer">🏦 Chuyển khoản</option>
                                <option value="momo">📱 MoMo</option>
                                <option value="other">💳 Khác</option>
                            </select>
                        </div>
                        <div>
                            <label class="block text-xs font-medium text-gray-700 mb-1">Ngày thanh toán</label>
                            <input v-model="editForm.paid_at" type="datetime-local"
                                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                        </div>
                        <div>
                            <label class="block text-xs font-medium text-gray-700 mb-1">Ghi chú</label>
                            <input v-model="editForm.notes" type="text" placeholder="Tuỳ chọn..."
                                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                        </div>
                    </div>
                    <!-- Footer -->
                    <div class="flex gap-2 px-5 pb-5">
                        <button @click="closeEdit"
                            class="flex-1 rounded-lg border border-gray-300 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors">
                            Hủy
                        </button>
                        <button @click="submitEdit" :disabled="editForm.processing"
                            class="flex-1 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-700 disabled:opacity-60 transition-colors">
                            {{ editForm.processing ? 'Đang lưu...' : 'Lưu thay đổi' }}
                        </button>
                    </div>
                </div>
            </div>
        </Teleport>
    </AdminLayout>
</template>
