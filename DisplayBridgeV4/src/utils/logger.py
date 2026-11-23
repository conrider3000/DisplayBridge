import os
import time

_log_dir = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "DisplayBridge")
_log_file_path = os.path.join(_log_dir, "debug.log")


def init_logger():
    # Garante que a pasta exista e que o log seja limpo na inicialização
    try:
        os.makedirs(_log_dir, exist_ok=True)
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
