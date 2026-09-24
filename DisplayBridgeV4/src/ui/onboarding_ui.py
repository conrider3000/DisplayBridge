import tkinter as tk
from utils.config import load_settings, save_settings

class RoundedButton(tk.Canvas):
    def __init__(self, parent, text, command, width=150, height=40, bg="#8BC34A", fg="white", font=("Segoe UI", 11, "bold"), radius=20):
        super().__init__(parent, width=width, height=height, bg="#1c1c1e", highlightthickness=0)
        self.command = command
        self.text = text
        self.bg_color = bg
        self.fg_color = fg
        self.font = font
        self.radius = radius
        self.rect_id = None
        self.text_id = None
        
        self.bind("<ButtonPress-1>", self.on_press)
        self.bind("<ButtonRelease-1>", self.on_release)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        
        self.draw()

    def draw(self, color=None):
        self.delete("all")
        c = color if color else self.bg_color
        w = int(self["width"])
        h = int(self["height"])
        r = self.radius
        
        self.rect_id = self.create_polygon(
            r, 0, w-r, 0, w, 0, w, r, w, h-r, w, h, w-r, h, r, h, 0, h, 0, h-r, 0, r, 0, 0,
            fill=c, outline=c, smooth=True
        )
        self.text_id = self.create_text(w/2, h/2, text=self.text, fill=self.fg_color, font=self.font)

    def on_press(self, event):
        self.draw("#689F38")
        
    def on_release(self, event):
        self.draw()
        if self.command:
            self.command()
            
    def on_enter(self, event):
        self.draw("#9CCC65")
        
    def on_leave(self, event):
        self.draw()

def show_onboarding():
    root = tk.Tk()
    root.title("Bem-vindo ao DisplayBridge")
    root.configure(bg="#1c1c1e")
    
    width, height = 450, 500
    try:
        sw = root.winfo_screenwidth()
        sh = root.winfo_screenheight()
        x = (sw - width) // 2
        y = (sh - height) // 2
        root.geometry(f"{width}x{height}+{x}+{y}")
    except:
        root.geometry(f"{width}x{height}")
        
    root.resizable(False, False)
    
    # Ícone vetorial desenhado
    canvas = tk.Canvas(root, width=120, height=80, bg="#1c1c1e", highlightthickness=0)
    canvas.pack(pady=(40, 20))
    # Monitores e círculo verde abacate
    canvas.create_rectangle(10, 10, 40, 60, fill="#8BC34A", outline="", width=2)
    canvas.create_rectangle(80, 10, 110, 60, fill="#8BC34A", outline="", width=2)
    canvas.create_oval(40, 15, 80, 55, outline="#8BC34A", width=4)
    canvas.create_polygon(75, 30, 85, 35, 75, 40, fill="#8BC34A") # Seta no círculo
    
    # Textos
    tk.Label(root, text="Bem-vindo ao DisplayBridge", font=("Segoe UI", 18, "bold"), fg="white", bg="#1c1c1e").pack(pady=(0, 10))
    
    info_text = (
        "O DisplayBridge está rodando invisível na bandeja do relógio.\n\n"
        "Atalho Mágico: TAB + ALT\n"
        "Pressione a tecla TAB e segure, e depois toque no ALT para jogar a "
        "janela atual para o próximo monitor instantaneamente!\n\n"
        "A Circularidade:\n"
        "Se a janela estiver no último monitor, não se preocupe! "
        "Ela dará a volta e aparecerá no primeiro monitor novamente."
    )
    
    tk.Label(root, text=info_text, font=("Segoe UI", 11), fg="#8e8e93", bg="#1c1c1e", justify="center", wraplength=380).pack(pady=20)
    
    def finish():
        settings = load_settings()
        settings["first_run"] = False
        save_settings(settings)
        root.destroy()
        
    btn = RoundedButton(root, "Começar", finish)
    btn.pack(pady=30)
    
    # Impede que fechem pelo X sem salvar (ou salva do mesmo jeito)
    def on_close():
        finish()
        
    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()

if __name__ == "__main__":
    show_onboarding()
