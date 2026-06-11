<script setup>
import { ref, computed } from 'vue'
import { useForm, router } from '@inertiajs/vue3'
import AdminLayout from '@/Layouts/AdminLayout.vue'
import { ArrowLeft, Upload, X, ChevronDown } from 'lucide-vue-next'

const props = defineProps({
  categories:      Array,
  defaultParentId: [String, Number, null],
})

const form = useForm({
  name:      '',
  parent_id: props.defaultParentId ?? null,
  img_url:   null,
})

const imagePreview = ref(null)
const showParentDropdown = ref(false)

const selectedParentLabel = computed(() => {
  if (!form.parent_id) return 'Không có (danh mục gốc)'
  const cat = props.categories?.find(c => c.id == form.parent_id)
  return cat ? cat.name.replace(/^[│├└─\s]+/, '') : 'Không có (danh mục gốc)'
})

function selectParent(cat) {
  form.parent_id = cat ? cat.id : null
  showParentDropdown.value = false
}

function handleImageChange(e) {
  const file = e.target.files[0]
  if (!file) return
  form.img_url = file
  imagePreview.value = URL.createObjectURL(file)
}

function clearImage() {
  form.img_url = null
  imagePreview.value = null
}

function submit() {
  form.post('/admin/categories', {
    forceFormData: true,
  })
}
</script>

<template>
  <AdminLayout>
    <div class="space-y-6">
      <button @click="router.visit('/admin/categories')" class="flex items-center gap-2 text-sm text-gray-500 hover:text-gray-700">
        <ArrowLeft :size="16" /> Quay lại danh sách
      </button>

      <h1 class="text-2xl font-bold text-gray-900">Thêm danh mục mới</h1>

      <form @submit.prevent="submit" class="rounded-xl border border-gray-200 bg-white p-6 shadow-sm space-y-5">
        <!-- Name -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Tên danh mục <span class="text-red-500">*</span></label>
          <input
            v-model="form.name"
            type="text"
            required
            maxlength="255"
            :class="['w-full rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500', form.errors.name ? 'border-red-300' : 'border-gray-300']"
            placeholder="Nhập tên danh mục..."
          />
          <p v-if="form.errors.name" class="mt-1 text-xs text-red-600">{{ form.errors.name }}</p>
        </div>

        <!-- Parent -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Danh mục cha</label>
          <div class="relative">
            <button
              type="button"
              @click="showParentDropdown = !showParentDropdown"
              class="w-full flex items-center justify-between rounded-lg border border-gray-300 px-3 py-2 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500 text-left"
            >
              <span :class="form.parent_id ? 'text-gray-900' : 'text-gray-500'">{{ selectedParentLabel }}</span>
              <ChevronDown :size="16" class="text-gray-400 shrink-0" />
            </button>
            <div
              v-if="showParentDropdown"
              class="absolute z-50 mt-1 w-full bg-white border border-gray-200 rounded-lg shadow-lg max-h-60 overflow-y-auto"
            >
              <button
                type="button"
                @click="selectParent(null)"
                class="w-full text-left px-3 py-2 text-sm hover:bg-indigo-50 text-gray-500 italic border-b border-gray-100"
              >Không có (danh mục gốc)</button>
              <button
                v-for="cat in categories"
                :key="cat.id"
                type="button"
                @click="selectParent(cat)"
                :style="{ paddingLeft: (12 + cat.depth * 16) + 'px' }"
                class="w-full text-left py-2 pr-3 text-sm hover:bg-indigo-50 text-gray-700 flex items-center gap-1.5"
              >
                <span v-if="cat.depth > 0" class="text-gray-300 shrink-0 text-xs">└─</span>
                <span>{{ cat.name.replace(/^[│├└─\s]+/, '') }}</span>
              </button>
            </div>
          </div>
          <p v-if="form.errors.parent_id" class="mt-1 text-xs text-red-600">{{ form.errors.parent_id }}</p>
        </div>

        <!-- Image upload -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Ảnh danh mục</label>
          <div v-if="imagePreview" class="relative mb-3 inline-block">
            <img :src="imagePreview" alt="Preview" class="h-24 w-24 rounded-lg object-cover border border-gray-200" />
            <button type="button" @click="clearImage" class="absolute -top-2 -right-2 flex h-5 w-5 items-center justify-center rounded-full bg-red-500 text-white hover:bg-red-600">
              <X :size="10" />
            </button>
          </div>
          <label class="flex cursor-pointer items-center gap-2 rounded-lg border-2 border-dashed border-gray-300 px-4 py-3 text-sm text-gray-500 hover:border-indigo-400 hover:text-indigo-600 transition-colors">
            <Upload :size="16" />
            <span>Chọn ảnh (jpg, jpeg, png, webp — tối đa 2MB)</span>
            <input type="file" accept=".jpg,.jpeg,.png,.webp" class="hidden" @change="handleImageChange" />
          </label>
          <p v-if="form.errors.img_url" class="mt-1 text-xs text-red-600">{{ form.errors.img_url }}</p>
        </div>

        <!-- Submit -->
        <div class="flex gap-3 pt-2">
          <button type="submit" :disabled="form.processing" class="rounded-lg bg-indigo-600 px-6 py-2.5 text-sm font-semibold text-white hover:bg-indigo-700 disabled:opacity-60">
            {{ form.processing ? 'Đang tạo...' : 'Tạo danh mục' }}
          </button>
          <button type="button" @click="router.visit('/admin/categories')" class="rounded-lg border border-gray-300 px-6 py-2.5 text-sm text-gray-700 hover:bg-gray-50">Hủy</button>
        </div>
      </form>
    </div>
  </AdminLayout>
</template>
