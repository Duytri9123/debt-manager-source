<script setup>
import { ref } from 'vue'
import { useForm, router } from '@inertiajs/vue3'
import AdminLayout from '@/Layouts/AdminLayout.vue'
import { ArrowLeft, Save, Eye, EyeOff } from 'lucide-vue-next'

const showPassword = ref(false)

const form = useForm({
    name:     '',
    email:    '',
    password: '',
    isAdmin:  false,
})

function submit() {
    form.post('/admin/users', {
        onSuccess: () => {
            // Redirect handled by controller
        },
    })
}
</script>

<template>
    <AdminLayout>
        <div class="max-w-3xl space-y-5">
            <!-- Back -->
            <button @click="router.visit('/admin/users')"
                class="flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-700 transition-colors">
                <ArrowLeft :size="15" /> Quay lại danh sách
            </button>

            <!-- Form -->
            <div class="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
                <h1 class="text-xl font-bold text-gray-900 mb-5">Thêm người dùng mới</h1>

                <form @submit.prevent="submit" class="space-y-5">
                    <div class="grid grid-cols-1 gap-5 sm:grid-cols-2">
                        <!-- Tên -->
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1.5">
                                Tên <span class="text-red-500">*</span>
                            </label>
                            <input v-model="form.name" type="text" required
                                :class="['w-full rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500',
                                    form.errors.name ? 'border-red-300' : 'border-gray-300']"
                                placeholder="Nhập tên người dùng" />
                            <p v-if="form.errors.name" class="mt-1 text-xs text-red-600">{{ form.errors.name }}</p>
                        </div>

                        <!-- Email -->
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1.5">
                                Email <span class="text-red-500">*</span>
                            </label>
                            <input v-model="form.email" type="email" required
                                :class="['w-full rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500',
                                    form.errors.email ? 'border-red-300' : 'border-gray-300']"
                                placeholder="Nhập email" />
                            <p v-if="form.errors.email" class="mt-1 text-xs text-red-600">{{ form.errors.email }}</p>
                        </div>

                        <!-- Mật khẩu -->
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1.5">
                                Mật khẩu <span class="text-red-500">*</span>
                            </label>
                            <div class="relative">
                                <input v-model="form.password" :type="showPassword ? 'text' : 'password'" required
                                    :class="['w-full rounded-lg border px-3 py-2 pr-10 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500',
                                        form.errors.password ? 'border-red-300' : 'border-gray-300']"
                                    placeholder="Nhập mật khẩu (tối thiểu 8 ký tự)" />
                                <button type="button" @click="showPassword = !showPassword"
                                    class="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600">
                                    <Eye v-if="!showPassword" :size="16" />
                                    <EyeOff v-else :size="16" />
                                </button>
                            </div>
                            <p v-if="form.errors.password" class="mt-1 text-xs text-red-600">{{ form.errors.password }}</p>
                        </div>

                        <!-- Vai trò -->
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1.5">
                                Vai trò
                            </label>
                            <select v-model="form.isAdmin"
                                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                                <option :value="false">User</option>
                                <option :value="true">Admin</option>
                            </select>
                        </div>
                    </div>

                    <!-- Actions -->
                    <div class="flex gap-3 pt-3 border-t border-gray-200">
                        <button type="submit" :disabled="form.processing"
                            class="flex items-center gap-2 rounded-lg bg-indigo-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-indigo-700 disabled:opacity-60 transition-colors">
                            <Save :size="16" />
                            {{ form.processing ? 'Đang lưu...' : 'Tạo người dùng' }}
                        </button>
                        <button type="button" @click="router.visit('/admin/users')"
                            class="rounded-lg border border-gray-300 px-5 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors">
                            Hủy
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </AdminLayout>
</template>
