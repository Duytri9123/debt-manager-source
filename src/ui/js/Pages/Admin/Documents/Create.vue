<script setup>
import AdminLayout from '@/Layouts/AdminLayout.vue'
import { useForm, router } from '@inertiajs/vue3'
import { Plus, Trash2 } from 'lucide-vue-next'

const props = defineProps({
    suppliers: Array,
    customers: Array,
    products: Array,
    types: Object,
})

const form = useForm({
    type: '',
    title: '',
    supplier_id: '',
    customer_id: '',
    document_date: new Date().toISOString().split('T')[0],
    status: 'draft',
    content: '',
    notes: '',
    items: [{ product_id: null, product_name: '', unit: '', expected_quantity: 0, actual_quantity: 0, notes: '' }],
})

function addItem() {
    form.items.push({ product_id: null, product_name: '', unit: '', expected_quantity: 0, actual_quantity: 0, notes: '' })
}

function removeItem(i) {
    form.items.splice(i, 1)
}

function onProductSelect(i, productId) {
    const product = props.products?.find(p => p.id == productId)
    if (product) {
        form.items[i].product_id = product.id
        form.items[i].product_name = product.name
        const variant = product.variants?.[0]
        if (variant) {
            form.items[i].unit = variant.unit ?? ''
        }
    }
}

const typeOptions = [
    { value: 'delivery', label: 'Giao hàng' },
    { value: 'inventory', label: 'Kiểm kho' },
    { value: 'return', label: 'Trả hàng' },
    { value: 'other', label: 'Khác' },
]

function submit() {
    form.post('/admin/documents')
}
</script>

<template>
    <AdminLayout>
        <div class="space-y-6">
            <!-- Header -->
            <div class="flex items-center gap-3">
                <button @click="router.visit('/admin/documents')" class="text-gray-500 hover:text-gray-700 text-sm">← Quay lại</button>
                <h1 class="text-xl font-bold text-gray-900">Tạo biên bản</h1>
            </div>

            <form @submit.prevent="submit" class="space-y-6">
                <!-- General info -->
                <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                    <h2 class="font-semibold text-gray-900 mb-4">Thông tin biên bản</h2>
                    <div class="grid grid-cols-2 gap-4">
                        <!-- Type -->
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">
                                Loại biên bản <span class="text-red-500">*</span>
                            </label>
                            <select v-model="form.type"
                                class="w-full rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                                :class="form.errors.type ? 'border-red-400' : 'border-gray-300'">
                                <option value="">— Chọn loại —</option>
                                <option v-for="t in typeOptions" :key="t.value" :value="t.value">{{ t.label }}</option>
                            </select>
                            <p v-if="form.errors.type" class="mt-1 text-xs text-red-500">{{ form.errors.type }}</p>
                        </div>

                        <!-- Status -->
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">Trạng thái</label>
                            <select v-model="form.status"
                                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                                <option value="draft">Nháp</option>
                                <option value="confirmed">Đã xác nhận</option>
                                <option value="cancelled">Đã hủy</option>
                            </select>
                        </div>

                        <!-- Title -->
                        <div class="col-span-2">
                            <label class="block text-sm font-medium text-gray-700 mb-1">
                                Tiêu đề <span class="text-red-500">*</span>
                            </label>
                            <input v-model="form.title" type="text"
                                class="w-full rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                                :class="form.errors.title ? 'border-red-400' : 'border-gray-300'" />
                            <p v-if="form.errors.title" class="mt-1 text-xs text-red-500">{{ form.errors.title }}</p>
                        </div>

                        <!-- Supplier -->
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">Nhà cung cấp</label>
                            <select v-model="form.supplier_id"
                                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                                <option value="">— Không chọn —</option>
                                <option v-for="s in suppliers" :key="s.id" :value="s.id">{{ s.name }}</option>
                            </select>
                        </div>

                        <!-- Customer -->
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">Khách hàng</label>
                            <select v-model="form.customer_id"
                                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                                <option value="">— Không chọn —</option>
                                <option v-for="c in customers" :key="c.id" :value="c.id">{{ c.name }}</option>
                            </select>
                        </div>

                        <!-- Document date -->
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">Ngày biên bản</label>
                            <input v-model="form.document_date" type="date"
                                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                        </div>

                        <!-- Content -->
                        <div class="col-span-2">
                            <label class="block text-sm font-medium text-gray-700 mb-1">Nội dung</label>
                            <textarea v-model="form.content" rows="4"
                                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                        </div>

                        <!-- Notes -->
                        <div class="col-span-2">
                            <label class="block text-sm font-medium text-gray-700 mb-1">Ghi chú</label>
                            <textarea v-model="form.notes" rows="2"
                                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                        </div>
                    </div>
                </div>

                <!-- Items -->
                <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                    <div class="flex items-center justify-between mb-4">
                        <h2 class="font-semibold text-gray-900">Danh sách hàng hóa</h2>
                        <button type="button" @click="addItem"
                            class="flex items-center gap-1.5 rounded-lg border border-indigo-300 px-3 py-1.5 text-sm text-indigo-600 hover:bg-indigo-50 transition-colors">
                            <Plus :size="14" /> Thêm dòng
                        </button>
                    </div>

                    <div class="overflow-x-auto">
                        <table class="w-full text-sm">
                            <thead>
                                <tr class="border-b border-gray-200">
                                    <th class="text-left pb-2 font-medium text-gray-600 w-44">Sản phẩm</th>
                                    <th class="text-left pb-2 font-medium text-gray-600 w-32">Tên hàng</th>
                                    <th class="text-left pb-2 font-medium text-gray-600 w-20">ĐVT</th>
                                    <th class="text-right pb-2 font-medium text-gray-600 w-24">SL dự kiến</th>
                                    <th class="text-right pb-2 font-medium text-gray-600 w-24">SL thực tế</th>
                                    <th class="text-left pb-2 font-medium text-gray-600">Ghi chú</th>
                                    <th class="w-8"></th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-gray-100">
                                <tr v-for="(item, i) in form.items" :key="i">
                                    <td class="py-2 pr-2">
                                        <select @change="e => onProductSelect(i, e.target.value)"
                                            class="w-full rounded border border-gray-200 px-2 py-1.5 text-xs focus:outline-none focus:ring-1 focus:ring-indigo-500">
                                            <option value="">— Chọn SP —</option>
                                            <option v-for="p in products" :key="p.id" :value="p.id">{{ p.name }}</option>
                                        </select>
                                    </td>
                                    <td class="py-2 pr-2">
                                        <input v-model="item.product_name" type="text" placeholder="Tên hàng"
                                            class="w-full rounded border border-gray-200 px-2 py-1.5 text-xs focus:outline-none focus:ring-1 focus:ring-indigo-500" />
                                    </td>
                                    <td class="py-2 pr-2">
                                        <input v-model="item.unit" type="text" placeholder="cái"
                                            class="w-full rounded border border-gray-200 px-2 py-1.5 text-xs focus:outline-none focus:ring-1 focus:ring-indigo-500" />
                                    </td>
                                    <td class="py-2 pr-2">
                                        <input v-model.number="item.expected_quantity" type="number" min="0" step="0.001"
                                            class="w-full rounded border border-gray-200 px-2 py-1.5 text-xs text-right focus:outline-none focus:ring-1 focus:ring-indigo-500" />
                                    </td>
                                    <td class="py-2 pr-2">
                                        <input v-model.number="item.actual_quantity" type="number" min="0" step="0.001"
                                            class="w-full rounded border border-gray-200 px-2 py-1.5 text-xs text-right focus:outline-none focus:ring-1 focus:ring-indigo-500" />
                                    </td>
                                    <td class="py-2 pr-2">
                                        <input v-model="item.notes" type="text" placeholder="Ghi chú"
                                            class="w-full rounded border border-gray-200 px-2 py-1.5 text-xs focus:outline-none focus:ring-1 focus:ring-indigo-500" />
                                    </td>
                                    <td class="py-2">
                                        <button type="button" @click="removeItem(i)" :disabled="form.items.length === 1"
                                            class="text-red-400 hover:text-red-600 disabled:opacity-30 transition-colors">
                                            <Trash2 :size="14" />
                                        </button>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>

                <!-- Submit -->
                <div class="flex gap-3 justify-end">
                    <button type="button" @click="router.visit('/admin/documents')"
                        class="rounded-lg border border-gray-300 px-5 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors">
                        Hủy
                    </button>
                    <button type="submit" :disabled="form.processing"
                        class="rounded-lg bg-indigo-600 px-5 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50 transition-colors">
                        {{ form.processing ? 'Đang lưu...' : 'Tạo biên bản' }}
                    </button>
                </div>
            </form>
        </div>
    </AdminLayout>
</template>
