; ─────────────────────────────────────────────────────────────────────────────
; Inno Setup Script for Debt Manager Application
; Production-ready installer with data safety
; ─────────────────────────────────────────────────────────────────────────────

; Application: Debt Manager
; Version: 1.0.0
; 
; Usage:
;   1. Install Inno Setup 6: https://jrsoftware.org/isdl.php
;   2. Run: build_all.bat (creates Output/DebtManager_Setup.exe)
;
; Silent Install:
;   DebtManager_Setup.exe /VERYSILENT /NORESTART
;
; ─────────────────────────────────────────────────────────────────────────────

#define MyAppName "Debt Manager"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Duytri9123"
#define MyAppURL "https://github.com/Duytri9123/debt-manager-release"
#define MyAppExeName "DebtManager.exe"
#define MyAppUpdaterName "updater.exe"
#define MyAppID "{{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}"

[Setup]
; ── Application Information ─────────────────────────────────────────────────
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
AppId={#MyAppID}

; ── Installation Directory (AppData/Local - NOT Program Files) ──────────────
; This ensures no admin rights required and user data stays separate
DefaultDirName={localappdata}\DebtManager
DisableProgramGroupPage=yes
PrivilegesRequired=lowest

; ── Output Settings ────────────────────────────────────────────────────────
OutputDir=..\Output
OutputBaseFilename=DebtManager_Setup
SetupIconFile=icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}

; ── Compression ────────────────────────────────────────────────────────────
Compression=lzma2/ultra64
SolidCompression=yes
CompressionThreads=auto

; ── Architecture ───────────────────────────────────────────────────────────
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

; ── Wizard Settings ────────────────────────────────────────────────────────
WizardStyle=modern
WizardSizePercent=100,100

; ── Language ───────────────────────────────────────────────────────────────

; ── Uninstall Settings ─────────────────────────────────────────────────────
UninstallDisplayName={#MyAppName}
UninstallDisplaySize=52428800

; ── Version Information ────────────────────────────────────────────────────
VersionInfoVersion={#MyAppVersion}
VersionInfoCopyright=Copyright © 2026 {#MyAppPublisher}
VersionInfoDescription=Installer for {#MyAppName}
VersionInfoProductName={#MyAppName}
VersionInfoProductVersion={#MyAppVersion}

[Languages]
Name: "en"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
; ── Application Binaries ───────────────────────────────────────────────────
Source: "..\Output\DebtManager.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\Output\updater.exe"; DestDir: "{app}"; Flags: ignoreversion

; NOTE: Don't include source code, database, or user data!
; User data should be created dynamically by the application

[Icons]
; ── Start Menu Shortcuts ───────────────────────────────────────────────────
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"

; ── Desktop Shortcut ───────────────────────────────────────────────────────
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
; ── Launch Application After Install ───────────────────────────────────────
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
// ── Data Safety: Preserve user data during upgrade ────────────────────────
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssInstall then
  begin
    // Log that we're preserving user data
    Log('Installing to: ' + ExpandConstant('{app}'));
    Log('User data will be preserved in: ' + ExpandConstant('{localappdata}\DebtManager'));
  end;
end;

// ── Check for running application before install ─────────────────────────
function InitializeSetup(): Boolean;
var
  ResultCode: Integer;
begin
  Result := True;
  
  // Try to close running application
  if FindWindowByWindowName('Debt Manager') <> 0 then
  begin
    if MsgBox('Debt Manager is currently running.' + #13#10 +
              'Please close it and click OK to continue, or Cancel to abort.',
              mbConfirmation, MB_OKCANCEL) = IDOK then
    begin
      // Try to terminate the process
      Exec('taskkill', '/F /IM DebtManager.exe', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
      Exec('taskkill', '/F /IM updater.exe', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
      Sleep(2000); // Wait for processes to close
    end
    else
    begin
      Result := False;
    end;
  end;
end;
