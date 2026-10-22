"""Arma datos/galeria.json a partir de la clasificación del álbum (datos/album-catalogo.json)
y la revisión de recortes (datos/recortes-revision.json). Uso: python3 herramientas/armar_galeria.py
Después: python3 herramientas/recortes_web.py . <carpeta_recortes> <ids del desfile> (si cambió el desfile)
y python3 herramientas/generar_galeria_completa.py ."""
import json, sys, pathlib
S = pathlib.Path(__file__).resolve().parent.parent / 'datos'
R = pathlib.Path(__file__).resolve().parent.parent
d = json.loads((S / 'album-catalogo.json').read_text())
qa = {v['id']: v for v in json.loads((S / 'recortes-revision.json').read_text())}
cat = {c['id']: c for c in d['catalogo']}
cur = d['curaduria']

piezas = {}
for g in d['agrupados']:
    for p in g['piezas']:
        if p['pieza'] in piezas:  # mismo slug en dos familias: unir fotos
            piezas[p['pieza']]['fotos'] += [f for f in p['fotos'] if f not in piezas[p['pieza']]['fotos']]
        else:
            piezas[p['pieza']] = dict(p)
# fusiones señaladas por la curaduría
if 'rostro-negro-ave' in piezas:
    piezas['rostro-negro-ave-alada']['fotos'] = ['a114', 'a032']
    del piezas['rostro-negro-ave']
piezas['rostro-negro-lengua']['fotos'] = ['a105', 'a135']; piezas['rostro-negro-lengua']['principal'] = 'a105'

descartar = set(sum((g['duplicados_descartar'] for g in d['agrupados']), [])) | {'a132', 'a145'}
debiles = set(cur['fotos_debiles'])
# piezas que no van en la galería. Ya ninguna: el felino y los toros en tonos pastel y el ave azul se habían
# apartado mientras no se sabía si eran de don Gorgonio, y Humberto confirmó que todas las de las fotos son suyas
APARTADAS = set()
# nombres más neutrales donde la identificación no está confirmada
NOMBRES = {
    'pantera-negra-ojos-amarillos': 'Felino negro de ojos amarillos',
    'pantera-negra-ojos-verdes': 'Felino negro de ojos verdes',
    'jaguar-rosetas': 'Felino de rosetas',
    'jaguar-orejas-rojas': 'Felino de orejas rojas',
    'canido-negro-ojos-cafes': 'Cánido negro de ojos cafés (¿coyote o perro?)',
    'canido-negro-ojos-rojos': 'Cánido negro de ojos rojos (¿coyote o perro?)',
    'canido-negro-nariz-gris': 'Cánido negro de nariz gris (¿coyote o perro?)',
    'canido-negro-boca-abierta': 'Cánido negro de boca abierta (¿coyote o perro?)',
    'coyote-negro-lineas-blancas': 'Cánido negro de líneas blancas (¿coyote o perro?)',
    'felino-rosetas': 'Felino anaranjado de rosetas (¿ocelote?)',
    'felino-lunares': 'Felino amarillo de lunares (¿ocelote?)',
    'felino-moteado': 'Felino anaranjado moteado (¿ocelote?)',
    'perro-blanco-mancha': 'Perro blanco de mancha café',
    'rostro-negro-tecolote': 'Rostro negro con búho',
    'lince-buho-jaguar': 'Lince, búho y felino de rosetas',
    'jaguar-amarillo-con-buho': 'Búho sobre felino amarillo',
    'jaguar-anaranjado-con-buho': 'Búho sobre felino anaranjado',
    'tigre-blanco-con-buho': 'Búho sobre felino blanco de rayas',
    'coyote-naturalista-ocre': 'Cánido ocre naturalista (¿coyote?)',
    'chivo-morado': 'Animal morado de cuernos cortos (¿chivo?)',
    'chivo-azul-hocico-rosa': 'Chivo azul de hocico rosa (¿de la danza?)',
    'el-tiempo-corona-azul': 'Tres rostros con corona de sol (¿El Tiempo?)',
    'pavo-real-celeste': 'Ave de penacho de cara celeste',
    'pavo-real-pico-dorado': 'Ave de penacho y pico dorado',
    'pavo-real-pico-anaranjado': 'Ave de penacho y pico anaranjado',
    'pavo-real-ocelos-azules': 'Ave de penacho de tres plumas',
    'pavo-real-anaranjado': 'Ave de penacho de cara anaranjada',
    'pavo-real-lila': 'Ave de penacho de cara lila',
    'cebra-blanco-negro': 'Cebra blanca y negra',
    'canido-anaranjado': 'Cánido anaranjado (¿zorro?)',
    'calavera-y-rostro-negro-estrellas': 'Rostro negro de estrellas anaranjadas',
}
# textos alternativos que afirmaban una especie no confirmada o describían collages ya recortados
ALTS = {
    'a058': 'Máscara de felino amarillo con rosetas negras, ojos verdes y boca abierta con colmillos blancos',
    'a063': 'Máscara de felino amarillo con manchas negras, orejas rojas y hocico abierto con colmillos, vista de lado',
    'a037': 'Máscara de felino negro con ojos amarillos, bigotes grises y hocico rojo abierto con colmillos amarillos',
    'a076': 'Máscara de cánido negro con mejillas blancas, orejas verdes y bandas de arcoíris en el hocico',
    'a136': 'Máscara de cánido negro con orejas verdes y amarillas, cejas y banda de arcoíris en el hocico',
    'a059': 'Máscara de cánido negro con espirales blancas en las mejillas, ojos rojos y nariz roja',
    'a052': 'Máscara de cánido de estilo realista con pelaje café grisáceo, orejas altas y ojo ámbar, vista de tres cuartos',
    'a126': 'Máscara de ave roja y verde con trazos azules y pico ganchudo negro y crema, vista de lado',
    'a043': 'Máscara negra de rostro alargado con lengua roja de fuera y un búho de ojos amarillos tallado en la frente',
    'a111': 'Máscara negra con un búho en la frente, vista de tres cuartos, con cejas doradas y lengua roja',
    'a044': 'Máscara de felino amarillo con manchas oscuras, colmillos y lengua roja, coronada por un búho gris de ojos amarillos',
    'a057': 'Máscara de felino anaranjado con manchas café y lengua roja, coronada por un búho gris de pico anaranjado',
    'a118': 'Máscara de búho gris verdoso con grandes ojos amarillos y negros y pico amarillo sobre pared azul',
    'a122': 'Máscara de madera con un lince, un búho y un felino de rosetas tallados uno encima de otro, sobre pared clara',
    'a094': 'Máscara de tres rostros barbados con banda azul, corona dorada y un sol con cara',
    'a027': 'Máscara de ave azul con pico dorado y penacho de plumas amarillas con ojos morados',
    'a107': 'Máscara La Noche de dos rostros, uno ocre y otro azul, con barba negra y corona con luna y estrella',
    'a102': 'Máscara de nahual negro con cara de felino, ojo anaranjado, orejas con rayas rojas y colmillos, vista de lado',
    'a104': 'Máscara negra de perfil con oreja felina, cresta de picos rojos, ojo anaranjado y dientes rayados de rojo',
    'a105': 'Máscara negra brillante con ojos anaranjados en forma de sol, orejas puntiagudas y la lengua de fuera',
    'a124': 'Máscara de búho gris con ojos negros de anillo anaranjado y pico anaranjado sobre pared amarilla',
    'a002': 'Máscara con cabeza de búho café sobre un felino blanco de rayas negras con la lengua roja de fuera',
    'a069': 'Máscara de tigre blanco con rayas negras, ojos verdes y fauces abiertas con colmillos',
    'a034': 'Máscara de tigre anaranjado con rayas negras, ojos verdes y colmillos, de frente',
    'a146': 'Máscara de cánido gris con pinceladas amarillas, ojos verdes y nariz roja, de frente',
    'a153': 'Máscara negra alargada cubierta de puntos crema, con estrellas anaranjadas y bigote en espiral',
    'a065': 'Máscara de ave de rostro azul y frente roja con espirales, ojos de iris anaranjado y pico largo y recto amarillo',
}
# descripciones de fotos que ya no corresponden (la foto se recortó de un collage)
DESC_FOTOS = {
    'a065': 'Máscara de ave de rostro azul y frente roja con espirales, ojos de iris anaranjado y pico largo y recto amarillo.',
}
# vistas extra sacadas de los collages (ver limpiar_album.py): id -> (pieza, texto alternativo)
EXTRA_VISTAS = {
    'a059b': ('coyote-negro-lineas-blancas', 'La misma máscara de cánido negro vista de lado, con su espiral blanca en la mejilla'),
    'a034b': ('tigre-anaranjado', 'El mismo tigre anaranjado visto de perfil, con las fauces abiertas'),
    'a146b': ('canido-gris-pinceladas', 'El mismo cánido gris de pinceladas visto de lado'),
    'a146c': ('canido-gris-pinceladas', 'El mismo cánido gris de pinceladas visto de tres cuartos'),
}
# correcciones de redacción en las descripciones de las piezas
REEMPLAZOS = [
    ('chevrón de franjas de arcoíris', 'franjas de arcoíris en V'), ('chevrón de arcoíris', 'franjas de arcoíris en V'),
    ('chevrón de franjas verde, roja, amarilla, azul marino y azul cielo', 'franjas verde, roja, amarilla, azul marino y azul cielo en V'),
    ('chevrón de franjas verde, azul marino, amarilla, roja y lila', 'franjas verde, azul marino, amarilla, roja y lila en V'),
    ('chevrón de bandas roja, amarilla, azul marino y anaranjada', 'bandas roja, amarilla, azul marino y anaranjada en V'),
    ('chevrón blanco en la frente', 'una V blanca en la frente'), ('chevrones amarillos en la caña', 'franjas amarillas en V sobre la nariz'),
    ('sobre frente y caña', 'sobre la frente y la nariz'), ('laqueadas', 'brillantes'), ('laqueado', 'brillante'),
    ('Rostro negro brillante, visto de perfil, con una oreja grande de interior rojo', 'Rostro negro brillante con orejas grandes de interior rojo'),
    ('un tecolote negro tallado en la frente', 'un búho negro tallado en la frente'),
    ('plumas de pavo real con ocelos azules', 'plumas con ocelos azules'),
]
DESCRIPCIONES = {
    'ave-azul-pico-amarillo': 'Ave de rostro azul y frente roja con espirales celestes, ojos redondos de iris anaranjado y un pico largo, recto y amarillo. Solo hay una foto pequeña de esta pieza.',
    'calavera-y-rostro-negro-estrellas': 'Rostro negro alargado cubierto de puntos color crema en líneas onduladas, con estrellas anaranjadas de ocho puntas en la frente y la barbilla, ojos azules y bigote en espiral.',
}
# textos de las salas corregidos en la revisión
SALAS = {
    'danza-de-los-morenos': {'subtitulo': 'Nueve parejas de animales, macho y hembra',
        'texto': 'En Suchitlán, la Danza de los Morenos la bailan nueve parejas de animales, macho y hembra: coyotes, chivos, borregos, tecolotes, lince y ocelote, burros, guacamayas, gallos y perros. Al frente van el coyote y el chivo como capitanes. Cuenta la familia que el coyote de bigotes de arcoíris lo crearon el abuelo y el padre de Don Gorgonio al ver a un coyote beber en un charco donde se reflejaba el arcoíris. Las piezas que ya identificó la familia llevan la marca «Confirmada por la familia»; las demás se agruparon por su parecido y esperan su confirmación.'},
    'nahuales': {'subtitulo': 'Entre la persona y el animal',
        'texto': 'Además de los animales de la danza, Don Gorgonio talla nahuales: según la tradición, personas que pueden transformarse en animal. No forman parte de la Danza de los Morenos. La familia confirmó tres: el blanco de puntos dorados, el negro y el café de larga cabellera. Las dos aves negras de pico largo se les parecen, pero aún no están confirmadas.'},
    'felinos': {'texto': 'Algunas fuentes cuentan a los tigres entre los personajes de la Danza de los Morenos, pero la pareja de felinos que nombra la familia es la del lince y el ocelote. Los felinos de esta sala, casi todos de boca abierta y colmillos, no coinciden con los linces confirmados de la danza; todavía no sabemos si alguno es el ocelote, un nahual —como el nahual negro, de cara felina— o una pieza aparte.'},
    'pelaje-de-pincel': {'subtitulo': '¿Coyotes, perros, zorros?',
        'texto': 'En estas máscaras el pelaje está pintado con pinceladas cortas, casi pelo por pelo, muy distinto del coyote de bigotes de arcoíris de la danza. Casi todas son animales de hocico largo, quizá coyotes, perros o zorros, y una tiene grandes orejas de arcoíris. Todavía no sabemos qué animal es cada una ni si alguna se usa en la danza.'},
    'bestiario': {'texto': 'Más allá de la danza, el álbum de la familia incluye venados de grandes astas, toros, jirafas, cebras, mariposas, un elefante, un jabalí, un mandril, un gorila y dos animales de cuernos que podrían ser chivos. Según AmoMéxico, el maestro crea diseños nuevos a partir de los tradicionales.'},
}
for slug, nombre in NOMBRES.items():
    if slug in piezas: piezas[slug]['nombre'] = nombre

for slug, p in piezas.items():
    for a, b in REEMPLAZOS:
        p['descripcion'] = p['descripcion'].replace(a, b)
    if slug in DESCRIPCIONES:
        p['descripcion'] = DESCRIPCIONES[slug]

for slug, p in list(piezas.items()):
    fotos = [f for f in p['fotos'] if f not in descartar]
    if len(fotos) > 1:
        fotos = [f for f in fotos if f not in debiles] or fotos
    if p['principal'] not in fotos:
        p['principal'] = max(fotos, key=lambda f: cat[f]['calidad'])
    fotos.remove(p['principal']); fotos.insert(0, p['principal'])
    fotos += [x for x, (pz, _) in EXTRA_VISTAS.items() if pz == slug]
    p['fotos'] = fotos

PAREJAS = [('danza-coyote', 'Coyotes', 'Capitán · la inteligencia'), ('danza-chivo', 'Chivos', 'Capitán · la unión y la fuerza'),
           ('danza-borrego', 'Borregos cimarrones', 'La fuerza y la testarudez'), ('danza-tecolote', 'Tecolotes', 'La sabiduría'),
           ('danza-lince-ocelote', 'Lince y ocelote', 'La agilidad y la destreza'), ('danza-burro', 'Burros', ''),
           ('danza-guacamaya', 'Guacamayas', ''), ('danza-gallo', 'Gallos', ''), ('danza-perro', 'Perros', 'Por confirmar')]
ORDEN = ['danza-de-los-morenos', 'el-tiempo-y-la-noche', 'nahuales', 'diablos', 'vida-y-muerte', 'rostros-negros', 'seres-encimados', 'felinos', 'aves', 'pelaje-de-pincel', 'bestiario']
salas_cur = {s['id']: s for s in cur['salas']}
salas, usadas = [], {}  # dict como conjunto ordenado: la salida no cambia de orden entre corridas
for sid in ORDEN:
    s = dict(salas_cur[sid], **SALAS.get(sid, {}))
    lista = [x for x in s['piezas'] if x in piezas and x not in APARTADAS and x not in usadas]
    usadas.update(dict.fromkeys(lista))
    s['piezas'] = lista
    if sid == 'danza-de-los-morenos':
        s['subsalas'] = []
        for c, t, nota in PAREJAS:
            ps = [x for x in lista if piezas[x]['categoria'] == c]
            s['subsalas'].append({'titulo': t, 'nota': nota, 'piezas': ps})
        resto = [x for x in lista if not piezas[x]['categoria'].startswith('danza-')]
        if resto: s['subsalas'].append({'titulo': 'Otras', 'nota': '', 'piezas': resto})
    salas.append(s)
faltan = [x for x in piezas if x not in usadas and x not in APARTADAS]
print('piezas sin sala:', faltan)

usadas_fotos = dict.fromkeys(f for x in usadas for f in piezas[x]['fotos'])
fotos = {}
for f in usadas_fotos:
    if f in EXTRA_VISTAS:
        fotos[f] = {'alt': EXTRA_VISTAS[f][1], 'descripcion': '', 'recorte': False}
        continue
    c = cat[f]
    fotos[f] = {'alt': ALTS.get(f, c['alt']).rstrip('.'), 'descripcion': DESC_FOTOS.get(f, c['descripcion']), 'recorte': bool(qa.get(f, {}).get('usar_recorte'))}
pieza_de = {f: x for x in usadas for f in piezas[x]['fotos']}
destacadas = [f for f in cur['destacadas'] if f in pieza_de]
out = {
    'entrada': 'Una selección de las máscaras que Don Gorgonio ha tallado y pintado a mano: los animales de la Danza de los Morenos, El Tiempo y La Noche, nahuales, diablos, rostros y un bestiario entero. Toca cualquier pieza para verla en grande y recorrer todas sus vistas.',
    'entrada_corta': 'Más de un centenar de máscaras talladas y pintadas a mano, ordenadas en salas como en un museo: la Danza de los Morenos, El Tiempo y La Noche, nahuales, diablos y un bestiario completo.',
    'salas': salas,
    'piezas': {x: {k: piezas[x][k] for k in ('nombre', 'descripcion', 'fotos', 'principal', 'categoria', 'certeza')} for x in usadas},
    'fotos': fotos, 'pieza_de': pieza_de, 'destacadas': destacadas, 'muestra': destacadas[:12],
    'apartadas': sorted(APARTADAS),
}
# En las salas se muestra siempre la foto original; los recortes aprobados forman el desfile de la entrada
PREFERENCIA = ['a024', 'a001', 'a007', 'a169', 'a006', 'a121', 'a152', 'a018', 'a043', 'a073', 'a167', 'a108', 'a141', 'a052', 'a136', 'a066', 'a080', 'a036']
aprobados = [f for f, v in fotos.items() if v['recorte']]
desfile, vistas = [], set()
for f in [x for x in PREFERENCIA if x in aprobados] + [x for x in aprobados if x not in PREFERENCIA]:
    if pieza_de[f] not in vistas:
        vistas.add(pieza_de[f]); desfile.append(f)
for v in fotos.values():
    v['recorte'] = False
out['desfile'] = desfile
out['muestra'] = destacadas[:15]  # 15 llena el mosaico sin huecos en todos los anchos
(R / 'datos/galeria.json').write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding='utf-8')
print('salas', len(salas), '| piezas', len(usadas), '| fotos', len(usadas_fotos), '| con recorte', sum(1 for f in fotos.values() if f['recorte']))
print(' '.join(sorted(f for f, v in fotos.items() if v['recorte'])))
