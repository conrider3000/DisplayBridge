"""
DisplayBridge v2.2
  Tab → Alt  : move a janela em foco para o próximo monitor
  Alt → Tab  : comportamento padrão do Windows (Alt+Tab)

  Arquitetura de threads:
    - Thread 1 (principal): pystray (ícone da bandeja)
    - Thread 2 (hook):      loop de mensagens dedicado ao WH_KEYBOARD_LL
    - Thread 3 (worker):    executa o movimento da janela sem bloquear o hook
    - Thread 4 (watcher):   janela oculta para detectar WM_DISPLAYCHANGE
"""

import sys
import queue
import threading
import ctypes
import ctypes.wintypes as wt
import os
import time
import json
import winreg

# ── Dependências visuais ──────────────────────────────
try:
    import win32gui
    import win32api
    import win32con
    import pystray
    from PIL import Image, ImageDraw
except ImportError as e:
    import tkinter as tk
    from tkinter import messagebox
    root = tk.Tk(); root.withdraw()
    messagebox.showerror(
        "DisplayBridge",
        f"Dependência faltando:\n{e}\n\nRode '1_instalar_dependencias.bat' primeiro."
    )
    sys.exit(1)


# ── Configurações e Registro ──────────────────────────
_settings_dir = os.path.join(os.environ.get("APPDATA", ""), "DisplayBridge")
_settings_file = os.path.join(_settings_dir, "settings.json")

def load_settings():
    default_settings = {
        "start_with_windows": True,
        "enable_notifications": True
    }
    if not os.path.exists(_settings_dir):
        try:
            os.makedirs(_settings_dir, exist_ok=True)
        except Exception:
            pass
    if os.path.exists(_settings_file):
        try:
            with open(_settings_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Garante chaves padrão
                for k, v in default_settings.items():
                    if k not in data:
                        data[k] = v
                return data
        except Exception:
            pass
    return default_settings

def save_settings(settings):
    if not os.path.exists(_settings_dir):
        try:
            os.makedirs(_settings_dir, exist_ok=True)
        except Exception:
            pass
    try:
        with open(_settings_file, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=4, ensure_ascii=False)
    except Exception:
        pass

def toggle_startup_registry(enable):
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE
        )
        if enable:
            exe_path = os.path.abspath(sys.argv[0])
            if exe_path.endswith(".py"):
                cmd = f'"{sys.executable}" "{exe_path}"'
            else:
                cmd = f'"{exe_path}"'
            winreg.SetValueEx(key, "DisplayBridge", 0, winreg.REG_SZ, cmd)
        else:
            try:
                winreg.DeleteValue(key, "DisplayBridge")
            except FileNotFoundError:
                pass
        winreg.CloseKey(key)
    except Exception as e:
        log_debug(f"Erro ao alterar registro do startup: {e}")

def show_settings_ui():
    import tkinter as tk
    
    settings = load_settings()
    
    root = tk.Tk()
    root.title("DisplayBridge - Configurações")
    root.configure(bg="#1c1c1e")
    
    width = 340
    height = 240
    
    try:
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        root.geometry(f"{width}x{height}+{x}+{y}")
    except Exception:
        root.geometry(f"{width}x{height}")
        
    root.resizable(False, False)
    
    system_font_bold = ("Segoe UI", 12, "bold")
    system_font_normal = ("Segoe UI", 10)
    system_font_caption = ("Segoe UI", 8)
    
    class MacOSToggle(tk.Canvas):
        def __init__(self, parent, initial_state=False, command=None):
            super().__init__(parent, width=44, height=24, bg="#2c2c2e", highlightthickness=0)
            self.command = command
            self.state = initial_state
            self.bind("<Button-1>", self.toggle)
            self.draw()

        def draw(self):
            self.delete("all")
            color = "#34c759" if self.state else "#3a3a3c"
            
            self.create_arc(0, 0, 24, 24, start=90, extent=180, fill=color, outline="")
            self.create_arc(20, 0, 44, 24, start=270, extent=180, fill=color, outline="")
            self.create_rectangle(12, 0, 32, 24, fill=color, outline="")
            
            knob_x = 32 if self.state else 12
            self.create_oval(knob_x-10, 2, knob_x+10, 22, fill="#ffffff", outline="")

        def toggle(self, event):
            self.state = not self.state
            self.draw()
            if self.command:
                self.command(self.state)
                
    header_frame = tk.Frame(root, bg="#1c1c1e")
    header_frame.pack(pady=(20, 15), fill="x", padx=20)
    
    icon_canvas = tk.Canvas(header_frame, width=32, height=32, bg="#1c1c1e", highlightthickness=0)
    icon_canvas.pack(side="left", padx=(0, 10))
    icon_canvas.create_oval(2, 2, 30, 30, fill="#0a84ff", outline="")
    icon_canvas.create_rectangle(8, 8, 24, 18, outline="#ffffff", width=2)
    icon_canvas.create_line(16, 18, 16, 22, fill="#ffffff", width=2)
    icon_canvas.create_line(12, 22, 20, 22, fill="#ffffff", width=2)
    
    title_frame = tk.Frame(header_frame, bg="#1c1c1e")
    title_frame.pack(side="left")
    
    lbl_title = tk.Label(title_frame, text="DisplayBridge", fg="#ffffff", bg="#1c1c1e", font=system_font_bold)
    lbl_title.pack(anchor="w")
    
    lbl_ver = tk.Label(title_frame, text="Configurações do Sistema", fg="#8e8e93", bg="#1c1c1e", font=system_font_normal)
    lbl_ver.pack(anchor="w")
    
    group_frame = tk.Frame(root, bg="#2c2c2e", bd=0)
    group_frame.pack(fill="x", padx=20, pady=5)
    
    def make_row(parent, title, caption, val, cmd, is_last=False):
        row = tk.Frame(parent, bg="#2c2c2e", height=50)
        row.pack(fill="x", padx=15, pady=8)
        
        txt_frame = tk.Frame(row, bg="#2c2c2e")
        txt_frame.pack(side="left", fill="both", expand=True)
        
        lbl_t = tk.Label(txt_frame, text=title, fg="#ffffff", bg="#2c2c2e", font=system_font_normal, anchor="w")
        lbl_t.pack(fill="x", anchor="w")
        
        lbl_c = tk.Label(txt_frame, text=caption, fg="#8e8e93", bg="#2c2c2e", font=system_font_caption, anchor="w")
        lbl_c.pack(fill="x", anchor="w")
        
        toggle = MacOSToggle(row, initial_state=val, command=cmd)
        toggle.pack(side="right", padx=(5, 0))
        
        if not is_last:
            sep = tk.Frame(parent, bg="#3a3a3c", height=1)
            sep.pack(fill="x", padx=15)
            
    def on_toggle_startup(state):
        settings["start_with_windows"] = state
        save_settings(settings)
        toggle_startup_registry(state)
        
    def on_toggle_notif(state):
        settings["enable_notifications"] = state
        save_settings(settings)
        
    make_row(group_frame, "Iniciar com o Computador", "Executar DisplayBridge ao ligar o PC", settings["start_with_windows"], on_toggle_startup)
    make_row(group_frame, "Exibir Notificações", "Mostrar aviso ao mover janelas", settings["enable_notifications"], on_toggle_notif, is_last=True)
    
    footer_frame = tk.Frame(root, bg="#1c1c1e")
    footer_frame.pack(fill="x", padx=20, pady=(15, 0))
    
    btn_close = tk.Button(
        footer_frame, 
        text="Fechar", 
        command=root.destroy, 
        bg="#0a84ff", 
        fg="#ffffff", 
        activebackground="#007aff", 
        activeforeground="#ffffff", 
        bd=0, 
        font=system_font_normal,
        padx=20,
        pady=5,
        cursor="hand2"
    )
    btn_close.pack(side="right")
    
    root.mainloop()



# ════════════════════════════════════════════════════════
#  FILA DE AÇÕES (desacopla hook do processamento)
# ════════════════════════════════════════════════════════

_action_queue = queue.SimpleQueue()


VK_ESCAPE = 0x1B

def _action_worker():
    """Thread 3: processa ações enfileiradas pelo hook sem bloqueá-lo."""
    while True:
        action = _action_queue.get()
        if action == "move":
            move_window_to_next_monitor()
        elif action == "quit":
            break


# ════════════════════════════════════════════════════════
#  HOOK DE TECLADO — Thread 2 dedicada
# ════════════════════════════════════════════════════════

WH_KEYBOARD_LL = 13
WM_KEYDOWN     = 0x0100
WM_SYSKEYDOWN  = 0x0104
HC_ACTION      = 0
VK_TAB         = 0x09
VK_MENU        = 0x12   # Tecla Alt
VK_LMENU       = 0xA4   # Alt Esquerdo
VK_RMENU       = 0xA5   # Alt Direito

# Constantes de eventos de teclado
WM_KEYUP       = 0x0101
WM_SYSKEYUP    = 0x0105

class KBDLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [
        ("vkCode",      wt.DWORD),
        ("scanCode",    wt.DWORD),
        ("flags",       wt.DWORD),
        ("time",        wt.DWORD),
        ("dwExtraInfo", ctypes.POINTER(wt.ULONG)),
    ]

HOOKPROC = ctypes.WINFUNCTYPE(ctypes.c_long, ctypes.c_int, wt.WPARAM, wt.LPARAM)

_hook_handle  = None
_hook_proc_cb = None
_hook_active  = False
_hook_tid     = None   # thread ID da thread do hook (para PostThreadMessage)
_tab_is_held  = False  # Máquina de estados: rastreia se o Tab está sendo segurado



_log_file_path = "C:\\Users\\falac\\Documents\\DisplayBridge\\displaybridge_debug.txt"

def log_debug(msg):
    try:
        with open(_log_file_path, "a", encoding="utf-8") as f:
            f.write(f"{time.strftime('%H:%M:%S')} - {msg}\n")
    except Exception as e:
        pass

# Garante que o arquivo de log seja limpo na inicialização
try:
    if os.path.exists(_log_file_path):
        os.remove(_log_file_path)
except Exception:
    pass


KEYEVENTF_KEYUP = 0x0002

def send_key_event(vk, down=True):
    flags = 0 if down else KEYEVENTF_KEYUP
    ctypes.windll.user32.keybd_event(vk, 0, flags, 0)

_keyboard_thread_active = False
_keyboard_thread_obj = None

def _keyboard_polling_loop():
    """Thread 2: Monitor de teclado assíncrono passivo (sem hooks globais).
    Lógica: se Tab é segurado primeiro, e depois Alt é pressionado, move a janela.
    Se Alt é pressionado primeiro, não faz nada (deixa o Windows abrir Alt+Tab nativo).
    """
    global _keyboard_thread_active
    log_debug("Monitor de teclado assíncrono iniciado com sucesso!")
    
    # Mapeamento de teclas virtuais
    VK_TAB = 0x09
    VK_MENU = 0x12
    
    tab_was_down = False
    
    while _keyboard_thread_active:
        time.sleep(0.01) # 10ms (0% de CPU)
        
        # Lê o estado atual físico das teclas
        tab_down = (ctypes.windll.user32.GetAsyncKeyState(VK_TAB) & 0x8000) != 0
        alt_down = (ctypes.windll.user32.GetAsyncKeyState(VK_MENU) & 0x8000) != 0
        
        # Rastreia a transição do Tab
        if tab_down and not tab_was_down:
            # Tab acabou de ser pressionado.
            # Se o Alt já estiver pressionado, é Alt+Tab nativo, então não fazemos nada.
            if not alt_down:
                tab_was_down = True
                log_debug("TAB pressionado primeiro. Aguardando ALT...")
        elif not tab_down and tab_was_down:
            # Tab foi solto
            tab_was_down = False
            log_debug("TAB solto.")
            
        # Se Tab está sendo segurado (iniciado antes do Alt) e o Alt é pressionado:
        if tab_was_down and alt_down:
            log_debug("==> GATILHO DETECTADO: TAB + ALT! Movendo janela...")
            _action_queue.put("move")
            
            # Aguarda o Alt ser solto para não repetir
            while (ctypes.windll.user32.GetAsyncKeyState(VK_MENU) & 0x8000) != 0:
                time.sleep(0.05)
            log_debug("ALT solto pelo usuário.")


def start_hook():
    global _keyboard_thread_active, _keyboard_thread_obj
    if _keyboard_thread_active:
        return
    _keyboard_thread_active = True
    _keyboard_thread_obj = threading.Thread(target=_keyboard_polling_loop, daemon=True)
    _keyboard_thread_obj.start()


def stop_hook():
    global _keyboard_thread_active
    _keyboard_thread_active = False


# ════════════════════════════════════════════════════════
#  DETECÇÃO DE MONITOR (Thread 4 — janela oculta)
# ════════════════════════════════════════════════════════

WM_DISPLAYCHANGE = 0x007E
WM_DESTROY       = 0x0002
_WND_CLASS_NAME  = "DisplayBridgeWatcher"


def get_monitor_count():
    return len(win32api.EnumDisplayMonitors())


def _display_change_wnd_proc(hwnd, msg, wParam, lParam):
    if msg == WM_DISPLAYCHANGE:
        num = get_monitor_count()
        if num >= 2 and not _keyboard_thread_active:
            start_hook()
            _update_tray_icon()
            _notify("✅ Segundo monitor detectado — DisplayBridge ativo", force=True)
        elif num < 2 and _keyboard_thread_active:
            stop_hook()
            _update_tray_icon()
            _notify("⏸ Monitor desconectado — DisplayBridge pausado", force=True)
    elif msg == WM_DESTROY:
        ctypes.windll.user32.PostQuitMessage(0)
    # Define os tipos de DefWindowProcW para evitar problemas de casting em 64-bit
    DefWindowProcW = ctypes.windll.user32.DefWindowProcW
    DefWindowProcW.argtypes = [wt.HWND, wt.UINT, wt.WPARAM, wt.LPARAM]
    DefWindowProcW.restype = ctypes.c_int64
    return DefWindowProcW(hwnd, msg, wParam, lParam)


def _run_display_watcher():
    """Thread 4: janela de mensagens oculta para capturar WM_DISPLAYCHANGE."""
    # Retorno de wndproc no Win64 é INT_PTR (LRESULT), que mapeia para c_int64 ou c_ssize_t
    WNDPROCTYPE = ctypes.WINFUNCTYPE(
        ctypes.c_int64, wt.HWND, wt.UINT, wt.WPARAM, wt.LPARAM
    )
    wnd_proc_cb = WNDPROCTYPE(_display_change_wnd_proc)

    class WNDCLASSW(ctypes.Structure):
        _fields_ = [
            ("style",         wt.UINT),
            ("lpfnWndProc",   ctypes.c_void_p),
            ("cbClsExtra",    ctypes.c_int),
            ("cbWndExtra",    ctypes.c_int),
            ("hInstance",     wt.HANDLE),
            ("hIcon",         wt.HANDLE),
            ("hCursor",       wt.HANDLE),
            ("hbrBackground", wt.HANDLE),
            ("lpszMenuName",  wt.LPCWSTR),
            ("lpszClassName", wt.LPCWSTR),
        ]

    h_instance = ctypes.windll.kernel32.GetModuleHandleW(None)
    wc = WNDCLASSW()
    wc.lpfnWndProc   = ctypes.cast(wnd_proc_cb, ctypes.c_void_p)
    wc.hInstance     = h_instance
    wc.lpszClassName = _WND_CLASS_NAME
    ctypes.windll.user32.RegisterClassW(ctypes.byref(wc))

    HWND_MESSAGE = ctypes.c_void_p(-3)
    hwnd = ctypes.windll.user32.CreateWindowExW(
        0, _WND_CLASS_NAME, "DisplayBridgeWatcher",
        0, 0, 0, 0, 0,
        HWND_MESSAGE, None, h_instance, None
    )

    msg = wt.MSG()
    while ctypes.windll.user32.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
        ctypes.windll.user32.TranslateMessage(ctypes.byref(msg))
        ctypes.windll.user32.DispatchMessageW(ctypes.byref(msg))


# ════════════════════════════════════════════════════════
#  MOVER JANELAS
# ════════════════════════════════════════════════════════

def move_window_to_next_monitor():
    try:
        hwnd = win32gui.GetForegroundWindow()
        if not hwnd:
            log_debug("move: hwnd é Nulo")
            return
        
        class_name = win32gui.GetClassName(hwnd)
        if class_name in ("Shell_TrayWnd", "Progman", "WorkerW"):
            log_debug(f"move: ignorando classe de sistema: {class_name}")
            return

        # Envia a tecla ESCAPE imediatamente para cancelar o menu do ALT na janela atual,
        # liberando o foco antes de mover a janela.
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

        # Para que a janela vá e se torne a principal na frente de tudo:
        # 1. Removemos SWP_NOACTIVATE (assim ela ganha foco de ativação)
        # 2. Mantemos SWP_ASYNCWINDOWPOS (0x4000) para evitar travamentos
        # 3. Adicionamos SWP_SHOWWINDOW (0x0040) para forçar a janela a aparecer no topo
        SWP_FLAGS = 0x0040 | 0x4000

        log_debug(f"move: movendo janela {hwnd} ('{win32gui.GetWindowText(hwnd)[:20]}') para monitor {nxt_idx + 1}. Maximized: {maximized}")

        # Definimos o primeiro parâmetro de Z-order como HWND_TOP (0) para trazer para a frente
        HWND_TOP = 0

        if maximized:
            rc = placement[4]
            wx, wy = rc[0], rc[1]
            ww, wh = rc[2] - rc[0], rc[3] - rc[1]
            nx = scale(wx, cur_rect[0], cw, nxt_rect[0], nw)
            ny = scale(wy, cur_rect[1], ch, nxt_rect[1], nh)
            
            # ShowWindowAsync evita travamentos caso a janela não responda imediatamente
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

        # Garante o foco no topo (traz a janela para frente)
        try:
            win32gui.BringWindowToTop(hwnd)
            win32gui.SetForegroundWindow(hwnd)
        except Exception as fe:
            log_debug(f"Aviso ao trazer para frente: {fe}")

        title = win32gui.GetWindowText(hwnd) or "Janela"
        log_debug(f"move: Sucesso! Notificando: {title[:20]} -> Monitor {nxt_idx + 1}")
        _notify(f'"{title[:30]}" → Monitor {nxt_idx + 1}')
    except Exception as e:
        import traceback
        log_debug(f"move ERRO: {e}\n{traceback.format_exc()}")


# ════════════════════════════════════════════════════════
#  BANDEJA DO SISTEMA (Thread principal)
# ════════════════════════════════════════════════════════

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
    bg  = (12, 68, 124) if active else (80, 80, 80)
    d.rounded_rectangle([0, 0, sz-1, sz-1], radius=14, fill=bg)
    W = (255, 255, 255)
    G = (150, 150, 150) if not active else W
    d.rounded_rectangle([5, 16, 27, 38],  radius=3, outline=W, width=2)
    d.rounded_rectangle([14, 38, 18, 44], radius=1, fill=W)
    d.rounded_rectangle([8,  44, 24, 47], radius=1, fill=W)
    d.rounded_rectangle([37, 16, 59, 38], radius=3, outline=G, width=2)
    d.rounded_rectangle([46, 38, 50, 44], radius=1, fill=G)
    d.rounded_rectangle([40, 44, 56, 47], radius=1, fill=G)
    d.ellipse([29, 25, 35, 31], fill=W)
    return img


def _update_tray_icon():
    if _tray:
        try:
            active      = _keyboard_thread_active
            _tray.icon  = _make_icon(active)
            _tray.title = ("DisplayBridge  |  Tab+Alt → mover janela  ✅"
                           if active else
                           "DisplayBridge  |  Aguardando 2º monitor... ⏸")
        except Exception:
            pass


def _on_quit(icon, item):
    stop_hook()
    _action_queue.put("quit")
    icon.stop()
    sys.exit(0)


def _on_about(icon, item):
    num = get_monitor_count()
    if num >= 2:
        _notify(f"✅ Ativo  |  {num} monitores  |  Tab+Alt → próxima tela", force=True)
    else:
        _notify(f"⏸ Pausado  |  Apenas {num} monitor conectado", force=True)


def _on_settings(icon, item):
    try:
        import subprocess
        exe_path = os.path.abspath(sys.argv[0])
        if exe_path.endswith(".py"):
            subprocess.Popen([sys.executable, exe_path, "--settings"])
        else:
            subprocess.Popen([exe_path, "--settings"])
    except Exception as e:
        log_debug(f"Erro ao abrir configuracoes: {e}")

def run_tray():
    global _tray
    active = get_monitor_count() >= 2
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


# ════════════════════════════════════════════════════════
#  PONTO DE ENTRADA
# ════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys
    if "--settings" in sys.argv:
        show_settings_ui()
        sys.exit(0)

    # Evita múltiplas instâncias do daemon
    mutex = ctypes.windll.kernel32.CreateMutexW(None, False, "DisplayBridge_v2_Mutex")
    if ctypes.windll.kernel32.GetLastError() == 183:
        sys.exit(0)

    # Thread 3: worker que processa movimentos de janela
    threading.Thread(target=_action_worker, daemon=True).start()

    # Thread 4: detecta conexão/desconexão de monitores
    threading.Thread(target=_run_display_watcher, daemon=True).start()

    # Thread 2: hook de teclado (somente se já há 2+ monitores)
    if get_monitor_count() >= 2:
        start_hook()

    # Thread principal: bandeja do sistema
    run_tray()
