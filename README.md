# 🎯 Quản lý Công nợ & Đơn hàng B2B - Desktop App

Ứng dụng desktop **100% offline** quản lý công nợ và đơn hàng B2B với giao diện hiện đại giống Vue.js, được build bằng **Python + PySide6 Native (không WebView)**.

## ✨ Tính năng chính

- ✅ **Dashboard** - Thống kê tổng quan với cards hiện đại
- ✅ **Quản lý đơn hàng B2B** - CRUD, Import/Export Excel
- ✅ **Quản lý công nợ** - Theo dõi thanh toán, cảnh báo quá hạn
- ✅ **Quản lý khách hàng** - Thông tin KH B2B
- ✅ **Quản lý sản phẩm** - Sản phẩm & biến thể
- ✅ **Giao diện Tailwind-like** - QSS styling giống Vue.js 99%
- ✅ **SQLite Database** - Local, không cần server
- ✅ **Excel Import/Export** - openpyxl
- ✅ **Build .exe** - PyInstaller, chạy độc lập

## 🏗️ Kiến trúc

```
┌─────────────────────────────────────────────┐
│         PySide6 Desktop Application         │
├─────────────────────────────────────────────┤
│  Native UI (QSS)  │  Business Logic (Python)│
│  - Dashboard      │  - Order Service        │
│  - Orders         │  - Debt Service         │
│  - Debts          │  - Customer Service     │
│  - Customers      │  - Product Service      │
│  - Products       │  - Excel Service        │
├─────────────────────────────────────────────┤
│         SQLite Database (Local)             │
└─────────────────────────────────────────────┘
```

**Không có WebView!** Tất cả là native PySide6 widgets với QSS styling.

## 📁 Cấu trúc dự án

```
congnopython/
├── main.py                      # Entry point
├── requirements.txt             # Python dependencies
├── run.bat                      # Chạy ứng dụng
├── build.bat                    # Build .exe
├── QuanLyB2B.spec              # PyInstaller spec
├── README.md                    # File này
├── src/
│   ├── database.py             # SQLite database layer
│   ├── services/               # Business logic
│   │   ├── customer_service.py # Customer CRUD
│   │   ├── product_service.py  # Product CRUD
│   │   ├── order_service.py    # Order CRUD + Stats
│   │   ├── debt_service.py     # Debt management
│   │   └── excel_service.py    # Excel import/export
│   └── ui/
│       ├── theme.py            # QSS theme (Vue.js style)
│       ├── native_main_window.py # Main window with sidebar
│       └── pages/
│           ├── dashboard_page.py    # Dashboard với stat cards
│           ├── orders_page.py       # B2B Orders table
│           ├── debts_page.py        # Debts table
│           ├── customers_page.py    # Customers CRUD
│           └── products_page.py     # Products CRUD
└── data/
    └── b2b_management.db       # SQLite (auto-created)
```

## 🚀 Cài đặt & Chạy

### 1. Cài đặt dependencies

```bash
cd congnopython
pip install -r requirements.txt
```

### 2. Chạy ứng dụng

**Cách 1:** Dùng script
```bash
run.bat
```

**Cách 2:** Chạy trực tiếp
```bash
python main.py
```

Ứng dụng sẽ:
1. ✅ Tạo SQLite database
2. ✅ Áp dụng QSS theme (giống Vue.js)
3. ✅ Mở cửa sổ chính với sidebar navigation

## 🎨 Giao diện

### Màu sắc (giống Vue.js Tailwind)

| Màu | Vue.js (Tailwind) | PySide6 (QSS) | Hex Code |
|-----|-------------------|---------------|----------|
| Primary | indigo-600 | #6366F1 | Buttons, links |
| Success | emerald-600 | #10B981 | Badges, stats |
| Warning | amber-500 | #F59E0B | Alerts, profit |
| Danger | red-500 | #EF4444 | Errors, debts |
| Background | gray-50 | #F9FAFB | Main background |
| Card | white | #FFFFFF | Cards, tables |
| Sidebar | slate-900 | #0F172A | Navigation |

### Components đã style

- ✅ **Stat Cards** - Gradient backgrounds, icons, values
- ✅ **Tables** - Hover effects, alternating colors, headers
- ✅ **Buttons** - Primary, success, warning, danger, outline
- ✅ **Badges** - Success, warning, danger, info, neutral
- ✅ **Inputs** - Focus states, hover effects
- ✅ **Sidebar** - Dark theme, navigation buttons
- ✅ **Scrollbars** - Modern, rounded
- ✅ **Dialogs** - Forms, modals

## 📊 Database Schema

### Tables chính

```sql
customers          -- Khách hàng B2B
  ├── id, name, phone, email, tax_code, address
  └── is_active, created_at, updated_at

products           -- Sản phẩm
  ├── id, name, sku, category_id, brand_id
  ├── purchase_price, sale_price, stock
  └── is_active, created_at

orders             -- Đơn hàng B2B
  ├── id, order_number, customer_id
  ├── total_before_tax, tax_amount, grand_total
  ├── total_profit, payment_status
  └── created_at, updated_at

order_items        -- Chi tiết đơn hàng
  ├── id, order_id, product_id
  ├── quantity, unit_price, total_price
  └── profit

debts              -- Công nợ
  ├── id, order_id, customer_id
  ├── original_amount, paid_amount, remaining_amount
  ├── payment_status, due_date
  └── created_at, updated_at

debt_payments      -- Lịch sử thanh toán
  ├── id, debt_id, amount, payment_date
  └── notes, created_at
```

## 📥 Import Excel

### Cấu trúc file Excel

```
| Column A      | Column B  | Column C | Column D     | Column E |
|---------------|-----------|----------|--------------|----------|
| Tên khách hàng| Ngày đặt  | STT      | Mô tả SP     | Mã hàng  |
| Nguyễn Văn A  | 01/01/2026| 1       | Sản phẩm ABC | PRD-001  |

| Column F | Column G | Column H | Column I  | Column J  |
|----------|----------|----------|-----------|-----------|
| Xuất xứ  | Đơn vị   | Số lượng | Đơn giá   | Thành tiền|
| Việt Nam | Cái      | 10       | 100,000   | 1,000,000 |
```

## 📦 Build thành .exe

### 1. Cài đặt PyInstaller

```bash
pip install pyinstaller
```

### 2. Build

**Cách 1:** Dùng script
```bash
build.bat
```

**Cách 2:** Chạy trực tiếp
```bash
pyinstaller QuanLyB2B.spec --clean
```

### 3. Kết quả

File .exe sẽ nằm trong:
```
dist/QuanLyB2B.exe
```

### 4. Cấu hình nâng cao

**Không hiển thị console:**
Sửa `QuanLyB2B.spec`:
```python
exe = EXE(
    ...
    console=False,  # Đổi từ True sang False
    ...
)
```

**Thêm icon:**
```python
exe = EXE(
    ...
    icon='icon.ico',  # Thêm đường dẫn icon
    ...
)
```

**One-file mode** (1 file .exe duy nhất):
```bash
pyinstaller --onefile --windowed --name="QuanLyB2B" main.py
```

## 🔍 So sánh với các phương pháp

| Tiêu chí | WebView | Native PySide6 (✅ Đang dùng) |
|----------|---------|-------------------------------|
| Performance | Chậm hơn (Chrome engine) | **Nhanh** (native) |
| Memory | Cao (100-200MB) | **Thấp** (30-50MB) |
| Bundle Size | Lớn (50-100MB) | **Nhỏ** (20-30MB) |
| UI Quality | Giống web 100% | **Giống 95%** với QSS |
| Offline | Cần JS framework | **100% offline** |
| Debug | Phức tạp (browser devtools) | **Dễ** (Python debugger) |
| Build | Phức tạp | **Đơn giản** (PyInstaller) |

## 🐛 Troubleshooting

### Lỗi: "Module not found"
```bash
pip install -r requirements.txt
```

### Lỗi: "Database locked"
Xóa file `data/b2b_management.db` và chạy lại.

### Lỗi: "Port already in use" (nếu dùng Flask)
Ứng dụng này **không dùng Flask**, chỉ dùng native PySide6.

### Giao diện không đẹp?
Kiểm tra file `src/ui/theme.py` đã được import trong `main.py`.

### Build .exe bị lỗi?
```bash
pip install --upgrade pyinstaller
pyinstaller QuanLyB2B.spec --clean
```

## 📝 API Services

### OrderService
```python
order_service.get_all(search, from_date, to_date)
order_service.get_by_id(order_id)
order_service.create(data, items)
order_service.update(order_id, data, items)
order_service.delete(order_id)
order_service.get_stats()
```

### DebtService
```python
debt_service.get_all(search, status)
debt_service.get_by_id(debt_id)
debt_service.add_payment(debt_id, payment_data)
debt_service.recalculate_debt(order_id)
debt_service.get_stats()
```

### CustomerService
```python
customer_service.get_all(search)
customer_service.get_by_id(customer_id)
customer_service.create(data)
customer_service.update(customer_id, data)
customer_service.get_stats()
```

### ProductService
```python
product_service.get_all(search, category_id)
product_service.get_by_id(product_id)
product_service.create(data)
product_service.update(product_id, data)
```

### ExcelService
```python
excel_service.import_orders_from_excel(file_path, order_service)
excel_service.export_order_to_excel(order, items, output_path)
```

## 🎓 Hướng dẫn mở rộng

### Thêm page mới

1. Tạo file `src/ui/pages/new_page.py`
2. Kế thừa `QWidget` và implement `init_ui()`
3. Thêm vào `native_main_window.py`:
```python
from src.ui.pages.new_page import NewPage

# Trong init_pages()
self.pages = {
    ...
    'new_page': NewPage(self.db),
}

# Trong nav_items
nav_items = [
    ...
    ('new_page', '🆕 Page mới', 'Mô tả'),
]
```

### Thêm API service mới

1. Tạo file `src/services/new_service.py`
2. Implement methods
3. Sử dụng trong pages

### Custom QSS styling

Sửa file `src/ui/theme.py`:
```python
THEME_QSS = """
    /* Thêm custom styles ở đây */
    QPushButton#myButton {
        background-color: #6366F1;
        ...
    }
"""
```

## 📞 Support

- Email: support@example.com
- GitHub: [repository-url]

## 📄 License

MIT License - Tự do sử dụng và chỉnh sửa

## 🙏 Credits

- **Design**: Vue.js + Tailwind CSS (từ Laravel project)
- **GUI Framework**: PySide6 (Qt for Python)
- **Database**: SQLite3 (built-in Python)
- **Excel**: openpyxl
- **Build Tool**: PyInstaller

---

**Made with ❤️ using Python + PySide6**
