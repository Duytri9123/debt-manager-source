<script setup>
import AdminLayout from '@/Layouts/AdminLayout.vue'
import { router, Link } from '@inertiajs/vue3'
import { ref } from 'vue'
import { Plus, Search, Eye, Edit2, Trash2, Layers, RefreshCw } from 'lucide-vue-next'

const props = defineProps({
    bundles: Object,
    filters: Object,
})

const search = ref(props.filters?.search ?? '')
const status = ref(props.filters?.status ?? '')

function applyFilter() {
    router.get('/admin/product-bundles', {
        search: search.value || undefined,
        status: status.value || undefined,
    }, { preserveState: true, replace: true })
}

function destroy(id, name) {
    if (!confirm(`Xóa nhóm sản phẩm "${name}"?`)) return
    router.delete(`/admin/product-bundles/${id}`)
}

function formatMoney(v) { return v ? Number(v).toLocaleString('vi-VN') + 'đ' : '—' }
</script>

<template>
    <AdminLayout>
        <div class="space-y-5">
            <!-- Header -->
            <div class="flex items-center justify-between flex-wrap gap-3">
                <div>
                    <h1 class="text-xl font-bold text-gray-900 flex items-center gap-2">
                        <Layers :size="22" class="text-indigo-600" /> Nhóm sản phẩm
                    </h1>
                    <p class="text-sm text-gray-500 mt-0.5">Quản lý bộ sản phẩm tổ hợp (tủ điện, bộ kit, combo...)</p>
                </div>
                <Link href="/admin/product-bundles/create"
                    class="flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 transition-colors shrink-0 whitespace-nowrap">
                    <Plus :size="16" /> Tạo nhóm mới
                </Link>
            </div>

            <!-- Filters -->
            <div class="flex flex-wrap gap-3 bg-white rounded-xl border border-gray-200 p-3">
                <div class="flex-1 min-w-[200px] relative">
                    <Search :size="15" class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                    <input v-model="search" @keyup.enter="applyFilter"
                        placeholder="Tìm tên nhóm sản phẩm..."
                        class="w-full pl-9 pr-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                </div>
                <select v-model="status" @change="applyFilter"
                    class="text-sm border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500">
                    <option value="">Tất cả trạng thái</option>
                    <option value="active">✅ Đang hoạt động</option>
                    <option value="inactive">⏸ Tạm dừng</option>
                </select>
                <button @click="search=''; status=''; applyFilter()"
                    class="flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-700 px-3 py-2 rounded-lg hover:bg-gray-100 transition-colors">
                    <RefreshCw :size="14" /> Reset
                </button>
            </div>

            <!-- Grid -->
            <div v-if="!bundles.data?.length" class="text-center py-16 text-gray-400">
                <Layers :size="40" class="mx-auto mb-3 opacity-30" />
                <p class="font-medium">Chưa có nhóm sản phẩm nào</p>
                <p class="text-sm mt-1">Tạo nhóm để quản lý bộ sản phẩm tổ hợp như tủ điện, bộ kit...</p>
                <Link href="/admin/product-bundles/create"
                    class="inline-flex items-center gap-2 mt-4 px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm hover:bg-indigo-700 transition-colors">
                    <Plus :size="15" /> Tạo nhóm đầu tiên
                </Link>
            </div>

            <div v-else class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
                <div v-for="bundle in bundles.data" :key="bundle.id"
                    class="bg-white rounded-xl border border-gray-200 hover:border-indigo-300 hover:shadow-md transition-all overflow-hidden">
                    <!-- Card header -->
                    <div class="p-4 border-b border-gray-100">
                        <div class="flex items-start justify-between gap-2">
                            <div class="flex-1 min-w-0">
                                <h3 class="font-semibold text-gray-900 truncate">{{ bundle.name }}</h3>
                                <p v-if="bundle.category" class="text-xs text-indigo-600 mt-0.5">{{ bundle.category }}</p>
                            </div>
                            <span :class="['shrink-0 text-xs px-2 py-0.5 rounded-full font-medium',
                                bundle.status === 'active' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500']">
                                {{ bundle.status === 'active' ? 'Hoạt động' : 'Tạm dừng' }}
                            </span>
                        </div>
                        <p v-if="bundle.description" class="text-xs text-gray-500 mt-1.5 line-clamp-2">{{ bundle.description }}</p>
                    </div>

                    <!-- Items preview -->
                    <div class="px-4 py-3 space-y-1.5 max-h-40 overflow-y-auto">
                        <div v-for="item in bundle.items?.slice(0, 5)" :key="item.id"
                            class="flex items-center justify-between text-xs">
                            <span class="text-gray-700 truncate flex-1">
                                {{ item.product?.name ?? '—' }}
                                <span v-if="item.product_variant" class="text-gray-400">
                                    ({{ item.product_variant?.sku }})
                                </span>
                            </span>
                            <span class="shrink-0 ml-2 font-semibold text-indigo-600 bg-indigo-50 px-1.5 py-0.5 rounded">
                                x{{ item.quantity }}
                            </span>
                        </div>
                        <p v-if="bundle.items?.length > 5" class="text-xs text-gray-400 text-center pt-1">
                            +{{ bundle.items.length - 5 }} thành phần khác...
                        </p>
                    </div>

                    <!-- Footer -->
                    <div class="flex items-center justify-between px-4 py-3 border-t border-gray-100 bg-gray-50">
                        <div>
                            <p class="text-xs text-gray-400">{{ bundle.items_count }} thành phần</p>
                            <p v-if="bundle.price" class="text-sm font-bold text-indigo-600">{{ formatMoney(bundle.price) }}</p>
                        </div>
                        <div class="flex gap-1">
                            <Link :href="`/admin/product-bundles/${bundle.id}`"
                                class="p-1.5 rounded-lg hover:bg-indigo-50 text-indigo-600 transition-colors">
                                <Eye :size="14" />
                            </Link>
                            <Link :href="`/admin/product-bundles/${bundle.id}/edit`"
                                class="p-1.5 rounded-lg hover:bg-amber-50 text-amber-600 transition-colors">
                                <Edit2 :size="14" />
                            </Link>
                            <button @click="destroy(bundle.id, bundle.name)"
                                class="p-1.5 rounded-lg hover:bg-red-50 text-red-500 transition-colors">
                                <Trash2 :size="14" />
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Pagination -->
            <div v-if="bundles.last_page > 1" class="flex justify-center gap-1">
                <Link v-for="link in bundles.links" :key="link.label"
                    :href="link.url ?? '#'"
                    :class="['px-3 py-1.5 text-sm rounded-lg transition-colors',
                        link.active ? 'bg-indigo-600 text-white' : 'text-gray-600 hover:bg-gray-100',
                        !link.url ? 'opacity-40 pointer-events-none' : '']"
                    v-html="link.label" />
            </div>
        </div>
    </AdminLayout>
</template>
