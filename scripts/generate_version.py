# -*- coding: utf-8 -*-
"""
Generate version.json for GitHub Releases
Calculates SHA256 checksum and updates version metadata
"""
import json
import hashlib
import argparse
from pathlib import Path
from datetime import datetime


def calculate_sha256(file_path: str) -> str:
    """Calculate SHA256 hash of a file"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()


def generate_version_json(
    setup_exe_path: str,
    version: str,
    minimum_version: str = "1.0.0",
    mandatory: bool = False,
    release_notes: list = None,
    output_path: str = "version.json"
):
    """Generate version.json file for GitHub Releases"""
    
    if not Path(setup_exe_path).exists():
        print(f"❌ Error: {setup_exe_path} not found!")
        return False
    
    # Calculate SHA256
    print(f"🔐 Calculating SHA256 for {setup_exe_path}...")
    sha256 = calculate_sha256(setup_exe_path)
    print(f"✅ SHA256: {sha256}")
    
    # Build version info
    version_info = {
        "version": version,
        "minimum_supported_version": minimum_version,
        "download_url": f"https://github.com/Duytri9123/debt-manager-release/releases/download/v{version}/DebtManager_Setup.exe",
        "sha256": sha256,
        "mandatory": mandatory,
        "release_date": datetime.now().strftime("%Y-%m-%d"),
        "release_notes": release_notes or ["Bug fixes and improvements"]
    }
    
    # Write to file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(version_info, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Generated {output_path}")
    print(f"📦 Version: {version}")
    print(f"🔗 Download URL: {version_info['download_url']}")
    
    return True


def main():
    parser = argparse.ArgumentParser(description='Generate version.json for GitHub Releases')
    parser.add_argument('--setup', required=True, help='Path to DebtManager_Setup.exe')
    parser.add_argument('--version', required=True, help='Version number (e.g., 1.0.0)')
    parser.add_argument('--min-version', default='1.0.0', help='Minimum supported version')
    parser.add_argument('--mandatory', action='store_true', help='Mark as mandatory update')
    parser.add_argument('--notes', nargs='*', help='Release notes')
    parser.add_argument('--output', default='version.json', help='Output file path')
    
    args = parser.parse_args()
    
    success = generate_version_json(
        setup_exe_path=args.setup,
        version=args.version,
        minimum_version=args.min_version,
        mandatory=args.mandatory,
        release_notes=args.notes,
        output_path=args.output
    )
    
    if success:
        print("\n✨ version.json generated successfully!")
        print("\nNext steps:")
        print("1. Upload DebtManager_Setup.exe to GitHub Releases")
        print("2. Upload version.json to GitHub Releases")
        print("3. Create release tag: v" + args.version)
    else:
        print("\n❌ Failed to generate version.json")
        exit(1)


if __name__ == "__main__":
    main()
