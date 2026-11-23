<p align="center">
  <img src="DisplayBridgeV4/assets/icon_store.png" alt="DisplayBridge Logo" width="120" />
</p>

<h1 align="center">DisplayBridge</h1>

<p align="center">
  Utilitário leve para Windows 10 e 11 que move a janela ativa entre monitores instantaneamente com <strong>Tab + Alt</strong>.
</p>

<p align="center">
  <a href="https://displaybridge.vercel.app/"><strong>🌐 Site Oficial (displaybridge.vercel.app)</strong></a>
  ·
  <a href="https://github.com/conrider3000/DisplayBridge/releases/latest/download/Instalar_DisplayBridge_v4.exe"><strong>⬇️ Baixar Instalador v4.0 (.exe)</strong></a>
  ·
  <a href="https://github.com/conrider3000/DisplayBridge/releases/latest/download/DisplayBridge_Portable.exe"><strong>📦 Versão Portátil (.exe)</strong></a>
  ·
  <a href="https://github.com/conrider3000/DisplayBridge/releases/latest"><strong>🏷️ Releases</strong></a>
</p>

---

## O que é o DisplayBridge?

O **DisplayBridge** roda silenciosamente na bandeja do sistema (ao lado do relógio) e permite alternar janelas entre múltiplos monitores no Windows sem precisar arrastar com o mouse nem perder o atalho padrão `Alt + Tab`.

## Principais Recursos

- **Atalho rápido `Tab + Alt`:** segure `Tab` e toque em `Alt` para enviar a janela em foco para o próximo monitor (sem interferir no `Alt + Tab` padrão do Windows).
- **Circularidade automática:** ao atingir o último monitor, o próximo acionamento traz a janela de volta para o primeiro monitor.
- **Preserva posição proporcional e estado maximizado:** adapta coordenadas entre monitores de resoluções diferentes e restaura/maximiza janelas maximizadas corretamente no monitor de destino.
- **Detecção automática de monitores:** ativa o atalho automaticamente quando há 2 ou mais monitores conectados e pausa quando resta apenas 1 monitor.
- **Bandeja do sistema & Configurações:** menu na bandeja com **Status**, **Configurações** (iniciar com o Windows e exibir notificações) e **Sair**.
- **Instalador padrão do Windows:** instala em `%LOCALAPPDATA%\DisplayBridge`, cria atalhos opcionais, registra inicialização automática e aparece em **Configurações → Aplicativos → Aplicativos instalados** com desinstalador nativo (`--uninstall`).

## Download e Instalação (Windows)

Acesse a página oficial em **[displaybridge.vercel.app/#download](https://displaybridge.vercel.app/#download)** ou baixe diretamente pela **[Release v4.0.0](https://github.com/conrider3000/DisplayBridge/releases/latest)**:

| Pacote | Tipo | Tamanho | SHA-256 |
| --- | --- | --- | --- |
| **[Instalar_DisplayBridge_v4.exe](https://github.com/conrider3000/DisplayBridge/releases/latest/download/Instalar_DisplayBridge_v4.exe)** | Instalador Windows (Recomendado) | 34,0 MB | `E23C36A8A687CB31C35EB61F042FE03DB2DD4F1E9907C2954DD70596A1955D7C` |
| **[DisplayBridge_Portable.exe](https://github.com/conrider3000/DisplayBridge/releases/latest/download/DisplayBridge_Portable.exe)** | Executável Portátil | 18,7 MB | `9B3C3D461B1D0EFFFE3272140432EF9B602174F364AB2F78976C3FBBE01B01A2` |

> **Nota sobre Windows SmartScreen:** por ser um aplicativo gratuito sem certificado pago, o Windows pode exibir *"O Windows protegeu o computador"* na primeira execução. Clique em **Mais informações** → **Executar assim mesmo**.

## Estrutura do Projeto

```text
DisplayBridge/
├── index.html                  # Landing page profissional (Vercel)
├── README.md                   # Documentação do repositório
└── DisplayBridgeV4/
    ├── assets/                 # Ícones (.ico) e logos PNG usadas na UI e bandeja
    ├── dist/                   # Executáveis compilados (Instalador e Portátil)
    ├── generate_icon.py        # Gerador de ícones e assets a partir da logo fonte
    └── src/
        ├── __main__.py         # Ponto de entrada (--settings, --uninstall e app)
        ├── installer.py        # Instalador padrão em Tkinter/ttk
        ├── core/
        │   ├── monitor_watcher.py  # Monitoramento contínuo da contagem de telas
        │   └── window_manager.py   # Movimentação e escala de janelas entre monitores
        ├── input/
        │   └── keyboard_hook.py    # Leitura assíncrona do gatilho Tab + Alt
        ├── ui/
        │   ├── onboarding_ui.py    # Tela de boas-vindas
        │   ├── settings_ui.py      # Janela de configurações
        │   └── tray_icon.py        # Ícone e menu da bandeja (pystray)
        └── utils/
            ├── config.py           # Persistência em %APPDATA%\DisplayBridge\settings.json
            ├── logger.py           # Logs em %APPDATA%\DisplayBridge\debug.log
            ├── resources.py        # Resolução de assets em dev e PyInstaller
            └── uninstaller.py      # Desinstalação completa pelo Windows
```

## Executar a partir do Código-Fonte

Requisitos: Python 3 + `pywin32`, `pystray` e `Pillow`.

```powershell
cd DisplayBridgeV4
python src/__main__.py
```
