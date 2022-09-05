; Script generated by the Inno Setup Script Wizard.
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING INNO SETUP SCRIPT FILES!

#define MyAppName "Subtitles Incorporated"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Andrei7506238"
#define MyAppURL "https://github.com/Andrei7506238/SubInc"
#define MyAppExeName "subinc.exe"

[Setup]
; NOTE: The value of AppId uniquely identifies this application. Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{2163A14F-115F-4D08-A359-5E57C767F18E}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
;AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\SubtitlesIncorporated
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
LicenseFile=LICENSE.txt
; Uncomment the following line to run in non administrative install mode (install for current user only.)
;PrivilegesRequired=lowest
OutputDir=OUT
OutputBaseFilename=SubInc_Win32
SetupIconFile=icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Tasks]
Name: InstallVCRedis; Description: "Install VC_redist.x86"

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "config\settings.json"; DestDir:"{app}\config"
Source: "config\placeholder\auth.json"; DestDir:"{app}\config"
Source: "config\validCategories.txt"; DestDir:"{app}\config"
Source: "mkvtoolnik\*"; DestDir:"{app}"
Source: "main.exe"; DestDir:"{app}"
Source: "movieHashCalculator.py"; DestDir:"{app}"
Source: "LICENSE.txt"; DestDir:"{app}"

Source: "0PREREQ\VC_redist.x86.exe"; DestDir:"{tmp}"
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"

[Registry]
Root: HKCR; Subkey: "Directory\Background\shell\SubInc\command"; ValueType: string; ValueData: "{app}\{#MyAppExeName}"; Flags: uninsdeletekey

[Run]
Filename: "{tmp}\VC_redist.x86.exe";    Tasks: InstallVCRedis
