; Inno Setup Script for Gym Bot
; This creates a Windows installer for the application

#define MyAppName "Gym Bot"
#define MyAppVersion "2.3.12"
#define MyAppPublisher "Anytime Fitness"
#define MyAppURL "https://www.anytimefitness.com"
#define MyAppExeName "GymBot.exe"

[Setup]
; Basic application info
AppId={{GYM-BOT-DASHBOARD-12345678}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}

; Installation directories
DefaultDirName={autopf}\GymBot
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes

; Output configuration
OutputDir=Output
OutputBaseFilename=GymBotInstaller
Compression=lzma
SolidCompression=yes

; UI configuration
WizardStyle=modern
; SetupIconFile=static\favicon.ico (commented out - no icon file available)
; UninstallDisplayIcon={app}\{#MyAppExeName}

; Privileges
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog

; Architecture
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
; Main application files
Source: "dist\GymBot\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; User guide
Source: "QUICK_START_GUIDE.md"; DestDir: "{app}"; Flags: ignoreversion; DestName: "Quick Start Guide.txt"

; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Dirs]
; Create data directories
Name: "{app}\data"; Permissions: users-full
Name: "{app}\logs"; Permissions: users-full
Name: "{app}\backups"; Permissions: users-full

[Icons]
; Start menu icons
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Quick Start Guide"; Filename: "{app}\Quick Start Guide.txt"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"

; Desktop icon
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

; Quick launch icon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
; Option to launch application after installation
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
// Custom installation code

function GetUninstallString(): String;
var
  sUnInstPath: String;
  sUnInstallString: String;
begin
  sUnInstPath := ExpandConstant('Software\Microsoft\Windows\CurrentVersion\Uninstall\{#emit SetupSetting("AppId")}_is1');
  sUnInstallString := '';
  if not RegQueryStringValue(HKLM, sUnInstPath, 'UninstallString', sUnInstallString) then
    RegQueryStringValue(HKCU, sUnInstPath, 'UninstallString', sUnInstallString);
  Result := sUnInstallString;
end;

function IsUpgrade(): Boolean;
begin
  Result := (GetUninstallString() <> '');
end;

function UnInstallOldVersion(): Integer;
var
  sUnInstallString: String;
  iResultCode: Integer;
begin
  Result := 0;
  sUnInstallString := GetUninstallString();
  if sUnInstallString <> '' then begin
    sUnInstallString := RemoveQuotes(sUnInstallString);
    if Exec(sUnInstallString, '/SILENT /NORESTART /SUPPRESSMSGBOXES','', SW_HIDE, ewWaitUntilTerminated, iResultCode) then
      Result := 3
    else
      Result := 2;
  end else
    Result := 1;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if (CurStep=ssInstall) then
  begin
    if (IsUpgrade()) then
    begin
      UnInstallOldVersion();
    end;
  end;
end;

function InitializeSetup(): Boolean;
begin
  Result := True;

  // Check if .NET or other prerequisites are needed
  // Add prerequisite checks here if needed
end;

procedure InitializeWizard();
begin
  // Custom wizard initialization if needed
end;
