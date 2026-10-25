"""Prepara versiones limpias de fotos del álbum: recorta un panel de los collages, quita
letreros sobrepuestos y rellena las esquinas de color de los marcos ovalados. Escribe en
fotos/limpias/<id>.jpg (y <id>b.jpg, <id>c.jpg para vistas extra) y anota en
datos/album-indice.json el archivo limpio de cada foto.
Uso: python3 herramientas/limpiar_album.py . [ids…]   (con ids, solo esas fotos; sin ids, todas)"""
import sys, json, pathlib
from PIL import Image, ImageOps, ImageFilter

raiz = pathlib.Path(sys.argv[1])
solo = set(sys.argv[2:])
ruta_idx = raiz / 'datos/album-indice.json'
indice = json.loads(ruta_idx.read_text(encoding='utf-8'))
por_id = {f['id']: f for f in indice['fotos']}
dst = raiz / 'fotos/limpias'

def quitar_texto(im, caja):
    """Rellena la caja interpolando entre la orilla de arriba y la de abajo (o, con 'h', entre izquierda y derecha)."""
    px = im.load(); W, H = im.size
    x0, y0, x1, y1 = caja[:4]; y1 = min(y1, H - 1); x1 = min(x1, W - 1)
    if len(caja) > 4 and caja[4] == 'h':
        for y in range(y0, y1):
            a = px[max(x0 - 1, 0), y]; b = px[x1, y]
            for x in range(x0, x1):
                t = (x - x0) / max(x1 - x0, 1)
                px[x, y] = tuple(round(p + (q - p) * t) for p, q in zip(a, b))
    else:
        for x in range(x0, x1):
            a = px[x, max(y0 - 1, 0)]; b = px[x, y1]
            for y in range(y0, y1):
                t = (y - y0) / max(y1 - y0, 1)
                px[x, y] = tuple(round(p + (q - p) * t) for p, q in zip(a, b))
    c = (max(x0 - 3, 0), max(y0 - 3, 0), min(x1 + 3, W), min(y1 + 3, H))
    im.paste(im.crop(c).filter(ImageFilter.GaussianBlur(2)), c[:2])
    return im

def rellenar_color(im, color, relleno, tolerancia=70):
    px = im.load(); W, H = im.size
    for y in range(H):
        for x in range(W):
            if sum(abs(p - q) for p, q in zip(px[x, y], color)) < tolerancia:
                px[x, y] = relleno
    return im

# id: (recorte del panel principal o None, letreros a borrar, (color de esquinas, relleno) o None)
PRINCIPAL = {
    'a059': ((0, 0, 636, 1280), [], None),
    'a034': ((0, 0, 636, 1280), [], None),
    'a027': ((0, 0, 604, 1280), [], None),
    'a146': ((439, 0, 813, 1280), [], None),
    'a002': ((0, 0, 632, 1280), [], ((25, 65, 245), (250, 250, 250))),
    'a069': ((0, 0, 640, 1280), [], ((250, 245, 20), (215, 205, 190))),
    'a153': ((337, 0, 719, 1280), [], ((140, 70, 220), (240, 236, 230))),
    'a020': ((0, 74, 540, 886), [], None),
    'a144': (None, [(146, 388, 243, 425)], None),
    'a005': (None, [(200, 1150, 500, 1235)], None),
    'a016': (None, [(672, 420, 952, 540, 'h')], None),
    'a065': ((195, 14, 367, 550), [], None),  # el ave azul, panel central de un collage (no hay otra foto)
}
# vistas extra: id nuevo -> (id de origen, recorte)
EXTRAS = {
    'a059b': ('a059', (644, 0, 1280, 1280)),
    'a034b': ('a034', (643, 0, 1280, 1280)),
    'a146b': ('a146', (0, 0, 385, 1280)),
    'a146c': ('a146', (861, 0, 1280, 1280)),
    'a027b': ('a027', (644, 8, 1272, 1272)),   # la otra foto del pavo real, sobre una pared azul
    'a051c': ('a051', (856, 166, 1272, 1114)),  # el coyote del collage de tres máscaras (las otras dos ya están en la galería)
}

def abrir(fid):
    return ImageOps.exif_transpose(Image.open(raiz / 'fotos/album' / por_id[fid]['archivo'])).convert('RGB')

for fid, (caja, letreros, esquinas) in PRINCIPAL.items():
    if solo and fid not in solo: continue
    im = abrir(fid)
    if caja: im = im.crop(caja)
    for l in letreros: im = quitar_texto(im, l)
    if esquinas: im = rellenar_color(im, *esquinas)
    im.save(dst / f'{fid}.jpg', quality=95)
    por_id[fid]['limpia'] = f'fotos/limpias/{fid}.jpg'
for nid, (origen, caja) in EXTRAS.items():
    if solo and nid not in solo: continue
    abrir(origen).crop(caja).save(dst / f'{nid}.jpg', quality=95)
    if nid not in por_id:
        e = {'id': nid, 'archivo': por_id[origen]['archivo'], 'vista_de': origen}
        indice['fotos'].append(e); por_id[nid] = e
    por_id[nid]['limpia'] = f'fotos/limpias/{nid}.jpg'
# las dos que ya se habían limpiado antes
por_id['a164']['limpia'] = 'fotos/limpias/borrego-anaranjado.jpg'
por_id['a166']['limpia'] = 'fotos/limpias/lince.jpg'
ruta_idx.write_text(json.dumps(indice, ensure_ascii=False, indent=1), encoding='utf-8')
print('ok', len(PRINCIPAL), 'limpias,', len(EXTRAS), 'vistas extra')
