[Setup]
AppName=Anoid
AppVersion=1.0.0 PRO
DefaultDirName={pf}\Anoid
DefaultGroupName=Anoid Tools
OutputDir=installer_output
OutputBaseFilename=Anoid_Setup_PRO
; Uncomment these if you have the files
; SetupIconFile=Anoid.ico
; LicenseFile=license.txt
; InfoBeforeFile=readme.txt

[Files]
; This assumes you ran 'python build_exe.py' first to create the EXE in dist\
Source: "dist\Anoid.exe"; DestDir: "{app}"; Flags: ignoreversion

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional icons:"; Flags: unchecked

[Registry]
Root: HKCU; Subkey: "Software\Anoid"; ValueType: string; ValueName: "InstallPath"; ValueData: "{app}"; Flags: uninsdeletekey

[Icons]
Name: "{group}\Anoid"; Filename: "{app}\Anoid.exe"
Name: "{commondesktop}\Anoid"; Filename: "{app}\Anoid.exe"; Tasks: desktopicon
Name: "{group}\Uninstall Anoid"; Filename: "{uninstallexe}"

[Run]
Filename: "{app}\Anoid.exe"; Description: "Launch Anoid"; Flags: nowait postinstall skipifsilent
