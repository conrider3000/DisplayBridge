import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys
import time
import shutil
import json
import subprocess
import winreg
import win32com.client


def _asset_path(filename):
    if hasattr(sys, "_MEIPASS"):
        base = sys._MEIPASS
    else:
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return os.path.join(base, "assets", filename)


class StandardInstaller(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Instalação do DisplayBridge 4.0")
        self.geometry("520x380")
        self.resizable(False, False)

        try:
            self.iconbitmap(_asset_path("icon.ico"))
        except Exception:
            pass

        self.logo_80 = None
        self.logo_48 = None
        try:
            self.logo_80 = tk.PhotoImage(file=_asset_path("logo_80.png"))
        except Exception:
            pass
        try:
            self.logo_48 = tk.PhotoImage(file=_asset_path("logo_48.png"))
        except Exception:
            pass

        # Tema nativo do Windows
        style = ttk.Style(self)
        try:
            style.theme_use("vista")
        except Exception:
            pass

        self.current_step = 0
        self.install_path = tk.StringVar(
            value=os.path.join(os.environ.get("LOCALAPPDATA", ""), "DisplayBridge")
        )
        self.create_desktop = tk.BooleanVar(value=True)
        self.create_start = tk.BooleanVar(value=True)
        self.start_with_windows = tk.BooleanVar(value=True)
        self.launch_after_install = tk.BooleanVar(value=True)

        self.pages = []

        self.create_ui()
        self.show_page(0)

    def _add_page_header(self, frame, title_text, subtitle_text=None):
        header = tk.Frame(frame, bg="white")
        header.pack(fill=tk.X, padx=20, pady=(16, 10))

        text_col = tk.Frame(header, bg="white")
        text_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        lbl_title = tk.Label(
            text_col,
            text=title_text,
            font=("Segoe UI", 12, "bold"),
            bg="white",
            anchor="w",
        )
        lbl_title.pack(fill=tk.X)

        if subtitle_text:
            lbl_sub = tk.Label(
                text_col,
                text=subtitle_text,
                font=("Segoe UI", 9),
                fg="#555555",
                bg="white",
                anchor="w",
            )
            lbl_sub.pack(fill=tk.X, pady=(2, 0))

        if self.logo_48 is not None:
            tk.Label(header, image=self.logo_48, bg="white", bd=0).pack(
                side=tk.RIGHT, padx=(10, 0)
            )

        ttk.Separator(frame, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=20, pady=(0, 12))

    def create_ui(self):
        # Container Principal
        self.main_container = tk.Frame(self, bg="white")
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # Barra inferior cinza com botões
        self.bottom_bar = tk.Frame(self, bg="#f0f0f0", height=50)
        self.bottom_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Linha separadora
        ttk.Separator(self, orient=tk.HORIZONTAL).pack(side=tk.BOTTOM, fill=tk.X)

        # Botões
        self.btn_cancel = ttk.Button(self.bottom_bar, text="Cancelar", command=self.destroy)
        self.btn_cancel.pack(side=tk.RIGHT, padx=10, pady=10)

        self.btn_next = ttk.Button(self.bottom_bar, text="Avançar >", command=self.next_page)
        self.btn_next.pack(side=tk.RIGHT, padx=10, pady=10)

        self.btn_back = ttk.Button(self.bottom_bar, text="< Voltar", command=self.prev_page)
        self.btn_back.pack(side=tk.RIGHT, pady=10)

        # Criação das Páginas
        self.pages.append(self.create_page_welcome())
        self.pages.append(self.create_page_path())
        self.pages.append(self.create_page_options())
        self.pages.append(self.create_page_progress())
        self.pages.append(self.create_page_done())

    def create_page_welcome(self):
        frame = tk.Frame(self.main_container, bg="white")

        body = tk.Frame(frame, bg="white")
        body.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        if self.logo_80 is not None:
            left_col = tk.Frame(body, bg="white")
            left_col.pack(side=tk.LEFT, anchor="n", padx=(4, 18), pady=(6, 0))
            tk.Label(left_col, image=self.logo_80, bg="white", bd=0).pack()

        right_col = tk.Frame(body, bg="white")
        right_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        lbl_title = tk.Label(
            right_col,
            text="Bem-vindo ao Instalador do DisplayBridge",
            font=("Segoe UI", 14, "bold"),
            bg="white",
            anchor="w",
            justify="left",
            wraplength=360,
        )
        lbl_title.pack(fill=tk.X, pady=(0, 12))

        txt = (
            "Este assistente guiará você na instalação do DisplayBridge versão 4.0 no seu computador.\n\n"
            "É recomendado que você feche outras instâncias do aplicativo antes de continuar.\n\n"
            "Clique em Avançar para continuar ou Cancelar para sair do instalador."
        )
        lbl_desc = tk.Label(
            right_col,
            text=txt,
            font=("Segoe UI", 10),
            bg="white",
            justify="left",
            anchor="nw",
            wraplength=360,
        )
        lbl_desc.pack(fill=tk.BOTH, expand=True)
        return frame

    def create_page_path(self):
        frame = tk.Frame(self.main_container, bg="white")
        self._add_page_header(
            frame,
            "Selecione o Local de Instalação",
            "Onde o DisplayBridge deve ser instalado?",
        )

        path_frame = tk.Frame(frame, bg="white")
        path_frame.pack(fill=tk.X, padx=20, pady=15)

        entry = ttk.Entry(path_frame, textvariable=self.install_path)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=3)

        def browse():
            folder = filedialog.askdirectory(initialdir=self.install_path.get())
            if folder:
                self.install_path.set(os.path.join(folder, "DisplayBridge"))

        btn_browse = ttk.Button(path_frame, text="Procurar...", command=browse)
        btn_browse.pack(side=tk.LEFT, padx=(10, 0))

        return frame

    def create_page_options(self):
        frame = tk.Frame(self.main_container, bg="white")
        self._add_page_header(
            frame,
            "Selecionar Tarefas Adicionais",
            "Quais tarefas adicionais devem ser executadas?",
        )

        opts_frame = tk.Frame(frame, bg="white")
        opts_frame.pack(fill=tk.BOTH, expand=True, padx=32, pady=10)

        ttk.Checkbutton(
            opts_frame,
            text="Criar um atalho na Área de Trabalho",
            variable=self.create_desktop,
        ).pack(anchor="w", pady=6)
        ttk.Checkbutton(
            opts_frame,
            text="Criar atalho no Menu Iniciar",
            variable=self.create_start,
        ).pack(anchor="w", pady=6)
        ttk.Checkbutton(
            opts_frame,
            text="Iniciar automaticamente com o Windows",
            variable=self.start_with_windows,
        ).pack(anchor="w", pady=6)

        return frame

    def create_page_progress(self):
        frame = tk.Frame(self.main_container, bg="white")
        self._add_page_header(
            frame,
            "Instalando o DisplayBridge...",
            "Aguarde enquanto os arquivos e configurações são aplicados.",
        )

        self.lbl_status = tk.Label(
            frame,
            text="Preparando instalação...",
            font=("Segoe UI", 10),
            bg="white",
            anchor="w",
        )
        self.lbl_status.pack(fill=tk.X, padx=20, pady=(15, 0))

        self.progress = ttk.Progressbar(frame, mode="indeterminate")
        self.progress.pack(fill=tk.X, padx=20, pady=15)

        return frame

    def create_page_done(self):
        frame = tk.Frame(self.main_container, bg="white")

        body = tk.Frame(frame, bg="white")
        body.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        if self.logo_80 is not None:
            left_col = tk.Frame(body, bg="white")
            left_col.pack(side=tk.LEFT, anchor="n", padx=(4, 18), pady=(6, 0))
            tk.Label(left_col, image=self.logo_80, bg="white", bd=0).pack()

        right_col = tk.Frame(body, bg="white")
        right_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        lbl_title = tk.Label(
            right_col,
            text="Instalação Concluída",
            font=("Segoe UI", 14, "bold"),
            bg="white",
            anchor="w",
        )
        lbl_title.pack(fill=tk.X, pady=(0, 10))

        txt = "A instalação do DisplayBridge no seu computador foi concluída com sucesso."
        lbl_desc = tk.Label(
            right_col,
            text=txt,
            font=("Segoe UI", 10),
            bg="white",
            justify="left",
            wraplength=360,
            anchor="w",
        )
        lbl_desc.pack(fill=tk.X, pady=(0, 16))

        chk_launch = ttk.Checkbutton(
            right_col,
            text="Iniciar o DisplayBridge agora",
            variable=self.launch_after_install,
        )
        chk_launch.pack(anchor="w", pady=8)

        lbl_footer = tk.Label(
            right_col,
            text="Clique em Concluir para sair do instalador.",
            font=("Segoe UI", 10),
            bg="white",
            justify="left",
            anchor="w",
        )
        lbl_footer.pack(fill=tk.X, pady=(16, 0))
        return frame

    def show_page(self, index):
        for p in self.pages:
            p.pack_forget()

        self.pages[index].pack(fill=tk.BOTH, expand=True)
        self.current_step = index

        if index == 0:
            self.btn_back.config(state="disabled")
            self.btn_next.config(text="Avançar >", state="normal")
        elif index == 3:
            self.btn_back.config(state="disabled")
            self.btn_next.config(state="disabled")
            self.btn_cancel.config(state="disabled")
            self.after(300, self.do_install)
        elif index == 4:
            self.btn_back.config(state="disabled")
            self.btn_next.config(text="Concluir", state="normal")
            self.btn_cancel.config(state="disabled")
        else:
            self.btn_back.config(state="normal")
            self.btn_next.config(text="Instalar" if index == 2 else "Avançar >", state="normal")

    def next_page(self):
        if self.current_step == 4:
            if self.launch_after_install.get():
                target_dir = self.install_path.get()
                exe_path = os.path.join(target_dir, "DisplayBridge.exe")
                if os.path.exists(exe_path):
                    self.btn_next.config(text="Iniciando...", state="disabled")
                    self.update()
                    try:
                        subprocess.Popen([exe_path], cwd=target_dir)
                    except Exception:
                        os.startfile(exe_path)
                    self.after(400, self.destroy)
                    return
            self.destroy()
        else:
            self.show_page(self.current_step + 1)

    def prev_page(self):
        self.show_page(self.current_step - 1)

    def do_install(self):
        self.progress.start(15)
        self.lbl_status.config(text="Copiando arquivos...")
        self.update()

        try:
            target_dir = os.path.abspath(self.install_path.get())
            os.makedirs(target_dir, exist_ok=True)

            # Deletar settings.json antigo para garantir estado limpo
            appdata = os.environ.get("APPDATA", "")
            settings_path = os.path.join(appdata, "DisplayBridge", "settings.json")
            if os.path.exists(settings_path):
                try:
                    os.remove(settings_path)
                except Exception:
                    pass

            # Localizar executável embutido
            base_path = (
                sys._MEIPASS
                if hasattr(sys, "_MEIPASS")
                else os.path.dirname(os.path.abspath(__file__))
            )
            src_exe = os.path.join(base_path, "DisplayBridge_Portable.exe")
            if not os.path.exists(src_exe):
                src_exe = os.path.abspath(
                    os.path.join(base_path, "..", "dist", "DisplayBridge_Portable.exe")
                )

            if not os.path.exists(src_exe):
                raise Exception(f"Arquivo executável não encontrado: {src_exe}")

            dst_exe = os.path.join(target_dir, "DisplayBridge.exe")

            # Encerra processo antigo caso esteja rodando antes de sobrescrever
            try:
                creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
                subprocess.run(
                    ["taskkill", "/F", "/IM", "DisplayBridge.exe"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    creationflags=creationflags,
                    timeout=5,
                )
            except Exception:
                pass

            last_err = None
            for _ in range(6):
                try:
                    shutil.copy2(src_exe, dst_exe)
                    last_err = None
                    break
                except Exception as copy_err:
                    last_err = copy_err
                    time.sleep(0.3)
            if last_err is not None:
                raise last_err

            self.lbl_status.config(text="Criando atalhos e registrando no Windows...")
            self.update()

            shell = win32com.client.Dispatch("WScript.Shell")

            if self.create_desktop.get():
                desktop = shell.SpecialFolders("Desktop") or os.path.join(
                    os.environ.get("USERPROFILE", ""), "Desktop"
                )
                shortcut = shell.CreateShortCut(os.path.join(desktop, "DisplayBridge.lnk"))
                shortcut.Targetpath = dst_exe
                shortcut.WorkingDirectory = target_dir
                shortcut.IconLocation = f"{dst_exe},0"
                shortcut.save()

            if self.create_start.get():
                start_menu = shell.SpecialFolders("Programs") or os.path.join(
                    os.environ.get("APPDATA", ""),
                    r"Microsoft\Windows\Start Menu\Programs",
                )
                shortcut = shell.CreateShortCut(os.path.join(start_menu, "DisplayBridge.lnk"))
                shortcut.Targetpath = dst_exe
                shortcut.WorkingDirectory = target_dir
                shortcut.IconLocation = f"{dst_exe},0"
                shortcut.save()

            # Registro de inicialização com o Windows
            run_key = r"Software\Microsoft\Windows\CurrentVersion\Run"
            approved_key = r"Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run"
            key = winreg.CreateKeyEx(
                winreg.HKEY_CURRENT_USER, run_key, 0, winreg.KEY_SET_VALUE
            )
            if self.start_with_windows.get():
                winreg.SetValueEx(key, "DisplayBridge", 0, winreg.REG_SZ, f'"{dst_exe}"')
                try:
                    k2 = winreg.CreateKeyEx(
                        winreg.HKEY_CURRENT_USER, approved_key, 0, winreg.KEY_SET_VALUE
                    )
                    winreg.SetValueEx(
                        k2, "DisplayBridge", 0, winreg.REG_BINARY, bytes([2] + [0] * 11)
                    )
                    winreg.CloseKey(k2)
                except Exception:
                    pass
            else:
                try:
                    winreg.DeleteValue(key, "DisplayBridge")
                except FileNotFoundError:
                    pass
            winreg.CloseKey(key)

            # Registro em "Aplicativos Instalados" / "Programas e Recursos" do Windows
            uninstall_key = r"Software\Microsoft\Windows\CurrentVersion\Uninstall\DisplayBridge"
            uk = winreg.CreateKeyEx(
                winreg.HKEY_CURRENT_USER, uninstall_key, 0, winreg.KEY_SET_VALUE
            )
            size_kb = max(1, os.path.getsize(dst_exe) // 1024)
            winreg.SetValueEx(uk, "DisplayName", 0, winreg.REG_SZ, "DisplayBridge")
            winreg.SetValueEx(uk, "DisplayVersion", 0, winreg.REG_SZ, "4.0.0")
            winreg.SetValueEx(uk, "Publisher", 0, winreg.REG_SZ, "DisplayBridge")
            winreg.SetValueEx(uk, "InstallLocation", 0, winreg.REG_SZ, target_dir)
            winreg.SetValueEx(uk, "DisplayIcon", 0, winreg.REG_SZ, f"{dst_exe},0")
            winreg.SetValueEx(
                uk, "UninstallString", 0, winreg.REG_SZ, f'"{dst_exe}" --uninstall'
            )
            winreg.SetValueEx(
                uk,
                "QuietUninstallString",
                0,
                winreg.REG_SZ,
                f'"{dst_exe}" --uninstall --silent',
            )
            winreg.SetValueEx(uk, "InstallDate", 0, winreg.REG_SZ, time.strftime("%Y%m%d"))
            winreg.SetValueEx(uk, "EstimatedSize", 0, winreg.REG_DWORD, size_kb)
            winreg.SetValueEx(uk, "NoModify", 0, winreg.REG_DWORD, 1)
            winreg.SetValueEx(uk, "NoRepair", 0, winreg.REG_DWORD, 1)
            winreg.CloseKey(uk)

            # Grava configurações iniciais coerentes com a escolha do instalador
            # (first_run=True garante que o onboarding apareça a cada reinstalação)
            try:
                os.makedirs(os.path.dirname(settings_path), exist_ok=True)
                with open(settings_path, "w", encoding="utf-8") as f:
                    json.dump(
                        {
                            "start_with_windows": bool(self.start_with_windows.get()),
                            "enable_notifications": True,
                            "first_run": True,
                        },
                        f,
                        indent=4,
                        ensure_ascii=False,
                    )
            except Exception:
                pass

            self.progress.stop()
            self.show_page(4)

        except Exception as e:
            self.progress.stop()
            messagebox.showerror("Erro de Instalação", str(e))
            self.destroy()


if __name__ == "__main__":
    app = StandardInstaller()
    app.mainloop()
