import tkinter as tk
from utils.config import load_settings, save_settings, toggle_startup_registry

def show_settings_ui():
    settings = load_settings()
    
    root = tk.Tk()
    root.title("DisplayBridge - Configurações")
    root.configure(bg="#1c1c1e")
    
    width = 340
    height = 240
    
    try:
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        root.geometry(f"{width}x{height}+{x}+{y}")
    except Exception:
        root.geometry(f"{width}x{height}")
    # Janela maior para evitar corte no botão Fechar em telas com escala > 100%
    root.geometry("400x320")
    root.resizable(False, False)
    
    system_font_bold = ("Segoe UI", 12, "bold")
    system_font_normal = ("Segoe UI", 10)
    system_font_caption = ("Segoe UI", 8)
    
    class MacOSToggle(tk.Canvas):
        def __init__(self, parent, initial_state=False, command=None):
            super().__init__(parent, width=44, height=24, bg="#2c2c2e", highlightthickness=0)
            self.command = command
            self.state = initial_state
            self.bind("<Button-1>", self.toggle)
            self.draw()

        def draw(self):
            self.delete("all")
            color = "#34c759" if self.state else "#3a3a3c"
            
            self.create_arc(0, 0, 24, 24, start=90, extent=180, fill=color, outline="")
            self.create_arc(20, 0, 44, 24, start=270, extent=180, fill=color, outline="")
            self.create_rectangle(12, 0, 32, 24, fill=color, outline="")
            
            knob_x = 32 if self.state else 12
            self.create_oval(knob_x-10, 2, knob_x+10, 22, fill="#ffffff", outline="")

        def toggle(self, event):
            self.state = not self.state
            self.draw()
            if self.command:
                self.command(self.state)
                
    header_frame = tk.Frame(root, bg="#1c1c1e")
    header_frame.pack(pady=(20, 15), fill="x", padx=20)
    
    icon_canvas = tk.Canvas(header_frame, width=32, height=32, bg="#1c1c1e", highlightthickness=0)
    icon_canvas.pack(side="left", padx=(0, 10))
    icon_canvas.create_rectangle(4, 10, 14, 22, fill="#8BC34A", outline="")
    icon_canvas.create_rectangle(18, 10, 28, 22, fill="#8BC34A", outline="")
    icon_canvas.create_oval(12, 12, 20, 20, outline="#8BC34A", width=2)
    
    title_frame = tk.Frame(header_frame, bg="#1c1c1e")
    title_frame.pack(side="left")
    
    lbl_title = tk.Label(title_frame, text="DisplayBridge", fg="#ffffff", bg="#1c1c1e", font=system_font_bold)
    lbl_title.pack(anchor="w")
    
    lbl_ver = tk.Label(title_frame, text="Configurações do Sistema", fg="#8e8e93", bg="#1c1c1e", font=system_font_normal)
    lbl_ver.pack(anchor="w")
    
    group_frame = tk.Frame(root, bg="#2c2c2e", bd=0)
    group_frame.pack(fill="x", padx=20, pady=5)
    
    def make_row(parent, title, caption, val, cmd, is_last=False):
        row = tk.Frame(parent, bg="#2c2c2e", height=50)
        row.pack(fill="x", padx=15, pady=8)
        
        txt_frame = tk.Frame(row, bg="#2c2c2e")
        txt_frame.pack(side="left", fill="both", expand=True)
        
        lbl_t = tk.Label(txt_frame, text=title, fg="#ffffff", bg="#2c2c2e", font=system_font_normal, anchor="w")
        lbl_t.pack(fill="x", anchor="w")
        
        lbl_c = tk.Label(txt_frame, text=caption, fg="#8e8e93", bg="#2c2c2e", font=system_font_caption, anchor="w")
        lbl_c.pack(fill="x", anchor="w")
        
        toggle = MacOSToggle(row, initial_state=val, command=cmd)
        toggle.pack(side="right", padx=(5, 0))
        
        if not is_last:
            sep = tk.Frame(parent, bg="#3a3a3c", height=1)
            sep.pack(fill="x", padx=15)
            
    def on_toggle_startup(state):
        settings["start_with_windows"] = state
        save_settings(settings)
        toggle_startup_registry(state)
        
    def on_toggle_notif(state):
        settings["enable_notifications"] = state
        save_settings(settings)
        
    make_row(group_frame, "Iniciar com o Computador", "Executar DisplayBridge ao ligar o PC", settings["start_with_windows"], on_toggle_startup)
    make_row(group_frame, "Exibir Notificações", "Mostrar aviso ao mover janelas", settings["enable_notifications"], on_toggle_notif, is_last=True)
    
    footer_frame = tk.Frame(root, bg="#1c1c1e")
    footer_frame.pack(fill="x", padx=20, pady=(15, 0))
    
    btn_close = tk.Button(
        footer_frame, 
        text="Fechar", 
        command=root.destroy, 
        bg="#8BC34A", 
        fg="#ffffff", 
        activebackground="#689F38", 
        activeforeground="#ffffff", 
        bd=0, 
        font=system_font_normal,
        padx=20,
        pady=5,
        cursor="hand2"
    )
    btn_close.pack(side="right", pady=5)
    
    root.mainloop()
