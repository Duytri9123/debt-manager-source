<script setup>
import AdminLayout from '@/Layouts/AdminLayout.vue'
import { useForm, router, usePage } from '@inertiajs/vue3'
import { ref, computed } from 'vue'
import { ArrowLeft, Upload, FileSpreadsheet, CheckCircle, AlertTriangle, Info } from 'lucide-vue-next'

const page = usePage()
const flash = computed(() => page.props.flash)

const form = useForm({ file: null })
const fileInput = ref(null)
const dragOver  = ref(false)
const fileName  = ref('')

function onFileChange(e) {
    const f = e.target.files?.[0]
    if (f) { form.file = f; fileName.value = f.name }
}

function onDrop(e) {
    dragOver.value = false
    const f = e.dataTransfer.files?.[0]
    if (f && (f.name.endsWith('.xlsx') || f.name.endsWith('.xls'))) {
        form.file = f; fileName.value = f.name
    }
}

function submit() {
    form.post('/admin/b2b-orders/import', {
        forceFormData: true,
    })
}
</script>

<template>
    <AdminLayout>
        <div class="space-y-5 max-w-2xl">
            <!-- Header -->
            <div class="flex items-center gap-3">
                <button @click="router.visit('/admin/b2b-orders')"
                    class="p-2 rounded-lg hover:bg-gray-100 transition-colors">
                    <ArrowLeft :size="18" class="text-gray-600" />
                </button>
                <div>
                    <h1 class="text-xl font-bold text-gray-900">Import Excel</h1>
                    <p class="text-sm text-gray-500">Nhập dữ liệu từ file Excel theo dõi đơn hàng</p>
                </div>
            </div>

            <!-- Success/Error flash -->
            <div v-if="flash?.success" class="flex items-start gap-3 rounded-xl bg-emerald-50 border border-emerald-200 px-4 py-3">
                <CheckCircle :size="18" class="text-emerald-500 shrink-0 mt-0.5" />
                <div>
                    <p class="text-sm font-medium text-emerald-800">{{ flash.success }}</p>
                    <ul v-if="flash.import_errors?.length" class="mt-2 space-y-0.5">
                        <li v-for="(err, i) in flash.import_errors" :key="i"
                            class="text-xs text-amber-700">⚠️ {{ err }}</li>
                    </ul>
                </div>
            </div>

            <!-- Info box -->
            <div class="flex items-start gap-3 rounded-xl bg-blue-50 border border-blue-200 px-4 py-3">
                <Info :size="16" class="text-blue-500 shrink-0 mt-0.5" />
                <div class="text-sm text-blue-800 space-y-1">
                    <p class="font-medium">Định dạng file Excel được hỗ trợ:</p>
                    <ul class="text-xs space-y-0.5 text-blue-700 list-disc list-inside">
                        <li>File .xlsx hoặc .xls, tối đa 10MB</li>
                        <li>Cấu trúc: KHÁCH HÀNG | NGÀY ĐẶT | TT | MÔ TẢ | MÃ HÀNG | XUẤT XỨ | ĐƠN VỊ | SỐ LƯỢNG | ĐƠN GIÁ | THÀNH TIỀN | GHI CHÚ | ĐẦU VÀO | GIÁ BÁN | % KD | LÃI/KG | KL(KG) | LÃI TỔNG</li>
                        <li>Mỗi sheet là 1 tháng (T01, T02, ...) — bỏ qua sheet: foxz, TỔNG, HH+DS</li>
                        <li>Dữ liệu trùng sẽ được thêm mới (không ghi đè)</li>
                    </ul>
                </div>
            </div>

            <!-- Upload form -->
            <div class="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
                <form @submit.prevent="submit" class="space-y-5">
                    <!-- Drop zone -->
                    <div
                        @dragover.prevent="dragOver = true"
                        @dragleave="dragOver = false"
                        @drop.prevent="onDrop"
                        @click="fileInput.click()"
                        :class="['border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition-colors',
                            dragOver ? 'border-indigo-400 bg-indigo-50' : 'border-gray-300 hover:border-indigo-300 hover:bg-gray-50']">
                        <input ref="fileInput" type="file" accept=".xlsx,.xls" class="hidden" @change="onFileChange" />
                        <FileSpreadsheet :size="40" :class="['mx-auto mb-3', fileName ? 'text-emerald-500' : 'text-gray-300']" />
                        <p v-if="fileName" class="text-sm font-semibold text-emerald-700">✅ {{ fileName }}</p>
                        <p v-else class="text-sm text-gray-500">
                            Kéo thả file Excel vào đây hoặc <span class="text-indigo-600 font-medium">click để chọn</span>
                        </p>
                        <p class="text-xs text-gray-400 mt-1">Hỗ trợ .xlsx, .xls — tối đa 10MB</p>
                    </div>

                    <p v-if="form.errors.file" class="text-sm text-red-500">{{ form.errors.file }}</p>

                    <div class="flex gap-3 justify-end">
                        <button type="button" @click="router.visit('/admin/b2b-orders')"
                            class="rounded-lg border border-gray-300 px-5 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors">
                            Hủy
                        </button>
                        <button type="submit" :disabled="form.processing || !form.file"
                            class="flex items-center gap-2 rounded-lg bg-indigo-600 px-5 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50 transition-colors">
                            <Upload :size="15" />
                            {{ form.processing ? 'Đang import...' : 'Import dữ liệu' }}
                        </button>
                    </div>
                </form>
            </div>

            <!-- Template download hint -->
            <div class="text-center text-xs text-gray-400">
                File Excel của bạn đang ở: <code class="bg-gray-100 px-1 rounded">database/THEO DÕI ĐƠN HÀNG KD PHÚC 2025.xlsx</code>
            </div>
        </div>
    </AdminLayout>
</template>
