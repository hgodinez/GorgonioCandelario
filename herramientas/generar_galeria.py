"""Uso: python3 herramientas/generar_galeria.py .

Genera los bloques de HTML (portada, galería, imagen de la danza) a partir de datos/mascaras.json
y los inserta en index.html en lugar de los comentarios marcadores."""
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

# Portada
h = fotos[datos['portada']['archivo']]
portada = f'''<section class="portada" id="inicio" aria-labelledby="titulo-portada">
      <div class="contenedor">
        <div>
          <p class="antetitulo">Maestro mascarero · Suchitlán, Colima</p>
          <h1 id="titulo-portada">Gorgonio Candelario <em>Castro</em></h1>
          <p class="entrada">Talla y pinta a mano máscaras de madera para la Danza de los Morenos, las pastorelas y otras danzas de su pueblo. Heredó el oficio de su padre, el mascarero don Herminio Candelario.</p>
          <div class="botones">
            <a class="boton boton-principal" href="#mascaras">Ver las máscaras</a>
            <a class="boton boton-secundario" href="#taller">Visitar el taller</a>
          </div>
        </div>
        <figure class="portada-imagen">
          <div class="portada-marco">{picture(h, "(max-width: 440px) 88vw, (max-width: 760px) 24rem, (max-width: 1160px) 42vw, 30rem", lazy=False)}</div>
          <figcaption>{e(h["pie"])}</figcaption>
        </figure>
      </div>
    </section>'''

# Galería
sizes = "(max-width: 736px) 46vw, (max-width: 1003px) 30vw, 17rem"
botones = ['<button type="button" data-filtro="todas" aria-pressed="true">Todas</button>']
grupos = []
for i, s in enumerate(datos['secciones']):
    gid = s['id']
    botones.append(f'<button type="button" data-filtro="{gid}" aria-pressed="false">{e(s["titulo"])}</button>')
    items = []
    for a in s['archivos']:
        f = fotos[a]
        items.append(f'''            <li><figure>
              <a href="{grande(f)}.jpg" data-grande="{grande(f)}.webp" data-titulo="{e(f["personaje"])}" data-descripcion="{e(f["descripcion"])}">
                <div class="marco"{f' style="background: {f["fondo"]}"' if f.get("fondo") else ""}>{picture(f, sizes)}</div>
              </a>
              <figcaption>{e(f["pie"])}</figcaption>
            </figure></li>''')
    grupos.append(f'''        <div class="grupo" id="{gid}">
          <div class="grupo-titulo"><h3>{e(s["titulo"])}</h3></div>
          <p>{e(s["descripcion"])}</p>
          <ul class="galeria">
{chr(10).join(items)}
          </ul>
        </div>''')

galeria = f'''<section class="seccion" id="mascaras" aria-labelledby="titulo-mascaras">
      <div class="contenedor">
        <div class="encabezado-seccion">
          <p class="antetitulo">Su obra</p>
          <h2 id="titulo-mascaras">Las máscaras</h2>
          <p class="texto-suave">Una muestra de las máscaras que talla y pinta a mano en su taller. Toca una foto para verla en grande.</p>
        </div>
        <div class="filtros" role="group" aria-label="Filtrar máscaras">
          {chr(10).join("          " + b for b in botones).strip()}
        </div>
{chr(10).join(grupos)}
      </div>
    </section>'''

d = fotos[datos['danza']['archivo']]
imagen_danza = f'''<figure class="imagen-danza">
          {picture(d, "(max-width: 820px) 92vw, (max-width: 1230px) 45vw, 34rem")}
          <figcaption>{e(d["pie"])}</figcaption>
        </figure>'''

p = raiz / 'index.html'
s = p.read_text(encoding='utf-8')
def reemplazar(s, marcador, bloque):
    patron = re.compile(r'<!-- ' + marcador + r' -->(.*?<!-- /' + marcador + r' -->)?', re.S)
    assert patron.search(s), marcador
    return patron.sub(lambda m: f'<!-- {marcador} -->\n    {bloque}\n    <!-- /{marcador} -->', s, count=1)
s = reemplazar(s, 'PORTADA', portada)
s = reemplazar(s, 'MÁSCARAS', galeria)
s = reemplazar(s, 'IMAGEN-DANZA', imagen_danza)
p.write_text(s, encoding='utf-8')
print('ok', len(fotos), 'fotos,', len(datos['secciones']), 'secciones')
