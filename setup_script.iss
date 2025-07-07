; Script generated for Android Studio Installer
; This script is for use with Inno Setup to create an installer for the application

[Setup]
AppName=Android Studio
AppVersion=1.0.0
AppPublisher=Yasir Subhani
AppPublisherURL=https://github.com/yasirSub
AppSupportURL=https://github.com/yasirSub
AppUpdatesURL=https://github.com/yasirSub
DefaultDirName={autopf}\Android Studio
DefaultGroupName=Android Studio
AllowNoIcons=yes
; LicenseFile=LICENSE.txt ; Uncomment and provide a license file if available
OutputDir=installer_output
OutputBaseFilename=AndroidStudioSetup
; SetupIconFile=Android_Studio_icon_(2023).ico ; Uncomment and provide a valid .ico file if available
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1

[Files]
Source: "dist\Android Studio.exe"; DestDir: "{app}"; Flags: ignoreversion
; IMPORTANT: This targets the executable file directly in the 'dist' folder. If the executable name or path differs, update this 'Source' path to match the actual location of the built application file after running 'pyinstaller AndroidStudio.spec'.

[Icons]
Name: "{group}\Android Studio"; Filename: "{app}\Android Studio.exe"
Name: "{group}\{cm:UninstallProgram,Android Studio}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Android Studio"; Filename: "{app}\Android Studio.exe"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\Android Studio"; Filename: "{app}\Android Studio.exe"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\Android Studio.exe"; Description: "{cm:LaunchProgram,Android Studio}"; Flags: nowait postinstall skipifsilent

[Code]
function InitializeSetup: Boolean;
begin
  Result := True;
end;
