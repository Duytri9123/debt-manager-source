# -*- coding: utf-8 -*-
"""
Publish release to GitHub using GitHub REST API
Automatically creates release and uploads assets
"""
import os
import sys
import json
import requests
from pathlib import Path
from datetime import datetime


class GitHubReleasePublisher:
    """Publish releases to GitHub via REST API"""
    
    def __init__(self, token: str, owner: str, repo: str):
        """
        Initialize publisher
        
        Args:
            token: GitHub Personal Access Token
            owner: GitHub username or organization
            repo: Repository name
        """
        self.token = token
        self.owner = owner
        self.repo = repo
        self.base_url = f"https://api.github.com/repos/{owner}/{repo}"
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    def create_release(self, tag: str, title: str, notes: list, draft: bool = False) -> dict:
        """
        Create a new GitHub Release
        
        Args:
            tag: Git tag (e.g., v1.0.0)
            title: Release title
            notes: List of release notes
            draft: If True, create as draft release
            
        Returns:
            Release data dict
        """
        url = f"{self.base_url}/releases"
        
        data = {
            "tag_name": tag,
            "name": title,
            "body": "\n".join([f"- {note}" for note in notes]),
            "draft": draft,
            "prerelease": False,
            "generate_release_notes": False
        }
        
        print(f"📝 Creating release {tag}...")
        response = requests.post(url, headers=self.headers, json=data)
        
        if response.status_code == 201:
            print(f"✅ Release created: {title}")
            return response.json()
        else:
            print(f"❌ Failed to create release!")
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    
    def upload_asset(self, release_id: int, file_path: str, content_type: str = "application/octet-stream") -> bool:
        """
        Upload an asset to a GitHub Release
        
        Args:
            release_id: Release ID from GitHub API
            file_path: Path to file to upload
            content_type: MIME type of file
            
        Returns:
            True if successful
        """
        uploads_base = self.base_url.replace("api.github.com", "uploads.github.com")
        url = f"{uploads_base}/releases/{release_id}/assets"
        
        file_name = Path(file_path).name
        file_size = Path(file_path).stat().st_size
        
        print(f"📤 Uploading {file_name} ({file_size / (1024*1024):.2f} MB)...")
        
        headers = self.headers.copy()
        headers["Content-Type"] = content_type
        
        params = {
            "name": file_name,
            "label": file_name
        }
        
        with open(file_path, 'rb') as f:
            response = requests.post(
                url,
                headers=headers,
                params=params,
                data=f
            )
        
        if response.status_code == 201:
            print(f"✅ Uploaded: {file_name}")
            return True
        else:
            print(f"❌ Failed to upload {file_name}!")
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    
    def get_release_by_tag(self, tag: str) -> dict:
        """Get existing release by tag"""
        url = f"{self.base_url}/releases/tags/{tag}"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        return None


def load_env_file(env_path: str = ".env") -> dict:
    """Load environment variables from .env file"""
    env_vars = {}
    if Path(env_path).exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    return env_vars


def main():
    """Main publishing workflow"""
    print("=" * 60)
    print("  GitHub Release Publisher")
    print("=" * 60)
    print()
    
    # Load configuration
    env_vars = load_env_file()
    
    github_token = os.environ.get("GITHUB_TOKEN") or env_vars.get("GITHUB_TOKEN")
    github_owner = os.environ.get("GITHUB_OWNER") or env_vars.get("GITHUB_OWNER", "Duytri9123")
    github_repo = os.environ.get("GITHUB_REPO") or env_vars.get("GITHUB_REPO", "debt-manager-release")
    
    if not github_token:
        print("❌ Error: GITHUB_TOKEN not found!")
        print("\nPlease set it in one of these ways:")
        print("1. Environment variable: GITHUB_TOKEN")
        print("2. .env file: GITHUB_TOKEN=your_token_here")
        print("\nTo create a token:")
        print("  Go to: https://github.com/settings/tokens")
        print("  Create token with 'repo' scope")
        sys.exit(1)
    
    # Get version from arguments or version.json
    version_file = Path("version.json")
    if not version_file.exists():
        version_file = Path("Output/version.json")
    
    if not version_file.exists():
        print("❌ Error: version.json not found!")
        print("Please run build_all.bat first.")
        sys.exit(1)
    
    with open(version_file, 'r') as f:
        version_info = json.load(f)
    
    version = version_info.get("version", "1.0.0")
    release_notes = version_info.get("release_notes", ["Bug fixes and improvements"])
    
    # Setup file paths
    setup_exe = Path("Output/DebtManager_Setup.exe")
    if not setup_exe.exists():
        print(f"❌ Error: {setup_exe} not found!")
        print("Please run build_all.bat first.")
        sys.exit(1)
    
    # Initialize publisher
    publisher = GitHubReleasePublisher(
        token=github_token,
        owner=github_owner,
        repo=github_repo
    )
    
    # Check if release already exists
    tag = f"v{version}"
    existing_release = publisher.get_release_by_tag(tag)
    
    if existing_release:
        print(f"⚠️  Release {tag} already exists!")
        print("Do you want to:")
        print("1. Delete and recreate it")
        print("2. Upload assets to existing release")
        print("3. Cancel")
        
        choice = input("\nEnter choice (1/2/3): ").strip()
        
        if choice == "1":
            print(f"Deleting release {tag}...")
            # Note: Would need to implement delete_release method
            print("Please delete it manually from GitHub and try again.")
            sys.exit(1)
        elif choice == "2":
            release_id = existing_release["id"]
            print(f"Using existing release (ID: {release_id})")
        else:
            print("Cancelled.")
            sys.exit(0)
    else:
        # Create new release
        release_data = publisher.create_release(
            tag=tag,
            title=f"Debt Manager {tag}",
            notes=release_notes,
            draft=False
        )
        
        if not release_data:
            print("❌ Failed to create release!")
            sys.exit(1)
        
        release_id = release_data["id"]
    
    # Upload assets
    print()
    print("Uploading release assets...")
    print("-" * 60)
    
    # Upload Setup.exe
    success1 = publisher.upload_asset(
        release_id=release_id,
        file_path=str(setup_exe),
        content_type="application/octet-stream"
    )
    
    # Upload version.json
    success2 = publisher.upload_asset(
        release_id=release_id,
        file_path=str(version_file),
        content_type="application/json"
    )
    
    # Summary
    print()
    print("=" * 60)
    if success1 and success2:
        print("  ✅ Release published successfully!")
        print("=" * 60)
        print()
        print(f"Release URL: https://github.com/{github_owner}/{github_repo}/releases/tag/{tag}")
        print()
        print("Assets uploaded:")
        print(f"  - DebtManager_Setup.exe")
        print(f"  - version.json")
        print()
        print("Users will now be able to:")
        print("  1. Download the installer from GitHub Releases")
        print("  2. Receive auto-update notifications")
    else:
        print("  ❌ Some uploads failed!")
        print("=" * 60)
        print("Please check the errors above and try again.")
        sys.exit(1)


if __name__ == "__main__":
    main()
