# Release Deployment Guide

This document describes how to build and release new versions of Debt Manager.

## Repository Structure

- **Private Repository**: `debt-manager-source` (https://github.com/Duytri9123/debt-manager-source)
  - Contains all source code
  - Never made public
  
- **Public Repository**: `debt-manager-release` (https://github.com/Duytri9123/debt-manager-release)
  - Contains only GitHub Releases
  - Never contains source code
  - Used for distributing compiled installers

## Prerequisites

- Python 3.x installed
- PyInstaller: `pip install pyinstaller`
- Inno Setup 6: https://jrsoftware.org/isdl.php
- GitHub account with access to both repositories

## Build Process

### Step 1: Update Version Number

Edit `src/core/version.py`:

```python
APP_VERSION = SemanticVersion("1.0.0")  # Update this
```

### Step 2: Run Build Script

```bash
build_all.bat
```

This will:
1. Build `DebtManager.exe` (main application)
2. Build `updater.exe` (update handler)
3. Create `DebtManager_Setup.exe` (Inno Setup installer)
4. Generate `version.json` with SHA256 checksum

### Step 3: Verify Build Output

Check the `Output/` directory contains:
- `DebtManager.exe`
- `updater.exe`
- `DebtManager_Setup.exe`
- `version.json`

### Step 4: Test Installer Locally

1. Run `Output/DebtManager_Setup.exe`
2. Complete installation
3. Launch Debt Manager
4. Verify it works correctly
5. Check data is stored in `%LOCALAPPDATA%\DebtManager\`

## Manual Release to GitHub

### Step 1: Create New Release

Go to: https://github.com/Duytri9123/debt-manager-release/releases/new

### Step 2: Fill Release Information

**Tag version:** `v1.0.0` (match your version)

**Release title:** `Debt Manager v1.0.0`

**Description:** Add release notes describing what changed

### Step 3: Upload Assets

Upload these files from `Output/` directory:

1. `DebtManager_Setup.exe` - Windows installer
2. `version.json` - Update metadata

### Step 4: Publish Release

Click "Publish release"

## Auto Update Flow

When users have an older version installed:

1. Application starts
2. Downloads `version.json` from GitHub Releases
3. Compares current version with latest version
4. If newer version exists, shows update dialog
5. User clicks "Update Now"
6. Downloads `DebtManager_Setup.exe`
7. Verifies SHA256 checksum
8. Launches `updater.exe`
9. Main application closes
10. Installer runs silently
11. Application restarts with new version
12. All user data preserved

## version.json Structure

```json
{
  "version": "1.0.0",
  "minimum_supported_version": "1.0.0",
  "download_url": "https://github.com/Duytri9123/debt-manager-release/releases/latest/download/DebtManager_Setup.exe",
  "sha256": "CALCULATED_HASH",
  "mandatory": false,
  "release_date": "2026-06-12",
  "release_notes": [
    "Feature 1",
    "Feature 2",
    "Bug fix"
  ]
}
```

### Field Descriptions

- **version**: Current release version (semantic versioning)
- **minimum_supported_version**: Oldest version that can auto-update
- **download_url**: Direct download link to Setup.exe
- **sha256**: SHA256 checksum of Setup.exe (security verification)
- **mandatory**: If true, users must update (cannot skip)
- **release_date**: Release date (YYYY-MM-DD)
- **release_notes**: Array of strings describing changes

## Generate version.json Manually

If you need to regenerate version.json:

```bash
python scripts/generate_version.py ^
    --setup Output\DebtManager_Setup.exe ^
    --version 1.0.0 ^
    --min-version 1.0.0 ^
    --notes "Feature 1" "Feature 2" "Bug fix"
```

Or with PowerShell to get SHA256:

```powershell
Get-FileHash .\Output\DebtManager_Setup.exe -Algorithm SHA256
```

## Mandatory Updates

To force all users to update:

1. Set `"mandatory": true` in version.json
2. Application will not allow skipping the update
3. Useful for critical bug fixes or security patches

## Rollback Plan

If a release has issues:

1. Delete the GitHub Release
2. Upload previous version's Setup.exe and version.json
3. Users who haven't updated yet will not see the problematic version
4. Users who updated can reinstall from previous release

## Security Checklist

Before publishing:

- [ ] No source code in release
- [ ] No `.env` files or secrets
- [ ] No database files
- [ ] No user data
- [ ] No logs with sensitive information
- [ ] SHA256 checksum is correct
- [ ] Download URL is correct
- [ ] Version number follows semantic versioning
- [ ] Tested installer on clean Windows machine

## Data Safety

The installer is designed to:

- ✅ Install to `%LOCALAPPDATA%\DebtManager\`
- ✅ Never delete user data
- ✅ Preserve `app.db`, `config.json`, `license.json`
- ✅ Preserve `backup/`, `exports/`, `imports/`, `uploads/`, `logs/`
- ✅ Only replace application binaries
- ✅ Rollback automatically if installation fails

## Troubleshooting

### Build fails
- Ensure PyInstaller is installed: `pip install pyinstaller`
- Ensure Inno Setup 6 is installed
- Check `build_all.bat` output for errors

### SHA256 mismatch
- Regenerate version.json using the script
- Verify Setup.exe wasn't modified after generation

### Auto-update not working
- Check `version.json` is uploaded to GitHub Releases
- Verify download URL is correct
- Check Internet connectivity
- Check application logs in `%LOCALAPPDATA%\DebtManager\logs\`

## Version Numbering

Follow Semantic Versioning (SemVer):

- **MAJOR**: Incompatible API changes (2.0.0)
- **MINOR**: Backwards-compatible features (1.1.0)
- **PATCH**: Backwards-compatible bug fixes (1.0.1)

Examples:
- `1.0.0` → Initial release
- `1.0.1` → Bug fix
- `1.1.0` → New feature
- `2.0.0` → Major breaking change

## Support

For issues with the release process, contact the software provider.

---

**Debt Manager** © 2026 - All Rights Reserved
