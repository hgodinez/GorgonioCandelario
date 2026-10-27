"""Genera la galería completa (galeria.html) y la muestra de la galería en index.html
a partir de datos/galeria.json, datos/album-tamanos.json y las imágenes de img/galeria.
Uso: python3 herramientas/generar_galeria_completa.py ."""
import json, sys, html, re, pathlib

raiz = pathlib.Path(sys.argv[1])
g = json.loads((raiz / 'datos/galeria.json').read_text(encoding='utf-8'))
tam = json.loads((raiz / 'datos/album-tamanos.json').read_text(encoding='utf-8'))
fotos, piezas = g['fotos'], g['piezas']


def e(s):
    return html.escape(s or '', quote=True)


def carpeta(fid):
    return 'img/galeria/recortes' if fotos[fid].get('recorte') else 'img/galeria'


def anchos(fid):
    return tam[fid]['recorte_tamanos'] if fotos[fid].get('recorte') else tam[fid]['tamanos']


def medidas(fid):
    t = tam[fid]
    return (t['recorte_w'], t['recorte_h']) if fotos[fid].get('recorte') else (t['w'], t['h'])


def srcset(fid):
    return ', '.join(f'{carpeta(fid)}/{fid}-{w}.webp {w}w' for w in anchos(fid))


def grande(fid):
    return f'{carpeta(fid)}/{fid}-{anchos(fid)[-1]}.webp'


def mini(fid):
    return f'{carpeta(fid)}/{fid}-{anchos(fid)[0]}.webp'


def img(fid, sizes, lazy=True):
    w, h = medidas(fid)
    w0 = anchos(fid)[0]
    h0 = round(h * w0 / w)
    carga = 'loading="lazy" decoding="async"' if lazy else 'decoding="async"'
    return (f'<img src="{mini(fid)}" srcset="{srcset(fid)}" sizes="{sizes}" width="{w0}" height="{h0}" '
            f'alt="{e(fotos[fid]["alt"])}" {carga}>')


def enlace(slug, fid, contenido, clase=''):
    p = piezas[slug]
    vistas = [{'src': grande(v), 'alt': fotos[v]['alt'], 'mini': mini(v)} for v in p['fotos']]
    datos_vistas = f' data-vistas="{e(json.dumps(vistas, ensure_ascii=False))}"' if len(vistas) > 1 else ''
    cl = f' class="{clase}"' if clase else ''
    return (f'<a{cl} href="{grande(fid)}" data-grande="{grande(fid)}" data-titulo="{e(p["nombre"])}" '
            f'data-descripcion="{e(p["descripcion"])}"{datos_vistas}>{contenido}</a>')


def tarjeta(slug):
    p = piezas[slug]
    fid = p['principal']
    n = len(p['fotos'])
    vistas = f'<span class="pieza-vistas">{n} vistas</span>' if n > 1 else ''
    clase = 'pieza pieza-recorte' if fotos[fid].get('recorte') else 'pieza'
    if p.get('pie'):
        sub = f'<span>{e(p["pie"])}</span>'
    elif p.get('certeza') == 'confirmada-maestro':
        sub = '<span>Pieza confirmada por Don Gorgonio</span>'
    elif p.get('certeza') == 'confirmada-familia':
        sub = '<span>Pieza confirmada por la familia</span>'
    else:
        sub = ''
    return (f'          <li class="{clase}"><figure>'
            f'{enlace(slug, fid, img(fid, "(max-width: 560px) 46vw, 15rem") + vistas)}'
            f'<figcaption><strong>{e(p["nombre"])}</strong>{sub}</figcaption></figure></li>')


def subsala(sub, n=None):
    tarjetas = '\n'.join(tarjeta(s) for s in sub['piezas'])
    titulo = ''
    if sub['titulo']:
        nota = f'<span>{e(sub["nota"])}</span>' if sub.get('nota') else ''
        titulo = f'<div class="subsala-titulo"><h3>{e(sub["titulo"])}</h3>{nota}</div>\n'
    estilo = f' style="--n:{n}"' if n else ''
    return f'''        <div class="subsala"{estilo}>
          {titulo}<ul class="muro" data-conjunto>
{tarjetas}
          </ul>
        </div>'''


# Las subsalas de pocas piezas se acomodan lado a lado (hasta 4 piezas por fila)
CHICA, POR_FILA = 3, 4


def filas(subs):
    grupo = []
    for sub in subs + [None]:
        chica = sub is not None and len(sub['piezas']) <= CHICA
        if grupo and (not chica or sum(len(x['piezas']) for x in grupo) + len(sub['piezas']) > POR_FILA):
            if len(grupo) == 1:
                yield subsala(grupo[0])
            else:
                dentro = '\n'.join(subsala(x, len(x['piezas'])) for x in grupo)
                yield f'        <div class="subsalas-fila">\n{dentro}\n        </div>'
            grupo = []
        if sub is None:
            break
        if chica:
            grupo.append(sub)
        else:
            yield subsala(sub)


def portada(n, sala):
    """La portada de la sala: la foto de una máscara que se acerca al hacer scroll (js/portadas.js) y el número, el nombre
    y el subtítulo de la sala. Es solo visual: repite el título de la sala, que los lectores de pantalla encuentran en ella."""
    fid, foco = sala['portada']['foto'], sala['portada']['foco']
    t = tam[fid]
    return f'''    <section class="zoom" id="zoom-{sala["id"]}" aria-hidden="true">
      <div class="zoom-escena">
        <div class="zoom-caja">
          <figure class="zoom-foto">
            <picture>
              <source type="image/webp" srcset="{', '.join(f'img/galeria/{fid}-{w}.webp {w}w' for w in t['tamanos'])}" sizes="(min-aspect-ratio: 1/1) 45vw, 100vw">
              <img src="img/galeria/{fid}.jpg" width="{t['w']}" height="{t['h']}" loading="lazy" decoding="async" style="--foco: {foco}%" alt="">
            </picture>
          </figure>
        </div>
        <div class="zoom-texto">
          <span class="sala-numero">Sala {n}</span>
          <p class="zoom-nombre">{e(sala["titulo"])}</p>
          <p class="sala-sub">{e(sala["subtitulo"])}</p>
        </div>
        <p class="zoom-pista">Desliza</p>
      </div>
    </section>
'''


# Salas
nav, bloques = [], []
total_piezas = 0
for n, sala in enumerate(g['salas'], 1):
    nav.append(f'<li><a href="#sala-{sala["id"]}">{e(sala["titulo"])}</a></li>')
    subs = [x for x in (sala.get('subsalas') or [{'titulo': '', 'piezas': sala['piezas']}]) if x['piezas']]
    total_piezas += sum(len(x['piezas']) for x in subs)
    partes = list(filas(subs))
    oculto = ' class="visualmente-oculto"' if sala.get('portada') else ''  # con portada, el número y el título ya están en ella
    bloques.append((portada(n, sala) if sala.get('portada') else '') + f'''    <section class="sala" id="sala-{sala["id"]}" aria-labelledby="titulo-sala-{sala["id"]}">
      <div class="contenedor">
        <div class="sala-encabezado">
          <div{oculto}>
            <span class="sala-numero">Sala {n}</span>
            <h2 id="titulo-sala-{sala["id"]}">{e(sala["titulo"])}</h2>
            <p class="sala-sub">{e(sala["subtitulo"])}</p>
          </div>
          <div class="sala-texto">{"".join(f"<p>{e(x)}</p>" for x in sala["texto"].split(chr(10) * 2))}</div>
        </div>
{chr(10).join(partes)}
      </div>
    </section>''')


def mosaico(ids, conjunto=True):
    items = []
    for fid in ids:
        slug = g['pieza_de'][fid]
        items.append(f'          <li>{enlace(slug, fid, img(fid, "(max-width: 760px) 50vw, 25vw"))}</li>')
    return f'<ul class="mosaico"{" data-conjunto" if conjunto else ""}>\n' + '\n'.join(items) + '\n        </ul>'


def desfile(ids):
    """Máscaras recortadas que avanzan como la cuadrilla de la danza; la segunda pista es copia decorativa."""
    items, copia = [], []
    for i, fid in enumerate(ids):
        t = tam[fid]
        anch = t['recorte_tamanos']
        src = ', '.join(f'img/galeria/recortes/{fid}-{w}.webp {w}w' for w in anch)
        h0 = round(t['recorte_h'] * anch[0] / t['recorte_w'])
        # La altura es clamp(9rem, 22vw, 17rem): el ancho mostrado depende de la proporción de cada máscara
        r = t['recorte_w'] / t['recorte_h']
        sizes = f'(max-width: 654px) {round(144 * r)}px, (max-width: 1236px) {22 * r:.1f}vw, {round(272 * r)}px'
        carga = ' loading="lazy"' if i >= 4 else ''
        imagen = (f'<img src="img/galeria/recortes/{fid}-{anch[0]}.webp" srcset="{src}" sizes="{sizes}" '
                  f'width="{anch[0]}" height="{h0}" alt="{e(fotos[fid]["alt"])}"{carga} decoding="async">')
        items.append(f'            <li>{enlace(g["pieza_de"][fid], fid, imagen)}</li>')
        decorativa = imagen.replace(f' alt="{e(fotos[fid]["alt"])}"', ' alt=""')
        if 'loading=' not in decorativa:
            decorativa = decorativa.replace(' decoding=', ' loading="lazy" decoding=')
        copia.append(f'            <li>{decorativa}</li>')
    return ('<div class="contenedor desfile-control"><button class="desfile-pausa" type="button" aria-controls="desfile">'
            'Pausar el desfile</button></div>\n    '
            '<section class="desfile" id="desfile" aria-label="Desfile de máscaras">\n        <div class="desfile-pistas">\n'
            '          <ul class="desfile-pista" data-conjunto>\n' + '\n'.join(items) + '\n          </ul>\n'
            '          <ul class="desfile-pista" aria-hidden="true">\n' + '\n'.join(copia) + '\n          </ul>\n'
            '        </div>\n      </section>')


total_fotos = sum(len(piezas[s]['fotos']) for sala in g['salas'] for sub in (sala.get('subsalas') or [{'piezas': sala['piezas']}]) for s in sub['piezas'])
cuerpo = f'''<section class="galeria-entrada" aria-labelledby="titulo-galeria">
      <div class="contenedor">
        <p class="antetitulo">La galería</p>
        <h1 id="titulo-galeria">Las máscaras de Don Gorgonio</h1>
        <p>{e(g["entrada"])}</p>
        <ul class="galeria-cifras">
          <li><strong>{total_piezas}</strong>piezas</li>
          <li><strong>{total_fotos}</strong>fotografías</li>
          <li><strong>{len(g["salas"])}</strong>salas</li>
        </ul>
      </div>
    </section>
    {desfile(g["desfile"])}
    <nav class="salas-nav" aria-label="Salas de la galería">
      <div class="contenedor"><ul>{"".join(nav)}</ul></div>
    </nav>
{chr(10).join(bloques)}'''

p = raiz / 'galeria.html'
s = p.read_text(encoding='utf-8')
patron = re.compile(r'<!-- GALERIA -->.*?<!-- /GALERIA -->', re.S)
assert patron.search(s), 'falta el marcador GALERIA'
s = patron.sub(lambda m: f'<!-- GALERIA -->\n    {cuerpo}\n    <!-- /GALERIA -->', s, count=1)
p.write_text(s, encoding='utf-8')

# Muestra en la página principal
muestra = f'''<section class="seccion seccion-oscura muestra-galeria" id="mascaras" aria-labelledby="titulo-mascaras">
      <div class="contenedor">
        <div class="encabezado-seccion">
          <p class="antetitulo">Su obra</p>
          <h2 id="titulo-mascaras">La galería</h2>
          <p class="texto-suave">{e(g["entrada_corta"])}</p>
        </div>
        {mosaico(g["muestra"])}
        <div class="botones">
          <a class="boton boton-principal" href="galeria.html">Ver las {total_piezas} piezas</a>
        </div>
      </div>
    </section>'''
p = raiz / 'index.html'
s = p.read_text(encoding='utf-8')
patron = re.compile(r'<!-- MÁSCARAS -->.*?<!-- /MÁSCARAS -->', re.S)
assert patron.search(s), 'falta el marcador MÁSCARAS'
s = patron.sub(lambda m: f'<!-- MÁSCARAS -->\n    {muestra}\n    <!-- /MÁSCARAS -->', s, count=1)
p.write_text(s, encoding='utf-8')
print('ok', total_piezas, 'piezas,', total_fotos, 'fotos,', len(g['salas']), 'salas')
