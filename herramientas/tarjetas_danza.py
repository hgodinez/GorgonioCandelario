"""Genera las fotos de las tarjetas de las parejas de la danza (proporción 3:4) con la
máscara completa: encuadra la caja de la máscara anotada en datos/danza.json («caja»,
[izq, arriba, der, abajo] en pixeles de la foto) y, si la foto no alcanza, prolonga la
pared con el color de su orilla (sin reflejar nada de lo que hay junto a la máscara).
Escribe img/mascaras/<slug>-tarjeta-<ancho>.webp y .jpg y anota «tarjeta» en datos/danza.json.
Requiere Pillow y numpy. Uso: python3 herramientas/tarjetas_danza.py ."""
import json, sys, pathlib
import numpy as np
from PIL import Image, ImageOps

PROPORCION = 3 / 4   # ancho / alto de la tarjeta
MARGEN = 0.06        # aire alrededor de la máscara, en fracción de su alto
MARGEN_MIN = 0.03    # si la foto no da para MARGEN, al menos esto (se completa con pared)
ANCHOS = (360, 540, 720)
SALTO, BANDA = 3, 16  # la orilla de la pared se mide en una banda de 16 px, sin los 3 px del borde

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
    toca_v = y0 <= 1 and y1 >= H - 1  # la máscara toca arriba y abajo: no cabe pared en ese eje
    toca_h = x0 <= 1 and x1 >= W - 1
    alto = bh * (1 + 2 * MARGEN)
    if alto > H:  # la foto no da: usar todo el alto, sin bajar del margen mínimo
        alto = H if toca_v else max(H, bh * (1 + 2 * MARGEN_MIN))
    ancho = alto * PROPORCION
    minimo = W if toca_h else bw * (1 + 2 * MARGEN)
    if ancho < minimo:  # máscara ancha: manda el ancho
        ancho = minimo
        alto = ancho / PROPORCION
    ancho, alto = round(ancho), round(alto)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2

    def colocar(centro, lado, total, lo, hi):
        inicio = round(centro - lado / 2)
        if lado <= total:  # cabe: se recorre para no salirse de la foto
            inicio = min(max(inicio, 0), total - lado)
        elif lo <= 1 and hi < total - 1:  # la máscara toca la orilla: no se inventa pared de ese lado
            inicio = 0
        elif hi >= total - 1 and lo > 1:
            inicio = total - lado
        return inicio
    wx, wy = colocar(cx, ancho, W, x0, x1), colocar(cy, alto, H, y0, y1)
    return wx, wy, ancho, alto


def suavizar(v, sigma):
    """Promedio gaussiano a lo largo del primer eje (v: n x 3)."""
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
    # color de reserva: la orilla de la foto fuera de la caja de la máscara
    orilla = np.concatenate([a[fy0:fy1, fx0:fx0 + 2].reshape(-1, 3), a[fy0:fy1, fx1 - 2:fx1].reshape(-1, 3),
                             a[fy0:fy0 + 2, fx0:fx1].reshape(-1, 3), a[fy1 - 2:fy1, fx0:fx1].reshape(-1, 3)])
    reserva = np.median(orilla, axis=0)

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


for n, par in enumerate(danza['parejas']):
    if not par.get('archivo') or not par.get('caja'):
        par.pop('tarjeta', None)
        continue
    im = ImageOps.exif_transpose(Image.open(origen(par['archivo']))).convert('RGB')
    W, H = im.size
    wx, wy, ancho, alto = ventana(W, H, par['caja'])
    lienzo = Image.new('RGB', (ancho, alto))
    lienzo.paste(im.crop((max(wx, 0), max(wy, 0), min(wx + ancho, W), min(wy + alto, H))), (max(-wx, 0), max(-wy, 0)))
    foto_caja = (max(-wx, 0), max(-wy, 0), min(W - wx, ancho), min(H - wy, alto))
    x0, y0, x1, y1 = par['caja']
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
    # «archivo» liga la tarjeta con su foto: si cambia la foto, generar_galeria.py pide volver a correr esto
    par['tarjeta'] = {'archivo': par['archivo'], 'slug': f'{slug}-tarjeta', 'tamanos': hechos}
    print(par['nombre'], (wx, wy, ancho, alto), 'con pared prolongada' if rellena else '', hechos)

ruta.write_text(json.dumps(danza, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
