[Setup]
AppName=Android Studio
AppVersion=1.0.2
DefaultDirName={pf}\Android StudioV1
DefaultGroupName=Android StudioV1 Tools
OutputDir=installer_output
OutputBaseFilename=AndroidStudioSetup
SetupIconFile=Android_Studio_icon.ico
LicenseFile=license.txt
InfoBeforeFile=readme.txt
InfoAfterFile=after_install.txt
UninstallIconFile=Android_Studio_icon.ico
WizardImageFile=setup_banner.bmp
WizardSmallImageFile=setup_icon.bmp
SilentInstall=true
SilentUninstall=true

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "french"; MessagesFile: "compiler:Languages\\French.isl"

[Files]
Source: "dist\\Android Studio\\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional icons:"; Flags: unchecked

[Icons]
Name: "{group}\\Android Studio"; Filename: "{app}\\Android Studio.exe"; Flags: runas
Name: "{commondesktop}\\Android Studio"; Filename: "{app}\\Android Studio.exe"; Tasks: desktopicon; Flags: runas
Name: "{group}\\Uninstall Android Studio"; Filename: "{uninstallexe}"

[Registry]
Root: HKCU; Subkey: "Software\\AndroidStudioV1"; ValueType: string; ValueName: "InstallPath"; ValueData: "{app}"; Flags: uninsdeletekey
Root: HKCR; Subkey: ".asv1"; ValueType: string; ValueData: "AndroidStudioV1File"
Root: HKCR; Subkey: "AndroidStudioV1File\\shell\\open\\command"; ValueType: string; ValueData: '"{app}\\Android Studio.exe" "%1"'

[UninstallDelete]
Type: filesandordirs; Name: "{app}\\user_data"

[Run]
Filename: "{app}\\Android Studio.exe"; Description: "Launch Android Studio"; Flags: nowait postinstall skipifsilent

[Code]
function InitializeSetup(): Boolean;
begin
  if not FileExists(ExpandConstant('{pf}\\Python313\\python.exe')) then
  begin
    MsgBox('Python 3.13 is required. Please install it first.', mbError, MB_OK);
    Result := False;
  end
  else
    Result := True;
end;
