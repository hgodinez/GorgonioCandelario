"""Genera los acercamientos de la sección de técnica a partir de datos/detalles.json.
Uso: python3 herramientas/detalles.py ."""
import sys, json, pathlib
from PIL import Image, ImageOps

raiz = pathlib.Path(sys.argv[1])
datos = json.loads((raiz / 'datos/detalles.json').read_text(encoding='utf-8'))
dst = raiz / 'img/detalles'
dst.mkdir(parents=True, exist_ok=True)
for d in datos['detalles']:
    im = ImageOps.exif_transpose(Image.open(raiz / 'fotos/originales' / d['archivo'])).convert('RGB')
    x0, y0, x1, y1 = d['caja']
    lado = round((x1 - x0) * im.width)
    izq, arr = round(x0 * im.width), round(y0 * im.height)
    rec = im.crop((izq, arr, izq + lado, arr + lado))
    tamanos = []
    for w in (360, 720):
        ww = min(w, lado)
        if ww in tamanos:
            break
        r = rec.resize((ww, ww), Image.LANCZOS)
        r.save(dst / f'{d["id"]}-{ww}.webp', 'WEBP', quality=80, method=6)
        r.save(dst / f'{d["id"]}-{ww}.jpg', 'JPEG', quality=82, optimize=True, progressive=True)
        tamanos.append(ww)
    d['tamanos'] = tamanos
(raiz / 'datos/detalles.json').write_text(json.dumps(datos, ensure_ascii=False, indent=1), encoding='utf-8')
print('ok', [(d['id'], d['tamanos']) for d in datos['detalles']])
