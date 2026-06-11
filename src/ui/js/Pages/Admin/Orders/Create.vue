<script setup>
import AdminLayout from '@/Layouts/AdminLayout.vue'
import { useForm, router } from '@inertiajs/vue3'
import { ref, computed, watch } from 'vue'
import { ArrowLeft, Plus, Trash2, Search } from 'lucide-vue-next'

const props = defineProps({
    customers: Array,
    products:  Array,
})

const form = useForm({
    user_id:          '',
    customer_name:    '',
    customer_email:   '',
    customer_phone:   '',
    shipping_address: '',
    notes:            '',
    status:           'pending',
    payment_status:   'unpaid',
    items:            [],
})

// Khi chọn khách hàng → tự điền thông tin
function selectCustomer(c) {
    form.user_id       = c.id
    form.customer_name = c.name
    form.customer_email = c.email ?? ''
    form.customer_phone = c.phone ?? ''
    customerSearch.value = c.name
    showCustomerDrop.value = false
}

const customerSearch    = ref('')
const showCustomerDrop  = ref(false)
const filteredCustomers = computed(() => {
    if (!customerSearch.value) return props.customers?.slice(0, 10) ?? []
    const q = customerSearch.value.toLowerCase()
    return (props.customers ?? []).filter(c =>
        c.name.toLowerCase().includes(q) || (c.phone ?? '').includes(q)
    ).slice(0, 10)
})

// Thêm sản phẩm
const productSearch   = ref('')
const showProductDrop = ref(false)
const filteredProducts = computed(() => {
    if (!productSearch.value) return props.products?.slice(0, 10) ?? []
    const q = productSearch.value.toLowerCase()
    return (props.products ?? []).filter(p => p.name.toLowerCase().includes(q)).slice(0, 10)
})

function addProduct(p) {
    form.items.push({
        product_name: p.name,
        variant_sku:  p.default_variant?.sku ?? 'SKU-' + p.id,
        price:        Number(p.default_variant?.selling_price ?? 0),
        quantity:     1,
        _key:         Date.now() + Math.random(),
    })
    productSearch.value  = ''
    showProductDrop.value = false
}

function addManualRow() {
    form.items.push({
        product_name: '',
        variant_sku:  '',
        price:        0,
        quantity:     1,
        _key:         Date.now() + Math.random(),
    })
}

function removeRow(idx) { form.items.splice(idx, 1) }

const subtotal   = computed(() => form.items.reduce((s, i) => s + Number(i.price) * Number(i.quantity), 0))
const grandTotal = computed(() => subtotal.value)

function fmt(v) { return Number(v || 0).toLocaleString('vi-VN') + 'đ' }

function submit() {
    form.post('/admin/orders')
}
</script>

<template>
    <AdminLayout>
        <div class="space-y-5 max-w-4xl">
            <!-- Header -->
            <div class="flex items-center gap-3">
                <button @click="router.visit('/admin/orders')"
                    class="p-2 rounded-lg hover:bg-gray-100 transition-colors">
                    <ArrowLeft :size="18" class="text-gray-600" />
                </button>
                <div>
                    <h1 class="text-xl font-bold text-gray-900">Tạo đơn hàng mới</h1>
                    <p class="text-sm text-gray-500">Tạo đơn hàng thủ công cho khách hàng</p>
                </div>
            </div>

            <form @submit.prevent="submit" class="space-y-5">
                <div class="grid grid-cols-1 lg:grid-cols-3 gap-5">

                    <!-- Left: Items -->
                    <div class="lg:col-span-2 space-y-4">

                        <!-- Add product -->
                        <div class="bg-white rounded-xl border border-gray-200 p-4 shadow-sm space-y-3">
                            <h2 class="font-semibold text-gray-800">Sản phẩm</h2>
                            <div class="flex gap-2">
                                <div class="flex-1 relative">
                                    <Search :size="14" class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                                    <input v-model="productSearch"
                                        @focus="showProductDrop = true"
                                        @blur="setTimeout(() => showProductDrop = false, 200)"
                                        placeholder="Tìm sản phẩm..."
                                        class="w-full pl-9 pr-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                                    <div v-if="showProductDrop && filteredProducts.length"
                                        class="absolute z-20 top-full left-0 right-0 mt-1 bg-white border border-gray-200 rounded-xl shadow-lg max-h-48 overflow-y-auto">
                                        <button v-for="p in filteredProducts" :key="p.id"
                                            type="button"
                                            @mousedown.prevent="addProduct(p)"
                                            class="w-full text-left px-3 py-2 hover:bg-indigo-50 text-sm transition-colors">
                                            <span class="font-medium text-gray-800">{{ p.name }}</span>
                                        </button>
                                    </div>
                                </div>
                                <button type="button" @click="addManualRow"
                                    class="flex items-center gap-1.5 px-3 py-2 text-sm border border-gray-200 rounded-lg hover:bg-gray-50 text-gray-600 transition-colors">
                                    <Plus :size="14" /> Thêm thủ công
                                </button>
                            </div>

                            <!-- Items list -->
                            <div v-if="form.items.length" class="space-y-2">
                                <div v-for="(item, idx) in form.items" :key="item._key"
                                    class="grid grid-cols-12 gap-2 items-center bg-gray-50 rounded-lg p-2">
                                    <div class="col-span-5">
                                        <input v-model="item.product_name" placeholder="Tên sản phẩm *" required
                                            class="w-full rounded border border-gray-200 px-2 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-indigo-400" />
                                    </div>
                                    <div class="col-span-2">
                                        <input v-model="item.variant_sku" placeholder="SKU" required
                                            class="w-full rounded border border-gray-200 px-2 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-indigo-400" />
                                    </div>
                                    <div class="col-span-2">
                                        <input v-model.number="item.price" type="number" min="0" placeholder="Giá"
                                            class="w-full rounded border border-gray-200 px-2 py-1.5 text-sm text-right focus:outline-none focus:ring-1 focus:ring-indigo-400" />
                                    </div>
                                    <div class="col-span-2">
                                        <div class="flex items-center gap-1">
                                            <button type="button" @click="item.quantity = Math.max(1, item.quantity - 1)"
                                                class="w-6 h-6 rounded border border-gray-200 flex items-center justify-center text-gray-500 hover:bg-gray-100 text-sm">−</button>
                                            <input v-model.number="item.quantity" type="number" min="1"
                                                class="w-10 text-center text-sm border border-gray-200 rounded py-1 focus:outline-none focus:ring-1 focus:ring-indigo-400" />
                                            <button type="button" @click="item.quantity++"
                                                class="w-6 h-6 rounded border border-gray-200 flex items-center justify-center text-gray-500 hover:bg-gray-100 text-sm">+</button>
                                        </div>
                                    </div>
                                    <div class="col-span-1 flex justify-end">
                                        <button type="button" @click="removeRow(idx)"
                                            class="p-1 rounded hover:bg-red-50 text-red-400 transition-colors">
                                            <Trash2 :size="14" />
                                        </button>
                                    </div>
                                </div>
                            </div>

                            <div v-else class="text-center py-6 text-sm text-gray-400">
                                Tìm sản phẩm hoặc thêm thủ công
                            </div>

                            <!-- Total -->
                            <div v-if="form.items.length" class="border-t border-gray-200 pt-3 flex justify-between items-center">
                                <span class="text-sm font-semibold text-gray-700">Tổng cộng:</span>
                                <span class="text-base font-bold text-indigo-600">{{ fmt(grandTotal) }}</span>
                            </div>
                        </div>

                        <p v-if="form.errors.items" class="text-sm text-red-500">{{ form.errors.items }}</p>
                    </div>

                    <!-- Right: Info -->
                    <div class="space-y-4">
                        <!-- Customer -->
                        <div class="bg-white rounded-xl border border-gray-200 p-4 shadow-sm space-y-3">
                            <h2 class="font-semibold text-gray-800">Khách hàng</h2>

                            <!-- Search customer -->
                            <div class="relative">
                                <Search :size="14" class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                                <input v-model="customerSearch"
                                    @focus="showCustomerDrop = true"
                                    @blur="setTimeout(() => showCustomerDrop = false, 200)"
                                    placeholder="Tìm khách hàng..."
                                    class="w-full pl-9 pr-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                                <div v-if="showCustomerDrop && filteredCustomers.length"
                                    class="absolute z-20 top-full left-0 right-0 mt-1 bg-white border border-gray-200 rounded-xl shadow-lg max-h-48 overflow-y-auto">
                                    <button v-for="c in filteredCustomers" :key="c.id"
                                        type="button"
                                        @mousedown.prevent="selectCustomer(c)"
                                        class="w-full text-left px-3 py-2 hover:bg-indigo-50 transition-colors">
                                        <p class="text-sm font-medium text-gray-800">{{ c.name }}</p>
                                        <p class="text-xs text-gray-400">{{ c.phone || c.email }}</p>
                                    </button>
                                </div>
                            </div>

                            <input v-model="form.customer_name" placeholder="Tên khách hàng *" required
                                class="w-full rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                                :class="form.errors.customer_name ? 'border-red-400' : 'border-gray-300'" />

                            <input v-model="form.customer_phone" placeholder="Số điện thoại"
                                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />

                            <input v-model="form.customer_email" type="email" placeholder="Email"
                                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />

                            <textarea v-model="form.shipping_address" rows="2" placeholder="Địa chỉ giao hàng"
                                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none" />
                        </div>

                        <!-- Status -->
                        <div class="bg-white rounded-xl border border-gray-200 p-4 shadow-sm space-y-3">
                            <h2 class="font-semibold text-gray-800">Trạng thái</h2>
                            <select v-model="form.status"
                                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                                <option value="pending">⏳ Chờ xác nhận</option>
                                <option value="processing">🔄 Đang xử lý</option>
                                <option value="shipped">🚚 Đang giao</option>
                                <option value="delivered">✅ Đã giao</option>
                                <option value="cancelled">❌ Đã hủy</option>
                            </select>
                            <select v-model="form.payment_status"
                                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                                <option value="unpaid">💳 Chưa thanh toán</option>
                                <option value="paid">✅ Đã thanh toán</option>
                            </select>
                            <textarea v-model="form.notes" rows="2" placeholder="Ghi chú đơn hàng..."
                                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none" />
                        </div>

                        <!-- Actions -->
                        <div class="flex flex-col gap-2">
                            <button type="submit"
                                :disabled="form.processing || !form.items.length || !form.customer_name"
                                class="w-full py-2.5 rounded-lg bg-indigo-600 text-white text-sm font-medium hover:bg-indigo-700 disabled:opacity-50 transition-colors">
                                {{ form.processing ? 'Đang tạo...' : '✓ Tạo đơn hàng' }}
                            </button>
                            <button type="button" @click="router.visit('/admin/orders')"
                                class="w-full py-2.5 rounded-lg border border-gray-300 text-gray-700 text-sm hover:bg-gray-50 transition-colors">
                                Hủy
                            </button>
                        </div>
                    </div>
                </div>
            </form>
        </div>
    </AdminLayout>
</template>
