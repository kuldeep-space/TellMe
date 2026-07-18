; ==============================================================================
; TellMe AI Desktop Application — Enterprise Production Installer Script
; ==============================================================================

#define MyAppName "TellMe"
#define MyAppVersion "0.1.0"
#define MyAppPublisher "TellMe AI"
#define MyAppURL "https://github.com/kuldeep-space/TellMe"
#define MyAppExeName "app.exe"
#define SourceAppDir "D:\TellMe"
#define BuildOutputDir "D:\TellMe\app.dist"
#define MyAppAppUserModelID "tellme.app.version0.1.0"

[Setup]
; Unique Application ID
AppId={{5D9D437D-6655-46D7-90C4-70494A3D5E00}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}

; Native 64-bit Architecture Setup
ArchitecturesInstallIn64BitMode=x64compatible
DefaultDirName={autopf}\{#MyAppName}
DisableProgramGroupPage=yes
OutputBaseFilename=TellMe_Setup

; Modern Ultra Compression
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern

; Branding Assets
SetupIconFile=D:\TellMe\frontend\assets\logos\Logo.ico
WizardImageFile=D:\TellMe\frontend\assets\logos\Logo.bmp
WizardSmallImageFile=D:\TellMe\frontend\assets\logos\Logo_small.bmp

; Version Information Metadata
VersionInfoVersion=0.1.0.0
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription=TellMe AI Desktop Application
VersionInfoCopyright=Copyright (C) 2026 {#MyAppPublisher}

; Process Handling & Clean Upgrade
CloseApplications=force
RestartApplications=yes
UsedUserAreasWarning=no

; Control Panel / Uninstallation Settings
UninstallDisplayName={#MyAppName} AI Coach
UninstallDisplayIcon={app}\assets\logos\Logo.ico

[InstallDelete]
; Clean up old application binaries to prevent DLL version mismatches from older Nuitka compiles
Type: files; Name: "{app}\{#MyAppExeName}"
Type: files; Name: "{app}\*.dll"
Type: files; Name: "{app}\*.pyd"
Type: filesandordirs; Name: "{app}\assets"
Type: filesandordirs; Name: "{app}\frontend"

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Standalone compiled binaries from Nuitka
Source: "{#BuildOutputDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; Backend native DLL dependencies
Source: "{#SourceAppDir}\dependencies\llama_binaries\ggml-*.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#SourceAppDir}\dependencies\llama_binaries\libomp140.x86_64.dll"; DestDir: "{app}"; Flags: ignoreversion

; Frontend UI assets and themes
Source: "{#SourceAppDir}\frontend\assets\*"; DestDir: "{app}\assets"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "{#SourceAppDir}\frontend\themes\*"; DestDir: "{app}\frontend\themes"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "{#SourceAppDir}\frontend\themes\*"; DestDir: "{app}\themes"; Flags: ignoreversion recursesubdirs createallsubdirs

[Dirs]
; Pre-create clean runtime directory structure (app handles dynamic data generation)
Name: "{app}\runtime"
Name: "{app}\runtime\logs"
Name: "{app}\runtime\temp"
Name: "{app}\runtime\models"

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; AppUserModelID: "{#MyAppAppUserModelID}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon; AppUserModelID: "{#MyAppAppUserModelID}"
Name: "{autoprograms}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Registry]
Root: HKCU; Subkey: "Software\TellMe"; Flags: uninsdeletekey

[UninstallDelete]
Type: filesandordirs; Name: "{localappdata}\TellMe"
