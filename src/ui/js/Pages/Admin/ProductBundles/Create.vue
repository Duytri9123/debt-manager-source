<script setup>
import AdminLayout from '@/Layouts/AdminLayout.vue'
import { useForm, router } from '@inertiajs/vue3'
import { ref, computed } from 'vue'
import { ArrowLeft, Plus, Trash2, Search, Package, GripVertical, ChevronDown } from 'lucide-vue-next'

const props = defineProps({ products: Array })

// ── Form ──────────────────────────────────────────────────────────────────────
const form = useForm({
    name:        '',
    description: '',
    price:       '',
    status:      'active',
    category:    '',
    items:       [],
})

// ── Product search ────────────────────────────────────────────────────────────
const searchQuery   = ref('')
const showDropdown  = ref(false)
const selectedProd  = ref(null)   // product đang chọn để thêm

const filteredProducts = computed(() => {
    if (!searchQuery.value.trim()) return props.products?.slice(0, 20) ?? []
    const q = searchQuery.value.toLowerCase()
    return (props.products ?? []).filter(p => p.name.toLowerCase().includes(q)).slice(0, 20)
})

function selectProduct(product) {
    selectedProd.value  = product
    searchQuery.value   = product.name
    showDropdown.value  = false
}

function addItem() {
    if (!selectedProd.value) return
    const product = selectedProd.value

    // Nếu sản phẩm có nhiều variant → thêm từng variant riêng
    // Nếu không → thêm 1 dòng với variant mặc định
    const variant = product.default_variant ?? product.variants?.[0] ?? null

    form.items.push({
        product_id:         product.id,
        product_variant_id: variant?.id ?? null,
        product_name:       product.name,
        product_variants:   product.variants ?? [],
        variant_label:      getVariantLabel(variant),
        quantity:           1,
        note:               '',
        sort_order:         form.items.length,
        _key:               Date.now() + Math.random(),
    })

    searchQuery.value  = ''
    selectedProd.value = null
    showDropdown.value = false
}

function removeItem(idx) { form.items.splice(idx, 1) }

function getVariantLabel(variant) {
    if (!variant) return null
    const attrs = variant.attribute_values
    if (!attrs?.length) return variant.sku
    return attrs.map(a => a.value).join(' / ')
}

function getVariantPrice(item) {
    const v = item.product_variants?.find(v => v.id === item.product_variant_id)
           ?? item.product_variants?.[0]
    return v?.selling_price ?? 0
}

function lineTotal(item) {
    return getVariantPrice(item) * item.quantity
}

const grandTotal = computed(() => form.items.reduce((s, i) => s + lineTotal(i), 0))

function formatMoney(v) { return Number(v || 0).toLocaleString('vi-VN') + 'đ' }

// ── Submit ────────────────────────────────────────────────────────────────────
function submit() {
    const payload = {
        ...form.data(),
        price: form.price ? Number(form.price) : null,
        items: form.items.map((item, i) => ({
            product_id:         item.product_id,
            product_variant_id: item.product_variant_id,
            quantity:           item.quantity,
            note:               item.note,
            sort_order:         i,
        })),
    }
    form.transform(() => payload).post('/admin/product-bundles')
}
</script>

<template>
    <AdminLayout>
        <div class="space-y-5 max-w-5xl">
            <!-- Header -->
            <div class="flex items-center gap-3">
                <button @click="router.visit('/admin/product-bundles')"
                    class="p-2 rounded-lg hover:bg-gray-100 transition-colors">
                    <ArrowLeft :size="18" class="text-gray-600" />
                </button>
                <div>
                    <h1 class="text-xl font-bold text-gray-900">Tạo nhóm sản phẩm mới</h1>
                    <p class="text-sm text-gray-500">Ví dụ: Tủ điện 3 pha, Bộ kit điện, Combo...</p>
                </div>
            </div>

            <form @submit.prevent="submit" class="space-y-5">
                <div class="grid grid-cols-1 lg:grid-cols-3 gap-5">

                    <!-- Left: Items -->
                    <div class="lg:col-span-2 space-y-4">

                        <!-- Search & add product -->
                        <div class="bg-white rounded-xl border border-gray-200 p-4 space-y-3">
                            <h2 class="font-semibold text-gray-800 flex items-center gap-2">
                                <Package :size="16" class="text-indigo-600" /> Thêm thành phần
                            </h2>
                            <div class="flex gap-2">
                                <div class="flex-1 relative">
                                    <Search :size="14" class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                                    <input v-model="searchQuery"
                                        @focus="showDropdown = true"
                                        @blur="setTimeout(() => showDropdown = false, 200)"
                                        placeholder="Tìm sản phẩm..."
                                        class="w-full pl-9 pr-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                                    <!-- Dropdown -->
                                    <div v-if="showDropdown && filteredProducts.length"
                                        class="absolute z-20 top-full left-0 right-0 mt-1 bg-white border border-gray-200 rounded-xl shadow-lg max-h-56 overflow-y-auto">
                                        <button v-for="p in filteredProducts" :key="p.id"
                                            type="button"
                                            @mousedown.prevent="selectProduct(p)"
                                            class="w-full flex items-center gap-2 px-3 py-2 hover:bg-indigo-50 text-left transition-colors">
                                            <div class="w-8 h-8 rounded bg-gray-100 overflow-hidden shrink-0">
                                                <img v-if="p.thumbnail_image?.url" :src="p.thumbnail_image.url" class="w-full h-full object-cover" />
                                                <Package v-else :size="14" class="m-auto mt-1.5 text-gray-300" />
                                            </div>
                                            <div class="flex-1 min-w-0">
                                                <p class="text-sm font-medium text-gray-800 truncate">{{ p.name }}</p>
                                                <p class="text-xs text-gray-400">{{ p.variants?.length ?? 0 }} biến thể</p>
                                            </div>
                                        </button>
                                    </div>
                                </div>
                                <button type="button" @click="addItem"
                                    :disabled="!selectedProd"
                                    class="flex items-center gap-1.5 px-4 py-2 bg-indigo-600 text-white text-sm rounded-lg hover:bg-indigo-700 disabled:opacity-40 transition-colors">
                                    <Plus :size="15" /> Thêm
                                </button>
                            </div>
                        </div>

                        <!-- Items list -->
                        <div class="bg-white rounded-xl border border-gray-200 overflow-hidden">
                            <div class="px-4 py-3 border-b border-gray-100 bg-gray-50 flex items-center justify-between">
                                <span class="text-sm font-semibold text-gray-700">Danh sách thành phần</span>
                                <span class="text-xs text-gray-400">{{ form.items.length }} thành phần</span>
                            </div>

                            <div v-if="!form.items.length" class="text-center py-10 text-gray-400">
                                <Package :size="32" class="mx-auto mb-2 opacity-30" />
                                <p class="text-sm">Chưa có thành phần nào. Tìm và thêm sản phẩm ở trên.</p>
                            </div>

                            <div v-else class="divide-y divide-gray-100">
                                <div v-for="(item, idx) in form.items" :key="item._key"
                                    class="flex items-start gap-3 px-4 py-3 hover:bg-gray-50 transition-colors">
                                    <!-- Drag handle (visual only) -->
                                    <GripVertical :size="16" class="text-gray-300 mt-2 shrink-0 cursor-grab" />

                                    <!-- Number -->
                                    <span class="text-xs text-gray-400 mt-2.5 w-5 shrink-0 text-center">{{ idx + 1 }}</span>

                                    <!-- Product info -->
                                    <div class="flex-1 min-w-0 space-y-2">
                                        <p class="text-sm font-medium text-gray-800 truncate">{{ item.product_name }}</p>

                                        <!-- Variant selector -->
                                        <div v-if="item.product_variants?.length > 1">
                                            <select v-model="item.product_variant_id"
                                                class="w-full text-xs border border-gray-200 rounded-lg px-2 py-1.5 focus:outline-none focus:ring-2 focus:ring-indigo-500">
                                                <option v-for="v in item.product_variants" :key="v.id" :value="v.id">
                                                    {{ v.attribute_values?.map(a => a.value).join(' / ') || v.sku }}
                                                    — {{ Number(v.selling_price || 0).toLocaleString('vi-VN') }}đ
                                                </option>
                                            </select>
                                        </div>
                                        <div v-else class="text-xs text-gray-400">
                                            {{ item.variant_label ?? 'Mặc định' }}
                                            — {{ formatMoney(getVariantPrice(item)) }}
                                        </div>

                                        <!-- Note -->
                                        <input v-model="item.note" placeholder="Ghi chú (tùy chọn)"
                                            class="w-full text-xs border border-gray-200 rounded-lg px-2 py-1.5 focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                                    </div>

                                    <!-- Quantity -->
                                    <div class="flex items-center gap-1 shrink-0">
                                        <button type="button" @click="item.quantity = Math.max(1, item.quantity - 1)"
                                            class="w-7 h-7 rounded-lg border border-gray-200 flex items-center justify-center text-gray-500 hover:bg-gray-100 text-lg leading-none">−</button>
                                        <input v-model.number="item.quantity" type="number" min="1"
                                            class="w-12 text-center text-sm border border-gray-200 rounded-lg py-1 focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                                        <button type="button" @click="item.quantity++"
                                            class="w-7 h-7 rounded-lg border border-gray-200 flex items-center justify-center text-gray-500 hover:bg-gray-100 text-lg leading-none">+</button>
                                    </div>

                                    <!-- Line total -->
                                    <div class="text-right shrink-0 w-24">
                                        <p class="text-sm font-semibold text-gray-800">{{ formatMoney(lineTotal(item)) }}</p>
                                    </div>

                                    <!-- Remove -->
                                    <button type="button" @click="removeItem(idx)"
                                        class="p-1.5 rounded-lg hover:bg-red-50 text-red-400 transition-colors shrink-0 mt-0.5">
                                        <Trash2 :size="14" />
                                    </button>
                                </div>
                            </div>

                            <!-- Total row -->
                            <div v-if="form.items.length" class="border-t-2 border-gray-200 px-4 py-3 bg-gray-50 flex justify-between items-center">
                                <span class="text-sm font-semibold text-gray-700">Tổng giá trị thành phần:</span>
                                <span class="text-base font-bold text-indigo-600">{{ formatMoney(grandTotal) }}</span>
                            </div>
                        </div>

                        <p v-if="form.errors.items" class="text-sm text-red-500">{{ form.errors.items }}</p>
                    </div>

                    <!-- Right: Info -->
                    <div class="space-y-4">
                        <div class="bg-white rounded-xl border border-gray-200 p-4 space-y-4">
                            <h2 class="font-semibold text-gray-800">Thông tin nhóm</h2>

                            <div>
                                <label class="block text-sm font-medium text-gray-700 mb-1">
                                    Tên nhóm <span class="text-red-500">*</span>
                                </label>
                                <input v-model="form.name" required placeholder="VD: Tủ điện 3 pha 100A"
                                    class="w-full rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                                    :class="form.errors.name ? 'border-red-400' : 'border-gray-300'" />
                                <p v-if="form.errors.name" class="mt-1 text-xs text-red-500">{{ form.errors.name }}</p>
                            </div>

                            <div>
                                <label class="block text-sm font-medium text-gray-700 mb-1">Phân loại</label>
                                <input v-model="form.category" placeholder="VD: Tủ điện, Bộ kit, Combo..."
                                    class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                            </div>

                            <div>
                                <label class="block text-sm font-medium text-gray-700 mb-1">Giá bán cả bộ</label>
                                <div class="relative">
                                    <input v-model="form.price" type="number" min="0" placeholder="Để trống = tính theo thành phần"
                                        class="w-full rounded-lg border border-gray-300 px-3 py-2 pr-8 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                                    <span class="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-gray-400">đ</span>
                                </div>
                            </div>

                            <div>
                                <label class="block text-sm font-medium text-gray-700 mb-1">Mô tả</label>
                                <textarea v-model="form.description" rows="3" placeholder="Mô tả nhóm sản phẩm..."
                                    class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none" />
                            </div>

                            <div>
                                <label class="block text-sm font-medium text-gray-700 mb-1">Trạng thái</label>
                                <select v-model="form.status"
                                    class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                                    <option value="active">✅ Hoạt động</option>
                                    <option value="inactive">⏸ Tạm dừng</option>
                                </select>
                            </div>
                        </div>

                        <!-- Actions -->
                        <div class="flex flex-col gap-2">
                            <button type="submit" :disabled="form.processing || !form.items.length"
                                class="w-full py-2.5 rounded-lg bg-indigo-600 text-white text-sm font-medium hover:bg-indigo-700 disabled:opacity-50 transition-colors">
                                {{ form.processing ? 'Đang lưu...' : '💾 Tạo nhóm sản phẩm' }}
                            </button>
                            <button type="button" @click="router.visit('/admin/product-bundles')"
                                class="w-full py-2.5 rounded-lg border border-gray-300 text-gray-700 text-sm hover:bg-gray-50 transition-colors">
                                Hủy
                            </button>
                        </div>
                    </div>
                </div>
            </form>
        </div>
    </AdminLayout>
</template>
