// Portadas de las salas de la galería: la foto de una máscara empieza como tarjeta y crece hasta su tamaño completo al
// hacer scroll; luego aparecen el número, el nombre y el subtítulo de la sala. Mientras una portada está fija se
// esconden el encabezado y la barra de salas, y la barra lleva a la portada ya terminada. Con «reducir movimiento»
// las portadas se ven completas y quietas (la clase zoom-activo la pone el script del <head> de galeria.html).
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
