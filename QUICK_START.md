# Quick Start: Automated Release Pipeline

Complete automation from source code to GitHub Releases.

## One-Time Setup

### 1. Create GitHub Personal Access Token

1. Go to: https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Token name: `Debt Manager Release`
4. Select scope: ✅ `repo` (all repo permissions)
5. Click "Generate token"
6. **Copy the token** (you won't see it again!)

### 2. Configure .env File

```bash
# Copy example file
copy .env.example .env

# Edit .env and paste your token
notepad .env
```

Fill in:
```
GITHUB_TOKEN=ghp_your_token_here
GITHUB_OWNER=Duytri9123
GITHUB_REPO=debt-manager-release
```

### 3. Install Dependencies

```bash
pip install requests
```

## Release Workflow

### Step 1: Build Everything

```bash
build_all.bat
```

**What it does:**
- ✅ Builds DebtManager.exe
- ✅ Builds updater.exe
- ✅ Creates DebtManager_Setup.exe (Inno Setup)
- ✅ Calculates SHA256 checksum
- ✅ Generates version.json automatically
- ✅ Copies all artifacts to Output/
- ✅ Opens Output folder

**Output:**
```
Output/
├── DebtManager.exe
├── updater.exe
├── DebtManager_Setup.exe
└── version.json
```

### Step 2: Test Installer (Recommended)

```bash
Output\DebtManager_Setup.exe
```

Install and verify the application works correctly.

### Step 3: Publish to GitHub Releases

```bash
publish_release.bat
```

**What it does:**
- ✅ Reads version from version.json
- ✅ Creates GitHub Release via API
- ✅ Uploads DebtManager_Setup.exe
- ✅ Uploads version.json
- ✅ Publishes release

**Result:**
```
✅ Release published successfully!

Release URL: https://github.com/Duytri9123/debt-manager-release/releases/tag/v1.0.0

Assets uploaded:
  - DebtManager_Setup.exe
  - version.json
```

## Complete Automation (Optional)

Create `release.bat` to do everything in one command:

```batch
@echo off
call build_all.bat
call publish_release.bat
```

Then just run:
```bash
release.bat
```

## Version Management

### Update Version Number

Before building, update the version in `src/core/version.py`:

```python
APP_VERSION = SemanticVersion("1.0.1")  # Update this
```

Also update `build_all.bat`:

```batch
set VERSION=1.0.1
```

### Version Numbering Rules

- **PATCH** (1.0.0 → 1.0.1): Bug fixes
- **MINOR** (1.0.0 → 1.1.0): New features
- **MAJOR** (1.0.0 → 2.0.0): Breaking changes

## Troubleshooting

### "GITHUB_TOKEN not found"
- Ensure .env file exists
- Check GITHUB_TOKEN is set correctly
- Token must have `repo` scope

### "Build failed"
- Check PyInstaller installed: `pip install pyinstaller`
- Check Inno Setup 6 installed
- Review build output for specific errors

### "Release already exists"
- Delete old release from GitHub
- Or upload assets manually to existing release

### "SHA256 mismatch"
- Regenerate by running build_all.bat again
- Don't modify Setup.exe after generation

## Manual Release (Alternative)

If you prefer manual upload:

1. Run `build_all.bat`
2. Go to: https://github.com/Duytri9123/debt-manager-release/releases/new
3. Create release with tag `v1.0.0`
4. Upload `Output/DebtManager_Setup.exe`
5. Upload `Output/version.json`
6. Publish

## Auto-Update Verification

After publishing:

1. Install previous version on test machine
2. Launch application
3. Wait 1-2 seconds (update check)
4. Verify update dialog appears
5. Click "Update Now"
6. Verify download and installation
7. Verify app restarts with new version
8. Verify user data preserved

## Security Notes

- ✅ Never commit .env file
- ✅ Never share GitHub token
- ✅ Token stored only in .env (gitignored)
- ✅ Source code stays in private repo
- ✅ Only compiled binaries in public repo

## Files Overview

| File | Purpose |
|------|---------|
| `build_all.bat` | Complete build pipeline |
| `publish_release.bat` | Publish to GitHub |
| `scripts/generate_version.py` | Generate version.json with SHA256 |
| `scripts/publish_release.py` | GitHub API client |
| `.env.example` | Template for configuration |
| `.env` | Your actual config (gitignored) |

## Summary

```
Source Code (Private Repo)
         ↓
  build_all.bat
         ↓
  Output/DebtManager_Setup.exe
  Output/version.json
         ↓
  publish_release.bat
         ↓
  GitHub Releases (Public Repo)
         ↓
  Users receive auto-update notification
         ↓
  One-click update with data preservation
```

---

**Debt Manager** © 2026 - All Rights Reserved
