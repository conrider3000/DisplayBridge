import os
import time

_log_file_path = "C:\\Users\\falac\\Documents\\DisplayBridge\\displaybridge_debug.txt"

def init_logger():
    # Garante que o arquivo de log seja limpo na inicialização
    try:
        if os.path.exists(_log_file_path):
            os.remove(_log_file_path)
    except Exception:
        pass

def log_debug(msg):
    try:
        with open(_log_file_path, "a", encoding="utf-8") as f:
            f.write(f"{time.strftime('%H:%M:%S')} - {msg}\n")
    except Exception:
        pass
