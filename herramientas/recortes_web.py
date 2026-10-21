"""Convierte los recortes aprobados (WebP con transparencia hechos con recortar_fondo.py)
a tamaños web en img/galeria/recortes y anota sus medidas en datos/album-tamanos.json.
Uso: python3 herramientas/recortes_web.py . carpeta_recortes id1 [id2 ...]"""
import sys, json, pathlib
from PIL import Image

raiz, recortes, ids = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]), sys.argv[3:]
LIMPIAS = {'IMG-20261020-WA0086.jpg': 'borrego-anaranjado', 'IMG-20261020-WA0088.jpg': 'lince'}
indice = {f['id']: f for f in json.loads((raiz / 'datos/album-indice.json').read_text(encoding='utf-8'))['fotos']}
ruta_tam = raiz / 'datos/album-tamanos.json'
tam = json.loads(ruta_tam.read_text(encoding='utf-8'))
dst = raiz / 'img/galeria/recortes'
dst.mkdir(parents=True, exist_ok=True)
for fid in ids:
    archivo = indice[fid]['archivo']
    im = Image.open(recortes / (LIMPIAS.get(archivo, pathlib.Path(archivo).stem) + '.webp')).convert('RGBA')
    hechos = []
    for w in (400, 800, 1400):
        ww = min(w, im.width)
        if ww in hechos:
            break
        im.resize((ww, round(im.height * ww / im.width)), Image.LANCZOS).save(dst / f'{fid}-{ww}.webp', 'WEBP', quality=82, method=6)
        hechos.append(ww)
    tam[fid].update(recorte_w=im.width, recorte_h=im.height, recorte_tamanos=hechos)
ruta_tam.write_text(json.dumps(tam, indent=1), encoding='utf-8')
print('ok', len(ids))
