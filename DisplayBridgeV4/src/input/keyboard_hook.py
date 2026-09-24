import time
import threading
import ctypes
import queue
from utils.logger import log_debug
from core.window_manager import move_window_to_next_monitor

_action_queue = queue.SimpleQueue()
_keyboard_thread_active = False
_keyboard_thread_obj = None

def _action_worker(notify_callback):
    """Thread 3: processa ações enfileiradas pelo hook sem bloqueá-lo."""
    while True:
        action = _action_queue.get()
        if action == "move":
            move_window_to_next_monitor(notify_callback)
        elif action == "quit":
            break

def start_action_worker(notify_callback):
    threading.Thread(target=_action_worker, args=(notify_callback,), daemon=True).start()

def queue_action(action):
    _action_queue.put(action)

def _keyboard_polling_loop():
    global _keyboard_thread_active
    log_debug("Monitor de teclado assíncrono iniciado com sucesso!")
    
    VK_TAB = 0x09
    VK_MENU = 0x12
    tab_was_down = False
    
    while _keyboard_thread_active:
        time.sleep(0.01) # 10ms
        
        tab_down = (ctypes.windll.user32.GetAsyncKeyState(VK_TAB) & 0x8000) != 0
        alt_down = (ctypes.windll.user32.GetAsyncKeyState(VK_MENU) & 0x8000) != 0
        
        if tab_down and not tab_was_down:
            if not alt_down:
                tab_was_down = True
                log_debug("TAB pressionado primeiro. Aguardando ALT...")
        elif not tab_down and tab_was_down:
            tab_was_down = False
            log_debug("TAB solto.")
            
        if tab_was_down and alt_down:
            log_debug("==> GATILHO DETECTADO: TAB + ALT! Movendo janela...")
            queue_action("move")
            
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

def is_hook_active():
    return _keyboard_thread_active
