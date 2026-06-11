<script setup>
import AdminLayout from '@/Layouts/AdminLayout.vue'
import { ref, onMounted, computed, nextTick } from 'vue'
import { router } from '@inertiajs/vue3'
import { Trash2, RefreshCw, Image, AlertTriangle, CheckCircle, ChevronLeft } from 'lucide-vue-next'

// ── State ─────────────────────────────────────────────────────────────────────
const images      = ref([])
const storage     = ref(null)
const loading     = ref(false)
const deleting    = ref(new Set())
const selected    = ref(new Set())
const currentPage = ref(1)
const lastPage    = ref(1)

// Cache thumbnails đã load: { [id]: dataUrl | 'error' }
const thumbCache  = ref({})

// ── Computed ──────────────────────────────────────────────────────────────────
const allSelected = computed(() =>
    images.value.length > 0 && images.value.every(img => selected.value.has(img.id))
)

function formatBytes(bytes) {
    if (!bytes) return '0 B'
    if (bytes < 1024) return bytes + ' B'
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
    if (bytes < 1024 * 1024 * 1024) return (bytes / 1024 / 1024).toFixed(2) + ' MB'
    return (bytes / 1024 / 1024 / 1024).toFixed(2) + ' GB'
}

function formatDate(dateStr) {
    return new Date(dateStr).toLocaleString('vi-VN')
}

// ── API helpers ───────────────────────────────────────────────────────────────
function apiFetch(url, opts = {}) {
    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content ?? ''
    return fetch(url, {
        headers: {
            'X-CSRF-TOKEN': csrfToken,
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        },
        credentials: 'include',
        ...opts,
    })
}

// ── Load thumbnails (lazy, batch) ─────────────────────────────────────────────
async function loadThumbnails(imgs) {
    // Load tối đa 6 ảnh cùng lúc để không quá tải
    const toLoad = imgs.filter(img => !thumbCache.value[img.id])
    const chunks = []
    for (let i = 0; i < toLoad.length; i += 6) chunks.push(toLoad.slice(i, i + 6))

    for (const chunk of chunks) {
        await Promise.all(chunk.map(async (img) => {
            try {
                const res  = await apiFetch(`/admin/ai/images/${img.id}`)
                if (!res.ok) { thumbCache.value[img.id] = 'error'; return }
                const data = await res.json()
                thumbCache.value[img.id] = data.data_url ?? 'error'
            } catch {
                thumbCache.value[img.id] = 'error'
            }
        }))
    }
}

// ── Load data ─────────────────────────────────────────────────────────────────
async function loadImages(page = 1) {
    loading.value = true
    try {
        const res  = await apiFetch(`/admin/ai/images?page=${page}`)
        const data = await res.json()
        images.value      = data.images?.data ?? []
        storage.value     = data.storage ?? null
        currentPage.value = data.images?.current_page ?? 1
        lastPage.value    = data.images?.last_page ?? 1
        selected.value    = new Set()
        // Load thumbnails sau khi có danh sách
        nextTick(() => loadThumbnails(images.value))
    } catch (e) {
        console.error(e)
    } finally {
        loading.value = false
    }
}

// ── Delete ────────────────────────────────────────────────────────────────────
async function deleteImage(id) {
    if (!confirm('Xóa ảnh này?')) return
    deleting.value = new Set([...deleting.value, id])
    try {
        await apiFetch(`/admin/ai/images/${id}`, { method: 'DELETE' })
        delete thumbCache.value[id]
        await loadImages(currentPage.value)
    } finally {
        const s = new Set(deleting.value)
        s.delete(id)
        deleting.value = s
    }
}

async function deleteSelected() {
    if (!selected.value.size) return
    if (!confirm(`Xóa ${selected.value.size} ảnh đã chọn?`)) return
    const ids = [...selected.value]
    deleting.value = new Set([...deleting.value, ...ids])
    try {
        await apiFetch('/admin/ai/images', {
            method: 'DELETE',
            body: JSON.stringify({ ids }),
        })
        ids.forEach(id => delete thumbCache.value[id])
        await loadImages(currentPage.value)
    } finally {
        const s = new Set(deleting.value)
        ids.forEach(id => s.delete(id))
        deleting.value = s
    }
}

// ── Select ────────────────────────────────────────────────────────────────────
function toggleSelect(id) {
    const s = new Set(selected.value)
    if (s.has(id)) s.delete(id)
    else s.add(id)
    selected.value = s
}

function toggleAll() {
    if (allSelected.value) {
        selected.value = new Set()
    } else {
        selected.value = new Set(images.value.map(img => img.id))
    }
}

onMounted(() => loadImages())
</script>

<template>
    <AdminLayout>
        <div class="space-y-5 max-w-5xl mx-auto">

            <!-- Header -->
            <div class="flex items-center justify-between flex-wrap gap-3">
                <div class="flex items-center gap-3">
                    <button @click="router.visit('/admin/ai-providers')"
                        class="p-1.5 rounded-lg hover:bg-gray-100 text-gray-500 transition-colors">
                        <ChevronLeft :size="18" />
                    </button>
                    <div>
                        <h1 class="text-xl font-bold text-gray-900">Quản lý ảnh Chat AI</h1>
                        <p class="text-sm text-gray-500 mt-0.5">Ảnh đã gửi trong các cuộc hội thoại AI</p>
                    </div>
                </div>
                <button @click="loadImages(currentPage)"
                    :disabled="loading"
                    class="flex items-center gap-2 rounded-lg border border-gray-200 px-3 py-2 text-sm text-gray-600 hover:bg-gray-50 transition-colors disabled:opacity-50">
                    <RefreshCw :size="14" :class="loading ? 'animate-spin' : ''" />
                    Làm mới
                </button>
            </div>

            <!-- Storage stats card -->
            <div v-if="storage" :class="[
                'rounded-xl border p-4',
                storage.over_quota ? 'bg-red-50 border-red-200' : storage.warning ? 'bg-amber-50 border-amber-200' : 'bg-white border-gray-200'
            ]">
                <div class="flex items-start gap-3">
                    <div :class="['mt-0.5', storage.over_quota ? 'text-red-500' : storage.warning ? 'text-amber-500' : 'text-indigo-500']">
                        <AlertTriangle v-if="storage.over_quota || storage.warning" :size="20" />
                        <CheckCircle v-else :size="20" />
                    </div>
                    <div class="flex-1">
                        <div class="flex items-center justify-between flex-wrap gap-2">
                            <div>
                                <p class="font-semibold text-gray-900">
                                    {{ storage.over_quota ? '🚫 Đã vượt giới hạn dung lượng!' : storage.warning ? '⚠️ Sắp đầy dung lượng' : '✅ Dung lượng bình thường' }}
                                </p>
                                <p class="text-sm text-gray-600 mt-0.5">
                                    Đã dùng <strong>{{ storage.used_mb }} MB</strong> / {{ storage.quota_gb }} GB
                                    <span class="text-gray-400">({{ storage.percent }}%)</span>
                                </p>
                            </div>
                            <div class="text-right text-sm text-gray-500">
                                Còn lại: <strong>{{ (storage.quota_gb * 1024 - storage.used_mb).toFixed(0) }} MB</strong>
                            </div>
                        </div>
                        <!-- Progress bar -->
                        <div class="mt-3 h-2.5 rounded-full bg-gray-200 overflow-hidden">
                            <div :class="[
                                'h-full rounded-full transition-all duration-500',
                                storage.over_quota ? 'bg-red-500' : storage.warning ? 'bg-amber-500' : 'bg-indigo-500'
                            ]" :style="`width: ${Math.min(storage.percent, 100)}%`" />
                        </div>
                        <p v-if="storage.over_quota" class="mt-2 text-sm text-red-600 font-medium">
                            Vui lòng xóa bớt ảnh cũ để tiếp tục sử dụng tính năng gửi ảnh trong chat AI.
                        </p>
                        <p v-else-if="storage.warning" class="mt-2 text-sm text-amber-600">
                            Dung lượng sắp đầy. Hãy xóa bớt ảnh không cần thiết.
                        </p>
                    </div>
                </div>
            </div>

            <!-- Bulk actions -->
            <div v-if="images.length > 0" class="flex items-center gap-3 flex-wrap">
                <label class="flex items-center gap-2 cursor-pointer text-sm text-gray-600 select-none">
                    <input type="checkbox" :checked="allSelected" @change="toggleAll"
                        class="w-4 h-4 rounded accent-indigo-600" />
                    Chọn tất cả ({{ images.length }})
                </label>
                <button v-if="selected.size > 0"
                    @click="deleteSelected"
                    class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-red-600 text-white text-sm hover:bg-red-700 transition-colors">
                    <Trash2 :size="13" />
                    Xóa {{ selected.size }} ảnh đã chọn
                </button>
            </div>

            <!-- Loading -->
            <div v-if="loading" class="flex justify-center py-16">
                <RefreshCw :size="24" class="animate-spin text-indigo-400" />
            </div>

            <!-- Empty state -->
            <div v-else-if="!images.length" class="text-center py-16 text-gray-400">
                <Image :size="40" class="mx-auto mb-3 opacity-30" />
                <p class="text-sm">Chưa có ảnh nào được lưu</p>
                <p class="text-xs mt-1">Ảnh sẽ xuất hiện ở đây khi bạn gửi ảnh trong chat AI</p>
            </div>

            <!-- Image grid -->
            <div v-else class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-3">
                <div v-for="img in images" :key="img.id"
                    :class="[
                        'relative group rounded-xl border overflow-hidden bg-white transition-all cursor-pointer',
                        selected.has(img.id) ? 'border-indigo-500 ring-2 ring-indigo-300' : 'border-gray-200 hover:border-gray-300'
                    ]"
                    @click="toggleSelect(img.id)">

                    <!-- Checkbox overlay -->
                    <div class="absolute top-2 left-2 z-10" @click.stop>
                        <input type="checkbox" :checked="selected.has(img.id)"
                            @change="toggleSelect(img.id)"
                            class="w-4 h-4 rounded accent-indigo-600 cursor-pointer" />
                    </div>

                    <!-- Thumbnail -->
                    <div class="aspect-square bg-gray-100 flex items-center justify-center overflow-hidden">
                        <!-- Loaded successfully -->
                        <img v-if="thumbCache[img.id] && thumbCache[img.id] !== 'error'"
                            :src="thumbCache[img.id]"
                            class="w-full h-full object-cover"
                            :alt="img.original_name" />
                        <!-- Error -->
                        <div v-else-if="thumbCache[img.id] === 'error'" class="text-center p-2">
                            <Image :size="24" class="mx-auto text-gray-300 mb-1" />
                            <p class="text-[10px] text-gray-400">Lỗi tải ảnh</p>
                        </div>
                        <!-- Loading spinner -->
                        <div v-else class="flex flex-col items-center gap-1">
                            <RefreshCw :size="18" class="animate-spin text-gray-300" />
                            <p class="text-[10px] text-gray-400">Đang tải...</p>
                        </div>
                    </div>

                    <!-- Info -->
                    <div class="p-2 border-t border-gray-100">
                        <p class="text-[11px] font-medium text-gray-700 truncate">{{ img.original_name }}</p>
                        <p class="text-[10px] text-gray-400">{{ formatBytes(img.size) }}</p>
                        <p class="text-[10px] text-gray-400">{{ formatDate(img.created_at) }}</p>
                    </div>

                    <!-- Delete button -->
                    <button @click.stop="deleteImage(img.id)"
                        :disabled="deleting.has(img.id)"
                        class="absolute top-2 right-2 w-6 h-6 rounded-full bg-red-500 text-white flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity disabled:opacity-50 hover:bg-red-600 z-10">
                        <RefreshCw v-if="deleting.has(img.id)" :size="10" class="animate-spin" />
                        <Trash2 v-else :size="10" />
                    </button>
                </div>
            </div>

            <!-- Pagination -->
            <div v-if="lastPage > 1" class="flex justify-center gap-2 flex-wrap">
                <button v-for="page in lastPage" :key="page"
                    @click="loadImages(page)"
                    :class="[
                        'w-8 h-8 rounded-lg text-sm font-medium transition-colors',
                        page === currentPage ? 'bg-indigo-600 text-white' : 'bg-white border border-gray-200 text-gray-600 hover:bg-gray-50'
                    ]">
                    {{ page }}
                </button>
            </div>

        </div>
    </AdminLayout>
</template>
