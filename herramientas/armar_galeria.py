"""Arma datos/galeria.json a partir de la clasificación del álbum (datos/album-catalogo.json)
y la revisión de recortes (datos/recortes-revision.json). Uso: python3 herramientas/armar_galeria.py
Después hay que volver a fijar el desfile y la muestra (ver README) y correr generar_galeria_completa.py."""
import json, sys, pathlib
S = pathlib.Path(__file__).resolve().parent.parent / 'datos'
R = pathlib.Path('/home/user/GorgonioCandelario')
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
# piezas apartadas hasta que la familia confirme la autoría
APARTADAS = {'felino-multicolor-pastel', 'toro-pastel-cuernos-rosas', 'toro-pastel-cuernos-azules'}
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
}
for slug, nombre in NOMBRES.items():
    if slug in piezas: piezas[slug]['nombre'] = nombre

for slug, p in list(piezas.items()):
    fotos = [f for f in p['fotos'] if f not in descartar]
    if len(fotos) > 1:
        fotos = [f for f in fotos if f not in debiles] or fotos
    if p['principal'] not in fotos:
        p['principal'] = max(fotos, key=lambda f: cat[f]['calidad'])
    fotos.remove(p['principal']); fotos.insert(0, p['principal'])
    p['fotos'] = fotos

PAREJAS = [('danza-coyote', 'Coyotes', 'Capitán · la inteligencia'), ('danza-chivo', 'Chivos', 'Capitán · la unión y la fuerza'),
           ('danza-borrego', 'Borregos cimarrones', 'La fuerza y la testarudez'), ('danza-tecolote', 'Tecolotes', 'La sabiduría'),
           ('danza-lince-ocelote', 'Lince y ocelote', 'La agilidad y la destreza'), ('danza-burro', 'Burros', ''),
           ('danza-guacamaya', 'Guacamayas', ''), ('danza-gallo', 'Gallos', ''), ('danza-perro', 'Perros', '')]
ORDEN = ['danza-de-los-morenos', 'el-tiempo-y-la-noche', 'nahuales', 'diablos', 'vida-y-muerte', 'rostros-negros', 'seres-encimados', 'felinos', 'aves', 'pelaje-de-pincel', 'bestiario']
salas_cur = {s['id']: s for s in cur['salas']}
salas, usadas = [], set()
for sid in ORDEN:
    s = dict(salas_cur[sid])
    lista = [x for x in s['piezas'] if x in piezas and x not in APARTADAS and x not in usadas]
    usadas.update(lista)
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

usadas_fotos = {f for x in usadas for f in piezas[x]['fotos']}
fotos = {}
for f in usadas_fotos:
    c = cat[f]
    fotos[f] = {'alt': c['alt'].rstrip('.'), 'descripcion': c['descripcion'], 'recorte': bool(qa.get(f, {}).get('usar_recorte'))}
pieza_de = {f: x for x in usadas for f in piezas[x]['fotos']}
destacadas = [f for f in cur['destacadas'] if f in pieza_de]
out = {
    'entrada': 'Una selección de las máscaras que don Gorgonio ha tallado y pintado a mano: los animales de la Danza de los Morenos, El Tiempo y La Noche, nahuales, diablos, rostros y un bestiario entero. Toca cualquier pieza para verla en grande y recorrer todas sus vistas.',
    'entrada_corta': 'Más de un centenar de máscaras talladas y pintadas a mano, ordenadas en salas como en un museo: la Danza de los Morenos, El Tiempo y La Noche, nahuales, diablos y un bestiario completo.',
    'salas': salas,
    'piezas': {x: {k: piezas[x][k] for k in ('nombre', 'descripcion', 'fotos', 'principal', 'categoria', 'certeza')} for x in usadas},
    'fotos': fotos, 'pieza_de': pieza_de, 'destacadas': destacadas, 'muestra': destacadas[:12],
    'apartadas': sorted(APARTADAS),
}
(R / 'datos/galeria.json').write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding='utf-8')
print('salas', len(salas), '| piezas', len(usadas), '| fotos', len(usadas_fotos), '| con recorte', sum(1 for f in fotos.values() if f['recorte']))
print(' '.join(sorted(f for f, v in fotos.items() if v['recorte'])))
