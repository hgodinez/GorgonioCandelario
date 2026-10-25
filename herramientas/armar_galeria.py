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

# a051 y a145 son collages: sus paneles ya están en la galería (el coyote de a051 entra como a051c)
descartar = set(sum((g['duplicados_descartar'] for g in d['agrupados']), [])) | {'a132', 'a145', 'a051'}
# Todas las fotos de sus máscaras van en la galería. Estas dos se habían marcado como duplicadas,
# pero son otra toma de la misma máscara, no la misma foto
OTRAS_TOMAS = {'a133': 'el-tiempo', 'a125': 'trio-rostros-negros-astros'}
descartar -= set(OTRAS_TOMAS)
for f, pieza in OTRAS_TOMAS.items():
    piezas[pieza]['fotos'].append(f)
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
# textos alternativos que afirmaban una especie no confirmada o describían collages ya recortados,
# y los de las piezas que identificó Don Gorgonio, con el nombre que les dio
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
    'a027': 'Máscara de pavo real azul con pico dorado y penacho de plumas amarillas con ojos morados',
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
    'a065': 'Máscara de pelícano de rostro azul y frente roja con espirales, ojos de iris anaranjado y pico largo y recto amarillo',
    'a163': 'Máscara de gallina anaranjada con cresta color vino escalonada, pico amarillo y barbas rojas, de frente en pared blanca',
    'a119': 'Máscara de chiva blanca y negra con cuernos largos color café, ojos verdes y barba de fibra',
    'a087': 'Máscara de coyota amarilla con orejas verdes y bandas de arcoíris alrededor de los ojos',
    'a020': 'Máscara de coyota de rostro blanco con orejas amarillas, franjas y espirales de arcoíris y nariz negra',
    'a157': 'Máscara de perro xoloitzcuintle negro con franjas de arcoíris en ceja y hocico, orejas verdes y colmillos',
    'a089': 'Perfil de máscara de chiva morada con cuernos curvos rayados y hocico verde',
    'a081': 'Máscara de ocelote amarillo con lunares rojos, anaranjados y negros y orejas grises',
    'a073': 'Máscara de ocelote amarillo con lunares rojos, negros y anaranjados, orejas grises y hocico largo, vista de perfil',
    'a045': 'Máscara de jaguar anaranjado con rosetas negras, orejas rojas puntiagudas y ojos azules',
    'a026': 'Máscara de jaguar anaranjado con manchas negras en anillo, ojos azules y orejas grandes rojizas, vista de tres cuartos',
    'a099': 'Máscara de jaguar multicolor con diseños geométricos y florales en azul, morado, rosa y anaranjado',
    'a117': 'Máscara de jaguar multicolor de orejas redondas, pintada con figuras geométricas y hojas en azul, lila, verde y negro',
    'a140': 'Máscara de águila azul con trazos amarillos, ojo verde con pestañas y pico curvo amarillo',
    'a055': 'Máscara de zorro anaranjado con pelo en trazos negros, orejas puntiagudas grises y ojos verdes',
    'a036': 'Máscara de zorro anaranjado de hocico largo con trazos negros de pelo, orejas grises y nariz negra, vista de tres cuartos',
    'a083': 'Máscara de lobo gris de estilo realista con ojos amarillo verdoso y boca abierta',
    'a077': 'Máscara de coyota amarilla con franjas de colores alrededor de los ojos, orejas verdes y nariz negra, sobre una pared rosa',
    'a080': 'Máscara de ave anaranjada de pico rojo con penacho verde de plumas con ocelos, de frente',
    'a012': 'Máscara del gallo rojo, de rostro blanco con cresta roja, ojos amarillos de rayos negros y pico verde, sobre una mesa de madera',
}
# descripciones de fotos que ya no corresponden (la foto se recortó de un collage, o Don Gorgonio dijo que es hembra)
DESC_FOTOS = {
    'a065': 'Máscara de pelícano de rostro azul y frente roja con espirales, ojos de iris anaranjado y pico largo y recto amarillo.',
    'a163': 'Gallina de la Danza de los Morenos, de cara anaranjada y pico amarillo. Lleva una cresta alta y escalonada color vino, decorada con triángulos amarillos, y barbas rojas a los lados.',
    'a119': 'Chiva blanca y negra con cuernos largos color café, ojos verdes y barba de fibra.',
    'a087': 'Máscara de coyota amarilla con orejas verdes y azules, y anillos de colores de arcoíris alrededor de los ojos.',
    'a020': 'Coyota de rostro blanco con orejas amarillas, franjas de arcoíris en la frente y espirales de colores en las mejillas. Coincide con el diseño del coyote de la danza confirmado por la familia.',
}
# vistas extra sacadas de los collages (ver limpiar_album.py): id -> (pieza, texto alternativo)
EXTRA_VISTAS = {
    'a059b': ('coyote-negro-lineas-blancas', 'La misma máscara de cánido negro vista de lado, con su espiral blanca en la mejilla'),
    'a034b': ('tigre-anaranjado', 'El mismo tigre anaranjado visto de perfil, con las fauces abiertas'),
    'a146b': ('canido-gris-pinceladas', 'El mismo cánido gris de pinceladas visto de lado'),
    'a146c': ('canido-gris-pinceladas', 'El mismo cánido gris de pinceladas visto de tres cuartos'),
    'a027b': ('pavo-real-pico-dorado', 'El mismo pavo real de pico dorado de frente, sobre una pared azul'),
    'a051c': ('coyote-blanco-arcoiris', 'El coyote blanco de arcoíris de frente, sobre una pared azul'),
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
    'ave-azul-pico-amarillo': 'Ave de rostro azul y frente roja con espirales celestes, ojos redondos de iris anaranjado y un pico largo, recto y amarillo.',
    'gallo-anaranjado': 'Gallina de cara anaranjada con pico amarillo grueso, cresta escalonada color vino con triángulos amarillos, barbas rojas y ojos de iris verde.',
    'chivo-blanco-negro': 'Chiva blanca y negra brillante con cuernos largos café oscuro, orejas negras de interior blanco, ojos amarillos de iris verde, boca verde y barba de fibra clara.',
    'coyote-amarillo-anillos': 'Coyota amarilla con orejas verdes y azul marino, anillos morados, rojos, blancos y verdes que rodean los ojos y bajan hacia el hocico, y nariz café oscuro.',
    'coyote-crema-ojos-azules': 'Coyota de base crema con orejas amarillas por fuera y azul marino por dentro, franjas verde, roja, amarilla, azul marino y azul cielo en V, espirales de arcoíris en las mejillas y ojos blancos de iris azul.',
    'calavera-y-rostro-negro-estrellas': 'Rostro negro alargado cubierto de puntos color crema en líneas onduladas, con estrellas anaranjadas de ocho puntas en la frente y la barbilla, ojos azules y bigote en espiral.',
}
# Lo que contestó Don Gorgonio en la encuesta (23 de octubre de 2026; ver datos/respuestas-don-gorgonio.json):
# el nombre que les dio, la sala a la que van y lo que representan, en sus palabras
NOMBRES_DON_GORGONIO = {
    'coyote-crema-ojos-azules': 'Coyota crema de ojos azules',
    'coyote-amarillo-anillos': 'Coyota amarilla de anillos',
    'canido-negro-boca-abierta': 'Perro xoloitzcuintle',
    'chivo-blanco-negro': 'Chiva blanca y negra',
    'felino-lunares': 'Ocelote amarillo de lunares',
    'felino-rosetas': 'Jaguar anaranjado de rosetas',
    'gallo-anaranjado': 'Gallina anaranjada',
    'gallo-cresta-roja': 'Gallo rojo',
    'sol-y-luna': 'El Ocaso',
    'diablo-marco-moteado-lengua-negra': 'Diablo el Pecado',
    'vida-muerte-malva': 'Dualidad vida y muerte',
    'felino-multicolor-pastel': 'Jaguar multicolor',
    'pavo-real-pico-dorado': 'Pavo real de pico dorado',
    'ave-azul-pico-curvo': 'Águila multicolor',
    'ave-azul-pico-amarillo': 'Pelícano',
    'canido-anaranjado': 'Zorro anaranjado',
    'canido-gris-verdoso': 'Lobo gris verdoso',
    'toro-pastel-cuernos-rosas': 'Toro multicolor de cuernos ondulados',
    'mariposa-azul': 'Mariposa multicolor',
    'chivo-azul-hocico-rosa': 'Chivo multicolor',
    'chivo-morado': 'Chiva morada',
}
# pieza -> (sala, categoría): las que según él son de la danza entran a su pareja; las de adorno salen de la danza
MOVER = {
    'canido-negro-boca-abierta': ('danza-de-los-morenos', 'danza-perro'),
    'lince-naturalista': ('danza-de-los-morenos', 'danza-lince-ocelote'),
    'buho-azul': ('danza-de-los-morenos', 'danza-tecolote'),
    'chivo-morado': ('danza-de-los-morenos', 'danza-chivo'),
    'felino-rosetas': ('felinos', 'otro-animal'),
    'chivo-azul-hocico-rosa': ('bestiario', 'otro-animal'),
    'canido-gris-verdoso': ('pelaje-de-pincel', 'otro-animal'),
}
DICE_DON_GORGONIO = {
    'coyote-blanco-arcoiris': 'Según Don Gorgonio, es el coyote, segundo capitán de la Danza de los Morenos, y representa la inteligencia.',
    'coyote-blanco-esbelto': 'Según Don Gorgonio, es el mismo coyote blanco de arcoíris en otra expresión de forma.',
    'coyote-crema-ojos-azules': 'Según Don Gorgonio, es una coyota.',
    'coyote-amarillo-anillos': 'Según Don Gorgonio, es una coyota de la Danza de los Morenos y representa la inteligencia.',
    'canido-negro-boca-abierta': 'Según Don Gorgonio, es un perro xoloitzcuintle macho de la Danza de los Morenos y representa la fidelidad y la compañía.',
    'chivo-rojo-antifaz-amarillo': 'Según Don Gorgonio, es el chivo, primer capitán de la Danza de los Morenos, y representa la unión y la fuerza.',
    'chivo-blanco-negro': 'Según Don Gorgonio, es la chiva de la Danza de los Morenos y representa la unión y la fuerza.',
    'borrego-anaranjado': 'Según Don Gorgonio, es un borrego macho de la Danza de los Morenos y representa la fuerza y la testarudez.',
    'tecolote-rojo': 'Según Don Gorgonio, es un tecolote macho de la Danza de los Morenos y representa la sabiduría.',
    'lince-franjas-zigzag': 'Según Don Gorgonio, es un lince hembra de la Danza de los Morenos y representa la agudeza visual y el sigilo.',
    'felino-lunares': 'Según Don Gorgonio, es un ocelote macho de la Danza de los Morenos y representa la audacia y el valor.',
    'felino-rosetas': 'Según Don Gorgonio, es un jaguar de adorno, que no se baila, y representa la valentía y el poder.',
    'burro-gris': 'Según Don Gorgonio, es un burro macho de la Danza de los Morenos y representa la docilidad y la resistencia.',
    'guacamaya-verde': 'Según Don Gorgonio, es una guacamaya hembra de la Danza de los Morenos y representa la fertilidad y la abundancia.',
    'gallo-anaranjado': 'Según Don Gorgonio, es la gallina de la Danza de los Morenos y representa la maternidad y la prosperidad.',
    'gallo-cresta-roja': 'Según Don Gorgonio, es el gallo rojo de la Danza de los Morenos y representa el nuevo día o el amanecer.',
    'el-tiempo': 'Según Don Gorgonio, esta máscara es de adorno, no se baila, y representa las tres etapas de la vida: niño, adulto y viejo.',
    'sol-y-luna': 'Según Don Gorgonio, es El Ocaso, una máscara de adorno que representa el final del día.',
    'diablo-marco-moteado-lengua-negra': 'Según Don Gorgonio, es el Diablo el Pecado: se usa en las pastorelas y representa los siete pecados capitales.',
    'vida-muerte-malva': 'Según Don Gorgonio, es la Dualidad vida y muerte, una máscara de adorno que representa el ciclo de la vida.',
    'lince-naturalista': 'Según Don Gorgonio, es un lince macho de la Danza de los Morenos y representa la agudeza visual y el sigilo.',
    'felino-multicolor-pastel': 'Según Don Gorgonio, es un jaguar multicolor de adorno y representa la valentía y el poder.',
    'pavo-real-pico-dorado': 'Según Don Gorgonio, es un pavo real hembra de la Danza de los Morenos y representa la belleza y la elegancia.',
    'ave-azul-pico-curvo': 'Según Don Gorgonio, es un águila multicolor de adorno y representa el liderazgo y la libertad.',
    'ave-azul-pico-amarillo': 'Según Don Gorgonio, es un pelícano de adorno y representa la generosidad y el sacrificio.',
    'pato': 'Según Don Gorgonio, es de adorno y representa el equilibrio y la resiliencia.',
    'buho-azul': 'Según Don Gorgonio, es un búho macho de la Danza de los Morenos y representa la sabiduría.',
    'canido-anaranjado': 'Según Don Gorgonio, es un zorro de adorno y representa la adaptabilidad y la astucia.',
    'canido-gris-verdoso': 'Según Don Gorgonio, es un lobo de adorno y representa la astucia y la autenticidad.',
    'toro-cafe': 'Según Don Gorgonio, es de adorno y representa la fuerza y la ascendencia.',
    'toro-pastel-cuernos-rosas': 'Según Don Gorgonio, es un toro multicolor de adorno y representa la fuerza y la ascendencia.',
    'jabali': 'Según Don Gorgonio, es de adorno y representa la ferocidad y el coraje.',
    'mandril': 'Según Don Gorgonio, es de adorno y representa la protección.',
    'gorila': 'Según Don Gorgonio, es de adorno y representa la lealtad y el liderazgo.',
    'mariposa-azul': 'Según Don Gorgonio, es una mariposa multicolor de adorno y representa la transformación y el renacimiento.',
    'chivo-azul-hocico-rosa': 'Según Don Gorgonio, es un chivo multicolor de adorno y representa la unión y la fuerza.',
    'chivo-morado': 'Según Don Gorgonio, es una chiva morada de la Danza de los Morenos y representa la unión y la fuerza.',
}
# notas del sitio que van después de lo que dijo Don Gorgonio
NOTAS = {'ave-azul-pico-amarillo': 'Solo hay una foto pequeña de esta pieza.'}
# textos de las salas corregidos en la revisión
SALAS = {
    'danza-de-los-morenos': {'subtitulo': 'Nueve parejas de animales, macho y hembra',
        'texto': 'En Suchitlán, la Danza de los Morenos la bailan nueve parejas de animales, macho y hembra: chivos, coyotes, borregos, tecolotes, lince y ocelote, burros, guacamayas, gallos y perros. Al frente van el chivo y el coyote como capitanes: según Don Gorgonio, el chivo es el primero y el coyote el segundo. Cuenta la familia que el coyote de bigotes de arcoíris lo crearon el abuelo y el padre de Don Gorgonio al ver a un coyote beber en un charco donde se reflejaba el arcoíris. Las piezas que ya identificaron Don Gorgonio o su familia llevan la marca «Confirmada por Don Gorgonio» o «Confirmada por la familia»; las demás se agruparon por su parecido y esperan confirmación.'},
    'el-tiempo-y-la-noche': {'texto': 'El Tiempo tiene tres rostros que comparten los ojos, bajo una corona con sol, luna y estrella; La Noche tiene dos, y uno de ellos es azul. En el Museum of International Folk Art, en Santa Fe, Nuevo México, hay un Tiempo de Don Gorgonio de 1995, catalogado como máscara para la Danza de la Pastorela: hay Tiempos de los dos usos. El de esta sala, según Don Gorgonio, es de adorno, no se baila, y representa las tres etapas de la vida: niño, adulto y viejo. El Ocaso, la máscara de sol y luna, representa para él el final del día. Las demás piezas de dos o tres rostros de esta sala esperan todavía la confirmación de la familia.'},
    'diablos': {'texto': 'Fuera de la danza, Don Gorgonio talla diablos, pastores, ángeles de pastorela y los siete pecados capitales. Sus diablos tienen el rostro rojo, cuernos y colmillos largos, y algunos llevan animales tallados en la frente, alrededor de la cara o bajo la barbilla. Uno de ellos es el Diablo el Pecado, que según Don Gorgonio se usa en las pastorelas y representa los siete pecados capitales; de los demás todavía no sabemos en qué fiesta se usó cada uno.'},
    'vida-y-muerte': {'texto': 'En estas máscaras un mismo rostro se parte a lo largo: de un lado, un hombre de barba tallada; del otro, una calavera. Don Gorgonio llama a una de ellas Dualidad vida y muerte, y dice que representa el ciclo de la vida. Las acompañan otros rostros humanos, entre ellos un hombre calvo de barba negra, otro con gorro de sol y luna y uno de dos tonos, cuyos personajes aún no conocemos.'},
    'aves': {'texto': 'Además de las guacamayas, los gallos y los tecolotes de la danza, esta sala reúne aves de penacho con plumas de ojos de colores —Don Gorgonio identificó una como pavo real y dice que es de la Danza de los Morenos, aunque el pavo real no está entre las nueve parejas—, un pato, un águila multicolor, un pelícano, un ave de pico ganchudo y varios búhos de rostro gris o plateado. Según Don Gorgonio, el búho azul es de la danza; por eso está en la sala de la Danza de los Morenos, con los tecolotes. De los demás búhos todavía no sabemos si son tecolotes, nahuales u otras piezas.'},
    'nahuales': {'subtitulo': 'Entre la persona y el animal',
        'texto': 'Además de los animales de la danza, Don Gorgonio talla nahuales: según la tradición, personas que pueden transformarse en animal. No forman parte de la Danza de los Morenos. La familia confirmó tres: el blanco de puntos dorados, el negro y el café de larga cabellera. Las dos aves negras de pico largo se les parecen, pero aún no están confirmadas.'},
    'felinos': {'texto': 'Algunas fuentes cuentan a los tigres entre los personajes de la Danza de los Morenos, pero la pareja de felinos que nombra la familia es la del lince y el ocelote. Don Gorgonio identificó como de la danza dos linces, una hembra y un macho, y un ocelote, y están en la sala de la Danza de los Morenos. Aquí quedan los demás felinos, casi todos de boca abierta y colmillos. Don Gorgonio identificó dos jaguares de adorno, el anaranjado de rosetas y el multicolor; de los demás todavía no sabemos si alguno es de la danza, un nahual —como el nahual negro, de cara felina— o una pieza aparte.'},
    'pelaje-de-pincel': {'subtitulo': 'Un zorro, un lobo y otros animales de hocico largo',
        'texto': 'En estas máscaras el pelaje está pintado con pinceladas cortas, casi pelo por pelo, muy distinto del coyote de bigotes de arcoíris de la danza. Casi todas son animales de hocico largo, y una tiene grandes orejas de arcoíris. Don Gorgonio identificó un zorro y un lobo, los dos de adorno; de las demás todavía no sabemos qué animal es cada una ni si alguna se usa en la danza.'},
    'bestiario': {'texto': 'Más allá de la danza, el álbum de la familia incluye venados de grandes astas, toros, jirafas, cebras, mariposas, un elefante, un jabalí, un mandril, un gorila y un chivo multicolor. Don Gorgonio confirmó que el toro café, el toro multicolor de cuernos ondulados, el jabalí, el mandril, el gorila, la mariposa multicolor y el chivo multicolor son de adorno: no se bailan. Según AmoMéxico, el maestro crea diseños nuevos a partir de los tradicionales.'},
}
for slug, nombre in list(NOMBRES.items()) + list(NOMBRES_DON_GORGONIO.items()):
    if slug in piezas: piezas[slug]['nombre'] = nombre
for slug, (sala, categoria) in MOVER.items():
    piezas[slug]['categoria'] = categoria
for slug in DICE_DON_GORGONIO:
    piezas[slug]['certeza'] = 'confirmada-maestro'

for slug, p in piezas.items():
    for a, b in REEMPLAZOS:
        p['descripcion'] = p['descripcion'].replace(a, b)
    if slug in DESCRIPCIONES:
        p['descripcion'] = DESCRIPCIONES[slug]
    if slug in DICE_DON_GORGONIO:
        p['descripcion'] = p['descripcion'].rstrip() + ' ' + DICE_DON_GORGONIO[slug]
    if slug in NOTAS:
        p['descripcion'] = p['descripcion'].rstrip() + ' ' + NOTAS[slug]

for slug, p in list(piezas.items()):
    # también las fotos chicas o borrosas: quedan como vistas extra, la principal sigue siendo la mejor
    fotos = [f for f in p['fotos'] if f not in descartar]
    if p['principal'] not in fotos:
        p['principal'] = max(fotos, key=lambda f: cat[f]['calidad'])
    fotos.remove(p['principal']); fotos.insert(0, p['principal'])
    fotos += [x for x, (pz, _) in EXTRA_VISTAS.items() if pz == slug]
    p['fotos'] = fotos

# Las nueve parejas, con lo que simboliza cada una según Don Gorgonio (el chivo es el primer capitán y el coyote el segundo)
PAREJAS = [('danza-chivo', 'Chivos', 'Primer capitán · la unión y la fuerza'), ('danza-coyote', 'Coyotes', 'Segundo capitán · la inteligencia'),
           ('danza-borrego', 'Borregos cimarrones', 'La fuerza y la testarudez'), ('danza-tecolote', 'Tecolotes', 'La sabiduría'),
           ('danza-lince-ocelote', 'Lince y ocelote', 'El lince, la agudeza visual y el sigilo; el ocelote, la audacia y el valor'),
           ('danza-burro', 'Burros', 'La docilidad y la resistencia'), ('danza-guacamaya', 'Guacamayas', 'La fertilidad y la abundancia'),
           ('danza-gallo', 'Gallos', 'El gallo, el nuevo día o el amanecer; la gallina, la maternidad y la prosperidad'), ('danza-perro', 'Perros', 'La fidelidad y la compañía')]
ORDEN = ['danza-de-los-morenos', 'el-tiempo-y-la-noche', 'nahuales', 'diablos', 'vida-y-muerte', 'rostros-negros', 'seres-encimados', 'felinos', 'aves', 'pelaje-de-pincel', 'bestiario']
salas_cur = {s['id']: dict(s, piezas=[x for x in s['piezas'] if x not in MOVER]) for s in cur['salas']}
for slug, (sala, categoria) in MOVER.items():
    salas_cur[sala]['piezas'].append(slug)
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
# las fotos chicas o borrosas están en las salas, pero no en el desfile
debiles = set(cur['fotos_debiles'])
aprobados = [f for f, v in fotos.items() if v['recorte'] and f not in debiles]
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
