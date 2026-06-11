<script setup>
import AdminLayout from '@/Layouts/AdminLayout.vue'
import { useForm, router } from '@inertiajs/vue3'

const form = useForm({
  name: '',
  provider: 'openrouter',
  model: '',
  api_key: '',
  base_url: '',
  is_active: true,
  is_default: false,
  max_tokens: 4096,
  temperature: 0.7,
  capabilities: [],
  system_prompt: 'Bạn là AI Assistant của hệ thống quản trị. Hãy trả lời ngắn gọn, chính xác bằng tiếng Việt.',
})

const providerOptions = [
  { value: 'openrouter', label: 'OpenRouter (nhiều model miễn phí)' },
  { value: 'openai',     label: 'OpenAI (GPT-4, GPT-3.5)' },
  { value: 'google',     label: 'Google Gemini' },
  { value: 'anthropic',  label: 'Anthropic Claude' },
  { value: 'ollama',     label: 'Ollama (Local)' },
  { value: 'custom',     label: 'Custom API' },
]

const suggestedModels = {
  openrouter: ['openai/gpt-4o-mini:free', 'google/gemma-3-4b-it:free', 'meta-llama/llama-3.1-8b-instruct:free', 'openai/gpt-4o'],
  openai:     ['gpt-4o-mini', 'gpt-4o', 'gpt-3.5-turbo'],
  google:     ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-2.0-flash'],
  anthropic:  ['claude-3-haiku-20240307', 'claude-3-5-sonnet-20241022'],
  ollama:     ['llama3.2', 'mistral', 'qwen2.5'],
  custom:     [],
}

const capabilityOptions = ['text', 'image', 'code', 'analysis', 'search']

function toggleCapability(cap) {
  const idx = form.capabilities.indexOf(cap)
  if (idx === -1) form.capabilities.push(cap)
  else form.capabilities.splice(idx, 1)
}

function submit() {
  form.post('/admin/ai-providers')
}
</script>

<template>
  <AdminLayout>
    <div class="space-y-6">
      <div class="flex items-center gap-3">
        <button @click="router.visit('/admin/ai-providers')" class="text-gray-500 hover:text-gray-700 text-sm">← Quay lại</button>
        <h1 class="text-xl font-bold text-gray-900">Thêm AI Provider</h1>
      </div>

      <form @submit.prevent="submit" class="space-y-5">
        <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 space-y-4">
          <h2 class="font-semibold text-gray-900">Thông tin cơ bản</h2>

          <div class="grid grid-cols-2 gap-4">
            <div class="col-span-2">
              <label class="block text-sm font-medium text-gray-700 mb-1">Tên hiển thị <span class="text-red-500">*</span></label>
              <input v-model="form.name" type="text" placeholder="VD: OpenRouter Free Models"
                class="w-full rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                :class="form.errors.name ? 'border-red-400' : 'border-gray-300'" />
              <p v-if="form.errors.name" class="mt-1 text-xs text-red-500">{{ form.errors.name }}</p>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Provider <span class="text-red-500">*</span></label>
              <select v-model="form.provider"
                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                <option v-for="opt in providerOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Model <span class="text-red-500">*</span></label>
              <input v-model="form.model" type="text" list="model-suggestions"
                placeholder="VD: gpt-4o-mini"
                class="w-full rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                :class="form.errors.model ? 'border-red-400' : 'border-gray-300'" />
              <datalist id="model-suggestions">
                <option v-for="m in (suggestedModels[form.provider] ?? [])" :key="m" :value="m" />
              </datalist>
              <p v-if="form.errors.model" class="mt-1 text-xs text-red-500">{{ form.errors.model }}</p>
            </div>

            <div class="col-span-2">
              <label class="block text-sm font-medium text-gray-700 mb-1">API Key</label>
              <input v-model="form.api_key" type="password" placeholder="sk-... hoặc để trống nếu dùng Ollama"
                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
            </div>

            <div v-if="['ollama', 'custom'].includes(form.provider)" class="col-span-2">
              <label class="block text-sm font-medium text-gray-700 mb-1">Base URL</label>
              <input v-model="form.base_url" type="url" placeholder="http://localhost:11434"
                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Max Tokens</label>
              <input v-model.number="form.max_tokens" type="number" min="1" max="128000"
                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Temperature (0-2)</label>
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
            {{ form.processing ? 'Đang lưu...' : 'Thêm Provider' }}
          </button>
        </div>
      </form>
    </div>
  </AdminLayout>
</template>
