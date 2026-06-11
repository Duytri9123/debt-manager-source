<script setup>
import AdminLayout from '@/Layouts/AdminLayout.vue'
import { useForm, router } from '@inertiajs/vue3'

const props = defineProps({
    supplier: Object,
})

const form = useForm({
    name: props.supplier.name ?? '',
    code: props.supplier.code ?? '',
    phone: props.supplier.phone ?? '',
    email: props.supplier.email ?? '',
    address: props.supplier.address ?? '',
    tax_code: props.supplier.tax_code ?? '',
    contact_person: props.supplier.contact_person ?? '',
    notes: props.supplier.notes ?? '',
    is_active: props.supplier.is_active ?? true,
})

function submit() {
    form.put('/admin/suppliers/' + props.supplier.id)
}
</script>

<template>
    <AdminLayout>
        <div class="space-y-6">
            <!-- Header -->
            <div class="flex items-center gap-3">
                <button @click="router.visit('/admin/suppliers/' + supplier.id)" class="text-gray-500 hover:text-gray-700 text-sm">← Quay lại</button>
                <h1 class="text-xl font-bold text-gray-900">Chỉnh sửa nhà cung cấp</h1>
            </div>

            <form @submit.prevent="submit" class="space-y-6">
                <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 space-y-4">
                    <h2 class="font-semibold text-gray-900">Thông tin nhà cung cấp</h2>

                    <div class="grid grid-cols-2 gap-4">
                        <!-- Name -->
                        <div class="col-span-2">
                            <label class="block text-sm font-medium text-gray-700 mb-1">
                                Tên nhà cung cấp <span class="text-red-500">*</span>
                            </label>
                            <input v-model="form.name" type="text" required
                                class="w-full rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                                :class="form.errors.name ? 'border-red-400' : 'border-gray-300'" />
                            <p v-if="form.errors.name" class="mt-1 text-xs text-red-500">{{ form.errors.name }}</p>
                        </div>

                        <!-- Code -->
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">Mã NCC</label>
                            <input v-model="form.code" type="text"
                                class="w-full rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                                :class="form.errors.code ? 'border-red-400' : 'border-gray-300'" />
                            <p v-if="form.errors.code" class="mt-1 text-xs text-red-500">{{ form.errors.code }}</p>
                        </div>

                        <!-- Tax code -->
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">Mã số thuế</label>
                            <input v-model="form.tax_code" type="text"
                                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                        </div>

                        <!-- Phone -->
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">Điện thoại</label>
                            <input v-model="form.phone" type="text"
                                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                        </div>

                        <!-- Email -->
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
                            <input v-model="form.email" type="email"
                                class="w-full rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                                :class="form.errors.email ? 'border-red-400' : 'border-gray-300'" />
                            <p v-if="form.errors.email" class="mt-1 text-xs text-red-500">{{ form.errors.email }}</p>
                        </div>

                        <!-- Contact person -->
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">Người liên hệ</label>
                            <input v-model="form.contact_person" type="text"
                                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                        </div>

                        <!-- Address -->
                        <div class="col-span-2">
                            <label class="block text-sm font-medium text-gray-700 mb-1">Địa chỉ</label>
                            <input v-model="form.address" type="text"
                                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                        </div>

                        <!-- Notes -->
                        <div class="col-span-2">
                            <label class="block text-sm font-medium text-gray-700 mb-1">Ghi chú</label>
                            <textarea v-model="form.notes" rows="3"
                                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                        </div>

                        <!-- Is active toggle -->
                        <div class="col-span-2 flex items-center gap-3">
                            <button type="button" @click="form.is_active = !form.is_active"
                                :class="['relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2',
                                    form.is_active ? 'bg-indigo-600' : 'bg-gray-200']">
                                <span :class="['inline-block h-4 w-4 transform rounded-full bg-white shadow transition-transform',
                                    form.is_active ? 'translate-x-6' : 'translate-x-1']" />
                            </button>
                            <span class="text-sm font-medium text-gray-700">
                                {{ form.is_active ? 'Đang hoạt động' : 'Ngừng hoạt động' }}
                            </span>
                        </div>
                    </div>
                </div>

                <!-- Actions -->
                <div class="flex gap-3 justify-end">
                    <button type="button" @click="router.visit('/admin/suppliers/' + supplier.id)"
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
