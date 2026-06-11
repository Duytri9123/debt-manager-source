<script setup>
import { computed } from 'vue'
import { useForm, router } from '@inertiajs/vue3'
import AdminLayout from '@/Layouts/AdminLayout.vue'
import { useCurrency } from '@/composables/useCurrency.js'
import { ArrowLeft, CreditCard, CheckCircle, Phone, Mail, Calendar, FileText, Banknote } from 'lucide-vue-next'

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

function submitPayment() {
    form.post(`/admin/debts/${props.debt.id}/payments`, {
        onSuccess: () => form.reset(),
    })
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
        <div class="space-y-5 max-w-5xl">

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

            <div class="grid grid-cols-1 gap-5 lg:grid-cols-2">

                <!-- Order info -->
                <div class="rounded-xl border border-gray-200 bg-white p-5 shadow-sm space-y-4">
                    <h2 class="font-semibold text-gray-900 flex items-center gap-2">
                        <FileText :size="16" class="text-indigo-500" /> Thông tin đơn hàng
                    </h2>
                    <dl class="space-y-2.5 text-sm">
                        <div class="flex justify-between items-center">
                            <dt class="text-gray-500">Mã đơn</dt>
                            <dd class="font-mono font-semibold text-indigo-600">{{ debt.order?.order_number }}</dd>
                        </div>
                        <div class="flex justify-between items-center">
                            <dt class="text-gray-500">Khách hàng</dt>
                            <dd class="font-medium text-gray-900">{{ debt.order?.customer_name }}</dd>
                        </div>
                        <div v-if="debt.order?.customer_phone" class="flex justify-between items-center">
                            <dt class="text-gray-500 flex items-center gap-1"><Phone :size="12" /> SĐT</dt>
                            <dd class="text-gray-700">{{ debt.order.customer_phone }}</dd>
                        </div>
                        <div v-if="debt.order?.customer_email" class="flex justify-between items-center">
                            <dt class="text-gray-500 flex items-center gap-1"><Mail :size="12" /> Email</dt>
                            <dd class="text-gray-700">{{ debt.order.customer_email }}</dd>
                        </div>
                        <div class="flex justify-between items-center">
                            <dt class="text-gray-500">Tổng đơn hàng</dt>
                            <dd class="font-semibold text-gray-900">{{ formatVND(debt.order?.grand_total) }}</dd>
                        </div>
                        <div class="flex justify-between items-center">
                            <dt class="text-gray-500 flex items-center gap-1"><Calendar :size="12" /> Ngày đến hạn</dt>
                            <dd :class="['font-medium', isOverdue ? 'text-red-600' : 'text-gray-700']">
                                {{ formatDate(debt.due_date) }}
                                <span v-if="isOverdue" class="ml-1 text-xs">(Quá hạn)</span>
                            </dd>
                        </div>
                    </dl>
                    <div v-if="debt.notes" class="rounded-lg bg-amber-50 border border-amber-200 p-3 text-sm text-amber-800">
                        <p class="font-medium mb-0.5">📝 Ghi chú:</p>
                        {{ debt.notes }}
                    </div>
                </div>

                <!-- Payment form / Paid notice -->
                <div v-if="debt.status !== 'paid'" class="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
                    <h2 class="font-semibold text-gray-900 mb-4 flex items-center gap-2">
                        <Banknote :size="16" class="text-emerald-500" /> Ghi nhận thanh toán
                    </h2>
                    <form @submit.prevent="submitPayment" class="space-y-3">
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">
                                Số tiền <span class="text-red-500">*</span>
                                <span class="text-xs text-gray-400 ml-1">(tối đa {{ formatVND(debt.remaining_amount) }})</span>
                            </label>
                            <input v-model="form.amount" type="number" step="1000"
                                :max="debt.remaining_amount" min="0.01" required
                                placeholder="0"
                                :class="['w-full rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500',
                                    form.errors.amount ? 'border-red-300' : 'border-gray-300']" />
                            <p v-if="form.errors.amount" class="mt-1 text-xs text-red-600">{{ form.errors.amount }}</p>
                            <p v-if="form.amount" class="mt-1 text-xs text-gray-400">= {{ formatVND(form.amount) }}</p>
                        </div>

                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">Phương thức</label>
                            <select v-model="form.payment_method"
                                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                                <option value="">Chọn phương thức</option>
                                <option value="cash">💵 Tiền mặt</option>
                                <option value="bank_transfer">🏦 Chuyển khoản</option>
                                <option value="momo">📱 MoMo</option>
                                <option value="other">💳 Khác</option>
                            </select>
                        </div>

                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">Ngày thanh toán</label>
                            <input v-model="form.paid_at" type="datetime-local"
                                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                        </div>

                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">Ghi chú</label>
                            <textarea v-model="form.notes" rows="2"
                                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none"
                                placeholder="Ghi chú thêm..." />
                        </div>

                        <button type="submit" :disabled="form.processing"
                            class="w-full rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-indigo-700 disabled:opacity-60 transition-colors">
                            {{ form.processing ? 'Đang xử lý...' : '✓ Ghi nhận thanh toán' }}
                        </button>
                    </form>
                </div>

                <div v-else class="rounded-xl border border-emerald-200 bg-emerald-50 p-5 shadow-sm flex items-center gap-3">
                    <CheckCircle :size="28" class="text-emerald-500 shrink-0" />
                    <div>
                        <p class="font-semibold text-emerald-800">Đã thanh toán đủ ✅</p>
                        <p class="text-sm text-emerald-600 mt-0.5">Công nợ này đã được thanh toán hoàn toàn.</p>
                    </div>
                </div>
            </div>

            <!-- Order items -->
            <div class="rounded-xl border border-gray-200 bg-white shadow-sm overflow-hidden">
                <div class="px-5 py-3.5 border-b border-gray-100 flex items-center justify-between bg-gray-50">
                    <h2 class="font-semibold text-gray-900">Sản phẩm đặt hàng</h2>
                    <span class="text-xs text-gray-400 bg-white border border-gray-200 rounded-full px-2 py-0.5">
                        {{ debt.order?.items?.length ?? 0 }} sản phẩm
                    </span>
                </div>
                <div v-if="!debt.order?.items?.length" class="px-5 py-8 text-center text-sm text-gray-400">
                    Không có sản phẩm nào
                </div>
                <div v-else>
                    <div v-for="item in debt.order.items" :key="item.id"
                        class="flex items-center gap-4 px-5 py-3 border-b border-gray-50 last:border-0 hover:bg-gray-50 transition-colors">
                        <div class="flex-1 min-w-0">
                            <p class="font-medium text-gray-800 truncate">{{ item.product_name }}</p>
                            <p class="text-xs text-gray-400 mt-0.5">{{ item.variant_sku }}</p>
                        </div>
                        <div class="text-right shrink-0">
                            <p class="font-semibold text-gray-800">{{ formatVND(item.price) }}</p>
                            <p class="text-xs text-gray-400">x{{ item.quantity ?? 1 }}</p>
                        </div>
                        <div class="text-right shrink-0 w-28">
                            <p class="font-semibold text-indigo-600">{{ formatVND((item.price || 0) * (item.quantity || 1)) }}</p>
                        </div>
                    </div>
                    <!-- Total row -->
                    <div class="flex justify-between items-center px-5 py-3 bg-gray-50 border-t border-gray-200">
                        <span class="text-sm font-semibold text-gray-700">Tổng cộng</span>
                        <span class="font-bold text-gray-900">{{ formatVND(debt.order?.grand_total) }}</span>
                    </div>
                </div>
            </div>

            <!-- Payment history -->
            <div class="rounded-xl border border-gray-200 bg-white shadow-sm overflow-hidden">
                <div class="px-5 py-3.5 border-b border-gray-100 flex items-center justify-between bg-gray-50">
                    <h2 class="font-semibold text-gray-900">Lịch sử thanh toán</h2>
                    <span class="text-xs text-gray-400 bg-white border border-gray-200 rounded-full px-2 py-0.5">
                        {{ debt.payments?.length ?? 0 }} lần
                    </span>
                </div>
                <div v-if="!debt.payments?.length" class="px-5 py-8 text-center text-sm text-gray-400">
                    Chưa có thanh toán nào
                </div>
                <div v-else class="divide-y divide-gray-100">
                    <div v-for="(payment, idx) in debt.payments" :key="payment.id"
                        class="flex items-start gap-4 px-5 py-4 hover:bg-gray-50 transition-colors">
                        <div class="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-emerald-100 text-emerald-600 font-bold text-sm">
                            {{ idx + 1 }}
                        </div>
                        <div class="flex-1 min-w-0">
                            <div class="flex items-center justify-between gap-2 flex-wrap">
                                <span class="text-base font-bold text-emerald-700">{{ formatVND(payment.amount) }}</span>
                                <span class="text-xs text-gray-400">{{ formatDateTime(payment.paid_at) }}</span>
                            </div>
                            <div class="mt-1 flex flex-wrap gap-2 text-xs">
                                <span v-if="payment.payment_method"
                                    class="inline-flex items-center rounded-full bg-gray-100 px-2 py-0.5 text-gray-600">
                                    {{ PAYMENT_METHOD_LABELS[payment.payment_method] ?? payment.payment_method }}
                                </span>
                                <span v-if="payment.notes" class="text-gray-400 italic">{{ payment.notes }}</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

        </div>
    </AdminLayout>
</template>
