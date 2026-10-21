"""Genera las versiones web de las fotos del álbum (fotos/album) para la galería.
Uso: python3 herramientas/optimizar_album.py .
Escribe img/galeria/<id>-<ancho>.webp (y un .jpg de respaldo en 800) y datos/album-tamanos.json."""
import sys, json, pathlib
from PIL import Image, ImageOps

raiz = pathlib.Path(sys.argv[1])
indice = json.loads((raiz / 'datos/album-indice.json').read_text(encoding='utf-8'))
# fotos a las que ya se les quitó un texto sobrepuesto
LIMPIAS = {'IMG-20261020-WA0086.jpg': 'fotos/limpias/borrego-anaranjado.jpg', 'IMG-20261020-WA0088.jpg': 'fotos/limpias/lince.jpg'}
dst = raiz / 'img/galeria'
dst.mkdir(parents=True, exist_ok=True)
tamanos = {}
for f in indice['fotos']:
    origen = raiz / LIMPIAS.get(f['archivo'], 'fotos/album/' + f['archivo'])
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
    tamanos[f['id']] = {'w': im.width, 'h': im.height, 'tamanos': hechos}
(raiz / 'datos/album-tamanos.json').write_text(json.dumps(tamanos, indent=1), encoding='utf-8')
print('ok', len(tamanos))
