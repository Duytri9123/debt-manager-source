<script setup>
import AdminLayout from '@/Layouts/AdminLayout.vue'
import { router, Link, useForm } from '@inertiajs/vue3'
import { computed, ref } from 'vue'
import { ArrowLeft, Edit2, Trash2, RefreshCw, CreditCard, ChevronRight, ChevronDown, Plus, X, Download } from 'lucide-vue-next'
import { jsPDF } from 'jspdf'
import autoTable from 'jspdf-autotable'

const props = defineProps({ 
    order:   Object,
    taxRate: { type: Number, default: 10 },
})

const statusForm = useForm({
    status: props.order.status ?? 'delivered',
})

function updateStatus() {
    statusForm.patch(`/admin/b2b-orders/${props.order.id}/status`, {
        preserveScroll: true,
    })
}

const items = computed(() => props.order.items ?? [])

const totalBeforeTax = computed(() => {
    if (props.order.total_before_tax > 0) return Number(props.order.total_before_tax)
    if (props.order.subtotal > 0) return Number(props.order.subtotal)
    return items.value.reduce((s, i) => s + Number(i.price) * Number(i.quantity), 0)
})

const tax = computed(() => {
    if (props.order.tax_amount > 0) return Number(props.order.tax_amount)
    const grand = Number(props.order.grand_total) || 0
    const before = totalBeforeTax.value
    if (grand > before && before > 0) return grand - before
    return Math.round(before * props.taxRate / 100)
})

const taxRate = computed(() => {
    const before = totalBeforeTax.value
    const t = tax.value
    if (before > 0 && t > 0) return Math.round(t / before * 100)
    return props.taxRate
})
const grandTotal = computed(() => Number(props.order.grand_total) || (totalBeforeTax.value + tax.value))

// ── Debt / Payment ────────────────────────────────────────────────────────────
const debt = computed(() => props.order.debts?.[0] ?? null)
const payments = computed(() => debt.value?.payments ?? [])
const totalPaid = computed(() => {
    if (debt.value) return Number(debt.value.paid_amount ?? 0)
    return props.order.payment_status === 'paid' ? grandTotal.value : 0
})
const remaining = computed(() => {
    // Tính trực tiếp từ grandTotal - totalPaid, không tin vào DB có thể stale
    const r = grandTotal.value - totalPaid.value
    return r > 0 ? r : 0
})

// Badge trạng thái TT — tính từ remaining thực tế
const paymentStatus = computed(() => {
    const paid = totalPaid.value
    const rem  = remaining.value
    if (paid <= 0)  return 'unpaid'
    if (rem <= 0)   return 'paid'
    return 'partial'
})

const ORDER_STATUS = {
    pending:    { label: 'Chờ xử lý',  cls: 'bg-yellow-100 text-yellow-700' },
    processing: { label: 'Đang xử lý', cls: 'bg-blue-100 text-blue-700' },
    shipped:    { label: 'Đang giao',  cls: 'bg-indigo-100 text-indigo-700' },
    delivered:  { label: 'Đã giao',   cls: 'bg-emerald-100 text-emerald-700' },
    cancelled:  { label: 'Đã hủy',    cls: 'bg-red-100 text-red-700' },
}

function getNote(item) {
    if (!item.variant_attributes) return ''
    try {
        const a = typeof item.variant_attributes === 'string'
            ? JSON.parse(item.variant_attributes)
            : item.variant_attributes
        return a?.note ?? ''
    } catch { return '' }
}

function isCategory(item) {
    try {
        const a = typeof item.variant_attributes === 'string'
            ? JSON.parse(item.variant_attributes)
            : (item.variant_attributes ?? {})
        return a?.type === 'category'
    } catch { return false }
}

function categoryTotalShow(idx) {
    let total = 0
    for (let i = idx + 1; i < items.value.length; i++) {
        if (isCategory(items.value[i])) break
        total += Number(items.value[i].price) * Number(items.value[i].quantity)
    }
    return total
}

function itemSeqNumber(idx) {
    let num = 0
    for (let i = 0; i <= idx; i++) {
        if (isCategory(items.value[i])) num = 0
        else num++
    }
    return num
}

// ── Payment modal ─────────────────────────────────────────────────────────────
const showPaymentModal = ref(false)
const paymentForm = useForm({
    amount:         '',
    payment_method: 'Tiền mặt',
    notes:          '',
    paid_at:        new Date().toISOString().slice(0, 16),
})

const paymentMode = ref('partial') // 'full' | 'partial'

// Format tiền trong input: lưu số thực, hiển thị có dấu chấm
const amountDisplay = ref('')

function onAmountInput(e) {
    const raw = e.target.value.replace(/\./g, '').replace(/[^0-9]/g, '')
    paymentForm.amount = raw ? Number(raw) : ''
    amountDisplay.value = raw ? Number(raw).toLocaleString('vi-VN') : ''
}

function setPaymentMode(mode) {
    paymentMode.value = mode
    if (mode === 'full') {
        paymentForm.amount = remaining.value
        amountDisplay.value = remaining.value ? Number(remaining.value).toLocaleString('vi-VN') : ''
    } else {
        paymentForm.amount = ''
        amountDisplay.value = ''
    }
}

function submitPayment() {
    paymentForm.post(`/admin/b2b-orders/${props.order.id}/payments`, {
        preserveScroll: true,
        onSuccess: () => {
            showPaymentModal.value = false
            paymentMode.value = 'partial'
            amountDisplay.value = ''
            paymentForm.reset()
        },
    })
}

function fmt(v)    { return Number(v || 0).toLocaleString('vi-VN') + 'đ' }
function fmtVND(v) { return Number(v || 0).toLocaleString('vi-VN') + 'đ' }
function fmtDate(d) {
    if (!d) return '—'
    return new Date(d).toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit', year: 'numeric' })
}
function fmtDateTime(d) {
    if (!d) return '—'
    return new Date(d).toLocaleString('vi-VN', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}

const paymentSectionOpen = ref(true)

const showExportMenu = ref(false)

function exportOrder(format) {
    showExportMenu.value = false
    if (format === 'pdf') {
        exportPdf()
        return
    }
    // Excel: window.location → browser nhận Content-Disposition: attachment → tải file
    window.location.href = `/admin/b2b-orders/${props.order.id}/export?format=xlsx`
}

function exportPdf() {
    const order = props.order
    const allItems = order.items ?? []

    const subtotal = Number(order.subtotal ?? 0)
    const tax      = Math.max(0, Number(order.grand_total ?? 0) - subtotal)
    const grand    = Number(order.grand_total ?? 0)
    const taxRate  = subtotal > 0 ? Math.round(tax / subtotal * 100) : 0
    const year     = order.created_at ? new Date(order.created_at).getFullYear() : new Date().getFullYear()
    const title    = (order.order_name || order.order_number || '').toUpperCase()

    const fmtNum  = v => Number(v || 0).toLocaleString('vi-VN')
    const fmtDate = d => d ? new Date(d).toLocaleDateString('vi-VN') : '—'
    const getAttrs = item => { try { return typeof item.variant_attributes === 'string' ? JSON.parse(item.variant_attributes) : (item.variant_attributes ?? {}) } catch { return {} } }
    const isCategory = item => (getAttrs(item)?.type ?? '') === 'category'

    // Build rows HTML
    let rowsHtml = ''
    allItems.forEach(item => {
        const attrs = getAttrs(item)
        const note  = attrs.note ?? ''
        if (isCategory(item)) {
            rowsHtml += `<tr class="cat-row">
                <td class="center">${year}</td>
                <td></td>
                <td colspan="7" class="cat-name">${item.product_name.toUpperCase()}</td>
            </tr>`
        } else {
            const lineTotal = item.line_total ?? (item.price * item.quantity)
            const noteStyle = note ? 'color:#dc2626;font-weight:bold' : ''
            rowsHtml += `<tr>
                <td class="center">${year}</td>
                <td class="center">+</td>
                <td>${item.product_name}${note ? `<br><span style="color:#dc2626;font-size:8pt">${note}</span>` : ''}</td>
                <td class="center">${item.variant_sku ?? ''}</td>
                <td class="center">${item.origin ?? ''}</td>
                <td class="center">${item.unit ?? ''}</td>
                <td class="center">${item.quantity}</td>
                <td class="right" style="${noteStyle}">${fmtNum(item.price)}</td>
                <td class="right" style="${noteStyle}">${fmtNum(lineTotal)}</td>
            </tr>`
        }
    })

    const html = `<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<title>Don hang ${order.order_number}</title>
<style>
  @page { size: A4 landscape; margin: 12mm 10mm; }
  * { box-sizing: border-box; }
  body { font-family: 'Times New Roman', Times, serif; font-size: 10pt; color: #000; margin: 0; }
  h1 { font-size: 15pt; font-weight: bold; text-align: center; color: #1F3864; margin: 0 0 4px; letter-spacing: 1px; }
  .sub { text-align: center; color: #666; font-size: 9pt; margin-bottom: 10px; }
  .info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 2px 20px; margin-bottom: 10px; font-size: 9.5pt; }
  .info-row { display: flex; gap: 6px; }
  .lbl { font-weight: bold; min-width: 80px; }
  table { width: 100%; border-collapse: collapse; margin-top: 6px; font-size: 9pt; }
  th { background: #FFD700; font-weight: bold; text-align: center; padding: 5px 4px; border: 1px solid #000; }
  td { border: 1px solid #000; padding: 3px 4px; vertical-align: top; }
  .center { text-align: center; }
  .right { text-align: right; }
  .cat-row td { background: #FFFACD; font-weight: bold; }
  .cat-name { text-align: left; }
  .total-section { margin-top: 6px; }
  .total-row { display: flex; justify-content: flex-end; border: 1px solid #000; margin-top: -1px; }
  .total-label { padding: 4px 10px; font-weight: bold; font-size: 9.5pt; flex: 1; text-align: right; background: #f3f4f6; }
  .total-value { padding: 4px 10px; font-weight: bold; font-size: 9.5pt; min-width: 120px; text-align: right; background: #f3f4f6; border-left: 1px solid #000; }
  .grand .total-label, .grand .total-value { background: #FFD700; font-size: 10.5pt; }
  @media print {
    body { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  }
</style>
</head>
<body>
<h1>ĐƠN HÀNG: ${title}</h1>
<p class="sub">${order.order_number ?? ''}</p>
<div class="info-grid">
  <div>
    <div class="info-row"><span class="lbl">Khách hàng:</span> <span>${order.customer_name ?? ''}</span></div>
    <div class="info-row"><span class="lbl">SĐT:</span> <span>${order.customer_phone ?? '—'}</span></div>
    <div class="info-row"><span class="lbl">Địa chỉ:</span> <span>${order.shipping_address ?? '—'}</span></div>
  </div>
  <div>
    <div class="info-row"><span class="lbl">Ngày đặt:</span> <span>${fmtDate(order.created_at)}</span></div>
    <div class="info-row"><span class="lbl">Ngày xuất:</span> <span>${fmtDate(order.delivery_date)}</span></div>
    <div class="info-row"><span class="lbl">Ghi chú:</span> <span>${order.notes ?? ''}</span></div>
  </div>
</div>
<table>
  <thead>
    <tr>
      <th style="width:32px">Năm</th>
      <th style="width:28px">TT</th>
      <th>MÔ TẢ CHI TIẾT</th>
      <th style="width:70px">MÃ HÀNG</th>
      <th style="width:50px">XUẤT XỨ</th>
      <th style="width:50px">ĐƠN VỊ</th>
      <th style="width:44px">SỐ LƯỢNG</th>
      <th style="width:80px">ĐƠN GIÁ</th>
      <th style="width:80px">THÀNH TIỀN</th>
    </tr>
  </thead>
  <tbody>${rowsHtml}</tbody>
</table>
<div class="total-section">
  <div class="total-row">
    <div class="total-label">TỔNG GIÁ TRỊ TRƯỚC THUẾ:</div>
    <div class="total-value">${fmtNum(subtotal)}đ</div>
  </div>
  <div class="total-row">
    <div class="total-label">THUẾ GTGT ${taxRate}%:</div>
    <div class="total-value">${fmtNum(tax)}đ</div>
  </div>
  <div class="total-row grand">
    <div class="total-label">TỔNG GIÁ TRỊ SAU THUẾ:</div>
    <div class="total-value">${fmtNum(grand)}đ</div>
  </div>
</div>
<script>window.onload = () => { window.print(); }<\/script>
</body>
</html>`

    const blob = new Blob([html], { type: 'text/html;charset=utf-8' })
    const url  = URL.createObjectURL(blob)
    const win  = window.open(url, '_blank')
    if (win) win.onunload = () => URL.revokeObjectURL(url)
}

function destroy() {
    if (!confirm('Xóa đơn hàng này?')) return
    router.delete(`/admin/b2b-orders/${props.order.id}`)
}
</script>

<template>
    <AdminLayout>
        <div class="space-y-4">

            <!-- Header -->
            <div class="space-y-1.5">
                <!-- Hàng 1: ← + tên đơn -->
                <div class="flex items-center gap-2">
                    <Link href="/admin/b2b-orders" class="p-1.5 rounded-lg hover:bg-gray-100 transition-colors shrink-0">
                        <ArrowLeft :size="18" class="text-gray-600" />
                    </Link>
                    <h1 class="text-base sm:text-lg font-bold text-gray-900 flex-1 min-w-0 truncate">{{ order.order_name || order.order_number }}</h1>
                </div>
                <!-- Hàng 2: mã đơn + badge + tất cả buttons -->
                <div class="flex items-center justify-between gap-2 pl-9 flex-wrap">
                    <div class="flex items-center gap-2">
                        <p class="text-xs text-gray-400 font-mono shrink-0">{{ order.order_number }}</p>
                        <span :class="['inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium shrink-0',
                            ORDER_STATUS[order.status]?.cls ?? 'bg-gray-100 text-gray-600']">
                            {{ ORDER_STATUS[order.status]?.label ?? order.status }}
                        </span>
                    </div>
                    <!-- Buttons nhóm lại -->
                    <div class="flex items-center gap-1.5 w-full sm:w-auto">
                        <Link :href="`/admin/b2b-orders/${order.id}/edit`"
                            class="flex-1 sm:flex-none flex items-center justify-center gap-1 px-2.5 py-1.5 rounded-lg bg-amber-500 text-white text-xs font-medium hover:bg-amber-600 transition-colors whitespace-nowrap">
                            <Edit2 :size="12" /> Chỉnh sửa
                        </Link>
                        <button @click="destroy"
                            class="flex-1 sm:flex-none flex items-center justify-center gap-1 px-2.5 py-1.5 rounded-lg bg-red-500 text-white text-xs font-medium hover:bg-red-600 transition-colors whitespace-nowrap">
                            <Trash2 :size="12" /> Xóa
                        </button>
                        <!-- Export dropdown -->
                        <div class="relative flex-1 sm:flex-none">
                            <button @click="showExportMenu = !showExportMenu"
                                class="w-full flex items-center justify-center gap-1 px-2.5 py-1.5 rounded-lg border border-gray-300 bg-white text-gray-700 text-xs font-medium hover:bg-gray-50 transition-colors whitespace-nowrap">
                                <Download :size="12" /> Xuất
                                <ChevronDown :size="11" :class="['transition-transform', showExportMenu ? 'rotate-180' : '']" />
                            </button>
                            <div v-if="showExportMenu"
                                class="absolute left-0 top-full mt-1 z-30 w-40 bg-white rounded-xl shadow-lg border border-gray-200 py-1 text-sm">
                                <button @click="exportOrder('xlsx')"
                                    class="w-full flex items-center gap-2.5 px-3 py-2 hover:bg-green-50 text-gray-700 transition-colors">
                                    <span>📊</span> Excel (.xlsx)
                                </button>
                                <button @click="exportOrder('pdf')"
                                    class="w-full flex items-center gap-2.5 px-3 py-2 hover:bg-red-50 text-gray-700 transition-colors">
                                    <span>📄</span> In / PDF
                                </button>
                            </div>
                            <div v-if="showExportMenu" class="fixed inset-0 z-20" @click="showExportMenu = false" />
                        </div>
                    </div>
                </div>
            </div>

            <!-- Thông tin khách hàng -->
            <div class="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
                <div class="px-4 py-3 border-b border-gray-100 bg-gray-50 flex items-center justify-between">
                    <h3 class="text-sm font-semibold text-gray-700">Thông tin khách hàng</h3>
                    <Link v-if="order.customer_id" :href="`/admin/customers/${order.customer_id}`"
                        class="flex items-center gap-1 text-xs text-indigo-600 hover:text-indigo-800 font-medium transition-colors">
                        Xem hồ sơ <ChevronRight :size="13" />
                    </Link>
                </div>
                <div class="p-4">
                    <!-- Tên KH — click vào hồ sơ -->
                    <div class="flex items-center gap-2 mb-3">
                        <div class="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-indigo-100 text-sm font-bold text-indigo-600">
                            {{ (order.customer_name || '?').charAt(0).toUpperCase() }}
                        </div>
                        <div>
                            <component :is="order.customer_id ? Link : 'span'"
                                :href="order.customer_id ? `/admin/customers/${order.customer_id}` : undefined"
                                :class="['text-base font-bold text-gray-900', order.customer_id ? 'hover:text-indigo-600 cursor-pointer transition-colors' : '']">
                                {{ order.customer_name || '—' }}
                            </component>
                            <p v-if="order.customer?.tax_code" class="text-xs text-gray-400">MST: {{ order.customer.tax_code }}</p>
                        </div>
                    </div>
                    <!-- Thông tin liên hệ + ngày -->
                    <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 text-sm">
                        <div v-if="order.customer_phone">
                            <p class="text-xs text-gray-400 mb-0.5">Số điện thoại</p>
                            <a :href="`tel:${order.customer_phone}`" class="font-medium text-gray-800 hover:text-indigo-600 transition-colors">
                                {{ order.customer_phone }}
                            </a>
                        </div>
                        <div v-if="order.customer_email">
                            <p class="text-xs text-gray-400 mb-0.5">Email</p>
                            <a :href="`mailto:${order.customer_email}`" class="font-medium text-gray-800 hover:text-indigo-600 transition-colors truncate block">
                                {{ order.customer_email }}
                            </a>
                        </div>
                        <div>
                            <p class="text-xs text-gray-400 mb-0.5">Ngày nhập</p>
                            <p class="font-medium text-gray-800">{{ fmtDate(order.created_at) }}</p>
                        </div>
                        <div>
                            <p class="text-xs text-gray-400 mb-0.5">Ngày xuất</p>
                            <p class="font-medium text-gray-800">{{ fmtDate(order.delivery_date) }}</p>
                        </div>
                    </div>
                    <div v-if="order.notes" class="mt-3 pt-3 border-t border-gray-100">
                        <p class="text-xs text-gray-400 mb-0.5">Ghi chú</p>
                        <p class="text-sm text-gray-700 whitespace-pre-wrap">{{ order.notes }}</p>
                    </div>
                </div>
            </div>

            <!-- Thanh toán + Cập nhật trạng thái (gộp 1 card) -->
            <div class="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
                <div class="px-4 py-3 border-b border-gray-100 bg-gray-50 flex items-center justify-between gap-2">
                    <div class="flex items-center gap-2 shrink-0">
                        <CreditCard :size="15" class="text-indigo-500 shrink-0" />
                        <h3 class="text-sm font-semibold text-gray-700 whitespace-nowrap">Thanh toán & Trạng thái</h3>
                    </div>
                    <div class="flex items-center gap-2 shrink-0">
                        <button @click="showPaymentModal = true"
                            class="flex items-center gap-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-700 px-3 py-1.5 text-xs font-semibold text-white shadow-sm transition-colors whitespace-nowrap">
                            <Plus :size="13" /> <span class="hidden sm:inline">Tạo thanh toán</span><span class="sm:hidden">Tạo TT</span>
                        </button>
                        <button @click.stop="paymentSectionOpen = !paymentSectionOpen"
                            class="p-1.5 rounded-lg hover:bg-gray-200 transition-colors shrink-0">
                            <ChevronDown :size="15" class="text-gray-400 transition-transform duration-200"
                                :style="{ transform: paymentSectionOpen ? 'rotate(0deg)' : 'rotate(-180deg)' }" />
                        </button>
                    </div>
                </div>
                <div v-show="paymentSectionOpen" class="p-4 space-y-4">
                    <!-- Hàng 1: 3 ô tổng quan + cập nhật trạng thái -->
                    <div class="flex flex-wrap gap-3 items-start">
                        <!-- 3 ô số tiền -->
                        <div class="flex gap-2 flex-1 min-w-0">
                            <div class="flex-1 bg-gray-50 rounded-lg p-2.5 text-center">
                                <p class="text-[10px] text-gray-400 mb-0.5">Tổng đơn</p>
                                <p class="text-sm font-bold text-gray-900">{{ fmtVND(grandTotal) }}</p>
                            </div>
                            <div class="flex-1 bg-emerald-50 rounded-lg p-2.5 text-center">
                                <p class="text-[10px] text-gray-400 mb-0.5">Đã thanh toán</p>
                                <p class="text-sm font-bold text-emerald-600">{{ fmtVND(totalPaid) }}</p>
                            </div>
                            <div :class="['flex-1 rounded-lg p-2.5 text-center', remaining > 0 ? 'bg-red-50' : 'bg-emerald-50']">
                                <p class="text-[10px] text-gray-400 mb-0.5">Còn lại</p>
                                <p :class="['text-sm font-bold', remaining > 0 ? 'text-red-600' : 'text-emerald-600']">
                                    {{ remaining > 0 ? fmtVND(remaining) : '—' }}
                                </p>
                            </div>
                        </div>
                    </div>

                    <!-- Badge trạng thái TT -->
                    <div class="flex items-center gap-2">
                        <span :class="[
                            'inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold border',
                            paymentStatus === 'paid'    ? 'bg-emerald-100 text-emerald-700 border-emerald-300' :
                            paymentStatus === 'partial' ? 'bg-yellow-100 text-yellow-700 border-yellow-300' :
                                                          'bg-red-100 text-red-700 border-red-300'
                        ]">
                            {{ paymentStatus === 'paid'    ? '✅ Đã thanh toán' :
                               paymentStatus === 'partial' ? '🔄 Một phần' : '❌ Chưa thanh toán' }}
                        </span>
                        <span v-if="order.payment_method" class="text-xs text-gray-400">{{ order.payment_method }}</span>
                    </div>

                    <!-- Lịch sử thanh toán -->
                    <div v-if="payments.length > 0" class="border-t border-gray-100 pt-3">
                        <p class="text-xs font-semibold text-gray-500 mb-2">Lịch sử thanh toán</p>
                        <div class="space-y-1.5">
                            <div v-for="p in payments" :key="p.id"
                                class="flex items-center justify-between text-xs bg-gray-50 rounded-lg px-3 py-2">
                                <div>
                                    <p class="font-semibold text-emerald-700">{{ fmtVND(p.amount) }}</p>
                                    <p class="text-gray-400 text-[10px]">{{ fmtDateTime(p.paid_at) }}</p>
                                </div>
                                <div class="text-right">
                                    <p v-if="p.payment_method" class="text-gray-500">{{ p.payment_method }}</p>
                                    <p v-if="p.notes" class="text-gray-400 text-[10px] truncate max-w-[120px]">{{ p.notes }}</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Modal tạo thanh toán -->
            <Teleport to="body">
                <div v-if="showPaymentModal"
                    class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm"
                    @click.self="showPaymentModal = false">
                    <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md">
                        <!-- Header -->
                        <div class="flex items-center justify-between px-5 py-4 border-b border-gray-100">
                            <div class="flex items-center gap-2">
                                <CreditCard :size="16" class="text-emerald-600" />
                                <h2 class="font-semibold text-gray-900">Tạo thanh toán</h2>
                            </div>
                            <button @click="showPaymentModal = false" class="p-1 rounded-lg hover:bg-gray-100 transition-colors">
                                <X :size="18" class="text-gray-500" />
                            </button>
                        </div>
                        <!-- Body -->
                        <div class="p-5 space-y-4">
                            <!-- Tóm tắt -->
                            <div class="grid grid-cols-2 gap-2 text-xs">
                                <div class="bg-gray-50 rounded-lg p-2.5">
                                    <p class="text-gray-400 mb-0.5">Tổng đơn</p>
                                    <p class="font-bold text-gray-900">{{ fmtVND(grandTotal) }}</p>
                                </div>
                                <div :class="['rounded-lg p-2.5', remaining > 0 ? 'bg-red-50' : 'bg-emerald-50']">
                                    <p class="text-gray-400 mb-0.5">Còn lại</p>
                                    <p :class="['font-bold', remaining > 0 ? 'text-red-600' : 'text-emerald-600']">
                                        {{ remaining > 0 ? fmtVND(remaining) : '—' }}
                                    </p>
                                </div>
                            </div>
                            <!-- Chế độ thanh toán -->
                            <div class="flex gap-2">
                                <button type="button" @click="setPaymentMode('full')"
                                    :class="[
                                        'flex-1 flex items-center gap-2 rounded-lg border px-3 py-2.5 text-xs font-medium transition-colors',
                                        paymentMode === 'full'
                                            ? 'border-emerald-500 bg-emerald-50 text-emerald-700'
                                            : 'border-gray-200 bg-white text-gray-600 hover:border-gray-300 hover:bg-gray-50'
                                    ]">
                                    <span :class="[
                                        'flex h-4 w-4 shrink-0 items-center justify-center rounded-full border-2 transition-colors',
                                        paymentMode === 'full' ? 'border-emerald-500' : 'border-gray-300'
                                    ]">
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
                                    <span :class="[
                                        'flex h-4 w-4 shrink-0 items-center justify-center rounded-full border-2 transition-colors',
                                        paymentMode === 'partial' ? 'border-indigo-500' : 'border-gray-300'
                                    ]">
                                        <span v-if="paymentMode === 'partial'" class="h-2 w-2 rounded-full bg-indigo-500" />
                                    </span>
                                    Từng phần
                                </button>
                            </div>

                            <!-- Form -->
                            <div>
                                <label class="block text-xs font-medium text-gray-700 mb-1">Số tiền thanh toán *</label>
                                <input
                                    :value="amountDisplay"
                                    @input="onAmountInput"
                                    type="text"
                                    inputmode="numeric"
                                    :placeholder="`Tối đa ${fmt(remaining)}`"
                                    :disabled="paymentMode === 'full'"
                                    :class="[
                                        'w-full rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500',
                                        paymentMode === 'full' ? 'border-gray-200 bg-gray-50 text-gray-500 cursor-not-allowed' : 'border-gray-300'
                                    ]" />
                                <p v-if="paymentForm.errors.amount" class="text-xs text-red-500 mt-1">{{ paymentForm.errors.amount }}</p>
                            </div>
                            <div>
                                <label class="block text-xs font-medium text-gray-700 mb-1">Phương thức</label>
                                <select v-model="paymentForm.payment_method"
                                    class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500">
                                    <option>Tiền mặt</option>
                                    <option>Chuyển khoản</option>
                                    <option>Thẻ ngân hàng</option>
                                    <option>Khác</option>
                                </select>
                            </div>
                            <div>
                                <label class="block text-xs font-medium text-gray-700 mb-1">Thời gian thanh toán</label>
                                <input v-model="paymentForm.paid_at" type="datetime-local"
                                    class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500" />
                            </div>
                            <div>
                                <label class="block text-xs font-medium text-gray-700 mb-1">Ghi chú</label>
                                <input v-model="paymentForm.notes" type="text" placeholder="Tuỳ chọn..."
                                    class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500" />
                            </div>
                        </div>
                        <!-- Footer -->
                        <div class="flex gap-2 px-5 pb-5">
                            <button @click="showPaymentModal = false"
                                class="flex-1 rounded-lg border border-gray-300 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors">
                                Hủy
                            </button>
                            <button @click="submitPayment" :disabled="paymentForm.processing || !paymentForm.amount"
                                class="flex-1 rounded-lg bg-emerald-600 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-700 disabled:opacity-60 transition-colors">
                                {{ paymentForm.processing ? 'Đang lưu...' : 'Xác nhận thanh toán' }}
                            </button>
                        </div>
                    </div>
                </div>
            </Teleport>

            <!-- Bảng chi tiết sản phẩm -->
            <div class="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
                <div class="px-4 py-3 border-b border-gray-100 bg-gray-50">
                    <div class="flex items-center justify-between">
                        <h2 class="font-semibold text-gray-800">Chi tiết sản phẩm</h2>
                        <span class="text-xs text-gray-400">{{ items.length }} dòng</span>
                    </div>
                </div>

                <div v-if="!items.length" class="text-center py-10 text-gray-400 text-sm">
                    Không có sản phẩm nào
                </div>

                <div v-else class="overflow-x-auto">
                    <table class="w-full min-w-[800px] text-xs border-collapse">
                        <thead class="bg-yellow-50 border-b-2 border-yellow-300">
                            <tr>
                                <th class="px-2 py-2 text-center font-semibold text-gray-700 border border-yellow-200 w-8 whitespace-nowrap">TT</th>
                                <th class="px-2 py-2 text-left font-semibold text-gray-700 border border-yellow-200 w-[32%]">Mô tả chi tiết</th>
                                <th class="px-2 py-2 text-left font-semibold text-gray-700 border border-yellow-200 w-28 whitespace-nowrap">Mã hàng</th>
                                <th class="px-2 py-2 text-center font-semibold text-gray-700 border border-yellow-200 w-14 whitespace-nowrap">Xuất xứ</th>
                                <th class="px-2 py-2 text-center font-semibold text-gray-700 border border-yellow-200 w-16 whitespace-nowrap">Đơn vị</th>
                                <th class="px-2 py-2 text-right font-semibold text-gray-700 border border-yellow-200 w-16 whitespace-nowrap">Số lượng</th>
                                <th class="px-2 py-2 text-right font-semibold text-gray-700 border border-yellow-200 w-28 whitespace-nowrap">Đơn giá</th>
                                <th class="px-2 py-2 text-right font-semibold text-gray-700 border border-yellow-200 w-28 whitespace-nowrap">Thành tiền</th>
                                <th class="px-2 py-2 text-left font-semibold text-gray-700 border border-yellow-200 w-36 whitespace-nowrap">Ghi chú</th>
                            </tr>
                        </thead>
                        <tbody>
                            <template v-for="(item, idx) in items" :key="item.id">
                                <!-- Category row -->
                                <tr v-if="isCategory(item)" class="bg-amber-50 border-l-4 border-amber-400">
                                    <td class="px-2 py-2 text-center text-amber-400 border border-amber-200">
                                        <span class="text-xs">📁</span>
                                    </td>
                                    <td colspan="6" class="px-2 py-2 border border-amber-200">
                                        <span class="font-bold text-amber-800 text-xs">{{ item.product_name }}</span>
                                    </td>
                                    <td class="px-2 py-2 text-right font-bold text-amber-700 whitespace-nowrap border border-amber-200">
                                        {{ fmt(categoryTotalShow(idx)) }}
                                    </td>
                                    <td class="border border-amber-200"></td>
                                </tr>
                                <!-- Item row -->
                                <tr v-else :class="idx % 2 === 0 ? 'bg-white' : 'bg-gray-50/50'">
                                    <td class="px-2 py-2 text-center text-gray-400 border border-gray-200">{{ itemSeqNumber(idx) }}</td>
                                    <td class="px-2 py-2 border border-gray-200">
                                        <div class="font-medium text-gray-800 whitespace-pre-wrap leading-relaxed">{{ item.product_name }}</div>
                                    </td>
                                    <td class="px-2 py-2 text-gray-500 font-mono border border-gray-200">{{ item.variant_sku || '—' }}</td>
                                    <td class="px-2 py-2 text-center text-gray-600 border border-gray-200">{{ item.origin || '—' }}</td>
                                    <td class="px-2 py-2 text-center text-gray-600 border border-gray-200">{{ item.unit || '—' }}</td>
                                    <td class="px-2 py-2 text-right text-gray-700 font-medium border border-gray-200">
                                        {{ Number(item.quantity).toLocaleString('vi-VN') }}
                                    </td>
                                    <td class="px-2 py-2 text-right text-gray-700 border border-gray-200">{{ fmt(item.price) }}</td>
                                    <td class="px-2 py-2 text-right font-semibold text-gray-900 whitespace-nowrap border border-gray-200">
                                        {{ fmt(Number(item.price) * Number(item.quantity)) }}
                                    </td>
                                    <td class="px-2 py-2 text-gray-600 text-xs whitespace-pre-wrap border border-gray-200">{{ getNote(item) || '—' }}</td>
                                </tr>
                            </template>
                        </tbody>
                        <tfoot class="border-t-2 border-gray-300 bg-gray-50">
                            <tr>
                                <td colspan="7" class="px-3 py-2 text-right font-semibold text-gray-700 text-xs border border-gray-200">Tổng giá trị trước thuế:</td>
                                <td class="px-3 py-2 text-right font-bold text-gray-900 text-xs whitespace-nowrap border border-gray-200">{{ fmt(totalBeforeTax) }}</td>
                                <td class="border border-gray-200"></td>
                            </tr>
                            <tr>
                                <td colspan="7" class="px-3 py-1.5 text-right text-gray-500 text-xs border border-gray-200">Thuế GTGT {{ taxRate }}%:</td>
                                <td class="px-3 py-1.5 text-right text-gray-700 text-xs whitespace-nowrap border border-gray-200">{{ fmt(tax) }}</td>
                                <td class="border border-gray-200"></td>
                            </tr>
                            <tr class="bg-indigo-50">
                                <td colspan="7" class="px-3 py-2 text-right font-bold text-indigo-700 text-xs border border-indigo-200">Tổng giá trị sau thuế:</td>
                                <td class="px-3 py-2 text-right font-bold text-indigo-700 text-sm whitespace-nowrap border border-indigo-200">{{ fmt(grandTotal) }}</td>
                                <td class="border border-indigo-200"></td>
                            </tr>
                        </tfoot>
                    </table>
                </div>
            </div>

        </div>
    </AdminLayout>
</template>
