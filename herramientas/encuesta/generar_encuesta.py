"""Arma la encuesta para don Gorgonio (una máscara por pantalla) a partir de datos/galeria.json.
Escribe la página y una lista de archivos para publicarla como Artifact de claude.ai.
Uso: python3 herramientas/encuesta/generar_encuesta.py . carpeta_salida
Salida: carpeta_salida/encuesta.html, carpeta_salida/archivos.json ({ruta publicada: ruta en el repo})
y datos/preguntas-para-don-gorgonio.md (el mismo cuestionario como documento, con los mismos números)."""
import json, sys, pathlib

raiz, salida = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
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


def foto(fid):
    w = max([x for x in tam[fid]['tamanos'] if x <= ANCHO_MAX] or tam[fid]['tamanos'][:1])
    ruta = f'img/{fid}.webp'
    archivos[ruta] = f'img/galeria/{fid}-{w}.webp'
    return ruta


mascaras = []
for sala in g['salas']:
    for sub in sala.get('subsalas') or [{'titulo': '', 'piezas': sala['piezas']}]:
        for slug in sub['piezas']:
            p = g['piezas'][slug]
            fotos = [p['principal']] + [f for f in p['fotos'] if f != p['principal']]
            mascaras.append({
                'id': slug, 'nombre': p['nombre'], 'sala': sala['titulo'], 'grupo': sub['titulo'],
                'fotos': [foto(f) for f in fotos[:VISTAS_MAX]],
                'confirmada': p.get('certeza') == 'confirmada-familia', 'apartada': False,
            })

agrupadas = {x['pieza']: x for grupo in catalogo['agrupados'] for x in grupo['piezas']}
for slug in APARTADAS:
    p = agrupadas[slug]
    fotos = [p['principal']] + [f for f in p['fotos'] if f != p['principal']]
    mascaras.append({'id': slug, 'nombre': p['nombre'], 'sala': 'Otras máscaras', 'grupo': '',
                     'fotos': [foto(f) for f in fotos[:VISTAS_MAX]], 'confirmada': False, 'apartada': True})

for n, m in enumerate(mascaras, 1):
    m['n'] = n

# Preguntas sobre él y el taller: id estable, texto y, si aplica, opciones para tocar
GENERALES = [
    {'id': 'nacimiento', 'texto': '¿En qué año nació?'},
    {'id': 'empezo', 'texto': '¿A qué edad empezó a tallar máscaras? ¿Quién le enseñó?'},
    {'id': 'generacion', 'texto': '¿Usted es la tercera o la cuarta generación de mascareros de su familia?',
     'opciones': ['Tercera', 'Cuarta', 'Otra']},
    {'id': 'guelo-baci', 'texto': '¿Qué quiere decir el nombre de su taller, «Mi Güelo Baci»?'},
    {'id': 'premios', 'texto': '¿Qué premios ha recibido y en qué año? ¿En qué año lo nombraron Gran Maestro del Arte Popular?'},
    {'id': 'perros', 'texto': 'En la Danza de los Morenos, ¿la novena pareja son los perros?',
     'opciones': ['Sí, son los perros', 'No, es otro animal']},
    {'id': 'simbolos', 'texto': 'En la danza, ¿qué representan el burro, la guacamaya, el gallo y el perro?'},
    {'id': 'tecnica', 'texto': '¿Qué madera usa? ¿Qué pintura? ¿Con qué hace el pelo y las barbas?'},
    {'id': 'taller', 'texto': '¿Qué días y a qué hora se le puede visitar en el taller? ¿Da clases? ¿Manda máscaras a otras ciudades?'},
    {'id': 'videos', 'texto': '¿Nos da permiso de poner en su página los dos videos de YouTube donde sale usted?',
     'opciones': ['Sí', 'No']},
    {'id': 'fotos', 'texto': '¿Quién tomó las fotos de las máscaras y cómo quiere que aparezca su nombre?'},
    {'id': 'ave-azul', 'texto': 'Hay una foto chiquita, en un collage, de un ave azul de pico amarillo. ¿Es suya?',
     'opciones': ['Sí', 'No', 'No sé']},
    {'id': 'mas', 'texto': '¿Hay algo más que quiera contar en su página? Una historia, un recuerdo o una frase suya.'},
]

datos = {'mascaras': mascaras, 'generales': GENERALES, 'destino': ''}
plantilla = (pathlib.Path(__file__).parent / 'plantilla.html').read_text(encoding='utf-8')
assert '/*DATOS*/null' in plantilla
html = plantilla.replace('/*DATOS*/null', json.dumps(datos, ensure_ascii=False).replace('</', '<\\/'))
(salida / 'encuesta.html').write_text(html, encoding='utf-8')
(salida / 'archivos.json').write_text(json.dumps(archivos, indent=1), encoding='utf-8')
# El mismo cuestionario como documento sencillo, con la misma numeración que la encuesta
lineas = [
    '# Preguntas para don Gorgonio', '',
    'Todo lo que falta preguntarle, en un solo lugar. La forma más fácil de contestar es la encuesta en línea:',
    'enseña cada máscara con su foto y guarda las respuestas. Este documento tiene las mismas preguntas y los',
    'mismos números, por si prefiere contestar por WhatsApp, por teléfono o en papel («la 12 es un perro»).',
    '', '## De cada máscara', '',
    '1. ¿Qué es? (¿está bien el nombre que le pusimos?)',
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
lineas += ['', '## Fotos que nos faltan', '',
           '- Un retrato de don Gorgonio, su taller y él trabajando.',
           '- Los perros y el ocelote de la Danza de los Morenos.',
           '- Las fotos originales del teléfono (las que llegaron por WhatsApp están comprimidas).', '']
(raiz / 'datos/preguntas-para-don-gorgonio.md').write_text('\n'.join(lineas), encoding='utf-8')
print(len(mascaras), 'máscaras,', len(archivos), 'fotos,', len(GENERALES), 'preguntas generales')
