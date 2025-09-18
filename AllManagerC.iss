#define MyAppName "AllManagerC"
#define MyAppVersion "5.5.7"
#define MyAppPublisher "AI Manager Team"
#define MyAppURL "https://example.local"
#define MyAppExeName "AllManagerC.exe"

[Setup]
AppId={{F61F4C41-2D5E-46BE-9D03-C2C6E6A1A5A1}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
OutputDir=dist
OutputBaseFilename=AllManagerC_Installer
Compression=lzma
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64
WizardStyle=modern
SetupIconFile=static\images\icon.ico

[Languages]
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"

[Files]
; основная сборка PyInstaller
Source: "dist\AllManagerC\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs ignoreversion

[Dirs]
; пользовательские данные и конфиги
Name: "{userappdata}\AllManagerC"; Flags: uninsneveruninstall
Name: "{userappdata}\AllManagerC\data"; Flags: uninsneveruninstall
Name: "{userappdata}\AllManagerC\uploads"; Flags: uninsneveruninstall

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Создать ярлык на рабочем столе"; GroupDescription: "Дополнительно:"; Flags: unchecked

[Run]
; Перед запуском создаём маркер установленной версии
Filename: "{cmd}"; Parameters: "/C setx ALLMANAGERC_INSTALLED 1"; Flags: runhidden
Filename: "{app}\{#MyAppExeName}"; Description: "Запустить {#MyAppName}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; НЕ удаляем пользовательские данные
Type: filesandordirs; Name: "{userappdata}\AllManagerC\logs"

[Code]
procedure CurStepChanged(CurStep: TSetupStep);
var cfg: string;
begin
  if CurStep = ssPostInstall then
  begin
    cfg := ExpandConstant('{userappdata}') + '\\AllManagerC\\config.json';
    if not DirExists(ExtractFileDir(cfg)) then
      ForceDirectories(ExtractFileDir(cfg));
    if not FileExists(cfg) then
      SaveStringToFile(cfg, '{\n  "app_info": {\n    "version": "{#MyAppVersion}",\n    "developer": "AI Manager Team",\n    "last_updated": ""\n  },\n  "service_urls": {\n    "ip_check_api": "https://ipinfo.io/{ip}/json"\n  }\n}', False);
  end;
end;


