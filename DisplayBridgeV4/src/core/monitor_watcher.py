import ctypes
import ctypes.wintypes as wt
import win32api
from utils.logger import log_debug

WM_DISPLAYCHANGE = 0x007E
WM_DESTROY       = 0x0002
_WND_CLASS_NAME  = "DisplayBridgeWatcher"

def get_monitor_count():
    return len(win32api.EnumDisplayMonitors())

def _display_change_wnd_proc(hwnd, msg, wParam, lParam, cb_on_change):
    if msg == WM_DISPLAYCHANGE:
        if cb_on_change:
            cb_on_change(get_monitor_count())
    elif msg == WM_DESTROY:
        ctypes.windll.user32.PostQuitMessage(0)
    
    DefWindowProcW = ctypes.windll.user32.DefWindowProcW
    DefWindowProcW.argtypes = [wt.HWND, wt.UINT, wt.WPARAM, wt.LPARAM]
    DefWindowProcW.restype = ctypes.c_int64
    return DefWindowProcW(hwnd, msg, wParam, lParam)

def run_display_watcher(cb_on_change):
    def wnd_proc_wrapper(hwnd, msg, wParam, lParam):
        return _display_change_wnd_proc(hwnd, msg, wParam, lParam, cb_on_change)
        
    WNDPROCTYPE = ctypes.WINFUNCTYPE(ctypes.c_int64, wt.HWND, wt.UINT, wt.WPARAM, wt.LPARAM)
    wnd_proc_cb = WNDPROCTYPE(wnd_proc_wrapper)

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
