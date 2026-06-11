# Setup & Build Guide - Debt Manager

## Quick Setup (First Time Only)

### Step 1: Install Python 3.x

If Python is not installed:

1. Download from: https://www.python.org/downloads/
2. Run installer
3. ✅ **CHECK** "Add Python to PATH"
4. Click "Install Now"
5. Verify: Open new terminal and run:
   ```bash
   python --version
   ```

### Step 2: Install Dependencies

```bash
cd "c:\My BACKEND\congnopython"
python -m pip install -r requirements.txt
```

This installs:
- PySide6 (GUI framework)
- openpyxl (Excel processing)
- PyInstaller (build .exe)
- requests (HTTP client)
- Pillow (image processing for icon)

### Step 3: Create Icon (Optional)

```bash
python create_icon.py
```

This creates `installer/icon.ico`

Or use any .ico file you prefer.

### Step 4: Build Application

```bash
build_all.bat
```

This will:
1. Build DebtManager.exe
2. Build updater.exe
3. Create DebtManager_Setup.exe (installer)
4. Generate version.json with SHA256
5. Open Output/ folder

### Step 5: Test

```bash
Output\DebtManager_Setup.exe
```

---

## Troubleshooting

### "Python was not found"

**Problem:** Python not installed or not in PATH

**Solution:**
1. Install Python from https://www.python.org/downloads/
2. During installation, CHECK "Add Python to PATH"
3. Open a NEW terminal window
4. Try: `python --version`

### "pyinstaller is not recognized"

**Problem:** Dependencies not installed

**Solution:**
```bash
python -m pip install -r requirements.txt
```

### "ModuleNotFoundError: PySide6"

**Problem:** PySide6 not installed

**Solution:**
```bash
python -m pip install PySide6
```

### Build fails with missing imports

**Solution:** Ensure all dependencies are installed:
```bash
python -m pip install --upgrade -r requirements.txt
```

---

## Build Commands

### Full Build (Recommended)
```bash
build_all.bat
```

### Build Only Main App
```bash
pyinstaller QuanLyB2B.spec --clean
```

### Build Only Updater
```bash
pyinstaller updater.spec --clean
```

### Build Installer Only (Inno Setup required)
```
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer\setup.iss
```

---

## Publish to GitHub Releases

### One Command
```bash
release.bat
```

### Step by Step
```bash
# 1. Build
build_all.bat

# 2. Publish
publish_release.bat
```

### Manual Upload
1. Go to: https://github.com/Duytri9123/debt-manager-release/releases/new
2. Create tag: `v1.0.0`
3. Upload from Output/ folder:
   - DebtManager_Setup.exe
   - version.json
4. Click "Publish release"

---

## Project Structure

```
congnopython/
├── main.py                    # Entry point
├── updater.py                 # Update handler
├── requirements.txt           # Python dependencies
├── QuanLyB2B.spec            # PyInstaller config (main app)
├── updater.spec              # PyInstaller config (updater)
├── build_all.bat             # Full build script
├── release.bat               # Build + publish script
├── publish_release.bat       # GitHub release script
│
├── installer/
│   ├── setup.iss             # Inno Setup script
│   └── icon.ico              # Application icon
│
├── scripts/
│   ├── generate_version.py   # Generate version.json
│   └── publish_release.py    # GitHub API client
│
├── src/
│   ├── core/                 # Core modules
│   ├── services/             # Business logic
│   ├── ui/                   # User interface
│   └── update/               # Update system
│
└── Output/                   # Build output (gitignored)
    ├── DebtManager.exe
    ├── updater.exe
    ├── DebtManager_Setup.exe
    └── version.json
```

---

## Environment Setup

### Create .env file (for GitHub publishing)

```bash
copy .env.example .env
notepad .env
```

Fill in:
```
GITHUB_TOKEN=your_token_here
GITHUB_OWNER=Duytri9123
GITHUB_REPO=debt-manager-release
```

Get token at: https://github.com/settings/tokens

---

## Next Steps

1. ✅ Install Python 3.x
2. ✅ Run: `python -m pip install -r requirements.txt`
3. ✅ Run: `build_all.bat`
4. ✅ Test installer
5. ✅ Publish to GitHub Releases

---

**Need help?** Check RELEASE_GUIDE.md and QUICK_START.md
