"""Genera versiones web (WebP y JPG en varios anchos) de las fotos originales.
Uso: python3 herramientas/optimizar.py fotos/originales img/mascaras"""
import sys, json, pathlib
from PIL import Image, ImageOps
src, dst = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
dst.mkdir(parents=True, exist_ok=True)
WIDTHS = [480, 960, 1440]
meta = {}
for f in sorted(src.glob('*.jpg')):
    im = ImageOps.exif_transpose(Image.open(f)).convert('RGB')
    slug = f.stem.replace('IMG-20250829-WA', 'mascara-')
    out = []
    for w in WIDTHS:
        ww = min(w, im.width)
        if ww in out:
            break
        r = im.resize((ww, round(im.height * ww / im.width)), Image.LANCZOS)
        r.save(dst / f'{slug}-{ww}.webp', 'WEBP', quality=80, method=6)
        r.save(dst / f'{slug}-{ww}.jpg', 'JPEG', quality=82, optimize=True, progressive=True)
        out.append(ww)
    meta[f.name] = {'slug': slug, 'w': im.width, 'h': im.height, 'sizes': out}
print(json.dumps(meta, indent=1))
