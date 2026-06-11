<script setup>
import AdminLayout from '@/Layouts/AdminLayout.vue'
import { useForm, router } from '@inertiajs/vue3'
import { computed, ref, watch } from 'vue'

const props = defineProps({
    orders: Array,
})

const form = useForm({
    order_id:        '',
    original_amount: '',
    notes:           '',
    due_date:        '',
})

// Khi chọn order, tự điền số tiền từ grand_total
const selectedOrder = computed(() =>
    props.orders.find(o => o.id == form.order_id)
)

watch(() => form.order_id, (id) => {
    const order = props.orders.find(o => o.id == id)
    if (order) {
        form.original_amount = order.grand_total
    }
})

function formatVND(v) {
    return Number(v).toLocaleString('vi-VN', { style: 'currency', currency: 'VND' })
}

function submit() {
    form.post('/admin/debts')
}
</script>

<template>
    <AdminLayout>
        <div class="space-y-6">
            <!-- Header -->
            <div class="flex items-center gap-3">
                <button @click="router.visit('/admin/debts')"
                    class="text-gray-500 hover:text-gray-700 text-sm transition-colors">
                    ← Quay lại
                </button>
                <h1 class="text-xl font-bold text-gray-900">Tạo công nợ mới</h1>
            </div>

            <form @submit.prevent="submit" class="space-y-5">
                <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 space-y-5">
                    <h2 class="font-semibold text-gray-900">Thông tin công nợ</h2>

                    <!-- Order select -->
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">
                            Đơn hàng <span class="text-red-500">*</span>
                        </label>
                        <select v-model="form.order_id"
                            class="w-full rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                            :class="form.errors.order_id ? 'border-red-400' : 'border-gray-300'">
                            <option value="">— Chọn đơn hàng chưa có công nợ —</option>
                            <option v-for="order in orders" :key="order.id" :value="order.id">
                                {{ order.order_number }} — {{ order.customer_name }} ({{ formatVND(order.grand_total) }})
                            </option>
                        </select>
                        <p v-if="form.errors.order_id" class="mt-1 text-xs text-red-500">{{ form.errors.order_id }}</p>
                        <p v-if="!orders.length" class="mt-1 text-xs text-amber-600">
                            Tất cả đơn hàng đã có công nợ hoặc chưa có đơn hàng nào.
                        </p>
                    </div>

                    <!-- Selected order info -->
                    <div v-if="selectedOrder"
                        class="rounded-lg bg-indigo-50 border border-indigo-200 p-4 text-sm space-y-1">
                        <p class="font-medium text-indigo-900">{{ selectedOrder.order_number }}</p>
                        <p class="text-indigo-700">Khách hàng: {{ selectedOrder.customer_name }}</p>
                        <p class="text-indigo-700">Giá trị đơn: <span class="font-semibold">{{ formatVND(selectedOrder.grand_total) }}</span></p>
                    </div>

                    <!-- Original amount -->
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">
                            Số tiền công nợ <span class="text-red-500">*</span>
                        </label>
                        <div class="relative">
                            <input v-model.number="form.original_amount" type="number" min="0.01" step="1000"
                                placeholder="0"
                                class="w-full rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 pr-12"
                                :class="form.errors.original_amount ? 'border-red-400' : 'border-gray-300'" />
                            <span class="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-gray-400">VNĐ</span>
                        </div>
                        <p v-if="form.original_amount" class="mt-1 text-xs text-gray-500">
                            = {{ formatVND(form.original_amount) }}
                        </p>
                        <p v-if="form.errors.original_amount" class="mt-1 text-xs text-red-500">{{ form.errors.original_amount }}</p>
                    </div>

                    <!-- Due date -->
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Ngày đến hạn</label>
                        <input v-model="form.due_date" type="date"
                            class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                    </div>

                    <!-- Notes -->
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Ghi chú</label>
                        <textarea v-model="form.notes" rows="3"
                            placeholder="Ghi chú về công nợ này..."
                            class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none" />
                    </div>
                </div>

                <!-- Actions -->
                <div class="flex gap-3 justify-end">
                    <button type="button" @click="router.visit('/admin/debts')"
                        class="rounded-lg border border-gray-300 px-5 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors">
                        Hủy
                    </button>
                    <button type="submit" :disabled="form.processing || !form.order_id || !form.original_amount"
                        class="rounded-lg bg-indigo-600 px-5 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50 transition-colors">
                        {{ form.processing ? 'Đang tạo...' : 'Tạo công nợ' }}
                    </button>
                </div>
            </form>
        </div>
    </AdminLayout>
</template>
