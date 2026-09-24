import ctypes
import win32gui
import win32api
import win32con
from utils.logger import log_debug

VK_ESCAPE = 0x1B
KEYEVENTF_KEYUP = 0x0002

def send_key_event(vk, down=True):
    flags = 0 if down else KEYEVENTF_KEYUP
    ctypes.windll.user32.keybd_event(vk, 0, flags, 0)

def move_window_to_next_monitor(notify_callback):
    try:
        hwnd = win32gui.GetForegroundWindow()
        if not hwnd:
            log_debug("move: hwnd é Nulo")
            return
        
        class_name = win32gui.GetClassName(hwnd)
        if class_name in ("Shell_TrayWnd", "Progman", "WorkerW"):
            log_debug(f"move: ignorando classe de sistema: {class_name}")
            return

        # Envia ESCAPE para cancelar o menu do ALT
        send_key_event(VK_ESCAPE, down=True)
        send_key_event(VK_ESCAPE, down=False)

        monitors = win32api.EnumDisplayMonitors()
        log_debug(f"move: detectados {len(monitors)} monitores")
        if len(monitors) < 2:
            return

        hmon_current = win32api.MonitorFromWindow(hwnd, win32con.MONITOR_DEFAULTTONEAREST)
        monitor_handles = [m[0] for m in monitors]
        try:
            cur_idx = monitor_handles.index(hmon_current)
        except ValueError:
            cur_idx = 0

        nxt_idx  = (cur_idx + 1) % len(monitors)
        cur_info = win32api.GetMonitorInfo(hmon_current)
        nxt_info = win32api.GetMonitorInfo(monitor_handles[nxt_idx])
        cur_rect = cur_info['Monitor']
        nxt_rect = nxt_info['Monitor']

        placement = win32gui.GetWindowPlacement(hwnd)
        maximized = placement[1] == win32con.SW_SHOWMAXIMIZED

        def scale(val, old_origin, old_size, new_origin, new_size):
            return new_origin + int((val - old_origin) / max(old_size, 1) * new_size)

        cw = cur_rect[2] - cur_rect[0]
        ch = cur_rect[3] - cur_rect[1]
        nw = nxt_rect[2] - nxt_rect[0]
        nh = nxt_rect[3] - nxt_rect[1]

        SWP_FLAGS = 0x0040 | 0x4000
        HWND_TOP = 0

        log_debug(f"move: movendo janela {hwnd} ('{win32gui.GetWindowText(hwnd)[:20]}') para monitor {nxt_idx + 1}. Maximized: {maximized}")

        if maximized:
            rc = placement[4]
            wx, wy = rc[0], rc[1]
            ww, wh = rc[2] - rc[0], rc[3] - rc[1]
            nx = scale(wx, cur_rect[0], cw, nxt_rect[0], nw)
            ny = scale(wy, cur_rect[1], ch, nxt_rect[1], nh)
            
            ctypes.windll.user32.ShowWindowAsync(hwnd, win32con.SW_RESTORE)
            win32gui.SetWindowPos(hwnd, HWND_TOP, nx, ny, ww, wh, SWP_FLAGS)
            ctypes.windll.user32.ShowWindowAsync(hwnd, win32con.SW_MAXIMIZE)
        else:
            rect = win32gui.GetWindowRect(hwnd)
            wx, wy = rect[0], rect[1]
            ww, wh = rect[2] - rect[0], rect[3] - rect[1]
            nx = scale(wx, cur_rect[0], cw, nxt_rect[0], nw)
            ny = scale(wy, cur_rect[1], ch, nxt_rect[1], nh)
            win32gui.SetWindowPos(hwnd, HWND_TOP, nx, ny, ww, wh, SWP_FLAGS)

        try:
            win32gui.BringWindowToTop(hwnd)
            win32gui.SetForegroundWindow(hwnd)
        except Exception as fe:
            log_debug(f"Aviso ao trazer para frente: {fe}")

        title = win32gui.GetWindowText(hwnd) or "Janela"
        log_debug(f"move: Sucesso! Notificando: {title[:20]} -> Monitor {nxt_idx + 1}")
        if notify_callback:
            notify_callback(f'"{title[:30]}" → Monitor {nxt_idx + 1}')
    except Exception as e:
        import traceback
        log_debug(f"move ERRO: {e}\n{traceback.format_exc()}")
