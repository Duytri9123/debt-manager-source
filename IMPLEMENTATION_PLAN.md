# Professional Windows Desktop Application - Implementation Plan

## Context

The user has an existing B2B Management desktop application built with PySide6, SQLite, and PyInstaller. The codebase has a solid foundation with basic UI, database layer, services, and partial update system infrastructure. The goal is to transform this into a production-ready application with complete auto-update system, dark mode, background workers, modern UI, and professional deployment workflow.

## Implementation Phases

### Phase 1: Core Infrastructure Enhancement

**Objective**: Complete foundational components for internet detection, checksums, and enhanced update models.

#### Files to Create/Modify:

1. **`src/core/internet.py`** (NEW)
   - Internet connectivity detection
   - Methods: `is_online()`, `check_connection(url)`
   
2. **`src/update/checksum.py`** (NEW)
   - SHA256 file verification
   - Methods: `calculate_sha256(file_path)`, `verify_sha256(file_path, expected_hash)`

3. **`src/update/models.py`** (ENHANCE)
   - Add validation methods
   - Add JSON schema validation
   - Add update status enum

#### Key Implementation:
```python
# src/core/internet.py
import socket
import requests

def is_online(timeout=3):
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=timeout)
        return True
    except OSError:
        pass
    try:
        requests.get("https://github.com", timeout=timeout)
        return True
    except requests.RequestException:
        return False
```

### Phase 2: Update System Core

**Objective**: Build complete update checking, downloading, and verification logic.

#### Files to Create:

1. **`src/update/github.py`** (NEW)
   - GitHub release API client
   - Methods: `fetch_version_info(repo_url, token)`, `get_latest_release()`
   - Parse GitHub releases API response
   - Handle authentication for private repos

2. **`src/update/checker.py`** (NEW)
   - Update checking orchestration
   - Methods: `check_for_update()`, `should_skip_version()`
   - Integration with settings for skipped versions
   - Internet connectivity check before checking updates

3. **`src/update/downloader.py`** (NEW)
   - File download with progress tracking
   - Methods: `download_file(url, destination, progress_callback)`
   - Resume capability
   - Speed calculation
   - ETA estimation

4. **`src/update/rollback.py`** (NEW)
   - Rollback mechanism
   - Methods: `create_backup()`, `restore_backup()`, `cleanup_backup()`
   - Preserve user data during rollback

#### Key Implementation:
```python
# src/update/downloader.py
import requests
import time
from pathlib import Path

class FileDownloader:
    def __init__(self, url, destination):
        self.url = url
        self.destination = destination
        self.downloaded = 0
        self.total = 0
        self.start_time = None
        
    def download(self, progress_callback=None):
        self.start_time = time.time()
        response = requests.get(self.url, stream=True)
        self.total = int(response.headers.get('content-length', 0))
        
        with open(self.destination, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    self.downloaded += len(chunk)
                    if progress_callback:
                        speed = self.downloaded / (time.time() - self.start_time)
                        progress_callback(self.downloaded, self.total, speed)
```

### Phase 3: Background Workers

**Objective**: Move Excel operations to background threads for responsive UI.

#### Files to Create:

1. **`src/workers/__init__.py`** (NEW)

2. **`src/workers/excel_worker.py`** (NEW)
   - QThread for Excel import/export
   - Signals: `progress`, `finished`, `error`
   - Methods: `import_excel()`, `export_excel()`

3. **`src/workers/download_worker.py`** (NEW)
   - QThread for update downloads
   - Signals: `progress`, `speed`, `finished`, `error`
   - Integration with downloader.py

4. **`src/workers/update_worker.py`** (NEW)
   - QThread for complete update process
   - Orchestrate: check → download → verify → install

#### Key Implementation:
```python
# src/workers/excel_worker.py
from PySide6.QtCore import QThread, Signal

class ExcelImportWorker(QThread):
    progress = Signal(int, str)  # percentage, message
    finished = Signal(object)    # result data
    error = Signal(str)          # error message
    
    def __init__(self, file_path, service):
        super().__init__()
        self.file_path = file_path
        self.service = service
        
    def run(self):
        try:
            # Excel import logic here
            result = self.service.import_from_excel(self.file_path)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))
```

### Phase 4: UI Enhancement - Dark Mode

**Objective**: Add dark mode theme and dynamic switching.

#### Files to Modify/Create:

1. **`src/ui/theme.py`** (ENHANCE)
   - Add `DARK_THEME_QSS` dictionary
   - Add `get_theme(theme_name)` method
   - Add theme switching function

2. **`src/ui/theme_manager.py`** (NEW)
   - Theme manager singleton
   - Methods: `apply_theme()`, `toggle_theme()`, `get_current_theme()`
   - Persist theme choice in settings

#### Key Implementation:
```python
# Add to src/ui/theme.py
DARK_THEME_QSS = """
QWidget {
    background-color: #0F172A;
    color: #E2E8F0;
}

QFrame#sidebar {
    background-color: #020617;
    border-right: 1px solid #1E293B;
}

QTableWidget {
    background-color: #1E293B;
    border: 1px solid #334155;
    gridline-color: #334155;
}
...
"""

def apply_theme(app, theme='light'):
    if theme == 'dark':
        app.setStyleSheet(DARK_THEME_QSS)
    else:
        app.setStyleSheet(THEME_QSS)
```

### Phase 5: Modern Dialogs

**Objective**: Create beautiful, modern dialogs for updates and CRUD operations.

#### Files to Create:

1. **`src/ui/dialogs/__init__.py`** (NEW)

2. **`src/ui/dialogs/update_dialog.py`** (NEW)
   - Modern update prompt dialog
   - Show: current version, latest version, release notes
   - Buttons: [Update Now] [Remind Later] [Skip Version]
   - Animated, modern design

3. **`src/ui/dialogs/download_dialog.py`** (NEW)
   - Download progress dialog
   - Progress bar with percentage
   - Download speed display
   - ETA display
   - Cancel button

4. **`src/ui/dialogs/crud_dialogs.py`** (NEW)
   - Base dialog class with modern styling
   - Form validation
   - Success/error states
   - Animated transitions

#### Key Implementation:
```python
# src/ui/dialogs/update_dialog.py
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt

class UpdateDialog(QDialog):
    def __init__(self, current_version, latest_version, release_notes, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Update Available")
        self.setModal(True)
        self.setup_ui(current_version, latest_version, release_notes)
        
    def setup_ui(self, current, latest, notes):
        layout = QVBoxLayout(self)
        
        # Version info
        layout.addWidget(QLabel(f"Current: {current}"))
        layout.addWidget(QLabel(f"Latest: {latest}"))
        
        # Release notes
        notes_label = QLabel("\n".join([f"• {note}" for note in notes]))
        layout.addWidget(notes_label)
        
        # Buttons
        btn_layout = QHBoxLayout()
        self.update_btn = QPushButton("Update Now")
        self.later_btn = QPushButton("Remind Me Later")
        self.skip_btn = QPushButton("Skip This Version")
        
        btn_layout.addWidget(self.update_btn)
        btn_layout.addWidget(self.later_btn)
        btn_layout.addWidget(self.skip_btn)
        layout.addLayout(btn_layout)
        
        self.update_btn.clicked.connect(self.accept)
        self.later_btn.clicked.connect(self.reject)
        self.skip_btn.clicked.connect(lambda: self.done(2))
```

### Phase 6: Updater Executable

**Objective**: Create separate updater.exe that handles installation safely.

#### Files to Create/Modify:

1. **`updater.py`** (REWRITE COMPLETELY)
   - Standalone executable
   - Close main application
   - Run Inno Setup installer silently
   - Wait for installation to complete
   - Verify installation success
   - Restart main application
   - Rollback on failure

2. **`updater.spec`** (NEW)
   - PyInstaller spec for updater.exe
   - Minimal dependencies
   - Console mode for debugging

3. **`build_updater.bat`** (NEW)
   - Build script for updater.exe

#### Key Implementation:
```python
# updater.py - Critical flow
import sys
import subprocess
import time
import os
from pathlib import Path

def main():
    # Get arguments
    main_exe_path = sys.argv[1]
    installer_path = sys.argv[2]
    rollback_path = sys.argv[3]
    
    # Step 1: Close main application
    subprocess.run(['taskkill', '/F', '/IM', Path(main_exe_path).name], 
                   capture_output=True)
    time.sleep(2)
    
    # Step 2: Create backup
    create_backup(main_exe_path, rollback_path)
    
    # Step 3: Run installer
    result = subprocess.run([installer_path, '/VERYSILENT', '/NORESTART'],
                          capture_output=True)
    
    # Step 4: Verify installation
    if result.returncode == 0 and os.path.exists(main_exe_path):
        # Success - restart application
        subprocess.Popen([main_exe_path])
    else:
        # Failure - rollback
        restore_backup(rollback_path, main_exe_path)
        subprocess.Popen([main_exe_path])
```

### Phase 7: Settings Page & UI Integration

**Objective**: Add settings page and integrate all new features into the UI.

#### Files to Create/Modify:

1. **`src/ui/pages/settings_page.py`** (NEW)
   - Theme toggle (light/dark)
   - Update check toggle
   - Version display
   - Check for updates button
   - Application info

2. **`src/ui/native_main_window.py`** (ENHANCE)
   - Add Settings to navigation
   - Add update check on startup
   - Add update button in top bar
   - Smooth page transitions with QPropertyAnimation

3. **`main.py`** (ENHANCE)
   - Initialize update system
   - Check for updates on startup (async)
   - Show update dialog if available

#### Key Implementation:
```python
# In main.py - startup update check
from src.update.checker import UpdateChecker
from src.ui.dialogs.update_dialog import UpdateDialog

def check_updates_async(db, settings):
    """Non-blocking update check"""
    if not settings.get('app.check_updates_on_startup', True):
        return
    
    checker = UpdateChecker(settings)
    result = checker.check_for_update()
    
    if result.update_available:
        dialog = UpdateDialog(
            result.current_version_str,
            result.latest_version_str,
            result.version_info.release_notes
        )
        result_code = dialog.exec()
        
        if result_code == QDialog.Accepted:
            # User clicked Update Now
            start_update_process(result.version_info)
        elif result_code == 2:
            # User clicked Skip Version
            settings.skipped_version = result.latest_version_str
```

### Phase 8: Build & Deployment System

**Objective**: Create complete build and deployment workflow.

#### Files to Create:

1. **`scripts/generate_version.py`** (NEW)
   - Generate version.json for GitHub releases
   - Calculate SHA256 of Setup.exe
   - Update version in source code

2. **`scripts/build_all.bat`** (ENHANCE)
   - Build main app
   - Build updater
   - Run Inno Setup
   - Generate version.json

3. **`installer/setup.iss`** (ENHANCE)
   - Preserve user data during installation
   - Only replace application binaries
   - Install to %LOCALAPPDATA%\\B2BManagement
   - Create uninstaller

4. **`.github/workflows/release.yml`** (NEW - Optional)
   - GitHub Actions for automated releases
   - Build on tag creation
   - Upload to GitHub Releases
   - Generate version.json

#### Key Implementation:
```python
# scripts/generate_version.py
import json
import hashlib
from pathlib import Path

def generate_version_json(setup_exe_path, version, download_url, release_notes):
    # Calculate SHA256
    sha256 = hashlib.sha256()
    with open(setup_exe_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            sha256.update(chunk)
    
    version_info = {
        'version': version,
        'minimum_supported_version': '1.0.0',
        'download_url': download_url,
        'sha256': sha256.hexdigest(),
        'mandatory': False,
        'release_notes': release_notes
    }
    
    with open('version.json', 'w') as f:
        json.dump(version_info, f, indent=2)
    
    return version_info
```

### Phase 9: Testing & Polish

**Objective**: Comprehensive testing and UI/UX polish.

#### Testing Checklist:

1. **Update System Testing**
   - [ ] Online update check works
   - [ ] Offline skips update gracefully
   - [ ] Update dialog displays correctly
   - [ ] Download with progress works
   - [ ] SHA256 verification works
   - [ ] Updater closes main app
   - [ ] Installer runs silently
   - [ ] App restarts after update
   - [ ] Rollback works on failure
   - [ ] User data preserved after update

2. **UI Testing**
   - [ ] Light mode displays correctly
   - [ ] Dark mode displays correctly
   - [ ] Theme switching works without restart
   - [ ] All dialogs are modal and styled
   - [ ] Page transitions are smooth
   - [ ] Tables are responsive
   - [ ] Forms validate input

3. **Background Workers Testing**
   - [ ] Excel import doesn't block UI
   - [ ] Progress updates show correctly
   - [ ] Error handling works
   - [ ] Cancel works during long operations

4. **Data Safety Testing**
   - [ ] app.db never deleted during update
   - [ ] config.json preserved
   - [ ] All user folders preserved
   - [ ] Rollback restores working state

## Integration Points

### With Existing Code:

1. **`main.py`**: Add update check on startup, initialize theme manager
2. **`src/ui/native_main_window.py`**: Add settings page, update button, smooth transitions
3. **`src/ui/theme.py`**: Add dark mode QSS
4. **`src/core/settings.py`**: Already has theme and update settings - perfect
5. **`src/core/paths.py`**: Already has all required paths - perfect
6. **`src/core/version.py`**: Already has semantic versioning - perfect
7. **`src/update/models.py`**: Enhance with validation
8. **`src/services/excel_service.py`**: Integrate with workers

## Verification Strategy

### After Each Phase:

1. **Phase 1**: Test internet detection, checksum calculation
2. **Phase 2**: Test update checking with mock GitHub API, test download with progress
3. **Phase 3**: Test Excel import with large files, verify UI stays responsive
4. **Phase 4**: Test theme switching, verify all UI elements styled in both modes
5. **Phase 5**: Test all dialogs, verify modern appearance
6. **Phase 6**: Test updater.exe with mock installer, test rollback
7. **Phase 7**: Test settings page, test startup update check
8. **Phase 8**: Build complete Setup.exe, test end-to-end update flow
9. **Phase 9**: Comprehensive testing, fix bugs, polish UI

### End-to-End Testing:

1. Build Setup.exe with Inno Setup
2. Install on clean Windows machine
3. Verify app launches and creates data in AppData/Local/B2BManagement/
4. Verify offline mode works (disable internet)
5. Enable internet, verify update check works
6. Create test version.json with newer version
7. Verify update dialog appears
8. Click "Update Now"
9. Verify download with progress
10. Verify SHA256 check
11. Verify updater.exe launches
12. Verify main app closes
13. Verify installer runs
14. Verify app restarts with new version
15. Verify all user data intact
16. Simulate failed installation, verify rollback works

## Build & Deployment Workflow

### For Developers:

```bash
# 1. Update version in src/core/version.py
APP_VERSION = SemanticVersion("1.1.0")

# 2. Build everything
build_all.bat

# 3. Test Setup.exe locally
dist\\MyApp_Setup.exe

# 4. Generate version.json
python scripts/generate_version.py --version 1.1.0 --release-notes "..."

# 5. Upload to GitHub Releases
# - Upload Setup.exe
# - Upload version.json
# - Create release notes
```

### For Users:

```
1. User has v1.0.0 installed
2. App starts, checks internet
3. Downloads version.json from GitHub
4. Sees v1.1.0 is available
5. Shows update dialog with release notes
6. User clicks "Update Now"
7. Downloads Setup.exe
8. Verifies SHA256
9. Launches updater.exe
10. Main app closes
11. Setup.exe installs silently
12. App restarts with v1.1.0
13. All user data preserved ✓
```

## Success Criteria

- ✅ 100% offline functionality
- ✅ Automatic updates when online
- ✅ Never loses user data
- ✅ Modern, professional UI
- ✅ Dark and light modes
- ✅ Responsive background workers
- ✅ Semantic versioning
- ✅ Rollback on failure
- ✅ SHA256 verification
- ✅ Clean modular architecture
- ✅ Single-button deployment to GitHub Releases

## Risk Mitigation

1. **Update fails mid-download**: Resume capability or restart download
2. **Installation corrupts app**: Rollback mechanism restores previous version
3. **User data lost**: Separate user data from application binaries
4. **Offline users**: Gracefully skip updates, no errors
5. **Network interruptions**: Timeout handling, retry logic
6. **SHA256 mismatch**: Reject corrupted downloads, notify user

## Timeline Estimate

- Phase 1-2: 2-3 days (Update system core)
- Phase 3: 1-2 days (Background workers)
- Phase 4: 1 day (Dark mode)
- Phase 5: 2 days (Modern dialogs)
- Phase 6: 2 days (Updater executable)
- Phase 7: 1-2 days (UI integration)
- Phase 8: 1-2 days (Build system)
- Phase 9: 2-3 days (Testing & polish)

**Total: 12-16 days** for complete implementation
