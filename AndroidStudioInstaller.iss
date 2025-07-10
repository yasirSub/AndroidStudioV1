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

[Files]
Source: "dist\\Android Studio\\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional icons:"; Flags: unchecked


[Registry]
Root: HKCU; Subkey: "Software\\AndroidStudioV1"; ValueType: string; ValueName: "InstallPath"; ValueData: "{app}"; Flags: uninsdeletekey

[Icons]
Name: "{group}\\Android Studio"; Filename: "{app}\\Android Studio.exe"
Name: "{commondesktop}\\Android Studio"; Filename: "{app}\\Android Studio.exe"; Tasks: desktopicon
Name: "{group}\\Uninstall Android Studio"; Filename: "{uninstallexe}"
