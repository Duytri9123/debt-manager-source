<script setup>
import AdminLayout from '@/Layouts/AdminLayout.vue'
import { useForm, router } from '@inertiajs/vue3'
import { computed } from 'vue'
import { ArrowLeft, Plus, Trash2, GripVertical } from 'lucide-vue-next'

const props = defineProps({ order: Object, customers: Array })

// Restore items từ order
const restoredItems = (props.order.items ?? []).map((item, i) => ({
    description:   item.product_name,
    product_code:  item.variant_sku,
    origin:        item.origin ?? '',
    unit:          item.unit ?? '',
    quantity:      Number(item.quantity),
    unit_price:    Number(item.price),
    line_total:    Number(item.price) * Number(item.quantity),
    note:          item.variant_attributes?.note ?? '',
    cost_price:    Number(item.cost_price ?? 0),
    selling_price: Number(item.selling_price ?? 0),
    business_pct:  Number(item.business_pct ?? 0),
    profit_per_kg: Number(item.profit_per_kg ?? 0),
    weight_kg:     Number(item.weight_kg ?? 0),
    total_profit:  Number(item.total_profit ?? 0),
    _key:          Date.now() + i,
}))

const form = useForm({
    customer_name: props.order.customer_name,
    order_date:    props.order.created_at?.slice(0, 10) ?? new Date().toISOString().slice(0, 10),
    notes:         props.order.notes ?? '',
    items:         restoredItems,
})

function addRow() {
    form.items.push({
        description: '', product_code: '', origin: 'VN', unit: '',
        quantity: 1, unit_price: 0, line_total: 0, note: '',
        cost_price: 0, selling_price: 0, business_pct: 0,
        profit_per_kg: 0, weight_kg: 0, total_profit: 0,
        _key: Date.now() + Math.random(),
    })
}

function removeRow(idx) { form.items.splice(idx, 1) }

function recalcRow(item) {
    item.line_total   = Math.round(item.unit_price * item.quantity)
    item.business_pct = item.selling_price > 0
        ? Math.round((item.selling_price - item.cost_price) * item.quantity)
        : 0
    item.total_profit = item.profit_per_kg > 0 && item.weight_kg > 0
        ? Math.round(item.profit_per_kg * item.weight_kg)
        : item.business_pct
}

const subtotal    = computed(() => form.items.reduce((s, i) => s + Number(i.line_total || 0), 0))
const tax         = computed(() => Math.round(subtotal.value * 0.1))
const grandTotal  = computed(() => subtotal.value + tax.value)
const totalProfit = computed(() => form.items.reduce((s, i) => s + Number(i.total_profit || 0), 0))

function fmt(v) { return Number(v || 0).toLocaleString('vi-VN') }

function submit() {
    form.put(`/admin/b2b-orders/${props.order.id}`)
}
</script>

<template>
    <AdminLayout>
        <div class="space-y-4">
            <div class="flex items-center gap-3">
                <button @click="router.visit(`/admin/b2b-orders/${order.id}`)"
                    class="p-2 rounded-lg hover:bg-gray-100 transition-colors">
                    <ArrowLeft :size="18" class="text-gray-600" />
                </button>
                <div>
                    <h1 class="text-xl font-bold text-gray-900">Chỉnh sửa: {{ order.order_number }}</h1>
                    <p class="text-sm text-gray-500">{{ order.customer_name }}</p>
                </div>
            </div>

            <form @submit.prevent="submit" class="space-y-4">
                <!-- Order info -->
                <div class="bg-white rounded-xl border border-gray-200 p-4 shadow-sm">
                    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">Khách hàng <span class="text-red-500">*</span></label>
                            <input v-model="form.customer_name" list="customer-list" required
                                class="w-full rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                                :class="form.errors.customer_name ? 'border-red-400' : 'border-gray-300'" />
                            <datalist id="customer-list">
                                <option v-for="c in customers" :key="c.id" :value="c.name" />
                            </datalist>
                        </div>
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">Ngày đặt <span class="text-red-500">*</span></label>
                            <input v-model="form.order_date" type="date" required
                                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                        </div>
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">Ghi chú</label>
                            <input v-model="form.notes"
                                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                        </div>
                    </div>
                </div>

                <!-- Items table -->
                <div class="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
                    <div class="px-4 py-3 border-b border-gray-100 bg-gray-50 flex items-center justify-between">
                        <h2 class="font-semibold text-gray-800">Chi tiết sản phẩm</h2>
                        <button type="button" @click="addRow"
                            class="flex items-center gap-1.5 text-sm text-indigo-600 hover:text-indigo-800 font-medium">
                            <Plus :size="15" /> Thêm dòng
                        </button>
                    </div>

                    <div class="overflow-x-auto">
                        <table class="w-full text-xs">
                            <thead class="bg-yellow-50 border-b border-yellow-200">
                                <tr>
                                    <th class="px-2 py-2 w-6"></th>
                                    <th class="px-2 py-2 w-6 text-gray-600">TT</th>
                                    <th class="px-2 py-2 text-left font-semibold text-gray-700 min-w-[180px]">Mô tả chi tiết *</th>
                                    <th class="px-2 py-2 text-left font-semibold text-gray-700 w-24">Mã hàng</th>
                                    <th class="px-2 py-2 text-left font-semibold text-gray-700 w-16">Xuất xứ</th>
                                    <th class="px-2 py-2 text-left font-semibold text-gray-700 w-16">Đơn vị</th>
                                    <th class="px-2 py-2 text-right font-semibold text-gray-700 w-20">Số lượng</th>
                                    <th class="px-2 py-2 text-right font-semibold text-gray-700 w-28">Đơn giá</th>
                                    <th class="px-2 py-2 text-right font-semibold text-gray-700 w-28">Thành tiền</th>
                                    <th class="px-2 py-2 text-left font-semibold text-gray-700 w-28">Ghi chú</th>
                                    <th class="px-2 py-2 text-right font-semibold text-blue-700 w-28 bg-blue-50">Đầu vào</th>
                                    <th class="px-2 py-2 text-right font-semibold text-blue-700 w-28 bg-blue-50">Giá bán</th>
                                    <th class="px-2 py-2 text-right font-semibold text-orange-700 w-28 bg-orange-50">% KD</th>
                                    <th class="px-2 py-2 text-right font-semibold text-orange-700 w-24 bg-orange-50">Lãi/1KG</th>
                                    <th class="px-2 py-2 text-right font-semibold text-orange-700 w-24 bg-orange-50">KL (KG)</th>
                                    <th class="px-2 py-2 text-right font-semibold text-orange-700 w-28 bg-orange-50">Lãi tổng KL</th>
                                    <th class="px-2 py-2 w-8"></th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-gray-100">
                                <tr v-for="(item, idx) in form.items" :key="item._key" class="hover:bg-gray-50">
                                    <td class="px-2 py-1.5 text-gray-300 cursor-grab"><GripVertical :size="12" /></td>
                                    <td class="px-2 py-1.5 text-gray-400 text-center">{{ idx + 1 }}</td>
                                    <td class="px-2 py-1.5">
                                        <textarea v-model="item.description" rows="2" required
                                            class="w-full rounded border border-gray-200 px-2 py-1 text-xs focus:outline-none focus:ring-1 focus:ring-indigo-400 resize-none min-w-[180px]" />
                                    </td>
                                    <td class="px-2 py-1.5">
                                        <input v-model="item.product_code"
                                            class="w-full rounded border border-gray-200 px-2 py-1 text-xs focus:outline-none focus:ring-1 focus:ring-indigo-400" />
                                    </td>
                                    <td class="px-2 py-1.5">
                                        <input v-model="item.origin"
                                            class="w-full rounded border border-gray-200 px-2 py-1 text-xs focus:outline-none focus:ring-1 focus:ring-indigo-400" />
                                    </td>
                                    <td class="px-2 py-1.5">
                                        <input v-model="item.unit"
                                            class="w-full rounded border border-gray-200 px-2 py-1 text-xs focus:outline-none focus:ring-1 focus:ring-indigo-400" />
                                    </td>
                                    <td class="px-2 py-1.5">
                                        <input v-model.number="item.quantity" type="number" min="0" step="0.01"
                                            @input="recalcRow(item)"
                                            class="w-full rounded border border-gray-200 px-2 py-1 text-xs text-right focus:outline-none focus:ring-1 focus:ring-indigo-400" />
                                    </td>
                                    <td class="px-2 py-1.5">
                                        <input v-model.number="item.unit_price" type="number" min="0"
                                            @input="recalcRow(item)"
                                            class="w-full rounded border border-gray-200 px-2 py-1 text-xs text-right focus:outline-none focus:ring-1 focus:ring-indigo-400" />
                                    </td>
                                    <td class="px-2 py-1.5 text-right font-semibold text-gray-800">{{ fmt(item.line_total) }}</td>
                                    <td class="px-2 py-1.5">
                                        <input v-model="item.note"
                                            class="w-full rounded border border-gray-200 px-2 py-1 text-xs focus:outline-none focus:ring-1 focus:ring-indigo-400" />
                                    </td>
                                    <td class="px-2 py-1.5 bg-blue-50/30">
                                        <input v-model.number="item.cost_price" type="number" min="0"
                                            @input="recalcRow(item)"
                                            class="w-full rounded border border-blue-200 px-2 py-1 text-xs text-right focus:outline-none focus:ring-1 focus:ring-blue-400" />
                                    </td>
                                    <td class="px-2 py-1.5 bg-blue-50/30">
                                        <input v-model.number="item.selling_price" type="number" min="0"
                                            @input="recalcRow(item)"
                                            class="w-full rounded border border-blue-200 px-2 py-1 text-xs text-right focus:outline-none focus:ring-1 focus:ring-blue-400" />
                                    </td>
                                    <td class="px-2 py-1.5 text-right text-orange-600 bg-orange-50/30 font-medium">{{ fmt(item.business_pct) }}</td>
                                    <td class="px-2 py-1.5 bg-orange-50/30">
                                        <input v-model.number="item.profit_per_kg" type="number" min="0"
                                            @input="recalcRow(item)"
                                            class="w-full rounded border border-orange-200 px-2 py-1 text-xs text-right focus:outline-none focus:ring-1 focus:ring-orange-400" />
                                    </td>
                                    <td class="px-2 py-1.5 bg-orange-50/30">
                                        <input v-model.number="item.weight_kg" type="number" min="0" step="0.001"
                                            @input="recalcRow(item)"
                                            class="w-full rounded border border-orange-200 px-2 py-1 text-xs text-right focus:outline-none focus:ring-1 focus:ring-orange-400" />
                                    </td>
                                    <td class="px-2 py-1.5 text-right font-semibold text-orange-700 bg-orange-50/30">{{ fmt(item.total_profit) }}</td>
                                    <td class="px-2 py-1.5">
                                        <button type="button" @click="removeRow(idx)"
                                            class="p-1 rounded hover:bg-red-50 text-red-400 transition-colors">
                                            <Trash2 :size="12" />
                                        </button>
                                    </td>
                                </tr>
                            </tbody>
                            <tfoot class="border-t-2 border-gray-300 bg-gray-50">
                                <tr>
                                    <td colspan="8" class="px-3 py-2 text-right font-semibold text-gray-700 text-xs">Tổng trước thuế:</td>
                                    <td class="px-3 py-2 text-right font-bold text-gray-900 text-xs">{{ fmt(subtotal) }}đ</td>
                                    <td colspan="6"></td>
                                    <td class="px-3 py-2 text-right font-bold text-orange-700 text-xs">{{ fmt(totalProfit) }}đ</td>
                                    <td></td>
                                </tr>
                                <tr>
                                    <td colspan="8" class="px-3 py-2 text-right text-gray-500 text-xs">Thuế GTGT 10%:</td>
                                    <td class="px-3 py-2 text-right text-gray-700 text-xs">{{ fmt(tax) }}đ</td>
                                    <td colspan="8"></td>
                                </tr>
                                <tr class="bg-indigo-50">
                                    <td colspan="8" class="px-3 py-2 text-right font-bold text-indigo-700 text-xs">Tổng sau thuế:</td>
                                    <td class="px-3 py-2 text-right font-bold text-indigo-700 text-sm">{{ fmt(grandTotal) }}đ</td>
                                    <td colspan="8"></td>
                                </tr>
                            </tfoot>
                        </table>
                    </div>
                </div>

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
