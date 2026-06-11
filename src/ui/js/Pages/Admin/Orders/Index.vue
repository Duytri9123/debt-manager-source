<script setup>
import AdminLayout from '@/Layouts/AdminLayout.vue'
import { router, Link } from '@inertiajs/vue3'
import { ref } from 'vue'
import { Search, Eye, RefreshCw, ShoppingCart, Plus } from 'lucide-vue-next'

const props = defineProps({
    orders:  Object,
    stats:   Object,
    filters: Object,
})

const search         = ref(props.filters?.search ?? '')
const statusFilter   = ref(props.filters?.status ?? '')
const paymentFilter  = ref(props.filters?.payment_status ?? '')

const statusOptions = [
    { value: '',           label: 'Tất cả trạng thái' },
    { value: 'pending',    label: '⏳ Chờ xác nhận' },
    { value: 'processing', label: '🔄 Đang xử lý' },
    { value: 'shipped',    label: '🚚 Đang giao' },
    { value: 'delivered',  label: '✅ Đã giao' },
    { value: 'cancelled',  label: '❌ Đã hủy' },
]

const paymentOptions = [
    { value: '',       label: 'Tất cả thanh toán' },
    { value: 'unpaid', label: '💳 Chưa thanh toán' },
    { value: 'paid',   label: '✅ Đã thanh toán' },
]

const statusColors = {
    pending:    'bg-yellow-100 text-yellow-700',
    processing: 'bg-blue-100 text-blue-700',
    shipped:    'bg-indigo-100 text-indigo-700',
    delivered:  'bg-green-100 text-green-700',
    cancelled:  'bg-red-100 text-red-700',
}
const statusLabels = {
    pending: '⏳ Chờ xác nhận', processing: '🔄 Đang xử lý',
    shipped: '🚚 Đang giao', delivered: '✅ Đã giao', cancelled: '❌ Đã hủy',
}
const paymentColors = { unpaid: 'bg-orange-100 text-orange-700', paid: 'bg-green-100 text-green-700' }

function applyFilter() {
    router.get('/admin/orders', {
        search:         search.value || undefined,
        status:         statusFilter.value || undefined,
        payment_status: paymentFilter.value || undefined,
    }, { preserveState: true, replace: true })
}

function formatMoney(v) {
    return Number(v || 0).toLocaleString('vi-VN') + 'đ'
}
function formatDate(d) {
    return new Date(d).toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}
</script>

<template>
    <AdminLayout>
        <div class="space-y-5">
            <!-- Header -->
            <div class="flex items-center justify-between">
                <div>
                    <h1 class="text-xl font-bold text-gray-900 flex items-center gap-2">
                        <ShoppingCart :size="22" class="text-indigo-600" /> Quản lý Đơn hàng
                    </h1>
                    <p class="text-sm text-gray-500 mt-0.5">Theo dõi và xử lý đơn hàng từ khách hàng</p>
                </div>
                <Link href="/admin/orders/create"
                    class="flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 transition-colors">
                    <Plus :size="16" /> Tạo đơn hàng
                </Link>
            </div>

            <!-- Stats -->
            <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
                <div v-for="(item, key) in [
                    { label: 'Tổng đơn',    value: stats.total,      color: 'bg-gray-50 border-gray-200',     text: 'text-gray-700' },
                    { label: 'Chờ xác nhận',value: stats.pending,    color: 'bg-yellow-50 border-yellow-200', text: 'text-yellow-700' },
                    { label: 'Đang xử lý',  value: stats.processing, color: 'bg-blue-50 border-blue-200',     text: 'text-blue-700' },
                    { label: 'Đang giao',   value: stats.shipped,    color: 'bg-indigo-50 border-indigo-200', text: 'text-indigo-700' },
                    { label: 'Đã giao',     value: stats.delivered,  color: 'bg-green-50 border-green-200',   text: 'text-green-700' },
                    { label: 'Đã hủy',      value: stats.cancelled,  color: 'bg-red-50 border-red-200',       text: 'text-red-700' },
                ]" :key="key"
                    :class="['rounded-xl border p-3 text-center', item.color]">
                    <p :class="['text-2xl font-bold', item.text]">{{ item.value }}</p>
                    <p class="text-xs text-gray-500 mt-0.5">{{ item.label }}</p>
                </div>
            </div>

            <!-- Filters -->
            <div class="flex flex-wrap gap-3 bg-white rounded-xl border border-gray-200 p-3">
                <div class="flex-1 min-w-[200px] relative">
                    <Search :size="15" class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                    <input v-model="search" @keyup.enter="applyFilter"
                        placeholder="Tìm mã đơn, tên, email, SĐT..."
                        class="w-full pl-9 pr-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                </div>
                <select v-model="statusFilter" @change="applyFilter"
                    class="text-sm border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500">
                    <option v-for="o in statusOptions" :key="o.value" :value="o.value">{{ o.label }}</option>
                </select>
                <select v-model="paymentFilter" @change="applyFilter"
                    class="text-sm border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500">
                    <option v-for="o in paymentOptions" :key="o.value" :value="o.value">{{ o.label }}</option>
                </select>
                <button @click="search=''; statusFilter=''; paymentFilter=''; applyFilter()"
                    class="flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-700 px-3 py-2 rounded-lg hover:bg-gray-100 transition-colors">
                    <RefreshCw :size="14" /> Reset
                </button>
            </div>

            <!-- Table -->
            <div class="bg-white rounded-xl border border-gray-200 overflow-hidden">
                <div class="overflow-x-auto">
                    <table class="w-full text-sm">
                        <thead class="bg-gray-50 border-b border-gray-200">
                            <tr>
                                <th class="text-left px-4 py-3 font-medium text-gray-600">Mã đơn</th>
                                <th class="text-left px-4 py-3 font-medium text-gray-600">Khách hàng</th>
                                <th class="text-left px-4 py-3 font-medium text-gray-600">Sản phẩm</th>
                                <th class="text-right px-4 py-3 font-medium text-gray-600">Tổng tiền</th>
                                <th class="text-center px-4 py-3 font-medium text-gray-600">Trạng thái</th>
                                <th class="text-center px-4 py-3 font-medium text-gray-600">Thanh toán</th>
                                <th class="text-left px-4 py-3 font-medium text-gray-600">Ngày đặt</th>
                                <th class="px-4 py-3"></th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-gray-100">
                            <tr v-if="!orders.data?.length">
                                <td colspan="8" class="text-center py-12 text-gray-400">
                                    <ShoppingCart :size="32" class="mx-auto mb-2 opacity-30" />
                                    Không có đơn hàng nào
                                </td>
                            </tr>
                            <tr v-for="order in orders.data" :key="order.id"
                                @click="router.visit(`/admin/orders/${order.id}`)"
                                class="hover:bg-indigo-50/40 cursor-pointer transition-colors">
                                <td class="px-4 py-3">
                                    <span class="font-mono text-xs font-semibold text-indigo-600">{{ order.order_number }}</span>
                                </td>
                                <td class="px-4 py-3">
                                    <p class="font-medium text-gray-800">{{ order.customer_name }}</p>
                                    <p class="text-xs text-gray-400">{{ order.customer_phone }}</p>
                                </td>
                                <td class="px-4 py-3 text-gray-500">
                                    {{ order.items_count }} sản phẩm
                                </td>
                                <td class="px-4 py-3 text-right font-semibold text-gray-800">
                                    {{ formatMoney(order.grand_total) }}
                                </td>
                                <td class="px-4 py-3 text-center">
                                    <span :class="['inline-flex px-2 py-0.5 rounded-full text-xs font-medium', statusColors[order.status] ?? 'bg-gray-100 text-gray-600']">
                                        {{ statusLabels[order.status] ?? order.status }}
                                    </span>
                                </td>
                                <td class="px-4 py-3 text-center">
                                    <span :class="['inline-flex px-2 py-0.5 rounded-full text-xs font-medium', paymentColors[order.payment_status] ?? 'bg-gray-100 text-gray-600']">
                                        {{ order.payment_status === 'paid' ? '✅ Đã TT' : '💳 Chưa TT' }}
                                    </span>
                                </td>
                                <td class="px-4 py-3 text-xs text-gray-500">{{ formatDate(order.created_at) }}</td>
                                <td class="px-4 py-3" @click.stop>
                                    <Link :href="`/admin/orders/${order.id}`"
                                        class="p-1.5 rounded-lg hover:bg-indigo-50 text-indigo-600 transition-colors inline-flex">
                                        <Eye :size="15" />
                                    </Link>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>

                <!-- Pagination -->
                <div v-if="orders.last_page > 1" class="flex items-center justify-between px-4 py-3 border-t border-gray-100">
                    <p class="text-xs text-gray-500">
                        Hiển thị {{ orders.from }}–{{ orders.to }} / {{ orders.total }} đơn hàng
                    </p>
                    <div class="flex gap-1">
                        <Link v-for="link in orders.links" :key="link.label"
                            :href="link.url ?? '#'"
                            :class="['px-3 py-1 text-xs rounded-lg transition-colors',
                                link.active ? 'bg-indigo-600 text-white' : 'text-gray-600 hover:bg-gray-100',
                                !link.url ? 'opacity-40 pointer-events-none' : '']"
                            v-html="link.label" />
                    </div>
                </div>
            </div>
        </div>
    </AdminLayout>
</template>
