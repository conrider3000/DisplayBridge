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

_RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
_APPROVED_KEY = r"Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run"


def _startup_command():
    """Comando que o Windows deve executar no logon."""
    if getattr(sys, "frozen", False):
        # Executável PyInstaller: sys.executable é o caminho real do .exe
        return f'"{os.path.abspath(sys.executable)}"'
    # Execução via Python: usa pythonw para não abrir console
    main_py = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "__main__.py"))
    pyw = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
    interpreter = pyw if os.path.exists(pyw) else sys.executable
    return f'"{interpreter}" "{main_py}"'


def _mark_startup_approved():
    """Reativa a entrada caso tenha sido desativada no Gerenciador de Tarefas."""
    try:
        key = winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, _APPROVED_KEY, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "DisplayBridge", 0, winreg.REG_BINARY, bytes([2] + [0] * 11))
        winreg.CloseKey(key)
    except Exception as e:
        log_debug(f"Erro ao marcar StartupApproved: {e}")


def ensure_startup_registry(settings):
    """Chamado a cada inicialização: mantém o registro coerente com a configuração.

    Corrige caminhos antigos (ex.: executável movido/reinstalado) e reativa a
    entrada se o usuário quer iniciar com o Windows.
    """
    if not getattr(sys, "frozen", False):
        return  # Em desenvolvimento não mexe no registro automaticamente
    toggle_startup_registry(bool(settings.get("start_with_windows", True)))


def toggle_startup_registry(enable):
    try:
        key = winreg.CreateKeyEx(
            winreg.HKEY_CURRENT_USER,
            _RUN_KEY,
            0,
            winreg.KEY_SET_VALUE
        )
        if enable:
            cmd = _startup_command()
            winreg.SetValueEx(key, "DisplayBridge", 0, winreg.REG_SZ, cmd)
            log_debug(f"Startup registrado: {cmd}")
            _mark_startup_approved()
        else:
            try:
                winreg.DeleteValue(key, "DisplayBridge")
            except FileNotFoundError:
                pass
        winreg.CloseKey(key)
    except Exception as e:
        log_debug(f"Erro ao alterar registro do startup: {e}")
