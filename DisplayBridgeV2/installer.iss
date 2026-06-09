#define AppName "DisplayBridge"
#define AppVersion "2.0.0"
#define AppPublisher "Conrado Dembiski"
#define AppExeName "DisplayBridge.exe"

[Setup]
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName}
AppPublisher={#AppPublisher}
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
OutputBaseFilename=DisplayBridge_Setup_v2.0.0
OutputDir=instalador
SetupIconFile=displaybridge.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
WizardSizePercent=120
DisableProgramGroupPage=yes
PrivilegesRequired=admin
UninstallDisplayIcon={app}\{#AppExeName}
ShowLanguageDialog=no
LanguageDetectionMethod=none
WizardImageFile=compiler:WizClassicImage.bmp
WizardSmallImageFile=compiler:WizClassicSmallImage.bmp

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Tasks]
Name: "startup"; Description: "Iniciar automaticamente com o Windows"; GroupDescription: "Op&ções:"

[Files]
Source: "dist\DisplayBridge\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#AppName}"; Filename: "{app}\{#AppExeName}"
Name: "{userstartup}\{#AppName}"; Filename: "{app}\{#AppExeName}"; Tasks: startup

[Run]
Filename: "{app}\{#AppExeName}"; Description: "Iniciar {#AppName} agora"; Flags: nowait postinstall skipifsilent

[UninstallRun]
Filename: "taskkill"; Parameters: "/F /IM DisplayBridge.exe"; RunOnceId: "KillDisplayBridge"; Flags: runhidden

[Messages]
WelcomeLabel1=Bem-vindo ao DisplayBridge!
WelcomeLabel2=Move janelas entre monitores com Tab + Alt.%n%nO Alt+Tab continua funcionando normalmente.
FinishedHeadingLabel=Instalação concluída!
FinishedLabel=Use Tab → Alt para mover a janela em foco para o próximo monitor.%n%nO ícone aparece na bandeja do sistema (perto do relógio).
