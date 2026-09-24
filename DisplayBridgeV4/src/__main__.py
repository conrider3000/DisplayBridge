import sys
import os
import threading
import ctypes

# Adiciona o diretorio atual no path para resolver imports internos quando executado cru
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.settings_ui import show_settings_ui
from ui.tray_icon import run_tray, update_tray_icon, _notify
from core.monitor_watcher import get_monitor_count, run_display_watcher
from input.keyboard_hook import start_action_worker, start_hook, stop_hook, queue_action, is_hook_active
from utils.logger import init_logger
from utils.config import load_settings
from ui.onboarding_ui import show_onboarding

def on_display_change(monitor_count):
    if monitor_count >= 2 and not is_hook_active():
        start_hook()
        update_tray_icon(True)
        _notify("✅ Segundo monitor detectado — DisplayBridge ativo", force=True)
    elif monitor_count < 2 and is_hook_active():
        stop_hook()
        update_tray_icon(False)
        _notify("⏸ Monitor desconectado — DisplayBridge pausado", force=True)

if __name__ == "__main__":
    if "--settings" in sys.argv:
        show_settings_ui()
        sys.exit(0)

    # Evita múltiplas instâncias
    mutex = ctypes.windll.kernel32.CreateMutexW(None, False, "DisplayBridge_v2_Mutex")
    if ctypes.windll.kernel32.GetLastError() == 183:
        sys.exit(0)

    init_logger()

    settings = load_settings()
    if settings.get("first_run", True):
        show_onboarding()

    # Thread 3: worker
    start_action_worker(notify_callback=_notify)

    # Thread 4: monitor watcher
    threading.Thread(target=run_display_watcher, args=(on_display_change,), daemon=True).start()

    # Thread 2: teclado
    if get_monitor_count() >= 2:
        start_hook()

    # Thread 1: tray icon
    run_tray(get_monitor_count, stop_hook, queue_action)
