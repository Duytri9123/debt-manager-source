<script setup>
import AdminLayout from '@/Layouts/AdminLayout.vue'
import { router, useForm } from '@inertiajs/vue3'
import { ref } from 'vue'
import { Plus, Edit2, Trash2, Zap, Star, CheckCircle, XCircle } from 'lucide-vue-next'

const props = defineProps({ providers: Array })

const providerLabels = {
  openai: 'OpenAI', openrouter: 'OpenRouter', google: 'Google Gemini',
  anthropic: 'Anthropic Claude', ollama: 'Ollama (Local)', custom: 'Custom API'
}
const providerColors = {
  openai: 'bg-green-100 text-green-700', openrouter: 'bg-purple-100 text-purple-700',
  google: 'bg-blue-100 text-blue-700', anthropic: 'bg-orange-100 text-orange-700',
  ollama: 'bg-gray-100 text-gray-700', custom: 'bg-pink-100 text-pink-700',
}

const testingId = ref(null)

function testProvider(id) {
  testingId.value = id
  router.post(`/admin/ai-providers/${id}/test`, {}, {
    onFinish: () => { testingId.value = null }
  })
}

function setDefault(id) {
  router.post(`/admin/ai-providers/${id}/set-default`)
}

function destroy(id, name) {
  if (confirm(`Xóa provider "${name}"?`)) {
    router.delete(`/admin/ai-providers/${id}`)
  }
}
</script>

<template>
  <AdminLayout>
    <div class="space-y-5">
      <div class="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 class="text-xl font-bold text-gray-900">Quản lý AI Providers</h1>
          <p class="text-sm text-gray-500 mt-0.5">Cấu hình các AI model cho chatbot và tính năng AI</p>
        </div>
        <button @click="router.visit('/admin/ai-providers/create')"
          class="flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 transition-colors shrink-0 whitespace-nowrap">
          <Plus :size="16" /> Thêm Provider
        </button>
        <button @click="router.visit('/admin/ai-providers/images')"
          class="flex items-center gap-2 rounded-lg border border-gray-200 px-4 py-2 text-sm font-medium text-gray-600 hover:bg-gray-50 transition-colors shrink-0 whitespace-nowrap">
          🖼️ Quản lý ảnh AI
        </button>
      </div>

      <!-- Providers grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        <div v-for="p in providers" :key="p.id"
          class="bg-white rounded-xl border border-gray-200 shadow-sm p-3 lg:p-5 flex flex-col gap-3">

          <!-- Header -->
          <div class="flex items-start justify-between">
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2 flex-wrap">
                <h3 class="font-semibold text-gray-900 truncate">{{ p.name }}</h3>
                <span v-if="p.is_default"
                  class="inline-flex items-center gap-1 rounded-full bg-amber-100 text-amber-700 px-2 py-0.5 text-xs font-medium">
                  <Star :size="10" /> Mặc định
                </span>
              </div>
              <p class="text-xs text-gray-500 mt-0.5 font-mono truncate">{{ p.model }}</p>
            </div>
            <div class="flex items-center gap-1 ml-2">
              <div :class="['w-2 h-2 rounded-full', p.is_active ? 'bg-emerald-500' : 'bg-gray-300']" :title="p.is_active ? 'Đang hoạt động' : 'Tắt'" />
            </div>
          </div>

          <!-- Provider badge -->
          <div class="flex items-center gap-2 flex-wrap">
            <span :class="['rounded-full px-2.5 py-0.5 text-xs font-medium', providerColors[p.provider] ?? 'bg-gray-100 text-gray-700']">
              {{ providerLabels[p.provider] ?? p.provider }}
            </span>
            <span class="text-xs text-gray-500">{{ p.max_tokens?.toLocaleString() }} tokens</span>
            <span class="text-xs text-gray-500">temp: {{ p.temperature }}</span>
          </div>

          <!-- Capabilities -->
          <div v-if="p.capabilities?.length" class="flex flex-wrap gap-1">
            <span v-for="cap in p.capabilities" :key="cap"
              class="rounded-full bg-indigo-50 text-indigo-600 px-2 py-0.5 text-xs">
              {{ cap }}
            </span>
          </div>

          <!-- Actions -->
          <div class="flex items-center gap-2 mt-auto pt-2 border-t border-gray-100">
            <button @click="testProvider(p.id)" :disabled="testingId === p.id"
              class="flex items-center gap-1.5 rounded-lg bg-emerald-50 text-emerald-700 px-3 py-1.5 text-xs font-medium hover:bg-emerald-100 disabled:opacity-50 transition-colors">
              <Zap :size="12" />
              {{ testingId === p.id ? 'Đang test...' : 'Test' }}
            </button>
            <button v-if="!p.is_default" @click="setDefault(p.id)"
              class="flex items-center gap-1.5 rounded-lg bg-amber-50 text-amber-700 px-3 py-1.5 text-xs font-medium hover:bg-amber-100 transition-colors">
              <Star :size="12" /> Đặt mặc định
            </button>
            <div class="flex-1" />
            <button @click="router.visit(`/admin/ai-providers/${p.id}/edit`)"
              class="p-1.5 rounded-lg text-gray-400 hover:bg-gray-100 hover:text-indigo-600 transition-colors">
              <Edit2 :size="14" />
            </button>
            <button @click="destroy(p.id, p.name)"
              class="p-1.5 rounded-lg text-gray-400 hover:bg-red-50 hover:text-red-600 transition-colors">
              <Trash2 :size="14" />
            </button>
          </div>
        </div>

        <!-- Empty state -->
        <div v-if="!providers?.length" class="col-span-full bg-white rounded-xl border border-dashed border-gray-300 p-12 text-center">
          <p class="text-gray-400 mb-3">Chưa có AI Provider nào</p>
          <button @click="router.visit('/admin/ai-providers/create')"
            class="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 transition-colors">
            Thêm Provider đầu tiên
          </button>
        </div>
      </div>

      <!-- Info box -->
      <div class="bg-blue-50 border border-blue-200 rounded-xl p-4 text-sm text-blue-800">
        <p class="font-semibold mb-1">💡 Hướng dẫn cấu hình</p>
        <ul class="space-y-1 text-blue-700 list-disc list-inside">
          <li><strong>OpenRouter</strong>: Hỗ trợ nhiều model miễn phí (GPT, Claude, Gemini). Đăng ký tại openrouter.ai</li>
          <li><strong>Google Gemini</strong>: Miễn phí với giới hạn. Lấy API key tại aistudio.google.com</li>
          <li><strong>Ollama</strong>: Chạy model local, không cần API key</li>
          <li>Provider được đánh dấu <strong>Mặc định</strong> sẽ được dùng cho chatbot</li>
        </ul>
      </div>
    </div>
  </AdminLayout>
</template>
