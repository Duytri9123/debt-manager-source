<script setup>
import AdminLayout from '@/Layouts/AdminLayout.vue'
import { useForm, router } from '@inertiajs/vue3'
import { ref, computed, onMounted, nextTick } from 'vue'
import { ArrowLeft, Plus, Trash2, GripVertical, ChevronDown, ChevronUp, FolderPlus } from 'lucide-vue-next'

const props = defineProps({ 
    customers:  Array,
    products:   Array,
    taxRate:    { type: Number, default: 10 },
    taxEnabled: { type: Boolean, default: true },
})

const form = useForm({
    order_name:      '',
    status:          'pending',
    customer_name:   '',
    customer_phone:  '',
    customer_email:  '',
    customer_address:'',
    order_date:      new Date().toISOString().slice(0, 10),
    delivery_date:   '',
    notes:           '',
    items:           [],
})

// Autocomplete state
const showProductSuggestions = ref({})
const filteredProducts = ref({})
const showCustomerSuggestions = ref(false)

// ── Track dòng đang active ────────────────────────────────────────────────────
const lastActiveIdx = ref(-1)

function setActiveIdx(idx) {
    lastActiveIdx.value = idx
}

// ── Drag & Drop ───────────────────────────────────────────────────────────────
const dragIdx = ref(null)
const dragOverIdx = ref(null)

function onDragStart(idx) {
    dragIdx.value = idx
}
function onDragOver(e, idx) {
    e.preventDefault()
    dragOverIdx.value = idx
}
function onDrop(idx) {
    if (dragIdx.value === null || dragIdx.value === idx) {
        dragIdx.value = null
        dragOverIdx.value = null
        return
    }
    // Swap items và priceDisplays
    const items = [...form.items]
    const prices = [...priceDisplays.value]
    const [movedItem]  = items.splice(dragIdx.value, 1)
    const [movedPrice] = prices.splice(dragIdx.value, 1)
    items.splice(idx, 0, movedItem)
    prices.splice(idx, 0, movedPrice)
    form.items = items
    priceDisplays.value = prices
    dragIdx.value = null
    dragOverIdx.value = null
}
function onDragEnd() {
    dragIdx.value = null
    dragOverIdx.value = null
}
const filteredCustomers = ref([])
const showCustomerInfo = ref(true)
const showAiBanner     = ref(false)  // banner thông báo AI đã điền dữ liệu

// Tìm khách hàng được chọn
const selectedCustomer = computed(() => {
    if (!form.customer_name || !props.customers) return null
    return props.customers.find(c => c.name === form.customer_name)
})

// Lấy customer_id từ URL query string hoặc dữ liệu AI prefill từ sessionStorage
onMounted(() => {
    const urlParams = new URLSearchParams(window.location.search)
    const customerId = urlParams.get('customer_id')
    const aiPrefill  = urlParams.get('ai_prefill')

    // ── AI Prefill: đọc dữ liệu từ sessionStorage ────────────────────────────
    if (aiPrefill) {
        try {
            const raw = sessionStorage.getItem('ai_order_prefill')
            if (raw) {
                const orderData = JSON.parse(raw)
                sessionStorage.removeItem('ai_order_prefill') // xóa sau khi đọc

                // Điền thông tin khách hàng
                if (orderData.customer_name)    form.customer_name    = orderData.customer_name
                if (orderData.customer_phone)   form.customer_phone   = orderData.customer_phone
                if (orderData.customer_email)   form.customer_email   = orderData.customer_email
                if (orderData.customer_address) form.customer_address = orderData.customer_address
                if (orderData.order_date)       form.order_date       = orderData.order_date
                if (orderData.delivery_date)    form.delivery_date    = orderData.delivery_date
                if (orderData.order_name)       form.order_name       = orderData.order_name
                if (orderData.notes)            form.notes            = orderData.notes

                // Điền items
                if (orderData.items?.length) {
                    form.items = orderData.items.map(item => ({
                        type:          item.type || 'item',
                        description:   item.description || '',
                        product_code:  item.product_code || '',
                        origin:        item.origin || 'VN',
                        unit:          item.unit || '',
                        quantity:      Number(item.quantity) || 1,
                        unit_price:    Number(item.unit_price) || 0,
                        line_total:    Number(item.unit_price || 0) * Number(item.quantity || 1),
                        note:          item.note || '',
                        cost_price:    Number(item.cost_price) || 0,
                        selling_price: Number(item.selling_price) || 0,
                        business_pct:  Number(item.business_pct) || 0,
                        profit_per_kg: Number(item.profit_per_kg) || 0,
                        weight_kg:     Number(item.weight_kg) || 0,
                        total_profit:  Number(item.total_profit) || 0,
                        _key:          Date.now() + Math.random(),
                    }))
                    // Sync priceDisplays
                    priceDisplays.value = form.items.map(item =>
                        item.unit_price > 0 ? Number(item.unit_price).toLocaleString('vi-VN') : ''
                    )
                }

                // Hiển thị banner thông báo AI đã điền
                showAiBanner.value = true
                setTimeout(() => { showAiBanner.value = false }, 6000)
            }
        } catch (e) {
            console.warn('AI prefill parse error:', e)
        }
    }

    // ── Customer ID từ URL ────────────────────────────────────────────────────
    if (customerId && props.customers) {
        const customer = props.customers.find(c => c.id == customerId)
        if (customer) {
            form.customer_name    = customer.name
            form.customer_phone   = customer.phone || ''
            form.customer_email   = customer.email || ''
            form.customer_address = customer.address || ''
        }
    }

    // Tự động thêm 1 dòng sản phẩm đầu tiên nếu chưa có
    if (form.items.length === 0) {
        addRow()
    }

    // Auto-resize tất cả textarea khi mount
    setTimeout(() => {
        document.querySelectorAll('textarea').forEach(textarea => {
            textarea.style.height = 'auto'
            textarea.style.height = textarea.scrollHeight + 'px'
        })
    }, 100)
})

// ── Format đơn giá trong input ────────────────────────────────────────────────
const priceDisplays = ref([])

function onPriceInput(e, idx) {
    const raw = e.target.value.replace(/\./g, '').replace(/[^0-9]/g, '')
    const num = raw ? Number(raw) : 0
    form.items[idx].unit_price = num
    priceDisplays.value[idx] = raw ? num.toLocaleString('vi-VN') : ''
    recalcRow(form.items[idx])
}

// Thêm dòng sản phẩm mới
function addRow() {
    const insertAt = lastActiveIdx.value >= 0 ? lastActiveIdx.value + 1 : form.items.length
    form.items.splice(insertAt, 0, {
        type:          'item',
        description:   '',
        product_code:  '',
        origin:        'VN',
        unit:          '',
        quantity:      1,
        unit_price:    0,
        line_total:    0,
        note:          '',
        cost_price:    0,
        selling_price: 0,
        business_pct:  0,
        profit_per_kg: 0,
        weight_kg:     0,
        total_profit:  0,
        _key:          Date.now() + Math.random(),
    })
    priceDisplays.value.splice(insertAt, 0, '')
    lastActiveIdx.value = insertAt
}

// Thêm dòng danh mục — chèn sau vị trí đang active, hoặc cuối nếu chưa có
function addCategory() {
    const insertAt = lastActiveIdx.value >= 0 ? lastActiveIdx.value + 1 : form.items.length
    form.items.splice(insertAt, 0, {
        type:        'category',
        description: '',
        _key:        Date.now() + Math.random(),
    })
    priceDisplays.value.splice(insertAt, 0, '')
    lastActiveIdx.value = insertAt
}

function removeRow(idx) { 
    form.items.splice(idx, 1)
    priceDisplays.value.splice(idx, 1)
    delete showProductSuggestions.value[idx]
    delete filteredProducts.value[idx]
}

// Tổng tiền của các item sau danh mục tại idx cho đến danh mục tiếp theo
function categoryTotal(idx) {
    let total = 0
    for (let i = idx + 1; i < form.items.length; i++) {
        if (form.items[i].type === 'category') break
        total += Number(form.items[i].line_total || 0)
    }
    return total
}

// Số thứ tự của item trong danh mục của nó (reset về 1 sau mỗi category)
function itemNumber(idx) {
    let num = 0
    for (let i = 0; i <= idx; i++) {
        if (form.items[i].type === 'category') {
            num = 0
        } else {
            num++
        }
    }
    return num
}

// Lọc sản phẩm khi gõ với fuzzy search
function onDescriptionInput(idx, value) {
    if (!value || value.length < 1) {
        showProductSuggestions.value[idx] = false
        return
    }
    
    const searchTerm = value.toLowerCase().trim()
    
    // Chuẩn hóa chuỗi: bỏ dấu và khoảng trắng thừa
    const normalizeString = (str) => {
        return str.toLowerCase()
            .normalize('NFD')
            .replace(/[\u0300-\u036f]/g, '') // Bỏ dấu
            .replace(/đ/g, 'd')
            .replace(/\s+/g, ' ') // Bỏ khoảng trắng thừa
            .trim()
    }
    
    const normalizedSearch = normalizeString(searchTerm)
    
    // Tính điểm tương đồng
    const calculateScore = (product) => {
        const normalizedName = normalizeString(product.name)
        const normalizedSku = normalizeString(product.sku || '')
        
        let score = 0
        
        // Khớp chính xác (điểm cao nhất)
        if (normalizedName.includes(normalizedSearch)) {
            score += 100
        }
        if (normalizedSku.includes(normalizedSearch)) {
            score += 90
        }
        
        // Khớp từng từ
        const searchWords = normalizedSearch.split(' ')
        const nameWords = normalizedName.split(' ')
        
        searchWords.forEach(searchWord => {
            nameWords.forEach(nameWord => {
                if (nameWord.includes(searchWord)) {
                    score += 10
                } else if (searchWord.includes(nameWord) && nameWord.length > 2) {
                    score += 5
                }
            })
        })
        
        // Khớp ký tự đầu của mỗi từ (VD: "td" -> "Tủ Điện")
        const initials = nameWords.map(w => w[0]).join('')
        if (initials.includes(normalizedSearch)) {
            score += 20
        }
        
        return score
    }
    
    // Lọc và sắp xếp theo điểm
    const results = props.products
        ?.map(p => ({ product: p, score: calculateScore(p) }))
        .filter(item => item.score > 0)
        .sort((a, b) => b.score - a.score)
        .slice(0, 10)
        .map(item => item.product) || []
    
    filteredProducts.value[idx] = results
    showProductSuggestions.value[idx] = results.length > 0
}

// Chọn sản phẩm từ dropdown
function selectProduct(idx, product) {
    const item = form.items[idx]
    item.description = product.name
    
    // Tự động điền thông tin từ variant đầu tiên
    const variant = product.variants?.[0]
    if (variant) {
        item.product_code = variant.sku || product.sku || ''
        item.unit = variant.unit || ''
        item.unit_price = variant.selling_price || 0
        item.cost_price = variant.cost_price || 0
        item.selling_price = variant.selling_price || 0
    } else {
        item.product_code = product.sku || ''
    }
    
    showProductSuggestions.value[idx] = false
    recalcRow(item)
    priceDisplays.value[idx] = item.unit_price ? item.unit_price.toLocaleString('vi-VN') : ''
    
    // Auto-resize textarea sau khi chọn sản phẩm
    setTimeout(() => {
        const textareas = document.querySelectorAll('textarea')
        if (textareas[idx]) {
            textareas[idx].style.height = 'auto'
            textareas[idx].style.height = textareas[idx].scrollHeight + 'px'
        }
    }, 10)
}

// Đóng dropdown khi click ra ngoài
function closeDropdown(idx) {
    setTimeout(() => {
        showProductSuggestions.value[idx] = false
    }, 200)
}

// Auto-resize textarea
function autoResizeTextarea(event) {
    const textarea = event.target
    textarea.style.height = 'auto'
    textarea.style.height = Math.max(32, textarea.scrollHeight) + 'px'
}

function resizeAllTextareas() {
    document.querySelectorAll('textarea').forEach(t => {
        t.style.height = 'auto'
        t.style.height = Math.max(32, t.scrollHeight) + 'px'
    })
}

// Fuzzy search cho khách hàng
function onCustomerNameInput(value) {
    if (!value || value.length < 1) {
        showCustomerSuggestions.value = false
        return
    }
    
    const searchTerm = value.toLowerCase().trim()
    
    // Chuẩn hóa chuỗi
    const normalizeString = (str) => {
        return str.toLowerCase()
            .normalize('NFD')
            .replace(/[\u0300-\u036f]/g, '')
            .replace(/đ/g, 'd')
            .replace(/\s+/g, ' ')
            .trim()
    }
    
    const normalizedSearch = normalizeString(searchTerm)
    
    // Tính điểm tương đồng
    const calculateScore = (customer) => {
        const normalizedName = normalizeString(customer.name)
        const normalizedPhone = normalizeString(customer.phone || '')
        
        let score = 0
        
        // Khớp chính xác
        if (normalizedName.includes(normalizedSearch)) {
            score += 100
        }
        if (normalizedPhone.includes(normalizedSearch)) {
            score += 90
        }
        
        // Khớp từng từ
        const searchWords = normalizedSearch.split(' ')
        const nameWords = normalizedName.split(' ')
        
        searchWords.forEach(searchWord => {
            nameWords.forEach(nameWord => {
                if (nameWord.includes(searchWord)) {
                    score += 10
                } else if (searchWord.includes(nameWord) && nameWord.length > 2) {
                    score += 5
                }
            })
        })
        
        // Khớp ký tự đầu
        const initials = nameWords.map(w => w[0]).join('')
        if (initials.includes(normalizedSearch)) {
            score += 20
        }
        
        return score
    }
    
    // Lọc và sắp xếp
    const results = props.customers
        ?.map(c => ({ customer: c, score: calculateScore(c) }))
        .filter(item => item.score > 0)
        .sort((a, b) => b.score - a.score)
        .slice(0, 10)
        .map(item => item.customer) || []
    
    filteredCustomers.value = results
    showCustomerSuggestions.value = results.length > 0
}

// Chọn khách hàng từ dropdown
function selectCustomer(customer) {
    form.customer_name = customer.name
    form.customer_phone = customer.phone || ''
    form.customer_email = customer.email || ''
    form.customer_address = customer.address || ''
    showCustomerSuggestions.value = false
}

// Đóng dropdown khách hàng
function closeCustomerDropdown() {
    setTimeout(() => {
        showCustomerSuggestions.value = false
    }, 200)
}

// Tự tính thành tiền và lãi khi thay đổi
function recalcRow(item) {
    item.line_total   = Math.round(item.unit_price * item.quantity)
    item.business_pct = item.selling_price > 0
        ? Math.round((item.selling_price - item.cost_price) * item.quantity)
        : 0
    item.total_profit = item.profit_per_kg > 0 && item.weight_kg > 0
        ? Math.round(item.profit_per_kg * item.weight_kg)
        : item.business_pct
}

// Tổng (chỉ tính các dòng item, bỏ qua category)
const subtotal    = computed(() => form.items.filter(i => i.type !== 'category').reduce((s, i) => s + Number(i.line_total || 0), 0))
const tax         = computed(() => props.taxEnabled ? Math.round(subtotal.value * props.taxRate / 100) : 0)
const grandTotal  = computed(() => subtotal.value + tax.value)
const totalProfit = computed(() => form.items.filter(i => i.type !== 'category').reduce((s, i) => s + Number(i.total_profit || 0), 0))

function fmt(v) { return Number(v || 0).toLocaleString('vi-VN') }

// Parse số từ chuỗi Excel (bỏ dấu phẩy, khoảng trắng)
function parseNum(str) {
    if (!str) return 0
    const cleaned = String(str).replace(/[,\s]/g, '').replace(/[^\d.-]/g, '')
    return parseFloat(cleaned) || 0
}

// Parse TSV từ Excel — xử lý đúng ô có xuống dòng (bọc trong "...")
function parseTSV(text) {
    const rows = []
    let row = []
    let cell = ''
    let inQuote = false
    let i = 0

    while (i < text.length) {
        const ch = text[i]
        if (ch === '"') {
            if (inQuote && text[i+1] === '"') {
                cell += '"'; i += 2; continue
            }
            inQuote = !inQuote
        } else if (ch === '\t' && !inQuote) {
            row.push(cell); cell = ''
        } else if ((ch === '\r' || ch === '\n') && !inQuote) {
            if (ch === '\r' && text[i+1] === '\n') i++
            row.push(cell); cell = ''
            rows.push(row); row = []
        } else {
            cell += ch
        }
        i++
    }
    if (cell || row.length) { row.push(cell); rows.push(row) }
    // Bỏ dòng trống cuối
    while (rows.length && rows[rows.length-1].every(c => !c.trim())) rows.pop()
    return rows
}

// Xử lý paste từ Excel vào bảng
// Cột Excel: TT | Mô tả | Mã hàng | Xuất xứ | Đơn vị | Số lượng | Đơn giá | Thành tiền | Ghi chú
function handleTablePaste(event, startIdx) {
    const clipText = (event.clipboardData || window.clipboardData).getData('text')
    if (!clipText) return

    const rows = parseTSV(clipText)
    if (rows.length === 0) return

    // Nếu chỉ 1 ô đơn thì paste bình thường
    if (rows.length === 1 && rows[0].length === 1) return

    event.preventDefault()

    rows.forEach((cols, i) => {
        const idx = startIdx + i
        if (idx >= form.items.length) addRow()
        const item = form.items[idx]

        // Xác định offset: nếu cột đầu là số thứ tự (TT) thì bỏ qua
        const firstCol = cols[0]?.trim() ?? ''
        const offset = /^\d+$/.test(firstCol) ? 1 : 0

        const get = (n) => cols[offset + n]?.trim() ?? ''

        if (get(0)) item.description  = get(0)
        if (get(1)) item.product_code = get(1)
        if (get(2)) item.origin       = get(2)
        if (get(3)) item.unit         = get(3)
        if (get(4)) item.quantity     = parseNum(get(4))
        if (get(5)) {
            item.unit_price = parseNum(get(5))
            priceDisplays.value[idx] = item.unit_price ? item.unit_price.toLocaleString('vi-VN') : ''
        }
        // get(6) = thành tiền — bỏ qua, tự tính
        if (get(7)) item.note         = get(7)

        recalcRow(item)
    })

    // Resize tất cả textarea sau khi điền dữ liệu
    nextTick(() => resizeAllTextareas())
}

function submit() {
    // Filter out category rows before submitting
    const originalItems = form.items
    form.items = form.items.filter(i => i.type !== 'category')
    form.post('/admin/b2b-orders', {
        onFinish: () => {
            form.items = originalItems
        },
    })
}
</script>

<template>
    <AdminLayout>
        <div class="space-y-4">
            <!-- Banner AI đã điền dữ liệu -->
            <Transition name="slide-down">
                <div v-if="showAiBanner"
                    class="flex items-center gap-3 rounded-xl bg-indigo-50 border border-indigo-200 px-4 py-3">
                    <span class="text-xl">🤖</span>
                    <div class="flex-1">
                        <p class="text-sm font-semibold text-indigo-800">AI đã điền dữ liệu vào form</p>
                        <p class="text-xs text-indigo-600">Vui lòng kiểm tra lại thông tin trước khi lưu đơn hàng.</p>
                    </div>
                    <button @click="showAiBanner = false" class="text-indigo-400 hover:text-indigo-600 p-1">✕</button>
                </div>
            </Transition>

            <!-- Header -->
            <div class="flex items-center gap-3">
                <button @click="router.visit('/admin/b2b-orders')"
                    class="p-2 rounded-lg hover:bg-gray-100 transition-colors">
                    <ArrowLeft :size="18" class="text-gray-600" />
                </button>
                <div>
                    <h1 class="text-xl font-bold text-gray-900">Tạo đơn hàng mới</h1>
                    <p class="text-sm text-gray-500">
                        <span v-if="selectedCustomer" class="text-indigo-600 font-medium">Khách hàng: {{ selectedCustomer.name }}</span>
                        <span v-else>Nhập thông tin đơn hàng kinh doanh</span>
                    </p>
                </div>
            </div>

            <form @submit.prevent="submit" class="space-y-4">
                <div class="bg-white rounded-xl border border-gray-200 shadow-sm">
                    <!-- Header có nút ẩn/hiện -->
                    <div @click="showCustomerInfo = !showCustomerInfo"
                        class="w-full flex items-center justify-between px-4 py-3 cursor-pointer hover:bg-gray-50 transition-colors rounded-xl select-none">
                        <h3 class="text-sm font-semibold text-gray-700">Thông tin khách hàng</h3>
                        <ChevronUp v-if="showCustomerInfo" :size="16" class="text-gray-400" />
                        <ChevronDown v-else :size="16" class="text-gray-400" />
                    </div>

                    <div v-show="showCustomerInfo" class="px-4 pb-4 space-y-4 border-t border-gray-100">
                        <!-- Hàng 1: Tên KH | SĐT | Ngày đặt | Ngày xuất -->
                        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 pt-3">
                            <div class="relative">
                                <label class="block text-sm font-medium text-gray-700 mb-1">
                                    Tên khách hàng <span class="text-red-500">*</span>
                                </label>
                                <input 
                                    v-model="form.customer_name" 
                                    @input="onCustomerNameInput(form.customer_name)"
                                    @blur="closeCustomerDropdown"
                                    required
                                    placeholder="Tên khách hàng"
                                    class="w-full rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                                    :class="form.errors.customer_name ? 'border-red-400' : 'border-gray-300'" />
                                
                                <div v-if="showCustomerSuggestions" 
                                    class="absolute z-50 mt-1 w-full max-h-60 overflow-y-auto bg-white border border-gray-300 rounded-lg shadow-lg">
                                    <button
                                        v-for="customer in filteredCustomers"
                                        :key="customer.id"
                                        type="button"
                                        @mousedown.prevent="selectCustomer(customer)"
                                        class="w-full text-left px-3 py-2 text-sm hover:bg-indigo-50 border-b border-gray-100 last:border-0">
                                        <div class="font-medium text-gray-900">{{ customer.name }}</div>
                                        <div class="text-gray-500 text-xs mt-0.5">
                                            <span v-if="customer.phone">📞 {{ customer.phone }}</span>
                                        </div>
                                    </button>
                                </div>
                                <p v-if="form.errors.customer_name" class="mt-1 text-xs text-red-500">{{ form.errors.customer_name }}</p>
                            </div>

                            <div>
                                <label class="block text-sm font-medium text-gray-700 mb-1">Số điện thoại</label>
                                <input v-model="form.customer_phone" type="tel"
                                    placeholder="Số điện thoại"
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

                        <!-- Hàng 2: Ghi chú textarea full width -->
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">Ghi chú đơn hàng</label>
                            <textarea v-model="form.notes"
                                @input="autoResizeTextarea($event)"
                                rows="2"
                                placeholder="Ghi chú..."
                                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none overflow-hidden"
                                style="min-height: 60px;" />
                        </div>
                    </div>
                </div>

                <!-- Items table -->
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

                    <div v-if="!form.items.length" class="text-center py-10 text-gray-400">
                        <p class="text-sm">Chưa có sản phẩm. Nhấn "Thêm dòng" để bắt đầu.</p>
                    </div>

                    <div v-else class="overflow-x-auto">
                        <table class="w-full min-w-[900px] text-xs">
                            <thead class="bg-yellow-50 border-b border-yellow-200 sticky top-0">
                                <tr>
                                    <th class="px-1 py-2 w-5 shrink-0"></th>
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
                                            <textarea
                                                v-model="item.description"
                                                @input="e => { onDescriptionInput(idx, item.description); autoResizeTextarea(e) }"
                                                @blur="closeDropdown(idx)"
                                                @paste="e => { handleTablePaste(e, idx) }"
                                                rows="1"
                                                required
                                                placeholder="Mô tả sản phẩm... (hoặc paste từ Excel)"
                                                class="w-full rounded border border-gray-200 px-2 py-1 text-xs leading-relaxed focus:outline-none focus:ring-1 focus:ring-indigo-400 resize-y overflow-auto"
                                                style="min-height: 32px; line-height: 1.5;" />
                                            <!-- Dropdown gợi ý -->
                                            <div v-if="showProductSuggestions[idx]"
                                                class="absolute z-50 mt-1 w-full max-h-48 overflow-y-auto bg-white border border-gray-300 rounded-lg shadow-lg">
                                                <button
                                                    v-for="product in filteredProducts[idx]"
                                                    :key="product.id"
                                                    type="button"
                                                    @mousedown.prevent="selectProduct(idx, product)"
                                                    class="w-full text-left px-3 py-2 text-xs hover:bg-indigo-50 border-b border-gray-100 last:border-0">
                                                    <div class="font-medium text-gray-900">{{ product.name }}</div>
                                                    <div v-if="product.sku" class="text-gray-500 text-[10px]">SKU: {{ product.sku }}</div>
                                                </button>
                                            </div>
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
                                                type="text"
                                                inputmode="numeric"
                                                placeholder="0"
                                                class="w-full rounded border border-gray-200 px-1 py-1 text-xs text-right focus:outline-none focus:ring-1 focus:ring-indigo-400" />
                                        </td>
                                        <td class="px-2 py-1.5 text-right font-semibold text-gray-800 whitespace-nowrap">
                                            {{ fmt(item.line_total) }}
                                        </td>
                                        <td class="px-1 py-1.5 align-top">
                                            <textarea v-model="item.note"
                                                @input="autoResizeTextarea($event)"
                                                @paste="$nextTick(() => autoResizeTextarea({target: $event.target}))"
                                                placeholder="Ghi chú"
                                                rows="1"
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
                                    <td class="px-3 py-2 text-right font-bold text-gray-900 text-xs">{{ fmt(subtotal) }}đ</td>
                                    <td colspan="2"></td>
                                </tr>
                                <tr>
                                    <td colspan="8" class="px-3 py-2 text-right text-gray-500 text-xs">Thuế GTGT {{ taxRate }}%:</td>
                                    <td class="px-3 py-2 text-right text-gray-700 text-xs">{{ fmt(tax) }}đ</td>
                                    <td colspan="2"></td>
                                </tr>
                                <tr class="bg-indigo-50">
                                    <td colspan="8" class="px-3 py-2 text-right font-bold text-indigo-700 text-xs">Tổng giá trị sau thuế:</td>
                                    <td class="px-3 py-2 text-right font-bold text-indigo-700 text-sm">{{ fmt(grandTotal) }}đ</td>
                                    <td colspan="2"></td>
                                </tr>
                            </tfoot>
                        </table>
                    </div>
                </div>

                <p v-if="form.errors.items" class="text-sm text-red-500">{{ form.errors.items }}</p>

                <!-- Actions -->
                <div class="flex gap-3 justify-end">
                    <button type="button" @click="router.visit('/admin/b2b-orders')"
                        class="rounded-lg border border-gray-300 px-5 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors">
                        Hủy
                    </button>
                    <button type="submit" :disabled="form.processing || !form.items.length || !form.customer_name"
                        class="rounded-lg bg-indigo-600 px-5 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50 transition-colors">
                        {{ form.processing ? 'Đang lưu...' : '💾 Tạo đơn hàng' }}
                    </button>
                </div>
            </form>
        </div>
    </AdminLayout>
</template>

<style scoped>
.slide-down-enter-active, .slide-down-leave-active {
    transition: all 0.3s ease;
}
.slide-down-enter-from, .slide-down-leave-to {
    opacity: 0;
    transform: translateY(-8px);
}
</style>
