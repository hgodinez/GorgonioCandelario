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
    sub = f'<span>{e(p["pie"])}</span>' if p.get('pie') else ''
    return (f'          <li class="{clase}"><figure>'
            f'{enlace(slug, fid, img(fid, "(max-width: 560px) 46vw, 15rem") + vistas)}'
            f'<figcaption><strong>{e(p["nombre"])}</strong>{sub}</figcaption></figure></li>')


# Salas
nav, bloques = [], []
total_piezas = 0
for n, sala in enumerate(g['salas'], 1):
    nav.append(f'<li><a href="#sala-{sala["id"]}">{e(sala["titulo"])}</a></li>')
    partes = []
    for sub in sala.get('subsalas') or [{'titulo': '', 'piezas': sala['piezas']}]:
        if not sub['piezas']:
            continue
        total_piezas += len(sub['piezas'])
        tarjetas = '\n'.join(tarjeta(s) for s in sub['piezas'])
        titulo = ''
        if sub['titulo']:
            nota = f'<span>{e(sub["nota"])}</span>' if sub.get('nota') else ''
            titulo = f'<div class="subsala-titulo"><h3>{e(sub["titulo"])}</h3>{nota}</div>\n'
        partes.append(f'''        <div class="subsala">
          {titulo}<ul class="muro" data-conjunto>
{tarjetas}
          </ul>
        </div>''')
    bloques.append(f'''    <section class="sala" id="sala-{sala["id"]}" aria-labelledby="titulo-sala-{sala["id"]}">
      <div class="contenedor">
        <div class="sala-encabezado">
          <div>
            <span class="sala-numero">Sala {n}</span>
            <h2 id="titulo-sala-{sala["id"]}">{e(sala["titulo"])}</h2>
            <p class="sala-sub">{e(sala["subtitulo"])}</p>
          </div>
          <p class="sala-texto">{e(sala["texto"])}</p>
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
    for fid in ids:
        t = tam[fid]
        anch = t['recorte_tamanos']
        src = ', '.join(f'img/galeria/recortes/{fid}-{w}.webp {w}w' for w in anch)
        h0 = round(t['recorte_h'] * anch[0] / t['recorte_w'])
        imagen = (f'<img src="img/galeria/recortes/{fid}-{anch[0]}.webp" srcset="{src}" sizes="16rem" '
                  f'width="{anch[0]}" height="{h0}" alt="{e(fotos[fid]["alt"])}" decoding="async">')
        items.append(f'            <li>{enlace(g["pieza_de"][fid], fid, imagen)}</li>')
        copia.append(f'            <li>{imagen.replace(" alt=" + chr(34) + e(fotos[fid]["alt"]) + chr(34), " alt=" + chr(34) + chr(34))}</li>')
    return ('<section class="desfile" aria-label="Desfile de máscaras">\n        <div class="desfile-pistas">\n'
            '          <ul class="desfile-pista" data-conjunto>\n' + '\n'.join(items) + '\n          </ul>\n'
            '          <ul class="desfile-pista" aria-hidden="true" inert>\n' + '\n'.join(copia) + '\n          </ul>\n'
            '        </div>\n      </section>')


total_fotos = sum(len(piezas[s]['fotos']) for sala in g['salas'] for sub in (sala.get('subsalas') or [{'piezas': sala['piezas']}]) for s in sub['piezas'])
cuerpo = f'''<section class="galeria-entrada" aria-labelledby="titulo-galeria">
      <div class="contenedor">
        <p class="antetitulo">La galería</p>
        <h1 id="titulo-galeria">Las máscaras de don Gorgonio</h1>
        <p>{e(g["entrada"])}</p>
        <ul class="galeria-cifras">
          <li><strong>{total_piezas}</strong>máscaras</li>
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
          <a class="boton boton-principal" href="galeria.html">Ver las {total_piezas} máscaras</a>
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
