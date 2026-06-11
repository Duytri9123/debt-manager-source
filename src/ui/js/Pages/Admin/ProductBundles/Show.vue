<script setup>
import AdminLayout from '@/Layouts/AdminLayout.vue'
import { router, Link } from '@inertiajs/vue3'
import { computed } from 'vue'
import { ArrowLeft, Edit2, Trash2, Layers, Package, Tag, DollarSign } from 'lucide-vue-next'

const props = defineProps({ bundle: Object })

const totalValue = computed(() => {
    return props.bundle.items?.reduce((sum, item) => {
        const price = item.product_variant?.selling_price
                   ?? item.product?.default_variant?.selling_price
                   ?? 0
        return sum + (Number(price) * item.quantity)
    }, 0) ?? 0
})

function destroy() {
    if (!confirm(`Xóa nhóm sản phẩm "${props.bundle.name}"?`)) return
    router.delete(`/admin/product-bundles/${props.bundle.id}`)
}

function formatMoney(v) { return Number(v || 0).toLocaleString('vi-VN') + 'đ' }

function getVariantLabel(item) {
    if (!item.product_variant) return null
    const attrs = item.product_variant.attribute_values
    if (!attrs?.length) return item.product_variant.sku
    return attrs.map(a => a.value).join(' / ')
}
</script>

<template>
    <AdminLayout>
        <div class="space-y-5 max-w-4xl">
            <!-- Header -->
            <div class="flex items-center gap-3">
                <Link href="/admin/product-bundles" class="p-2 rounded-lg hover:bg-gray-100 transition-colors">
                    <ArrowLeft :size="18" class="text-gray-600" />
                </Link>
                <div class="flex-1">
                    <div class="flex items-center gap-2">
                        <Layers :size="20" class="text-indigo-600" />
                        <h1 class="text-xl font-bold text-gray-900">{{ bundle.name }}</h1>
                        <span :class="['text-xs px-2 py-0.5 rounded-full font-medium',
                            bundle.status === 'active' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500']">
                            {{ bundle.status === 'active' ? 'Hoạt động' : 'Tạm dừng' }}
                        </span>
                    </div>
                    <p v-if="bundle.category" class="text-sm text-indigo-600 mt-0.5">{{ bundle.category }}</p>
                </div>
                <div class="flex gap-2">
                    <Link :href="`/admin/product-bundles/${bundle.id}/edit`"
                        class="flex items-center gap-1.5 px-3 py-2 rounded-lg bg-amber-500 text-white text-sm hover:bg-amber-600 transition-colors">
                        <Edit2 :size="14" /> Chỉnh sửa
                    </Link>
                    <button @click="destroy"
                        class="flex items-center gap-1.5 px-3 py-2 rounded-lg bg-red-500 text-white text-sm hover:bg-red-600 transition-colors">
                        <Trash2 :size="14" /> Xóa
                    </button>
                </div>
            </div>

            <!-- Description -->
            <div v-if="bundle.description" class="bg-blue-50 border border-blue-200 rounded-xl px-4 py-3">
                <p class="text-sm text-blue-800">{{ bundle.description }}</p>
            </div>

            <!-- Summary cards -->
            <div class="grid grid-cols-3 gap-4">
                <div class="bg-white rounded-xl border border-gray-200 p-4 text-center">
                    <Package :size="20" class="mx-auto text-indigo-500 mb-1" />
                    <p class="text-2xl font-bold text-gray-900">{{ bundle.items?.length ?? 0 }}</p>
                    <p class="text-xs text-gray-500">Thành phần</p>
                </div>
                <div class="bg-white rounded-xl border border-gray-200 p-4 text-center">
                    <DollarSign :size="20" class="mx-auto text-green-500 mb-1" />
                    <p class="text-lg font-bold text-green-600">{{ formatMoney(totalValue) }}</p>
                    <p class="text-xs text-gray-500">Tổng giá trị</p>
                </div>
                <div class="bg-white rounded-xl border border-gray-200 p-4 text-center">
                    <Tag :size="20" class="mx-auto text-amber-500 mb-1" />
                    <p class="text-lg font-bold text-amber-600">{{ bundle.price ? formatMoney(bundle.price) : '—' }}</p>
                    <p class="text-xs text-gray-500">Giá bán bộ</p>
                </div>
            </div>

            <!-- Items table -->
            <div class="bg-white rounded-xl border border-gray-200 overflow-hidden">
                <div class="flex items-center gap-2 px-4 py-3 border-b border-gray-100 bg-gray-50">
                    <Package :size="16" class="text-indigo-600" />
                    <h2 class="font-semibold text-gray-800">Danh sách thành phần</h2>
                </div>
                <div class="overflow-x-auto">
                    <table class="w-full text-sm">
                        <thead class="bg-gray-50 border-b border-gray-100">
                            <tr>
                                <th class="text-left px-4 py-2.5 font-medium text-gray-600 w-8">#</th>
                                <th class="text-left px-4 py-2.5 font-medium text-gray-600">Sản phẩm</th>
                                <th class="text-left px-4 py-2.5 font-medium text-gray-600">Biến thể</th>
                                <th class="text-right px-4 py-2.5 font-medium text-gray-600">Đơn giá</th>
                                <th class="text-center px-4 py-2.5 font-medium text-gray-600">Số lượng</th>
                                <th class="text-right px-4 py-2.5 font-medium text-gray-600">Thành tiền</th>
                                <th class="text-left px-4 py-2.5 font-medium text-gray-600">Ghi chú</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-gray-100">
                            <tr v-for="(item, idx) in bundle.items" :key="item.id"
                                class="hover:bg-gray-50 transition-colors">
                                <td class="px-4 py-3 text-gray-400 text-xs">{{ idx + 1 }}</td>
                                <td class="px-4 py-3">
                                    <div class="flex items-center gap-2">
                                        <div class="w-9 h-9 rounded-lg bg-gray-100 overflow-hidden shrink-0">
                                            <img v-if="item.product?.thumbnail_image?.url"
                                                :src="item.product.thumbnail_image.url"
                                                class="w-full h-full object-cover" />
                                            <Package v-else :size="16" class="m-auto mt-2.5 text-gray-300" />
                                        </div>
                                        <div>
                                            <p class="font-medium text-gray-800">{{ item.product?.name ?? '—' }}</p>
                                            <p class="text-xs text-gray-400">SKU: {{ item.product_variant?.sku ?? item.product?.default_variant?.sku ?? '—' }}</p>
                                        </div>
                                    </div>
                                </td>
                                <td class="px-4 py-3 text-gray-600 text-xs">
                                    {{ getVariantLabel(item) ?? '—' }}
                                </td>
                                <td class="px-4 py-3 text-right text-gray-700">
                                    {{ formatMoney(item.product_variant?.selling_price ?? item.product?.default_variant?.selling_price) }}
                                </td>
                                <td class="px-4 py-3 text-center">
                                    <span class="inline-flex items-center justify-center w-8 h-8 rounded-lg bg-indigo-50 text-indigo-700 font-bold text-sm">
                                        {{ item.quantity }}
                                    </span>
                                </td>
                                <td class="px-4 py-3 text-right font-semibold text-gray-800">
                                    {{ formatMoney((item.product_variant?.selling_price ?? item.product?.default_variant?.selling_price ?? 0) * item.quantity) }}
                                </td>
                                <td class="px-4 py-3 text-xs text-gray-400">{{ item.note ?? '—' }}</td>
                            </tr>
                        </tbody>
                        <tfoot class="border-t-2 border-gray-200 bg-gray-50">
                            <tr>
                                <td colspan="5" class="px-4 py-3 text-right font-semibold text-gray-700">Tổng giá trị:</td>
                                <td class="px-4 py-3 text-right font-bold text-indigo-600 text-base">{{ formatMoney(totalValue) }}</td>
                                <td></td>
                            </tr>
                            <tr v-if="bundle.price">
                                <td colspan="5" class="px-4 py-2 text-right text-sm text-gray-500">Giá bán cả bộ:</td>
                                <td class="px-4 py-2 text-right font-bold text-green-600">{{ formatMoney(bundle.price) }}</td>
                                <td></td>
                            </tr>
                        </tfoot>
                    </table>
                </div>
            </div>
        </div>
    </AdminLayout>
</template>
