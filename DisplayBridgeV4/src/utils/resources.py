import os
import sys


def resource_path(relative_path):
    """Resolve o caminho de assets tanto em desenvolvimento quanto no .exe do PyInstaller."""
    if hasattr(sys, "_MEIPASS"):
        base_dir = sys._MEIPASS
    else:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    return os.path.join(base_dir, relative_path)
