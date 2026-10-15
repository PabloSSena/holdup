; Inno Setup 6 script: wraps the PyInstaller output in dist\Holdup into dist\HoldupSetup.exe.
; Built by build.ps1; do not run before PyInstaller.

#define AppVersion "0.1.0"

[Setup]
; AppId identifies the install for upgrades and uninstall; never change it.
AppId={{6F0D2B7E-3C1A-4E8B-9A57-2D4C8E1F5B90}
AppName=Holdup
AppVersion={#AppVersion}
AppPublisher=Holdup
; Per-user install: no admin prompt, and the User owns the files.
PrivilegesRequired=lowest
DefaultDirName={localappdata}\Programs\Holdup
DisableProgramGroupPage=yes
DisableDirPage=yes
OutputDir=dist
OutputBaseFilename=HoldupSetup
Compression=lzma2
SolidCompression=yes
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayIcon={app}\Holdup.exe

[Files]
Source: "dist\Holdup\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{userprograms}\Holdup"; Filename: "{app}\Holdup.exe"

[Registry]
; The app writes its Start with Windows entry itself (on by default); this only removes it on uninstall.
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: none; ValueName: "Holdup"; Flags: uninsdeletevalue

[Run]
Filename: "{app}\Holdup.exe"; Description: "Start Holdup"; Flags: nowait postinstall skipifsilent
