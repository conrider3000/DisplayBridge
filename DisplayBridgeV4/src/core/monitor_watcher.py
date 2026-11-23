import time
import win32api
from utils.logger import log_debug

_POLL_INTERVAL = 2.0  # segundos


def get_monitor_count():
    try:
        return len(win32api.EnumDisplayMonitors())
    except Exception as e:
        log_debug(f"Erro ao contar monitores: {e}")
        return 1


def run_display_watcher(cb_on_change):
    """Observa a quantidade de monitores por polling.

    Antes usávamos uma janela message-only (HWND_MESSAGE) esperando
    WM_DISPLAYCHANGE, mas o Windows não envia mensagens de broadcast para
    janelas message-only. Resultado: quando o app iniciava com o Windows antes
    do 2º monitor ser detectado, ele nunca era ativado. O polling é barato e
    funciona sempre.
    """
    last = get_monitor_count()
    log_debug(f"Watcher iniciado. Monitores: {last}")
    # Dispara uma vez para sincronizar o estado inicial
    try:
        cb_on_change(last)
    except Exception as e:
        log_debug(f"Erro no callback do watcher: {e}")

    while True:
        time.sleep(_POLL_INTERVAL)
        count = get_monitor_count()
        if count != last:
            log_debug(f"Mudança de monitores: {last} -> {count}")
            last = count
            try:
                cb_on_change(count)
            except Exception as e:
                log_debug(f"Erro no callback do watcher: {e}")
