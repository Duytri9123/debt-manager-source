<script setup>
import AdminLayout from '@/Layouts/AdminLayout.vue'
import { useForm, router } from '@inertiajs/vue3'
import { ref, computed, onMounted } from 'vue'
import { Plus, Trash2, Camera, Loader2, CheckCircle } from 'lucide-vue-next'

const props = defineProps({
    suppliers: Array,
    products: Array,
    customers: Array,
})

// ── Form ──────────────────────────────────────────────────────────────────────
const form = useForm({
    supplier_id: '',
    customer_id: '',
    invoice_date: new Date().toISOString().split('T')[0],
    due_date: '',
    status: 'draft',
    tax_amount: 0,
    discount_amount: 0,
    notes: '',
    items: [],
})

// Lấy customer_id từ URL query string
onMounted(() => {
    const urlParams = new URLSearchParams(window.location.search)
    const customerId = urlParams.get('customer_id')
    
    if (customerId) {
        form.customer_id = customerId
        // Nếu customer cũng là supplier, tự động chọn
        const supplier = props.suppliers?.find(s => s.customer_id == customerId)
        if (supplier) {
            form.supplier_id = supplier.id
        }
    }
    
    // Tự động thêm 1 dòng sản phẩm đầu tiên
    if (form.items.length === 0) {
        addItem()
    }
})

function addItem() {
    form.items.push({ product_name: '', unit: '', quantity: 1, unit_price: 0, tax_rate: 0, discount_rate: 0, product_id: null, product_variant_id: null })
}

function removeItem(i) {
    form.items.splice(i, 1)
}

function onProductSelect(i, productId) {
    const product = props.products.find(p => p.id == productId)
    if (product) {
        form.items[i].product_name = product.name
        form.items[i].product_id = product.id
        const defaultVariant = product.variants?.[0]
        if (defaultVariant) {
            form.items[i].unit = defaultVariant.unit ?? ''
            form.items[i].unit_price = defaultVariant.cost_price ?? defaultVariant.selling_price ?? 0
            form.items[i].product_variant_id = defaultVariant.id
        }
    }
}

function itemTotal(item) {
    const base = item.quantity * item.unit_price
    const afterDisc = base * (1 - item.discount_rate / 100)
    return afterDisc * (1 + item.tax_rate / 100)
}

const subtotal = computed(() => form.items.reduce((s, i) => s + itemTotal(i), 0))
const grandTotal = computed(() => subtotal.value + Number(form.tax_amount) - Number(form.discount_amount))

// Tìm tên khách hàng để hiển thị
const selectedCustomer = computed(() => {
    if (!form.customer_id || !props.customers) return null
    return props.customers.find(c => c.id == form.customer_id)
})

function formatVND(v) { return Number(v).toLocaleString('vi-VN', { style: 'currency', currency: 'VND' }) }

function submit() {
    form.post('/admin/purchase-invoices')
}

// ── AI Scan ───────────────────────────────────────────────────────────────────
const aiScanning = ref(false)
const aiResult = ref(null)
const aiError = ref('')
const imagePreview = ref('')

async function scanInvoice(e) {
    const file = e.target.files[0]
    if (!file) return

    imagePreview.value = URL.createObjectURL(file)
    aiScanning.value = true
    aiError.value = ''
    aiResult.value = null

    const fd = new FormData()
    fd.append('image', file)

    try {
        const res = await fetch('/admin/purchase-invoices/ai-extract', {
            method: 'POST',
            headers: { 'X-CSRF-TOKEN': document.querySelector('meta[name="csrf-token"]').content },
            body: fd,
        })
        const data = await res.json()
        if (data.success) {
            aiResult.value = data.data
        } else {
            aiError.value = data.error ?? 'Không thể đọc hóa đơn'
        }
    } catch (err) {
        aiError.value = 'Lỗi kết nối: ' + err.message
    } finally {
        aiScanning.value = false
    }
}

function applyAiResult() {
    if (!aiResult.value) return
    const d = aiResult.value

    // Điền thông tin chung
    if (d.invoice_date) form.invoice_date = d.invoice_date
    if (d.total_amount) {
        // Tìm supplier theo tên
        if (d.supplier_name) {
            const sup = props.suppliers.find(s => s.name.toLowerCase().includes(d.supplier_name.toLowerCase()))
            if (sup) form.supplier_id = sup.id
        }
    }

    // Điền items
    if (d.items?.length) {
        form.items = d.items.map(item => ({
            product_name: item.product_name ?? '',
            unit: item.unit ?? '',
            quantity: item.quantity ?? 1,
            unit_price: item.unit_price ?? 0,
            tax_rate: 0,
            discount_rate: 0,
            product_id: null,
            product_variant_id: null,
        }))
    }

    aiResult.value = null
    imagePreview.value = ''
}
</script>

<template>
    <AdminLayout>
        <div class="space-y-6">
            <!-- Header -->
            <div class="flex items-center gap-3">
                <button @click="router.visit('/admin/purchase-invoices')" class="text-gray-500 hover:text-gray-700">← Quay lại</button>
                <div>
                    <h1 class="text-xl font-bold text-gray-900">Tạo hóa đơn nhập hàng</h1>
                    <p v-if="selectedCustomer" class="text-sm text-indigo-600 font-medium mt-0.5">
                        Khách hàng: {{ selectedCustomer.name }}
                    </p>
                </div>
            </div>

            <!-- AI Scan Banner -->
            <div class="bg-gradient-to-r from-indigo-50 to-purple-50 border border-indigo-200 rounded-xl p-4">
                <div class="flex items-start gap-4">
                    <div class="flex-1">
                        <h3 class="font-semibold text-indigo-900 flex items-center gap-2">
                            <Camera :size="18" /> Quét hóa đơn bằng AI
                        </h3>
                        <p class="text-sm text-indigo-700 mt-1">Chụp ảnh hoặc upload hóa đơn giấy, AI sẽ tự động điền thông tin</p>
                    </div>
                    <label class="cursor-pointer flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 transition-colors">
                        <Camera :size="16" />
                        {{ aiScanning ? 'Đang đọc...' : 'Chọn ảnh hóa đơn' }}
                        <input type="file" class="hidden" accept="image/*" @change="scanInvoice" :disabled="aiScanning" />
                    </label>
                </div>

                <!-- Scanning indicator -->
                <div v-if="aiScanning" class="mt-3 flex items-center gap-2 text-indigo-700">
                    <Loader2 :size="16" class="animate-spin" />
                    <span class="text-sm">AI đang đọc hóa đơn...</span>
                </div>

                <!-- Error -->
                <div v-if="aiError" class="mt-3 text-sm text-red-600 bg-red-50 rounded-lg px-3 py-2">{{ aiError }}</div>

                <!-- AI Result preview -->
                <div v-if="aiResult" class="mt-4 bg-white rounded-xl border border-indigo-200 p-4">
                    <div class="flex items-center justify-between mb-3">
                        <h4 class="font-semibold text-gray-900 flex items-center gap-2">
                            <CheckCircle :size="16" class="text-emerald-500" /> AI đã đọc được thông tin
                        </h4>
                        <div class="flex gap-2">
                            <button @click="applyAiResult"
                                class="rounded-lg bg-emerald-600 px-4 py-1.5 text-sm font-medium text-white hover:bg-emerald-700 transition-colors">
                                Áp dụng
                            </button>
                            <button @click="aiResult = null" class="rounded-lg border border-gray-300 px-4 py-1.5 text-sm text-gray-600 hover:bg-gray-50">
                                Bỏ qua
                            </button>
                        </div>
                    </div>
                    <div class="grid grid-cols-2 gap-3 text-sm mb-3">
                        <div><span class="text-gray-500">Nhà cung cấp:</span> <span class="font-medium">{{ aiResult.supplier_name ?? '—' }}</span></div>
                        <div><span class="text-gray-500">Số HĐ:</span> <span class="font-medium">{{ aiResult.invoice_number ?? '—' }}</span></div>
                        <div><span class="text-gray-500">Ngày:</span> <span class="font-medium">{{ aiResult.invoice_date ?? '—' }}</span></div>
                        <div><span class="text-gray-500">Tổng tiền:</span> <span class="font-medium text-indigo-600">{{ aiResult.total_amount ? formatVND(aiResult.total_amount) : '—' }}</span></div>
                    </div>
                    <div v-if="aiResult.items?.length" class="text-sm">
                        <p class="text-gray-500 mb-1">{{ aiResult.items.length }} sản phẩm được nhận diện:</p>
                        <div class="space-y-1">
                            <div v-for="(item, i) in aiResult.items" :key="i" class="flex justify-between bg-gray-50 rounded px-3 py-1.5">
                                <span>{{ item.product_name }}</span>
                                <span class="text-gray-500">{{ item.quantity }} {{ item.unit }} × {{ formatVND(item.unit_price) }}</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <form @submit.prevent="submit" class="space-y-6">
                <!-- General info -->
                <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                    <h2 class="font-semibold text-gray-900 mb-4">Thông tin chung</h2>
                    <div class="grid grid-cols-2 gap-4">
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">Nhà cung cấp</label>
                            <select v-model="form.supplier_id"
                                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                                <option value="">— Chọn NCC —</option>
                                <option v-for="s in suppliers" :key="s.id" :value="s.id">{{ s.name }}</option>
                            </select>
                        </div>
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">Trạng thái</label>
                            <select v-model="form.status"
                                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                                <option value="draft">Nháp</option>
                                <option value="confirmed">Đã xác nhận</option>
                                <option value="received">Đã nhận hàng</option>
                                <option value="cancelled">Đã hủy</option>
                            </select>
                        </div>
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">Ngày hóa đơn <span class="text-red-500">*</span></label>
                            <input v-model="form.invoice_date" type="date"
                                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                                :class="{ 'border-red-400': form.errors.invoice_date }" />
                        </div>
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">Hạn thanh toán</label>
                            <input v-model="form.due_date" type="date"
                                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                        </div>
                        <div class="col-span-2">
                            <label class="block text-sm font-medium text-gray-700 mb-1">Ghi chú</label>
                            <textarea v-model="form.notes" rows="2"
                                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                        </div>
                    </div>
                </div>

                <!-- Items -->
                <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                    <div class="flex items-center justify-between mb-4">
                        <h2 class="font-semibold text-gray-900">Danh sách hàng hóa</h2>
                        <button type="button" @click="addItem"
                            class="flex items-center gap-1.5 rounded-lg border border-indigo-300 px-3 py-1.5 text-sm text-indigo-600 hover:bg-indigo-50 transition-colors">
                            <Plus :size="14" /> Thêm dòng
                        </button>
                    </div>

                    <div class="overflow-x-auto">
                        <table class="w-full text-sm">
                            <thead>
                                <tr class="border-b border-gray-200">
                                    <th class="text-left pb-2 font-medium text-gray-600 w-48">Sản phẩm</th>
                                    <th class="text-left pb-2 font-medium text-gray-600 w-24">Tên hàng</th>
                                    <th class="text-left pb-2 font-medium text-gray-600 w-20">ĐVT</th>
                                    <th class="text-right pb-2 font-medium text-gray-600 w-20">SL</th>
                                    <th class="text-right pb-2 font-medium text-gray-600 w-28">Đơn giá</th>
                                    <th class="text-right pb-2 font-medium text-gray-600 w-16">Thuế%</th>
                                    <th class="text-right pb-2 font-medium text-gray-600 w-16">CK%</th>
                                    <th class="text-right pb-2 font-medium text-gray-600 w-28">Thành tiền</th>
                                    <th class="w-8"></th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-gray-100">
                                <tr v-for="(item, i) in form.items" :key="i">
                                    <td class="py-2 pr-2">
                                        <select @change="e => onProductSelect(i, e.target.value)"
                                            class="w-full rounded border border-gray-200 px-2 py-1.5 text-xs focus:outline-none focus:ring-1 focus:ring-indigo-500">
                                            <option value="">— Chọn SP —</option>
                                            <option v-for="p in products" :key="p.id" :value="p.id">{{ p.name }}</option>
                                        </select>
                                    </td>
                                    <td class="py-2 pr-2">
                                        <input v-model="item.product_name" type="text" placeholder="Tên hàng"
                                            class="w-full rounded border border-gray-200 px-2 py-1.5 text-xs focus:outline-none focus:ring-1 focus:ring-indigo-500" />
                                    </td>
                                    <td class="py-2 pr-2">
                                        <input v-model="item.unit" type="text" placeholder="cái"
                                            class="w-full rounded border border-gray-200 px-2 py-1.5 text-xs focus:outline-none focus:ring-1 focus:ring-indigo-500" />
                                    </td>
                                    <td class="py-2 pr-2">
                                        <input v-model.number="item.quantity" type="number" min="0.001" step="0.001"
                                            class="w-full rounded border border-gray-200 px-2 py-1.5 text-xs text-right focus:outline-none focus:ring-1 focus:ring-indigo-500" />
                                    </td>
                                    <td class="py-2 pr-2">
                                        <input v-model.number="item.unit_price" type="number" min="0"
                                            class="w-full rounded border border-gray-200 px-2 py-1.5 text-xs text-right focus:outline-none focus:ring-1 focus:ring-indigo-500" />
                                    </td>
                                    <td class="py-2 pr-2">
                                        <input v-model.number="item.tax_rate" type="number" min="0" max="100"
                                            class="w-full rounded border border-gray-200 px-2 py-1.5 text-xs text-right focus:outline-none focus:ring-1 focus:ring-indigo-500" />
                                    </td>
                                    <td class="py-2 pr-2">
                                        <input v-model.number="item.discount_rate" type="number" min="0" max="100"
                                            class="w-full rounded border border-gray-200 px-2 py-1.5 text-xs text-right focus:outline-none focus:ring-1 focus:ring-indigo-500" />
                                    </td>
                                    <td class="py-2 pr-2 text-right font-medium text-gray-900 text-xs">
                                        {{ formatVND(itemTotal(item)) }}
                                    </td>
                                    <td class="py-2">
                                        <button type="button" @click="removeItem(i)" :disabled="form.items.length === 1"
                                            class="text-red-400 hover:text-red-600 disabled:opacity-30 transition-colors">
                                            <Trash2 :size="14" />
                                        </button>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>

                    <!-- Totals -->
                    <div class="mt-4 flex justify-end">
                        <div class="w-64 space-y-2 text-sm">
                            <div class="flex justify-between text-gray-600">
                                <span>Tạm tính:</span>
                                <span>{{ formatVND(subtotal) }}</span>
                            </div>
                            <div class="flex justify-between items-center text-gray-600">
                                <span>Thuế:</span>
                                <input v-model.number="form.tax_amount" type="number" min="0"
                                    class="w-28 rounded border border-gray-200 px-2 py-1 text-right text-xs focus:outline-none focus:ring-1 focus:ring-indigo-500" />
                            </div>
                            <div class="flex justify-between items-center text-gray-600">
                                <span>Chiết khấu:</span>
                                <input v-model.number="form.discount_amount" type="number" min="0"
                                    class="w-28 rounded border border-gray-200 px-2 py-1 text-right text-xs focus:outline-none focus:ring-1 focus:ring-indigo-500" />
                            </div>
                            <div class="flex justify-between font-bold text-gray-900 border-t border-gray-200 pt-2">
                                <span>Tổng cộng:</span>
                                <span class="text-indigo-600">{{ formatVND(grandTotal) }}</span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Submit -->
                <div class="flex gap-3 justify-end">
                    <button type="button" @click="router.visit('/admin/purchase-invoices')"
                        class="rounded-lg border border-gray-300 px-5 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors">
                        Hủy
                    </button>
                    <button type="submit" :disabled="form.processing"
                        class="rounded-lg bg-indigo-600 px-5 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50 transition-colors">
                        {{ form.processing ? 'Đang lưu...' : 'Tạo hóa đơn' }}
                    </button>
                </div>
            </form>
        </div>
    </AdminLayout>
</template>
