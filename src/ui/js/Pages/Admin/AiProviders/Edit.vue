<script setup>
import AdminLayout from '@/Layouts/AdminLayout.vue'
import { useForm, router } from '@inertiajs/vue3'

const props = defineProps({ provider: Object })

const form = useForm({
  name:          props.provider.name ?? '',
  provider:      props.provider.provider ?? 'openrouter',
  model:         props.provider.model ?? '',
  api_key:       '',  // không hiển thị key cũ vì security
  base_url:      props.provider.base_url ?? '',
  is_active:     props.provider.is_active ?? true,
  is_default:    props.provider.is_default ?? false,
  max_tokens:    props.provider.max_tokens ?? 4096,
  temperature:   props.provider.temperature ?? 0.7,
  capabilities:  props.provider.capabilities ?? [],
  system_prompt: props.provider.system_prompt ?? '',
})

const providerOptions = [
  { value: 'openrouter', label: 'OpenRouter' },
  { value: 'openai',     label: 'OpenAI' },
  { value: 'google',     label: 'Google Gemini' },
  { value: 'anthropic',  label: 'Anthropic Claude' },
  { value: 'ollama',     label: 'Ollama (Local)' },
  { value: 'custom',     label: 'Custom API' },
]

const capabilityOptions = ['text', 'image', 'code', 'analysis', 'search']

function toggleCapability(cap) {
  const idx = form.capabilities.indexOf(cap)
  if (idx === -1) form.capabilities.push(cap)
  else form.capabilities.splice(idx, 1)
}

function submit() {
  form.put('/admin/ai-providers/' + props.provider.id)
}
</script>

<template>
  <AdminLayout>
    <div class="space-y-6">
      <div class="flex items-center gap-3">
        <button @click="router.visit('/admin/ai-providers')" class="text-gray-500 hover:text-gray-700 text-sm">← Quay lại</button>
        <h1 class="text-xl font-bold text-gray-900">Chỉnh sửa: {{ provider.name }}</h1>
      </div>

      <form @submit.prevent="submit" class="space-y-5">
        <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div class="col-span-2">
              <label class="block text-sm font-medium text-gray-700 mb-1">Tên hiển thị <span class="text-red-500">*</span></label>
              <input v-model="form.name" type="text"
                class="w-full rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                :class="form.errors.name ? 'border-red-400' : 'border-gray-300'" />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Provider</label>
              <select v-model="form.provider"
                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                <option v-for="opt in providerOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Model <span class="text-red-500">*</span></label>
              <input v-model="form.model" type="text"
                class="w-full rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                :class="form.errors.model ? 'border-red-400' : 'border-gray-300'" />
            </div>

            <div class="col-span-2">
              <label class="block text-sm font-medium text-gray-700 mb-1">
                API Key <span class="text-gray-400 text-xs">(để trống để giữ nguyên key cũ)</span>
              </label>
              <input v-model="form.api_key" type="password" placeholder="Nhập key mới để thay đổi..."
                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
            </div>

            <div v-if="['ollama', 'custom'].includes(form.provider)" class="col-span-2">
              <label class="block text-sm font-medium text-gray-700 mb-1">Base URL</label>
              <input v-model="form.base_url" type="url"
                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Max Tokens</label>
              <input v-model.number="form.max_tokens" type="number" min="1" max="128000"
                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Temperature</label>
              <input v-model.number="form.temperature" type="number" min="0" max="2" step="0.1"
                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
            </div>

            <div class="col-span-2">
              <label class="block text-sm font-medium text-gray-700 mb-2">Capabilities</label>
              <div class="flex flex-wrap gap-2">
                <button v-for="cap in capabilityOptions" :key="cap" type="button"
                  @click="toggleCapability(cap)"
                  :class="['rounded-full px-3 py-1 text-xs font-medium transition-colors border',
                    form.capabilities.includes(cap)
                      ? 'bg-indigo-600 text-white border-indigo-600'
                      : 'bg-white text-gray-600 border-gray-300 hover:border-indigo-400']">
                  {{ cap }}
                </button>
              </div>
            </div>

            <div class="col-span-2">
              <label class="block text-sm font-medium text-gray-700 mb-1">System Prompt</label>
              <textarea v-model="form.system_prompt" rows="3"
                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
            </div>

            <div class="col-span-2 flex items-center gap-6">
              <label class="flex items-center gap-2 cursor-pointer">
                <button type="button" @click="form.is_active = !form.is_active"
                  :class="['relative inline-flex h-5 w-9 items-center rounded-full transition-colors', form.is_active ? 'bg-indigo-600' : 'bg-gray-200']">
                  <span :class="['inline-block h-3.5 w-3.5 transform rounded-full bg-white shadow transition-transform', form.is_active ? 'translate-x-4' : 'translate-x-1']" />
                </button>
                <span class="text-sm text-gray-700">Kích hoạt</span>
              </label>
              <label class="flex items-center gap-2 cursor-pointer">
                <button type="button" @click="form.is_default = !form.is_default"
                  :class="['relative inline-flex h-5 w-9 items-center rounded-full transition-colors', form.is_default ? 'bg-amber-500' : 'bg-gray-200']">
                  <span :class="['inline-block h-3.5 w-3.5 transform rounded-full bg-white shadow transition-transform', form.is_default ? 'translate-x-4' : 'translate-x-1']" />
                </button>
                <span class="text-sm text-gray-700">Đặt làm mặc định</span>
              </label>
            </div>
          </div>
        </div>

        <div class="flex gap-3 justify-end">
          <button type="button" @click="router.visit('/admin/ai-providers')"
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
