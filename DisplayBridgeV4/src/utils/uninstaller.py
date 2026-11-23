import os
import sys
import time
import shutil
import base64
import subprocess
import winreg
import tkinter as tk
from tkinter import messagebox
import win32com.client
from utils.resources import resource_path

_UNINSTALL_KEY = r"Software\Microsoft\Windows\CurrentVersion\Uninstall\DisplayBridge"
_RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
_APPROVED_KEY = r"Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run"


def _delete_reg_value(root, subkey, value_name):
    try:
        with winreg.OpenKey(root, subkey, 0, winreg.KEY_SET_VALUE) as key:
            winreg.DeleteValue(key, value_name)
    except FileNotFoundError:
        pass
    except Exception:
        pass


def _delete_reg_key(root, subkey):
    try:
        winreg.DeleteKey(root, subkey)
    except FileNotFoundError:
        pass
    except Exception:
        pass


def _get_install_dir():
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, _UNINSTALL_KEY, 0, winreg.KEY_READ) as key:
            val, _ = winreg.QueryValueEx(key, "InstallLocation")
            if val and os.path.isdir(val):
                return os.path.abspath(val)
    except Exception:
        pass

    if getattr(sys, "frozen", False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.join(os.environ.get("LOCALAPPDATA", ""), "DisplayBridge")


def _remove_shortcuts():
    candidates = set()
    try:
        shell = win32com.client.Dispatch("WScript.Shell")
        desktop = shell.SpecialFolders("Desktop")
        programs = shell.SpecialFolders("Programs")
        if desktop:
            candidates.add(os.path.join(desktop, "DisplayBridge.lnk"))
        if programs:
            candidates.add(os.path.join(programs, "DisplayBridge.lnk"))
    except Exception:
        pass

    userprofile = os.environ.get("USERPROFILE", "")
    appdata = os.environ.get("APPDATA", "")
    if userprofile:
        candidates.add(os.path.join(userprofile, "Desktop", "DisplayBridge.lnk"))
    if appdata:
        candidates.add(os.path.join(appdata, r"Microsoft\Windows\Start Menu\Programs", "DisplayBridge.lnk"))

    for path in candidates:
        if os.path.exists(path):
            try:
                os.remove(path)
            except Exception:
                pass


def run_uninstall(silent=False):
    root = None
    if not silent:
        root = tk.Tk()
        root.withdraw()
        try:
            root.iconbitmap(resource_path(os.path.join("assets", "icon.ico")))
        except Exception:
            pass
        confirmed = messagebox.askyesno(
            "Desinstalar DisplayBridge",
            "Deseja realmente desinstalar o DisplayBridge do seu computador?",
            parent=root,
        )
        if not confirmed:
            root.destroy()
            return

    install_dir = _get_install_dir()

    # Encerra outras instâncias em execução sem matar o próprio desinstalador
    try:
        creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        subprocess.run(
            ["taskkill", "/F", "/FI", f"PID ne {os.getpid()}", "/IM", "DisplayBridge.exe"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=creationflags,
            timeout=5,
        )
        time.sleep(0.4)
    except Exception:
        pass

    # Remove entradas de inicialização e desinstalação no Registro
    _delete_reg_value(winreg.HKEY_CURRENT_USER, _RUN_KEY, "DisplayBridge")
    _delete_reg_value(winreg.HKEY_CURRENT_USER, _APPROVED_KEY, "DisplayBridge")
    _delete_reg_key(winreg.HKEY_CURRENT_USER, _UNINSTALL_KEY)

    # Remove atalhos da Área de Trabalho e Menu Iniciar
    _remove_shortcuts()

    # Remove dados de configuração e log em %APPDATA%\DisplayBridge
    appdata_dir = os.path.join(os.environ.get("APPDATA", ""), "DisplayBridge")
    if appdata_dir and os.path.isdir(appdata_dir):
        shutil.rmtree(appdata_dir, ignore_errors=True)

    # Agenda remoção do executável e da pasta após este processo encerrar
    if getattr(sys, "frozen", False) and install_dir and os.path.isdir(install_dir):
        exe_path = os.path.join(install_dir, "DisplayBridge.exe")
        temp_cwd = os.environ.get("TEMP", os.path.expanduser("~"))
        is_dedicated_dir = os.path.basename(install_dir.rstrip("\\/")).lower() == "displaybridge"
        escaped_dir = install_dir.replace("'", "''")
        escaped_exe = exe_path.replace("'", "''")

        if is_dedicated_dir:
            ps_script = (
                f"$d = '{escaped_dir}'; "
                f"for ($i = 0; $i -lt 15; $i++) {{ "
                f"Start-Sleep -Milliseconds 600; "
                f"Remove-Item -LiteralPath $d -Recurse -Force -ErrorAction SilentlyContinue; "
                f"if (-not (Test-Path -LiteralPath $d)) {{ break }} "
                f"}}"
            )
        else:
            ps_script = (
                f"$f = '{escaped_exe}'; "
                f"for ($i = 0; $i -lt 15; $i++) {{ "
                f"Start-Sleep -Milliseconds 600; "
                f"Remove-Item -LiteralPath $f -Force -ErrorAction SilentlyContinue; "
                f"if (-not (Test-Path -LiteralPath $f)) {{ break }} "
                f"}}"
            )

        encoded = base64.b64encode(ps_script.encode("utf-16-le")).decode("ascii")
        try:
            creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
            subprocess.Popen(
                [
                    "powershell.exe",
                    "-NoProfile",
                    "-NonInteractive",
                    "-WindowStyle",
                    "Hidden",
                    "-EncodedCommand",
                    encoded,
                ],
                cwd=temp_cwd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=creationflags,
            )
        except Exception:
            pass

    if not silent and root is not None:
        messagebox.showinfo(
            "DisplayBridge Desinstalado",
            "O DisplayBridge foi removido com sucesso do seu computador.",
            parent=root,
        )
        root.destroy()
