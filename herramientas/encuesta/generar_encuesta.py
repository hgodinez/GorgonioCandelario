"""Arma la encuesta para don Gorgonio (una máscara por pantalla) a partir de datos/galeria.json.
Hay dos salidas:
  * Para el sitio (modo=sitio): preguntas/index.html, una página escondida del sitio (no va en el
    menú y los buscadores no la indexan) que usa las fotos de img/galeria. Si se le dan los datos de
    Supabase, cada respuesta y cada audio se guardan por internet (ver herramientas/encuesta/supabase.sql);
    si no, se guardan en el teléfono y se mandan por WhatsApp.
  * Para claude.ai: la página y una lista de archivos para publicarla como Artifact.
Uso: python3 herramientas/encuesta/generar_encuesta.py . carpeta_salida [modo=sitio] [destino=16466454572]
       [nombre="Nombre"] [firma="..."] [enlace=URL] [supabase_url=https://xxxx.supabase.co] [supabase_key=...]
modo=sitio: escribe preguntas/index.html en el sitio (carpeta_salida se ignora salvo para archivos.json).
supabase_key: la clave pública (anon o publishable) del proyecto; NUNCA la secreta (service_role/sb_secret).
destino: WhatsApp al que llegan las respuestas, con el código de país (1 Estados Unidos, 52 México); nombre: a quién le llegan; firma: quién saluda al inicio;
enlace: dirección de la encuesta publicada, para el documento de preguntas.
Salida: carpeta_salida/encuesta.html, carpeta_salida/archivos.json ({ruta publicada: ruta en el repo})
y datos/preguntas-para-don-gorgonio.md (el mismo cuestionario como documento, con los mismos números)."""
import json, re, sys, pathlib

raiz, salida = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
opciones = dict(a.split('=', 1) for a in sys.argv[3:])
salida.mkdir(parents=True, exist_ok=True)
g = json.loads((raiz / 'datos/galeria.json').read_text(encoding='utf-8'))
tam = json.loads((raiz / 'datos/album-tamanos.json').read_text(encoding='utf-8'))
catalogo = json.loads((raiz / 'datos/album-catalogo.json').read_text(encoding='utf-8'))

# Piezas que se apartaron de la galería hasta saber si son de don Gorgonio (la cuarta solo
# existe en un collage diminuto, así que se pregunta en «Sobre usted»)
APARTADAS = ['felino-multicolor-pastel', 'toro-pastel-cuernos-rosas', 'toro-pastel-cuernos-azules']
VISTAS_MAX = 3   # foto principal y hasta dos vistas más
ANCHO_MAX = 800  # pixeles de la foto en la encuesta

archivos = {}
SITIO = opciones.get('modo') == 'sitio'

# En pantalla se evitan palabras técnicas; el nombre original va en el texto de WhatsApp y en línea
PALABRAS = [('Cánido', 'Perro o coyote'), ('naturalista', 'pintado al natural')]
DUDAS_FIJAS = {'equino-rayado': ('Animal rayado', ['caballo', 'burro', 'cebra'])}


def para_ver(slug, nombre):
    """(nombre para mostrar, opciones de la duda): «Cánido negro (¿coyote o perro?)» da
    («Perro o coyote negro», ['coyote', 'perro']). «(¿de la danza?)» no es duda del nombre."""
    if slug in DUDAS_FIJAS:
        return DUDAS_FIJAS[slug]
    duda = []
    d = re.search(r'\s*\(¿(.+?)\?\)\s*$', nombre)
    if d and 'danza' not in d.group(1):
        duda = re.split(r'\s+o\s+', d.group(1))
        nombre = nombre[:d.start()]
    elif d:
        nombre = nombre[:d.start()]
    if nombre.startswith('Cánido'):  # en pantalla dice «Perro o coyote»: que la respuesta diga cuál es
        duda = ['coyote', 'perro'] + [x for x in duda if x not in ('coyote', 'perro')]
    for a, b in PALABRAS:
        nombre = nombre.replace(a, b)
    return nombre, duda


def foto(fid):
    w = max([x for x in tam[fid]['tamanos'] if x <= ANCHO_MAX] or tam[fid]['tamanos'][:1])
    if SITIO:  # la página vive en preguntas/ y usa las fotos que ya tiene el sitio
        return f'../img/galeria/{fid}-{w}.webp'
    ruta = f'img/{fid}.webp'
    archivos[ruta] = f'img/galeria/{fid}-{w}.webp'
    return ruta


mascaras = []
for sala in g['salas']:
    for sub in sala.get('subsalas') or [{'titulo': '', 'piezas': sala['piezas']}]:
        for slug in sub['piezas']:
            p = g['piezas'][slug]
            fotos = [p['principal']] + [f for f in p['fotos'] if f != p['principal']]
            ver, duda = para_ver(slug, p['nombre'])
            mascaras.append({
                'id': slug, 'nombre': p['nombre'], 'ver': ver, 'duda': duda, 'sala': sala['titulo'], 'grupo': sub['titulo'],
                'fotos': [foto(f) for f in fotos[:VISTAS_MAX]],
                'confirmada': p.get('certeza') == 'confirmada-familia', 'apartada': False,
            })

agrupadas = {x['pieza']: x for grupo in catalogo['agrupados'] for x in grupo['piezas']}
for slug in APARTADAS:
    p = agrupadas[slug]
    fotos = [p['principal']] + [f for f in p['fotos'] if f != p['principal']]
    ver, duda = para_ver(slug, p['nombre'])
    mascaras.append({'id': slug, 'nombre': p['nombre'], 'ver': ver, 'duda': duda, 'sala': 'Otras máscaras', 'grupo': '',
                     'fotos': [foto(f) for f in fotos[:VISTAS_MAX]], 'confirmada': False, 'apartada': True})

for n, m in enumerate(mascaras, 1):
    m['n'] = n

# Preguntas sobre él y el taller: id estable, texto y, si aplica, opciones para tocar, una foto,
# enlaces o un campo corto
GENERALES = [
    {'id': 'nacimiento', 'texto': '¿En qué año nació?', 'corto': True},
    {'id': 'empezo', 'texto': '¿A qué edad empezó a tallar máscaras? ¿Quién le enseñó?'},
    {'id': 'generacion', 'texto': '¿Hasta quién de su familia se acuerda que hacía máscaras?',
     'opciones': ['Mi papá', 'Mi abuelo', 'Mi bisabuelo', 'Más atrás', 'No sé']},
    {'id': 'guelo-baci', 'texto': '¿Qué quiere decir el nombre de su taller, «Mi Güelo Baci»?'},
    {'id': 'premios', 'texto': '¿Qué premios ha recibido y en qué año? ¿En qué año lo nombraron Gran Maestro del Arte Popular?'},
    {'id': 'perros', 'texto': 'Según lo que encontré, en la Danza de los Morenos salen nueve parejas: coyotes, chivos, borregos cimarrones, tecolotes, lince y ocelote, burros, guacamayas, gallos y perros. ¿Está bien?',
     'opciones': ['Sí, está bien', 'No, falta o sobra alguna', 'No sé']},
    {'id': 'simbolos', 'texto': 'Me contaron que en la danza el coyote es la inteligencia, el chivo la unión y la fuerza, el borrego la fuerza y la testarudez, el tecolote la sabiduría y los felinos la agilidad. ¿Qué representan el burro, la guacamaya, el gallo y el perro?'},
    {'id': 'tecnica', 'texto': '¿Qué pintura usa? ¿Con qué hace el pelo y las barbas de las máscaras?'},
    {'id': 'taller', 'texto': '¿Qué días y a qué hora se le puede visitar en el taller? ¿Da clases? ¿Manda máscaras a otras ciudades?'},
    {'id': 'videos', 'texto': '¿Me da permiso de poner en su página estos dos videos donde sale usted?',
     'enlaces': [['Ver el video «Hacedor de máscaras»', 'https://www.youtube.com/watch?v=IcQFjwiqZJI'],
                 ['Ver el video del taller', 'https://www.youtube.com/watch?v=u3Pr0mBtlms']],
     'opciones': ['Sí', 'No', 'No los he visto']},
    {'id': 'fotos', 'texto': '¿Quién tomó las fotos de las máscaras y las fotos de usted? ¿Cómo pongo el nombre de esa persona en la página?'},
    {'id': 'ave-azul', 'texto': 'En esta foto, ¿la máscara de en medio, el ave azul de pico largo y amarillo, es suya?',
     'foto': foto('a065'), 'alt': 'Tres máscaras juntas: un tecolote rojo, un ave azul de pico largo y amarillo, y un coyote blanco',
     'opciones': ['Sí', 'No', 'No sé']},
    {'id': 'mas', 'texto': '¿Hay algo más que quiera contar en su página? Una historia, un recuerdo o una frase suya.'},
]

datos = {'mascaras': mascaras, 'generales': GENERALES,
         'destino': re.sub(r'\D', '', opciones.get('destino', '')), 'destino_nombre': opciones.get('nombre', ''),
         'firma': opciones.get('firma', ''),
         'supabase': {'url': opciones.get('supabase_url', ''), 'key': opciones.get('supabase_key', '')}}
assert not datos['supabase']['key'].startswith(('sb_secret', 'service')), 'esa es la clave secreta: use la pública (anon o publishable)'
plantilla = (pathlib.Path(__file__).parent / 'plantilla.html').read_text(encoding='utf-8')
assert '/*DATOS*/null' in plantilla
html = plantilla.replace('/*DATOS*/null', json.dumps(datos, ensure_ascii=False).replace('</', '<\\/'))
if SITIO:
    # Página completa para el sitio: fuentes del propio sitio y fuera de los buscadores
    fuentes = re.compile(r'<link rel="preconnect"[^>]*>\n<link rel="preconnect"[^>]*>\n<link rel="stylesheet" href="https://fonts.googleapis.com[^>]*>\n')
    assert fuentes.search(html)
    html = fuentes.sub('', html).replace('<meta name="claude:viewport-fit-sides" content="cover">\n', '')
    caras = """@font-face { font-family: "Fraunces"; font-style: normal; font-weight: 100 900; font-display: swap; src: url("../fuentes/fraunces-latin-opsz-normal.woff2") format("woff2"); }
@font-face { font-family: "Source Sans 3"; font-style: normal; font-weight: 400; font-display: swap; src: url("../fuentes/source-sans-3-latin-400-normal.woff2") format("woff2"); }
@font-face { font-family: "Source Sans 3"; font-style: normal; font-weight: 600; font-display: swap; src: url("../fuentes/source-sans-3-latin-600-normal.woff2") format("woff2"); }
@font-face { font-family: "Source Sans 3"; font-style: normal; font-weight: 700; font-display: swap; src: url("../fuentes/source-sans-3-latin-700-normal.woff2") format("woff2"); }
:root { padding-top: env(safe-area-inset-top); padding-bottom: env(safe-area-inset-bottom); }
body { margin: 0; }
img { max-width: 100%; }
[hidden] { display: none !important; }
"""
    html = html.replace('<style>\n', '<style>\n' + caras, 1)
    html = ('<!doctype html>\n<html lang="es">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            '<meta name="robots" content="noindex, nofollow">\n<link rel="icon" href="../img/icono.svg" type="image/svg+xml">\n'
            + html.replace('<style>', '<style>', 1).replace('</style>\n', '</style>\n</head>\n<body>\n', 1) + '</body>\n</html>\n')
    (raiz / 'preguntas').mkdir(exist_ok=True)
    (raiz / 'preguntas/index.html').write_text(html, encoding='utf-8')
else:
    (salida / 'encuesta.html').write_text(html, encoding='utf-8')
(salida / 'archivos.json').write_text(json.dumps(archivos, indent=1), encoding='utf-8')
# El mismo cuestionario como documento sencillo, con la misma numeración que la encuesta
lineas = [
    '# Preguntas para don Gorgonio', '',
    'Todo lo que falta preguntarle, en un solo lugar. La forma más fácil de contestar es la encuesta en línea:',
    'enseña cada máscara con su foto y guarda las respuestas. Este documento tiene las mismas preguntas y los',
    'mismos números, por si prefiere contestar por WhatsApp, por teléfono o en papel («la 12 es un perro»).',
] + ([f"Encuesta: {opciones['enlace']}"] if opciones.get('enlace') else []) + [
    '', '## De cada máscara', '',
    '1. ¿Qué es? (¿está bien el nombre que le puse?)',
    '2. ¿En qué danza o fiesta se usa? (Danza de los Morenos, Pastorela, otra, o no se baila)',
    '3. ¿Qué significa?', '',
    'En las tres últimas (123 a 125) se pregunta además si las hizo él.', '',
    '## Las máscaras', '',
]
sala = None
for m in mascaras:
    if m['sala'] != sala:
        sala = m['sala']
        lineas += ['', f'### {sala}', '']
    nota = ' (ya confirmada por la familia)' if m['confirmada'] else ''
    grupo = f"{m['grupo']}: " if m['grupo'] else ''
    lineas.append(f"{m['n']}. {grupo}{m['nombre']}{nota}")
lineas += ['', '## Sobre él y el taller', '']
lineas += [f"{k}. {q['texto']}" for k, q in enumerate(GENERALES, 1)]
lineas += ['', '## Fotos que me faltan', '',
           '- Un retrato de don Gorgonio, su taller y él trabajando.',
           '- Los perros y el ocelote de la Danza de los Morenos.',
           '- Las fotos originales del teléfono (las que llegaron por WhatsApp están comprimidas).', '']
(raiz / 'datos/preguntas-para-don-gorgonio.md').write_text('\n'.join(lineas), encoding='utf-8')
print(len(mascaras), 'máscaras,', len(archivos), 'fotos,', len(GENERALES), 'preguntas generales')
