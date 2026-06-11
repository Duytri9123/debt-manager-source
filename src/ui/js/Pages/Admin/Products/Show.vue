<script setup>
import AdminLayout from '@/Layouts/AdminLayout.vue'
import { router, Link } from '@inertiajs/vue3'
import { computed } from 'vue'
import { Edit2, Trash2, Package, TrendingUp, ShoppingBag, DollarSign, BarChart3 } from 'lucide-vue-next'

const props = defineProps({
    product:      Object,
    salesHistory: Array,
    salesStats:   Object,
})

function fmt(v) {
    if (!v && v !== 0) return '—'
    return Number(v).toLocaleString('vi-VN', { style: 'currency', currency: 'VND' })
}
function fmtNum(v) { return Number(v || 0).toLocaleString('vi-VN') }
function fmtDate(d) {
    if (!d) return '—'
    return new Date(d).toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

const statusLabels = { active: 'Đang bán', inactive: 'Ngừng bán', draft: 'Nháp', out_of_stock: 'Hết hàng' }
const statusColors = {
    active:       'bg-emerald-100 text-emerald-700',
    inactive:     'bg-gray-100 text-gray-600',
    draft:        'bg-amber-100 text-amber-700',
    out_of_stock: 'bg-red-100 text-red-700',
}

function getStatus(p) { return p.status?.value ?? p.status }

function destroy() {
    if (confirm(`Xóa sản phẩm "${props.product.name}"?`)) {
        router.delete(`/admin/products/${props.product.id}`)
    }
}

function getImageUrl(img) {
    if (!img?.url) return null
    return img.url.startsWith('http') ? img.url : `/storage/${img.url}`
}

const totalStock = computed(() =>
    (props.product.variants ?? []).reduce((s, v) => s + (v.quantity ?? 0), 0)
)

// Nhóm lịch sử bán theo đơn hàng
const orderGroups = computed(() => {
    const map = new Map()
    for (const item of props.salesHistory ?? []) {
        const oid = item.order?.id ?? item.order_id
        if (!map.has(oid)) {
            map.set(oid, {
                order:    item.order,
                items:    [],
                subtotal: 0,
                profit:   0,
            })
        }
        const g = map.get(oid)
        g.items.push(item)
        g.subtotal += Number(item.price) * Number(item.quantity)
        g.profit   += Number(item.total_profit || 0)
    }
    return [...map.values()]
})
</script>

<template>
    <AdminLayout>
        <div class="space-y-5">
            <!-- Header -->
            <div class="flex items-center justify-between flex-wrap gap-3">
                <div class="flex items-center gap-3">
                    <button @click="router.visit('/admin/products')"
                        class="text-gray-500 hover:text-gray-700 text-sm transition-colors">← Quay lại</button>
                    <h1 class="text-xl font-bold text-gray-900 truncate max-w-lg">{{ product.name }}</h1>
                    <span :class="['rounded-full px-2.5 py-0.5 text-xs font-medium', statusColors[getStatus(product)]]">
                        {{ statusLabels[getStatus(product)] ?? getStatus(product) }}
                    </span>
                </div>
                <div class="flex gap-2">
                    <button @click="router.visit(`/admin/products/${product.id}/edit`)"
                        class="flex items-center gap-1.5 rounded-lg border border-indigo-300 px-3 py-1.5 text-sm text-indigo-600 hover:bg-indigo-50 transition-colors">
                        <Edit2 :size="14" /> Chỉnh sửa
                    </button>
                    <button @click="destroy"
                        class="flex items-center gap-1.5 rounded-lg border border-red-300 px-3 py-1.5 text-sm text-red-600 hover:bg-red-50 transition-colors">
                        <Trash2 :size="14" /> Xóa
                    </button>
                </div>
            </div>

            <!-- ── STATS BÁN HÀNG ── -->
            <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <div class="bg-indigo-50 rounded-xl border border-indigo-200 p-4 shadow-sm">
                    <div class="flex items-center gap-2 mb-1">
                        <ShoppingBag :size="15" class="text-indigo-500" />
                        <span class="text-xs text-indigo-500 uppercase tracking-wide">Số đơn hàng</span>
                    </div>
                    <p class="text-2xl font-bold text-indigo-700">{{ salesStats?.order_count ?? 0 }}</p>
                </div>
                <div class="bg-emerald-50 rounded-xl border border-emerald-200 p-4 shadow-sm">
                    <div class="flex items-center gap-2 mb-1">
                        <BarChart3 :size="15" class="text-emerald-500" />
                        <span class="text-xs text-emerald-500 uppercase tracking-wide">Đã bán</span>
                    </div>
                    <p class="text-2xl font-bold text-emerald-700">{{ fmtNum(salesStats?.total_sold) }}</p>
                    <p class="text-xs text-emerald-400 mt-0.5">sản phẩm</p>
                </div>
                <div class="bg-gray-50 rounded-xl border border-gray-200 p-4 shadow-sm">
                    <div class="flex items-center gap-2 mb-1">
                        <DollarSign :size="15" class="text-gray-500" />
                        <span class="text-xs text-gray-400 uppercase tracking-wide">Doanh thu</span>
                    </div>
                    <p class="text-base font-bold text-gray-800">{{ fmt(salesStats?.total_revenue) }}</p>
                </div>
                <div class="bg-orange-50 rounded-xl border border-orange-200 p-4 shadow-sm">
                    <div class="flex items-center gap-2 mb-1">
                        <TrendingUp :size="15" class="text-orange-500" />
                        <span class="text-xs text-orange-500 uppercase tracking-wide">Tiền lãi</span>
                    </div>
                    <p class="text-base font-bold text-orange-700">{{ fmt(salesStats?.total_profit) }}</p>
                </div>
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-3 gap-5">

                <!-- Left: Variants + Description -->
                <div class="lg:col-span-2 space-y-4">

                    <!-- Thumbnail -->
                    <div class="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
                        <div class="aspect-video bg-gray-100 flex items-center justify-center max-h-48">
                            <img v-if="getImageUrl(product.thumbnail_image)"
                                :src="getImageUrl(product.thumbnail_image)"
                                :alt="product.name"
                                class="h-full w-full object-contain" />
                            <Package v-else :size="48" class="text-gray-300" />
                        </div>
                    </div>

                    <!-- Variants -->
                    <div class="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
                        <div class="px-4 py-3 border-b border-gray-100 flex items-center justify-between bg-gray-50">
                            <h3 class="font-semibold text-gray-900 text-sm">Biến thể sản phẩm</h3>
                            <span class="text-xs text-gray-500">Tồn kho: <strong>{{ totalStock }}</strong></span>
                        </div>
                        <table class="w-full text-sm">
                            <thead class="bg-gray-50 border-b border-gray-100">
                                <tr>
                                    <th class="text-left px-4 py-2 font-medium text-gray-500 text-xs">SKU</th>
                                    <th class="text-left px-4 py-2 font-medium text-gray-500 text-xs">ĐVT</th>
                                    <th class="text-right px-4 py-2 font-medium text-gray-500 text-xs">Giá nhập</th>
                                    <th class="text-right px-4 py-2 font-medium text-gray-500 text-xs">Giá bán</th>
                                    <th class="text-right px-4 py-2 font-medium text-gray-500 text-xs">Tồn kho</th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-gray-100">
                                <tr v-for="v in product.variants" :key="v.id"
                                    :class="v.is_default ? 'bg-indigo-50/50' : ''">
                                    <td class="px-4 py-2 font-mono text-xs text-gray-700">{{ v.sku }}</td>
                                    <td class="px-4 py-2 text-gray-500 text-xs">{{ v.unit ?? '—' }}</td>
                                    <td class="px-4 py-2 text-right text-gray-500 text-xs">{{ fmt(v.cost_price) }}</td>
                                    <td class="px-4 py-2 text-right font-semibold text-indigo-600 text-xs">{{ fmt(v.selling_price) }}</td>
                                    <td class="px-4 py-2 text-right text-xs" :class="v.quantity <= 0 ? 'text-red-500' : 'text-gray-700'">
                                        {{ v.quantity ?? 0 }}
                                    </td>
                                </tr>
                                <tr v-if="!product.variants?.length">
                                    <td colspan="5" class="px-4 py-6 text-center text-gray-400 text-sm">Chưa có biến thể</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>

                    <!-- ── LỊCH SỬ BÁN HÀNG ── -->
                    <div class="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
                        <div class="px-4 py-3 border-b border-gray-100 bg-gray-50 flex items-center justify-between">
                            <h3 class="font-semibold text-gray-900 text-sm flex items-center gap-2">
                                <ShoppingBag :size="15" class="text-indigo-500" />
                                Lịch sử bán hàng
                            </h3>
                            <span class="text-xs text-gray-400">{{ orderGroups.length }} đơn hàng</span>
                        </div>

                        <div v-if="!orderGroups.length" class="py-10 text-center text-sm text-gray-400">
                            Chưa có lịch sử bán hàng
                        </div>

                        <div v-else class="divide-y divide-gray-100">
                            <div v-for="group in orderGroups" :key="group.order?.id"
                                class="px-4 py-3 hover:bg-gray-50 transition-colors">
                                <!-- Order header -->
                                <div class="flex items-center justify-between mb-2">
                                    <div class="flex items-center gap-2">
                                        <button @click="router.visit(`/admin/b2b-orders/${group.order?.id}`)"
                                            class="font-mono text-xs font-semibold text-indigo-600 hover:underline">
                                            {{ group.order?.order_number ?? '#' + group.order?.id }}
                                        </button>
                                        <span class="text-xs text-gray-500">·</span>
                                        <span class="text-xs text-gray-600 font-medium">{{ group.order?.customer_name }}</span>
                                        <span class="text-xs text-gray-400">{{ fmtDate(group.order?.created_at) }}</span>
                                    </div>
                                    <div class="flex items-center gap-3 text-xs">
                                        <span class="text-gray-700 font-semibold">{{ fmt(group.subtotal) }}</span>
                                        <span v-if="group.profit > 0" class="text-orange-600 font-medium">
                                            lãi: {{ fmt(group.profit) }}
                                        </span>
                                    </div>
                                </div>

                                <!-- Items trong đơn -->
                                <div class="space-y-1 pl-2 border-l-2 border-indigo-100">
                                    <div v-for="item in group.items" :key="item.id"
                                        class="flex items-center justify-between text-xs text-gray-600">
                                        <div class="flex items-center gap-2 min-w-0">
                                            <span class="text-gray-400 shrink-0">{{ item.stt || '—' }}</span>
                                            <span class="truncate">{{ item.product_name }}</span>
                                            <span v-if="item.variant_sku" class="font-mono text-gray-400 shrink-0">{{ item.variant_sku }}</span>
                                        </div>
                                        <div class="flex items-center gap-3 shrink-0 ml-2">
                                            <span class="text-gray-500">{{ item.unit || '' }}</span>
                                            <span class="font-medium text-gray-700">x{{ fmtNum(item.quantity) }}</span>
                                            <span class="text-gray-500">{{ fmt(item.price) }}</span>
                                            <span class="font-semibold text-gray-800">= {{ fmt(Number(item.price) * Number(item.quantity)) }}</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Right: Meta -->
                <div class="space-y-4">
                    <!-- Basic info -->
                    <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-4 space-y-3">
                        <h3 class="font-semibold text-gray-900 text-sm">Thông tin chung</h3>
                        <dl class="space-y-2 text-sm">
                            <div class="flex justify-between">
                                <dt class="text-gray-500">Danh mục</dt>
                                <dd class="font-medium text-gray-900 text-right">{{ product.category?.name ?? '—' }}</dd>
                            </div>
                            <div class="flex justify-between">
                                <dt class="text-gray-500">Thương hiệu</dt>
                                <dd class="font-medium text-gray-900">{{ product.brand?.name ?? '—' }}</dd>
                            </div>
                            <div class="flex justify-between">
                                <dt class="text-gray-500">Slug</dt>
                                <dd class="font-mono text-xs text-gray-500 truncate max-w-32">{{ product.slug }}</dd>
                            </div>
                        </dl>
                    </div>

                    <!-- Price summary -->
                    <div v-if="product.default_variant" class="bg-white rounded-xl border border-gray-200 shadow-sm p-4 space-y-3">
                        <h3 class="font-semibold text-gray-900 text-sm">Giá (biến thể mặc định)</h3>
                        <dl class="space-y-2 text-sm">
                            <div class="flex justify-between">
                                <dt class="text-gray-500">Giá nhập</dt>
                                <dd class="text-gray-700">{{ fmt(product.default_variant.cost_price) }}</dd>
                            </div>
                            <div class="flex justify-between">
                                <dt class="text-gray-500">Giá gốc</dt>
                                <dd class="text-gray-400 line-through">{{ fmt(product.default_variant.original_price) }}</dd>
                            </div>
                            <div class="flex justify-between border-t border-gray-100 pt-2">
                                <dt class="font-semibold text-gray-900">Giá bán</dt>
                                <dd class="font-bold text-indigo-600">{{ fmt(product.default_variant.selling_price) }}</dd>
                            </div>
                            <div v-if="product.default_variant.cost_price && product.default_variant.selling_price"
                                class="flex justify-between">
                                <dt class="text-gray-500">Lợi nhuận</dt>
                                <dd class="font-medium text-emerald-600 text-xs">
                                    {{ fmt(product.default_variant.selling_price - product.default_variant.cost_price) }}
                                    ({{ Math.round((product.default_variant.selling_price - product.default_variant.cost_price) / product.default_variant.selling_price * 100) }}%)
                                </dd>
                            </div>
                        </dl>
                    </div>

                    <!-- Description -->
                    <div v-if="product.short_description || product.description"
                        class="bg-white rounded-xl border border-gray-200 shadow-sm p-4">
                        <h3 class="font-semibold text-gray-900 text-sm mb-2">Mô tả</h3>
                        <p v-if="product.short_description" class="text-sm text-gray-600 mb-2">{{ product.short_description }}</p>
                        <div v-if="product.description" class="text-xs text-gray-500 prose max-w-none" v-html="product.description" />
                    </div>

                    <!-- Images gallery -->
                    <div v-if="product.images?.length > 1" class="bg-white rounded-xl border border-gray-200 shadow-sm p-4">
                        <h3 class="font-semibold text-gray-900 text-sm mb-3">Hình ảnh ({{ product.images.length }})</h3>
                        <div class="grid grid-cols-3 gap-2">
                            <div v-for="img in product.images" :key="img.id"
                                class="aspect-square rounded-lg overflow-hidden bg-gray-100">
                                <img v-if="getImageUrl(img)" :src="getImageUrl(img)" class="h-full w-full object-cover" />
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </AdminLayout>
</template>
