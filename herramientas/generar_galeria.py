"""Uso: python3 herramientas/generar_galeria.py .

Genera los bloques de HTML (portada, imagen de la danza, parejas de la danza y
acercamientos de la técnica; la galería la genera generar_galeria_completa.py) a partir de datos/mascaras.json, datos/danza.json y
datos/detalles.json, y los inserta en index.html en lugar de los comentarios marcadores."""
import json, sys, html, re, pathlib

raiz = pathlib.Path(sys.argv[1])
datos = json.loads((raiz / 'datos/mascaras.json').read_text(encoding='utf-8'))
fotos = {f['archivo']: f for f in datos['fotos']}

def e(s):
    return html.escape(s or '', quote=True)

def picture(f, sizes, lazy=True, clase=''):
    t = f['tamanos']
    slug = f['slug']
    webp = ', '.join(f'img/mascaras/{slug}-{w}.webp {w}w' for w in t)
    jpg = ', '.join(f'img/mascaras/{slug}-{w}.jpg {w}w' for w in t)
    w0 = t[0]
    h0 = round(f['alto'] * w0 / f['ancho'])
    carga = 'loading="lazy" decoding="async"' if lazy else 'fetchpriority="high" decoding="async"'
    reglas = []
    if f.get('ajuste') == 'contain':
        reglas.append('object-fit: contain')
    if f.get('enfoque'):
        reglas.append(f'object-position: {f["enfoque"]}')
    estilo = f' style="{"; ".join(reglas)}"' if reglas else ''
    cl = f' class="{clase}"' if clase else ''
    return (f'<picture><source type="image/webp" srcset="{webp}" sizes="{sizes}">'
            f'<img{cl} src="img/mascaras/{slug}-{w0}.jpg" srcset="{jpg}" sizes="{sizes}" '
            f'width="{w0}" height="{h0}" alt="{e(f["alt"])}" {carga}{estilo}></picture>')

def grande(f):
    return f'img/mascaras/{f["slug"]}-{f["tamanos"][-1]}'

def tarjeta(t, alt, sizes):
    """Foto 3:4 de una pareja de la danza con la máscara completa (la hace tarjetas_danza.py)."""
    webp = ', '.join(f'img/mascaras/{t["slug"]}-{w}.webp {w}w' for w in t['tamanos'])
    jpg = ', '.join(f'img/mascaras/{t["slug"]}-{w}.jpg {w}w' for w in t['tamanos'])
    w0 = t['tamanos'][0]
    return (f'<picture><source type="image/webp" srcset="{webp}" sizes="{sizes}">'
            f'<img src="img/mascaras/{t["slug"]}-{w0}.jpg" srcset="{jpg}" sizes="{sizes}" '
            f'width="{w0}" height="{round(w0 * 4 / 3)}" alt="{e(alt)}" loading="lazy" decoding="async"></picture>')

# Portada
h = fotos[datos['portada']['archivo']]
portada = f'''<section class="portada" id="inicio" aria-labelledby="titulo-portada">
      <div class="contenedor">
        <div>
          <p class="antetitulo">Maestro mascarero · Suchitlán, Colima</p>
          <h1 id="titulo-portada">Gorgonio Candelario <em>Castro</em></h1>
          <p class="lema">Antes de tallar, hay que danzar.</p>
          <p class="entrada">Talla y pinta a mano máscaras de madera para la Danza de los Morenos, las pastorelas y otras danzas de su pueblo. Heredó el oficio de su padre, el mascarero don Herminio Candelario.</p>
          <div class="botones">
            <a class="boton boton-principal" href="#maestro">Conoce su historia</a>
            <a class="boton boton-secundario" href="#mascaras">Ver las máscaras</a>
          </div>
        </div>
        <figure class="portada-imagen">
          <div class="portada-marco">{picture(h, "(max-width: 440px) 88vw, (max-width: 760px) 24rem, (max-width: 1160px) 42vw, 30rem", lazy=False)}</div>
          <figcaption>{e(h["pie"])}</figcaption>
        </figure>
      </div>
    </section>'''

d = fotos[datos['danza']['archivo']]
imagen_danza = f'''<figure class="imagen-danza">
          {picture(d, "(max-width: 820px) 92vw, (max-width: 1230px) 45vw, 34rem")}
          <figcaption>{e(datos['danza'].get('pie') or d["pie"])}</figcaption>
        </figure>'''

# Las nueve parejas de la danza
danza = json.loads((raiz / 'datos/danza.json').read_text(encoding='utf-8'))
tarjetas = []
for i, par in enumerate(danza['parejas'], 1):
    if par.get('archivo'):
        f = fotos[par['archivo']]
        tam = "(max-width: 560px) 46vw, (max-width: 1000px) 31vw, 23rem"
        t = par.get('tarjeta')
        if t and t.get('archivo') != par['archivo']:
            sys.exit(f'La tarjeta de «{par["nombre"]}» es de otra foto: corre primero python3 herramientas/tarjetas_danza.py .')
        foto = tarjeta(t, f['alt'], tam) if t else picture(f, tam)
        imagen = (f'<a class="pareja-imagen" href="{grande(f)}.jpg" data-grande="{grande(f)}.webp" '
                  f'data-titulo="{e(par["nombre"])}" data-descripcion="{e(f["descripcion"])}">{foto}</a>')
        clase = 'pareja'
    else:
        imagen = '<div class="pareja-imagen" aria-hidden="true"></div>'
        clase = 'pareja pareja-sin-foto'
    nota = f'<span class="pareja-nota">{e(par["nota"])}</span>' if par.get('nota') else ''
    tarjetas.append(f'''            <li class="{clase}">
              {imagen}
              <p><span class="pareja-numero">{i}</span><span><strong>{e(par["nombre"])}</strong>{nota}</span></p>
            </li>''')
parejas = f'''<ol class="parejas" data-conjunto>
{chr(10).join(tarjetas)}
          </ol>'''

# Acercamientos de la técnica
detalles = json.loads((raiz / 'datos/detalles.json').read_text(encoding='utf-8'))['detalles']
items_det = []
for d in detalles:
    t = d['tamanos']
    webp = ', '.join(f'img/detalles/{d["id"]}-{w}.webp {w}w' for w in t)
    jpg = ', '.join(f'img/detalles/{d["id"]}-{w}.jpg {w}w' for w in t)
    sz = "(max-width: 600px) 46vw, (max-width: 1000px) 23vw, 16rem"
    items_det.append(f'''            <li><figure>
              <picture><source type="image/webp" srcset="{webp}" sizes="{sz}"><img src="img/detalles/{d["id"]}-{t[0]}.jpg" srcset="{jpg}" sizes="{sz}" width="{t[0]}" height="{t[0]}" alt="{e(d["alt"])}" loading="lazy" decoding="async"></picture>
              <figcaption><strong>{e(d["titulo"])}</strong> {e(d["texto"])}</figcaption>
            </figure></li>''')
acercamientos = f'''<ul class="detalles">
{chr(10).join(items_det)}
          </ul>'''

p = raiz / 'index.html'
s = p.read_text(encoding='utf-8')
def reemplazar(s, marcador, bloque):
    patron = re.compile(r'<!-- ' + marcador + r' -->(.*?<!-- /' + marcador + r' -->)?', re.S)
    assert patron.search(s), marcador
    return patron.sub(lambda m: f'<!-- {marcador} -->\n    {bloque}\n    <!-- /{marcador} -->', s, count=1)
s = reemplazar(s, 'PORTADA', portada)
s = reemplazar(s, 'IMAGEN-DANZA', imagen_danza)
s = reemplazar(s, 'PAREJAS', parejas)
s = reemplazar(s, 'DETALLES', acercamientos)
p.write_text(s, encoding='utf-8')
print('ok', len(fotos), 'fotos,', len(datos['secciones']), 'secciones')
