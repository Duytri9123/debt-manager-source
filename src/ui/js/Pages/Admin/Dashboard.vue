<script setup>
import { ref, computed } from 'vue'
import { router } from '@inertiajs/vue3'
import AdminLayout from '@/Layouts/AdminLayout.vue'
import { useCurrency } from '@/composables/useCurrency.js'
import {
  Users, ShoppingBag, Package, CreditCard, TrendingUp, TrendingDown,
  X, ExternalLink, BarChart2, ArrowUpRight, ArrowDownRight, Minus,
  ShoppingCart, UserCheck, AlertCircle, CheckCircle, Clock, XCircle, Truck
} from 'lucide-vue-next'
import {
  Chart as ChartJS,
  CategoryScale, LinearScale, PointElement, LineElement, BarElement,
  ArcElement, Title, Tooltip, Legend, Filler
} from 'chart.js'
import { Line, Bar, Doughnut } from 'vue-chartjs'

ChartJS.register(
  CategoryScale, LinearScale, PointElement, LineElement, BarElement,
  ArcElement, Title, Tooltip, Legend, Filler
)

const props = defineProps({
  period:                 { type: String, default: 'month' },
  allTimeStats:           Object,
  periodStats:            Object,
  revenueChart:           Object,
  customerChart:          Object,
  debtPaymentChart:       Object,
  monthlyComparison:      Object,
  orderStatusBreakdown:   Object,
  paymentStatusBreakdown: Object,
  topProducts:            Array,
  topCustomers:           Array,
  topDebtors:             Array,
  recentOrders:           Array,
})

const { formatVND, formatNumber } = useCurrency()

// ── Period selector ───────────────────────────────────────────────────────────
const currentPeriod = ref(props.period)
const periods = [
  { value: 'week',    label: 'Tuần này' },
  { value: 'month',   label: 'Tháng này' },
  { value: 'quarter', label: 'Quý này' },
  { value: 'year',    label: 'Năm này' },
]
function changePeriod(p) {
  currentPeriod.value = p
  router.get('/admin/dashboard', { period: p }, { preserveState: true, preserveScroll: true })
}

// ── Growth badge ──────────────────────────────────────────────────────────────
function growthClass(v) {
  if (v === null || v === undefined) return 'text-gray-400'
  return v >= 0 ? 'text-emerald-600' : 'text-red-500'
}
function growthIcon(v) {
  if (v === null || v === undefined) return Minus
  return v >= 0 ? ArrowUpRight : ArrowDownRight
}
function growthText(v) {
  if (v === null || v === undefined) return 'N/A'
  return (v >= 0 ? '+' : '') + v + '%'
}

// ── Order status helpers ──────────────────────────────────────────────────────
const ORDER_STATUS_LABELS = {
  pending:    'Chờ xử lý',
  processing: 'Đang xử lý',
  shipped:    'Đang giao',
  delivered:  'Đã giao',
  cancelled:  'Đã hủy',
}
const ORDER_STATUS_CLASSES = {
  pending:    'bg-yellow-100 text-yellow-700',
  processing: 'bg-blue-100 text-blue-700',
  shipped:    'bg-purple-100 text-purple-700',
  delivered:  'bg-emerald-100 text-emerald-700',
  cancelled:  'bg-red-100 text-red-700',
}
const ORDER_STATUS_ICONS = {
  pending:    Clock,
  processing: BarChart2,
  shipped:    Truck,
  delivered:  CheckCircle,
  cancelled:  XCircle,
}
const PAYMENT_STATUS_LABELS = {
  unpaid:  'Chưa thanh toán',
  partial: 'Một phần',
  paid:    'Đã thanh toán',
}
const PAYMENT_STATUS_CLASSES = {
  unpaid:  'bg-red-100 text-red-700',
  partial: 'bg-amber-100 text-amber-700',
  paid:    'bg-emerald-100 text-emerald-700',
}

function formatDate(date) {
  if (!date) return '—'
  return new Date(date).toLocaleDateString('vi-VN')
}

// ── Chart configs ─────────────────────────────────────────────────────────────
const chartDefaults = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { display: false } },
}

const revenueLineData = computed(() => ({
  labels: props.revenueChart?.labels ?? [],
  datasets: [
    {
      label: 'Doanh thu',
      data: props.revenueChart?.revenue ?? [],
      borderColor: '#6366f1',
      backgroundColor: 'rgba(99,102,241,0.08)',
      fill: true,
      tension: 0.4,
      pointRadius: 3,
      pointHoverRadius: 6,
    },
  ],
}))

const revenueLineOptions = computed(() => ({
  ...chartDefaults,
  plugins: {
    legend: { display: false },
    tooltip: {
      callbacks: {
        label: ctx => ' ' + formatVND(ctx.raw),
      },
    },
  },
  scales: {
    y: {
      ticks: {
        callback: v => (v >= 1_000_000 ? (v / 1_000_000).toFixed(1) + 'M' : v >= 1000 ? (v / 1000).toFixed(0) + 'K' : v),
        font: { size: 11 },
      },
      grid: { color: 'rgba(0,0,0,0.04)' },
    },
    x: { ticks: { font: { size: 11 } }, grid: { display: false } },
  },
}))

const ordersBarData = computed(() => ({
  labels: props.revenueChart?.labels ?? [],
  datasets: [
    {
      label: 'Đơn hàng',
      data: props.revenueChart?.orders ?? [],
      backgroundColor: 'rgba(99,102,241,0.7)',
      borderRadius: 4,
    },
  ],
}))

const ordersBarOptions = computed(() => ({
  ...chartDefaults,
  scales: {
    y: { ticks: { font: { size: 11 } }, grid: { color: 'rgba(0,0,0,0.04)' } },
    x: { ticks: { font: { size: 11 } }, grid: { display: false } },
  },
}))

const monthlyBarData = computed(() => ({
  labels: props.monthlyComparison?.labels ?? [],
  datasets: [
    {
      label: 'Doanh thu',
      data: props.monthlyComparison?.revenue ?? [],
      backgroundColor: 'rgba(99,102,241,0.75)',
      borderRadius: 4,
      yAxisID: 'y',
    },
    {
      label: 'Đơn hàng',
      data: props.monthlyComparison?.orders ?? [],
      backgroundColor: 'rgba(16,185,129,0.7)',
      borderRadius: 4,
      yAxisID: 'y1',
    },
  ],
}))

const monthlyBarOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: true, position: 'top', labels: { font: { size: 12 } } },
    tooltip: {
      callbacks: {
        label: ctx => ctx.datasetIndex === 0
          ? ' ' + formatVND(ctx.raw)
          : ' ' + ctx.raw + ' đơn',
      },
    },
  },
  scales: {
    y: {
      type: 'linear',
      position: 'left',
      ticks: {
        callback: v => v >= 1_000_000 ? (v / 1_000_000).toFixed(1) + 'M' : v,
        font: { size: 11 },
      },
      grid: { color: 'rgba(0,0,0,0.04)' },
    },
    y1: {
      type: 'linear',
      position: 'right',
      ticks: { font: { size: 11 } },
      grid: { drawOnChartArea: false },
    },
    x: { ticks: { font: { size: 11 } }, grid: { display: false } },
  },
}))

const orderStatusDoughnutData = computed(() => {
  const statuses = ['pending', 'processing', 'shipped', 'delivered', 'cancelled']
  const colors   = ['#fbbf24', '#60a5fa', '#a78bfa', '#34d399', '#f87171']
  return {
    labels: statuses.map(s => ORDER_STATUS_LABELS[s]),
    datasets: [{
      data: statuses.map(s => props.orderStatusBreakdown?.[s]?.count ?? 0),
      backgroundColor: colors,
      borderWidth: 2,
      borderColor: '#fff',
    }],
  }
})

const doughnutOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { position: 'bottom', labels: { font: { size: 12 }, padding: 12 } },
  },
  cutout: '65%',
}

const customerLineData = computed(() => ({
  labels: props.customerChart?.labels ?? [],
  datasets: [{
    label: 'Khách mới',
    data: props.customerChart?.counts ?? [],
    borderColor: '#10b981',
    backgroundColor: 'rgba(16,185,129,0.08)',
    fill: true,
    tension: 0.4,
    pointRadius: 3,
    pointHoverRadius: 6,
  }],
}))

const debtPaymentBarData = computed(() => ({
  labels: props.debtPaymentChart?.labels ?? [],
  datasets: [{
    label: 'Thu nợ',
    data: props.debtPaymentChart?.amounts ?? [],
    backgroundColor: 'rgba(245,158,11,0.75)',
    borderRadius: 4,
  }],
}))

const debtPaymentBarOptions = computed(() => ({
  ...chartDefaults,
  plugins: {
    legend: { display: false },
    tooltip: { callbacks: { label: ctx => ' ' + formatVND(ctx.raw) } },
  },
  scales: {
    y: {
      ticks: {
        callback: v => v >= 1_000_000 ? (v / 1_000_000).toFixed(1) + 'M' : v,
        font: { size: 11 },
      },
      grid: { color: 'rgba(0,0,0,0.04)' },
    },
    x: { ticks: { font: { size: 11 } }, grid: { display: false } },
  },
}))

// ── Order detail modal ────────────────────────────────────────────────────────
const selectedOrder = ref(null)
function openOrder(order) { selectedOrder.value = order }
function closeModal()     { selectedOrder.value = null }
</script>

<template>
  <AdminLayout>
    <div class="space-y-6 pb-10">

      <!-- ── Header + Period selector ──────────────────────────────────────── -->
      <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 class="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p class="mt-0.5 text-sm text-gray-500">Tổng quan hệ thống</p>
        </div>
        <div class="flex gap-1 rounded-xl border border-gray-200 bg-white p-1 shadow-sm">
          <button
            v-for="p in periods" :key="p.value"
            @click="changePeriod(p.value)"
            :class="[
              'rounded-lg px-3 py-1.5 text-sm font-medium transition-colors',
              currentPeriod === p.value
                ? 'bg-indigo-600 text-white shadow-sm'
                : 'text-gray-600 hover:bg-gray-100'
            ]"
          >{{ p.label }}</button>
        </div>
      </div>

      <!-- ── All-time stat cards ────────────────────────────────────────────── -->
      <div class="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <div class="rounded-xl border border-gray-200 bg-white p-3 lg:p-5 shadow-sm">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-xs font-medium uppercase tracking-wide text-gray-500">Người dùng</p>
              <p class="mt-1 text-2xl font-bold text-gray-900">{{ formatNumber(allTimeStats.total_users) }}</p>
            </div>
            <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-50 text-indigo-600">
              <Users :size="20" />
            </div>
          </div>
        </div>
        <div class="rounded-xl border border-gray-200 bg-white p-3 lg:p-5 shadow-sm">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-xs font-medium uppercase tracking-wide text-gray-500">Tổng đơn hàng</p>
              <p class="mt-1 text-2xl font-bold text-gray-900">{{ formatNumber(allTimeStats.total_orders) }}</p>
            </div>
            <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-50 text-blue-600">
              <ShoppingBag :size="20" />
            </div>
          </div>
        </div>
        <div class="rounded-xl border border-gray-200 bg-white p-3 lg:p-5 shadow-sm">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-xs font-medium uppercase tracking-wide text-gray-500">Sản phẩm</p>
              <p class="mt-1 text-2xl font-bold text-gray-900">{{ formatNumber(allTimeStats.total_products) }}</p>
            </div>
            <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-50 text-emerald-600">
              <Package :size="20" />
            </div>
          </div>
        </div>
        <div class="rounded-xl border border-amber-100 bg-amber-50 p-3 lg:p-5 shadow-sm">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-xs font-medium uppercase tracking-wide text-amber-600">Công nợ chưa TT</p>
              <p class="mt-1 text-2xl font-bold text-amber-800">{{ formatNumber(allTimeStats.total_debt_count) }}</p>
              <p class="text-xs text-amber-600 mt-0.5">{{ formatVND(allTimeStats.total_debt_amount) }}</p>
            </div>
            <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-amber-100 text-amber-600">
              <CreditCard :size="20" />
            </div>
          </div>
        </div>
      </div>

      <!-- ── Period KPI cards ───────────────────────────────────────────────── -->
      <div class="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <!-- Revenue -->
        <div class="rounded-xl border border-gray-200 bg-white p-3 lg:p-5 shadow-sm">
          <p class="text-xs font-medium uppercase tracking-wide text-gray-500">Doanh thu kỳ này</p>
          <p class="mt-1 text-xl font-bold text-gray-900">{{ formatVND(periodStats.revenue) }}</p>
          <div :class="['mt-1 flex items-center gap-1 text-xs font-medium', growthClass(periodStats.revenue_growth)]">
            <component :is="growthIcon(periodStats.revenue_growth)" :size="13" />
            {{ growthText(periodStats.revenue_growth) }} so với kỳ trước
          </div>
        </div>
        <!-- Orders -->
        <div class="rounded-xl border border-gray-200 bg-white p-3 lg:p-5 shadow-sm">
          <p class="text-xs font-medium uppercase tracking-wide text-gray-500">Đơn hàng kỳ này</p>
          <p class="mt-1 text-xl font-bold text-gray-900">{{ formatNumber(periodStats.orders) }}</p>
          <div :class="['mt-1 flex items-center gap-1 text-xs font-medium', growthClass(periodStats.orders_growth)]">
            <component :is="growthIcon(periodStats.orders_growth)" :size="13" />
            {{ growthText(periodStats.orders_growth) }} so với kỳ trước
          </div>
        </div>
        <!-- New customers -->
        <div class="rounded-xl border border-gray-200 bg-white p-3 lg:p-5 shadow-sm">
          <p class="text-xs font-medium uppercase tracking-wide text-gray-500">Khách mới kỳ này</p>
          <p class="mt-1 text-xl font-bold text-gray-900">{{ formatNumber(periodStats.new_customers) }}</p>
          <div :class="['mt-1 flex items-center gap-1 text-xs font-medium', growthClass(periodStats.customers_growth)]">
            <component :is="growthIcon(periodStats.customers_growth)" :size="13" />
            {{ growthText(periodStats.customers_growth) }} so với kỳ trước
          </div>
        </div>
        <!-- Avg order value -->
        <div class="rounded-xl border border-gray-200 bg-white p-3 lg:p-5 shadow-sm">
          <p class="text-xs font-medium uppercase tracking-wide text-gray-500">Giá trị TB / đơn</p>
          <p class="mt-1 text-xl font-bold text-gray-900">{{ formatVND(periodStats.avg_order_value) }}</p>
          <p class="mt-1 text-xs text-red-500">{{ formatNumber(periodStats.cancelled_orders) }} đơn đã hủy</p>
        </div>
      </div>

      <!-- ── Revenue line chart + Orders bar chart ──────────────────────────── -->
      <div class="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <div class="rounded-xl border border-gray-200 bg-white p-3 lg:p-5 shadow-sm">
          <h2 class="mb-4 font-semibold text-gray-900">Doanh thu theo thời gian</h2>
          <div class="h-56">
            <Line :data="revenueLineData" :options="revenueLineOptions" />
          </div>
        </div>
        <div class="rounded-xl border border-gray-200 bg-white p-3 lg:p-5 shadow-sm">
          <h2 class="mb-4 font-semibold text-gray-900">Số đơn hàng theo thời gian</h2>
          <div class="h-56">
            <Bar :data="ordersBarData" :options="ordersBarOptions" />
          </div>
        </div>
      </div>

      <!-- ── Monthly 12-month comparison ───────────────────────────────────── -->
      <div class="rounded-xl border border-gray-200 bg-white p-3 lg:p-5 shadow-sm">
        <h2 class="mb-4 font-semibold text-gray-900">So sánh 12 tháng gần nhất</h2>
        <div class="h-64">
          <Bar :data="monthlyBarData" :options="monthlyBarOptions" />
        </div>
      </div>

      <!-- ── Order status doughnut + Payment status + Customer chart ─────────── -->
      <div class="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <!-- Order status doughnut -->
        <div class="rounded-xl border border-gray-200 bg-white p-3 lg:p-5 shadow-sm">
          <h2 class="mb-4 font-semibold text-gray-900">Trạng thái đơn hàng</h2>
          <div class="h-52">
            <Doughnut :data="orderStatusDoughnutData" :options="doughnutOptions" />
          </div>
        </div>

        <!-- Payment status breakdown -->
        <div class="rounded-xl border border-gray-200 bg-white p-3 lg:p-5 shadow-sm">
          <h2 class="mb-4 font-semibold text-gray-900">Thanh toán kỳ này</h2>
          <div class="space-y-3">
            <div v-for="(key, label) in { 'Chưa thanh toán': 'unpaid', 'Một phần': 'partial', 'Đã thanh toán': 'paid' }"
              :key="key"
              class="flex items-center justify-between rounded-lg bg-gray-50 px-4 py-3">
              <span class="text-sm text-gray-700">{{ label }}</span>
              <span :class="['rounded-full px-2.5 py-0.5 text-xs font-semibold', PAYMENT_STATUS_CLASSES[key]]">
                {{ paymentStatusBreakdown?.[key]?.count ?? 0 }} đơn
              </span>
            </div>
          </div>
          <div class="mt-4 space-y-2">
            <div v-for="(s, label) in { 'Chờ xử lý': 'pending', 'Đang xử lý': 'processing', 'Đang giao': 'shipped', 'Đã giao': 'delivered', 'Đã hủy': 'cancelled' }"
              :key="s"
              class="flex items-center justify-between text-sm">
              <div class="flex items-center gap-2">
                <component :is="ORDER_STATUS_ICONS[s]" :size="14" class="text-gray-400" />
                <span class="text-gray-600">{{ label }}</span>
              </div>
              <span :class="['rounded-full px-2 py-0.5 text-xs font-medium', ORDER_STATUS_CLASSES[s]]">
                {{ orderStatusBreakdown?.[s]?.count ?? 0 }}
              </span>
            </div>
          </div>
        </div>

        <!-- New customers chart -->
        <div class="rounded-xl border border-gray-200 bg-white p-3 lg:p-5 shadow-sm">
          <h2 class="mb-4 font-semibold text-gray-900">Khách hàng mới</h2>
          <div class="h-52">
            <Line :data="customerLineData" :options="{ ...revenueLineOptions, plugins: { legend: { display: false } } }" />
          </div>
        </div>
      </div>

      <!-- ── Debt payment chart ─────────────────────────────────────────────── -->
      <div class="rounded-xl border border-amber-100 bg-white p-3 lg:p-5 shadow-sm">
        <h2 class="mb-4 font-semibold text-gray-900">Thu nợ theo thời gian</h2>
        <div class="h-48">
          <Bar :data="debtPaymentBarData" :options="debtPaymentBarOptions" />
        </div>
      </div>

      <!-- ── Top products + Top customers ──────────────────────────────────── -->
      <div class="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <!-- Top products -->
        <div class="rounded-xl border border-gray-200 bg-white shadow-sm">
          <div class="border-b border-gray-100 px-5 py-4">
            <h2 class="font-semibold text-gray-900">Top sản phẩm bán chạy</h2>
            <p class="text-xs text-gray-400 mt-0.5">Theo kỳ đã chọn</p>
          </div>
          <div v-if="!topProducts?.length" class="px-5 py-8 text-center text-sm text-gray-400">Chưa có dữ liệu</div>
          <div v-else class="overflow-x-auto">
            <table class="w-full text-sm">
              <thead class="bg-gray-50 text-left text-xs font-medium uppercase tracking-wide text-gray-500">
                <tr>
                  <th class="px-4 py-3">#</th>
                  <th class="px-4 py-3">Sản phẩm</th>
                  <th class="px-4 py-3 text-right">Đã bán</th>
                  <th class="px-4 py-3 text-right">Doanh thu</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-100">
                <tr v-for="(p, i) in topProducts" :key="i" class="hover:bg-gray-50">
                  <td class="px-4 py-3 text-gray-400 font-medium">{{ i + 1 }}</td>
                  <td class="px-4 py-3 text-gray-800 font-medium max-w-[180px] truncate">{{ p.product_name }}</td>
                  <td class="px-4 py-3 text-right text-gray-600">{{ p.qty_sold }}</td>
                  <td class="px-4 py-3 text-right font-semibold text-indigo-600">{{ formatVND(p.total_revenue) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Top customers -->
        <div class="rounded-xl border border-gray-200 bg-white shadow-sm">
          <div class="border-b border-gray-100 px-5 py-4">
            <h2 class="font-semibold text-gray-900">Top khách hàng</h2>
            <p class="text-xs text-gray-400 mt-0.5">Theo doanh thu kỳ đã chọn</p>
          </div>
          <div v-if="!topCustomers?.length" class="px-5 py-8 text-center text-sm text-gray-400">Chưa có dữ liệu</div>
          <div v-else class="overflow-x-auto">
            <table class="w-full text-sm">
              <thead class="bg-gray-50 text-left text-xs font-medium uppercase tracking-wide text-gray-500">
                <tr>
                  <th class="px-4 py-3">#</th>
                  <th class="px-4 py-3">Khách hàng</th>
                  <th class="px-4 py-3 text-right">Đơn</th>
                  <th class="px-4 py-3 text-right">Tổng chi</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-100">
                <tr v-for="(c, i) in topCustomers" :key="i" class="hover:bg-gray-50">
                  <td class="px-4 py-3 text-gray-400 font-medium">{{ i + 1 }}</td>
                  <td class="px-4 py-3">
                    <p class="font-medium text-gray-800">{{ c.customer_name }}</p>
                    <p class="text-xs text-gray-400">{{ c.customer_email }}</p>
                  </td>
                  <td class="px-4 py-3 text-right text-gray-600">{{ c.order_count }}</td>
                  <td class="px-4 py-3 text-right font-semibold text-indigo-600">{{ formatVND(c.total_spent) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- ── Top debtors ────────────────────────────────────────────────────── -->
      <div class="rounded-xl border border-amber-100 bg-white shadow-sm">
        <div class="border-b border-amber-100 px-5 py-4 flex items-center justify-between">
          <div>
            <h2 class="font-semibold text-gray-900">Khách hàng nợ nhiều nhất</h2>
            <p class="text-xs text-gray-400 mt-0.5">Công nợ chưa thanh toán hiện tại</p>
          </div>
          <AlertCircle :size="18" class="text-amber-400" />
        </div>
        <div v-if="!topDebtors?.length" class="px-5 py-8 text-center text-sm text-gray-400">Không có công nợ</div>
        <div v-else class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead class="bg-amber-50 text-left text-xs font-medium uppercase tracking-wide text-amber-600">
              <tr>
                <th class="px-4 py-3">#</th>
                <th class="px-4 py-3">Khách hàng</th>
                <th class="px-4 py-3 text-right">Số khoản nợ</th>
                <th class="px-4 py-3 text-right">Tổng nợ còn lại</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-amber-50">
              <tr v-for="(d, i) in topDebtors" :key="i" class="hover:bg-amber-50/50">
                <td class="px-4 py-3 text-gray-400 font-medium">{{ i + 1 }}</td>
                <td class="px-4 py-3">
                  <p class="font-medium text-gray-800">{{ d.name }}</p>
                  <p class="text-xs text-gray-400">{{ d.email }}</p>
                </td>
                <td class="px-4 py-3 text-right text-gray-600">{{ d.debt_count }}</td>
                <td class="px-4 py-3 text-right font-bold text-amber-700">{{ formatVND(d.total_debt) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- ── Recent orders ──────────────────────────────────────────────────── -->
      <div class="rounded-xl border border-gray-200 bg-white shadow-sm">
        <div class="border-b border-gray-100 px-5 py-4 flex items-center justify-between">
          <h2 class="font-semibold text-gray-900">Đơn hàng gần đây</h2>
          <span class="text-xs text-gray-400">Click để xem chi tiết</span>
        </div>
        <div v-if="!recentOrders?.length" class="px-5 py-8 text-center text-sm text-gray-400">Chưa có đơn hàng</div>
        <div v-else class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead class="bg-gray-50 text-left text-xs font-medium uppercase tracking-wide text-gray-500">
              <tr>
                <th class="px-4 py-3">Mã đơn</th>
                <th class="px-4 py-3">Khách hàng</th>
                <th class="px-4 py-3 text-right">Tổng tiền</th>
                <th class="px-4 py-3">Đơn hàng</th>
                <th class="px-4 py-3">Thanh toán</th>
                <th class="px-4 py-3">Ngày tạo</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100">
              <tr v-for="order in recentOrders" :key="order.id"
                class="cursor-pointer hover:bg-indigo-50 transition-colors"
                @click="openOrder(order)">
                <td class="px-4 py-3 font-medium text-indigo-600">{{ order.order_number }}</td>
                <td class="px-4 py-3 text-gray-700">{{ order.customer_name }}</td>
                <td class="px-4 py-3 text-right font-semibold text-gray-900">{{ formatVND(order.grand_total) }}</td>
                <td class="px-4 py-3">
                  <span :class="['inline-flex rounded-full px-2 py-0.5 text-xs font-medium', ORDER_STATUS_CLASSES[order.status]]">
                    {{ ORDER_STATUS_LABELS[order.status] }}
                  </span>
                </td>
                <td class="px-4 py-3">
                  <span :class="['inline-flex rounded-full px-2 py-0.5 text-xs font-medium', PAYMENT_STATUS_CLASSES[order.payment_status]]">
                    {{ PAYMENT_STATUS_LABELS[order.payment_status] }}
                  </span>
                </td>
                <td class="px-4 py-3 text-gray-500">{{ formatDate(order.created_at) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

    </div>

    <!-- ── Order Detail Modal ─────────────────────────────────────────────── -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="selectedOrder"
          class="fixed inset-0 z-[100] flex items-center justify-center p-4"
          @click.self="closeModal">
          <div class="absolute inset-0 bg-black/40 backdrop-blur-sm" @click="closeModal" />
          <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
            <div class="flex items-center justify-between px-6 py-4 border-b border-gray-100 sticky top-0 bg-white rounded-t-2xl">
              <div>
                <h3 class="font-bold text-gray-900 text-lg">{{ selectedOrder.order_number }}</h3>
                <p class="text-xs text-gray-500 mt-0.5">Chi tiết đơn hàng</p>
              </div>
              <button @click="closeModal" class="p-2 rounded-lg text-gray-400 hover:bg-gray-100 transition-colors">
                <X :size="18" />
              </button>
            </div>
            <div class="px-6 py-5 space-y-5">
              <div class="flex items-center gap-2 flex-wrap">
                <span :class="['rounded-full px-3 py-1 text-xs font-medium', ORDER_STATUS_CLASSES[selectedOrder.status]]">
                  {{ ORDER_STATUS_LABELS[selectedOrder.status] }}
                </span>
                <span :class="['rounded-full px-3 py-1 text-xs font-medium', PAYMENT_STATUS_CLASSES[selectedOrder.payment_status]]">
                  {{ PAYMENT_STATUS_LABELS[selectedOrder.payment_status] }}
                </span>
              </div>
              <div class="bg-gray-50 rounded-xl p-4 space-y-2">
                <h4 class="text-xs font-semibold text-gray-500 uppercase tracking-wide">Thông tin khách hàng</h4>
                <div class="grid grid-cols-2 gap-2 text-sm">
                  <div><span class="text-gray-500">Tên:</span><span class="ml-1 font-medium text-gray-900">{{ selectedOrder.customer_name }}</span></div>
                  <div><span class="text-gray-500">Email:</span><span class="ml-1 text-gray-700">{{ selectedOrder.customer_email }}</span></div>
                  <div><span class="text-gray-500">SĐT:</span><span class="ml-1 text-gray-700">{{ selectedOrder.customer_phone ?? '—' }}</span></div>
                  <div><span class="text-gray-500">Ngày tạo:</span><span class="ml-1 text-gray-700">{{ formatDate(selectedOrder.created_at) }}</span></div>
                </div>
                <div v-if="selectedOrder.shipping_address" class="text-sm">
                  <span class="text-gray-500">Địa chỉ:</span>
                  <span class="ml-1 text-gray-700">{{ selectedOrder.shipping_address }}</span>
                </div>
              </div>
              <div class="bg-indigo-50 rounded-xl p-4 space-y-2">
                <h4 class="text-xs font-semibold text-indigo-600 uppercase tracking-wide">Tài chính</h4>
                <div class="space-y-1.5 text-sm">
                  <div class="flex justify-between"><span class="text-gray-600">Tạm tính:</span><span>{{ formatVND(selectedOrder.subtotal) }}</span></div>
                  <div v-if="selectedOrder.shipping_fee > 0" class="flex justify-between"><span class="text-gray-600">Phí vận chuyển:</span><span>{{ formatVND(selectedOrder.shipping_fee) }}</span></div>
                  <div v-if="selectedOrder.discount_amount > 0" class="flex justify-between"><span class="text-gray-600">Giảm giá:</span><span class="text-emerald-600">-{{ formatVND(selectedOrder.discount_amount) }}</span></div>
                  <div class="flex justify-between font-bold text-base border-t border-indigo-200 pt-2 mt-2">
                    <span>Tổng cộng:</span><span class="text-indigo-600">{{ formatVND(selectedOrder.grand_total) }}</span>
                  </div>
                </div>
              </div>
              <div v-if="selectedOrder.notes" class="text-sm">
                <span class="text-gray-500 font-medium">Ghi chú:</span>
                <p class="mt-1 text-gray-700 bg-gray-50 rounded-lg p-3">{{ selectedOrder.notes }}</p>
              </div>
            </div>
            <div class="px-6 py-4 border-t border-gray-100 flex gap-3 sticky bottom-0 bg-white rounded-b-2xl">
              <button @click="router.visit('/admin/debts'); closeModal()"
                class="flex items-center gap-1.5 rounded-lg bg-amber-50 border border-amber-200 px-4 py-2 text-sm font-medium text-amber-700 hover:bg-amber-100 transition-colors">
                <CreditCard :size="14" /> Xem công nợ
              </button>
              <button @click="router.visit('/admin/customers/' + selectedOrder.user_id); closeModal()"
                class="flex items-center gap-1.5 rounded-lg bg-indigo-50 border border-indigo-200 px-4 py-2 text-sm font-medium text-indigo-700 hover:bg-indigo-100 transition-colors">
                <ExternalLink :size="14" /> Hồ sơ khách hàng
              </button>
              <button @click="closeModal" class="ml-auto rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-600 hover:bg-gray-50 transition-colors">
                Đóng
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </AdminLayout>
</template>

<style scoped>
.modal-enter-active, .modal-leave-active { transition: all 0.2s ease; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
.modal-enter-from .relative, .modal-leave-to .relative { transform: scale(0.95) translateY(8px); }
</style>
