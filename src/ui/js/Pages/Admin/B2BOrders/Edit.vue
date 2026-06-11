<script setup>
import AdminLayout from '@/Layouts/AdminLayout.vue'
import { useForm, router } from '@inertiajs/vue3'
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { ArrowLeft, Plus, Trash2, GripVertical, ChevronDown, ChevronUp, FolderPlus } from 'lucide-vue-next'

const props = defineProps({
    order:      Object,
    customers:  Array,
    taxRate:    { type: Number, default: 10 },
    taxEnabled: { type: Boolean, default: true },
})

function getAttrs(item) {
    if (!item.variant_attributes) return {}
    try {
        return typeof item.variant_attributes === 'string'
            ? JSON.parse(item.variant_attributes)
            : item.variant_attributes
    } catch { return {} }
}

const restoredItems = (props.order.items ?? []).map((item, i) => {
    const attrs = getAttrs(item)
    if (attrs.type === 'category') {
        return {
            type:        'category',
            description: item.product_name,
            _key:        Date.now() + i,
        }
    }
    return {
        type:          'item',
        description:   item.product_name,
        product_code:  item.variant_sku ?? '',
        origin:        item.origin ?? '',
        unit:          item.unit ?? '',
        quantity:      Number(item.quantity),
        unit_price:    Number(item.price),
        line_total:    Number(item.price) * Number(item.quantity),
        note:          attrs.note ?? '',
        cost_price:    Number(item.cost_price ?? 0),
        selling_price: Number(item.selling_price ?? 0),
        business_pct:  Number(item.business_pct ?? 0),
        profit_per_kg: Number(item.profit_per_kg ?? 0),
        weight_kg:     Number(item.weight_kg ?? 0),
        total_profit:  Number(item.total_profit ?? 0),
        _key:          Date.now() + i,
    }
})

const form = useForm({
    order_name:      props.order.order_name ?? '',
    status:          props.order.status ?? 'delivered',
    customer_name:   props.order.customer_name ?? '',
    customer_phone:  props.order.customer_phone ?? '',
    customer_email:  props.order.customer_email ?? '',
    customer_address:props.order.shipping_address ?? '',
    order_date:      props.order.created_at?.slice(0, 10) ?? new Date().toISOString().slice(0, 10),
    delivery_date:   props.order.delivery_date ?? '',
    notes:           props.order.notes ?? '',
    items:           restoredItems,
})

// ── Undo / Redo ───────────────────────────────────────────────────────────────
const TRACKED_FIELDS = ['order_name', 'status', 'customer_name', 'customer_phone', 'customer_email', 'customer_address', 'order_date', 'delivery_date', 'notes', 'items']

function snapshot() {
    return JSON.parse(JSON.stringify(
        Object.fromEntries(TRACKED_FIELDS.map(k => [k, form[k]]))
    ))
}

function applySnapshot(state) {
    for (const key of TRACKED_FIELDS) {
        if (key === 'items') {
            form.items.splice(0, form.items.length, ...JSON.parse(JSON.stringify(state.items)))
            // Sync priceDisplays
            priceDisplays.value = form.items.map(item =>
                item.type === 'item' && item.unit_price
                    ? Number(item.unit_price).toLocaleString('vi-VN')
                    : ''
            )
        } else {
            form[key] = state[key]
        }
    }
    nextTick(() => resizeAllTextareas())
}

const undoHistory = ref([snapshot()])
const undoIndex   = ref(0)
let isApplying    = false

watch(
    () => snapshot(),
    (newVal) => {
        if (isApplying) return
        const current = JSON.stringify(undoHistory.value[undoIndex.value])
        if (JSON.stringify(newVal) === current) return
        undoHistory.value.splice(undoIndex.value + 1)
        undoHistory.value.push(newVal)
        undoIndex.value = undoHistory.value.length - 1
    },
    { deep: true }
)

function undo() {
    if (undoIndex.value <= 0) return
    undoIndex.value--
    isApplying = true
    applySnapshot(undoHistory.value[undoIndex.value])
    isApplying = false
}

function redo() {
    if (undoIndex.value >= undoHistory.value.length - 1) return
    undoIndex.value++
    isApplying = true
    applySnapshot(undoHistory.value[undoIndex.value])
    isApplying = false
}

function handleKeydown(e) {
    const tag = document.activeElement?.tagName
    if (tag === 'INPUT' || tag === 'TEXTAREA') return
    if (e.key === 'z' && (e.ctrlKey || e.metaKey)) {
        if (e.shiftKey) { e.preventDefault(); redo() }
        else            { e.preventDefault(); undo() }
    }
}

onUnmounted(() => window.removeEventListener('keydown', handleKeydown))
// ─────────────────────────────────────────────────────────────────────────────

// ── Price display ─────────────────────────────────────────────────────────────
const priceDisplays = ref(
    restoredItems.map(item =>
        item.type === 'item' && item.unit_price
            ? Number(item.unit_price).toLocaleString('vi-VN')
            : ''
    )
)

function onPriceInput(e, idx) {
    const raw = e.target.value.replace(/\./g, '').replace(/[^0-9]/g, '')
    const num = raw ? Number(raw) : 0
    form.items[idx].unit_price = num
    priceDisplays.value[idx] = raw ? num.toLocaleString('vi-VN') : ''
    recalcRow(form.items[idx])
}

// ── Customer autocomplete ─────────────────────────────────────────────────────
const showCustomerInfo = ref(true)
const showCustomerSuggestions = ref(false)
const filteredCustomers = ref([])

function onCustomerNameInput(value) {
    if (!value || value.length < 1) { showCustomerSuggestions.value = false; return }
    const norm = (s) => s.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/đ/g, 'd').trim()
    const q = norm(value)
    filteredCustomers.value = (props.customers ?? [])
        .filter(c => norm(c.name).includes(q) || (c.phone || '').includes(q))
        .slice(0, 10)
    showCustomerSuggestions.value = filteredCustomers.value.length > 0
}

function selectCustomer(c) {
    form.customer_name    = c.name
    form.customer_phone   = c.phone || ''
    form.customer_email   = c.email || ''
    form.customer_address = c.address || ''
    showCustomerSuggestions.value = false
}

function closeCustomerDropdown() {
    setTimeout(() => { showCustomerSuggestions.value = false }, 200)
}

// ── Track dòng đang active ────────────────────────────────────────────────────
const lastActiveIdx = ref(-1)

function setActiveIdx(idx) {
    lastActiveIdx.value = idx
}

// ── Row management ────────────────────────────────────────────────────────────
function addRow() {
    const insertAt = lastActiveIdx.value >= 0 ? lastActiveIdx.value + 1 : form.items.length
    form.items.splice(insertAt, 0, {
        type: 'item', description: '', product_code: '', origin: 'VN', unit: '',
        quantity: 1, unit_price: 0, line_total: 0, note: '',
        cost_price: 0, selling_price: 0, business_pct: 0,
        profit_per_kg: 0, weight_kg: 0, total_profit: 0,
        _key: Date.now() + Math.random(),
    })
    priceDisplays.value.splice(insertAt, 0, '')
    lastActiveIdx.value = insertAt
}

function addCategory() {
    const insertAt = lastActiveIdx.value >= 0 ? lastActiveIdx.value + 1 : form.items.length
    form.items.splice(insertAt, 0, { type: 'category', description: '', _key: Date.now() + Math.random() })
    priceDisplays.value.splice(insertAt, 0, '')
    lastActiveIdx.value = insertAt
}

function removeRow(idx) {
    form.items.splice(idx, 1)
    priceDisplays.value.splice(idx, 1)
}

function recalcRow(item) {
    item.line_total = Math.round(item.unit_price * item.quantity)
}

function categoryTotal(idx) {
    let total = 0
    for (let i = idx + 1; i < form.items.length; i++) {
        if (form.items[i].type === 'category') break
        total += Number(form.items[i].line_total || 0)
    }
    return total
}

function itemNumber(idx) {
    let num = 0
    for (let i = 0; i <= idx; i++) {
        if (form.items[i].type === 'category') num = 0
        else num++
    }
    return num
}

// ── Drag & Drop ───────────────────────────────────────────────────────────────
const dragIdx = ref(null)
const dragOverIdx = ref(null)

function onDragStart(idx) { dragIdx.value = idx }
function onDragOver(e, idx) { e.preventDefault(); dragOverIdx.value = idx }
function onDrop(idx) {
    if (dragIdx.value === null || dragIdx.value === idx) { dragIdx.value = null; dragOverIdx.value = null; return }
    const items = [...form.items]
    const prices = [...priceDisplays.value]
    const [mi] = items.splice(dragIdx.value, 1)
    const [mp] = prices.splice(dragIdx.value, 1)
    items.splice(idx, 0, mi)
    prices.splice(idx, 0, mp)
    form.items = items
    priceDisplays.value = prices
    dragIdx.value = null; dragOverIdx.value = null
}
function onDragEnd() { dragIdx.value = null; dragOverIdx.value = null }

// ── Textarea resize ───────────────────────────────────────────────────────────
function autoResizeTextarea(event) {
    const t = event.target
    t.style.height = 'auto'
    t.style.height = Math.max(32, t.scrollHeight) + 'px'
}
function resizeAllTextareas() {
    document.querySelectorAll('textarea').forEach(t => {
        t.style.height = 'auto'
        t.style.height = Math.max(32, t.scrollHeight) + 'px'
    })
}
onMounted(() => {
    setTimeout(() => resizeAllTextareas(), 100)
    window.addEventListener('keydown', handleKeydown)
})

// ── Totals ────────────────────────────────────────────────────────────────────
const subtotal   = computed(() => form.items.filter(i => i.type !== 'category').reduce((s, i) => s + Number(i.line_total || 0), 0))
const tax        = computed(() => props.taxEnabled ? Math.round(subtotal.value * props.taxRate / 100) : 0)
const grandTotal = computed(() => subtotal.value + tax.value)

function fmt(v) { return Number(v || 0).toLocaleString('vi-VN') }

function submit() {
    form.put(`/admin/b2b-orders/${props.order.id}`)
}
</script>

<template>
    <AdminLayout>
        <div class="space-y-4">
            <!-- Header -->
            <div class="flex items-center justify-between gap-3">
                <div class="flex items-center gap-3">
                    <button @click="router.visit(`/admin/b2b-orders/${order.id}`)"
                        class="p-2 rounded-lg hover:bg-gray-100 transition-colors">
                        <ArrowLeft :size="18" class="text-gray-600" />
                    </button>
                    <div>
                        <h1 class="text-xl font-bold text-gray-900">Chỉnh sửa đơn hàng</h1>
                        <p class="text-sm text-gray-500 font-mono">{{ order.order_number }}</p>
                    </div>
                </div>
                <!-- Undo / Redo -->
                <div class="flex items-center gap-1">
                    <button type="button" @click="undo" :disabled="undoIndex <= 0"
                        title="Hoàn tác (Ctrl+Z)"
                        class="rounded-lg border border-gray-200 p-1.5 text-gray-500 hover:bg-gray-100 disabled:opacity-30 disabled:cursor-not-allowed">
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 7v6h6"/><path d="M21 17a9 9 0 0 0-9-9 9 9 0 0 0-6 2.3L3 13"/></svg>
                    </button>
                    <button type="button" @click="redo" :disabled="undoIndex >= undoHistory.length - 1"
                        title="Làm lại (Ctrl+Shift+Z)"
                        class="rounded-lg border border-gray-200 p-1.5 text-gray-500 hover:bg-gray-100 disabled:opacity-30 disabled:cursor-not-allowed">
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 7v6h-6"/><path d="M3 17a9 9 0 0 1 9-9 9 9 0 0 1 6 2.3L21 13"/></svg>
                    </button>
                </div>
            </div>

            <form @submit.prevent="submit" class="space-y-4">
                <!-- Thông tin khách hàng -->
                <div class="bg-white rounded-xl border border-gray-200 shadow-sm">
                    <div @click="showCustomerInfo = !showCustomerInfo"
                        class="w-full flex items-center justify-between px-4 py-3 cursor-pointer hover:bg-gray-50 transition-colors rounded-xl select-none">
                        <h3 class="text-sm font-semibold text-gray-700">Thông tin khách hàng</h3>
                        <ChevronUp v-if="showCustomerInfo" :size="16" class="text-gray-400" />
                        <ChevronDown v-else :size="16" class="text-gray-400" />
                    </div>

                    <div v-show="showCustomerInfo" class="px-4 pb-4 space-y-4 border-t border-gray-100">
                        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 pt-3">
                            <div class="relative">
                                <label class="block text-sm font-medium text-gray-700 mb-1">Tên khách hàng <span class="text-red-500">*</span></label>
                                <input v-model="form.customer_name"
                                    @input="onCustomerNameInput(form.customer_name)"
                                    @blur="closeCustomerDropdown"
                                    required placeholder="Tên khách hàng"
                                    class="w-full rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                                    :class="form.errors.customer_name ? 'border-red-400' : 'border-gray-300'" />
                                <div v-if="showCustomerSuggestions"
                                    class="absolute z-50 mt-1 w-full max-h-60 overflow-y-auto bg-white border border-gray-300 rounded-lg shadow-lg">
                                    <button v-for="c in filteredCustomers" :key="c.id" type="button"
                                        @mousedown.prevent="selectCustomer(c)"
                                        class="w-full text-left px-3 py-2 text-sm hover:bg-indigo-50 border-b border-gray-100 last:border-0">
                                        <div class="font-medium text-gray-900">{{ c.name }}</div>
                                        <div v-if="c.phone" class="text-gray-500 text-xs">📞 {{ c.phone }}</div>
                                    </button>
                                </div>
                            </div>
                            <div>
                                <label class="block text-sm font-medium text-gray-700 mb-1">Số điện thoại</label>
                                <input v-model="form.customer_phone" type="tel" placeholder="Số điện thoại"
                                    class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                            </div>
                            <div>
                                <label class="block text-sm font-medium text-gray-700 mb-1">Ngày đặt <span class="text-red-500">*</span></label>
                                <input v-model="form.order_date" type="date" required
                                    class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                            </div>
                            <div>
                                <label class="block text-sm font-medium text-gray-700 mb-1">Ngày xuất</label>
                                <input v-model="form.delivery_date" type="date"
                                    class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                            </div>
                        </div>
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">Ghi chú đơn hàng</label>
                            <textarea v-model="form.notes" @input="autoResizeTextarea($event)" rows="2"
                                placeholder="Ghi chú..."
                                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none overflow-hidden"
                                style="min-height: 60px;" />
                        </div>
                    </div>
                </div>

                <!-- Chi tiết sản phẩm -->
                <div class="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
                    <div class="px-4 py-3 border-b border-gray-100 bg-gray-50">
                        <!-- Hàng 1: Tên đơn hàng (label trên, input + select dưới) -->
                        <div class="mb-3">
                            <label class="block text-sm font-semibold text-gray-800 mb-1">Tên đơn hàng</label>
                            <div class="flex items-center gap-2">
                                <input v-model="form.order_name"
                                    placeholder="VD: Đơn tháng 5, Dự án ABC..."
                                    class="w-full max-w-sm rounded-lg border border-gray-300 px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                                <select v-model="form.status"
                                    class="shrink-0 rounded-lg border border-gray-300 px-2.5 py-1.5 text-xs focus:outline-none focus:ring-2 focus:ring-indigo-500">
                                    <option value="pending">⏳ Chờ xử lý</option>
                                    <option value="processing">🔄 Đang xử lý</option>
                                    <option value="shipped">🚚 Đang giao</option>
                                    <option value="delivered">✅ Đã giao</option>
                                    <option value="cancelled">❌ Đã hủy</option>
                                </select>
                            </div>
                        </div>
                        <!-- Hàng 2: Chi tiết sản phẩm + Thêm dòng -->
                        <div class="flex items-center justify-between gap-2 flex-wrap">
                            <h2 class="text-sm font-semibold text-gray-800 shrink-0">Chi tiết sản phẩm</h2>
                            <div class="flex items-center gap-3 shrink-0">
                                <button type="button" @click="addCategory"
                                    class="flex items-center gap-1.5 text-sm text-amber-600 hover:text-amber-800 font-medium whitespace-nowrap">
                                    <FolderPlus :size="15" /> Thêm danh mục
                                </button>
                                <button type="button" @click="addRow"
                                    class="flex items-center gap-1.5 text-sm text-indigo-600 hover:text-indigo-800 font-medium whitespace-nowrap">
                                    <Plus :size="15" /> Thêm dòng
                                </button>
                            </div>
                        </div>
                    </div>

                    <div v-if="!form.items.length" class="text-center py-10 text-gray-400 text-sm">
                        Chưa có sản phẩm. Nhấn "Thêm dòng" để bắt đầu.
                    </div>

                    <div v-else class="overflow-x-auto">
                        <table class="w-full min-w-[900px] text-xs">
                            <thead class="bg-yellow-50 border-b border-yellow-200 sticky top-0">
                                <tr>
                                    <th class="px-1 py-2 w-5"></th>
                                    <th class="px-1 py-2 text-center font-semibold text-gray-700 w-7 whitespace-nowrap">TT</th>
                                    <th class="px-2 py-2 text-left font-semibold text-gray-700 w-[32%]">Mô tả chi tiết *</th>
                                    <th class="px-2 py-2 text-left font-semibold text-gray-700 w-28 whitespace-nowrap">Mã hàng</th>
                                    <th class="px-2 py-2 text-center font-semibold text-gray-700 w-14 whitespace-nowrap">Xuất xứ</th>
                                    <th class="px-2 py-2 text-center font-semibold text-gray-700 w-16 whitespace-nowrap">Đơn vị</th>
                                    <th class="px-2 py-2 text-right font-semibold text-gray-700 w-16 whitespace-nowrap">Số lượng</th>
                                    <th class="px-2 py-2 text-right font-semibold text-gray-700 w-28 whitespace-nowrap">Đơn giá</th>
                                    <th class="px-2 py-2 text-right font-semibold text-gray-700 w-28 whitespace-nowrap">Thành tiền</th>
                                    <th class="px-2 py-2 text-left font-semibold text-gray-700 w-36 whitespace-nowrap">Ghi chú</th>
                                    <th class="px-1 py-2 w-7"></th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-gray-100">
                                <template v-for="(item, idx) in form.items" :key="item._key">
                                    <!-- ── Dòng danh mục ── -->
                                    <tr v-if="item.type === 'category'"
                                        draggable="true"
                                        @focusin="setActiveIdx(idx)"
                                        @click="setActiveIdx(idx)"
                                        @dragstart="onDragStart(idx)"
                                        @dragover="onDragOver($event, idx)"
                                        @drop="onDrop(idx)"
                                        @dragend="onDragEnd"
                                        :class="[
                                            'bg-amber-50 border-l-4 border-amber-400 transition-opacity',
                                            dragOverIdx === idx && dragIdx !== idx ? 'opacity-60 border-t-2 border-t-indigo-400' : '',
                                            dragIdx === idx ? 'opacity-30' : ''
                                        ]">
                                        <td class="px-1 py-1.5 text-amber-400 cursor-grab active:cursor-grabbing">
                                            <GripVertical :size="12" />
                                        </td>
                                        <td class="px-1 py-1.5 text-amber-500 text-center">
                                            <FolderPlus :size="13" />
                                        </td>
                                        <td colspan="6" class="px-2 py-1.5">
                                            <input v-model="item.description"
                                                placeholder="Tên danh mục (VD: Tủ điện 1, Thiết bị chính...)"
                                                class="w-full rounded border border-amber-200 bg-amber-50 px-2 py-1 text-xs font-bold text-amber-800 focus:outline-none focus:ring-1 focus:ring-amber-400 placeholder:font-normal placeholder:text-amber-300" />
                                        </td>
                                        <td class="px-2 py-1.5 text-right font-bold text-amber-700 whitespace-nowrap">
                                            {{ fmt(categoryTotal(idx)) }}
                                        </td>
                                        <td class="px-1 py-1.5"></td>
                                        <td class="px-1 py-1.5 text-center">
                                            <button type="button" @click="removeRow(idx)"
                                                class="p-1 rounded hover:bg-red-50 text-red-400 transition-colors">
                                                <Trash2 :size="12" />
                                            </button>
                                        </td>
                                    </tr>

                                    <!-- ── Dòng sản phẩm ── -->
                                    <tr v-else
                                        draggable="true"
                                        @focusin="setActiveIdx(idx)"
                                        @click="setActiveIdx(idx)"
                                        @dragstart="onDragStart(idx)"
                                        @dragover="onDragOver($event, idx)"
                                        @drop="onDrop(idx)"
                                        @dragend="onDragEnd"
                                        :class="[
                                            'transition-opacity',
                                            dragOverIdx === idx && dragIdx !== idx ? 'opacity-60 border-t-2 border-t-indigo-400' : 'hover:bg-gray-50',
                                            dragIdx === idx ? 'opacity-30' : ''
                                        ]">
                                        <td class="px-1 py-1.5 text-gray-300 cursor-grab active:cursor-grabbing">
                                            <GripVertical :size="12" />
                                        </td>
                                        <td class="px-1 py-1.5 text-gray-400 text-center">{{ itemNumber(idx) }}</td>
                                        <td class="px-2 py-1.5 relative">
                                            <textarea v-model="item.description"
                                                @input="autoResizeTextarea($event)"
                                                rows="1" required
                                                placeholder="Mô tả sản phẩm..."
                                                class="w-full rounded border border-gray-200 px-2 py-1 text-xs leading-relaxed focus:outline-none focus:ring-1 focus:ring-indigo-400 resize-y overflow-auto"
                                                style="min-height: 32px; line-height: 1.5;" />
                                        </td>
                                        <td class="px-1 py-1.5">
                                            <input v-model="item.product_code" placeholder="Mã SP"
                                                class="w-full rounded border border-gray-200 px-2 py-1 text-xs focus:outline-none focus:ring-1 focus:ring-indigo-400" />
                                        </td>
                                        <td class="px-1 py-1.5">
                                            <input v-model="item.origin" placeholder="VN"
                                                class="w-full rounded border border-gray-200 px-1 py-1 text-xs text-center focus:outline-none focus:ring-1 focus:ring-indigo-400" />
                                        </td>
                                        <td class="px-1 py-1.5">
                                            <input v-model="item.unit" placeholder="Cái"
                                                class="w-full rounded border border-gray-200 px-1 py-1 text-xs text-center focus:outline-none focus:ring-1 focus:ring-indigo-400" />
                                        </td>
                                        <td class="px-1 py-1.5">
                                            <input v-model.number="item.quantity" type="number" min="0" step="1"
                                                @input="recalcRow(item)"
                                                class="w-full rounded border border-gray-200 px-1 py-1 text-xs text-right focus:outline-none focus:ring-1 focus:ring-indigo-400" />
                                        </td>
                                        <td class="px-1 py-1.5">
                                            <input
                                                :value="priceDisplays[idx]"
                                                @input="onPriceInput($event, idx)"
                                                type="text" inputmode="numeric" placeholder="0"
                                                class="w-full rounded border border-gray-200 px-1 py-1 text-xs text-right focus:outline-none focus:ring-1 focus:ring-indigo-400" />
                                        </td>
                                        <td class="px-2 py-1.5 text-right font-semibold text-gray-800 whitespace-nowrap">
                                            {{ fmt(item.line_total) }}
                                        </td>
                                        <td class="px-1 py-1.5 align-top">
                                            <textarea v-model="item.note"
                                                @input="autoResizeTextarea($event)"
                                                @paste="$nextTick(() => resizeAllTextareas())"
                                                placeholder="Ghi chú" rows="1"
                                                class="w-full rounded border border-gray-200 px-2 py-1 text-xs focus:outline-none focus:ring-1 focus:ring-indigo-400 resize-none overflow-hidden"
                                                style="min-height: 32px; line-height: 1.5;" />
                                        </td>
                                        <td class="px-1 py-1.5 text-center">
                                            <button type="button" @click="removeRow(idx)"
                                                class="p-1 rounded hover:bg-red-50 text-red-400 transition-colors">
                                                <Trash2 :size="12" />
                                            </button>
                                        </td>
                                    </tr>
                                </template>
                            </tbody>
                            <tfoot class="border-t-2 border-gray-300 bg-gray-50">
                                <tr>
                                    <td colspan="8" class="px-3 py-2 text-right font-semibold text-gray-700 text-xs">Tổng giá trị trước thuế:</td>
                                    <td class="px-3 py-2 text-right font-bold text-gray-900 text-xs whitespace-nowrap">{{ fmt(subtotal) }}đ</td>
                                    <td colspan="2"></td>
                                </tr>
                                <tr>
                                    <td colspan="8" class="px-3 py-2 text-right text-gray-500 text-xs">Thuế GTGT {{ taxRate }}%:</td>
                                    <td class="px-3 py-2 text-right text-gray-700 text-xs whitespace-nowrap">{{ fmt(tax) }}đ</td>
                                    <td colspan="2"></td>
                                </tr>
                                <tr class="bg-indigo-50">
                                    <td colspan="8" class="px-3 py-2 text-right font-bold text-indigo-700 text-xs">Tổng giá trị sau thuế:</td>
                                    <td class="px-3 py-2 text-right font-bold text-indigo-700 text-sm whitespace-nowrap">{{ fmt(grandTotal) }}đ</td>
                                    <td colspan="2"></td>
                                </tr>
                            </tfoot>
                        </table>
                    </div>
                </div>

                <!-- Actions -->
                <div class="flex gap-3 justify-end">
                    <button type="button" @click="router.visit(`/admin/b2b-orders/${order.id}`)"
                        class="rounded-lg border border-gray-300 px-5 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors">
                        Hủy
                    </button>
                    <button type="submit" :disabled="form.processing || !form.items.length"
                        class="rounded-lg bg-indigo-600 px-5 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50 transition-colors">
                        {{ form.processing ? 'Đang lưu...' : '💾 Lưu thay đổi' }}
                    </button>
                </div>
            </form>
        </div>
    </AdminLayout>
</template>
