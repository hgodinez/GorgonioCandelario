"""Quita el fondo de las fotos con el modelo isnet-general-use (rembg / DIS) y guarda
WebP con transparencia. Requiere onnxruntime, numpy y Pillow, y el modelo:
https://github.com/danielgatis/rembg/releases/download/v0.0.0/isnet-general-use.onnx
Uso: python3 herramientas/recortar_fondo.py modelo.onnx carpeta_salida foto1.jpg [foto2.jpg ...]"""
import sys, pathlib
import numpy as np
import onnxruntime as ort
from PIL import Image, ImageOps

modelo, salida, fotos = sys.argv[1], pathlib.Path(sys.argv[2]), sys.argv[3:]
salida.mkdir(parents=True, exist_ok=True)
sesion = ort.InferenceSession(modelo, providers=['CPUExecutionProvider'])
entrada = sesion.get_inputs()[0].name

def mascara(im):
    x = np.asarray(im.convert('RGB').resize((1024, 1024), Image.LANCZOS), dtype=np.float32)
    x = x / max(float(x.max()), 1e-6) - 0.5
    pred = sesion.run(None, {entrada: x.transpose(2, 0, 1)[None]})[0][0, 0]
    pred = (pred - pred.min()) / max(float(pred.max() - pred.min()), 1e-6)
    return Image.fromarray((pred * 255).astype('uint8'), 'L').resize(im.size, Image.LANCZOS)

for f in fotos:
    im = ImageOps.exif_transpose(Image.open(f)).convert('RGB')
    m = mascara(im)
    # endurece un poco los bordes semitransparentes del fondo
    m = m.point(lambda v: 0 if v < 20 else (255 if v > 235 else round((v - 20) * 255 / 215)))
    rgba = im.copy(); rgba.putalpha(m)
    # recorta al contenido con un margen
    caja = m.point(lambda v: 255 if v > 40 else 0).getbbox()
    if caja:
        mx, my = round(im.width * 0.03), round(im.height * 0.03)
        caja = (max(caja[0] - mx, 0), max(caja[1] - my, 0), min(caja[2] + mx, im.width), min(caja[3] + my, im.height))
        rgba = rgba.crop(caja)
    destino = salida / (pathlib.Path(f).stem + '.webp')
    rgba.save(destino, 'WEBP', quality=85, method=6)
    print(destino.name, rgba.size)
