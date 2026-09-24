import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys
import shutil
import winreg
import win32com.client

class StandardInstaller(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Instalação do DisplayBridge 3.0")
        self.geometry("500x360")
        self.resizable(False, False)
        
        # Tema nativo do Windows
        style = ttk.Style(self)
        try:
            style.theme_use('vista') # Ou 'clam', 'xpnative' dependendo da plataforma
        except:
            pass

        self.current_step = 0
        self.install_path = tk.StringVar(value=os.path.join(os.environ.get("LOCALAPPDATA", ""), "DisplayBridge"))
        self.create_desktop = tk.BooleanVar(value=True)
        self.create_start = tk.BooleanVar(value=True)
        self.start_with_windows = tk.BooleanVar(value=True)
        
        self.pages = []
        
        self.create_ui()
        self.show_page(0)

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
        lbl_title = tk.Label(frame, text="Bem-vindo ao Instalador do DisplayBridge", font=("Segoe UI", 14, "bold"), bg="white", anchor="w")
        lbl_title.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        txt = ("Este assistente guiará você na instalação do DisplayBridge versão 3.0 no seu computador.\n\n"
               "É recomendado que você feche todos os outros aplicativos antes de continuar.\n\n\n"
               "Clique em Avançar para continuar ou Cancelar para sair do instalador.")
        lbl_desc = tk.Label(frame, text=txt, font=("Segoe UI", 10), bg="white", justify="left", wraplength=450)
        lbl_desc.pack(fill=tk.BOTH, expand=True, padx=20)
        return frame

    def create_page_path(self):
        frame = tk.Frame(self.main_container, bg="white")
        lbl_title = tk.Label(frame, text="Selecione o Local de Instalação", font=("Segoe UI", 12, "bold"), bg="white", anchor="w")
        lbl_title.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        lbl_desc = tk.Label(frame, text="Onde o DisplayBridge deve ser instalado?", font=("Segoe UI", 10), bg="white", justify="left")
        lbl_desc.pack(fill=tk.X, padx=20)
        
        path_frame = tk.Frame(frame, bg="white")
        path_frame.pack(fill=tk.X, padx=20, pady=10)
        
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
        lbl_title = tk.Label(frame, text="Selecionar Tarefas Adicionais", font=("Segoe UI", 12, "bold"), bg="white", anchor="w")
        lbl_title.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        lbl_desc = tk.Label(frame, text="Quais tarefas adicionais devem ser executadas?", font=("Segoe UI", 10), bg="white", justify="left")
        lbl_desc.pack(fill=tk.X, padx=20)
        
        opts_frame = tk.Frame(frame, bg="white")
        opts_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=10)
        
        ttk.Checkbutton(opts_frame, text="Criar um atalho na Área de Trabalho", variable=self.create_desktop).pack(anchor="w", pady=5)
        ttk.Checkbutton(opts_frame, text="Criar atalho no Menu Iniciar", variable=self.create_start).pack(anchor="w", pady=5)
        ttk.Checkbutton(opts_frame, text="Iniciar automaticamente com o Windows", variable=self.start_with_windows).pack(anchor="w", pady=5)
        
        return frame

    def create_page_progress(self):
        frame = tk.Frame(self.main_container, bg="white")
        self.lbl_prog_title = tk.Label(frame, text="Instalando...", font=("Segoe UI", 12, "bold"), bg="white", anchor="w")
        self.lbl_prog_title.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        self.lbl_status = tk.Label(frame, text="Aguarde enquanto o DisplayBridge é instalado.", font=("Segoe UI", 10), bg="white", anchor="w")
        self.lbl_status.pack(fill=tk.X, padx=20)
        
        self.progress = ttk.Progressbar(frame, mode="indeterminate")
        self.progress.pack(fill=tk.X, padx=20, pady=20)
        
        return frame

    def create_page_done(self):
        frame = tk.Frame(self.main_container, bg="white")
        lbl_title = tk.Label(frame, text="Instalação Concluída", font=("Segoe UI", 14, "bold"), bg="white", anchor="w")
        lbl_title.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        txt = "A instalação do DisplayBridge no seu computador foi concluída com sucesso.\n\nClique em Concluir para sair."
        lbl_desc = tk.Label(frame, text=txt, font=("Segoe UI", 10), bg="white", justify="left", wraplength=450)
        lbl_desc.pack(fill=tk.BOTH, expand=True, padx=20)
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
            self.after(500, self.do_install)
        elif index == 4:
            self.btn_back.config(state="disabled")
            self.btn_next.config(text="Concluir", state="normal")
            self.btn_cancel.config(state="disabled")
        else:
            self.btn_back.config(state="normal")
            self.btn_next.config(text="Instalar" if index == 2 else "Avançar >", state="normal")

    def next_page(self):
        if self.current_step == 4:
            # Concluir e abrir o app
            exe_path = os.path.join(self.install_path.get(), "DisplayBridge.exe")
            if os.path.exists(exe_path):
                os.startfile(exe_path)
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
            target_dir = self.install_path.get()
            os.makedirs(target_dir, exist_ok=True)
            
            # Deletar settings.json para forçar o onboarding sempre
            appdata = os.environ.get("APPDATA", "")
            settings_path = os.path.join(appdata, "DisplayBridge", "settings.json")
            if os.path.exists(settings_path):
                try:
                    os.remove(settings_path)
                except:
                    pass

            # Copiar executável
            base_path = sys._MEIPASS if hasattr(sys, '_MEIPASS') else os.path.dirname(os.path.abspath(__file__))
            src_exe = os.path.join(base_path, "DisplayBridge_Portable.exe")
            
            if not os.path.exists(src_exe):
                # Fallback para desenvolvimento
                src_exe = os.path.abspath(os.path.join(base_path, "..", "dist", "DisplayBridge_Portable.exe"))
                
            dst_exe = os.path.join(target_dir, "DisplayBridge.exe")
            
            try:
                # Mata o processo se estiver rodando para poder sobrescrever
                os.system('taskkill /F /IM DisplayBridge.exe >nul 2>&1')
            except:
                pass

            if os.path.exists(src_exe):
                shutil.copy2(src_exe, dst_exe)
            else:
                raise Exception(f"Arquivo executável não encontrado: {src_exe}")

            self.lbl_status.config(text="Criando atalhos...")
            self.update()
            
            shell = win32com.client.Dispatch("WScript.Shell")
            
            if self.create_desktop.get():
                desktop = os.path.join(os.environ["USERPROFILE"], "Desktop")
                shortcut = shell.CreateShortCut(os.path.join(desktop, "DisplayBridge.lnk"))
                shortcut.Targetpath = dst_exe
                shortcut.WorkingDirectory = target_dir
                shortcut.save()

            if self.create_start.get():
                start_menu = os.path.join(os.environ["APPDATA"], r"Microsoft\Windows\Start Menu\Programs")
                shortcut = shell.CreateShortCut(os.path.join(start_menu, "DisplayBridge.lnk"))
                shortcut.Targetpath = dst_exe
                shortcut.WorkingDirectory = target_dir
                shortcut.save()

            if self.start_with_windows.get():
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
                winreg.SetValueEx(key, "DisplayBridge", 0, winreg.REG_SZ, f'"{dst_exe}"')
                winreg.CloseKey(key)

            self.progress.stop()
            self.show_page(4)

        except Exception as e:
            self.progress.stop()
            messagebox.showerror("Erro de Instalação", str(e))
            self.destroy()

if __name__ == "__main__":
    app = StandardInstaller()
    app.mainloop()
