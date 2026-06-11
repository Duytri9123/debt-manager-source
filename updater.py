"""
Auto-update process for B2B Management Application
This script checks for updates and downloads new versions.
"""

import sys
import os
import json
import urllib.request
import hashlib
import subprocess
import time
from pathlib import Path

def check_for_updates(version_url, current_version):
    """Check if a new version is available"""
    try:
        with urllib.request.urlopen(version_url) as response:
            version_info = json.loads(response.read().decode())
            
        latest_version = version_info.get('version', '0.0.0')
        print(f"Current version: {current_version}")
        print(f"Latest version: {latest_version}")
        
        # Simple version comparison
        if latest_version != current_version:
            return True, version_info
        return False, None
    except Exception as e:
        print(f"Error checking for updates: {e}")
        return False, None

def download_update(download_url, file_path):
    """Download the update file"""
    try:
        print(f"Downloading update from {download_url}...")
        urllib.request.urlretrieve(download_url, file_path)
        print("Download complete!")
        return True
    except Exception as e:
        print(f"Error downloading update: {e}")
        return False

def verify_file(file_path, expected_sha256):
    """Verify file integrity using SHA256"""
    try:
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        
        actual_hash = sha256_hash.hexdigest()
        return actual_hash == expected_sha256
    except Exception as e:
        print(f"Error verifying file: {e}")
        return False

def install_update(installer_path):
    """Run the installer"""
    try:
        print("Installing update...")
        subprocess.Popen([installer_path, '/VERYSILENT', '/NORESTART'])
        print("Update installation started. The application will restart after installation.")
        return True
    except Exception as e:
        print(f"Error installing update: {e}")
        return False

def main():
    print("=" * 50)
    print("B2B Management - Auto Update")
    print("=" * 50)
    
    # Configuration - these should be updated with your actual values
    VERSION_URL = "https://your-server.com/version.json"  # Update with actual URL
    CURRENT_VERSION = "1.0.0"  # This should be read from your app
    DOWNLOAD_DIR = Path.home() / "Downloads" / "B2BUpdate"
    
    # Create download directory
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    
    # Check for updates
    has_update, version_info = check_for_updates(VERSION_URL, CURRENT_VERSION)
    
    if not has_update:
        print("Your application is up to date!")
        return
    
    # Get update information
    download_url = version_info.get('download_url', '')
    expected_sha256 = version_info.get('sha256', '')
    installer_path = DOWNLOAD_DIR / "MyApp_Setup.exe"
    
    # Download update
    if not download_update(download_url, installer_path):
        return
    
    # Verify download
    if expected_sha256 and not verify_file(installer_path, expected_sha256):
        print("ERROR: Downloaded file verification failed!")
        return
    
    print("File verification successful!")
    
    # Install update
    if install_update(installer_path):
        print("Update process completed successfully!")
    else:
        print("Failed to install update.")

if __name__ == "__main__":
    main()
