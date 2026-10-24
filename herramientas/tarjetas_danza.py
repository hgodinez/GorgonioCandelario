"""Genera las fotos de las tarjetas de las parejas de la danza (proporción 3:4) con la
máscara completa: encuadra la caja de la máscara anotada en datos/danza.json («caja»,
[izq, arriba, der, abajo] en pixeles de la foto) y, si la foto no alcanza, prolonga la
pared con el color de su orilla (sin reflejar nada de lo que hay junto a la máscara).
Escribe img/mascaras/<slug>-tarjeta-<ancho>.webp y .jpg y anota «tarjeta» en datos/danza.json.
Requiere Pillow y numpy. Uso: python3 herramientas/tarjetas_danza.py . [parejas…]
(con nombres de parejas, por ejemplo Perros, solo rehace esas tarjetas; sin nombres, todas)."""
import json, math, re, sys, pathlib
import numpy as np
from PIL import Image, ImageOps

PROPORCION = 3 / 4   # ancho / alto de la tarjeta
MARGEN = 0.06        # aire alrededor de la máscara, en fracción de su alto
MARGEN_MIN = 0.05    # si la foto no da para MARGEN, al menos esto (se completa con pared)
ANCHOS = (360, 540, 720)
SALTO, BANDA = 3, 16  # la orilla de la pared se mide en una banda de 16 px, sin los 3 px del borde

raiz = pathlib.Path(sys.argv[1])
solo = set(sys.argv[2:])
ruta = raiz / 'datos/danza.json'
danza = json.loads(ruta.read_text(encoding='utf-8'))
fotos = {f['archivo']: f for f in json.loads((raiz / 'datos/mascaras.json').read_text(encoding='utf-8'))['fotos']}


def origen(archivo):
    limpia = raiz / 'fotos/limpias' / archivo
    return limpia if limpia.exists() else raiz / 'fotos/originales' / archivo


def ventana(W, H, caja):
    """Ventana (x, y, ancho, alto) en pixeles de la foto; puede salirse de ella (eso se llena con pared)."""
    x0, y0, x1, y1 = caja
    bw, bh = x1 - x0, y1 - y0

    def extremos(lo, hi, total, b):
        """Hasta dónde debe llegar la ventana en un eje. Cada lado lleva MARGEN si la foto lo tiene
        y nunca menos de MARGEN_MIN (lo que falte es pared); el lado donde la máscara toca la orilla
        de la foto no lleva margen, para no inventar pared junto a un corte."""
        a = 0 if lo <= 1 else lo - max(MARGEN_MIN * b, min(MARGEN * b, lo))
        z = total if hi >= total - 1 else hi + max(MARGEN_MIN * b, min(MARGEN * b, total - hi))
        return a, z

    ay, zy = extremos(y0, y1, H, bh)
    ax, zx = extremos(x0, x1, W, bw)
    alto, ancho = zy - ay, zx - ax
    if ancho < alto * PROPORCION:
        ancho = alto * PROPORCION
    else:  # máscara ancha: manda el ancho
        alto = ancho / PROPORCION
    ancho, alto = round(ancho), round(alto)

    def colocar(lado, total, a, z, lo, hi):
        """Inicio de la ventana en un eje: cubre [a, z], no pone pared antes de una orilla que la
        máscara toca, aprovecha toda la foto que pueda y, dentro de eso, se centra en la máscara."""
        p, q = z - lado, a
        if lo <= 1:
            p = max(p, 0)
        if hi >= total - 1:
            q = min(q, total - lado)
        r, t = (0, total - lado) if lado <= total else (total - lado, 0)
        centrado = round((lo + hi) / 2 - lado / 2)

        def entre(u, v, x):  # x en [u, v] con pixeles enteros; si no cabe ninguno, el punto medio
            a_, b_ = math.ceil(u), math.floor(v)
            return min(max(x, a_), b_) if a_ <= b_ else round((u + v) / 2)
        if p > q:
            if lo <= 1 and hi >= total - 1 and lado > total:  # toca las dos orillas y falta espacio
                return centrado
            x = round((p + q) / 2)  # diferencia de redondeo, menor a un pixel
            if lo <= 1:
                x = max(x, 0)
            if hi >= total - 1:
                x = min(x, total - lado)
            return x
        if max(p, r) <= min(q, t):  # se puede cumplir el margen usando toda la foto posible
            return entre(max(p, r), min(q, t), centrado)
        # no se puede: el extremo de [p, q] más cercano a lo que aprovecha la foto
        return entre(p, q, math.floor(q) if q < r else math.ceil(p))

    return colocar(ancho, W, ax, zx, x0, x1), colocar(alto, H, ay, zy, y0, y1), ancho, alto


def suavizar(v, sigma):
    """Mediana móvil (quita detalles angostos como la punta de un cuerno o un clavo junto a la
    orilla) y luego promedio gaussiano, a lo largo del primer eje (v: n x 3)."""
    m = max(5, round(len(v) * 0.04)) | 1
    if len(v) > m:
        p = np.pad(v, ((m // 2, m // 2), (0, 0)), mode='edge')
        v = np.median(np.lib.stride_tricks.sliding_window_view(p, m, axis=0), axis=-1)
    r = max(1, round(3 * sigma))
    k = np.exp(-0.5 * (np.arange(-r, r + 1) / sigma) ** 2)
    k /= k.sum()
    p = np.pad(v, ((r, r), (0, 0)), mode='edge')
    return np.stack([np.convolve(p[:, c], k, mode='valid') for c in range(v.shape[1])], axis=1)


def prolongar(lienzo, foto_caja, caja_masc, semilla):
    """lienzo: la ventana con la foto pegada en foto_caja. Lo que queda fuera de la foto se llena
    fila por fila (o columna por columna) con la mediana de una banda de pared junto a la orilla
    de la foto, suavizada, más un grano parecido al de la pared."""
    a = np.asarray(lienzo, dtype=np.float32).copy()
    h, w = a.shape[:2]
    fx0, fy0, fx1, fy1 = foto_caja
    mx0, my0, mx1, my1 = caja_masc
    azar = np.random.default_rng(semilla)
    sigma = max(2.0, h * 0.01)
    # color de reserva: la orilla de la foto (2 px) fuera de la caja de la máscara
    anillo = np.zeros((h, w), bool)
    anillo[fy0:fy1, fx0:fx1] = True
    anillo[fy0 + 2:fy1 - 2, fx0 + 2:fx1 - 2] = False
    fuera = anillo.copy()
    fuera[max(my0, 0):max(my1, 0), max(mx0, 0):max(mx1, 0)] = False
    reserva = np.median(a[fuera] if fuera.any() else a[anillo], axis=0)

    def banda(inicio, limite, hacia):
        """Rango de la banda de pared desde la orilla `inicio` hacia la máscara (`limite`)."""
        hueco = abs(limite - inicio)
        salto = min(SALTO, hueco // 4)
        largo = min(BANDA, hueco - salto)
        if largo < 2:
            return None
        b0 = inicio + hacia * salto
        b1 = b0 + hacia * largo
        return (min(b0, b1), max(b0, b1))

    def llenar(pad, muestra, eje, borde, lado):
        """pad: (filas, columnas) del arreglo a llenar; muestra: banda de pared (o None);
        borde: (filas, columnas) dentro de la foto junto a la orilla, donde la textura real se
        funde con el relleno; lado: +1 si el relleno queda antes de la orilla (izq./arriba), -1 si después."""
        region = a[pad]
        if muestra is None or muestra.size == 0:
            region[...] = reserva
            return
        perfil = np.median(muestra, axis=eje)  # colores a lo largo de la orilla
        perfil = suavizar(perfil, sigma)
        resto = muestra - np.expand_dims(perfil, eje)
        grano = min(6.0, 1.4826 * float(np.median(np.abs(resto - np.median(resto)))))  # dispersión robusta
        base = np.expand_dims(perfil, eje)
        region[...] = base + azar.normal(0, 1, region.shape[:2])[..., None] * grano
        zona = a[borde]
        n = zona.shape[eje]
        if n:
            # peso 0.85 junto a la orilla que baja a 0 hacia adentro de la foto
            d = np.arange(n) if lado == 1 else np.arange(n)[::-1]
            peso = 0.85 * (1 - (d + 0.5) / n)
            peso = peso[None, :, None] if eje == 1 else peso[:, None, None]
            relleno = base + azar.normal(0, 1, zona.shape[:2])[..., None] * grano
            zona[...] = zona * (1 - peso) + relleno * peso

    def ancho_borde(inicio, limite):
        return max(0, min(14, abs(limite - inicio) // 3))

    if fx0 > 0:
        r = banda(fx0, mx0, 1)
        f = ancho_borde(fx0, mx0)
        llenar((slice(fy0, fy1), slice(0, fx0)), a[fy0:fy1, r[0]:r[1]] if r else None, 1,
               (slice(fy0, fy1), slice(fx0, fx0 + f)), 1)
    if fx1 < w:
        r = banda(fx1, mx1, -1)
        f = ancho_borde(fx1, mx1)
        llenar((slice(fy0, fy1), slice(fx1, w)), a[fy0:fy1, r[0]:r[1]] if r else None, 1,
               (slice(fy0, fy1), slice(fx1 - f, fx1)), -1)
    # arriba y abajo, a todo lo ancho (incluye los lados ya prolongados)
    if fy0 > 0:
        r = banda(fy0, my0, 1)
        f = ancho_borde(fy0, my0)
        llenar((slice(0, fy0), slice(0, w)), a[r[0]:r[1], :] if r else None, 0,
               (slice(fy0, fy0 + f), slice(0, w)), 1)
    if fy1 < h:
        r = banda(fy1, my1, -1)
        f = ancho_borde(fy1, my1)
        llenar((slice(fy1, h), slice(0, w)), a[r[0]:r[1], :] if r else None, 0,
               (slice(fy1 - f, fy1), slice(0, w)), -1)
    return Image.fromarray(np.clip(a, 0, 255).round().astype(np.uint8), 'RGB')


def borrar_tarjetas(slug, menos=()):
    for f in (raiz / 'img/mascaras').glob(f'{slug}-tarjeta-*'):
        m = re.fullmatch(rf'{re.escape(slug)}-tarjeta-(\d+)\.(webp|jpg)', f.name)
        if m and int(m.group(1)) not in menos:
            f.unlink()


# primero se revisan todas las cajas, para no dejar el trabajo a medias
for par in danza['parejas']:
    if par.get('archivo') and par.get('caja'):
        W, H = ImageOps.exif_transpose(Image.open(origen(par['archivo']))).size
        x0, y0, x1, y1 = par['caja']
        if not (0 <= x0 < x1 <= W and 0 <= y0 < y1 <= H):
            sys.exit(f'La caja de «{par["nombre"]}» {par["caja"]} se sale de la foto ({W}x{H}).')

for n, par in enumerate(danza['parejas']):
    if solo and par['nombre'] not in solo:
        continue
    if not par.get('archivo') or not par.get('caja'):
        if par.get('archivo') in fotos:
            borrar_tarjetas(fotos[par['archivo']]['slug'])
        par.pop('tarjeta', None)
        continue
    im = ImageOps.exif_transpose(Image.open(origen(par['archivo']))).convert('RGB')
    W, H = im.size
    x0, y0, x1, y1 = par['caja']
    wx, wy, ancho, alto = ventana(W, H, par['caja'])
    lienzo = Image.new('RGB', (ancho, alto))
    lienzo.paste(im.crop((max(wx, 0), max(wy, 0), min(wx + ancho, W), min(wy + alto, H))), (max(-wx, 0), max(-wy, 0)))
    foto_caja = (max(-wx, 0), max(-wy, 0), min(W - wx, ancho), min(H - wy, alto))
    rellena = foto_caja != (0, 0, ancho, alto)
    if rellena:
        lienzo = prolongar(lienzo, foto_caja, (x0 - wx, y0 - wy, x1 - wx, y1 - wy), semilla=n)
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
    borrar_tarjetas(slug, hechos)  # tamaños viejos que ya no se usan
    # «archivo» liga la tarjeta con su foto: si cambia la foto, generar_galeria.py pide volver a correr esto
    par['tarjeta'] = {'archivo': par['archivo'], 'slug': f'{slug}-tarjeta', 'tamanos': hechos}
    print(par['nombre'], (wx, wy, ancho, alto), 'con pared prolongada' if rellena else '', hechos)

ruta.write_text(json.dumps(danza, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
