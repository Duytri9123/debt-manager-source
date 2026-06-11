# Hướng Dẫn Cài Đặt & Build - Debt Manager

## ⚠️ Vấn Đề Hiện Tại

Python **chưa được cài đặt** trên máy tính của bạn.

---

## ✅ Giải Pháp - 3 Bước Đơn Giản

### Bước 1: Cài Đặt Python (2 phút)

**Cách 1 - Tải trực tiếp (Nhanh nhất):**

1. Click vào link này:
   ```
   https://www.python.org/ftp/python/3.12.0/python-3.12.0-amd64.exe
   ```

2. Chạy file vừa tải về

3. ⚠️ **QUAN TRỌNG:** Tích vào ô **"Add Python to PATH"**

   ![Add Python to PATH checkbox](https://i.imgur.com/example.png)

4. Click **"Install Now"**

5. Đợi 1-2 phút

**Cách 2 - Tải từ trang chủ:**

1. Vào: https://www.python.org/downloads/
2. Click nút vàng "Download Python 3.x.x"
3. Làm theo bước 3-5 ở trên

---

### Bước 2: Kiểm Tra Python (30 giây)

1. Mở **terminal MỚI** (quan trọng!)

2. Chạy lệnh:
   ```bash
   python --version
   ```

3. Nếu hiện ra `Python 3.12.0` (hoặc tương tự) → ✅ Thành công!

4. Nếu vẫn báo lỗi → Đóng tất cả terminal và mở lại

---

### Bước 3: Build Ứng Dụng (5-10 phút)

1. Mở terminal tại thư mục project:
   ```bash
   cd "c:\My BACKEND\congnopython"
   ```

2. Cài đặt dependencies:
   ```bash
   python -m pip install -r requirements.txt
   ```
   ⏱️ Mất khoảng 3-5 phút

3. Build ứng dụng:
   ```bash
   build_all.bat
   ```
   ⏱️ Mất khoảng 5-10 phút

4. ✅ Hoàn thành! Folder `Output/` sẽ tự động mở

---

## 🎯 Kết Quả Mong Đợi

Sau khi build thành công, bạn sẽ thấy:

```
Output/
├── DebtManager.exe          (50-80 MB)
├── updater.exe              (10-15 MB)  
├── DebtManager_Setup.exe    (40-60 MB) ← File cài đặt
└── version.json             (500 bytes)
```

---

## 🚀 Test Ứng Dụng

### Test Installer:

1. Chạy:
   ```
   Output\DebtManager_Setup.exe
   ```

2. Làm theo hướng dẫn cài đặt

3. Sau khi cài xong, app sẽ tự mở

### Kiểm Tra:

- ✅ App mở được không có lỗi
- ✅ Có shortcut trên Desktop
- ✅ Có trong Start Menu
- ✅ Dữ liệu lưu tại: `%LOCALAPPDATA%\DebtManager\`

---

## 📦 Publish Lên GitHub (Tùy Chọn)

Nếu muốn chia sẻ với người dùng:

```bash
release.bat
```

Sẽ tự động:
1. Build mọi thứ
2. Tạo GitHub Release
3. Upload Setup.exe
4. Upload version.json

---

## ❌ Xử Lý Lỗi

### Lỗi: "python is not recognized"

**Nguyên nhân:** Python chưa được cài hoặc chưa thêm vào PATH

**Giải pháp:**
1. Cài lại Python
2. **BẮT BUỘC** tick vào "Add Python to PATH"
3. Mở terminal MỚI
4. Thử lại: `python --version`

---

### Lỗi: "pyinstaller is not recognized"

**Nguyên nhân:** Chưa cài dependencies

**Giải pháp:**
```bash
python -m pip install -r requirements.txt
```

---

### Lỗi: "ModuleNotFoundError: PySide6"

**Giải pháp:**
```bash
python -m pip install PySide6
```

---

### Build bị lỗi giữa chừng

**Giải pháp:**
1. Xóa folder `build/` và `dist/`
2. Chạy lại:
   ```bash
   build_all.bat
   ```

---

## 📋 Checklist Sau Khi Build

- [ ] Python đã cài đặt ✓
- [ ] Dependencies đã cài ✓  
- [ ] `build_all.bat` chạy thành công ✓
- [ ] Folder `Output/` có 4 files ✓
- [ ] `DebtManager_Setup.exe` cài được ✓
- [ ] App mở lên bình thường ✓
- [ ] Không có lỗi trong console ✓

---

## 🎓 Tài Liệu Tham Khảo

- **SETUP_GUIDE.md** - Hướng dẫn chi tiết
- **RELEASE_GUIDE.md** - Quy trình release
- **QUICK_START.md** - Bắt đầu nhanh
- **ACTION_REQUIRED.md** - Những việc cần làm

---

## 💡 Mẹo

### Build nhanh (sau lần đầu):
```bash
build_all.bat
```

### Build + Publish:
```bash
release.bat
```

### Chỉ build, không publish:
```bash
build_all.bat
```

---

## 🆘 Cần Trợ Giúp?

Nếu gặp lỗi không xử lý được:

1. Chụp màn hình lỗi
2. Kiểm tra các file log trong `Output/`
3. Xem lại hướng dẫn trên

---

**Chúc bạn thành!** 🎉

Sau khi cài Python xong, chỉ cần chạy `build_all.bat` là mọi thứ tự động!
