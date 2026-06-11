# B2B Management - Professional Desktop Application Architecture

## Project Structure

```
congnopython/
├── main.py                          # Application entry point
├── updater.py                       # Updater.exe entry point (separate process)
├── requirements.txt                 # Python dependencies
├── build.bat                        # Build main application
├── build_updater.bat               # Build updater.exe
├── README.md                        # This file
│
├── src/
│   ├── core/                        # Core infrastructure
│   │   ├── __init__.py
│   │   ├── version.py              # Semantic versioning
│   │   ├── logger.py               # Logging with rotation
│   │   ├── settings.py             # Configuration management
│   │   └── paths.py                # AppData paths management
│   │
│   ├── update/                      # Auto-update system
│   │   ├── __init__.py
│   │   ├── github_release.py       # GitHub API integration
│   │   ├── version_checker.py      # Update detection logic
│   │   ├── downloader.py           # HTTP downloader with progress
│   │   ├── checksum.py             # SHA256 verification
│   │   ├── rollback.py             # Rollback mechanism
│   │   └── models.py               # Update data models
│   │
│   ├── workers/                     # Background threads
│   │   ├── __init__.py
│   │   ├── update_worker.py        # Update checker worker
│   │   ├── download_worker.py      # Download progress worker
│   │   └── excel_worker.py         # Excel processing worker
│   │
│   ├── database/                    # Database layer
│   │   ├── __init__.py
│   │   ├── connection.py           # SQLite connection manager
│   │   └── migrations.py           # Database migrations
│   │
│   ├── services/                    # Business logic
│   │   ├── __init__.py
│   │   ├── customer_service.py
│   │   ├── product_service.py
│   │   ├── order_service.py
│   │   ├── debt_service.py
│   │   └── excel_service.py
│   │
│   ├── ui/                          # User interface
│   │   ├── __init__.py
│   │   ├── theme.py                # QSS theme (Dark/Light)
│   │   ├── main_window.py          # Main application window
│   │   ├── update_dialog.py        # Update notification dialog
│   │   ├── download_dialog.py      # Download progress dialog
│   │   └── pages/                  # Application pages
│   │       ├── __init__.py
│   │       ├── dashboard_page.py
│   │       ├── orders_page.py
│   │       ├── debts_page.py
│   │       ├── customers_page.py
│   │       └── products_page.py
│   │
│   └── utils/                       # Utilities
│       ├── __init__.py
│       ├── network.py              # Network connectivity check
│       ├── file_utils.py           # File operations
│       └── validators.py           # Input validators
│
├── data/                            # User data (AppData/Local)
│   ├── app.db                      # SQLite database
│   ├── config.json                 # User configuration
│   ├── license.json                # License information
│   ├── backup/                     # Database backups
│   ├── exports/                    # Exported files
│   ├── imports/                    # Imported files
│   ├── uploads/                    # Uploaded files
│   ├── logs/                       # Application logs
│   └── updates/                    # Update downloads
│
└── installer/                       # Inno Setup files
    ├── setup.iss                   # Installer script
    ├── version.json                # Update metadata
    └── icon.ico                    # Application icon
```

## Architecture Principles

### 1. Clean Architecture
- **Presentation Layer**: PySide6 UI components
- **Business Logic Layer**: Services
- **Data Access Layer**: Database, File storage
- **Infrastructure Layer**: Update system, Logging, Settings

### 2. SOLID Principles
- **Single Responsibility**: Each module has one purpose
- **Open/Closed**: Extensible without modification
- **Liskov Substitution**: Compatible components
- **Interface Segregation**: Focused interfaces
- **Dependency Inversion**: Depend on abstractions

### 3. Offline-First Design
- All features work without Internet
- Update system is optional and non-blocking
- User data always preserved

### 4. Safety First
- Never overwrite running executable
- SHA256 verification before installation
- Automatic rollback on failure
- User data never deleted

## Auto-Update Flow

```
1. App Startup
   ↓
2. Check Internet Connection
   ↓ (if online)
3. Download version.json from GitHub
   ↓
4. Compare versions (semantic versioning)
   ↓ (if update available)
5. Show Update Dialog
   ↓ (user clicks "Update Now")
6. Download Setup.exe with progress
   ↓
7. Verify SHA256 checksum
   ↓
8. Launch updater.exe
   ↓
9. updater.exe closes main app
   ↓
10. Run Setup.exe silently
    ↓
11. Setup.exe installs new version
    ↓
12. Restart application
```

## Data Protection

### Never Delete:
- `app.db` - User database
- `config.json` - User preferences
- `license.json` - License data
- `backup/` - Database backups
- `exports/` - User exports
- `imports/` - User imports
- `uploads/` - User uploads
- `logs/` - Application logs

### Only Replace:
- Application binaries (.exe files)
- Python libraries (if bundled)

## Update Metadata (version.json)

```json
{
  "version": "1.2.0",
  "minimum_supported_version": "1.0.0",
  "download_url": "https://github.com/USER/REPO/releases/latest/download/MyApp_Setup.exe",
  "sha256": "SHA256_HASH_OF_SETUP_EXE",
  "mandatory": false,
  "release_notes": [
    "Fixed Excel import performance",
    "Added debt reports",
    "Improved UI responsiveness"
  ]
}
```

## Security Measures

1. **SHA256 Verification**: Every download verified
2. **HTTPS Only**: GitHub releases use HTTPS
3. **No Source Code Access**: Users only get Setup.exe
4. **Private Repository**: Source code protected
5. **Rollback Protection**: Previous version preserved

## Next Steps

1. ✅ Architecture designed
2. ⏳ Implement core update infrastructure
3. ⏳ Build UI components
4. ⏳ Implement business services
5. ⏳ Create installer
6. ⏳ Test and deploy
