import os
import sys
import json
import winreg
from utils.logger import log_debug

_settings_dir = os.path.join(os.environ.get("APPDATA", ""), "DisplayBridge")
_settings_file = os.path.join(_settings_dir, "settings.json")

def load_settings():
    default_settings = {
        "start_with_windows": True,
        "enable_notifications": True,
        "first_run": True
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
