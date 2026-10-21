"""Genera las versiones web de las fotos del álbum (fotos/album) para la galería.
Uso: python3 herramientas/optimizar_album.py . [ids…]   (con ids, solo esas fotos; sin ids, todas)
Escribe img/galeria/<id>-<ancho>.webp (y un .jpg de respaldo en 800) y datos/album-tamanos.json."""
import sys, json, pathlib
from PIL import Image, ImageOps

raiz = pathlib.Path(sys.argv[1])
indice = json.loads((raiz / 'datos/album-indice.json').read_text(encoding='utf-8'))
dst = raiz / 'img/galeria'
dst.mkdir(parents=True, exist_ok=True)
# conserva lo que ya hay (por ejemplo, las medidas de los recortes del desfile)
ruta_tam = raiz / 'datos/album-tamanos.json'
tamanos = json.loads(ruta_tam.read_text(encoding='utf-8')) if ruta_tam.exists() else {}
solo = set(sys.argv[2:])
for f in indice['fotos']:
    if solo and f['id'] not in solo:
        continue
    for viejo in dst.glob(f'{f["id"]}-*.webp'):  # los tamaños de antes (si la foto cambió de ancho)
        viejo.unlink()
    # versión limpia (sin letreros ni collage) si existe; ver limpiar_album.py
    origen = raiz / f.get('limpia', 'fotos/album/' + f['archivo'])
    im = ImageOps.exif_transpose(Image.open(origen)).convert('RGB')
    hechos = []
    for w in (400, 800, 1400):
        ww = min(w, im.width)
        if ww in hechos:
            break
        r = im.resize((ww, round(im.height * ww / im.width)), Image.LANCZOS)
        r.save(dst / f'{f["id"]}-{ww}.webp', 'WEBP', quality=80, method=6)
        if w == 800 or ww == im.width and 800 not in hechos and ww < 800:
            r.save(dst / f'{f["id"]}.jpg', 'JPEG', quality=80, optimize=True, progressive=True)
        hechos.append(ww)
    tamanos.setdefault(f['id'], {}).update(w=im.width, h=im.height, tamanos=hechos)
ruta_tam.write_text(json.dumps(tamanos, indent=1), encoding='utf-8')
print('ok', len(tamanos))
