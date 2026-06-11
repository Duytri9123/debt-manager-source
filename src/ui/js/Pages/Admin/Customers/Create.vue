<script setup>
import { useForm, router } from '@inertiajs/vue3'
import AdminLayout from '@/Layouts/AdminLayout.vue'
import { ArrowLeft, Save } from 'lucide-vue-next'

const form = useForm({
    name:     '',
    phone:    '',
    email:    '',
    tax_code: '',
    address:  '',
    notes:    '',
})

function submit() {
    form.post('/admin/customers', {
        onSuccess: () => {
            // Redirect handled by controller
        },
    })
}
</script>

<template>
    <AdminLayout>
        <div class="space-y-5">
            <!-- Back -->
            <button @click="router.visit('/admin/customers')"
                class="flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-700 transition-colors">
                <ArrowLeft :size="15" /> Quay lại danh sách
            </button>

            <!-- Form -->
            <div class="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
                <h1 class="text-xl font-bold text-gray-900 mb-5">Thêm khách hàng mới</h1>

                <form @submit.prevent="submit" class="space-y-5">
                    <div class="grid grid-cols-1 gap-5 sm:grid-cols-2">
                        <!-- Tên -->
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1.5">
                                Tên khách hàng <span class="text-red-500">*</span>
                            </label>
                            <input v-model="form.name" type="text" required
                                :class="['w-full rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500',
                                    form.errors.name ? 'border-red-300' : 'border-gray-300']"
                                placeholder="Nhập tên khách hàng" />
                            <p v-if="form.errors.name" class="mt-1 text-xs text-red-600">{{ form.errors.name }}</p>
                        </div>

                        <!-- Số điện thoại -->
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1.5">
                                Số điện thoại
                            </label>
                            <input v-model="form.phone" type="text"
                                :class="['w-full rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500',
                                    form.errors.phone ? 'border-red-300' : 'border-gray-300']"
                                placeholder="Nhập số điện thoại" />
                            <p v-if="form.errors.phone" class="mt-1 text-xs text-red-600">{{ form.errors.phone }}</p>
                        </div>

                        <!-- Email -->
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1.5">
                                Email
                            </label>
                            <input v-model="form.email" type="email"
                                :class="['w-full rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500',
                                    form.errors.email ? 'border-red-300' : 'border-gray-300']"
                                placeholder="Nhập email (tùy chọn)" />
                            <p v-if="form.errors.email" class="mt-1 text-xs text-red-600">{{ form.errors.email }}</p>
                        </div>

                        <!-- Mã số thuế -->
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1.5">
                                Mã số thuế
                            </label>
                            <input v-model="form.tax_code" type="text"
                                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                                placeholder="Nhập mã số thuế (tùy chọn)" />
                        </div>

                        <!-- Địa chỉ -->
                        <div class="sm:col-span-2">
                            <label class="block text-sm font-medium text-gray-700 mb-1.5">
                                Địa chỉ
                            </label>
                            <input v-model="form.address" type="text"
                                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                                placeholder="Nhập địa chỉ (tùy chọn)" />
                        </div>

                        <!-- Ghi chú -->
                        <div class="sm:col-span-2">
                            <label class="block text-sm font-medium text-gray-700 mb-1.5">
                                Ghi chú
                            </label>
                            <textarea v-model="form.notes" rows="3"
                                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                                placeholder="Nhập ghi chú (tùy chọn)" />
                        </div>
                    </div>

                    <!-- Actions -->
                    <div class="flex gap-3 pt-3 border-t border-gray-200">
                        <button type="submit" :disabled="form.processing"
                            class="flex items-center gap-2 rounded-lg bg-indigo-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-indigo-700 disabled:opacity-60 transition-colors">
                            <Save :size="16" />
                            {{ form.processing ? 'Đang lưu...' : 'Lưu khách hàng' }}
                        </button>
                        <button type="button" @click="router.visit('/admin/customers')"
                            class="rounded-lg border border-gray-300 px-5 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors">
                            Hủy
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </AdminLayout>
</template>
