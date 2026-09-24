from PIL import Image, ImageDraw

def create_icon():
    # Cores
    bg_color = (0, 0, 0, 0) # Transparente
    green_avocado = "#8BC34A"
    
    # Alta resolução
    size = 512
    img = Image.new("RGBA", (size, size), bg_color)
    draw = ImageDraw.Draw(img)
    
    # Fundo arredondado (estilo ícone de app)
    # Se quiser fundo transparente, não desenhe um quadrado de fundo. Vamos fazer o ícone solto.
    
    # Retângulo esquerdo (monitor 1)
    rect_w = 120
    rect_h = 180
    space = 60
    
    x1 = (size - (rect_w * 2 + space)) // 2
    y1 = (size - rect_h) // 2
    
    # Desenha o monitor esquerdo
    draw.rounded_rectangle([x1, y1, x1+rect_w, y1+rect_h], radius=15, fill=green_avocado)
    
    # Desenha o monitor direito
    x2 = x1 + rect_w + space
    draw.rounded_rectangle([x2, y1, x2+rect_w, y1+rect_h], radius=15, fill=green_avocado)
    
    # Círculo central (mostrando a circularidade)
    cx = size // 2
    cy = size // 2
    radius = 50
    # Desenha o anel/círculo
    draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], outline=green_avocado, width=16)
    
    # Salvar PNG alta resolução (Store)
    img.save("assets/icon_store.png")
    
    # Salvar ICO para o windows (vários tamanhos embutidos)
    icon_sizes = [(16,16), (32,32), (48,48), (64,64), (128,128), (256,256)]
    img.save("assets/icon.ico", format="ICO", sizes=icon_sizes)
    print("Ícone gerado com sucesso!")

if __name__ == "__main__":
    create_icon()
