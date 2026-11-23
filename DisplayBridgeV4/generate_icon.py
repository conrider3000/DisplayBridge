import os
from PIL import Image, ImageEnhance

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
SOURCE_PNG = os.path.join(ASSETS_DIR, "logo_source.png")


def _load_trimmed_square(pad_ratio=0.04):
    """Carrega a logo original, remove margem transparente excessiva e centraliza em quadrado."""
    src = Image.open(SOURCE_PNG).convert("RGBA")
    alpha = src.getchannel("A")
    # Remove ruído invisível nas bordas (alpha <= 8)
    clean_alpha = alpha.point(lambda p: 0 if p <= 8 else p)
    src.putalpha(clean_alpha)

    bbox = clean_alpha.getbbox()
    if bbox:
        src = src.crop(bbox)

    side = max(src.width, src.height)
    pad = int(round(side * pad_ratio))
    canvas_side = side + pad * 2
    square = Image.new("RGBA", (canvas_side, canvas_side), (0, 0, 0, 0))
    offset_x = (canvas_side - src.width) // 2
    offset_y = (canvas_side - src.height) // 2
    square.paste(src, (offset_x, offset_y), src)
    return square


def _make_paused_variant(img):
    """Versão em escala de cinza suave para indicar modo pausado na bandeja."""
    r, g, b, a = img.split()
    gray = ImageEnhance.Color(img.convert("RGB")).enhance(0.12)
    dim = ImageEnhance.Brightness(gray).enhance(0.85)
    out = dim.convert("RGBA")
    out.putalpha(a.point(lambda p: int(p * 0.85)))
    return out


def _make_store_banner(logo_square, width, height, bg_color=(12, 82, 36, 255)):
    canvas = Image.new("RGBA", (width, height), bg_color)
    target = int(min(width, height) * 0.72)
    resized = logo_square.resize((target, target), Image.Resampling.LANCZOS)
    canvas.paste(resized, ((width - target) // 2, (height - target) // 2), resized)
    return canvas


def create_icons():
    os.makedirs(ASSETS_DIR, exist_ok=True)

    # Ícone principal (pequena margem de 3% para ficar nítido em qualquer escala)
    master = _load_trimmed_square(pad_ratio=0.03)
    master_512 = master.resize((512, 512), Image.Resampling.LANCZOS)
    master_512.save(os.path.join(ASSETS_DIR, "icon_store.png"))

    # ICO multi-resolução para executáveis, janelas e registro do Windows
    icon_sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    master_512.save(os.path.join(ASSETS_DIR, "icon.ico"), format="ICO", sizes=icon_sizes)

    # PNGs prontos para Tkinter (sem depender de PIL em runtime nas janelas)
    for size in (36, 48, 80):
        master.resize((size, size), Image.Resampling.LANCZOS).save(
            os.path.join(ASSETS_DIR, f"logo_{size}.png")
        )

    # Ícones da bandeja (sem margem extra para aproveitar ao máximo os 16x16 da barra)
    tray_base = _load_trimmed_square(pad_ratio=0.0).resize((64, 64), Image.Resampling.LANCZOS)
    tray_base.save(os.path.join(ASSETS_DIR, "tray_active.png"))
    _make_paused_variant(tray_base).save(os.path.join(ASSETS_DIR, "tray_paused.png"))

    # Assets da Store / manifest atualizados com a nova logo
    for name, sz in (
        ("Square44x44Logo.png", 44),
        ("StoreLogo.png", 50),
        ("Square71x71Logo.png", 71),
        ("Square150x150Logo.png", 150),
        ("Square310x310Logo.png", 310),
    ):
        master.resize((sz, sz), Image.Resampling.LANCZOS).save(os.path.join(ASSETS_DIR, name))

    _make_store_banner(master, 310, 150).save(os.path.join(ASSETS_DIR, "Wide310x150Logo.png"))
    _make_store_banner(master, 620, 300).save(os.path.join(ASSETS_DIR, "SplashScreen.png"))

    print("Todos os ícones e logos gerados com sucesso!")


if __name__ == "__main__":
    create_icons()
