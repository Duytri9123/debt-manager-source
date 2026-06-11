<script setup>
import AdminLayout from '@/Layouts/AdminLayout.vue'
import { useForm } from '@inertiajs/vue3'
import { ref, computed } from 'vue'

const props = defineProps({
    settings: Object,
})

// Flatten settings thành array để edit
const allSettings = computed(() => {
    const result = []
    for (const [group, items] of Object.entries(props.settings || {})) {
        for (const item of items) {
            result.push({ ...item })
        }
    }
    return result
})

const form = useForm({
    settings: allSettings.value.map(s => ({ key: s.key, value: s.value ?? '' })),
})

const groups = computed(() => Object.keys(props.settings || {}))
const activeGroup = ref(groups.value[0] ?? '')

function getGroupSettings(group) {
    return (props.settings[group] || []).map(s => {
        const idx = form.settings.findIndex(f => f.key === s.key)
        return { ...s, formIndex: idx }
    })
}

function submit() {
    form.post('/admin/settings')
}

// Image upload
const uploading = ref({})

async function uploadImage(key, file) {
    if (!file) return
    uploading.value[key] = true
    const fd = new FormData()
    fd.append('image', file)
    fd.append('key', key)
    try {
        const res = await fetch('/admin/settings/upload', {
            method: 'POST',
            headers: { 'X-CSRF-TOKEN': document.querySelector('meta[name="csrf-token"]').content },
            body: fd,
        })
        const data = await res.json()
        if (data.url) {
            const idx = form.settings.findIndex(f => f.key === key)
            if (idx !== -1) form.settings[idx].value = data.url
        }
    } finally {
        uploading.value[key] = false
    }
}
</script>

<template>
    <AdminLayout>
        <div class=" mx-auto">
            <h1 class="text-xl font-semibold text-gray-900 mb-6">Cài đặt hệ thống</h1>

            <div class="flex flex-col sm:flex-row gap-6">
                <!-- Group tabs -->
                <div class="sm:w-48 shrink-0">
                    <nav class="flex sm:flex-col gap-1 overflow-x-auto sm:overflow-visible pb-1 sm:pb-0">
                        <button v-for="group in groups" :key="group" @click="activeGroup = group"
                            :class="[
                                'shrink-0 sm:w-full text-left px-3 py-2 rounded-lg text-sm font-medium transition-colors capitalize whitespace-nowrap',
                                activeGroup === group
                                    ? 'bg-indigo-50 text-indigo-700'
                                    : 'text-gray-600 hover:bg-gray-100'
                            ]">
                            {{ group }}
                        </button>
                    </nav>
                </div>

                <!-- Settings form -->
                <div class="flex-1">
                    <form @submit.prevent="submit">
                        <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 space-y-5">
                            <template v-for="setting in getGroupSettings(activeGroup)" :key="setting.key">
                                <div>
                                    <label class="block text-sm font-medium text-gray-700 mb-1">
                                        {{ setting.label || setting.key }}
                                    </label>

                                    <!-- Image upload fields -->
                                    <template v-if="['logo_url','favicon_url','admin_logo_url'].includes(setting.key)">
                                        <div class="flex items-center gap-3">
                                            <img v-if="form.settings[setting.formIndex]?.value"
                                                :src="form.settings[setting.formIndex].value"
                                                class="h-10 w-auto rounded border border-gray-200 object-contain" />
                                            <label class="cursor-pointer rounded-lg border border-dashed border-gray-300 px-4 py-2 text-sm text-gray-500 hover:border-indigo-400 hover:text-indigo-600 transition-colors">
                                                {{ uploading[setting.key] ? 'Đang upload...' : 'Chọn ảnh' }}
                                                <input type="file" class="hidden" accept="image/*"
                                                    @change="e => uploadImage(setting.key, e.target.files[0])" />
                                            </label>
                                        </div>
                                    </template>

                                    <!-- Textarea for long text -->
                                    <template v-else-if="setting.type === 'textarea'">
                                        <textarea v-model="form.settings[setting.formIndex].value" rows="3"
                                            class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                                    </template>

                                    <!-- Boolean toggle -->
                                    <template v-else-if="setting.type === 'boolean'">
                                        <button type="button"
                                            @click="form.settings[setting.formIndex].value = form.settings[setting.formIndex].value === '1' ? '0' : '1'"
                                            :class="[
                                                'relative inline-flex h-6 w-11 items-center rounded-full transition-colors',
                                                form.settings[setting.formIndex]?.value === '1' ? 'bg-indigo-600' : 'bg-gray-200'
                                            ]">
                                            <span :class="[
                                                'inline-block h-4 w-4 transform rounded-full bg-white shadow transition-transform',
                                                form.settings[setting.formIndex]?.value === '1' ? 'translate-x-6' : 'translate-x-1'
                                            ]" />
                                        </button>
                                    </template>

                                    <!-- Default text input -->
                                    <template v-else>
                                        <input v-model="form.settings[setting.formIndex].value" type="text"
                                            class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                                    </template>
                                </div>
                            </template>
                        </div>

                        <div class="mt-4 flex justify-end">
                            <button type="submit" :disabled="form.processing"
                                class="rounded-lg bg-indigo-600 px-6 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50 transition-colors">
                                {{ form.processing ? 'Đang lưu...' : 'Lưu cài đặt' }}
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </AdminLayout>
</template>
