[Setup]
AppName=Jinada
AppVersion=1.0
DefaultDirName={pf}\Jinada
DefaultGroupName=Jinada
OutputBaseFilename=JinadaInstaller
Compression=lzma
SolidCompression=yes
DiskSpanning=yes

[Files]
Source: "dist\Jinada.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autodesktop}\Jinada"; Filename: "{app}\Jinada.exe"
Name: "{group}\Jinada"; Filename: "{app}\Jinada.exe"
