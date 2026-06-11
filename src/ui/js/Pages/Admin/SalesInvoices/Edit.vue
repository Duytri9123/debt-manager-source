<script setup>
import AdminLayout from '@/Layouts/AdminLayout.vue'
import { useForm, router } from '@inertiajs/vue3'
import { computed } from 'vue'
import { Plus, Trash2 } from 'lucide-vue-next'

const props = defineProps({
    invoice: Object,
    customers: Array,
    orders: Array,
    products: Array,
})

const form = useForm({
    customer_id: props.invoice.customer_id ?? '',
    order_id: props.invoice.order_id ?? '',
    invoice_date: props.invoice.invoice_date ?? new Date().toISOString().split('T')[0],
    due_date: props.invoice.due_date ?? '',
    status: props.invoice.status ?? 'draft',
    notes: props.invoice.notes ?? '',
    items: props.invoice.items?.length
        ? props.invoice.items.map(i => ({
            product_id: i.product_id ?? null,
            product_name: i.product_name ?? '',
            unit: i.unit ?? '',
            quantity: i.quantity ?? 1,
            unit_price: i.unit_price ?? 0,
            tax_rate: i.tax_rate ?? 0,
            discount_rate: i.discount_rate ?? 0,
          }))
        : [{ product_id: null, product_name: '', unit: '', quantity: 1, unit_price: 0, tax_rate: 0, discount_rate: 0 }],
})

function addItem() {
    form.items.push({ product_id: null, product_name: '', unit: '', quantity: 1, unit_price: 0, tax_rate: 0, discount_rate: 0 })
}

function removeItem(i) {
    form.items.splice(i, 1)
}

function onProductSelect(i, productId) {
    const product = props.products?.find(p => p.id == productId)
    if (product) {
        form.items[i].product_id = product.id
        form.items[i].product_name = product.name
        const variant = product.variants?.[0]
        if (variant) {
            form.items[i].unit = variant.unit ?? ''
            form.items[i].unit_price = variant.selling_price ?? 0
        }
    }
}

function itemTotal(item) {
    const base = item.quantity * item.unit_price
    const afterDisc = base * (1 - item.discount_rate / 100)
    return afterDisc * (1 + item.tax_rate / 100)
}

const subtotal = computed(() => form.items.reduce((s, i) => s + i.quantity * i.unit_price, 0))
const totalTax = computed(() => form.items.reduce((s, i) => s + (i.quantity * i.unit_price * i.tax_rate / 100), 0))
const totalDiscount = computed(() => form.items.reduce((s, i) => s + (i.quantity * i.unit_price * i.discount_rate / 100), 0))
const grandTotal = computed(() => form.items.reduce((s, i) => s + itemTotal(i), 0))

function formatVND(v) { return Number(v).toLocaleString('vi-VN', { style: 'currency', currency: 'VND' }) }

function submit() {
    form.put('/admin/sales-invoices/' + props.invoice.id)
}
</script>

<template>
    <AdminLayout>
        <div class="space-y-6">
            <!-- Header -->
            <div class="flex items-center gap-3">
                <button @click="router.visit('/admin/sales-invoices/' + invoice.id)" class="text-gray-500 hover:text-gray-700 text-sm">← Quay lại</button>
                <h1 class="text-xl font-bold text-gray-900">Chỉnh sửa hóa đơn</h1>
            </div>

            <form @submit.prevent="submit" class="space-y-6">
                <!-- General info -->
                <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                    <h2 class="font-semibold text-gray-900 mb-4">Thông tin chung</h2>
                    <div class="grid grid-cols-2 gap-4">
                        <!-- Customer -->
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">
                                Khách hàng <span class="text-red-500">*</span>
                            </label>
                            <select v-model="form.customer_id"
                                class="w-full rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                                :class="form.errors.customer_id ? 'border-red-400' : 'border-gray-300'">
                                <option value="">— Chọn khách hàng —</option>
                                <option v-for="c in customers" :key="c.id" :value="c.id">{{ c.name }}</option>
                            </select>
                            <p v-if="form.errors.customer_id" class="mt-1 text-xs text-red-500">{{ form.errors.customer_id }}</p>
                        </div>

                        <!-- Order (optional) -->
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">Đơn hàng (tùy chọn)</label>
                            <select v-model="form.order_id"
                                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                                <option value="">— Không liên kết —</option>
                                <option v-for="o in orders" :key="o.id" :value="o.id">{{ o.order_number ?? '#' + o.id }}</option>
                            </select>
                        </div>

                        <!-- Invoice date -->
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">
                                Ngày hóa đơn <span class="text-red-500">*</span>
                            </label>
                            <input v-model="form.invoice_date" type="date"
                                class="w-full rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                                :class="form.errors.invoice_date ? 'border-red-400' : 'border-gray-300'" />
                            <p v-if="form.errors.invoice_date" class="mt-1 text-xs text-red-500">{{ form.errors.invoice_date }}</p>
                        </div>

                        <!-- Due date -->
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">Hạn thanh toán</label>
                            <input v-model="form.due_date" type="date"
                                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                        </div>

                        <!-- Status -->
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">Trạng thái</label>
                            <select v-model="form.status"
                                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                                <option value="draft">Nháp</option>
                                <option value="issued">Đã xuất</option>
                                <option value="cancelled">Đã hủy</option>
                            </select>
                        </div>

                        <!-- Notes -->
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
                                    <th class="text-left pb-2 font-medium text-gray-600 w-44">Sản phẩm</th>
                                    <th class="text-left pb-2 font-medium text-gray-600 w-28">Tên hàng</th>
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
                                        <select :value="item.product_id" @change="e => onProductSelect(i, e.target.value)"
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

                    <!-- Totals summary -->
                    <div class="mt-4 flex justify-end">
                        <div class="w-64 space-y-2 text-sm">
                            <div class="flex justify-between text-gray-600">
                                <span>Tạm tính:</span>
                                <span>{{ formatVND(subtotal) }}</span>
                            </div>
                            <div class="flex justify-between text-gray-600">
                                <span>Thuế:</span>
                                <span>{{ formatVND(totalTax) }}</span>
                            </div>
                            <div class="flex justify-between text-gray-600">
                                <span>Chiết khấu:</span>
                                <span>-{{ formatVND(totalDiscount) }}</span>
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
                    <button type="button" @click="router.visit('/admin/sales-invoices/' + invoice.id)"
                        class="rounded-lg border border-gray-300 px-5 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors">
                        Hủy
                    </button>
                    <button type="submit" :disabled="form.processing"
                        class="rounded-lg bg-indigo-600 px-5 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50 transition-colors">
                        {{ form.processing ? 'Đang lưu...' : 'Lưu thay đổi' }}
                    </button>
                </div>
            </form>
        </div>
    </AdminLayout>
</template>
