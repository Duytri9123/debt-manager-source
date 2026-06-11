<script setup>
import AdminLayout from '@/Layouts/AdminLayout.vue'
import { router, Link } from '@inertiajs/vue3'
import { computed } from 'vue'
import { ArrowLeft, Edit2, Trash2, Calendar, User, FileText, TrendingUp } from 'lucide-vue-next'

const props = defineProps({ order: Object })

const items = computed(() => props.order.items ?? [])

const totalBeforeTax = computed(() =>
    props.order.total_before_tax > 0
        ? Number(props.order.total_before_tax)
        : items.value.reduce((s, i) => s + Number(i.price) * Number(i.quantity), 0)
)
const tax         = computed(() => props.order.tax_amount > 0 ? Number(props.order.tax_amount) : 0)
const taxRate     = computed(() => {
    if (props.order.tax_amount > 0 && props.order.total_before_tax > 0)
        return Math.round(props.order.tax_amount / props.order.total_before_tax * 100)
    return 0
})
const grandTotal  = computed(() => Number(props.order.grand_total) || (totalBeforeTax.value + tax.value))
const totalProfit = computed(() => items.value.reduce((s, i) => s + Number(i.total_profit || 0), 0))
const totalWeight = computed(() => items.value.reduce((s, i) => s + Number(i.weight_kg || 0), 0))

// Parse ghi chú từ variant_attributes
function getNote(item) {
    if (!item.variant_attributes) return ''
    try {
        const a = typeof item.variant_attributes === 'string'
            ? JSON.parse(item.variant_attributes)
            : item.variant_attributes
        return a?.note ?? ''
    } catch { return '' }
}

function fmt(v)     { return Number(v || 0).toLocaleString('vi-VN') }
function fmtDate(d) {
    if (!d) return '—'
    return new Date(d).toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

function destroy() {
    if (!confirm('Xóa đơn hàng này?')) return
    router.delete(`/admin/b2b-orders/${props.order.id}`)
}
</script>

<template>
    <AdminLayout>
        <div class="space-y-4">

            <!-- Header -->
            <div class="flex items-center gap-3 flex-wrap">
                <Link href="/admin/b2b-orders" class="p-2 rounded-lg hover:bg-gray-100 transition-colors">
                    <ArrowLeft :size="18" class="text-gray-600" />
                </Link>
                <div class="flex-1 min-w-0">
                    <div class="flex items-center gap-2 flex-wrap">
                        <h1 class="text-xl font-bold text-gray-900 font-mono">{{ order.order_number }}</h1>
                        <span class="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full font-medium">✅ Đã giao</span>
                    </div>
                    <div class="flex items-center gap-4 mt-1 text-sm text-gray-500 flex-wrap">
                        <span class="flex items-center gap-1"><User :size="13" /> {{ order.customer_name }}</span>
                        <span class="flex items-center gap-1"><Calendar :size="13" /> {{ fmtDate(order.created_at) }}</span>
                        <span class="flex items-center gap-1"><FileText :size="13" /> {{ items.length }} sản phẩm</span>
                    </div>
                </div>
                <div class="flex gap-2 shrink-0">
                    <Link :href="`/admin/b2b-orders/${order.id}/edit`"
                        class="flex items-center gap-1.5 px-3 py-2 rounded-lg bg-amber-500 text-white text-sm hover:bg-amber-600 transition-colors">
                        <Edit2 :size="14" /> Chỉnh sửa
                    </Link>
                    <button @click="destroy"
                        class="flex items-center gap-1.5 px-3 py-2 rounded-lg bg-red-500 text-white text-sm hover:bg-red-600 transition-colors">
                        <Trash2 :size="14" /> Xóa
                    </button>
                </div>
            </div>

            <!-- Summary cards -->
            <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <div class="bg-white rounded-xl border border-gray-200 p-3 shadow-sm">
                    <p class="text-xs text-gray-400 uppercase tracking-wide">Tổng trước thuế</p>
                    <p class="text-lg font-bold text-gray-900 mt-0.5">{{ fmt(totalBeforeTax) }}<span class="text-xs font-normal text-gray-400">đ</span></p>
                </div>
                <div class="bg-white rounded-xl border border-gray-200 p-3 shadow-sm">
                    <p class="text-xs text-gray-400 uppercase tracking-wide">Thuế GTGT {{ taxRate > 0 ? taxRate + '%' : '' }}</p>
                    <p class="text-lg font-bold text-gray-700 mt-0.5">{{ fmt(tax) }}<span class="text-xs font-normal text-gray-400">đ</span></p>
                </div>
                <div class="bg-indigo-50 rounded-xl border border-indigo-200 p-3 shadow-sm">
                    <p class="text-xs text-indigo-600 uppercase tracking-wide font-medium">Tổng sau thuế</p>
                    <p class="text-lg font-bold text-indigo-700 mt-0.5">{{ fmt(grandTotal) }}<span class="text-xs font-normal text-indigo-400">đ</span></p>
                </div>
                <div class="bg-orange-50 rounded-xl border border-orange-200 p-3 shadow-sm">
                    <p class="text-xs text-orange-600 uppercase tracking-wide font-medium flex items-center gap-1">
                        <TrendingUp :size="11" /> Tổng tiền lãi
                    </p>
                    <p class="text-lg font-bold text-orange-700 mt-0.5">{{ fmt(totalProfit) }}<span class="text-xs font-normal text-orange-400">đ</span></p>
                </div>
            </div>

            <!-- Excel-style detail table -->
            <div class="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
                <!-- Table header info giống Excel -->
                <div class="px-4 py-3 bg-yellow-50 border-b border-yellow-200 flex items-center justify-between">
                    <div>
                        <span class="font-bold text-gray-800 text-sm">{{ order.customer_name }}</span>
                        <span class="mx-2 text-gray-400">·</span>
                        <span class="text-sm text-gray-600">{{ fmtDate(order.created_at) }}</span>
                    </div>
                    <span class="text-xs text-gray-400">{{ items.length }} dòng</span>
                </div>

                <div class="overflow-x-auto">
                    <table class="w-full text-xs border-collapse">
                        <!-- Header giống Excel -->
                        <thead>
                            <tr class="bg-yellow-100 border-b-2 border-yellow-300">
                                <th class="px-2 py-2 text-center font-bold text-gray-700 border-r border-yellow-200 w-8">TT</th>
                                <th class="px-3 py-2 text-left font-bold text-gray-700 border-r border-yellow-200 min-w-[220px]">MÔ TẢ CHI TIẾT</th>
                                <th class="px-2 py-2 text-left font-bold text-gray-700 border-r border-yellow-200 w-28">MÃ HÀNG</th>
                                <th class="px-2 py-2 text-center font-bold text-gray-700 border-r border-yellow-200 w-16">XUẤT XỨ</th>
                                <th class="px-2 py-2 text-center font-bold text-gray-700 border-r border-yellow-200 w-16">ĐƠN VỊ</th>
                                <th class="px-2 py-2 text-right font-bold text-gray-700 border-r border-yellow-200 w-20">SỐ LƯỢNG</th>
                                <th class="px-2 py-2 text-right font-bold text-gray-700 border-r border-yellow-200 w-28">ĐƠN GIÁ</th>
                                <th class="px-2 py-2 text-right font-bold text-gray-700 border-r border-yellow-200 w-28">THÀNH TIỀN</th>
                                <th class="px-2 py-2 text-left font-bold text-gray-700 border-r border-yellow-200 w-32">GHI CHÚ</th>
                                <th class="px-2 py-2 text-right font-bold text-blue-800 border-r border-yellow-200 w-28 bg-blue-100">ĐẦU VÀO</th>
                                <th class="px-2 py-2 text-right font-bold text-blue-800 border-r border-yellow-200 w-28 bg-blue-100">GIÁ BÁN</th>
                                <th class="px-2 py-2 text-right font-bold text-orange-800 border-r border-yellow-200 w-28 bg-orange-100">% KINH DOANH</th>
                                <th class="px-2 py-2 text-right font-bold text-orange-800 border-r border-yellow-200 w-24 bg-orange-100">TIỀN LÃI /1KG</th>
                                <th class="px-2 py-2 text-right font-bold text-orange-800 border-r border-yellow-200 w-24 bg-orange-100">KHỐI LƯỢNG (KG)</th>
                                <th class="px-2 py-2 text-right font-bold text-orange-800 w-28 bg-orange-100">TIỀN LÃI TỔNG KL</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="(item, idx) in items" :key="item.id"
                                :class="['border-b border-gray-100 hover:bg-yellow-50/30 transition-colors', idx % 2 === 0 ? 'bg-white' : 'bg-gray-50/30']">
                                <td class="px-2 py-2 text-center text-gray-400 border-r border-gray-100">{{ idx + 1 }}</td>
                                <td class="px-3 py-2 border-r border-gray-100">
                                    <div class="font-medium text-gray-800 whitespace-pre-wrap leading-relaxed">{{ item.product_name }}</div>
                                </td>
                                <td class="px-2 py-2 text-gray-500 font-mono border-r border-gray-100">{{ item.variant_sku || '—' }}</td>
                                <td class="px-2 py-2 text-center text-gray-600 border-r border-gray-100">{{ item.origin || 'VN' }}</td>
                                <td class="px-2 py-2 text-center text-gray-600 border-r border-gray-100">{{ item.unit || '—' }}</td>
                                <td class="px-2 py-2 text-right text-gray-700 border-r border-gray-100 font-medium">
                                    {{ Number(item.quantity).toLocaleString('vi-VN') }}
                                </td>
                                <td class="px-2 py-2 text-right text-gray-700 border-r border-gray-100">
                                    {{ fmt(item.price) }}
                                </td>
                                <td class="px-2 py-2 text-right font-semibold text-gray-900 border-r border-gray-100">
                                    {{ fmt(Number(item.price) * Number(item.quantity)) }}
                                </td>
                                <td class="px-2 py-2 text-gray-400 border-r border-gray-100 italic">
                                    {{ getNote(item) || '—' }}
                                </td>
                                <!-- Giá nhập / giá bán — màu xanh -->
                                <td class="px-2 py-2 text-right text-blue-700 border-r border-gray-100 bg-blue-50/20">
                                    {{ item.cost_price ? fmt(item.cost_price) : '—' }}
                                </td>
                                <td class="px-2 py-2 text-right text-blue-700 border-r border-gray-100 bg-blue-50/20">
                                    {{ item.selling_price ? fmt(item.selling_price) : '—' }}
                                </td>
                                <!-- Lãi — màu cam -->
                                <td class="px-2 py-2 text-right text-orange-600 border-r border-gray-100 bg-orange-50/20">
                                    {{ item.business_pct ? fmt(item.business_pct) : '—' }}
                                </td>
                                <td class="px-2 py-2 text-right text-orange-600 border-r border-gray-100 bg-orange-50/20">
                                    {{ item.profit_per_kg ? fmt(item.profit_per_kg) : '—' }}
                                </td>
                                <td class="px-2 py-2 text-right text-orange-600 border-r border-gray-100 bg-orange-50/20">
                                    {{ item.weight_kg ? Number(item.weight_kg).toLocaleString('vi-VN') : '—' }}
                                </td>
                                <td class="px-2 py-2 text-right font-semibold text-orange-700 bg-orange-50/20">
                                    {{ item.total_profit ? fmt(item.total_profit) : '—' }}
                                </td>
                            </tr>
                        </tbody>

                        <!-- Footer tổng — giống Excel -->
                        <tfoot>
                            <tr class="border-t-2 border-gray-400 bg-yellow-50 font-semibold">
                                <td colspan="7" class="px-3 py-2 text-right text-gray-700 text-xs uppercase tracking-wide">
                                    TỔNG GIÁ TRỊ TRƯỚC THUẾ
                                </td>
                                <td class="px-2 py-2 text-right font-bold text-gray-900">{{ fmt(totalBeforeTax) }}</td>
                                <td colspan="5" class="border-r border-gray-200"></td>
                                <td class="px-2 py-2 text-right text-gray-600 bg-orange-50/30">
                                    {{ Number(totalWeight).toLocaleString('vi-VN') }}
                                </td>
                                <td class="px-2 py-2 text-right font-bold text-orange-700 bg-orange-50/30">
                                    {{ fmt(totalProfit) }}
                                </td>
                            </tr>
                            <tr class="bg-yellow-50/50">
                                <td colspan="7" class="px-3 py-1.5 text-right text-gray-500 text-xs">THUẾ GTGT {{ taxRate > 0 ? taxRate + '%' : '' }}</td>
                                <td class="px-2 py-1.5 text-right text-gray-700 font-medium">{{ fmt(tax) }}</td>
                                <td colspan="7"></td>
                            </tr>
                            <tr class="bg-indigo-50 border-t border-indigo-200">
                                <td colspan="7" class="px-3 py-2 text-right font-bold text-indigo-800 text-xs uppercase tracking-wide">
                                    TỔNG GIÁ TRỊ SAU THUẾ
                                </td>
                                <td class="px-2 py-2 text-right font-bold text-indigo-700 text-sm">{{ fmt(grandTotal) }}</td>
                                <td colspan="7"></td>
                            </tr>
                        </tfoot>
                    </table>
                </div>
            </div>

            <!-- Notes -->
            <div v-if="order.notes" class="bg-amber-50 border border-amber-200 rounded-xl px-4 py-3 text-sm text-amber-800">
                <span class="font-medium">📝 Ghi chú:</span> {{ order.notes }}
            </div>

        </div>
    </AdminLayout>
</template>
