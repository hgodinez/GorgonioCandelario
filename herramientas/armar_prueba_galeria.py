"""Arma pruebas/galeria.html: una copia de galeria.html en la que cada sala abre con una portada que se acerca al hacer
scroll: la foto de una máscara empieza como tarjeta y crece hasta su tamaño completo, y luego aparecen el número, el nombre
y el subtítulo de la sala (la portada es de la sala, no habla de la máscara). Debajo, la sala solo conserva su párrafo;
su título queda para los lectores de pantalla. La barra de salas lleva a la portada ya terminada.
Sirve para probar el efecto en la galería sin tocar la de verdad. La copia no está enlazada desde el sitio, tiene
noindex y Netlify no la publica (netlify.toml no copia pruebas/). Si cambia la galería, vuelve a correrlo.
El efecto se prueba aparte en pruebas/zoom.html; los dos llevan los mismos arreglos.
Uso: python3 herramientas/armar_prueba_galeria.py ."""
import html, json, pathlib, re, sys

R = pathlib.Path(sys.argv[1])
t = (R / 'galeria.html').read_text(encoding='utf-8')
g = json.loads((R / 'datos/galeria.json').read_text(encoding='utf-8'))
tam = json.loads((R / 'datos/album-tamanos.json').read_text(encoding='utf-8'))

# La máscara que abre cada sala: (pieza, foto, foco vertical en % desde arriba, hacia donde se acerca).
# Elegidas por nitidez a pantalla completa (1200x1600 de preferencia), encuadre 3:4 y fondo limpio.
APERTURAS = {
    'danza-de-los-morenos': ('buho-azul', 'a050', 35),            # el tecolote que confirmó Don Gorgonio (el tecolote rojo solo tiene foto de 364x567)
    'el-tiempo-y-la-noche': ('el-tiempo', 'a025', 49),
    'nahuales': ('nahual-negro', 'a102', 43),
    'diablos': ('diablo-rojo-lengua', 'a008', 55),
    'vida-y-muerte': ('vida-muerte-malva', 'a127', 38),
    'rostros-negros': ('rostro-negro-cresta-roja', 'a134', 38),
    'seres-encimados': ('jaguar-amarillo-con-buho', 'a033', 42),
    'felinos': ('jaguar-rosetas', 'a058', 31),                    # fauces abiertas, como dice el subtítulo de la sala
    'aves': ('pavo-real-pico-anaranjado', 'a108', 50),           # un pavo real y no otro búho
    'pelaje-de-pincel': ('canido-anaranjado', 'a055', 43),
    'bestiario': ('toro-pastel-cuernos-rosas', 'a142', 55),
}

CABEZA = '''  <script>
    if (!matchMedia("(prefers-reduced-motion: reduce)").matches) document.documentElement.classList.add("zoom-activo");
    // con #sala-… en la dirección, el navegador salta sin animación; el script lleva luego a la portada de esa sala
    if (/^#sala-/.test(location.hash)) document.documentElement.style.scrollBehavior = "auto";
  </script>
  <style>
    /* Portada de cada sala (prueba). --recorrido: cuántas pantallas de scroll dura el acercamiento */
    .zoom { --recorrido: 1; position: relative; border-top: 1px solid rgba(255, 250, 240, 0.08); }
    .zoom-escena { --alto-escena: 100svh; position: relative; min-height: var(--alto-escena); overflow: hidden; display: grid; place-items: center; }
    .zoom-caja {
      position: relative; z-index: 1;
      width: min(100%, calc((var(--alto-escena) - 11rem) * 0.75)); aspect-ratio: 3 / 4; align-self: start;
      transform-origin: 50% 50%; will-change: transform;
    }
    /* en teléfonos, a todo el ancho y con el alto limitado (la foto se recorta un poco con object-fit) */
    @media (max-aspect-ratio: 1 / 1) and (max-width: 600px) {
      .zoom-escena { --alto-foto: min(calc(100vw * 4 / 3), calc(var(--alto-escena) - 11rem)); }
      .zoom-caja { width: 100%; aspect-ratio: auto; height: var(--alto-foto); }
      /* el texto va justo debajo de la foto, sin una franja vacía en medio */
      .zoom-texto { top: var(--alto-foto); bottom: auto; padding-top: 1.25rem; }
      .zoom-texto::before { display: none; }
    }
    /* la sombra se compensa una sola vez (--k, --radio-sombra al medir): en cada cuadro solo cambia su opacidad */
    .zoom-caja::before {
      content: ""; position: absolute; inset: 0; border-radius: var(--radio-sombra, 0);
      box-shadow: 0 0 0 calc(1px * var(--k, 1)) rgba(255, 250, 240, 0.16), 0 calc(24px * var(--k, 1)) calc(48px * var(--k, 1)) rgba(0, 0, 0, 0.5);
      opacity: var(--sombra, 0); will-change: opacity;
    }
    .zoom-foto { position: relative; margin: 0; width: 100%; height: 100%; overflow: hidden; border-radius: var(--radio-caja, 0); background: #2a211b; }
    .zoom-foto img {
      width: 100%; height: 100%; object-fit: cover; object-position: 50% var(--foco, 42%); transform-origin: 50% var(--foco, 42%);
      will-change: transform; color: #e9dfcf; font-size: 0.95rem;
    }
    .zoom-texto {
      position: absolute; z-index: 2; left: 0; right: 0; bottom: 0; max-height: 100%; overflow-y: auto;
      padding: 2.5rem var(--margen) max(1.5rem, env(safe-area-inset-bottom)); color: var(--blanco);
    }
    .zoom-texto::before {
      content: ""; position: absolute; inset: 0; z-index: -1; opacity: var(--texto, 1);
      background: linear-gradient(rgba(20, 16, 13, 0), rgba(20, 16, 13, 0.9) 2.5rem, #14100d 5rem);
    }
    .zoom-texto .sala-numero { display: block; margin-bottom: 0.3rem; }
    .zoom-texto .zoom-nombre { font-family: var(--fuente-titulos); font-weight: 600; font-size: clamp(1.9rem, 4.2vw, 2.9rem); line-height: 1.12; margin: 0 0 0.3em; color: var(--blanco); max-width: none; }
    .zoom-texto p { margin: 0; max-width: 32rem; color: #e2d7c6; font-size: 1.08rem; }
    .zoom-texto .sala-sub { margin: 0.1rem 0 0; color: var(--cempasuchil); font-family: var(--fuente-titulos); font-style: italic; font-size: 1.2rem; }
    /* Debajo de la portada, la sala solo muestra su párrafo: el número, el título y el subtítulo ya están en la portada
       (el título sigue ahí para los lectores de pantalla) */
    .visualmente-oculto { position: absolute !important; width: 1px; height: 1px; overflow: hidden; clip-path: inset(50%); white-space: nowrap; }
    .zoom + .sala { padding-top: clamp(1.75rem, 4vw, 3rem); border-top: 0; }
    .zoom + .sala .sala-encabezado { display: block; }
    .zoom + .sala .sala-texto { max-width: 46rem; font-size: 1.08rem; }
    .zoom-pista {
      position: absolute; z-index: 2; left: 0; right: 0; bottom: max(1.25rem, env(safe-area-inset-bottom)); margin: 0;
      text-align: center; font-size: 0.85rem; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase; color: #cbbfae; pointer-events: none;
    }
    .zoom-pista::after { content: ""; display: block; width: 1px; height: 2rem; margin: 0.5rem auto 0; background: currentColor; }
    @media (max-height: 500px) { .zoom-pista { display: none; } }
    @media (min-aspect-ratio: 1 / 1) {
      .zoom-escena { grid-template-columns: auto minmax(0, 30rem); justify-content: center; column-gap: clamp(2rem, 5vw, 5rem); }
      .zoom-caja { width: auto; height: min(var(--alto-escena), 60vw); align-self: center; }
      /* el relleno absorbe los 16px con que sube el texto (sin desborde falso) y deja ver el anillo de foco */
      .zoom-texto { position: relative; max-height: var(--alto-escena); padding: 1rem var(--margen) 1rem 0.5rem; margin-left: -0.5rem; }
      .zoom-texto::before { display: none; }
    }
    @media (min-aspect-ratio: 3 / 2) { .zoom-caja { height: var(--alto-escena); } }
    .zoom-activo .zoom { height: calc((1 + var(--recorrido)) * 100vh); height: calc((1 + var(--recorrido)) * 100svh); }
    .zoom-activo .zoom-escena { position: sticky; top: 0; height: 100vh; height: var(--alto-escena); }
    .zoom-activo .zoom-texto > * { opacity: 0; pointer-events: none; will-change: opacity, transform; }
    .zoom-activo .zoom-texto::before { opacity: var(--texto, 0); }
    html:not(.zoom-activo) .zoom-pista { display: none; }
    /* mientras una escena está fija se esconden el encabezado y la barra de salas; solo el foco del teclado los retiene */
    .zoom-activo .encabezado, .zoom-activo .salas-nav { transition: transform 0.3s ease; }
    .zoom-activo .encabezado:focus-within, .zoom-activo .salas-nav:focus-within { transition: none; }
    .zoom-fijo .encabezado:not(:has(:focus-visible)) { transform: translateY(-100%); }
    .zoom-fijo .salas-nav:not(:has(:focus-visible)) { transform: translateY(calc(-100% - 4rem)); }
    /* Shift+Tab a una barra escondida: sin scroll-padding, el navegador no retrocede la página */
    html.zoom-fijo:has(.encabezado:focus-within, .salas-nav:focus-within) { scroll-padding-top: 0; }
  </style>
'''

SCRIPT = '''  <script>
    (function () {
      var raiz = document.documentElement;
      var zooms = [].map.call(document.querySelectorAll(".zoom"), function (seccion) {
        var escena = seccion.querySelector(".zoom-escena"), caja = seccion.querySelector(".zoom-caja");
        return { seccion: seccion, escena: escena, caja: caja, foto: caja.querySelector("img"), pista: seccion.querySelector(".zoom-pista"),
                 textos: seccion.querySelectorAll(".zoom-texto > *"), inicio: null, ultimoP: 0 };
      });
      var pendiente = false;
      function activo() { return raiz.classList.contains("zoom-activo"); }
      function tramo(p, a, b) { return Math.min(1, Math.max(0, (p - a) / (b - a))); }
      function suave(t) { return t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2; }
      // empieza a crecer en cuanto se fija, con la misma velocidad con que venía (pendiente 1), y llega despacio
      function arranque(t) { return t + t * t - t * t * t; }
      function recorrido(z) { return z.seccion.offsetHeight - z.escena.offsetHeight; }
      function inicioSeccion(z) { return z.seccion.getBoundingClientRect().top + scrollY; }
      function saltar(y) { var antes = raiz.style.scrollBehavior; raiz.style.scrollBehavior = "auto"; scrollTo(0, y); raiz.style.scrollBehavior = antes; }

      // Cada caja está en su lugar final; se mide para saber cuánto encogerla y moverla al principio (como tarjeta).
      // Primero se quitan todas las transformaciones y después se leen todas las medidas, para no forzar el diseño en cada una.
      function medir() {
        zooms.forEach(function (z) { z.caja.style.transform = "none"; });
        zooms.forEach(function (z) {
          var r = z.caja.getBoundingClientRect(), e = z.escena.getBoundingClientRect();
          var ancho = Math.min(e.width * 0.62, e.height * 0.62 * 0.75, 300);
          z.inicio = { escala: ancho / r.width, dx: e.left + e.width / 2 - (r.left + r.width / 2), dy: e.top + e.height * 0.42 - (r.top + r.height / 2) };
        });
        zooms.forEach(function (z) {
          z.caja.style.setProperty("--k", (1 / z.inicio.escala).toFixed(3));
          z.caja.style.setProperty("--radio-sombra", (14 / z.inicio.escala).toFixed(1) + "px");
        });
      }

      function pintarZoom(z, arriba, largo) {
        z.ultimoP = largo > 0 ? -arriba / largo : 1;  // sin recortar: sirve para volver al mismo punto al girar
        var p = Math.min(1, Math.max(0, z.ultimoP));
        var c = arranque(tramo(p, 0, 0.45));
        var s = z.inicio.escala + (1 - z.inicio.escala) * c;
        z.caja.style.transform = "translate3d(" + (z.inicio.dx * (1 - c)).toFixed(1) + "px," + (z.inicio.dy * (1 - c)).toFixed(1) + "px,0) scale(" + s.toFixed(4) + ")";
        z.caja.style.setProperty("--radio-caja", (14 * (1 - c) / s).toFixed(1) + "px");
        z.caja.style.setProperty("--sombra", (1 - c).toFixed(3));
        z.foto.style.transform = "scale(" + (1 + 0.06 * suave(tramo(p, 0.45, 1))).toFixed(4) + ")";
        z.pista.style.opacity = (1 - tramo(c, 0.03, 0.2)).toFixed(3);
        var primero = 0;
        for (var i = 0; i < z.textos.length; i++) {
          var t = suave(tramo(p, 0.45 + i * 0.06, 0.55 + i * 0.06));
          if (i === 0) primero = t;
          z.textos[i].style.opacity = t.toFixed(3);
          z.textos[i].style.transform = "translate3d(0," + ((1 - t) * 16).toFixed(1) + "px,0)";
          z.textos[i].style.pointerEvents = t > 0.5 ? "auto" : "";
        }
        z.escena.style.setProperty("--texto", primero.toFixed(3));
      }

      function pintar() {
        pendiente = false;
        if (!activo()) return;
        // primero se lee todo, después se escribe
        var alto = innerHeight, medidas = zooms.map(function (z) {
          var r = z.seccion.getBoundingClientRect();
          return { arriba: r.top, abajo: r.bottom, largo: recorrido(z), escena: z.escena.offsetHeight };
        });
        // las barras se esconden al fijarse una escena y vuelven cuando ya se fue un cuarto de ella; con 48px de margen
        // para que no parpadeen si el dedo o la inercia se detienen justo en el borde
        var dentro = false, cerca = false;
        medidas.forEach(function (m) {
          var limite = -m.largo - m.escena / 4;
          if (m.arriba <= 0 && m.arriba >= limite) dentro = true;
          if (m.arriba <= 48 && m.arriba >= limite - 48) cerca = true;
        });
        var fijo = raiz.classList.contains("zoom-fijo");
        if (!fijo && dentro) raiz.classList.add("zoom-fijo");
        else if (fijo && !cerca) raiz.classList.remove("zoom-fijo");
        // solo se pintan las que están en pantalla o cerca; el largo se guarda para compararlo al cambiar el tamaño
        zooms.forEach(function (z, i) {
          var m = medidas[i];
          z.largo = m.largo;
          if (m.abajo < -alto || m.arriba > alto * 1.5) return;
          pintarZoom(z, m.arriba, m.largo);
        });
      }
      function pedir() { if (!pendiente) { pendiente = true; requestAnimationFrame(pintar); } }
      function rehacer() { medir(); pintar(); }

      // Al cambiar el tamaño, la escena que estaba fija vuelve al mismo punto de su animación
      addEventListener("resize", function () {
        if (!activo()) return;
        // el largo de antes es el que se guardó al pintar: al llegar aquí el navegador ya aplicó el tamaño nuevo
        var actual = null;
        zooms.forEach(function (z) { if (z.ultimoP > 0 && z.ultimoP <= 1.001) actual = { z: z, p: z.ultimoP, largo: z.largo }; });
        rehacer();
        if (actual && recorrido(actual.z) !== actual.largo) { saltar(inicioSeccion(actual.z) + Math.min(actual.p, 1) * recorrido(actual.z)); pintar(); }
      });
      // La barra de salas lleva a la portada de cada sala ya terminada, sin la animación.
      // Sin movimiento (o sin el efecto), al principio de la portada, que ya se ve completa.
      function irAPortada(hash) {
        var s = document.getElementById("zoom-" + hash.replace(/^#sala-/, ""));
        if (!s) return false;
        var z = zooms.filter(function (x) { return x.seccion === s; })[0];
        if (activo() && z) { saltar(inicioSeccion(z) + recorrido(z)); pintar(); }
        else s.scrollIntoView();
        return true;
      }
      document.querySelectorAll('.salas-nav a[href^="#sala-"]').forEach(function (a) {
        a.addEventListener("click", function (e) {
          if (e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
          if (irAPortada(a.hash)) { e.preventDefault(); history.replaceState(null, "", a.hash); }
        });
      });
      function revisarAncla() { if (/^#sala-/.test(location.hash)) irAPortada(location.hash); }
      addEventListener("hashchange", revisarAncla);
      // el navegador vuelve a bajar al ancla al terminar de cargar: se corrige en ese mismo scroll y otra vez un momento después
      addEventListener("load", function () {
        addEventListener("scroll", revisarAncla, { once: true });
        setTimeout(function () { removeEventListener("scroll", revisarAncla); revisarAncla(); raiz.style.scrollBehavior = ""; }, 60);
      });
      if (activo()) rehacer();
      addEventListener("scroll", pedir, { passive: true });
      if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () { if (activo()) rehacer(); });
    })();
  </script>
'''


def seccion(numero, sala, slug, foto, foco):
    p = g['piezas'][slug]
    assert foto in p['fotos'], (slug, foto)
    t_ = tam[foto]
    anchos = t_['tamanos']
    srcset = ', '.join(f'img/galeria/{foto}-{w}.webp {w}w' for w in anchos)
    e = html.escape
    # la portada es solo visual (repite el título de la sala, que los lectores de pantalla encuentran en la sala)
    return f'''    <section class="zoom" id="zoom-{sala['id']}" aria-hidden="true">
      <div class="zoom-escena">
        <div class="zoom-caja">
          <figure class="zoom-foto">
            <picture>
              <source type="image/webp" srcset="{srcset}" sizes="(min-aspect-ratio: 1/1) 45vw, 100vw">
              <img src="img/galeria/{foto}.jpg" width="{t_['w']}" height="{t_['h']}" loading="lazy" decoding="async" style="--foco: {foco}%" alt="">
            </picture>
          </figure>
        </div>
        <div class="zoom-texto">
          <span class="sala-numero">Sala {numero}</span>
          <p class="zoom-nombre">{e(sala['titulo'])}</p>
          <p class="sala-sub">{e(sala.get('subtitulo') or '')}</p>
        </div>
        <p class="zoom-pista">Desliza</p>
      </div>
    </section>
'''


for viejo, nuevo in [
    ('  <link rel="stylesheet" href="css/galeria.css">\n', '  <link rel="stylesheet" href="css/galeria.css">\n' + CABEZA),
    ('  <script src="js/sitio.js" defer></script>\n', '  <script src="js/sitio.js" defer></script>\n' + SCRIPT),
]:
    assert t.count(viejo) == 1, viejo[:60]
    t = t.replace(viejo, nuevo)
for n, sala in enumerate(g['salas'], 1):
    marca = f'    <section class="sala" id="sala-{sala["id"]}"'
    assert t.count(marca) == 1, marca
    slug, foto, foco = APERTURAS[sala['id']]
    t = t.replace(marca, seccion(n, sala, slug, foto, foco) + marca)
    i = t.index(marca)
    viejo = '        <div class="sala-encabezado">\n          <div>\n'
    j = t.index(viejo, i)
    assert j - i < 400, sala['id']
    t = t[:j] + '        <div class="sala-encabezado">\n          <div class="visualmente-oculto">\n' + t[j + len(viejo):]

# La copia vive en pruebas/: las rutas relativas al sitio llevan ../ (la galería misma se queda en pruebas/galeria.html)
RUTA = re.compile(r'^(img|css|js|fuentes)/|^index\.html')
def subir(valor):
    return ','.join(re.sub(r'^(\s*)(\S+)', lambda m: m.group(1) + ('../' + m.group(2) if RUTA.match(m.group(2)) else m.group(2)), parte)
                    for parte in valor.split(','))
t = re.sub(r'(\s(?:href|src|srcset|data-grande)=")([^"]*)(")', lambda m: m.group(1) + subir(m.group(2)) + m.group(3), t)
t = re.sub(r'(&quot;[a-z]+&quot;: &quot;)(img/)', r'\1../\2', t)

# aviso de página de prueba y noindex
for viejo, nuevo in [
    ('  <meta name="viewport" content="width=device-width, initial-scale=1">\n',
     '  <meta name="viewport" content="width=device-width, initial-scale=1">\n'
     '  <!-- Página de prueba (herramientas/armar_prueba_galeria.py): no está enlazada desde el sitio ni se publica en Netlify -->\n'
     '  <meta name="robots" content="noindex, nofollow">\n'),
    ('<body class="pagina-galeria">\n',
     '<body class="pagina-galeria">\n'
     '  <p class="aviso-prueba" style="margin:0;padding:0.5rem var(--margen);background:var(--cempasuchil);color:var(--tinta);'
     'font-size:0.9rem;text-align:center">Página de prueba: la galería con una portada que se acerca al abrir cada sala. '
     '<a href="../galeria.html" style="color:var(--tinta)">Ver la galería de verdad</a></p>\n'),
]:
    assert t.count(viejo) == 1, viejo[:60]
    t = t.replace(viejo, nuevo)

sobran = re.findall(r'(?:href|src|srcset|data-grande)="(?:img|css|js|fuentes)/', t) + re.findall(r'&quot;: &quot;img/', t)
assert not sobran, sobran[:3]
(R / 'pruebas/galeria.html').write_text(t, encoding='utf-8')
print('ok pruebas/galeria.html', len(t), '·', len(APERTURAS), 'salas')
for n, sala in enumerate(g['salas'], 1):
    slug, foto, _ = APERTURAS[sala['id']]
    print(f"  Sala {n} {sala['titulo']} · {sala.get('subtitulo')}: abre con {g['piezas'][slug]['nombre']} ({foto})")
