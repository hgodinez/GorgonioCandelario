"""Borra un texto sobrepuesto en una zona lisa de pared, interpolando entre los pixeles
de arriba y de abajo de la caja. Uso:
python3 herramientas/quitar_texto.py entrada.jpg salida.jpg izq arriba der abajo"""
import sys
from PIL import Image, ImageFilter

src, dst = sys.argv[1], sys.argv[2]
x0, y0, x1, y1 = map(int, sys.argv[3:7])
im = Image.open(src).convert('RGB')
px = im.load()
W, H = im.size
y1 = min(y1, H - 1)
for x in range(x0, x1):
    arriba = px[x, max(y0 - 1, 0)]
    abajo = px[x, y1] if y1 < H - 1 else arriba
    for y in range(y0, y1):
        t = (y - y0) / max(y1 - y0, 1)
        px[x, y] = tuple(round(a + (b - a) * t) for a, b in zip(arriba, abajo))
caja = (max(x0 - 3, 0), max(y0 - 3, 0), min(x1 + 3, W), min(y1 + 3, H))
im.paste(im.crop(caja).filter(ImageFilter.GaussianBlur(2)), caja[:2])
im.save(dst, quality=95)
