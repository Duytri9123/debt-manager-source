# -*- coding: utf-8 -*-
"""
Update service - checks for updates and downloads new versions.
Uses QThread to keep UI responsive during network requests.
"""
import json
import hashlib
import urllib.request
import urllib.error
import subprocess
from pathlib import Path

from PySide6.QtCore import QObject, Signal, QThread


VERSION_URL = (
    "https://github.com/Duytri9123/debt-manager-release/"
    "releases/latest/download/version.json"
)


class UpdateCheckWorker(QObject):
    """Worker that checks for updates in a background thread."""
    finished = Signal(object)  # emits version_info dict or None
    error = Signal(str)

    def __init__(self, current_version: str):
        super().__init__()
        self.current_version = current_version

    def run(self):
        try:
            with urllib.request.urlopen(VERSION_URL, timeout=15) as resp:
                version_info = json.loads(resp.read().decode())

            latest = version_info.get("version", "")
            if latest and latest != self.current_version:
                self.finished.emit(version_info)
            else:
                self.finished.emit(None)
        except Exception as e:
            self.error.emit(str(e))


class UpdateDownloadWorker(QObject):
    """Worker that downloads the installer in a background thread."""
    progress = Signal(int)
    finished = Signal(str)  # emits installer path
    error = Signal(str)

    def __init__(self, download_url: str, expected_sha256: str, target_path: str):
        super().__init__()
        self.download_url = download_url
        self.expected_sha256 = expected_sha256
        self.target_path = target_path

    def run(self):
        try:
            # Download
            Path(self.target_path).parent.mkdir(parents=True, exist_ok=True)

            def report(block_count, block_size, total_size):
                if total_size > 0:
                    pct = int(block_count * block_size * 100 / total_size)
                    self.progress.emit(min(pct, 100))

            urllib.request.urlretrieve(
                self.download_url, self.target_path, reporthook=report
            )
            self.progress.emit(100)

            # Verify SHA256
            if self.expected_sha256:
                sha = hashlib.sha256()
                with open(self.target_path, "rb") as f:
                    for chunk in iter(lambda: f.read(65536), b""):
                        sha.update(chunk)
                if sha.hexdigest() != self.expected_sha256:
                    self.error.emit("SHA256 verification failed!")
                    return

            self.finished.emit(self.target_path)
        except Exception as e:
            self.error.emit(str(e))


class UpdateService(QObject):
    """High-level service to check & apply updates."""

    update_available = Signal(dict)     # version_info
    no_update = Signal()
    check_error = Signal(str)
    download_progress = Signal(int)     # 0-100
    download_complete = Signal(str)     # installer path
    download_error = Signal(str)

    def __init__(self, current_version: str = "1.0.0"):
        super().__init__()
        self.current_version = current_version
        self._thread = None
        self._worker = None
        self._version_info = None

    def check(self):
        """Start checking for updates in background."""
        self._thread = QThread()
        self._worker = UpdateCheckWorker(self.current_version)
        self._worker.moveToThread(self._thread)

        self._thread.started.connect(self._worker.run)
        self._worker.finished.connect(self._on_check_finished)
        self._worker.error.connect(self._on_check_error)
        self._worker.finished.connect(self._thread.quit)
        self._worker.error.connect(self._thread.quit)
        self._thread.finished.connect(self._worker.deleteLater)

        self._thread.start()

    def _on_check_finished(self, version_info):
        if version_info:
            self._version_info = version_info
            self.update_available.emit(version_info)
        else:
            self.no_update.emit()

    def _on_check_error(self, error_msg):
        self.check_error.emit(error_msg)

    def download_update(self):
        """Start downloading the update installer."""
        if not self._version_info:
            self.download_error.emit("No update information available")
            return

        download_url = self._version_info.get("download_url", "")
        expected_sha256 = self._version_info.get("sha256", "")
        target = str(Path.home() / "Downloads" / "B2BUpdate" / "DebtManager_Setup.exe")

        self._thread = QThread()
        self._worker = UpdateDownloadWorker(download_url, expected_sha256, target)
        self._worker.moveToThread(self._thread)

        self._thread.started.connect(self._worker.run)
        self._worker.progress.connect(self.download_progress)
        self._worker.finished.connect(self._on_download_finished)
        self._worker.error.connect(self._on_download_error)
        self._worker.finished.connect(self._thread.quit)
        self._worker.error.connect(self._thread.quit)
        self._thread.finished.connect(self._worker.deleteLater)

        self._thread.start()

    def _on_download_finished(self, installer_path):
        self.download_complete.emit(installer_path)

    def _on_download_error(self, error_msg):
        self.download_error.emit(error_msg)

    @staticmethod
    def install_update(installer_path: str):
        """Launch the installer silently."""
        try:
            subprocess.Popen([installer_path, "/VERYSILENT", "/NORESTART"])
            return True
        except Exception:
            return False
