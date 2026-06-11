<script setup>
import { ref } from 'vue'
import { router } from '@inertiajs/vue3'
import AdminLayout from '@/Layouts/AdminLayout.vue'
import { Plus } from 'lucide-vue-next'

const props = defineProps({
  categories: Array,
})

const expanded = ref(new Set())
const openMenuId = ref(null)

function toggle(id) {
  if (expanded.value.has(id)) {
    expanded.value.delete(id)
  } else {
    expanded.value.add(id)
  }
  // Force reactivity
  expanded.value = new Set(expanded.value)
}

function toggleMenu(id) {
  openMenuId.value = openMenuId.value === id ? null : id
}

function deleteCategory(category) {
  if (!confirm(`Xóa danh mục "${category.name}"?`)) return
  router.delete(`/admin/categories/${category.id}`)
  openMenuId.value = null
}
</script>

<template>
  <AdminLayout>
    <div class="space-y-4 sm:space-y-6">
      <!-- Header -->
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <h1 class="text-xl sm:text-2xl font-bold text-gray-900">Danh mục sản phẩm</h1>
          <p class="mt-1 text-xs sm:text-sm text-gray-500">Quản lý cây danh mục sản phẩm ({{ categories?.length ?? 0 }} danh mục gốc)</p>
        </div>
        <button
          @click="router.visit('/admin/categories/create')"
          class="flex items-center justify-center gap-2 rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-indigo-700 shadow-sm"
        >
          <Plus :size="16" /> 
          <span class="hidden xs:inline">Thêm danh mục</span>
          <span class="xs:hidden">Thêm</span>
        </button>
      </div>

      <!-- Tree -->
      <div class="rounded-xl border border-gray-200 bg-white shadow-sm overflow-hidden">
        <div v-if="!categories?.length" class="px-6 py-12 text-center text-sm text-gray-500">
          Chưa có danh mục nào
        </div>
        <div v-else class="divide-y divide-gray-100">
          <CategoryRow
            v-for="cat in categories"
            :key="cat.id"
            :category="cat"
            :depth="0"
            :expanded="expanded"
            :open-menu-id="openMenuId"
            @toggle="toggle"
            @toggle-menu="toggleMenu"
            @delete="deleteCategory"
          />
        </div>
      </div>
    </div>
  </AdminLayout>
</template>

<script>
import { defineComponent, h } from 'vue'
import { router } from '@inertiajs/vue3'
import { ChevronRight, ChevronDown, Edit, Trash2, FolderPlus, MoreVertical } from 'lucide-vue-next'

const CategoryRow = defineComponent({
  name: 'CategoryRow',
  props: {
    category: Object,
    depth:    { type: Number, default: 0 },
    expanded: Object,
    openMenuId: [Number, null],
  },
  emits: ['toggle', 'toggleMenu', 'delete'],
  setup(props, { emit }) {
    const hasChildren = () => {
      return props.category.children && props.category.children.length > 0
    }

    function getImageUrl(cat) {
      if (!cat.img_url) return null
      if (cat.img_url.startsWith('http')) return cat.img_url
      return `/storage/${cat.img_url}`
    }

    return () => {
      const isExp = props.expanded.has(props.category.id)
      const indent = props.depth * 20 // Giảm indent cho mobile
      const children = props.category.children || []
      const isMenuOpen = props.openMenuId === props.category.id

      return h('div', {}, [
        // Row
        h('div', {
          class: 'flex items-center gap-2 sm:gap-3 px-3 sm:px-4 py-2.5 sm:py-3 hover:bg-gray-50 transition-colors relative',
          style: { paddingLeft: `${12 + indent}px` },
        }, [
          // Expand toggle
          h('button', {
            onClick: () => hasChildren() && emit('toggle', props.category.id),
            class: ['w-5 h-5 sm:w-6 sm:h-6 flex items-center justify-center rounded text-gray-400 transition-colors shrink-0', hasChildren() ? 'hover:bg-gray-200 cursor-pointer' : 'cursor-default'],
          }, hasChildren()
            ? [h(isExp ? ChevronDown : ChevronRight, { size: 12, class: 'sm:w-3.5 sm:h-3.5' })]
            : [h('span', { class: 'w-2.5 h-2.5 sm:w-3.5 sm:h-3.5 rounded-full border-2 border-gray-200 inline-block' })]
          ),

          // Thumbnail
          h('div', { class: 'h-8 w-8 sm:h-9 sm:w-9 shrink-0 rounded-lg overflow-hidden bg-gray-100' }, [
            getImageUrl(props.category)
              ? h('img', { src: getImageUrl(props.category), alt: props.category.name, class: 'h-full w-full object-cover' })
              : h('div', { class: 'h-full w-full flex items-center justify-center text-gray-300' },
                  [h('svg', { class: 'h-3.5 w-3.5 sm:h-4 sm:w-4', fill: 'none', viewBox: '0 0 24 24', stroke: 'currentColor' },
                    [h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '1.5', d: 'M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z' })]
                  )]
                )
          ]),

          // Name + meta
          h('div', { class: 'flex-1 min-w-0' }, [
            h('p', { class: 'text-xs sm:text-sm font-medium text-gray-900 truncate' }, props.category.name),
            h('p', { class: 'text-[10px] sm:text-xs text-gray-400 truncate' }, [
              `${props.category.products_count ?? 0} SP`,
              hasChildren() ? ` · ${children.length} con` : '',
            ]),
          ]),

          // Actions - Desktop (hidden on mobile)
          h('div', { class: 'hidden md:flex items-center gap-1 shrink-0' }, [
            h('button', {
              onClick: () => router.visit(`/admin/categories/create?parent_id=${props.category.id}`),
              title: 'Thêm danh mục con',
              class: 'flex items-center gap-1 rounded px-2 py-1 text-xs font-medium text-gray-500 hover:bg-gray-100 hover:text-indigo-600',
            }, [h(FolderPlus, { size: 13 }), h('span', { class: 'hidden lg:inline' }, ' Con')]),

            h('button', {
              onClick: () => router.visit(`/admin/categories/${props.category.id}/edit`),
              class: 'flex items-center gap-1 rounded px-2 py-1 text-xs font-medium text-indigo-600 hover:bg-indigo-50',
            }, [h(Edit, { size: 13 }), h('span', { class: 'hidden lg:inline' }, ' Sửa')]),

            h('button', {
              onClick: () => emit('delete', props.category),
              class: 'flex items-center gap-1 rounded px-2 py-1 text-xs font-medium text-red-600 hover:bg-red-50',
            }, [h(Trash2, { size: 13 }), h('span', { class: 'hidden lg:inline' }, ' Xóa')]),
          ]),

          // Mobile menu button
          h('div', { class: 'md:hidden relative' }, [
            h('button', {
              onClick: (e) => {
                e.stopPropagation()
                emit('toggleMenu', props.category.id)
              },
              class: 'p-1.5 rounded hover:bg-gray-100 text-gray-500',
            }, [h(MoreVertical, { size: 16 })]),

            // Dropdown menu
            isMenuOpen ? h('div', {
              class: 'absolute right-0 top-full mt-1 w-40 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-10',
              onClick: (e) => e.stopPropagation(),
            }, [
              h('button', {
                onClick: () => {
                  router.visit(`/admin/categories/create?parent_id=${props.category.id}`)
                  emit('toggleMenu', null)
                },
                class: 'w-full flex items-center gap-2 px-3 py-2 text-xs text-gray-700 hover:bg-gray-50',
              }, [h(FolderPlus, { size: 14 }), 'Thêm con']),

              h('button', {
                onClick: () => {
                  router.visit(`/admin/categories/${props.category.id}/edit`)
                  emit('toggleMenu', null)
                },
                class: 'w-full flex items-center gap-2 px-3 py-2 text-xs text-indigo-600 hover:bg-indigo-50',
              }, [h(Edit, { size: 14 }), 'Sửa']),

              h('button', {
                onClick: () => {
                  emit('delete', props.category)
                  emit('toggleMenu', null)
                },
                class: 'w-full flex items-center gap-2 px-3 py-2 text-xs text-red-600 hover:bg-red-50',
              }, [h(Trash2, { size: 14 }), 'Xóa']),
            ]) : null,
          ]),
        ]),

        // Children (recursive)
        isExp && hasChildren()
          ? h('div', {},
              children.map(child =>
                h(CategoryRow, {
                  key: child.id,
                  category: child,
                  depth: props.depth + 1,
                  expanded: props.expanded,
                  openMenuId: props.openMenuId,
                  onToggle: (id) => emit('toggle', id),
                  onToggleMenu: (id) => emit('toggleMenu', id),
                  onDelete: (cat) => emit('delete', cat),
                })
              )
            )
          : null,
      ])
    }
  }
})

export default { components: { CategoryRow } }
</script>
