<script setup>
import { ref, computed, watch, nextTick, onMounted, onUnmounted } from 'vue'
import { router } from '@inertiajs/vue3'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import {
    Bot, X, Send, Minimize2, Maximize2, ChevronDown, ChevronUp,
    GripVertical, Plus, Trash2, History, ChevronLeft, Loader2,
    MessageSquare, Cpu, Image, Mic, MicOff, ImagePlus, FolderOpen, RefreshCw
} from 'lucide-vue-next'

// ── Markdown renderer ─────────────────────────────────────────────────────────
marked.setOptions({ breaks: true, gfm: true })
function renderMarkdown(text) {
    if (!text) return ''
    try {
        const raw = marked.parse(String(text))
        return DOMPurify.sanitize(raw, { ADD_ATTR: ['target'] })
    } catch { return String(text) }
}

// ── Persistent state via localStorage ────────────────────────────────────────
const STORAGE_KEY = 'ai_chat_state_v2'

function loadState() {
    try {
        const raw = localStorage.getItem(STORAGE_KEY)
        return raw ? JSON.parse(raw) : null
    } catch { return null }
}

function saveState() {
    try {
        // Không lưu imageData (base64 quá lớn) — chỉ lưu imageId để load lại từ server
        const tabsToSave = tabs.value.map(t => ({
            ...t,
            loading:   false,
            abortCtrl: null,
            messages:  t.messages.map(m => ({ ...m, imageData: undefined })),
        }))
        localStorage.setItem(STORAGE_KEY, JSON.stringify({
            tabs:        tabsToSave,
            activeTabId: activeTabId.value,
            posBottom:   posBottom.value,
            posRight:    posRight.value,
            isOpen:      isOpen.value,
            isExpanded:  isExpanded.value,
        }))
    } catch {}
}

/**
 * Load lại imageData từ server cho các messages có imageId
 * Gọi sau khi restore state hoặc mở history
 */
async function restoreImagesInMessages(messages) {
    const toLoad = messages.filter(m => m.imageId && !m.imageData)
    if (!toLoad.length) return
    await Promise.all(toLoad.map(async (m) => {
        const dataUrl = await loadImageFromServer(m.imageId)
        if (dataUrl) m.imageData = dataUrl
    }))
}

// ── UI state ──────────────────────────────────────────────────────────────────
const isOpen        = ref(false)
const isMinimized   = ref(false)
const isExpanded    = ref(false)
const showHistory   = ref(false)
const showProviders = ref(false)
const showImageLib  = ref(false)   // panel thư viện ảnh đã lưu
const input         = ref('')
const container     = ref(null)
const inputRef      = ref(null)
const fileInputRef  = ref(null)

// ── Providers ─────────────────────────────────────────────────────────────────
const providers        = ref([])
const selectedProvider = ref(null)

async function loadProviders() {
    try {
        const res  = await apiFetch('/admin/ai/providers-list')
        const data = await res.json()
        providers.value = Array.isArray(data) ? data : []
    } catch {}
}

// ── Image attachment ──────────────────────────────────────────────────────────
const pendingImage    = ref(null)   // { dataUrl, base64, mimeType, name }
const imageStorageInfo = ref(null)  // { used_mb, quota_gb, percent, warning, over_quota }

function triggerImagePick() { fileInputRef.value?.click() }

function onImagePicked(e) {
    const file = e.target.files?.[0]
    if (!file) return
    if (!file.type.startsWith('image/')) { alert('Chỉ hỗ trợ file ảnh'); return }
    if (file.size > 5 * 1024 * 1024) { alert('Ảnh tối đa 5MB'); return }
    const reader = new FileReader()
    reader.onload = ev => {
        const dataUrl  = ev.target.result
        const base64   = dataUrl.split(',')[1]
        pendingImage.value = { dataUrl, base64, mimeType: file.type, name: file.name }
    }
    reader.readAsDataURL(file)
    e.target.value = ''
}

function removePendingImage() { pendingImage.value = null }

/**
 * Upload ảnh lên server, trả về image_id
 * Nếu over_quota → hiển thị cảnh báo và không cho gửi
 */
async function uploadImageToServer(base64, mimeType, name) {
    try {
        const res = await apiFetch('/admin/ai/images', {
            method: 'POST',
            body: JSON.stringify({ base64, mime_type: mimeType, original_name: name }),
        })
        const data = await res.json()
        if (!res.ok) {
            if (data.over_quota) {
                // Cập nhật storage info để hiển thị cảnh báo
                imageStorageInfo.value = {
                    over_quota: true,
                    used_mb: Math.round(data.used_bytes / 1024 / 1024),
                    quota_gb: 2,
                    percent: 100,
                    warning: true,
                }
            }
            return null
        }
        return data.id  // image_id
    } catch {
        return null
    }
}

/**
 * Load ảnh từ server theo image_id → trả về dataUrl
 */
async function loadImageFromServer(imageId) {
    try {
        const res  = await apiFetch(`/admin/ai/images/${imageId}`)
        if (!res.ok) return null
        const data = await res.json()
        return data.data_url ?? null
    } catch {
        return null
    }
}

/**
 * Load thông tin dung lượng ảnh
 */
async function loadStorageInfo() {
    try {
        const res  = await apiFetch('/admin/ai/images?page=1')
        const data = await res.json()
        if (data.storage) imageStorageInfo.value = data.storage
    } catch {}
}

// ── Image Library (thư viện ảnh đã lưu) ──────────────────────────────────────
const imageLibList    = ref([])   // danh sách ảnh đã lưu
const imageLibLoading = ref(false)
const imageLibThumb   = ref({})   // cache thumbnails { [id]: dataUrl | 'error' | 'loading' }

async function openImageLib() {
    showImageLib.value  = !showImageLib.value
    showHistory.value   = false
    showProviders.value = false
    if (showImageLib.value && !imageLibList.value.length) {
        await loadImageLib()
    }
}

async function loadImageLib() {
    imageLibLoading.value = true
    try {
        const res  = await apiFetch('/admin/ai/images?page=1')
        const data = await res.json()
        imageLibList.value = data.images?.data ?? []
        if (data.storage) imageStorageInfo.value = data.storage
        // Load thumbnails cho tất cả ảnh
        loadImageLibThumbs(imageLibList.value)
    } catch {} finally {
        imageLibLoading.value = false
    }
}

async function loadImageLibThumbs(imgs) {
    const toLoad = imgs.filter(img => !imageLibThumb.value[img.id])
    toLoad.forEach(img => { imageLibThumb.value[img.id] = 'loading' })
    // Load 4 ảnh cùng lúc
    for (let i = 0; i < toLoad.length; i += 4) {
        const chunk = toLoad.slice(i, i + 4)
        await Promise.all(chunk.map(async (img) => {
            try {
                const res  = await apiFetch(`/admin/ai/images/${img.id}`)
                if (!res.ok) { imageLibThumb.value[img.id] = 'error'; return }
                const data = await res.json()
                imageLibThumb.value[img.id] = data.data_url ?? 'error'
            } catch {
                imageLibThumb.value[img.id] = 'error'
            }
        }))
    }
}

/**
 * Chọn ảnh từ thư viện → set làm pendingImage để gửi AI
 */
async function selectFromLibrary(img) {
    // Nếu đã có thumb → dùng luôn
    let dataUrl = imageLibThumb.value[img.id]
    if (!dataUrl || dataUrl === 'loading' || dataUrl === 'error') {
        // Load lại
        dataUrl = await loadImageFromServer(img.id)
    }
    if (!dataUrl || dataUrl === 'error') return

    const base64 = dataUrl.split(',')[1]
    pendingImage.value = {
        dataUrl,
        base64,
        mimeType: img.mime_type,
        name: img.original_name,
        fromLibrary: true,  // đánh dấu từ thư viện, không upload lại
        existingId: img.id,
    }
    showImageLib.value = false
    nextTick(() => inputRef.value?.focus())
}

// ── Voice input (Web Speech API) ──────────────────────────────────────────────
const isListening   = ref(false)
const voiceSupported = ref(false)
let recognition = null

function initVoice() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    if (!SpeechRecognition) { voiceSupported.value = false; return }
    voiceSupported.value = true
    recognition = new SpeechRecognition()
    recognition.lang = 'vi-VN'
    recognition.continuous = false
    recognition.interimResults = true

    recognition.onresult = (e) => {
        const transcript = Array.from(e.results)
            .map(r => r[0].transcript)
            .join('')
        input.value = transcript
        if (e.results[e.results.length - 1].isFinal) {
            isListening.value = false
        }
    }
    recognition.onerror = () => { isListening.value = false }
    recognition.onend   = () => { isListening.value = false }
}

function toggleVoice() {
    if (!recognition) return
    if (isListening.value) {
        recognition.stop()
        isListening.value = false
    } else {
        input.value = ''
        recognition.start()
        isListening.value = true
    }
}

// ── Tabs / multi-chat ─────────────────────────────────────────────────────────
let tabCounter = 1

const defaultWelcome = {
    role: 'assistant',
    content: 'Xin chào! Tôi là **AI Assistant** 🤖\n\nTôi có thể giúp bạn:\n- 🔍 Tìm kiếm dữ liệu hệ thống\n- 📸 Phân tích hình ảnh\n- 🎤 Nhận lệnh bằng giọng nói\n- 🧭 Điều hướng nhanh\n- 📊 Thống kê tổng quan\n\nHãy nhập yêu cầu hoặc dùng nút 📸/🎤!'
}

function makeTab(id, title, messages, convId, providerId) {
    return {
        id:             id ?? ++tabCounter,
        title:          title ?? 'Chat mới',
        messages:       messages ?? [{ ...defaultWelcome }],
        conversationId: convId ?? null,
        providerId:     providerId ?? null,
        loading:        false,
        abortCtrl:      null,
    }
}

const tabs        = ref([makeTab(1, 'Chat mới', null, null, null)])
const activeTabId = ref(1)
const activeTab   = computed(() => tabs.value.find(t => t.id === activeTabId.value) ?? tabs.value[0])

function switchTab(id) {
    activeTabId.value = id
    showHistory.value = false
    nextTick(scrollToBottom)
}

function newTab() {
    const tab = makeTab(null, 'Chat mới', null, null, null)
    tabs.value.push(tab)
    activeTabId.value = tab.id
    showHistory.value = false
    nextTick(() => inputRef.value?.focus())
}

function closeTab(id) {
    const idx = tabs.value.findIndex(t => t.id === id)
    if (idx === -1) return
    const tab = tabs.value[idx]
    if (tab.abortCtrl) tab.abortCtrl.abort()
    tabs.value.splice(idx, 1)
    if (tabs.value.length === 0) tabs.value.push(makeTab(null, 'Chat mới', null, null, null))
    if (activeTabId.value === id) activeTabId.value = tabs.value[Math.max(0, idx - 1)].id
}

// ── History ───────────────────────────────────────────────────────────────────
const history        = ref([])
const historyLoading = ref(false)

async function loadHistory() {
    historyLoading.value = true
    try {
        const res  = await apiFetch('/admin/ai/conversations?page=1')
        const data = await res.json()
        history.value = data.data ?? []
    } catch {} finally { historyLoading.value = false }
}

async function openHistory(conv) {
    const existing = tabs.value.find(t => t.conversationId === conv.id)
    if (existing) { switchTab(existing.id); showHistory.value = false; return }
    try {
        const res  = await apiFetch(`/admin/ai/conversations/${conv.id}`)
        const data = await res.json()
        const tab  = makeTab(null, data.title ?? 'Lịch sử', data.messages ?? [], data.id, data.ai_provider_id)
        tabs.value.push(tab)
        activeTabId.value = tab.id
        showHistory.value = false
        nextTick(async () => {
            scrollToBottom()
            // Load lại ảnh từ server cho messages có imageId
            await restoreImagesInMessages(tab.messages)
        })
    } catch {}
}

async function deleteHistory(id) {
    if (!confirm('Xóa cuộc hội thoại này?')) return
    try {
        // Dùng Inertia router để DELETE — tự xử lý CSRF
        await new Promise((resolve, reject) => {
            router.delete(`/admin/ai/conversations/${id}`, {
                preserveState: true,
                preserveScroll: true,
                onSuccess: resolve,
                onError: reject,
                onFinish: resolve,
            })
        })
    } catch {}
    history.value = history.value.filter(h => h.id !== id)
    const tab = tabs.value.find(t => t.conversationId === id)
    if (tab) closeTab(tab.id)
}

// ── Quick actions ─────────────────────────────────────────────────────────────
const quickActions = [
    { label: '🔍 Tìm khách hàng', text: 'Tìm kiếm khách hàng trong hệ thống' },
    { label: '📦 Tạo sản phẩm',   text: 'Hướng dẫn tạo sản phẩm mới' },
    { label: '💰 Xem công nợ',    text: 'Mở trang công nợ' },
    { label: '📊 Thống kê',       text: 'Cho tôi xem thống kê tổng quan hệ thống' },
]

const navMap = {
    'khách hàng':   '/admin/customers',
    'sản phẩm':     '/admin/products',
    'công nợ':      '/admin/debts',
    'đơn hàng':     '/admin/debts',
    'danh mục':     '/admin/categories',
    'nhà cung cấp': '/admin/suppliers',
    'hóa đơn nhập': '/admin/purchase-invoices',
    'hóa đơn bán':  '/admin/sales-invoices',
    'biên bản':     '/admin/documents',
    'tạm ứng':      '/admin/advances',
    'cài đặt':      '/admin/settings',
    'ai':           '/admin/ai-providers',
    'dashboard':    '/admin/dashboard',
}

// ── Send message ──────────────────────────────────────────────────────────────
async function send() {
    const text  = input.value.trim()
    const image = pendingImage.value
    const tab   = activeTab.value

    if ((!text && !image) || tab.loading) return

    // Kiểm tra over_quota trước khi gửi ảnh
    if (image && imageStorageInfo.value?.over_quota) {
        tab.messages.push({
            role: 'assistant',
            content: `⚠️ **Đã vượt giới hạn 2GB ảnh chat AI!**\n\nVui lòng xóa bớt ảnh cũ tại trang [Quản lý ảnh AI](/admin/ai-providers?tab=images) trước khi gửi ảnh mới.`
        })
        await nextTick(); scrollToBottom()
        return
    }

    // Hiển thị message user (dùng dataUrl tạm để hiển thị ngay)
    const userMsg = { role: 'user', content: text || '📸 [Hình ảnh]', imageData: image?.dataUrl, imageId: null }
    tab.messages.push(userMsg)
    input.value    = ''
    pendingImage.value = null
    tab.loading    = true
    await nextTick(); scrollToBottom()

    // Upload ảnh lên server (background) để lưu lại cho history
    if (image) {
        // Nếu ảnh từ thư viện → dùng lại existingId, không upload lại
        if (image.fromLibrary && image.existingId) {
            userMsg.imageId = image.existingId
        } else {
            const imageId = await uploadImageToServer(image.base64, image.mimeType, image.name)
            if (imageId) {
                userMsg.imageId = imageId
            } else if (imageStorageInfo.value?.over_quota) {
                tab.messages.push({
                    role: 'assistant',
                    content: `⚠️ **Đã vượt giới hạn 2GB ảnh chat AI!**\n\nVui lòng xóa bớt ảnh cũ tại trang [Quản lý ảnh AI](/admin/ai-providers/images).`
                })
                tab.loading = false
                await nextTick(); scrollToBottom()
                return
            }
        }
    }

    const lower = (text || '').toLowerCase()

    // Điều hướng nhanh (chỉ khi không có ảnh)
    if (!image && (lower.includes('mở') || lower.includes('đến') || lower.includes('vào') || lower.includes('xem trang'))) {
        for (const [key, path] of Object.entries(navMap)) {
            if (lower.includes(key)) {
                tab.messages.push({ role: 'assistant', content: `🧭 Đang chuyển đến trang **${key}**...` })
                tab.loading = false
                await nextTick(); scrollToBottom()
                setTimeout(() => router.visit(path), 600)
                saveState(); return
            }
        }
    }

    // Lấy context dữ liệu hệ thống
    // Khi có ảnh → KHÔNG inject context DB dù có text hay không
    // AI phải tập trung đọc ảnh, không bị nhiễu bởi dữ liệu hệ thống
    let contextBlock = ''
    try {
        if (!image) {
            const ctxRes  = await apiFetch(`/admin/ai/context?q=${encodeURIComponent(text || '')}`)
            const ctxData = await ctxRes.json()
            const parts   = []

            if (ctxData.summary) {
                const s = ctxData.summary
                parts.push(
                    `\n\n━━ DỮ LIỆU HỆ THỐNG THỰC TẾ (${new Date().toLocaleDateString('vi-VN')}) ━━`,
                    `📊 Tổng quan: ${s.total_customers} khách hàng | ${s.total_products} sản phẩm | ${s.total_orders} đơn hàng | ${s.total_suppliers} NCC`,
                    `💰 Tháng này: ${s.orders_this_month} đơn | Doanh thu: ${Number(s.revenue_this_month||0).toLocaleString('vi-VN')}đ`,
                    `⚠️ Công nợ chưa TT: ${s.pending_debts} đơn | Nhóm SP: ${s.total_bundles}`
                )
                if (s.recent_orders?.length) {
                    parts.push(`\n📋 Đơn hàng gần đây:\n` + s.recent_orders.map(o =>
                        `  • ${o.order_number} | ${o.customer_name} | ${Number(o.grand_total||0).toLocaleString('vi-VN')}đ | ${o.status}`
                    ).join('\n'))
                }
            }
            if (ctxData.customers?.length) {
                parts.push(`\n👤 Khách hàng tìm thấy (${ctxData.customers.length} kết quả):\n` +
                    ctxData.customers.map(c =>
                        `  • ID#${c.id} | ${c.name} | ${c.email} | SĐT: ${c.phone || 'N/A'}${c.order_count ? ` | ${c.order_count} đơn hàng | DT: ${Number(c.total_revenue||0).toLocaleString('vi-VN')}đ` : ''} | Tham gia: ${new Date(c.created_at).toLocaleDateString('vi-VN')}`
                    ).join('\n'))
            }
            if (ctxData.orders?.length) {
                const summary = ctxData.orders_summary
                const headerNote = summary && summary.total_found > summary.showing
                    ? ` (hiển thị ${summary.showing}/${summary.total_found} đơn)`
                    : ` (${ctxData.orders.length} đơn)`
                parts.push(`\n🛒 Đơn hàng tìm thấy${headerNote}:\n` +
                    ctxData.orders.map(o =>
                        `  • ${o.order_number} | KH: ${o.customer_name} (${o.customer_phone||''}) | ${Number(o.total||0).toLocaleString('vi-VN')}đ | ${o.status} | TT: ${o.payment_status}`
                    ).join('\n'))
                if (summary) {
                    parts.push(`  📊 Tổng: ${summary.total_found} đơn | Doanh thu: ${Number(summary.total_revenue||0).toLocaleString('vi-VN')}đ | Đã TT: ${summary.paid_count} | Chưa TT: ${summary.unpaid_count}`)
                }
            }
            if (ctxData.products?.length) {
                parts.push(`\n📦 Sản phẩm tìm thấy:\n` +
                    ctxData.products.map(p =>
                        `  • ID#${p.id} | ${p.name} | ${Number(p.price||0).toLocaleString('vi-VN')}đ | ${p.status}`
                    ).join('\n'))
            }
            if (ctxData.debts?.length) {
                parts.push(`\n💳 Công nợ tìm thấy:\n` +
                    ctxData.debts.map(d =>
                        `  • ${d.customer_name} (${d.customer_email||''}) | Gốc: ${Number(d.original_amount||0).toLocaleString('vi-VN')}đ | Đã TT: ${Number(d.paid_amount||0).toLocaleString('vi-VN')}đ | Còn nợ: ${Number(d.remaining_amount||0).toLocaleString('vi-VN')}đ | ${d.status}`
                    ).join('\n'))
            }
            if (ctxData.suppliers?.length) {
                parts.push(`\n🏭 Nhà cung cấp:\n` +
                    ctxData.suppliers.map(s => `  • ${s.name} | ${s.phone||''} | ${s.email||''}`).join('\n'))
            }
            if (ctxData.bundles?.length) {
                parts.push(`\n🗂️ Nhóm sản phẩm:\n` +
                    ctxData.bundles.map(b => `  • ${b.name} | ${b.category||''} | ${b.price ? Number(b.price).toLocaleString('vi-VN')+'đ' : 'Chưa có giá'}`).join('\n'))
            }
            contextBlock = parts.join('\n')
        }
    } catch {}

    // Phát hiện ý định tạo đơn hàng từ text
    const isOrderIntent = /tạo đơn|tạo order|tạo b2b|nhập đơn|lập đơn|tạo hóa đơn|điền đơn|import đơn/i.test(text || '')
    const isImageOrderIntent = image && /tạo đơn|tạo order|nhập đơn|lập đơn|điền đơn|đơn hàng này|tạo hóa đơn/i.test(text || '')

    const systemPrompt = image
        ? (isImageOrderIntent
            ? `Bạn là AI Assistant của hệ thống quản trị DuyTris Admin Panel.
Nhiệm vụ: Đọc ảnh và trích xuất thông tin để tạo đơn hàng B2B.
Hãy đọc CHÍNH XÁC từ ảnh và trả về JSON theo định dạng sau (KHÔNG thêm text ngoài JSON):
{"__order__":true,"customer_name":"...","customer_phone":"...","customer_email":"","customer_address":"","order_date":"YYYY-MM-DD","delivery_date":"YYYY-MM-DD hoặc rỗng","order_name":"...","notes":"...","items":[{"type":"item","description":"Tên sản phẩm","product_code":"Mã SP","origin":"VN","unit":"Cái","quantity":1,"unit_price":0,"note":""}]}
Nếu có dòng tiêu đề/nhóm trong ảnh, dùng type:"category" và chỉ có field description.
Ngày định dạng YYYY-MM-DD. Số không có dấu phẩy/chấm ngàn.`
            : `Bạn là AI Assistant của hệ thống quản trị DuyTris Admin Panel.
Nhiệm vụ hiện tại: Đọc và phân tích NỘI DUNG THỰC TẾ trong ảnh được gửi lên.
QUAN TRỌNG: Hãy đọc chính xác text, số liệu, tên sản phẩm, mã code TRỰC TIẾP từ ảnh. KHÔNG suy đoán hay thay thế bằng dữ liệu khác.
Trả lời ngắn gọn, thân thiện bằng tiếng Việt. Dùng markdown để format. Dùng emoji phù hợp.
KHÔNG trả về JSON hay code block. Chỉ trả lời bằng văn bản tự nhiên.`)
        : (isOrderIntent
            ? `Bạn là AI Assistant của hệ thống quản trị DuyTris Admin Panel.
Nhiệm vụ: Trích xuất thông tin đơn hàng B2B từ nội dung người dùng cung cấp.
Trả về JSON theo định dạng sau (KHÔNG thêm text ngoài JSON):
{"__order__":true,"customer_name":"...","customer_phone":"...","customer_email":"","customer_address":"","order_date":"YYYY-MM-DD","delivery_date":"","order_name":"...","notes":"...","items":[{"type":"item","description":"Tên sản phẩm","product_code":"","origin":"VN","unit":"Cái","quantity":1,"unit_price":0,"note":""}]}
Nếu thiếu thông tin, để trống hoặc dùng giá trị mặc định hợp lý. Ngày định dạng YYYY-MM-DD.`
            : `Bạn là AI Assistant của hệ thống quản trị DuyTris Admin Panel. Bạn có quyền đọc toàn bộ dữ liệu hệ thống.
Hệ thống quản lý: Khách hàng, Sản phẩm, Danh mục, Đơn hàng, Công nợ, Nhà cung cấp, Hóa đơn nhập/bán, Biên bản, Tạm ứng, Nhóm sản phẩm, Cài đặt.
Khi người dùng muốn TẠO ĐƠN HÀNG từ dữ liệu đã có (ảnh, text, bảng), hãy trả về JSON với format: {"__order__":true,...dữ liệu đơn hàng...}
Trả lời ngắn gọn, thân thiện bằng tiếng Việt. Dùng markdown để format. Dùng emoji phù hợp.
QUAN TRỌNG: KHÔNG trả về JSON hay code block trừ khi tạo đơn hàng. Chỉ trả lời bằng văn bản tự nhiên.`)

    // Build messages cho API
    const historyMsgs = tab.messages.slice(-10).filter(m => m !== userMsg)
    const apiMessages = [
        { role: 'system', content: systemPrompt },
        ...historyMsgs.map(m => ({ role: m.role, content: m.content })),
    ]

    // Thêm message cuối — inject context trực tiếp vào user message
    // Khi có ảnh: chỉ dùng text của user (không inject DB context) để AI đọc ảnh chính xác
    // Khi không có ảnh: inject context DB để AI trả lời nhanh hơn
    const userTextWithContext = contextBlock
        ? `${contextBlock}\n\n━━ YÊU CẦU CỦA ADMIN ━━\n${text || 'Phân tích thông tin trên'}`
        : (text || (image ? 'Hãy đọc và liệt kê chính xác toàn bộ nội dung trong ảnh này' : 'Phân tích thông tin trên'))

    if (image) {
        apiMessages.push({
            role: 'user',
            content: [
                { type: 'text', text: userTextWithContext },
                { type: 'image_url', image_url: { url: `data:${image.mimeType};base64,${image.base64}` } }
            ]
        })
    } else {
        apiMessages.push({ role: 'user', content: userTextWithContext })
    }

    const ctrl = new AbortController()
    tab.abortCtrl = ctrl

    try {
        const body = {
            messages:        apiMessages,
            context:         'admin_assistant',
            conversation_id: tab.conversationId ?? undefined,
            has_image:       !!image,
        }
        if (selectedProvider.value) body.provider_id = selectedProvider.value

        const res = await apiFetch('/admin/ai/chat', {
            method: 'POST',
            body:   JSON.stringify(body),
            signal: ctrl.signal,
        })

        // Xử lý lỗi HTTP trước khi parse JSON
        if (!res.ok) {
            let errMsg = `Lỗi HTTP ${res.status}`
            try {
                const errData = await res.json()
                if (res.status === 401) errMsg = '🔐 Phiên đăng nhập hết hạn. Vui lòng tải lại trang.'
                else if (res.status === 403) errMsg = '🚫 Không có quyền truy cập AI.'
                else if (res.status === 422) errMsg = errData.message ?? errData.error ?? errMsg
                else if (res.status === 503) errMsg = errData.error ?? 'Tất cả AI providers đều không khả dụng.'
                else errMsg = errData.message ?? errData.error ?? errMsg
            } catch {}
            tab.messages.push({ role: 'assistant', content: `❌ ${errMsg}` })
            return
        }

        const data = await res.json()

        if (data.error) {
            tab.messages.push({ role: 'assistant', content: `❌ ${data.error}` })
        } else {
            let content = data.content ?? ''

            // ── Detect JSON đơn hàng từ AI ────────────────────────────────────
            let orderData = null
            try {
                // Thử parse toàn bộ content như JSON
                const trimmed = content.trim()
                if (trimmed.startsWith('{') && trimmed.includes('__order__')) {
                    const parsed = JSON.parse(trimmed)
                    if (parsed.__order__) orderData = parsed
                }
                // Thử tìm JSON block trong markdown
                if (!orderData) {
                    const jsonMatch = content.match(/```(?:json)?\s*(\{[\s\S]*?"__order__"[\s\S]*?\})\s*```/)
                    if (jsonMatch) {
                        const parsed = JSON.parse(jsonMatch[1])
                        if (parsed.__order__) orderData = parsed
                    }
                }
                // Thử tìm JSON inline
                if (!orderData) {
                    const inlineMatch = content.match(/\{[^{}]*"__order__"[^{}]*(?:\{[^{}]*\}[^{}]*)?\}/)
                    if (inlineMatch) {
                        const parsed = JSON.parse(inlineMatch[0])
                        if (parsed.__order__) orderData = parsed
                    }
                }
            } catch {}

            if (orderData) {
                // Xóa JSON khỏi content hiển thị
                content = content.replace(/```(?:json)?\s*\{[\s\S]*?"__order__"[\s\S]*?\}\s*```/g, '').trim()
                content = content.replace(/\{[\s\S]*?"__order__"[\s\S]*?\}/g, '').trim()

                // Tạo summary text để hiển thị
                const itemCount = (orderData.items || []).filter(i => i.type !== 'category').length
                const total = (orderData.items || [])
                    .filter(i => i.type !== 'category')
                    .reduce((s, i) => s + (Number(i.unit_price || 0) * Number(i.quantity || 0)), 0)

                const summaryLines = [
                    `📋 **Đã trích xuất đơn hàng từ ${image ? 'ảnh' : 'nội dung'}:**`,
                    orderData.customer_name ? `👤 Khách hàng: **${orderData.customer_name}**${orderData.customer_phone ? ` | ${orderData.customer_phone}` : ''}` : '',
                    orderData.order_date ? `📅 Ngày đặt: **${orderData.order_date}**` : '',
                    orderData.delivery_date ? `🚚 Ngày giao: **${orderData.delivery_date}**` : '',
                    `📦 Số sản phẩm: **${itemCount} dòng**`,
                    total > 0 ? `💰 Tổng tiền (ước tính): **${total.toLocaleString('vi-VN')}đ**` : '',
                    orderData.notes ? `📝 Ghi chú: ${orderData.notes}` : '',
                ].filter(Boolean).join('\n')

                tab.messages.push({
                    role: 'assistant',
                    content: summaryLines,
                    model_used: data.model_used,
                    response_time_ms: data.response_time_ms,
                    orderData,   // đính kèm để render card xác nhận
                })
            } else {
                // Lọc bỏ JSON block thường nếu AI vẫn trả về
                content = content.replace(/```json[\s\S]*?```/gi, '').trim()
                content = content.replace(/\{"type":\s*"navigate"[\s\S]*?\}/g, '').trim()
                if (!content) content = '_(Không có nội dung trả về)_'

                tab.messages.push({ role: 'assistant', content, model_used: data.model_used, response_time_ms: data.response_time_ms })
            }

            if (data.conversation_id) {
                tab.conversationId = data.conversation_id
                if (image && userMsg.imageId) {
                    apiFetch(`/admin/ai/images/${userMsg.imageId}/attach`, {
                        method: 'PATCH',
                        body: JSON.stringify({ conversation_id: data.conversation_id }),
                    }).catch(() => {})
                }
            }
            if (tab.title === 'Chat mới') tab.title = (text || 'Ảnh').slice(0, 30) + ((text?.length > 30) ? '…' : '')
        }
    } catch (err) {
        if (err.name !== 'AbortError') {
            // Lỗi network thực sự (offline, CORS, v.v.)
            const isOffline = !navigator.onLine
            tab.messages.push({
                role: 'assistant',
                content: isOffline
                    ? '📡 Mất kết nối mạng. Kiểm tra internet và thử lại.'
                    : `❌ Lỗi kết nối: ${err.message || 'Network error'}. Kiểm tra cấu hình tại \`/admin/ai-providers\``
            })
        }
    } finally {
        tab.loading   = false
        tab.abortCtrl = null
        await nextTick(); scrollToBottom()
        saveState()
    }
}

function stopGeneration() {
    const tab = activeTab.value
    if (tab.abortCtrl) {
        tab.abortCtrl.abort()
        tab.abortCtrl = null
        tab.loading   = false
        tab.messages.push({ role: 'assistant', content: '⏹ Đã dừng.' })
    }
}

/**
 * Điều hướng đến form tạo đơn hàng B2B với dữ liệu đã trích xuất
 */
function createOrderFromData(orderData) {
    try {
        // Lưu dữ liệu vào sessionStorage để form đọc
        sessionStorage.setItem('ai_order_prefill', JSON.stringify(orderData))
    } catch {}
    router.visit('/admin/b2b-orders/create?ai_prefill=1')
}

/**
 * Từ chối tạo đơn — xóa orderData khỏi message để ẩn card
 */
function dismissOrder(msgIndex) {
    const tab = activeTab.value
    if (tab.messages[msgIndex]) {
        tab.messages[msgIndex] = { ...tab.messages[msgIndex], orderData: null, orderDismissed: true }
    }
}

function scrollToBottom() {
    if (container.value) container.value.scrollTop = container.value.scrollHeight
}

function onKeydown(e) {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send() }
}

function useQuick(text) { input.value = text; send() }

function toggle() {
    isOpen.value = !isOpen.value
    isMinimized.value = false
    if (isOpen.value) {
        loadProviders()
        loadStorageInfo()
        nextTick(() => {
            inputRef.value?.focus()
            restoreImagesInMessages(activeTab.value?.messages ?? [])
        })
    } else {
        showImageLib.value = false
    }
}

// ── Paste image from clipboard ────────────────────────────────────────────────
function onPaste(e) {
    const items = e.clipboardData?.items
    if (!items) return
    for (const item of items) {
        if (item.type.startsWith('image/')) {
            const file = item.getAsFile()
            if (!file) continue
            const reader = new FileReader()
            reader.onload = ev => {
                const dataUrl = ev.target.result
                pendingImage.value = { dataUrl, base64: dataUrl.split(',')[1], mimeType: file.type, name: 'clipboard.png' }
            }
            reader.readAsDataURL(file)
            e.preventDefault()
            break
        }
    }
}

// ── Helper fetch ──────────────────────────────────────────────────────────────
function apiFetch(url, opts = {}) {
    // Lấy CSRF token từ meta tag (luôn đúng với Laravel session)
    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content ?? ''

    const headers = {
        'X-CSRF-TOKEN': csrfToken,
        'Accept':       'application/json',
    }
    if (!opts.body || typeof opts.body === 'string') headers['Content-Type'] = 'application/json'
    return fetch(url, { headers, credentials: 'include', ...opts })
}

// ── Draggable ─────────────────────────────────────────────────────────────────
const posBottom = ref(24)
const posRight  = ref(24)
const dragging  = ref(false)
const dragData  = ref({ startX: 0, startY: 0, startBottom: 24, startRight: 24 })

function startDrag(e) {
    if (e.target.closest('button') || e.target.closest('textarea') || e.target.closest('input')) return
    e.preventDefault()
    dragging.value = true
    const cx = e.touches ? e.touches[0].clientX : e.clientX
    const cy = e.touches ? e.touches[0].clientY : e.clientY
    dragData.value = { startX: cx, startY: cy, startBottom: posBottom.value, startRight: posRight.value }
    document.addEventListener('mousemove', onDrag)
    document.addEventListener('mouseup', stopDrag)
    document.addEventListener('touchmove', onDrag, { passive: false })
    document.addEventListener('touchend', stopDrag)
}

function onDrag(e) {
    if (!dragging.value) return
    if (e.cancelable) e.preventDefault()
    const cx = e.touches ? e.touches[0].clientX : e.clientX
    const cy = e.touches ? e.touches[0].clientY : e.clientY
    const chatW  = isExpanded.value ? 560 : 400
    const chatH  = isMinimized.value ? 52 : (isExpanded.value ? window.innerHeight - 120 : 560)
    const totalH = isOpen.value ? chatH + 56 + 12 : 56
    posRight.value  = Math.max(8, Math.min(window.innerWidth  - chatW - 8, dragData.value.startRight  - (cx - dragData.value.startX)))
    posBottom.value = Math.max(8, Math.min(window.innerHeight - totalH - 8, dragData.value.startBottom - (cy - dragData.value.startY)))
}

function stopDrag() {
    dragging.value = false
    document.removeEventListener('mousemove', onDrag)
    document.removeEventListener('mouseup', stopDrag)
    document.removeEventListener('touchmove', onDrag)
    document.removeEventListener('touchend', stopDrag)
    saveState()
}

// ── Lifecycle ─────────────────────────────────────────────────────────────────
onMounted(() => {
    initVoice()
    const saved = loadState()
    if (saved) {
        if (saved.tabs?.length) {
            tabs.value = saved.tabs.map(t => ({ ...t, loading: false, abortCtrl: null }))
            tabCounter = Math.max(...tabs.value.map(t => t.id), 1)
        }
        if (saved.activeTabId) activeTabId.value = saved.activeTabId
        if (saved.posBottom != null) posBottom.value = saved.posBottom
        if (saved.posRight  != null) posRight.value  = saved.posRight
        if (saved.isOpen)    isOpen.value    = saved.isOpen
        if (saved.isExpanded) isExpanded.value = saved.isExpanded
    }
    if (isOpen.value) {
        loadProviders()
        loadStorageInfo()
        // Restore ảnh cho tab đang active
        nextTick(() => restoreImagesInMessages(activeTab.value?.messages ?? []))
    }
})

onUnmounted(() => {
    stopDrag()
    if (recognition) recognition.abort()
})

watch([tabs, activeTabId], saveState, { deep: true })
</script>

<template>
    <!-- Hidden file input -->
    <input ref="fileInputRef" type="file" accept="image/*" class="hidden" @change="onImagePicked" />

    <div
        class="fixed z-50 flex flex-col items-end gap-3"
        :style="`bottom: ${posBottom}px; right: ${posRight}px; user-select: none;`"
    >
        <!-- ── Chat window ── -->
        <Transition name="chat">
            <div v-if="isOpen"
                class="flex flex-col bg-white rounded-2xl shadow-2xl border border-gray-200 overflow-hidden"
                :style="{
                    width:      isExpanded ? '560px' : '400px',
                    height:     isMinimized ? '52px' : (isExpanded ? 'calc(100vh - 120px)' : '560px'),
                    maxHeight:  'calc(100vh - 120px)',
                    transition: dragging ? 'none' : 'width 0.2s ease, height 0.2s ease',
                }">

                <!-- Header -->
                <div
                    class="flex items-center gap-1.5 px-3 py-2 bg-indigo-600 text-white shrink-0"
                    :class="dragging ? 'cursor-grabbing' : 'cursor-grab'"
                    @mousedown="startDrag" @touchstart.passive="startDrag"
                >
                    <GripVertical :size="12" class="opacity-40 shrink-0" />
                    <Bot :size="14" class="shrink-0" />
                    <span class="text-xs font-semibold select-none flex-1 truncate">AI Assistant</span>

                    <button @click.stop="showProviders = !showProviders; showHistory = false"
                        :class="['p-1 rounded transition-colors', showProviders ? 'bg-indigo-400' : 'hover:bg-indigo-500']"
                        title="Chọn AI model"><Cpu :size="12" /></button>

                    <button @click.stop="showHistory = !showHistory; showProviders = false; if(showHistory) loadHistory()"
                        :class="['p-1 rounded transition-colors', showHistory ? 'bg-indigo-400' : 'hover:bg-indigo-500']"
                        title="Lịch sử chat"><History :size="12" /></button>

                    <button @click.stop="newTab"
                        class="p-1 rounded hover:bg-indigo-500 transition-colors" title="Chat mới">
                        <Plus :size="12" /></button>

                    <button @click.stop="isExpanded = !isExpanded" class="p-1 rounded hover:bg-indigo-500 transition-colors">
                        <Maximize2 v-if="!isExpanded" :size="12" /><Minimize2 v-else :size="12" /></button>

                    <button @click.stop="isMinimized = !isMinimized" class="p-1 rounded hover:bg-indigo-500 transition-colors">
                        <ChevronDown v-if="!isMinimized" :size="12" /><ChevronUp v-else :size="12" /></button>

                    <button @click.stop="isOpen = false" class="p-1 rounded hover:bg-indigo-500 transition-colors">
                        <X :size="12" /></button>
                </div>

                <template v-if="!isMinimized">

                    <!-- Provider dropdown -->
                    <div v-if="showProviders" class="border-b border-gray-100 bg-gray-50 px-3 py-2 shrink-0 max-h-44 overflow-y-auto">
                        <p class="text-xs text-gray-500 mb-1.5 font-medium">Chọn AI model:</p>
                        <label class="flex items-center gap-2 cursor-pointer hover:bg-white rounded px-1.5 py-1">
                            <input type="radio" :value="null" v-model="selectedProvider" class="accent-indigo-600" />
                            <span class="text-xs text-gray-700">🤖 Tự động (Smart select)</span>
                        </label>
                        <label v-for="p in providers" :key="p.id"
                            class="flex items-center gap-2 cursor-pointer hover:bg-white rounded px-1.5 py-1">
                            <input type="radio" :value="p.id" v-model="selectedProvider" class="accent-indigo-600" />
                            <span class="text-xs text-gray-700 truncate">{{ p.name }}
                                <span class="text-gray-400 text-[10px]">({{ p.model }})</span>
                            </span>
                            <span v-if="p.is_default" class="ml-auto text-[10px] bg-indigo-100 text-indigo-600 px-1 rounded">default</span>
                        </label>
                        <p v-if="!providers.length" class="text-xs text-gray-400 py-1">Chưa có provider nào active</p>
                    </div>

                    <!-- Storage warning bar (hiện khi >= 80% hoặc over quota) -->
                    <div v-if="imageStorageInfo && (imageStorageInfo.warning || imageStorageInfo.over_quota)"
                        :class="[
                            'shrink-0 px-3 py-2 border-b text-xs flex items-center gap-2',
                            imageStorageInfo.over_quota
                                ? 'bg-red-50 border-red-200 text-red-700'
                                : 'bg-amber-50 border-amber-200 text-amber-700'
                        ]">
                        <span class="text-base leading-none">{{ imageStorageInfo.over_quota ? '🚫' : '⚠️' }}</span>
                        <div class="flex-1 min-w-0">
                            <div class="font-medium">
                                {{ imageStorageInfo.over_quota ? 'Đã đầy dung lượng ảnh!' : 'Sắp đầy dung lượng ảnh' }}
                            </div>
                            <div class="opacity-80">
                                {{ imageStorageInfo.used_mb }}MB / {{ imageStorageInfo.quota_gb }}GB
                                ({{ imageStorageInfo.percent }}%)
                            </div>
                            <!-- Progress bar -->
                            <div class="mt-1 h-1 rounded-full bg-black/10 overflow-hidden">
                                <div :class="['h-full rounded-full transition-all', imageStorageInfo.over_quota ? 'bg-red-500' : 'bg-amber-500']"
                                    :style="`width: ${Math.min(imageStorageInfo.percent, 100)}%`" />
                            </div>
                        </div>
                        <a href="/admin/ai-providers?tab=images" target="_blank"
                            :class="['shrink-0 text-[10px] px-2 py-1 rounded font-medium whitespace-nowrap',
                                imageStorageInfo.over_quota ? 'bg-red-600 text-white hover:bg-red-700' : 'bg-amber-600 text-white hover:bg-amber-700']">
                            Quản lý ảnh
                        </a>
                    </div>

                    <!-- History panel -->
                    <div v-if="showHistory" class="flex-1 overflow-y-auto bg-gray-50">
                        <div class="flex items-center gap-2 px-3 py-2 border-b border-gray-100 bg-white sticky top-0">
                            <button @click="showHistory = false" class="p-0.5 rounded hover:bg-gray-100">
                                <ChevronLeft :size="14" class="text-gray-500" /></button>
                            <span class="text-xs font-semibold text-gray-700">Lịch sử hội thoại</span>
                        </div>
                        <div v-if="historyLoading" class="flex justify-center py-8">
                            <Loader2 :size="20" class="animate-spin text-indigo-400" />
                        </div>
                        <div v-else-if="!history.length" class="text-center py-10 text-xs text-gray-400">
                            Chưa có lịch sử chat
                        </div>
                        <div v-else class="divide-y divide-gray-100">
                            <div v-for="conv in history" :key="conv.id"
                                class="flex items-center gap-2 px-3 py-2.5 hover:bg-white cursor-pointer group"
                                @click="openHistory(conv)">
                                <MessageSquare :size="13" class="text-indigo-400 shrink-0" />
                                <div class="flex-1 min-w-0">
                                    <p class="text-xs font-medium text-gray-700 truncate">{{ conv.title }}</p>
                                    <p class="text-[10px] text-gray-400">{{ new Date(conv.updated_at).toLocaleDateString('vi-VN') }}</p>
                                </div>
                                <button @click.stop="deleteHistory(conv.id)"
                                    class="opacity-0 group-hover:opacity-100 p-0.5 rounded hover:bg-red-50 text-red-400 transition-opacity">
                                    <Trash2 :size="12" /></button>
                            </div>
                        </div>
                    </div>

                    <!-- Tabs bar -->
                    <div v-if="!showHistory && tabs.length > 1"
                        class="flex items-center gap-0.5 px-2 pt-1.5 bg-gray-50 border-b border-gray-100 overflow-x-auto shrink-0 scrollbar-none">
                        <button v-for="tab in tabs" :key="tab.id"
                            @click="switchTab(tab.id)"
                            :class="[
                                'flex items-center gap-1 px-2.5 py-1 rounded-t text-xs whitespace-nowrap transition-colors max-w-[130px]',
                                tab.id === activeTabId
                                    ? 'bg-white text-indigo-700 font-medium border border-b-white border-gray-200 -mb-px'
                                    : 'text-gray-500 hover:bg-gray-100'
                            ]">
                            <Loader2 v-if="tab.loading" :size="10" class="animate-spin shrink-0 text-indigo-500" />
                            <span class="truncate">{{ tab.title }}</span>
                            <button @click.stop="closeTab(tab.id)" class="ml-0.5 rounded hover:bg-gray-200 p-0.5 shrink-0">
                                <X :size="9" /></button>
                        </button>
                    </div>

                    <!-- Messages -->
                    <div v-if="!showHistory" ref="container"
                        class="flex-1 overflow-y-auto p-3 space-y-3 bg-gray-50">

                        <div v-for="(msg, i) in activeTab.messages" :key="i"
                            :class="['flex', msg.role === 'user' ? 'justify-end' : 'justify-start']">
                            <div :class="[
                                'max-w-[90%] rounded-2xl px-3 py-2 text-sm leading-relaxed break-words',
                                msg.role === 'user'
                                    ? 'bg-indigo-600 text-white rounded-br-sm'
                                    : 'bg-white text-gray-800 border border-gray-200 rounded-bl-sm shadow-sm prose prose-sm max-w-none'
                            ]">
                                <!-- Ảnh đính kèm (user) -->
                                <img v-if="msg.imageData" :src="msg.imageData"
                                    class="rounded-lg mb-1.5 max-h-40 object-cover" alt="ảnh đính kèm" />

                                <!-- Nội dung: markdown cho AI, plain text cho user -->
                                <div v-if="msg.role === 'assistant'"
                                    class="ai-message"
                                    v-html="renderMarkdown(msg.content)" />
                                <span v-else class="whitespace-pre-wrap">{{ msg.content }}</span>

                                <!-- Model badge -->
                                <span v-if="msg.model_used"
                                    class="block text-[10px] opacity-40 mt-1 not-prose">
                                    {{ msg.model_used }}
                                    <span v-if="msg.response_time_ms" class="ml-1 opacity-70">· {{ msg.response_time_ms }}ms</span>
                                </span>
                            </div>

                            <!-- ── Card xác nhận tạo đơn hàng ── -->
                            <div v-if="msg.orderData && !msg.orderDismissed"
                                class="mt-2 rounded-xl border border-indigo-200 bg-indigo-50 p-3 text-sm max-w-[90%]">
                                <p class="font-semibold text-indigo-800 mb-2 text-xs">🛒 Bạn có muốn tạo đơn hàng này không?</p>

                                <!-- Preview items -->
                                <div v-if="msg.orderData.items?.length" class="mb-2 max-h-28 overflow-y-auto space-y-0.5">
                                    <div v-for="(item, ii) in msg.orderData.items" :key="ii"
                                        :class="['text-xs', item.type === 'category' ? 'font-semibold text-indigo-700 mt-1' : 'text-gray-700 pl-2']">
                                        <span v-if="item.type === 'category'">📁 {{ item.description }}</span>
                                        <span v-else>
                                            {{ item.description }}
                                            <span v-if="item.product_code" class="text-gray-400 ml-1">[{{ item.product_code }}]</span>
                                            <span class="text-gray-500 ml-1">× {{ item.quantity }} {{ item.unit }}</span>
                                            <span v-if="item.unit_price > 0" class="text-indigo-600 ml-1">= {{ Number(item.unit_price * item.quantity).toLocaleString('vi-VN') }}đ</span>
                                        </span>
                                    </div>
                                </div>

                                <div class="flex gap-2 mt-2">
                                    <button @click="createOrderFromData(msg.orderData)"
                                        class="flex-1 py-1.5 rounded-lg bg-indigo-600 text-white text-xs font-medium hover:bg-indigo-700 transition-colors">
                                        ✅ Mở form tạo đơn
                                    </button>
                                    <button @click="dismissOrder(i)"
                                        class="px-3 py-1.5 rounded-lg border border-gray-300 text-gray-600 text-xs hover:bg-gray-100 transition-colors">
                                        ✕ Bỏ qua
                                    </button>
                                </div>
                            </div>
                            <div v-else-if="msg.orderDismissed" class="mt-1 text-[10px] text-gray-400 italic">
                                Đã bỏ qua tạo đơn hàng
                            </div>
                        </div>

                        <!-- Loading dots -->
                        <div v-if="activeTab.loading" class="flex justify-start">
                            <div class="bg-white border border-gray-200 rounded-2xl rounded-bl-sm px-3 py-2.5 shadow-sm">
                                <span class="flex gap-1 items-center">
                                    <span v-for="n in 3" :key="n"
                                        class="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce"
                                        :style="`animation-delay:${(n-1)*150}ms`" />
                                </span>
                            </div>
                        </div>
                    </div>

                    <!-- Quick actions -->
                    <div v-if="!showHistory && activeTab.messages.length <= 2"
                        class="px-3 pb-2 flex flex-wrap gap-1.5 shrink-0">
                        <button v-for="qa in quickActions" :key="qa.label"
                            @click="useQuick(qa.text)"
                            class="text-xs px-2.5 py-1 rounded-full bg-indigo-50 text-indigo-700 hover:bg-indigo-100 border border-indigo-200 transition-colors">
                            {{ qa.label }}
                        </button>
                    </div>

                    <!-- Input area -->
                    <div v-if="!showHistory" class="border-t border-gray-100 bg-white shrink-0">

                        <!-- Pending image preview -->
                        <div v-if="pendingImage" class="flex items-center gap-2 px-3 pt-2">
                            <div class="relative">
                                <img :src="pendingImage.dataUrl" class="h-14 w-14 rounded-lg object-cover border border-gray-200" />
                                <button @click="removePendingImage"
                                    class="absolute -top-1.5 -right-1.5 w-4 h-4 bg-red-500 text-white rounded-full flex items-center justify-center">
                                    <X :size="9" />
                                </button>
                            </div>
                            <span class="text-xs text-gray-500 truncate">{{ pendingImage.name }}</span>
                        </div>

                        <!-- Voice listening indicator -->
                        <div v-if="isListening" class="flex items-center gap-2 px-3 pt-2">
                            <span class="flex gap-0.5">
                                <span v-for="n in 4" :key="n"
                                    class="w-0.5 bg-red-500 rounded-full animate-pulse"
                                    :style="`height:${8 + n*3}px; animation-delay:${n*80}ms`" />
                            </span>
                            <span class="text-xs text-red-500 font-medium">Đang nghe...</span>
                        </div>

                        <div class="flex items-end gap-1.5 p-2.5">
                            <!-- Image button (upload mới) -->
                            <button @click="triggerImagePick" :disabled="activeTab.loading"
                                :class="['shrink-0 w-8 h-8 flex items-center justify-center rounded-xl transition-colors disabled:opacity-40',
                                    pendingImage ? 'bg-indigo-100 text-indigo-600' : 'bg-gray-100 text-gray-500 hover:bg-gray-200']"
                                title="Đính kèm ảnh mới (hoặc Ctrl+V)">
                                <ImagePlus :size="15" />
                            </button>

                            <!-- Library button (ảnh đã lưu) -->
                            <button @click="openImageLib" :disabled="activeTab.loading"
                                :class="['shrink-0 w-8 h-8 flex items-center justify-center rounded-xl transition-colors disabled:opacity-40',
                                    showImageLib ? 'bg-indigo-100 text-indigo-600' : 'bg-gray-100 text-gray-500 hover:bg-gray-200']"
                                title="Chọn ảnh từ thư viện đã lưu">
                                <FolderOpen :size="15" />
                            </button>

                            <!-- Voice button -->
                            <button v-if="voiceSupported" @click="toggleVoice" :disabled="activeTab.loading"
                                :class="['shrink-0 w-8 h-8 flex items-center justify-center rounded-xl transition-colors disabled:opacity-40',
                                    isListening ? 'bg-red-500 text-white animate-pulse' : 'bg-gray-100 text-gray-500 hover:bg-gray-200']"
                                :title="isListening ? 'Dừng ghi âm' : 'Nhập bằng giọng nói'">
                                <Mic v-if="!isListening" :size="15" />
                                <MicOff v-else :size="15" />
                            </button>

                            <!-- Text input -->
                            <textarea ref="inputRef" v-model="input"
                                @keydown="onKeydown" @paste="onPaste"
                                :disabled="activeTab.loading"
                                :placeholder="isListening ? 'Đang nghe giọng nói...' : 'Nhập tin nhắn... '"
                                class="flex-1 resize-none rounded-xl border border-gray-200 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:opacity-50"
                                style="min-height:36px;max-height:96px" />

                            <!-- Stop / Send -->
                            <button v-if="activeTab.loading" @click="stopGeneration"
                                class="shrink-0 w-8 h-8 flex items-center justify-center rounded-xl bg-red-500 text-white hover:bg-red-600 transition-colors"
                                title="Dừng">
                                <X :size="14" />
                            </button>
                            <button v-else @click="send" :disabled="!input.trim() && !pendingImage"
                                class="shrink-0 w-8 h-8 flex items-center justify-center rounded-xl bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-40 transition-colors">
                                <Send :size="14" />
                            </button>
                        </div>

                        <!-- Image Library panel -->
                        <div v-if="showImageLib"
                            class="border-t border-gray-100 bg-gray-50 px-3 py-2.5 max-h-52 overflow-y-auto">
                            <div class="flex items-center justify-between mb-2">
                                <span class="text-xs font-semibold text-gray-600">📁 Thư viện ảnh đã lưu</span>
                                <div class="flex items-center gap-1.5">
                                    <button @click="loadImageLib" :disabled="imageLibLoading"
                                        class="p-1 rounded hover:bg-gray-200 text-gray-400 disabled:opacity-40">
                                        <RefreshCw :size="11" :class="imageLibLoading ? 'animate-spin' : ''" />
                                    </button>
                                    <a href="/admin/ai-providers/images" target="_blank"
                                        class="text-[10px] text-indigo-500 hover:underline">Quản lý</a>
                                </div>
                            </div>

                            <!-- Loading -->
                            <div v-if="imageLibLoading" class="flex justify-center py-4">
                                <RefreshCw :size="16" class="animate-spin text-indigo-400" />
                            </div>

                            <!-- Empty -->
                            <div v-else-if="!imageLibList.length" class="text-center py-4 text-xs text-gray-400">
                                <Image :size="20" class="mx-auto mb-1 opacity-30" />
                                Chưa có ảnh nào được lưu
                            </div>

                            <!-- Grid ảnh -->
                            <div v-else class="grid grid-cols-4 gap-1.5">
                                <button v-for="img in imageLibList" :key="img.id"
                                    @click="selectFromLibrary(img)"
                                    class="relative aspect-square rounded-lg overflow-hidden border border-gray-200 hover:border-indigo-400 hover:ring-2 hover:ring-indigo-200 transition-all group bg-gray-100"
                                    :title="img.original_name">
                                    <!-- Thumbnail loaded -->
                                    <img v-if="imageLibThumb[img.id] && imageLibThumb[img.id] !== 'loading' && imageLibThumb[img.id] !== 'error'"
                                        :src="imageLibThumb[img.id]"
                                        class="w-full h-full object-cover" />
                                    <!-- Loading -->
                                    <div v-else-if="imageLibThumb[img.id] === 'loading'"
                                        class="w-full h-full flex items-center justify-center">
                                        <RefreshCw :size="12" class="animate-spin text-gray-300" />
                                    </div>
                                    <!-- Error / placeholder -->
                                    <div v-else class="w-full h-full flex items-center justify-center">
                                        <Image :size="14" class="text-gray-300" />
                                    </div>
                                    <!-- Hover overlay -->
                                    <div class="absolute inset-0 bg-indigo-600/0 group-hover:bg-indigo-600/20 transition-colors flex items-center justify-center">
                                        <span class="opacity-0 group-hover:opacity-100 text-white text-[10px] font-bold drop-shadow">Chọn</span>
                                    </div>
                                </button>
                            </div>

                            <!-- Storage mini bar -->
                            <div v-if="imageStorageInfo" class="mt-2 pt-2 border-t border-gray-200">
                                <div class="flex items-center justify-between text-[10px] text-gray-400 mb-1">
                                    <span>{{ imageStorageInfo.used_mb }} MB / {{ imageStorageInfo.quota_gb }} GB</span>
                                    <span :class="imageStorageInfo.over_quota ? 'text-red-500 font-medium' : imageStorageInfo.warning ? 'text-amber-500' : ''">
                                        {{ imageStorageInfo.percent }}%
                                    </span>
                                </div>
                                <div class="h-1 rounded-full bg-gray-200 overflow-hidden">
                                    <div :class="['h-full rounded-full', imageStorageInfo.over_quota ? 'bg-red-500' : imageStorageInfo.warning ? 'bg-amber-500' : 'bg-indigo-400']"
                                        :style="`width:${Math.min(imageStorageInfo.percent,100)}%`" />
                                </div>
                            </div>
                        </div>
                    </div>
                </template>
            </div>
        </Transition>

        <!-- FAB -->
        <div
            class="w-14 h-14 flex items-center justify-center rounded-full bg-indigo-600 text-white shadow-lg relative"
            :class="dragging ? 'cursor-grabbing scale-95' : 'cursor-grab hover:bg-indigo-700 hover:scale-105'"
            style="transition: transform 0.15s ease, background-color 0.15s ease;"
            @mousedown="startDrag" @touchstart.passive="startDrag" @click="toggle"
        >
            <Bot v-if="!isOpen" :size="24" />
            <X v-else :size="22" />
            <span v-if="!isOpen && tabs.some(t => t.loading)"
                class="absolute -top-1 -right-1 w-4 h-4 bg-orange-500 rounded-full flex items-center justify-center text-[9px] font-bold">
                {{ tabs.filter(t => t.loading).length }}
            </span>
        </div>
    </div>
</template>

<style scoped>
.chat-enter-active, .chat-leave-active { transition: all 0.2s ease; }
.chat-enter-from, .chat-leave-to { opacity: 0; transform: translateY(12px) scale(0.96); }
.scrollbar-none::-webkit-scrollbar { display: none; }
.scrollbar-none { -ms-overflow-style: none; scrollbar-width: none; }

/* Markdown styles trong bubble AI */
.ai-message :deep(p)          { margin: 0 0 0.4em; }
.ai-message :deep(p:last-child){ margin-bottom: 0; }
.ai-message :deep(ul),
.ai-message :deep(ol)         { margin: 0.3em 0 0.3em 1.2em; padding: 0; }
.ai-message :deep(li)         { margin: 0.1em 0; }
.ai-message :deep(strong)     { font-weight: 600; }
.ai-message :deep(em)         { font-style: italic; }
.ai-message :deep(code)       { background: #f3f4f6; padding: 0.1em 0.3em; border-radius: 3px; font-size: 0.85em; }
.ai-message :deep(pre)        { background: #1e1e2e; color: #cdd6f4; padding: 0.6em 0.8em; border-radius: 8px; overflow-x: auto; margin: 0.4em 0; font-size: 0.8em; }
.ai-message :deep(pre code)   { background: none; padding: 0; color: inherit; }
.ai-message :deep(h1),.ai-message :deep(h2),.ai-message :deep(h3) { font-weight: 600; margin: 0.4em 0 0.2em; }
.ai-message :deep(blockquote) { border-left: 3px solid #6366f1; padding-left: 0.6em; color: #6b7280; margin: 0.3em 0; }
.ai-message :deep(a)          { color: #6366f1; text-decoration: underline; }
.ai-message :deep(hr)         { border: none; border-top: 1px solid #e5e7eb; margin: 0.5em 0; }
.ai-message :deep(table)      { border-collapse: collapse; width: 100%; font-size: 0.85em; margin: 0.4em 0; }
.ai-message :deep(th)         { background: #f3f4f6; padding: 0.3em 0.5em; border: 1px solid #e5e7eb; font-weight: 600; }
.ai-message :deep(td)         { padding: 0.3em 0.5em; border: 1px solid #e5e7eb; }
</style>
