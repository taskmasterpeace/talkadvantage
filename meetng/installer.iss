#define MyAppName "PowerPlay"
#define MyAppVersion "1.0"
#define MyAppPublisher "Your Company"
#define MyAppExeName "transcription_app_qt.py"
#define PythonDir "C:\Users\taskm\anaconda3\envs\powerplay"
#define PythonVer "312"

[Setup]
AppId={{8A839397-45B7-44CF-9B72-12856F9B7C71}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
OutputBaseFilename=PowerPlay_Setup
Compression=none
SolidCompression=no
WizardStyle=modern
DisableDirPage=no
DisableProgramGroupPage=no
UninstallDisplayIcon={app}\qt_version\resources\icons\app_icon.ico
OutputDir=installer_output
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

[Files]
; Python core and required DLLs
Source: "{#PythonDir}\python.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#PythonDir}\python{#PythonVer}.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#PythonDir}\*.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#PythonDir}\Library\bin\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; Python standard library
Source: "{#PythonDir}\DLLs\*"; DestDir: "{app}\DLLs"; Flags: ignoreversion recursesubdirs
Source: "{#PythonDir}\Lib\*"; DestDir: "{app}\Lib"; Flags: ignoreversion recursesubdirs createallsubdirs; Excludes: "site-packages\*"
Source: "{#PythonDir}\Lib\site-packages\PyQt6\*"; DestDir: "{app}\Lib\site-packages\PyQt6"; Flags: ignoreversion recursesubdirs
Source: "{#PythonDir}\Lib\site-packages\langchain*"; DestDir: "{app}\Lib\site-packages"; Flags: ignoreversion recursesubdirs
Source: "{#PythonDir}\Lib\site-packages\openai*"; DestDir: "{app}\Lib\site-packages"; Flags: ignoreversion recursesubdirs
Source: "{#PythonDir}\Lib\site-packages\pydantic*"; DestDir: "{app}\Lib\site-packages"; Flags: ignoreversion recursesubdirs
; Your application files
Source: "qt_version\*"; DestDir: "{app}\qt_version"; Flags: ignoreversion recursesubdirs
Source: "services\*"; DestDir: "{app}\services"; Flags: ignoreversion recursesubdirs
Source: "utils\*"; DestDir: "{app}\utils"; Flags: ignoreversion recursesubdirs

[Dirs]
Name: "{app}\temp"; Permissions: everyone-full
Name: "{app}\logs"; Permissions: everyone-full

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\python.exe"; Parameters: """{app}\qt_version\{#MyAppExeName}"""; WorkingDir: "{app}"; IconFilename: "{app}\qt_version\resources\icons\app_icon.ico"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\python.exe"; Parameters: """{app}\qt_version\{#MyAppExeName}"""; WorkingDir: "{app}"; IconFilename: "{app}\qt_version\resources\icons\app_icon.ico"

[Run]
Filename: "{app}\python.exe"; Parameters: "-m pip install --no-warn-script-location -r ""{app}\requirements.txt"""; WorkingDir: "{app}"; Flags: runhidden
Filename: "{app}\python.exe"; Parameters: """{app}\qt_version\{#MyAppExeName}"""; Description: "Launch application"; Flags: postinstall nowait

[Code]
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    SaveStringToFile(
      ExpandConstant('{app}\.env'),
      'OPENAI_API_KEY=your-api-key-here' + #13#10 +
      'ASSEMBLYAI_API_KEY=your-api-key-here' + #13#10,
      False
    );
  end;
end;

[UninstallDelete]
Type: filesandordirs; Name: "{app}"
