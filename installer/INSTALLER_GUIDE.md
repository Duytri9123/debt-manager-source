# 📦 Inno Setup Installer Guide

## Overview

Professional Windows installer for B2B Management application with:
- ✅ Installation to Program Files
- ✅ Desktop & Start Menu shortcuts
- ✅ User data protection in AppData
- ✅ Silent install support
- ✅ Auto-update ready
- ✅ Rollback protection

---

## 📋 Prerequisites

### 1. Install Inno Setup 6

Download from: https://jrsoftware.org/isdl.php

Choose: **Inno Setup 6.x.x** (Unicode version)

### 2. Build Executables First

Run one of these before building installer:
```bash
# Build everything (recommended)
build_all.bat

# Or build separately
build.bat          # Builds QuanLyB2B.exe
build_updater.bat  # Builds Updater.exe
build_installer.bat  # Builds installer
```

---

## 🚀 Building the Installer

### Option 1: One-Click Build (Recommended)
```bash
build_all.bat
```
This will:
1. Build QuanLyB2B.exe
2. Build Updater.exe
3. Create MyApp_Setup.exe
4. Calculate SHA256
5. Update version.json

### Option 2: Build Installer Only
```bash
# After executables are ready
build_installer.bat
```

### Option 3: Manual Build
1. Open `installer\setup.iss` in Inno Setup Compiler
2. Click **Build** → **Compile** (or press F9)
3. Wait for compilation
4. Find installer in `Output\MyApp_Setup.exe`

---

## 📦 Installer Output

```
Output/
└── MyApp_Setup.exe    (~50-80 MB depending on bundling)
```

---

## 💻 Installation

### Normal Installation (GUI)
```bash
Output\MyApp_Setup.exe
```

User will see:
1. Welcome screen
2. License agreement
3. Installation folder (default: `C:\Program Files\Quản lý B2B`)
4. Additional tasks:
   - ☐ Create desktop shortcut
5. Ready to install
6. Installation progress
7. Finish (optionally launch app)

### Silent Installation
```bash
Output\MyApp_Setup.exe /VERYSILENT /NORESTART
```

**Flags:**
- `/VERYSILENT` - No UI, no prompts
- `/NORESTART` - Never restart computer
- `/DIR="C:\Custom\Path"` - Custom installation directory
- `/TASKS="desktopicon"` - Force create desktop shortcut

**Example with all options:**
```bash
MyApp_Setup.exe /VERYSILENT /NORESTART /TASKS="desktopicon" /DIR="D:\Apps\B2B"
```

### Administrative Installation (GPO/SCCM)
```bash
MyApp_Setup.exe /VERYSILENT /NORESTART /LOG="install.log"
```

---

## 📁 Installation Structure

### Program Files (Application Binaries)
```
C:\Program Files\Quản lý B2B\
├── QuanLyB2B.exe          # Main application
├── Updater.exe            # Auto-update process
└── _internal/             # Python runtime (if bundled)
    ├── Python libraries
    └── Resources
```

### AppData/Local (User Data - NEVER OVERWRITTEN)
```
C:\Users\[User]\AppData\Local\B2BManagement\
├── data\
│   └── app.db             # SQLite database
├── config.json            # User preferences
├── license.json           # License information
├── backup/                # Database backups
├── exports/               # Exported files
├── imports/               # Imported files
├── uploads/               # Uploaded files
├── logs/                  # Application logs
└── updates/               # Downloaded updates
```

---

## 🛡️ Data Protection

### What is NEVER Overwritten:

| File/Directory | Purpose | Protection |
|----------------|---------|------------|
| `app.db` | User database | ✅ Never deleted |
| `config.json` | User settings | ✅ Never deleted |
| `license.json` | License data | ✅ Never deleted |
| `backup/` | Database backups | ✅ Never deleted |
| `exports/` | User exports | ✅ Never deleted |
| `imports/` | User imports | ✅ Never deleted |
| `uploads/` | User uploads | ✅ Never deleted |
| `logs/` | Application logs | ✅ Never deleted |

### How It Works:

1. **Inno Setup installs to Program Files only**
2. **User data lives in AppData/Local**
3. **Installer never touches AppData**
4. **Update process preserves AppData**

### Update Flow:

```
Old Version Installed
    ↓
User downloads MyApp_Setup.exe (new version)
    ↓
Run installer (normal or silent)
    ↓
Installer replaces:
  ✓ QuanLyB2B.exe
  ✓ Updater.exe
  ✓ _internal/ (Python libs)
    ↓
Installer DOES NOT touch:
  ✗ AppData/Local/B2BManagement/
    ↓
User data preserved ✅
Application updated ✅
```

---

## 🔄 Uninstallation

### Normal Uninstall
1. **Start Menu** → "Quản lý B2B" → "Uninstall"
2. **Settings** → Apps → "Quản lý B2B" → Uninstall
3. **Control Panel** → Programs → Uninstall

### Silent Uninstall
```bash
"C:\Program Files\Quản lý B2B\unins000.exe" /VERYSILENT /NORESTART
```

### What Happens on Uninstall:

**Default Behavior:**
- ✅ Removes Program Files installation
- ✅ Removes shortcuts
- ✅ Removes registry entries
- ❌ **KEEPS** AppData/Local/B2BManagement/

**User is prompted:**
```
Do you want to delete all user data?

WARNING: This cannot be undone!
- Database (app.db)
- Configuration (config.json)
- License (license.json)
- All exports, imports, uploads, logs

[Yes] [No]
```

**If user clicks Yes:**
- Deletes entire AppData/Local/B2BManagement/
- All data lost permanently

**If user clicks No (default):**
- AppData preserved
- Can reinstall later without data loss

---

## 🔧 Customization

### Change Application Name

Edit `installer\setup.iss`:
```ini
#define MyAppName "Your App Name"
```

### Change Version

```ini
#define MyAppVersion "1.2.0"
```

### Add Custom Icon

1. Create `installer\icon.ico` (256x256 recommended)
2. Already configured in setup.iss

### Change Wizard Images

```ini
WizardImageFile=installer\wizard-large.bmp     # 164x314 pixels
WizardSmallImageFile=installer\wizard-small.bmp # 55x55 pixels
```

### Add License Agreement

```ini
[Setup]
LicenseFile=installer\license.txt

[Files]
Source: "installer\license.txt"; DestDir: "{app}"
```

### Add Additional Languages

```ini
[Languages]
Name: "en"; MessagesFile: "compiler:Default.isl"
Name: "vi"; MessagesFile: "compiler:Languages\Vietnamese.isl"
Name: "fr"; MessagesFile: "compiler:Languages\French.isl"
```

---

## 🎯 Auto-Update Integration

### How It Works:

1. **version.json** (in GitHub repo):
```json
{
  "version": "1.2.0",
  "download_url": "https://github.com/.../MyApp_Setup.exe",
  "sha256": "ABC123...",
  "mandatory": false
}
```

2. **Application checks for updates** on startup (if online)

3. **User clicks "Update Now"**

4. **Downloads MyApp_Setup.exe** to AppData/Local/B2BManagement/updates/

5. **Verifies SHA256** checksum

6. **Launches Updater.exe**:
```bash
Updater.exe "C:\Users\...\updates\MyApp_Setup.exe" "C:\Program Files\...\QuanLyB2B.exe"
```

7. **Updater.exe:**
   - Closes main application
   - Runs installer silently: `MyApp_Setup.exe /VERYSILENT`
   - Restarts application

8. **Installer:**
   - Replaces binaries in Program Files
   - Preserves AppData (user data)
   - Completes silently

### SHA256 Calculation

**Automatic (using build_all.bat):**
```bash
build_all.bat
# SHA256 automatically calculated and version.json updated
```

**Manual:**
```bash
certutil -hashfile Output\MyApp_Setup.exe SHA256
```

Copy the hash (remove spaces) and update `installer\version.json`:
```json
{
  "sha256": "YOUR_HASH_HERE"
}
```

---

## 🧪 Testing the Installer

### Test 1: Clean Installation
```bash
# On clean machine
Output\MyApp_Setup.exe

# Verify:
# 1. App installs to C:\Program Files\Quản lý B2B\
# 2. Desktop shortcut created (if selected)
# 3. Start Menu folder created
# 4. Application launches
```

### Test 2: Silent Installation
```bash
Output\MyApp_Setup.exe /VERYSILENT /NORESTART

# Verify:
# 1. No UI shown
# 2. App installed correctly
# 3. Shortcuts created
```

### Test 3: Update Installation
```bash
# 1. Install v1.0.0
Output\MyApp_Setup.exe

# 2. Create test data
# Open app, add some records, create exports

# 3. Install v1.1.0 (update)
Output\MyApp_Setup.exe

# Verify:
# 1. Application updated
# 2. User data preserved in AppData
# 3. No data loss
```

### Test 4: Uninstallation
```bash
# Uninstall normally
"C:\Program Files\Quản lý B2B\unins000.exe"

# Verify:
# 1. Program Files folder removed
# 2. Shortcuts removed
# 3. AppData folder PRESERVED
```

### Test 5: Custom Directory
```bash
Output\MyApp_Setup.exe /DIR="D:\Custom\B2B"

# Verify:
# 1. Installs to D:\Custom\B2B\
# 2. Works correctly
```

---

## 🐛 Troubleshooting

### Issue: "Inno Setup not found"
**Solution:**
1. Install Inno Setup 6 from https://jrsoftware.org/isdl.php
2. Make sure it's in `C:\Program Files (x86)\Inno Setup 6\`
3. Or update path in build script

### Issue: "Installer too large"
**Solutions:**
1. Use `--onedir` instead of `--onefile` in PyInstaller
2. Exclude unnecessary modules
3. Use UPX compression

### Issue: "User data lost after update"
**Cause:** User manually deleted AppData or installer bug
**Solution:** Check installer logs, verify AppData path

### Issue: "Silent install fails"
**Check:**
1. Run with `/LOG="install.log"`
2. Check log file for errors
3. Verify admin privileges

### Issue: "SHA256 mismatch"
**Cause:** File corrupted or version.json not updated
**Solution:**
```bash
# Recalculate SHA256
certutil -hashfile Output\MyApp_Setup.exe SHA256

# Update version.json
# Commit to GitHub
```

---

## 📊 Build Comparison

| Method | Time | Effort | Recommended |
|--------|------|--------|-------------|
| `build_all.bat` | 5-10 min | One click | ✅ Yes |
| Manual steps | 15-20 min | Multiple steps | ❌ No |

---

## 🎯 Deployment Workflow

### Developer Workflow:

```
1. Make code changes
2. Update version in src/core/version.py
   APP_VERSION = SemanticVersion("1.2.0")
3. Run: build_all.bat
4. Test: Output\MyApp_Setup.exe
5. Commit version.json to GitHub
6. Create GitHub Release:
   - Tag: v1.2.0
   - Upload: Output\MyApp_Setup.exe
   - Publish
7. Users receive update notification
```

### User Workflow:

```
1. User opens application
2. App checks for updates (background)
3. If update available → Show dialog
4. User clicks "Update Now"
5. Downloads MyApp_Setup.exe
6. Verifies SHA256
7. Installs silently
8. App restarts with new version
9. User data preserved ✅
```

---

## 📝 Checklist

### Before Release:
- [ ] Update version in `src/core/version.py`
- [ ] Update `installer/version.json`
- [ ] Run `build_all.bat`
- [ ] Test installer (clean install)
- [ ] Test installer (update install)
- [ ] Test silent install
- [ ] Test uninstall
- [ ] Verify SHA256 matches version.json
- [ ] Commit version.json to GitHub
- [ ] Create GitHub Release
- [ ] Upload MyApp_Setup.exe

### After Release:
- [ ] Test update from previous version
- [ ] Verify update works silently
- [ ] Check user data preserved
- [ ] Monitor for crash reports

---

## 📚 Resources

- [Inno Setup Documentation](https://jrsoftware.org/isshelp/)
- [Inno Setup Examples](https://jrsoftware.org/is3examples.php)
- [Silent Install Guide](https://silentinstallhq.com/)
- [PyInstaller Documentation](https://pyinstaller.org/)

---

## ✅ Summary

**What You Have:**
- ✅ Professional installer script (setup.iss)
- ✅ Automated build scripts (build_all.bat, build_installer.bat)
- ✅ Data protection (AppData never overwritten)
- ✅ Silent install support (/VERYSILENT)
- ✅ Auto-update integration ready
- ✅ Rollback protection
- ✅ Complete documentation

**Next Steps:**
1. Install Inno Setup 6
2. Run `build_all.bat`
3. Test installer
4. Deploy to GitHub Releases
5. Test auto-update flow

**Ready to deploy!** 🚀
