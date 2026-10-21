"""Genera las fotos de las tarjetas de las parejas de la danza (proporción 3:4) con la
máscara completa: encuadra la caja de la máscara anotada en datos/danza.json («caja»,
[izq, arriba, der, abajo] en pixeles de la foto) y, si la foto no alcanza, prolonga la
pared reflejando la franja de fondo que hay junto a la máscara.
Escribe img/mascaras/<slug>-tarjeta-<ancho>.webp y .jpg y anota «tarjeta» en datos/danza.json.
Uso: python3 herramientas/tarjetas_danza.py ."""
import json, sys, pathlib
from PIL import Image, ImageOps, ImageFilter

PROPORCION = 3 / 4   # ancho / alto de la tarjeta
MARGEN = 0.06        # aire alrededor de la máscara, en fracción de su alto
MARGEN_MIN = 0.03    # si la foto no da para MARGEN, al menos esto (se completa con pared)
ANCHOS = (360, 540, 720)

raiz = pathlib.Path(sys.argv[1])
ruta = raiz / 'datos/danza.json'
danza = json.loads(ruta.read_text(encoding='utf-8'))
fotos = {f['archivo']: f for f in json.loads((raiz / 'datos/mascaras.json').read_text(encoding='utf-8'))['fotos']}


def origen(archivo):
    limpia = raiz / 'fotos/limpias' / archivo
    return limpia if limpia.exists() else raiz / 'fotos/originales' / archivo


def ventana(W, H, caja):
    x0, y0, x1, y1 = caja
    bw, bh = x1 - x0, y1 - y0
    alto = bh * (1 + 2 * MARGEN)
    if alto > H:  # la foto no da: usar todo el alto, sin bajar del margen mínimo
        alto = max(H, bh * (1 + 2 * MARGEN_MIN))
    ancho = alto * PROPORCION
    if ancho < bw * (1 + 2 * MARGEN):  # máscara ancha: manda el ancho
        ancho = bw * (1 + 2 * MARGEN)
        alto = ancho / PROPORCION
    ancho, alto = round(ancho), round(alto)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2

    def colocar(centro, lado, total, lo, hi):
        inicio = round(centro - lado / 2)
        if lado <= total:  # cabe: se recorre para no salirse de la foto
            inicio = min(max(inicio, 0), total - lado)
        elif lo <= 1:  # la máscara toca la orilla de la foto: no se inventa pared de ese lado
            inicio = 0
        elif hi >= total - 1:
            inicio = total - lado
        return inicio
    wx, wy = colocar(cx, ancho, W, x0, x1), colocar(cy, alto, H, y0, y1)
    return wx, wy, ancho, alto


def mosaico_espejo(franja, largo, eje):
    """Tira de al menos `largo` pixeles que sigue a la franja hacia la derecha (eje x) o hacia
    abajo (eje y): la franja reflejada, luego la original, y así sucesivamente."""
    piezas, n = [], 0
    while n < largo:
        p = (ImageOps.mirror(franja) if eje == 'x' else ImageOps.flip(franja)) if len(piezas) % 2 == 0 else franja
        piezas.append(p)
        n += p.width if eje == 'x' else p.height
    if eje == 'x':
        tira = Image.new('RGB', (n, franja.height))
        x = 0
        for p in piezas:
            tira.paste(p, (x, 0)); x += p.width
        return tira
    tira = Image.new('RGB', (franja.width, n))
    y = 0
    for p in piezas:
        tira.paste(p, (0, y)); y += p.height
    return tira


def prolongar(lienzo, foto_caja, caja_masc):
    """lienzo: la ventana con la foto pegada en foto_caja; rellena lo que queda fuera de la foto."""
    fx0, fy0, fx1, fy1 = foto_caja
    mx0, my0, mx1, my1 = caja_masc
    w, h = lienzo.size
    relleno = Image.new('L', (w, h), 0)
    # izquierda y derecha, con las filas que tiene la foto
    if fx0 > 0:
        franja = lienzo.crop((fx0, fy0, max(fx0 + 1, mx0), fy1))
        # hacia la izquierda: se refleja la franja reflejada y se voltea la tira
        tira = ImageOps.mirror(mosaico_espejo(ImageOps.mirror(franja), fx0, 'x'))
        tira = tira.crop((tira.width - fx0, 0, tira.width, tira.height))
        lienzo.paste(tira, (0, fy0)); relleno.paste(255, (0, fy0, fx0, fy1))
    if fx1 < w:
        franja = lienzo.crop((min(fx1 - 1, mx1), fy0, fx1, fy1))
        tira = mosaico_espejo(franja, w - fx1, 'x').crop((0, 0, w - fx1, fy1 - fy0))
        lienzo.paste(tira, (fx1, fy0)); relleno.paste(255, (fx1, fy0, w, fy1))
    # arriba y abajo, ya con los lados prolongados
    if fy0 > 0:
        franja = lienzo.crop((0, fy0, w, max(fy0 + 1, my0)))
        tira = ImageOps.flip(mosaico_espejo(ImageOps.flip(franja), fy0, 'y'))
        tira = tira.crop((0, tira.height - fy0, w, tira.height))
        lienzo.paste(tira, (0, 0)); relleno.paste(255, (0, 0, w, fy0))
    if fy1 < h:
        franja = lienzo.crop((0, min(fy1 - 1, my1), w, fy1))
        tira = mosaico_espejo(franja, h - fy1, 'y').crop((0, 0, w, h - fy1))
        lienzo.paste(tira, (0, fy1)); relleno.paste(255, (0, fy1, w, h))
    if relleno.getbbox():
        # la pared prolongada se difumina poco a poco, para que no se note el reflejo
        radio = max(2, round(w * 0.012))
        suave = lienzo.filter(ImageFilter.GaussianBlur(radio))
        # de 0 junto a la foto a 255 unos pixeles hacia afuera
        transicion = relleno.filter(ImageFilter.GaussianBlur(max(3, round(w * 0.02))))
        transicion = transicion.point(lambda v: max(0, min(255, (v - 128) * 2)))
        transicion = Image.composite(transicion, Image.new('L', (w, h), 0), relleno)
        lienzo = Image.composite(suave, lienzo, transicion)
    return lienzo


for par in danza['parejas']:
    if not par.get('archivo') or not par.get('caja'):
        continue
    im = ImageOps.exif_transpose(Image.open(origen(par['archivo']))).convert('RGB')
    W, H = im.size
    wx, wy, ancho, alto = ventana(W, H, par['caja'])
    lienzo = Image.new('RGB', (ancho, alto))
    lienzo.paste(im.crop((max(wx, 0), max(wy, 0), min(wx + ancho, W), min(wy + alto, H))), (max(-wx, 0), max(-wy, 0)))
    foto_caja = (max(-wx, 0), max(-wy, 0), min(W - wx, ancho), min(H - wy, alto))
    x0, y0, x1, y1 = par['caja']
    lienzo = prolongar(lienzo, foto_caja, (x0 - wx, y0 - wy, x1 - wx, y1 - wy))
    slug = fotos[par['archivo']]['slug']
    hechos = []
    for a in ANCHOS:
        a = min(a, ancho)
        if a in hechos:
            break
        t = lienzo.resize((a, round(a / PROPORCION)), Image.LANCZOS)
        t.save(raiz / f'img/mascaras/{slug}-tarjeta-{a}.webp', 'WEBP', quality=82, method=6)
        t.save(raiz / f'img/mascaras/{slug}-tarjeta-{a}.jpg', 'JPEG', quality=82, optimize=True, progressive=True)
        hechos.append(a)
    par['tarjeta'] = {'slug': f'{slug}-tarjeta', 'tamanos': hechos}
    print(par['nombre'], (wx, wy, ancho, alto), 'relleno' if (wx < 0 or wy < 0 or wx + ancho > W or wy + alto > H) else '', hechos)

ruta.write_text(json.dumps(danza, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
