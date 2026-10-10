"""Rebuild clean product gallery images from original studio photos."""
from pathlib import Path
from rembg import remove, new_session
from PIL import Image, ImageFilter, ImageEnhance, ImageDraw
import io

ROOT = Path(r"e:\silkynest")
ASSETS = ROOT / "assets"
PREVIEW = ROOT / "preview" / "assets"
SRC_DIR = Path(r"C:\Users\Administrator\.cursor\projects\e-silkynest\assets")

PROD = next(SRC_DIR.glob("*11.00.01_PM-0ce1e347*"))
BOX = next(SRC_DIR.glob("*image-b882f7b9*"))
BEN = next(SRC_DIR.glob("*11.15.00_PM-1b5b2421*"))

SIZE = 1200
CREAM = (247, 244, 238)
SESSION = new_session("u2net")


def cut_clean(path: Path) -> Image.Image:
    raw = Image.open(path).convert("RGBA")
    # upscale small sources first for cleaner edges
    if max(raw.size) < 1400:
        scale = 1600 / max(raw.size)
        raw = raw.resize((int(raw.width * scale), int(raw.height * scale)), Image.Resampling.LANCZOS)

    out = remove(
        raw,
        session=SESSION,
        alpha_matting=True,
        alpha_matting_foreground_threshold=240,
        alpha_matting_background_threshold=10,
        alpha_matting_erode_size=8,
    )
    if not isinstance(out, Image.Image):
        out = Image.open(io.BytesIO(out)).convert("RGBA")
    else:
        out = out.convert("RGBA")

    # smooth alpha edge
    r, g, b, a = out.split()
    a = a.filter(ImageFilter.GaussianBlur(0.8))
    # knock near-white fringe
    px = out.load()
    w, h = out.size
    for y in range(h):
        for x in range(w):
            rr, gg, bb, aa = px[x, y]
            if aa < 12:
                px[x, y] = (0, 0, 0, 0)
            elif rr > 230 and gg > 230 and bb > 230 and aa < 250:
                px[x, y] = (rr, gg, bb, max(0, aa - 90))

    out.putalpha(a)
    bb = out.getbbox()
    return out.crop(bb) if bb else out


def match_cream(im: Image.Image, target=(246, 245, 240)) -> Image.Image:
    im = im.copy()
    px = im.load()
    w, h = im.size
    tr, tg, tb = target
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a < 20:
                continue
            if max(r, g, b) < 95:
                continue
            if r > 195 and g > 150 and b < 110 and (r - b) > 70:
                continue
            sat = max(r, g, b) - min(r, g, b)
            lum = (r + g + b) / 3
            if sat > 40 and r > 95 and g > 55 and b < 95 and lum < 175:
                continue
            yellow = ((r + g) / 2) - b
            if lum >= 145 and (sat <= 80 or yellow > 5) and b > 110:
                f = 0.9
                nr = min(255, int(r * (1 - f) + tr * f + 4))
                ng = min(255, int(g * (1 - f) + tg * f + 4))
                nb = min(255, int(b * (1 - f) + tb * f + 8))
                px[x, y] = (nr, ng, nb, a)
    return im


def soft_shadow(w: int, h: int) -> Image.Image:
    sh = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(sh)
    d.ellipse([int(w * 0.15), int(h * 0.55), int(w * 0.85), int(h * 0.92)], fill=(40, 30, 20, 55))
    return sh.filter(ImageFilter.GaussianBlur(28))


def on_studio(cut: Image.Image, pad_ratio: float = 0.12) -> Image.Image:
    canvas = Image.new("RGB", (SIZE, SIZE), CREAM)
    # subtle vignette-ish center lift
    overlay = Image.new("RGBA", (SIZE, SIZE), (255, 255, 255, 0))
    d = ImageDraw.Draw(overlay)
    d.ellipse([SIZE * 0.1, SIZE * 0.05, SIZE * 0.9, SIZE * 0.85], fill=(255, 255, 255, 35))
    canvas = Image.alpha_composite(canvas.convert("RGBA"), overlay).convert("RGB").convert("RGBA")

    max_h = int(SIZE * (1 - pad_ratio * 2))
    max_w = int(SIZE * (1 - pad_ratio * 2))
    ratio = min(max_w / cut.width, max_h / cut.height)
    nw, nh = int(cut.width * ratio), int(cut.height * ratio)
    prod = cut.resize((nw, nh), Image.Resampling.LANCZOS)
    prod = ImageEnhance.Sharpness(prod).enhance(1.15)
    prod = ImageEnhance.Contrast(prod).enhance(1.04)

    x = (SIZE - nw) // 2
    y = (SIZE - nh) // 2 + int(SIZE * 0.02)

    sh = soft_shadow(nw, int(nh * 0.35))
    canvas.alpha_composite(sh, (x, y + nh - int(sh.height * 0.55)))
    canvas.alpha_composite(prod, (x, y))
    return canvas.convert("RGB")


def frame_photo(path: Path) -> Image.Image:
    """Original studio photo centered on cream square — no cutout artifacts."""
    im = Image.open(path).convert("RGB")
    # crop a bit of empty edges
    w, h = im.size
    im = im.crop((int(w * 0.04), int(h * 0.02), int(w * 0.96), int(h * 0.98)))
    canvas = Image.new("RGB", (SIZE, SIZE), CREAM)
    ratio = min((SIZE * 0.9) / im.width, (SIZE * 0.92) / im.height)
    nw, nh = int(im.width * ratio), int(im.height * ratio)
    im = im.resize((nw, nh), Image.Resampling.LANCZOS)
    im = ImageEnhance.Color(im).enhance(0.98)
    im = ImageEnhance.Contrast(im).enhance(1.05)
    im = ImageEnhance.Sharpness(im).enhance(1.1)
    x = (SIZE - nw) // 2
    y = (SIZE - nh) // 2
    canvas.paste(im, (x, y))
    return canvas


def main() -> None:
    ASSETS.mkdir(exist_ok=True)
    PREVIEW.mkdir(parents=True, exist_ok=True)

    print("Building studio framed photos (clean, no jagged cutout)...")
    # Primary gallery: original photos on cream — looks real
    main_shot = frame_photo(PROD)
    box_shot = frame_photo(BOX)
    benefits = frame_photo(BEN)

    # Also make a cleaner cutout version as alternate
    print("Building improved cutouts...")
    prod_cut = match_cream(cut_clean(PROD))
    box_cut = match_cream(cut_clean(BOX))
    prod_studio = on_studio(prod_cut, pad_ratio=0.10)
    box_studio = on_studio(box_cut, pad_ratio=0.12)

    # Prefer studio-framed originals as main gallery assets (highest quality look)
    outputs = {
        "silky-nest-product-real.png": main_shot,
        "silky-nest-product.png": main_shot,
        "product-cutout-clean.png": prod_studio,
        "product-cutout.png": prod_studio,
        "silky-nest-box-real.png": box_shot,
        "silky-nest-box-side.png": box_shot,
        "silky-nest-benefits-side.jpg": benefits,
        "silky-nest-front.jpg": main_shot,
        "silky-nest-packaging.jpg": box_shot,
    }

    for folder in (ASSETS, PREVIEW):
        for name, img in outputs.items():
            path = folder / name
            if name.endswith(".png"):
                img.save(path, "PNG", optimize=True)
            else:
                img.convert("RGB").save(path, "JPEG", quality=93, optimize=True, progressive=True)
            print("wrote", path.name, img.size)

    print("DONE")


if __name__ == "__main__":
    main()
