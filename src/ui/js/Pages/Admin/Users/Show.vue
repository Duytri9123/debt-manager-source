<script setup>
import { ref, computed } from 'vue'
import { useForm, router } from '@inertiajs/vue3'
import AdminLayout from '@/Layouts/AdminLayout.vue'
import { ArrowLeft, Edit, Ban, CheckCircle, Key, Eye, EyeOff, ShoppingBag, MapPin, CreditCard, Lock } from 'lucide-vue-next'
import { useCurrency } from '@/composables/useCurrency.js'

const props = defineProps({
    user:       Object,
    orderStats: Object,
})

const { formatVND } = useCurrency()

// ─── Edit form ────────────────────────────────────────────────────────────────
const editMode = ref(false)
const editForm = useForm({
    name:    props.user.name,
    email:   props.user.email,
    phone:   props.user.phone ?? '',
    address: props.user.address ?? '',
    isAdmin: props.user.isAdmin,
})
function submitEdit() {
    editForm.patch(`/admin/users/${props.user.id}`, {
        onSuccess: () => { editMode.value = false },
    })
}

// ─── Password form ────────────────────────────────────────────────────────────
const showPasswordModal  = ref(false)
const showPassword       = ref(false)
const showPasswordConfirm = ref(false)
const passwordForm = useForm({ password: '', password_confirmation: '' })
function submitPassword() {
    passwordForm.post(`/admin/users/${props.user.id}/password`, {
        onSuccess: () => { showPasswordModal.value = false; passwordForm.reset() },
    })
}

// ─── Ban/Unban ────────────────────────────────────────────────────────────────
const showBanModal = ref(false)
const banForm = useForm({ reason: '' })
function submitBan() {
    banForm.post(`/admin/users/${props.user.id}/ban`, {
        onSuccess: () => { showBanModal.value = false },
    })
}
function submitUnban() {
    if (confirm('Kích hoạt lại tài khoản này?')) {
        router.post(`/admin/users/${props.user.id}/unban`)
    }
}

// ─── Helpers ──────────────────────────────────────────────────────────────────
function fmtDate(d) {
    if (!d) return '—'
    return new Date(d).toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit', year: 'numeric' })
}
function fmtDateTime(d) {
    if (!d) return '—'
    return new Date(d).toLocaleString('vi-VN', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}

const ORDER_STATUS = {
    pending:    { label: 'Chờ xử lý',  cls: 'bg-yellow-100 text-yellow-700' },
    processing: { label: 'Đang xử lý', cls: 'bg-blue-100 text-blue-700' },
    shipped:    { label: 'Đang giao',  cls: 'bg-indigo-100 text-indigo-700' },
    delivered:  { label: 'Đã giao',   cls: 'bg-emerald-100 text-emerald-700' },
    cancelled:  { label: 'Đã hủy',    cls: 'bg-red-100 text-red-700' },
}
const PAY_STATUS = {
    paid:    { label: 'Đã TT',    cls: 'bg-emerald-100 text-emerald-700' },
    partial: { label: 'Một phần', cls: 'bg-blue-100 text-blue-700' },
    unpaid:  { label: 'Chưa TT',  cls: 'bg-orange-100 text-orange-700' },
}
</script>

<template>
    <AdminLayout>
        <div class="space-y-5">

            <!-- Back -->
            <button @click="router.visit('/admin/users')"
                class="flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-700 transition-colors">
                <ArrowLeft :size="15" /> Quay lại danh sách
            </button>

            <!-- ── Profile header ─────────────────────────────────────────── -->
            <div class="rounded-xl border border-gray-200 bg-white p-4 lg:p-6 shadow-sm">
                <div class="flex flex-wrap items-start justify-between gap-4">
                    <div class="flex items-center gap-4">
                        <div class="flex h-14 w-14 items-center justify-center rounded-full bg-indigo-100 text-xl font-bold text-indigo-600 shrink-0">
                            {{ user.name?.charAt(0)?.toUpperCase() ?? '?' }}
                        </div>
                        <div>
                            <h1 class="text-xl font-bold text-gray-900">{{ user.name }}</h1>
                            <p class="text-sm text-gray-500 mt-0.5">{{ user.email }}</p>
                            <p v-if="user.phone" class="text-sm text-gray-500">{{ user.phone }}</p>
                            <div class="mt-2 flex items-center gap-2 flex-wrap">
                                <span :class="['inline-flex rounded-full px-2 py-0.5 text-xs font-medium', user.isAdmin ? 'bg-purple-100 text-purple-700' : 'bg-blue-100 text-blue-700']">
                                    {{ user.isAdmin ? '👑 Admin' : '👤 User' }}
                                </span>
                                <span :class="['inline-flex rounded-full px-2 py-0.5 text-xs font-medium', user.is_banned ? 'bg-red-100 text-red-700' : 'bg-emerald-100 text-emerald-700']">
                                    {{ user.is_banned ? '🚫 Bị khóa' : '✅ Hoạt động' }}
                                </span>
                                <span v-if="user.email_verified_at" class="inline-flex rounded-full bg-teal-100 px-2 py-0.5 text-xs font-medium text-teal-700">
                                    ✉️ Đã xác thực
                                </span>
                            </div>
                        </div>
                    </div>
                    <!-- Action buttons -->
                    <div class="flex gap-2 flex-wrap">
                        <button @click="editMode = !editMode"
                            class="flex items-center gap-1.5 rounded-lg border border-gray-300 px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors">
                            <Edit :size="14" /> Chỉnh sửa
                        </button>
                        <button @click="showPasswordModal = true"
                            class="flex items-center gap-1.5 rounded-lg bg-indigo-600 px-3 py-2 text-sm font-medium text-white hover:bg-indigo-700 transition-colors">
                            <Key :size="14" /> Đổi mật khẩu
                        </button>
                        <button v-if="!user.is_banned && !user.isAdmin" @click="showBanModal = true"
                            class="flex items-center gap-1.5 rounded-lg bg-red-600 px-3 py-2 text-sm font-medium text-white hover:bg-red-700 transition-colors">
                            <Ban :size="14" /> Khóa
                        </button>
                        <button v-if="user.is_banned" @click="submitUnban"
                            class="flex items-center gap-1.5 rounded-lg bg-emerald-600 px-3 py-2 text-sm font-medium text-white hover:bg-emerald-700 transition-colors">
                            <CheckCircle :size="14" /> Mở khóa
                        </button>
                    </div>
                </div>
                <!-- Ban reason -->
                <div v-if="user.is_banned && user.banned_reason"
                    class="mt-3 rounded-lg bg-red-50 border border-red-200 p-3 text-sm text-red-700">
                    <span class="font-medium">Lý do khóa:</span> {{ user.banned_reason }}
                    <span class="ml-2 text-red-400">({{ fmtDateTime(user.banned_at) }})</span>
                </div>
            </div>

            <!-- ── Edit form ──────────────────────────────────────────────── -->
            <div v-if="editMode" class="rounded-xl border border-indigo-200 bg-indigo-50 p-4 lg:p-5 shadow-sm">
                <h2 class="font-semibold text-gray-900 mb-4">Chỉnh sửa thông tin</h2>
                <form @submit.prevent="submitEdit" class="space-y-4">
                    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">Tên</label>
                            <input v-model="editForm.name" type="text"
                                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                            <p v-if="editForm.errors.name" class="mt-1 text-xs text-red-600">{{ editForm.errors.name }}</p>
                        </div>
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
                            <input v-model="editForm.email" type="email"
                                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                            <p v-if="editForm.errors.email" class="mt-1 text-xs text-red-600">{{ editForm.errors.email }}</p>
                        </div>
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">Số điện thoại</label>
                            <input v-model="editForm.phone" type="text"
                                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                        </div>
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">Vai trò</label>
                            <select v-model="editForm.isAdmin"
                                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                                <option :value="false">User</option>
                                <option :value="true">Admin</option>
                            </select>
                        </div>
                        <div class="sm:col-span-2">
                            <label class="block text-sm font-medium text-gray-700 mb-1">Địa chỉ</label>
                            <input v-model="editForm.address" type="text"
                                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                        </div>
                    </div>
                    <div class="flex gap-2">
                        <button type="submit" :disabled="editForm.processing"
                            class="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-700 disabled:opacity-60 transition-colors">
                            {{ editForm.processing ? 'Đang lưu...' : 'Lưu thay đổi' }}
                        </button>
                        <button type="button" @click="editMode = false"
                            class="rounded-lg border border-gray-300 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors">
                            Hủy
                        </button>
                    </div>
                </form>
            </div>

            <!-- ── Stats ──────────────────────────────────────────────────── -->
            <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
                <div class="bg-white rounded-xl border border-gray-200 p-4 shadow-sm">
                    <p class="text-xs text-gray-500 mb-1">Tổng đơn hàng</p>
                    <p class="text-2xl font-bold text-gray-900">{{ orderStats?.total_count ?? 0 }}</p>
                </div>
                <div class="bg-white rounded-xl border border-gray-200 p-4 shadow-sm">
                    <p class="text-xs text-gray-500 mb-1">Tổng chi tiêu</p>
                    <p class="text-lg font-bold text-indigo-600">{{ formatVND(orderStats?.total_spent ?? 0) }}</p>
                </div>
                <div class="bg-white rounded-xl border border-gray-200 p-4 shadow-sm">
                    <p class="text-xs text-gray-500 mb-1">Đã giao</p>
                    <p class="text-2xl font-bold text-emerald-600">{{ orderStats?.delivered ?? 0 }}</p>
                </div>
                <div class="bg-white rounded-xl border border-gray-200 p-4 shadow-sm">
                    <p class="text-xs text-gray-500 mb-1">Chờ xử lý</p>
                    <p class="text-2xl font-bold text-yellow-600">{{ orderStats?.pending ?? 0 }}</p>
                </div>
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-3 gap-5">

                <!-- ── Thông tin tài khoản ─────────────────────────────── -->
                <div class="lg:col-span-1 space-y-5">

                    <div class="rounded-xl border border-gray-200 bg-white p-4 shadow-sm">
                        <h2 class="font-semibold text-gray-800 mb-3 flex items-center gap-2 text-sm">
                            <CreditCard :size="15" class="text-indigo-500" /> Thông tin tài khoản
                        </h2>
                        <dl class="space-y-2 text-sm">
                            <div class="flex justify-between">
                                <dt class="text-gray-500">ID:</dt>
                                <dd class="font-mono text-gray-700">{{ user.id }}</dd>
                            </div>
                            <div class="flex justify-between">
                                <dt class="text-gray-500">Tên:</dt>
                                <dd class="font-medium text-gray-900">{{ user.name }}</dd>
                            </div>
                            <div class="flex justify-between">
                                <dt class="text-gray-500">Email:</dt>
                                <dd class="text-gray-700 truncate max-w-[180px]">{{ user.email }}</dd>
                            </div>
                            <div class="flex justify-between">
                                <dt class="text-gray-500">SĐT:</dt>
                                <dd class="text-gray-700">{{ user.phone || '—' }}</dd>
                            </div>
                            <div class="flex justify-between">
                                <dt class="text-gray-500">Địa chỉ:</dt>
                                <dd class="text-gray-700 text-right max-w-[180px] truncate">{{ user.address || '—' }}</dd>
                            </div>
                            <div class="flex justify-between">
                                <dt class="text-gray-500">Vai trò:</dt>
                                <dd>
                                    <span :class="['px-2 py-0.5 rounded-full text-xs font-medium', user.isAdmin ? 'bg-purple-100 text-purple-700' : 'bg-blue-100 text-blue-700']">
                                        {{ user.isAdmin ? 'Admin' : 'User' }}
                                    </span>
                                </dd>
                            </div>
                            <div class="flex justify-between">
                                <dt class="text-gray-500">Trạng thái:</dt>
                                <dd>
                                    <span :class="['px-2 py-0.5 rounded-full text-xs font-medium', user.is_banned ? 'bg-red-100 text-red-700' : 'bg-emerald-100 text-emerald-700']">
                                        {{ user.is_banned ? 'Bị khóa' : 'Hoạt động' }}
                                    </span>
                                </dd>
                            </div>
                            <div class="flex justify-between">
                                <dt class="text-gray-500">Xác thực email:</dt>
                                <dd class="text-gray-700">{{ user.email_verified_at ? fmtDate(user.email_verified_at) : 'Chưa xác thực' }}</dd>
                            </div>
                            <div class="flex justify-between">
                                <dt class="text-gray-500">Ngày tạo:</dt>
                                <dd class="text-gray-700">{{ fmtDateTime(user.created_at) }}</dd>
                            </div>
                        </dl>
                    </div>

                    <!-- Mật khẩu -->
                    <div class="rounded-xl border border-gray-200 bg-white p-4 shadow-sm">
                        <h2 class="font-semibold text-gray-800 mb-3 flex items-center gap-2 text-sm">
                            <Lock :size="15" class="text-indigo-500" /> Bảo mật
                        </h2>
                        <div class="flex items-center justify-between">
                            <div>
                                <p class="text-sm text-gray-600">Mật khẩu</p>
                                <p class="text-xs text-gray-400 mt-0.5">Được mã hóa, không thể xem trực tiếp</p>
                            </div>
                            <button @click="showPasswordModal = true"
                                class="flex items-center gap-1.5 rounded-lg bg-indigo-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-indigo-700 transition-colors">
                                <Key :size="12" /> Đặt lại
                            </button>
                        </div>
                    </div>

                    <!-- Địa chỉ giao hàng -->
                    <div class="rounded-xl border border-gray-200 bg-white p-4 shadow-sm">
                        <h2 class="font-semibold text-gray-800 mb-3 flex items-center gap-2 text-sm">
                            <MapPin :size="15" class="text-indigo-500" /> Địa chỉ giao hàng
                            <span class="ml-auto text-xs text-gray-400">{{ user.addresses?.length ?? 0 }} địa chỉ</span>
                        </h2>
                        <div v-if="user.addresses?.length" class="space-y-2">
                            <div v-for="addr in user.addresses" :key="addr.id"
                                :class="['rounded-lg border p-3 text-sm', addr.is_default ? 'border-indigo-200 bg-indigo-50' : 'border-gray-100']">
                                <div class="flex items-center justify-between mb-1">
                                    <span class="font-medium text-gray-900">{{ addr.receiver_name }}</span>
                                    <span v-if="addr.is_default" class="text-[10px] bg-indigo-100 text-indigo-700 px-1.5 py-0.5 rounded-full font-medium">Mặc định</span>
                                </div>
                                <p class="text-gray-500 text-xs">{{ addr.receiver_phone }}</p>
                                <p class="text-gray-600 text-xs mt-0.5">{{ addr.full_address || addr.address_line_1 }}</p>
                            </div>
                        </div>
                        <p v-else class="text-sm text-gray-400 text-center py-3">Chưa có địa chỉ</p>
                    </div>
                </div>

                <!-- ── Đơn hàng ────────────────────────────────────────── -->
                <div class="lg:col-span-2">
                    <div class="rounded-xl border border-gray-200 bg-white shadow-sm overflow-hidden">
                        <div class="px-4 py-3 border-b bg-indigo-50 flex items-center gap-2">
                            <ShoppingBag :size="15" class="text-indigo-600" />
                            <h2 class="font-semibold text-indigo-900 text-sm">Đơn hàng gần đây</h2>
                            <span class="ml-auto text-xs bg-indigo-200 text-indigo-700 px-2 py-0.5 rounded-full font-medium">
                                {{ orderStats?.total_count ?? 0 }} đơn
                            </span>
                        </div>
                        <div v-if="!user.orders?.length" class="py-12 text-center text-sm text-gray-400">
                            Chưa có đơn hàng
                        </div>
                        <div v-else class="divide-y divide-gray-100">
                            <div v-for="order in user.orders" :key="order.id"
                                class="px-4 py-3 hover:bg-gray-50 cursor-pointer transition-colors flex items-center justify-between gap-3"
                                @click="router.visit(`/admin/b2b-orders/${order.id}`)">
                                <div class="min-w-0">
                                    <p class="font-medium text-gray-900 text-sm truncate">
                                        {{ order.order_name || order.order_number }}
                                    </p>
                                    <p class="text-xs text-gray-400 font-mono">{{ order.order_number }}</p>
                                    <p class="text-xs text-gray-400 mt-0.5">{{ fmtDate(order.created_at) }}</p>
                                </div>
                                <div class="flex items-center gap-2 shrink-0">
                                    <span :class="['text-xs px-2 py-0.5 rounded-full font-medium', ORDER_STATUS[order.status]?.cls ?? 'bg-gray-100 text-gray-600']">
                                        {{ ORDER_STATUS[order.status]?.label ?? order.status }}
                                    </span>
                                    <span :class="['text-xs px-2 py-0.5 rounded-full font-medium', PAY_STATUS[order.payment_status]?.cls ?? 'bg-gray-100 text-gray-600']">
                                        {{ PAY_STATUS[order.payment_status]?.label ?? order.payment_status }}
                                    </span>
                                    <span class="text-sm font-semibold text-gray-900">{{ formatVND(order.grand_total) }}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- ── Password modal ─────────────────────────────────────────────── -->
        <div v-if="showPasswordModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
            <div class="w-full max-w-md rounded-2xl bg-white p-6 shadow-2xl">
                <h3 class="text-lg font-bold text-gray-900 mb-1">Đặt lại mật khẩu</h3>
                <p class="text-sm text-gray-500 mb-4">Đặt mật khẩu mới cho <strong>{{ user.name }}</strong></p>
                <form @submit.prevent="submitPassword" class="space-y-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1.5">Mật khẩu mới</label>
                        <div class="relative">
                            <input v-model="passwordForm.password" :type="showPassword ? 'text' : 'password'" required
                                :class="['w-full rounded-lg border px-3 py-2 pr-10 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500',
                                    passwordForm.errors.password ? 'border-red-300' : 'border-gray-300']"
                                placeholder="Tối thiểu 8 ký tự" />
                            <button type="button" @click="showPassword = !showPassword"
                                class="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600">
                                <Eye v-if="!showPassword" :size="16" /><EyeOff v-else :size="16" />
                            </button>
                        </div>
                        <p v-if="passwordForm.errors.password" class="mt-1 text-xs text-red-600">{{ passwordForm.errors.password }}</p>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1.5">Xác nhận mật khẩu</label>
                        <div class="relative">
                            <input v-model="passwordForm.password_confirmation" :type="showPasswordConfirm ? 'text' : 'password'" required
                                class="w-full rounded-lg border border-gray-300 px-3 py-2 pr-10 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                                placeholder="Nhập lại mật khẩu mới" />
                            <button type="button" @click="showPasswordConfirm = !showPasswordConfirm"
                                class="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600">
                                <Eye v-if="!showPasswordConfirm" :size="16" /><EyeOff v-else :size="16" />
                            </button>
                        </div>
                    </div>
                    <div class="flex gap-2 pt-1">
                        <button type="submit" :disabled="passwordForm.processing"
                            class="flex-1 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-700 disabled:opacity-60 transition-colors">
                            {{ passwordForm.processing ? 'Đang lưu...' : 'Đặt lại mật khẩu' }}
                        </button>
                        <button type="button" @click="showPasswordModal = false; passwordForm.reset()"
                            class="flex-1 rounded-lg border border-gray-300 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors">
                            Hủy
                        </button>
                    </div>
                </form>
            </div>
        </div>

        <!-- ── Ban modal ──────────────────────────────────────────────────── -->
        <div v-if="showBanModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
            <div class="w-full max-w-md rounded-2xl bg-white p-6 shadow-2xl">
                <h3 class="text-lg font-bold text-gray-900 mb-1">Khóa tài khoản</h3>
                <p class="text-sm text-gray-500 mb-4">Nhập lý do khóa <strong>{{ user.name }}</strong></p>
                <form @submit.prevent="submitBan" class="space-y-4">
                    <textarea v-model="banForm.reason" rows="3" required maxlength="500"
                        class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-red-500"
                        placeholder="Lý do khóa tài khoản..." />
                    <div class="flex gap-2">
                        <button type="submit" :disabled="banForm.processing"
                            class="flex-1 rounded-lg bg-red-600 px-4 py-2 text-sm font-semibold text-white hover:bg-red-700 disabled:opacity-60 transition-colors">
                            {{ banForm.processing ? 'Đang xử lý...' : 'Xác nhận khóa' }}
                        </button>
                        <button type="button" @click="showBanModal = false"
                            class="flex-1 rounded-lg border border-gray-300 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors">
                            Hủy
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </AdminLayout>
</template>
