from pathlib import Path
from rembg import remove
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps
import io

ROOT = Path(r"e:\silkynest")
ASSETS = ROOT / "assets"
PREVIEW = ROOT / "preview" / "assets"
ASSETS.mkdir(exist_ok=True)
PREVIEW.mkdir(parents=True, exist_ok=True)

PROD_SRC = Path(
    r"C:\Users\Administrator\.cursor\projects\e-silkynest\assets\c__Users_Administrator_AppData_Roaming_Cursor_User_workspaceStorage_33c80e412b7940b62dcfaae1ee8bc76c_images_WhatsApp_Image_2026-10-03_at_11.00.01_PM-0ce1e347-11f5-4639-b346-104cb0434e0d.png"
)
BOX_SRC = Path(
    r"C:\Users\Administrator\.cursor\projects\e-silkynest\assets\c__Users_Administrator_AppData_Roaming_Cursor_User_workspaceStorage_33c80e412b7940b62dcfaae1ee8bc76c_images_image-b882f7b9-4524-439e-9b5d-93693a565971.png"
)

W, H = 1920, 1080
BOX_CREAM = (236, 235, 228)

FONT_SERIF_B = r"C:\Windows\Fonts\georgiab.ttf"
FONT_SANS = r"C:\Windows\Fonts\arial.ttf"
FONT_SANS_B = r"C:\Windows\Fonts\arialbd.ttf"


def cutout(path: Path) -> Image.Image:
    raw = Image.open(path).convert("RGBA")
    out = remove(raw)
    if not isinstance(out, Image.Image):
        out = Image.open(io.BytesIO(out)).convert("RGBA")
    else:
        out = out.convert("RGBA")
    px = out.load()
    w, h = out.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a < 10:
                px[x, y] = (0, 0, 0, 0)
            elif r > 228 and g > 228 and b > 228 and a < 255:
                px[x, y] = (r, g, b, max(0, int(a * 0.25)))
    bb = out.getbbox()
    return out.crop(bb) if bb else out


def match_cream_label(im: Image.Image, target=BOX_CREAM) -> Image.Image:
    """Shift cream label pixels toward box cream; keep oil, ink, yellow badges."""
    im = im.copy()
    px = im.load()
    w, h = im.size
    tr, tg, tb = target
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a < 20:
                continue
            if r < 90 and g < 90 and b < 90:
                continue
            if r > 200 and g > 160 and b < 90:
                continue
            sat = max(r, g, b) - min(r, g, b)
            lum = (r + g + b) / 3
            if sat > 45 and r > 100 and g > 60 and b < 90 and lum < 170:
                continue
            if lum > 175 and sat < 55:
                f = 0.78
                px[x, y] = (
                    int(r * (1 - f) + tr * f),
                    int(g * (1 - f) + tg * f),
                    int(b * (1 - f) + tb * f),
                    a,
                )
            elif lum > 155 and sat < 40:
                f = 0.58
                px[x, y] = (
                    int(r * (1 - f) + tr * f),
                    int(g * (1 - f) + tg * f),
                    int(b * (1 - f) + tb * f),
                    a,
                )
    return im


def contact_shadow(w: int, h: int, blur: int = 22, opacity: int = 140) -> Image.Image:
    sh = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(sh)
    d.ellipse(
        [int(w * 0.08), int(h * 0.35), int(w * 0.92), int(h * 0.85)],
        fill=(40, 28, 16, opacity),
    )
    return sh.filter(ImageFilter.GaussianBlur(blur))


def load_sea(variant: int = 0) -> Image.Image:
    sea = (
        Image.open(ASSETS / "banner-sea-clean.jpg")
        .convert("RGBA")
        .resize((W, H), Image.Resampling.LANCZOS)
    )
    if variant == 1:
        sea = ImageEnhance.Color(sea).enhance(1.05)
        sea = ImageEnhance.Brightness(sea).enhance(1.02)
    elif variant == 2:
        sea = ImageEnhance.Color(sea).enhance(0.95)
        sea = ImageEnhance.Contrast(sea).enhance(1.06)
    return sea


def draw_left_copy(canvas: Image.Image, title: str, subtitle: str, bullets: list[str]) -> Image.Image:
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    for i in range(820):
        a = int(155 * (1 - i / 820) ** 1.35)
        d.line([(i, 0), (i, H)], fill=(255, 252, 246, a))

    brand_f = ImageFont.truetype(FONT_SERIF_B, 72)
    tag_f = ImageFont.truetype(FONT_SANS, 22)
    head_f = ImageFont.truetype(FONT_SERIF_B, 44)
    body_f = ImageFont.truetype(FONT_SANS, 24)
    small_f = ImageFont.truetype(FONT_SANS_B, 16)

    x0, y0 = 96, 200
    d.text((x0, y0), "SILKYNEST", font=brand_f, fill=(22, 20, 18, 245))
    d.text((x0, y0 + 82), "YOUR HAIRS SECRET TREASURE", font=tag_f, fill=(55, 50, 42, 220))
    d.rectangle([x0, y0 + 122, x0 + 220, y0 + 126], fill=(240, 208, 0, 230))
    d.text((x0, y0 + 150), title, font=head_f, fill=(22, 20, 18, 245))
    d.text((x0, y0 + 210), subtitle, font=body_f, fill=(55, 50, 42, 220))

    yy = y0 + 270
    for bullet in bullets:
        d.ellipse([x0 + 4, yy + 8, x0 + 14, yy + 18], fill=(240, 208, 0, 255))
        d.text((x0 + 28, yy), bullet, font=body_f, fill=(30, 28, 24, 235))
        yy += 42

    d.text((x0, H - 120), "150ML  ·  100% NATURAL", font=small_f, fill=(70, 65, 55, 200))
    canvas.alpha_composite(layer)
    return canvas


def place_product(
    canvas: Image.Image,
    product: Image.Image,
    scale_h: float = 0.70,
    x_ratio: float = 0.74,
    foot_y: float = 0.88,
) -> Image.Image:
    target_h = int(H * scale_h)
    ratio = target_h / product.height
    target_w = int(product.width * ratio)
    prod = product.resize((target_w, target_h), Image.Resampling.LANCZOS)
    prod = ImageEnhance.Color(prod).enhance(0.98)
    prod = ImageEnhance.Contrast(prod).enhance(1.03)

    x = int(W * x_ratio - target_w / 2)
    y = int(H * foot_y - target_h)
    x = max(40, min(x, W - target_w - 30))
    y = max(30, min(y, H - target_h - 10))

    sh = contact_shadow(target_w, int(target_h * 0.28), blur=26, opacity=125)
    canvas.alpha_composite(sh, (x, y + target_h - sh.height + 8))

    alpha = prod.split()[-1]
    amb = ImageOps.colorize(alpha.point(lambda a: int(a * 0.35)), black=(0, 0, 0), white=(0, 0, 0)).convert("RGBA")
    amb.putalpha(alpha.point(lambda a: int(a * 0.22)))
    amb = amb.filter(ImageFilter.GaussianBlur(8))
    canvas.alpha_composite(amb, (x + 8, y + 12))
    canvas.alpha_composite(prod, (x, y))
    return canvas


def main() -> None:
    print("Cutting...")
    product = match_cream_label(cutout(PROD_SRC))
    box = match_cream_label(cutout(BOX_SRC))
    product.save(ASSETS / "silky-nest-product-real.png")
    box.save(ASSETS / "silky-nest-box-real.png")
    print("product", product.size, "box", box.size)

    banners = [
        {
            "file": "banner-sea-1.jpg",
            "cat": "category-growth.jpg",
            "variant": 0,
            "use": "product",
            "scale": 0.72,
            "x": 0.76,
            "foot": 0.90,
            "title": "Stimulates Growth",
            "subtitle": "Nourish the scalp. Support stronger-looking hair.",
            "bullets": ["Herbal follicle care", "Roots to tip nourishment", "Visible vitality over time"],
        },
        {
            "file": "banner-sea-2.jpg",
            "cat": "category-hairfall.jpg",
            "variant": 1,
            "use": "product",
            "scale": 0.68,
            "x": 0.78,
            "foot": 0.91,
            "title": "Reduces Hair Fall",
            "subtitle": "100% natural anti hair-fall support.",
            "bullets": ["Fortifies each strand", "Less breakage while combing", "Daily scalp comfort"],
        },
        {
            "file": "banner-sea-3.jpg",
            "cat": "category-shine.jpg",
            "variant": 2,
            "use": "box",
            "scale": 0.78,
            "x": 0.77,
            "foot": 0.905,
            "title": "Adds Shine & Softness",
            "subtitle": "Silky finish. Soft touch. Natural glow.",
            "bullets": ["Non-sticky golden oil", "15+ herbs & oils", "Premium 150ML ritual"],
        },
    ]

    for b in banners:
        print("compose", b["file"])
        canvas = load_sea(b["variant"])
        img = product if b["use"] == "product" else box
        canvas = place_product(canvas, img, scale_h=b["scale"], x_ratio=b["x"], foot_y=b["foot"])
        canvas = draw_left_copy(canvas, b["title"], b["subtitle"], b["bullets"])
        rgb = canvas.convert("RGB")
        rgb = ImageEnhance.Sharpness(rgb).enhance(1.08)
        rgb = ImageEnhance.Color(rgb).enhance(0.96)
        for folder in (ASSETS, PREVIEW):
            rgb.save(folder / b["file"], "JPEG", quality=93, optimize=True, progressive=True)
            rgb.save(folder / b["cat"], "JPEG", quality=92, optimize=True, progressive=True)

    for folder in (ASSETS, PREVIEW):
        Image.open(ASSETS / "banner-sea-1.jpg").save(folder / "banner-main.png")
        product.save(folder / "silky-nest-product-real.png")
        box.save(folder / "silky-nest-box-real.png")
        product.resize(
            (int(product.width * 700 / product.height), 700), Image.Resampling.LANCZOS
        ).save(folder / "silky-nest-product.png")
        box.resize(
            (int(box.width * 720 / box.height), 720), Image.Resampling.LANCZOS
        ).save(folder / "silky-nest-box-side.png")
        product.save(folder / "product-cutout-clean.png")

    print("DONE")


if __name__ == "__main__":
    main()
