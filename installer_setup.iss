; Inno Setup Script for AndroidStudioV1 PRO
; Version: 1.0.4

[Setup]
AppId={{C6F4F5E1-B5D2-4A2E-9D12-7A9B3E4D5F6B}
AppName=AndroidStudioV1
AppVersion=1.0.4
AppPublisher=AndroidStudioV1 Team
DefaultDirName={autopf}\AndroidStudioV1
DefaultGroupName=AndroidStudioV1
AllowNoIcons=yes
OutputDir=.
OutputBaseFilename=AndroidStudioV1_Setup_v1.0.4
SetupIconFile=assets\logo.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; The main executable from the PyInstaller dist folder
Source: "dist\AndroidStudioV1.exe"; DestDir: "{app}"; Flags: ignoreversion
; Include the assets folder just in case (though PyInstaller bundles them, it's good for reference)
Source: "assets\*"; DestDir: "{app}\assets"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\AndroidStudioV1"; Filename: "{app}\AndroidStudioV1.exe"; IconFilename: "{app}\assets\logo.ico"
Name: "{autodesktop}\AndroidStudioV1"; Filename: "{app}\AndroidStudioV1.exe"; Tasks: desktopicon; IconFilename: "{app}\assets\logo.ico"

[Run]
Filename: "{app}\AndroidStudioV1.exe"; Description: "{cm:LaunchProgram,AndroidStudioV1}"; Flags: nowait postinstall skipifsilent
