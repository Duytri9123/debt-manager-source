<script setup>
import AdminLayout from '@/Layouts/AdminLayout.vue'
import { router, Link } from '@inertiajs/vue3'
import { ref } from 'vue'
import { Plus, Search, Eye, Edit2, Trash2, Upload, RefreshCw, TrendingUp, ShoppingBag, Users, DollarSign } from 'lucide-vue-next'

const props = defineProps({
    orders:  Object,
    stats:   Object,
    filters: Object,
})

const search = ref(props.filters?.search ?? '')
const from   = ref(props.filters?.from ?? '')
const to     = ref(props.filters?.to ?? '')

function applyFilter() {
    router.get('/admin/b2b-orders', {
        search: search.value || undefined,
        from:   from.value   || undefined,
        to:     to.value     || undefined,
    }, { preserveState: true, replace: true })
}

function reset() {
    search.value = ''; from.value = ''; to.value = ''
    applyFilter()
}

function destroy(id, name) {
    if (!confirm(`Xóa đơn hàng của "${name}"?`)) return
    router.delete(`/admin/b2b-orders/${id}`)
}

function fmt(v) { return Number(v || 0).toLocaleString('vi-VN') + 'đ' }
function fmtDate(d) { return d ? new Date(d).toLocaleDateString('vi-VN') : '—' }
</script>

<template>
    <AdminLayout>
        <div class="space-y-5">
            <!-- Header -->
            <div class="flex items-center justify-between flex-wrap gap-3">
                <div>
                    <h1 class="text-xl font-bold text-gray-900">📋 Theo dõi Đơn hàng KD</h1>
                    <p class="text-sm text-gray-500 mt-0.5">Quản lý đơn hàng kinh doanh </p>
                </div>
                <div class="flex gap-2">
                    <Link href="/admin/b2b-orders/import"
                        class="flex items-center gap-2 rounded-lg border border-indigo-300 bg-indigo-50 px-3 py-2 text-sm font-medium text-indigo-700 hover:bg-indigo-100 transition-colors">
                        <Upload :size="15" /> Import Excel
                    </Link>
                    <Link href="/admin/b2b-orders/create"
                        class="flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 transition-colors">
                        <Plus :size="15" /> Tạo đơn hàng
                    </Link>
                </div>
            </div>

            <!-- Stats -->
            <div class="grid grid-cols-2 lg:grid-cols-4 gap-3">
                <div class="bg-white rounded-xl border border-gray-200 p-4 shadow-sm">
                    <div class="flex items-center gap-2 mb-1">
                        <ShoppingBag :size="16" class="text-indigo-500" />
                        <span class="text-xs text-gray-400 uppercase tracking-wide">Tổng đơn</span>
                    </div>
                    <p class="text-2xl font-bold text-gray-900">{{ stats?.total_orders ?? 0 }}</p>
                </div>
                <div class="bg-white rounded-xl border border-gray-200 p-4 shadow-sm">
                    <div class="flex items-center gap-2 mb-1">
                        <Users :size="16" class="text-blue-500" />
                        <span class="text-xs text-gray-400 uppercase tracking-wide">Khách hàng</span>
                    </div>
                    <p class="text-2xl font-bold text-gray-900">{{ stats?.customers ?? 0 }}</p>
                </div>
                <div class="bg-white rounded-xl border border-gray-200 p-4 shadow-sm">
                    <div class="flex items-center gap-2 mb-1">
                        <DollarSign :size="16" class="text-emerald-500" />
                        <span class="text-xs text-gray-400 uppercase tracking-wide">Doanh thu</span>
                    </div>
                    <p class="text-lg font-bold text-emerald-700">{{ fmt(stats?.total_revenue) }}</p>
                </div>
                <div class="bg-white rounded-xl border border-gray-200 p-4 shadow-sm">
                    <div class="flex items-center gap-2 mb-1">
                        <TrendingUp :size="16" class="text-orange-500" />
                        <span class="text-xs text-gray-400 uppercase tracking-wide">Tổng lãi</span>
                    </div>
                    <p class="text-lg font-bold text-orange-600">{{ fmt(stats?.total_profit) }}</p>
                </div>
            </div>

            <!-- Filters -->
            <div class="flex flex-wrap gap-3 bg-white rounded-xl border border-gray-200 p-3">
                <div class="flex-1 min-w-[200px] relative">
                    <Search :size="14" class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                    <input v-model="search" @keyup.enter="applyFilter"
                        placeholder="Tìm mã đơn, tên khách..."
                        class="w-full pl-9 pr-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                </div>
                <input v-model="from" type="date" @change="applyFilter"
                    class="text-sm border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                <input v-model="to" type="date" @change="applyFilter"
                    class="text-sm border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                <button @click="reset"
                    class="flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-700 px-3 py-2 rounded-lg hover:bg-gray-100 transition-colors">
                    <RefreshCw :size="13" /> Reset
                </button>
            </div>

            <!-- Table -->
            <div class="bg-white rounded-xl border border-gray-200 overflow-hidden shadow-sm">
                <div class="overflow-x-auto">
                    <table class="w-full text-sm">
                        <thead class="bg-gray-50 border-b border-gray-200">
                            <tr>
                                <th class="text-left px-4 py-3 font-medium text-gray-600 whitespace-nowrap">Mã đơn</th>
                                <th class="text-left px-4 py-3 font-medium text-gray-600 whitespace-nowrap">Khách hàng</th>
                                <th class="text-left px-4 py-3 font-medium text-gray-600 whitespace-nowrap">Ngày đặt</th>
                                <th class="text-center px-4 py-3 font-medium text-gray-600 whitespace-nowrap">Số SP</th>
                                <th class="text-right px-4 py-3 font-medium text-gray-600 whitespace-nowrap">Trước thuế</th>
                                <th class="text-right px-4 py-3 font-medium text-gray-600 whitespace-nowrap">Thuế 10%</th>
                                <th class="text-right px-4 py-3 font-medium text-gray-600 whitespace-nowrap">Tổng sau thuế</th>
                                <th class="text-right px-4 py-3 font-medium text-orange-600 whitespace-nowrap">Tiền lãi</th>
                                <th class="px-4 py-3"></th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-gray-100">
                            <tr v-if="!orders.data?.length">
                                <td colspan="9" class="text-center py-12 text-gray-400">Chưa có đơn hàng nào</td>
                            </tr>
                            <tr v-for="order in orders.data" :key="order.id"
                                @click="router.visit(`/admin/b2b-orders/${order.id}`)"
                                class="hover:bg-indigo-50/40 cursor-pointer transition-colors">
                                <td class="px-4 py-3">
                                    <span class="font-mono text-xs font-semibold text-indigo-600 hover:underline">{{ order.order_number }}</span>
                                </td>
                                <td class="px-4 py-3 font-medium text-gray-800">{{ order.customer_name }}</td>
                                <td class="px-4 py-3 text-gray-500 text-xs">{{ fmtDate(order.created_at) }}</td>
                                <td class="px-4 py-3 text-center text-gray-500">{{ order.items?.length ?? 0 }}</td>
                                <td class="px-4 py-3 text-right text-gray-700">{{ fmt(order.total_before_tax) }}</td>
                                <td class="px-4 py-3 text-right text-gray-500">{{ fmt(order.tax_amount) }}</td>
                                <td class="px-4 py-3 text-right font-semibold text-gray-900">{{ fmt(order.grand_total) }}</td>
                                <td class="px-4 py-3 text-right font-semibold text-orange-600">{{ fmt(order.total_profit) }}</td>
                                <td class="px-4 py-3" @click.stop>
                                    <div class="flex items-center gap-1">
                                        <Link :href="`/admin/b2b-orders/${order.id}`"
                                            class="p-1.5 rounded-lg hover:bg-indigo-50 text-indigo-600 transition-colors">
                                            <Eye :size="14" />
                                        </Link>
                                        <Link :href="`/admin/b2b-orders/${order.id}/edit`"
                                            class="p-1.5 rounded-lg hover:bg-amber-50 text-amber-600 transition-colors">
                                            <Edit2 :size="14" />
                                        </Link>
                                        <button @click="destroy(order.id, order.customer_name)"
                                            class="p-1.5 rounded-lg hover:bg-red-50 text-red-500 transition-colors">
                                            <Trash2 :size="14" />
                                        </button>
                                    </div>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>

                <!-- Pagination -->
                <div v-if="orders.last_page > 1" class="flex items-center justify-between px-4 py-3 border-t border-gray-100">
                    <p class="text-xs text-gray-500">{{ orders.from }}–{{ orders.to }} / {{ orders.total }} đơn</p>
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
