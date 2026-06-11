; ─────────────────────────────────────────────────────────────────────────────
; Inno Setup Script for B2B Management Application
; ─────────────────────────────────────────────────────────────────────────────
; 
; Application: Quản lý B2B (B2B Management)
; Version: 1.0.0
; Build: Run build.bat first to create QuanLyB2B.exe and Updater.exe
;
; Usage:
;   1. Install Inno Setup 6: https://jrsoftware.org/isdl.php
;   2. Open this file in Inno Setup Compiler
;   3. Click "Build" → "Compile"
;   4. Output: Output\MyApp_Setup.exe
;
; Silent Install:
;   MyApp_Setup.exe /VERYSILENT /NORESTART
;
; ─────────────────────────────────────────────────────────────────────────────

#define MyAppName "Quản lý B2B"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "B2B Management"
#define MyAppURL "https://github.com/yourusername/b2b-management"
#define MyAppExeName "QuanLyB2B.exe"
#define MyAppUpdaterName "Updater.exe"
#define MyAppID "{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}"

[Setup]
; ── Application Information ──────────────────────────────────────────────────
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
AppId={#MyAppID}

; ── Installation Directories ─────────────────────────────────────────────────
; Install to Program Files
DefaultDirname={autopf}\{#MyAppName}
; Start Menu folder
DefaultGroupName={#MyAppName}

; ── Output Settings ──────────────────────────────────────────────────────────
OutputDir=Output
OutputBaseFilename=MyApp_Setup
SetupIconFile=installer\icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}

; ── Compression ──────────────────────────────────────────────────────────────
Compression=lzma2/ultra64
SolidCompression=yes
CompressionThreads=auto

; ── User Privileges ──────────────────────────────────────────────────────────
; Require admin privileges for Program Files installation
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog

; ── Architecture ─────────────────────────────────────────────────────────────
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

; ── Wizard Settings ──────────────────────────────────────────────────────────
WizardStyle=modern
WizardSizePercent=100,100
WizardImageFile=installer\wizard-large.bmp
WizardSmallImageFile=installer\wizard-small.bmp

; ── Language ─────────────────────────────────────────────────────────────────
Languages=en vi

; ── Uninstall Settings ───────────────────────────────────────────────────────
UninstallDisplayName={#MyAppName}
UninstallDisplaySize=52428800 ; 50 MB

; ── Mutex (prevent multiple instances during install) ────────────────────────
AppMutex={#MyAppName}-Installer

; ── Version Information ──────────────────────────────────────────────────────
VersionInfoVersion={#MyAppVersion}
VersionInfoCopyright=Copyright © 2026 {#MyAppPublisher}
VersionInfoDescription=Installer for {#MyAppName}
VersionInfoProductName={#MyAppName}
VersionInfoProductVersion={#MyAppVersion}

[Languages]
Name: "en"; MessagesFile: "compiler:Default.isl"
Name: "vi"; MessagesFile: "compiler:Languages\Vietnamese.isl"

[CustomMessages]
; English
en.AppDescription=Quản lý Công nợ & Đơn hàng B2B
en.CreateDesktopIcon=Create a &desktop shortcut
en.LaunchAfterInstall=&Launch {#MyAppName} after installation

; Vietnamese
vi.AppDescription=Quản lý Công nợ & Đơn hàng B2B
vi.CreateDesktopIcon=Tạo shortcut trên &Desktop
vi.LaunchAfterInstall=&Chạy {#MyAppName} sau khi cài đặt

[Tasks]
; Desktop icon task
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; ── Main Application Files ──────────────────────────────────────────────────
; Main executable
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
; Updater executable
Source: "dist\{#MyAppUpdaterName}"; DestDir: "{app}"; Flags: ignoreversion
; Python runtime files (if bundled separately)
; Source: "dist\_internal\*"; DestDir: "{app}\_internal"; Flags: ignoreversion recursesubdirs createallsubdirs

; ── Documentation (optional) ─────────────────────────────────────────────────
; Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion
; Source: "LICENSE"; DestDir: "{app}"; Flags: ignoreversion

; NOTE: Don't include user data files here!
; User data stays in AppData/Local and is NEVER overwritten

[Icons]
; ── Start Menu Shortcut ──────────────────────────────────────────────────────
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"

; ── Desktop Shortcut ─────────────────────────────────────────────────────────
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
; ── Launch Application After Install ─────────────────────────────────────────
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchAfterInstall}"; Flags: nowait postinstall skipifsilent shellexec

[UninstallDelete]
; ── Clean up AppData on uninstall (OPTIONAL - be careful!) ───────────────────
; UNCOMMENT ONLY if you want to delete user data on uninstall
; WARNING: This will delete ALL user data!
; Type: filesandordirs; Name: "{localappdata}\B2BManagement"

[Code]
// ─────────────────────────────────────────────────────────────────────────────
// Pascal Script - Custom Installation Logic
// ─────────────────────────────────────────────────────────────────────────────

var
  AppDataPath: String;
  DataProtected: Boolean;

// ── Initialize Setup ────────────────────────────────────────────────────────
function InitializeSetup(): Boolean;
begin
  Result := True;
  DataProtected := False;
  
  // Get AppData path
  AppDataPath := ExpandConstant('{localappdata}') + '\B2BManagement';
  
  Log('Installation started for ' + '{#MyAppName} ' + '{#MyAppVersion}');
  Log('AppData path: ' + AppDataPath);
end;

// ── Check if This is an Update Installation ─────────────────────────────────
function IsUpdateInstallation(): Boolean;
var
  OldExePath: String;
begin
  OldExePath := ExpandConstant('{app}') + '\{#MyAppExeName}';
  Result := FileExists(OldExePath);
  
  if Result then
    Log('Update installation detected (previous version found)');
end;

// ── Protect User Data Before Installation ───────────────────────────────────
procedure ProtectUserData();
var
  FilesToProtect: TStrings;
  i: Integer;
  SourceFile, DestFile: String;
begin
  if not DirExists(AppDataPath) then
  begin
    Log('No existing user data found, skipping protection');
    Exit;
  end;
  
  Log('Protecting user data before installation...');
  
  // List of files/directories to NEVER overwrite
  FilesToProtect := TStringList.Create;
  try
    FilesToProtect.Add('data\app.db');
    FilesToProtect.Add('config.json');
    FilesToProtect.Add('license.json');
    FilesToProtect.Add('backup');
    FilesToProtect.Add('exports');
    FilesToProtect.Add('imports');
    FilesToProtect.Add('uploads');
    FilesToProtect.Add('logs');
    
    // Note: We don't actually copy these anywhere because Inno Setup
    // only installs to {app} (Program Files), not AppData.
    // This procedure is for logging and verification.
    
    for i := 0 to FilesToProtect.Count - 1 do
    begin
      SourceFile := AppDataPath + '\' + FilesToProtect[i];
      if FileExists(SourceFile) or DirExists(SourceFile) then
      begin
        Log('  ✓ Protected: ' + FilesToProtect[i]);
      end;
    end;
    
    DataProtected := True;
    Log('User data protection completed');
  finally
    FilesToProtect.Free;
  end;
end;

// ── Prepare Installation ────────────────────────────────────────────────────
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssInstall then
  begin
    // Right before installation starts
    if IsUpdateInstallation() then
    begin
      Log('Preparing for update installation...');
      ProtectUserData();
    end;
  end;
  
  if CurStep = ssPostInstall then
  begin
    // After installation completed
    Log('Installation completed successfully');
    
    if DataProtected then
    begin
      Log('User data was protected during update');
    end;
  end;
end;

// ── Verify Installation ─────────────────────────────────────────────────────
function VerifyInstallation(): Boolean;
var
  ExePath: String;
begin
  ExePath := ExpandConstant('{app}') + '\{#MyAppExeName}';
  Result := FileExists(ExePath);
  
  if not Result then
  begin
    MsgBox('Installation verification failed!'#13#10 +
           'Main executable not found.', mbError, MB_OK);
  end
  else
  begin
    Log('Installation verified: ' + ExePath);
  end;
end;

// ── NextButtonClick Handler ─────────────────────────────────────────────────
function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
  
  if CurPageID = wpReady then
  begin
    // Right before installation starts (user clicked "Install")
    Log('User initiated installation');
  end;
end;

// ── Uninstall Confirmation ──────────────────────────────────────────────────
function InitializeUninstall(): Boolean;
begin
  Result := True;
  
  // Warn user about uninstallation
  if MsgBox('Are you sure you want to remove {#MyAppName}?'#13#10 +
            #13#10 +
            'Note: Your data in AppData will be preserved.'#13#10 +
            'You can reinstall later without losing data.',
            mbConfirmation, MB_YESNO) = IDNO then
  begin
    Result := False;
    Exit;
  end;
  
  Log('Uninstallation started');
end;

// ── CurUninstallStepChanged ─────────────────────────────────────────────────
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  AppDataPath: String;
begin
  if CurUninstallStep = usUninstall then
  begin
    Log('Removing application files from Program Files...');
  end;
  
  if CurUninstallStep = usPostUninstall then
  begin
    Log('Uninstallation completed');
    Log('User data preserved in: ' + ExpandConstant('{localappdata}') + '\B2BManagement');
    
    // Optional: Ask user if they want to delete user data
    if MsgBox('Do you want to delete all user data?'#13#10 +
              #13#10 +
              'WARNING: This cannot be undone!'#13#10 +
              '- Database (app.db)'#13#10 +
              '- Configuration (config.json)'#13#10 +
              '- License (license.json)'#13#10 +
              '- All exports, imports, uploads, logs',
              mbConfirmation, MB_YESNO) = IDYES then
    begin
      AppDataPath := ExpandConstant('{localappdata}') + '\B2BManagement';
      if DelTree(AppDataPath, True, True, True) then
      begin
        Log('User data deleted: ' + AppDataPath);
        MsgBox('All user data has been deleted.', mbInformation, MB_OK);
      end
      else
      begin
        Log('Failed to delete user data');
        MsgBox('Failed to delete some user data files.', mbError, MB_OK);
      end;
    end
    else
    begin
      Log('User chose to keep data in AppData');
    end;
  end;
end;
