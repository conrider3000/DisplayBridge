import time
import sys
import os
import pystray
from PIL import Image, ImageDraw
from utils.logger import log_debug
from utils.config import load_settings

_tray = None
_last_notify_time = 0.0
_notify_cooldown = 3.0

def _notify(msg, force=False):
    global _last_notify_time
    if _tray:
        settings = load_settings()
        if not settings.get("enable_notifications", True):
            log_debug("notify: ignorado (notificações desativas nas configurações)")
            return

        now = time.time()
        if not force and (now - _last_notify_time < _notify_cooldown):
            log_debug(f"notify: ignorado (cooldown): {msg}")
            return
        
        if not force:
            _last_notify_time = now

        try:
            import pystray._util.win32 as pystray_win32
            uFlags = 0x00000010 | 0x00000040  # NIF_INFO | NIF_REALTIME
            dwInfoFlags = 0x00000001 | 0x00000010  # NIIF_INFO | NIIF_NOSOUND
            _tray._message(
                pystray_win32.NIM_MODIFY,
                uFlags,
                szInfo=msg,
                szInfoTitle="DisplayBridge",
                dwInfoFlags=dwInfoFlags
            )
        except Exception as e:
            log_debug(f"notify ERRO: {e}")

def _make_icon(active=True):
    sz  = 64
    img = Image.new("RGBA", (sz, sz), (0, 0, 0, 0))
    d   = ImageDraw.Draw(img)
    color = (139, 195, 74, 255) if active else (150, 150, 150, 255)
    
    # Left monitor
    d.rounded_rectangle([4, 16, 26, 48], radius=2, fill=color)
    # Right monitor
    d.rounded_rectangle([38, 16, 60, 48], radius=2, fill=color)
    # Center circle
    d.ellipse([24, 24, 40, 40], outline=color, width=3)
    return img

def update_tray_icon(is_active):
    if _tray:
        try:
            _tray.icon  = _make_icon(is_active)
            _tray.title = ("DisplayBridge  |  Tab+Alt → mover janela  ✅"
                           if is_active else
                           "DisplayBridge  |  Aguardando 2º monitor... ⏸")
        except Exception:
            pass

def _on_settings(icon, item):
    try:
        import subprocess
        # Get absolute path to the base directory, regardless of how it was started
        if getattr(sys, 'frozen', False):
            exe_path = sys.executable
            subprocess.Popen([exe_path, "--settings"])
        else:
            # We are in python src/ folder, so __main__.py is the entry point
            entry_point = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "__main__.py"))
            subprocess.Popen([sys.executable, entry_point, "--settings"])
    except Exception as e:
        log_debug(f"Erro ao abrir configuracoes: {e}")

def run_tray(get_monitor_count_fn, stop_hook_fn, put_action_fn):
    global _tray

    def _on_quit(icon, item):
        stop_hook_fn()
        put_action_fn("quit")
        icon.stop()
        sys.exit(0)

    def _on_about(icon, item):
        num = get_monitor_count_fn()
        if num >= 2:
            _notify(f"✅ Ativo  |  {num} monitores  |  Tab+Alt → próxima tela", force=True)
        else:
            _notify(f"⏸ Pausado  |  Apenas {num} monitor conectado", force=True)

    active = get_monitor_count_fn() >= 2
    _tray = pystray.Icon(
        name  = "DisplayBridge",
        icon  = _make_icon(active),
        title = ("DisplayBridge  |  Tab+Alt → mover janela  ✅"
                 if active else
                 "DisplayBridge  |  Aguardando 2º monitor... ⏸"),
        menu  = pystray.Menu(
            pystray.MenuItem("ℹ️  Status", _on_about),
            pystray.MenuItem("⚙️  Configurações", _on_settings),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("❌  Sair", _on_quit),
        ),
    )
    _tray.run()
