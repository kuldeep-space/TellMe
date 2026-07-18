; Inno Setup Script for TellMe Application
; Generates a single TellMe_Setup.exe installer

#define MyAppName "TellMe"
#define MyAppVersion "0.1.0"
#define MyAppPublisher "TellMe AI"
#define MyAppExeName "app.exe"
#define SourceAppDir "D:\TellMe"
#define BuildOutputDir "D:\TellMe\app.dist"

[Setup]
AppId={{5D9D437D-6655-46D7-90C4-70494A3D5E00}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DisableProgramGroupPage=yes
OutputBaseFilename=TellMe_Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
SetupIconFile=D:\TellMe\frontend\assets\logos\Logo.ico
WizardImageFile=D:\TellMe\frontend\assets\logos\Logo.bmp
WizardSmallImageFile=D:\TellMe\frontend\assets\logos\Logo_small.bmp
CloseApplications=force
RestartApplications=yes
UsedUserAreasWarning=no


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
; Standalone build files from Nuitka
Source: "{#BuildOutputDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; Backend DLLs from local dependencies folder
Source: "{#SourceAppDir}\dependencies\llama_binaries\ggml-*.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#SourceAppDir}\dependencies\llama_binaries\libomp140.x86_64.dll"; DestDir: "{app}"; Flags: ignoreversion


; Frontend assets
Source: "{#SourceAppDir}\frontend\assets\*"; DestDir: "{app}\assets"; Flags: ignoreversion recursesubdirs createallsubdirs

; Frontend themes (required for dynamic discovery)
Source: "{#SourceAppDir}\frontend\themes\*"; DestDir: "{app}\frontend\themes"; Flags: ignoreversion recursesubdirs createallsubdirs



; Runtime config, settings, database, and folders (excluding the massive 8.5 GB GGUF model file)
; Excludes is used so the installer remains small, and the model can be placed in target user's runtime/models/ folder.
; If you WANT to bundle the 8.5 GB model file directly in the installer, delete the "Excludes: ..." from the line below and uncomment the model line.
Source: "{#SourceAppDir}\runtime\*"; DestDir: "{app}\runtime"; Excludes: "models\*.gguf,logs\*,temp\*,sessions\*,resumes\*,models.json,model_config.json,runtime_config.json,provider_*.json"; Flags: ignoreversion recursesubdirs createallsubdirs

; Optional: To bundle the 8.5 GB model file in the installer, uncomment the line below:
; Source: "{#SourceAppDir}\runtime\models\Qwen3-14B-Q4_K_M.gguf"; DestDir: "{app}\runtime\models"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; AppUserModelID: "tellme.app.version0.1.0"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon; AppUserModelID: "tellme.app.version0.1.0"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Registry]
Root: HKCU; Subkey: "Software\TellMe"; Flags: deletekey uninsdeletekey

[UninstallDelete]
Type: filesandordirs; Name: "{localappdata}\TellMe"

