<script setup>
import AdminLayout from '@/Layouts/AdminLayout.vue'
import { router, Link } from '@inertiajs/vue3'
import { ref } from 'vue'
import { ArrowLeft, Package, User, MapPin, CreditCard, RefreshCw } from 'lucide-vue-next'

const props = defineProps({ order: Object })

const statusOptions = [
    { value: 'pending',    label: '⏳ Chờ xác nhận' },
    { value: 'processing', label: '🔄 Đang xử lý' },
    { value: 'shipped',    label: '🚚 Đang giao hàng' },
    { value: 'delivered',  label: '✅ Đã giao hàng' },
    { value: 'cancelled',  label: '❌ Đã hủy' },
]
const paymentOptions = [
    { value: 'unpaid', label: '💳 Chưa thanh toán' },
    { value: 'paid',   label: '✅ Đã thanh toán' },
]

const newStatus        = ref(props.order.status)
const newPaymentStatus = ref(props.order.payment_status)
const updating         = ref(false)

const statusColors = {
    pending: 'bg-yellow-100 text-yellow-700', processing: 'bg-blue-100 text-blue-700',
    shipped: 'bg-indigo-100 text-indigo-700', delivered: 'bg-green-100 text-green-700',
    cancelled: 'bg-red-100 text-red-700',
}

function updateStatus() {
    updating.value = true
    router.patch(`/admin/orders/${props.order.id}/status`, {
        status:         newStatus.value,
        payment_status: newPaymentStatus.value,
    }, { onFinish: () => { updating.value = false } })
}

function formatMoney(v) { return Number(v || 0).toLocaleString('vi-VN') + 'đ' }
function formatDate(d)  { return new Date(d).toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' }) }

function getVariantLabel(item) {
    if (!item.variant_attributes) return item.variant_sku
    try {
        const attrs = typeof item.variant_attributes === 'string'
            ? JSON.parse(item.variant_attributes) : item.variant_attributes
        return Object.values(attrs).join(' / ')
    } catch { return item.variant_sku }
}
</script>

<template>
    <AdminLayout>
        <div class="space-y-5 max-w-5xl">
            <!-- Header -->
            <div class="flex items-center gap-3">
                <Link href="/admin/orders" class="p-2 rounded-lg hover:bg-gray-100 transition-colors">
                    <ArrowLeft :size="18" class="text-gray-600" />
                </Link>
                <div>
                    <h1 class="text-xl font-bold text-gray-900">Đơn hàng {{ order.order_number }}</h1>
                    <p class="text-sm text-gray-500">{{ formatDate(order.created_at) }}</p>
                </div>
                <span :class="['ml-auto px-3 py-1 rounded-full text-sm font-medium', statusColors[order.status] ?? 'bg-gray-100 text-gray-600']">
                    {{ statusOptions.find(s => s.value === order.status)?.label ?? order.status }}
                </span>
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-3 gap-5">
                <!-- Left: Items + Summary -->
                <div class="lg:col-span-2 space-y-4">
                    <!-- Order items -->
                    <div class="bg-white rounded-xl border border-gray-200 overflow-hidden">
                        <div class="flex items-center gap-2 px-4 py-3 border-b border-gray-100">
                            <Package :size="16" class="text-indigo-600" />
                            <h2 class="font-semibold text-gray-800">Sản phẩm đặt hàng</h2>
                            <span class="ml-auto text-xs text-gray-400">{{ order.items?.length }} sản phẩm</span>
                        </div>
                        <div class="divide-y divide-gray-100">
                            <div v-for="item in order.items" :key="item.id" class="flex items-center gap-3 px-4 py-3">
                                <!-- Thumbnail -->
                                <div class="w-12 h-12 rounded-lg bg-gray-100 overflow-hidden shrink-0">
                                    <img v-if="item.product_variant?.product?.thumbnail_image?.url"
                                        :src="item.product_variant.product.thumbnail_image.url"
                                        class="w-full h-full object-cover" />
                                    <Package v-else :size="20" class="m-auto mt-3 text-gray-300" />
                                </div>
                                <div class="flex-1 min-w-0">
                                    <p class="font-medium text-gray-800 truncate">{{ item.product_name }}</p>
                                    <p class="text-xs text-gray-400">{{ getVariantLabel(item) }}</p>
                                </div>
                                <div class="text-right shrink-0">
                                    <p class="font-semibold text-gray-800">{{ formatMoney(item.price) }}</p>
                                    <p class="text-xs text-gray-400">x{{ item.quantity ?? 1 }}</p>
                                </div>
                            </div>
                        </div>
                        <!-- Totals -->
                        <div class="border-t border-gray-100 px-4 py-3 space-y-1.5 bg-gray-50">
                            <div class="flex justify-between text-sm text-gray-600">
                                <span>Tạm tính</span><span>{{ formatMoney(order.subtotal) }}</span>
                            </div>
                            <div class="flex justify-between text-sm text-gray-600">
                                <span>Phí vận chuyển</span><span>{{ formatMoney(order.shipping_fee) }}</span>
                            </div>
                            <div v-if="order.discount_amount > 0" class="flex justify-between text-sm text-green-600">
                                <span>Giảm giá ({{ order.discount_code }})</span>
                                <span>-{{ formatMoney(order.discount_amount) }}</span>
                            </div>
                            <div class="flex justify-between font-bold text-gray-900 text-base pt-1 border-t border-gray-200">
                                <span>Tổng cộng</span><span class="text-indigo-600">{{ formatMoney(order.grand_total) }}</span>
                            </div>
                        </div>
                    </div>

                    <!-- Notes -->
                    <div v-if="order.notes" class="bg-amber-50 border border-amber-200 rounded-xl px-4 py-3">
                        <p class="text-xs font-medium text-amber-700 mb-1">Ghi chú của khách:</p>
                        <p class="text-sm text-amber-800">{{ order.notes }}</p>
                    </div>
                </div>

                <!-- Right: Info + Actions -->
                <div class="space-y-4">
                    <!-- Customer info -->
                    <div class="bg-white rounded-xl border border-gray-200 p-4 space-y-3">
                        <div class="flex items-center gap-2 mb-1">
                            <User :size="15" class="text-indigo-600" />
                            <h3 class="font-semibold text-gray-800 text-sm">Thông tin khách hàng</h3>
                        </div>
                        <div class="space-y-1.5 text-sm">
                            <p class="font-medium text-gray-800">{{ order.customer_name }}</p>
                            <p class="text-gray-500">{{ order.customer_email }}</p>
                            <p class="text-gray-500">{{ order.customer_phone }}</p>
                        </div>
                        <div class="pt-2 border-t border-gray-100">
                            <div class="flex items-start gap-1.5">
                                <MapPin :size="13" class="text-gray-400 mt-0.5 shrink-0" />
                                <p class="text-xs text-gray-500">{{ order.shipping_address }}</p>
                            </div>
                        </div>
                    </div>

                    <!-- Payment info -->
                    <div class="bg-white rounded-xl border border-gray-200 p-4 space-y-2">
                        <div class="flex items-center gap-2 mb-1">
                            <CreditCard :size="15" class="text-indigo-600" />
                            <h3 class="font-semibold text-gray-800 text-sm">Thanh toán</h3>
                        </div>
                        <p class="text-sm text-gray-600">{{ order.payment_method?.name ?? 'Không rõ' }}</p>
                        <span :class="['inline-flex px-2 py-0.5 rounded-full text-xs font-medium',
                            order.payment_status === 'paid' ? 'bg-green-100 text-green-700' : 'bg-orange-100 text-orange-700']">
                            {{ order.payment_status === 'paid' ? '✅ Đã thanh toán' : '💳 Chưa thanh toán' }}
                        </span>
                    </div>

                    <!-- Update status -->
                    <div class="bg-white rounded-xl border border-gray-200 p-4 space-y-3">
                        <div class="flex items-center gap-2">
                            <RefreshCw :size="15" class="text-indigo-600" />
                            <h3 class="font-semibold text-gray-800 text-sm">Cập nhật trạng thái</h3>
                        </div>
                        <div class="space-y-2">
                            <select v-model="newStatus"
                                class="w-full text-sm border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500">
                                <option v-for="o in statusOptions" :key="o.value" :value="o.value">{{ o.label }}</option>
                            </select>
                            <select v-model="newPaymentStatus"
                                class="w-full text-sm border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500">
                                <option v-for="o in paymentOptions" :key="o.value" :value="o.value">{{ o.label }}</option>
                            </select>
                            <button @click="updateStatus" :disabled="updating"
                                class="w-full py-2 rounded-lg bg-indigo-600 text-white text-sm font-medium hover:bg-indigo-700 disabled:opacity-50 transition-colors">
                                {{ updating ? 'Đang lưu...' : 'Lưu thay đổi' }}
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </AdminLayout>
</template>
