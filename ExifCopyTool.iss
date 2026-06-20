#define MyAppName "ExifCopyTool"
#define MyAppVersion "0.8.0"
#define MyAppPublisher "Megumi Tools"
#define MyAppExeName "ExifCopyTool.exe"

[Setup]
AppId={{A39C53E9-0365-4BCB-B901-55B8C0D4A15F}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={localappdata}\Programs\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=installer
OutputBaseFilename=ExifCopyToolSetup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
SetupIconFile=
UninstallDisplayIcon={app}\{#MyAppExeName}

[Languages]
Name: "japanese"; MessagesFile: "compiler:Languages\Japanese.isl"

[Tasks]
Name: "contextmenu"; Description: "右クリックメニューを有効にする"; GroupDescription: "追加設定:"; Flags: checkedonce
Name: "desktopicon"; Description: "デスクトップにショートカットを作成"; GroupDescription: "ショートカット:"; Flags: unchecked

[Files]
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "exiftool.exe"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Parameters: "--register-context-menu"; Flags: runhidden; Tasks: contextmenu
Filename: "{app}\{#MyAppExeName}"; Description: "{#MyAppName} を起動"; Flags: nowait postinstall skipifsilent

[UninstallRun]
Filename: "{app}\{#MyAppExeName}"; Parameters: "--unregister-context-menu"; Flags: runhidden
