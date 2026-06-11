<script setup>
import AdminLayout from '@/Layouts/AdminLayout.vue'
import { useForm, router } from '@inertiajs/vue3'
import { computed } from 'vue'

const props = defineProps({
    advance: Object,
    employees: Array,
    customers: Array,
    suppliers: Array,
    types: Object,
})

const form = useForm({
    type: props.advance.type ?? '',
    employee_id: props.advance.employee_id ?? '',
    customer_id: props.advance.customer_id ?? '',
    supplier_id: props.advance.supplier_id ?? '',
    advance_date: props.advance.advance_date ?? new Date().toISOString().split('T')[0],
    expected_return_date: props.advance.expected_return_date ?? '',
    amount: props.advance.amount ?? 0,
    purpose: props.advance.purpose ?? '',
    notes: props.advance.notes ?? '',
    status: props.advance.status ?? 'pending',
})

const typeOptions = computed(() => {
    if (props.types && typeof props.types === 'object') {
        return Object.entries(props.types).map(([value, label]) => ({ value, label }))
    }
    return [
        { value: 'employee', label: 'Nhân viên' },
        { value: 'customer', label: 'Khách hàng' },
        { value: 'supplier', label: 'Nhà cung cấp' },
    ]
})

function submit() {
    form.put('/admin/advances/' + props.advance.id)
}
</script>

<template>
    <AdminLayout>
        <div class="space-y-6">
            <!-- Header -->
            <div class="flex items-center gap-3">
                <button @click="router.visit('/admin/advances/' + advance.id)" class="text-gray-500 hover:text-gray-700 text-sm">← Quay lại</button>
                <h1 class="text-xl font-bold text-gray-900">Chỉnh sửa tạm ứng</h1>
            </div>

            <form @submit.prevent="submit" class="space-y-6">
                <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 space-y-4">
                    <h2 class="font-semibold text-gray-900">Thông tin tạm ứng</h2>

                    <div class="grid grid-cols-2 gap-4">
                        <!-- Type -->
                        <div class="col-span-2">
                            <label class="block text-sm font-medium text-gray-700 mb-1">
                                Loại tạm ứng <span class="text-red-500">*</span>
                            </label>
                            <select v-model="form.type"
                                class="w-full rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                                :class="form.errors.type ? 'border-red-400' : 'border-gray-300'">
                                <option value="">— Chọn loại —</option>
                                <option v-for="t in typeOptions" :key="t.value" :value="t.value">{{ t.label }}</option>
                            </select>
                            <p v-if="form.errors.type" class="mt-1 text-xs text-red-500">{{ form.errors.type }}</p>
                        </div>

                        <!-- Conditional person select -->
                        <div v-if="form.type === 'employee'" class="col-span-2">
                            <label class="block text-sm font-medium text-gray-700 mb-1">
                                Nhân viên <span class="text-red-500">*</span>
                            </label>
                            <select v-model="form.employee_id"
                                class="w-full rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                                :class="form.errors.employee_id ? 'border-red-400' : 'border-gray-300'">
                                <option value="">— Chọn nhân viên —</option>
                                <option v-for="e in employees" :key="e.id" :value="e.id">{{ e.name }}</option>
                            </select>
                            <p v-if="form.errors.employee_id" class="mt-1 text-xs text-red-500">{{ form.errors.employee_id }}</p>
                        </div>

                        <div v-if="form.type === 'customer'" class="col-span-2">
                            <label class="block text-sm font-medium text-gray-700 mb-1">
                                Khách hàng <span class="text-red-500">*</span>
                            </label>
                            <select v-model="form.customer_id"
                                class="w-full rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                                :class="form.errors.customer_id ? 'border-red-400' : 'border-gray-300'">
                                <option value="">— Chọn khách hàng —</option>
                                <option v-for="c in customers" :key="c.id" :value="c.id">{{ c.name }}</option>
                            </select>
                            <p v-if="form.errors.customer_id" class="mt-1 text-xs text-red-500">{{ form.errors.customer_id }}</p>
                        </div>

                        <div v-if="form.type === 'supplier'" class="col-span-2">
                            <label class="block text-sm font-medium text-gray-700 mb-1">
                                Nhà cung cấp <span class="text-red-500">*</span>
                            </label>
                            <select v-model="form.supplier_id"
                                class="w-full rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                                :class="form.errors.supplier_id ? 'border-red-400' : 'border-gray-300'">
                                <option value="">— Chọn nhà cung cấp —</option>
                                <option v-for="s in suppliers" :key="s.id" :value="s.id">{{ s.name }}</option>
                            </select>
                            <p v-if="form.errors.supplier_id" class="mt-1 text-xs text-red-500">{{ form.errors.supplier_id }}</p>
                        </div>

                        <!-- Advance date -->
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">
                                Ngày tạm ứng <span class="text-red-500">*</span>
                            </label>
                            <input v-model="form.advance_date" type="date"
                                class="w-full rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                                :class="form.errors.advance_date ? 'border-red-400' : 'border-gray-300'" />
                            <p v-if="form.errors.advance_date" class="mt-1 text-xs text-red-500">{{ form.errors.advance_date }}</p>
                        </div>

                        <!-- Expected return date -->
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">Ngày hoàn trả dự kiến</label>
                            <input v-model="form.expected_return_date" type="date"
                                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                        </div>

                        <!-- Amount -->
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">
                                Số tiền <span class="text-red-500">*</span>
                            </label>
                            <input v-model.number="form.amount" type="number" min="0"
                                class="w-full rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                                :class="form.errors.amount ? 'border-red-400' : 'border-gray-300'" />
                            <p v-if="form.errors.amount" class="mt-1 text-xs text-red-500">{{ form.errors.amount }}</p>
                        </div>

                        <!-- Status -->
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">Trạng thái</label>
                            <select v-model="form.status"
                                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                                <option value="pending">Chờ duyệt</option>
                                <option value="approved">Đã duyệt</option>
                                <option value="settled">Đã quyết toán</option>
                                <option value="cancelled">Đã hủy</option>
                            </select>
                        </div>

                        <!-- Purpose -->
                        <div class="col-span-2">
                            <label class="block text-sm font-medium text-gray-700 mb-1">Mục đích</label>
                            <input v-model="form.purpose" type="text"
                                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                        </div>

                        <!-- Notes -->
                        <div class="col-span-2">
                            <label class="block text-sm font-medium text-gray-700 mb-1">Ghi chú</label>
                            <textarea v-model="form.notes" rows="3"
                                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                        </div>
                    </div>
                </div>

                <!-- Actions -->
                <div class="flex gap-3 justify-end">
                    <button type="button" @click="router.visit('/admin/advances/' + advance.id)"
                        class="rounded-lg border border-gray-300 px-5 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors">
                        Hủy
                    </button>
                    <button type="submit" :disabled="form.processing"
                        class="rounded-lg bg-indigo-600 px-5 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50 transition-colors">
                        {{ form.processing ? 'Đang lưu...' : 'Lưu thay đổi' }}
                    </button>
                </div>
            </form>
        </div>
    </AdminLayout>
</template>
