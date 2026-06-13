<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { usePage, router } from '@inertiajs/vue3'
import {
  LayoutDashboard, CreditCard, Users, Package, FolderOpen,
  ChevronLeft, ChevronRight, Menu, X, Settings,
  Truck, FileInput, FileOutput, FileText, Wallet, Brain,
  CheckCircle2, AlertCircle, Info, ShoppingCart, Layers, ClipboardList
} from 'lucide-vue-next'
import AiChat from '@/Components/AiChat.vue'

const page = usePage()
const flash = computed(() => page.props.flash)

// ─── Sidebar ──────────────────────────────────────────────────────────────────
const collapsed  = ref(false)
const mobileOpen = ref(false)

onMounted(() => {
  collapsed.value = localStorage.getItem('admin-sidebar-collapsed') === 'true'
})

function toggleCollapse() {
  collapsed.value = !collapsed.value
  localStorage.setItem('admin-sidebar-collapsed', String(collapsed.value))
}

// ─── Navigation ───────────────────────────────────────────────────────────────
const navItems = [
  { label: 'Dashboard',        href: '/admin/dashboard',          icon: LayoutDashboard },
  { label: 'Khách hàng',       href: '/admin/customers',          icon: ClipboardList },
  { label: 'Theo dõi KD',      href: '/admin/b2b-orders',         icon: ClipboardList },
  // { label: 'Đơn hàng',      href: '/admin/orders',             icon: ShoppingCart },
  { label: 'Công nợ',          href: '/admin/debts',              icon: CreditCard },
 // { label: 'Sản phẩm',         href: '/admin/products',           icon: Package },
  // { label: 'Nhóm sản phẩm',    href: '/admin/product-bundles',    icon: Layers },
  // { label: 'Danh mục',         href: '/admin/categories',         icon: FolderOpen },
  { label: 'Nhà cung cấp',     href: '/admin/suppliers',          icon: Truck },
  { label: 'Hóa đơn nhập',     href: '/admin/purchase-invoices',  icon: FileInput },
  { label: 'Hóa đơn bán',      href: '/admin/sales-invoices',     icon: FileOutput },
  { label: 'Biên bản',         href: '/admin/documents',          icon: FileText },
  { label: 'Tạm ứng',          href: '/admin/advances',           icon: Wallet },
  { label: 'Quản lý AI',       href: '/admin/ai-providers',       icon: Brain },
  { label: 'Cài đặt',          href: '/admin/settings',           icon: Settings },
  { label: 'Người dùng',       href: '/admin/users',              icon: Users },
]

function isActive(href) { return page.url.startsWith(href) }

function navigate(href) {
  mobileOpen.value = false
  router.visit(href)
}

// ─── Toast ────────────────────────────────────────────────────────────────────
const toasts = ref([])
let toastId  = 0

function addToast(message, type = 'success') {
  const id = ++toastId
  toasts.value.push({ id, message, type })
  setTimeout(() => { toasts.value = toasts.value.filter(t => t.id !== id) }, 4000)
}

watch(flash, (val) => {
  if (val?.success) addToast(val.success, 'success')
  if (val?.error)   addToast(val.error, 'error')
  if (val?.info)    addToast(val.info, 'info')
}, { immediate: true, deep: true })
</script>

<template>
  <div class="flex h-screen bg-gray-50 overflow-hidden">

    <!-- Mobile overlay -->
    <div v-if="mobileOpen" class="fixed inset-0 z-20 bg-black/50 md:hidden" @click="mobileOpen = false" />

    <!-- Sidebar -->
    <aside :class="[
      'fixed inset-y-0 left-0 z-30 flex flex-col bg-slate-900 transition-all duration-300',
      collapsed ? 'w-16' : 'w-60',
      mobileOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'
    ]">
      <!-- Logo -->
      <div class="flex h-14 items-center justify-between px-4 border-b border-slate-700">
        <span v-if="!collapsed" class="text-white font-bold text-xl truncate">Quản lý công nợ</span>
        <button @click="toggleCollapse"
          class="hidden md:flex items-center justify-center w-8 h-8 rounded-lg text-slate-400 hover:bg-slate-800 hover:text-white transition-colors">
          <ChevronLeft v-if="!collapsed" :size="16" />
          <ChevronRight v-else :size="16" />
        </button>
      </div>

      <!-- Nav items -->
      <nav class="flex-1 overflow-y-auto py-4 px-2 space-y-0.5">
        <div v-for="item in navItems" :key="item.href" class="relative group">
          <button @click="navigate(item.href)"
            :class="[
              'w-full flex items-center gap-3 px-3 py-3 rounded-lg text-base font-medium transition-colors',
              isActive(item.href)
                ? 'bg-indigo-600 text-white'
                : 'text-slate-400 hover:bg-slate-800 hover:text-slate-100'
            ]">
            <component :is="item.icon" :size="20" class="shrink-0" />
            <span v-if="!collapsed" class="truncate">{{ item.label }}</span>
          </button>
          <!-- Tooltip khi collapsed -->
          <div v-if="collapsed"
            class="absolute left-full top-1/2 -translate-y-1/2 ml-2 px-2.5 py-1.5 bg-slate-800 text-white text-xs rounded-lg whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-50 shadow-lg">
            {{ item.label }}
            <div class="absolute right-full top-1/2 -translate-y-1/2 border-4 border-transparent border-r-slate-800" />
          </div>
        </div>
      </nav>

    </aside>

    <!-- Main area -->
    <div :class="['flex flex-col flex-1 min-w-0 transition-all duration-300', collapsed ? 'md:ml-16' : 'md:ml-60']">
      <button @click="mobileOpen = true"
        class="fixed left-3 top-3 z-40 md:hidden p-2 rounded-lg bg-white text-gray-500 shadow-sm border border-gray-200 hover:bg-gray-100">
        <Menu :size="20" />
      </button>

      <!-- Page content -->
      <main class="flex-1 overflow-y-auto p-4 lg:p-6">
        <slot />
      </main>
    </div>

    <!-- Toast notifications -->
    <div class="fixed top-4 right-4 z-[60] flex flex-col gap-2 pointer-events-none">
      <transition-group name="toast">
        <div v-for="toast in toasts" :key="toast.id"
          :class="[
            'pointer-events-auto flex items-center gap-3 rounded-xl px-4 py-3 shadow-lg text-sm font-medium min-w-72 max-w-sm',
            toast.type === 'success' ? 'bg-emerald-50 text-emerald-800 border border-emerald-200' :
            toast.type === 'info'    ? 'bg-blue-50 text-blue-800 border border-blue-200' :
                                       'bg-red-50 text-red-800 border border-red-200'
          ]">
          <CheckCircle2 v-if="toast.type === 'success'" :size="16" class="shrink-0 text-emerald-500" />
          <Info         v-else-if="toast.type === 'info'" :size="16" class="shrink-0 text-blue-500" />
          <AlertCircle  v-else :size="16" class="shrink-0 text-red-500" />
          <span class="flex-1">{{ toast.message }}</span>
          <button @click="toasts = toasts.filter(t => t.id !== toast.id)"
            class="opacity-50 hover:opacity-100 transition-opacity">
            <X :size="14" />
          </button>
        </div>
      </transition-group>
    </div>

    <!-- AI Chat (draggable, viewport-aware) -->
    <AiChat />
  </div>
</template>

<style scoped>
.toast-enter-active, .toast-leave-active { transition: all 0.3s ease; }
.toast-enter-from, .toast-leave-to { opacity: 0; transform: translateX(100%); }
</style>
