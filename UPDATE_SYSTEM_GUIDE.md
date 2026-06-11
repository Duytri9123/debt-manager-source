# Auto-Update System Implementation Guide

## ✅ Completed Files

The following core infrastructure files have been created:

### 1. Core Infrastructure
- ✅ `src/core/version.py` - Semantic versioning parser and comparator
- ✅ `src/core/logger.py` - Logging system with rotation
- ✅ `src/core/paths.py` - AppData path management
- ✅ `src/core/settings.py` - Configuration manager
- ✅ `src/update/models.py` - Update data models

### 2. Architecture
- ✅ `ARCHITECTURE.md` - Complete project architecture
- ✅ Modular design with SOLID principles
- ✅ Offline-first approach
- ✅ Data protection strategy

---

## 📝 Files to Implement

Below is the complete implementation guide for remaining components.

---

### 3. Network Utility (`src/utils/network.py`)

```python
# -*- coding: utf-8 -*-
"""
Network connectivity checker
"""
import socket
import requests


def is_online(timeout: int = 3) -> bool:
    """Check if Internet connection is available"""
    try:
        # Try DNS resolution first (fastest)
        socket.setdefaulttimeout(timeout)
        socket.gethostbyname("github.com")
        return True
    except socket.error:
        pass
    
    try:
        # Try HTTP request
        requests.get("https://github.com", timeout=timeout)
        return True
    except requests.RequestException:
        return False
```

---

### 4. GitHub Release Parser (`src/update/github_release.py`)

```python
# -*- coding: utf-8 -*-
"""
GitHub Release API integration
"""
import requests
from typing import Optional
from src.core.logger import AppLogger
from src.update.models import VersionInfo

logger = AppLogger().get_logger()

GITHUB_API_URL = "https://api.github.com/repos/{owner}/{repo}/releases/latest"
VERSION_JSON_URL = "https://raw.githubusercontent.com/{owner}/{repo}/main/installer/version.json"


class GitHubReleaseChecker:
    """Check GitHub for new releases"""
    
    def __init__(self, owner: str, repo: str):
        self.owner = owner
        self.repo = repo
        self.headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'B2BManagement-UpdateChecker'
        }
    
    def get_version_json(self) -> Optional[dict]:
        """Download version.json from repository"""
        try:
            url = VERSION_JSON_URL.format(owner=self.owner, repo=self.repo)
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to download version.json: {e}")
            return None
    
    def get_latest_release(self) -> Optional[VersionInfo]:
        """Get latest release information"""
        try:
            version_data = self.get_version_json()
            if not version_data:
                return None
            
            version_info = VersionInfo.from_json(version_data)
            logger.info(f"Found version: {version_info.version}")
            return version_info
            
        except Exception as e:
            logger.error(f"Failed to get latest release: {e}")
            return None
```

---

### 5. Version Checker (`src/update/version_checker.py`)

```python
# -*- coding: utf-8 -*-
"""
Update detection logic
"""
from src.core.version import APP_VERSION
from src.core.settings import Settings
from src.core.logger import AppLogger
from src.update.models import UpdateResult, VersionInfo
from src.update.github_release import GitHubReleaseChecker
from src.utils.network import is_online

logger = AppLogger().get_logger()


class UpdateChecker:
    """Check for application updates"""
    
    def __init__(self, settings: Settings, github_owner: str, github_repo: str):
        self.settings = settings
        self.github_checker = GitHubReleaseChecker(github_owner, github_repo)
    
    def check_for_updates(self, force: bool = False) -> UpdateResult:
        """
        Check if update is available
        
        Returns:
            UpdateResult with update information
        """
        result = UpdateResult()
        
        # Check Internet connection
        result.is_online = is_online()
        if not result.is_online:
            logger.info("No Internet connection, skipping update check")
            return result
        
        # Get latest version
        version_info = self.github_checker.get_latest_release()
        if not version_info:
            result.error = "Failed to fetch version information"
            return result
        
        # Check if user skipped this version
        if not force and self.settings.skipped_version == str(version_info.version):
            logger.info(f"User skipped version {version_info.version}")
            return result
        
        # Compare versions
        if version_info.version > APP_VERSION:
            result.update_available = True
            result.version_info = version_info
            
            # Check minimum supported version
            if APP_VERSION < version_info.minimum_supported_version:
                result.version_info.mandatory = True
                logger.warning("Current version no longer supported, update mandatory")
            
            logger.info(f"Update available: {version_info.version}")
        else:
            logger.info("Application is up to date")
        
        return result
```

---

### 6. Downloader (`src/update/downloader.py`)

```python
# -*- coding: utf-8 -*-
"""
HTTP downloader with progress tracking
"""
import os
import time
import requests
from typing import Callable, Optional
from src.core.logger import AppLogger

logger = AppLogger().get_logger()


class Downloader:
    """Download files with progress tracking"""
    
    def __init__(self):
        self._cancelled = False
        self._downloaded_bytes = 0
        self._total_bytes = 0
        self._start_time = 0
        self._progress_callback: Optional[Callable] = None
    
    def download(
        self,
        url: str,
        output_path: str,
        progress_callback: Optional[Callable[[int, int, float], None]] = None
    ) -> bool:
        """
        Download file with progress
        
        Args:
            url: Download URL
            output_path: Save path
            progress_callback: Callback(downloaded, total, speed)
            
        Returns:
            True if download successful
        """
        self._cancelled = False
        self._progress_callback = progress_callback
        
        try:
            logger.info(f"Downloading: {url}")
            
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            self._total_bytes = int(response.headers.get('content-length', 0))
            self._downloaded_bytes = 0
            self._start_time = time.time()
            
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if self._cancelled:
                        logger.info("Download cancelled by user")
                        return False
                    
                    if chunk:
                        f.write(chunk)
                        self._downloaded_bytes += len(chunk)
                        
                        if self._progress_callback:
                            elapsed = time.time() - self._start_time
                            speed = self._downloaded_bytes / elapsed if elapsed > 0 else 0
                            self._progress_callback(
                                self._downloaded_bytes,
                                self._total_bytes,
                                speed
                            )
            
            logger.info(f"Download completed: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Download failed: {e}")
            return False
    
    def cancel(self):
        """Cancel download"""
        self._cancelled = True
```

---

### 7. Checksum Verifier (`src/update/checksum.py`)

```python
# -*- coding: utf-8 -*-
"""
SHA256 checksum verification
"""
import hashlib
from src.core.logger import AppLogger

logger = AppLogger().get_logger()


def calculate_sha256(file_path: str, chunk_size: int = 8192) -> str:
    """Calculate SHA256 hash of file"""
    sha256_hash = hashlib.sha256()
    
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            sha256_hash.update(chunk)
    
    return sha256_hash.hexdigest()


def verify_checksum(file_path: str, expected_hash: str) -> bool:
    """
    Verify file checksum
    
    Args:
        file_path: Path to file
        expected_hash: Expected SHA256 hash
        
    Returns:
        True if checksum matches
    """
    try:
        actual_hash = calculate_sha256(file_path)
        matches = actual_hash.lower() == expected_hash.lower()
        
        if matches:
            logger.info(f"Checksum verified: {file_path}")
        else:
            logger.error(f"Checksum mismatch!")
            logger.error(f"  Expected: {expected_hash}")
            logger.error(f"  Actual:   {actual_hash}")
        
        return matches
        
    except Exception as e:
        logger.error(f"Checksum verification failed: {e}")
        return False
```

---

### 8. Rollback Mechanism (`src/update/rollback.py`)

```python
# -*- coding: utf-8 -*-
"""
Rollback mechanism for failed updates
"""
import os
import shutil
from src.core.paths import AppPaths
from src.core.logger import AppLogger

logger = AppLogger().get_logger()


class RollbackManager:
    """Manage update rollback"""
    
    def __init__(self, paths: AppPaths):
        self.paths = paths
    
    def backup_current_exe(self) -> bool:
        """Backup current executable before update"""
        try:
            current_exe = os.path.join(self.paths.app_dir, 'QuanLyB2B.exe')
            
            if not os.path.exists(current_exe):
                logger.warning("Current executable not found, skipping backup")
                return True
            
            os.makedirs(self.paths.rollback_dir, exist_ok=True)
            shutil.copy2(current_exe, self.paths.previous_exe_path)
            
            logger.info(f"Backed up executable to: {self.paths.previous_exe_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to backup executable: {e}")
            return False
    
    def restore_previous_version(self) -> bool:
        """Restore previous version from backup"""
        try:
            current_exe = os.path.join(self.paths.app_dir, 'QuanLyB2B.exe')
            
            if not os.path.exists(self.paths.previous_exe_path):
                logger.error("No backup found for rollback")
                return False
            
            # Replace current executable with backup
            shutil.copy2(self.paths.previous_exe_path, current_exe)
            
            logger.info("Rolled back to previous version")
            return True
            
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            return False
    
    def cleanup_rollback(self):
        """Clean up rollback files after successful update"""
        try:
            if os.path.exists(self.paths.previous_exe_path):
                os.remove(self.paths.previous_exe_path)
                logger.info("Cleaned up rollback files")
        except Exception as e:
            logger.error(f"Failed to cleanup rollback: {e}")
```

---

### 9. Update Worker Thread (`src/workers/update_worker.py`)

```python
# -*- coding: utf-8 -*-
"""
Background worker for checking updates
"""
from PySide6.QtCore import QObject, Signal

from src.update.version_checker import UpdateChecker
from src.update.models import UpdateResult


class UpdateWorker(QObject):
    """Worker thread for update checking"""
    
    # Signals
    finished = Signal(object)  # UpdateResult
    error = Signal(str)
    
    def __init__(self, update_checker: UpdateChecker):
        super().__init__()
        self.update_checker = update_checker
    
    def run(self):
        """Check for updates"""
        try:
            result = self.update_checker.check_for_updates()
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))
```

---

### 10. Download Worker Thread (`src/workers/download_worker.py`)

```python
# -*- coding: utf-8 -*-
"""
Background worker for downloading updates
"""
from PySide6.QtCore import QObject, Signal

from src.update.downloader import Downloader


class DownloadWorker(QObject):
    """Worker thread for downloading updates"""
    
    # Signals
    progress = Signal(int, int, float)  # downloaded, total, speed
    finished = Signal(bool)
    error = Signal(str)
    
    def __init__(self, downloader: Downloader, url: str, output_path: str):
        super().__init__()
        self.downloader = downloader
        self.url = url
        self.output_path = output_path
    
    def run(self):
        """Download file"""
        try:
            success = self.downloader.download(
                self.url,
                self.output_path,
                self._on_progress
            )
            self.finished.emit(success)
        except Exception as e:
            self.error.emit(str(e))
    
    def _on_progress(self, downloaded: int, total: int, speed: float):
        """Emit progress signal"""
        self.progress.emit(downloaded, total, speed)
    
    def cancel(self):
        """Cancel download"""
        self.downloader.cancel()
```

---

### 11. Update Dialog (`src/ui/update_dialog.py`)

```python
# -*- coding: utf-8 -*-
"""
Modern update notification dialog
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTextEdit, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from src.update.models import UpdateResult


class UpdateDialog(QDialog):
    """Update notification dialog"""
    
    def __init__(self, result: UpdateResult, parent=None):
        super().__init__(parent)
        self.result = result
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup dialog UI"""
        self.setWindowTitle("Cập nhật phiên bản mới")
        self.setMinimumSize(500, 400)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        
        # Header
        header = QLabel("🎉 Phiên bản mới khả dụng!")
        header.setFont(QFont("Segoe UI", 18, QFont.Bold))
        layout.addWidget(header)
        
        # Version info
        version_frame = QFrame()
        version_frame.setObjectName("statCard")
        version_layout = QVBoxLayout(version_frame)
        
        current_label = QLabel(f"Hiện tại: {self.result.current_version_str}")
        current_label.setFont(QFont("Segoe UI", 12))
        version_layout.addWidget(current_label)
        
        latest_label = QLabel(f"Mới nhất: {self.result.latest_version_str}")
        latest_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        latest_label.setStyleSheet("color: #6366F1;")
        version_layout.addWidget(latest_label)
        
        layout.addWidget(version_frame)
        
        # Release notes
        notes_label = QLabel("📝 Ghi chú phiên bản:")
        notes_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        layout.addWidget(notes_label)
        
        notes_text = QTextEdit()
        notes_text.setReadOnly(True)
        notes_text.setStyleSheet("""
            QTextEdit {
                background-color: #F9FAFB;
                border: 1px solid #E5E7EB;
                border-radius: 8px;
                padding: 12px;
            }
        """)
        
        if self.result.version_info:
            notes = "\n".join([f"• {note}" for note in self.result.version_info.release_notes])
            notes_text.setPlainText(notes)
        
        layout.addWidget(notes_text, 1)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        if not self.result.is_mandatory:
            skip_btn = QPushButton("Bỏ qua phiên bản này")
            skip_btn.setObjectName("outlineButton")
            skip_btn.clicked.connect(self._on_skip)
            button_layout.addWidget(skip_btn)
            
            remind_btn = QPushButton("Nhắc tôi sau")
            remind_btn.setObjectName("outlineButton")
            remind_btn.clicked.connect(self.reject)
            button_layout.addWidget(remind_btn)
        
        update_btn = QPushButton("🚀 Cập nhật ngay")
        update_btn.setObjectName("primaryButton")
        update_btn.setMinimumWidth(150)
        update_btn.clicked.connect(self.accept)
        button_layout.addWidget(update_btn)
        
        layout.addLayout(button_layout)
    
    def _on_skip(self):
        """Skip this version"""
        self.done(2)  # Custom return code for skip
```

---

### 12. Download Progress Dialog (`src/ui/download_dialog.py`)

```python
# -*- coding: utf-8 -*-
"""
Download progress dialog
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QProgressBar, QFrame
)
from PySide6.QtCore import Qt, QThread
from PySide6.QtGui import QFont

from src.workers.download_worker import DownloadWorker


def format_size(size_bytes: int) -> str:
    """Format file size"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


class DownloadDialog(QDialog):
    """Download progress dialog"""
    
    def __init__(self, worker: DownloadWorker, parent=None):
        super().__init__(parent)
        self.worker = worker
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        """Setup dialog UI"""
        self.setWindowTitle("Đang tải bản cập nhật...")
        self.setMinimumSize(500, 250)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        
        # Title
        title = QLabel("📥 Đang tải bản cập nhật")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        layout.addWidget(title)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimumHeight(30)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #E5E7EB;
                border-radius: 8px;
                text-align: center;
                background-color: #F3F4F6;
            }
            QProgressBar::chunk {
                background-color: #6366F1;
                border-radius: 7px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # Progress info
        self.info_label = QLabel("Chuẩn bị tải...")
        self.info_label.setFont(QFont("Segoe UI", 11))
        self.info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.info_label)
        
        # Speed label
        self.speed_label = QLabel("")
        self.speed_label.setFont(QFont("Segoe UI", 10))
        self.speed_label.setAlignment(Qt.AlignCenter)
        self.speed_label.setStyleSheet("color: #6B7280;")
        layout.addWidget(self.speed_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_btn = QPushButton("❌ Hủy")
        self.cancel_btn.setObjectName("outlineButton")
        self.cancel_btn.clicked.connect(self._on_cancel)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
    
    def _connect_signals(self):
        """Connect worker signals"""
        self.worker.progress.connect(self._on_progress)
        self.worker.finished.connect(self._on_finished)
        self.worker.error.connect(self._on_error)
    
    def _on_progress(self, downloaded: int, total: int, speed: float):
        """Update progress"""
        if total > 0:
            percentage = int((downloaded / total) * 100)
            self.progress_bar.setValue(percentage)
            self.info_label.setText(
                f"{format_size(downloaded)} / {format_size(total)} ({percentage}%)"
            )
            self.speed_label.setText(f"Tốc độ: {format_size(speed)}/s")
    
    def _on_finished(self, success: bool):
        """Download finished"""
        if success:
            self.info_label.setText("✅ Tải xuống thành công!")
            self.accept()
        else:
            self.info_label.setText("❌ Tải xuống thất bại")
            self.reject()
    
    def _on_error(self, error: str):
        """Download error"""
        self.info_label.setText(f"❌ Lỗi: {error}")
        self.reject()
    
    def _on_cancel(self):
        """Cancel download"""
        self.worker.cancel()
        self.reject()
```

---

### 13. Updater.exe (`updater.py`)

```python
# -*- coding: utf-8 -*-
"""
Updater - Separate process that handles update installation
This runs OUTSIDE the main application
"""
import sys
import os
import subprocess
import time
from pathlib import Path


def main():
    """Run update process"""
    if len(sys.argv) < 3:
        print("Usage: updater.exe <setup_path> <main_exe_path>")
        sys.exit(1)
    
    setup_path = sys.argv[1]
    main_exe_path = sys.argv[2]
    
    try:
        # Wait for main app to close
        time.sleep(2)
        
        # Run setup silently
        print("Installing update...")
        subprocess.run([setup_path, '/SILENT'], check=True)
        
        # Wait for installation
        time.sleep(3)
        
        # Restart main application
        print("Restarting application...")
        subprocess.Popen([main_exe_path])
        
        print("Update completed successfully!")
        
    except Exception as e:
        print(f"Update failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
```

---

## 📦 Build Scripts

### `build.bat` (Main Application)

```batch
@echo off
echo Building QuanLyB2B.exe...
pyinstaller --clean ^
    --name="QuanLyB2B" ^
    --windowed ^
    --onefile ^
    --icon=installer\icon.ico ^
    --add-data "src;src" ^
    main.py

echo Build complete: dist\QuanLyB2B.exe
pause
```

### `build_updater.bat`

```batch
@echo off
echo Building Updater.exe...
pyinstaller --clean ^
    --name="Updater" ^
    --onefile ^
    --console ^
    updater.py

echo Build complete: dist\Updater.exe
pause
```

---

## 🎯 Next Steps

1. **Create remaining files** using the templates above
2. **Test update flow** locally with mock version.json
3. **Setup GitHub repository** with private access
4. **Create version.json** in `installer/` folder
5. **Build Setup.exe** using Inno Setup
6. **Deploy to GitHub Releases**
7. **Test auto-update** from clean installation

---

## 📚 Resources

- [PySide6 Documentation](https://doc.qt.io/qtforpython/)
- [PyInstaller Documentation](https://pyinstaller.org/)
- [Inno Setup Documentation](https://jrsoftware.org/isshelp/)
- [GitHub Releases API](https://docs.github.com/en/rest/releases)

---

**Ready to continue?** Let me know which component you'd like me to implement next!
