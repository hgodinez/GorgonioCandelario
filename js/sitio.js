// Menú, filtros de la galería, visor de fotos, desfile, salas y videos bajo demanda.
(function () {
  "use strict";

  // Mientras el visor está abierto (y al cerrarse, cuando el foco vuelve a la pieza) el desfile no cambia
  var enVisor = false;

  // Menú en pantallas chicas
  var boton = document.querySelector(".menu-boton");
  var nav = document.getElementById("navegacion");
  if (boton && nav) {
    var cerrarMenu = function (devolverFoco) {
      nav.classList.remove("abierta");
      boton.setAttribute("aria-expanded", "false");
      if (devolverFoco) boton.focus();
    };
    boton.addEventListener("click", function () {
      var abierto = nav.classList.toggle("abierta");
      boton.setAttribute("aria-expanded", String(abierto));
    });
    nav.addEventListener("click", function (e) {
      if (e.target.closest("a")) cerrarMenu(false);
    });
    // Esc cierra el menú; también se cierra si el foco sale de él
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && nav.classList.contains("abierta")) cerrarMenu(true);
    });
    // Tocar o hacer clic fuera del menú lo cierra (también al empezar a deslizar la página)
    document.addEventListener("pointerdown", function (e) {
      if (nav.classList.contains("abierta") && !nav.contains(e.target) && !boton.contains(e.target)) cerrarMenu(false);
    });
    nav.addEventListener("focusout", function (e) {
      if (nav.classList.contains("abierta") && e.relatedTarget && !nav.contains(e.relatedTarget) && e.relatedTarget !== boton) {
        cerrarMenu(false);
      }
    });
  }

  // Filtros de la galería
  var filtros = document.querySelectorAll(".filtros button");
  var grupos = document.querySelectorAll(".grupo");
  filtros.forEach(function (b) {
    b.addEventListener("click", function () {
      var f = b.dataset.filtro;
      filtros.forEach(function (o) { o.setAttribute("aria-pressed", String(o === b)); });
      grupos.forEach(function (g) { g.hidden = f !== "todas" && g.id !== f; });
    });
  });

  // Visor de fotos
  var visor = document.getElementById("visor");
  if (visor && typeof visor.showModal === "function") {
    var img = document.createElement("img");
    img.alt = "";
    visor.querySelector(".visor-siguiente").before(img);
    var titulo = visor.querySelector(".visor-titulo");
    var texto = visor.querySelector(".visor-descripcion");
    var contador = visor.querySelector(".visor-contador");
    var enlaces = [];
    var actual = 0;
    var origen = null;

    // Fotos del mismo conjunto (las parejas de la danza) o de la galería, sin los grupos ocultos
    function visibles(conjunto) {
      var enlaces = conjunto ? conjunto.querySelectorAll("a[data-grande]") : document.querySelectorAll(".galeria a[data-grande]");
      return Array.prototype.filter.call(enlaces, function (a) {
        return !a.closest(".grupo[hidden]");
      });
    }

    // Lo que simboliza en la danza (data-significado), en su propio renglón
    var significado = document.createElement("p");
    significado.className = "visor-significado";
    significado.hidden = true;
    texto.after(significado);

    // Tira de vistas cuando una pieza tiene varias fotos (data-vistas: [{src, alt, mini}])
    var tira = document.createElement("div");
    tira.className = "visor-vistas";
    significado.after(tira);

    function mostrar(i) {
      actual = (i + enlaces.length) % enlaces.length;
      var a = enlaces[actual];
      var miniatura = a.querySelector("img");
      img.src = a.dataset.grande;
      img.alt = miniatura ? miniatura.alt : "";
      titulo.textContent = a.dataset.titulo || "";
      texto.textContent = a.dataset.descripcion || "";
      significado.textContent = a.dataset.significado || "";
      significado.hidden = !a.dataset.significado;
      contador.textContent = (actual + 1) + " de " + enlaces.length;
      tira.textContent = "";
      tira.parentNode.scrollTop = 0;
      var vistas = a.dataset.vistas ? JSON.parse(a.dataset.vistas) : [];
      if (vistas.length > 1) {
        vistas.forEach(function (v, n) {
          var b = document.createElement("button");
          b.type = "button";
          b.setAttribute("aria-label", "Vista " + (n + 1) + " de " + vistas.length);
          b.setAttribute("aria-pressed", String(v.src === a.dataset.grande));
          var m = document.createElement("img");
          m.src = v.mini;
          m.alt = "";
          b.appendChild(m);
          b.addEventListener("click", function () {
            img.src = v.src;
            img.alt = v.alt;
            tira.querySelectorAll("button").forEach(function (o) { o.setAttribute("aria-pressed", String(o === b)); });
          });
          tira.appendChild(b);
        });
      }
    }

    document.addEventListener("click", function (e) {
      var a = e.target.closest(".galeria a[data-grande], [data-conjunto] a[data-grande]");
      // La copia del desfile (solo imágenes, para el bucle) abre la misma máscara que su original
      var copia = !a && e.target.closest(".desfile-pista[aria-hidden] li");
      if (copia) a = document.querySelectorAll("#desfile [data-conjunto] a[data-grande]")[Array.prototype.indexOf.call(copia.parentNode.children, copia)];
      if (!a || e.metaKey || e.ctrlKey || e.shiftKey) return;
      e.preventDefault();
      enlaces = visibles(a.closest("[data-conjunto]"));
      origen = copia ? null : a;  // a la copia solo se llega con ratón o dedo: no hay foco que devolver
      mostrar(enlaces.indexOf(a));
      enVisor = true;
      visor.showModal();
    });

    visor.querySelector(".visor-cerrar").addEventListener("click", function () { visor.close(); });
    visor.querySelector(".visor-anterior").addEventListener("click", function () { mostrar(actual - 1); });
    visor.querySelector(".visor-siguiente").addEventListener("click", function () { mostrar(actual + 1); });
    visor.addEventListener("keydown", function (e) {
      if (e.key === "ArrowLeft") mostrar(actual - 1);
      if (e.key === "ArrowRight") mostrar(actual + 1);
    });
    visor.addEventListener("close", function () {
      img.removeAttribute("src");
      if (origen) origen.focus({ preventScroll: true });
      enVisor = false;
    });
    // Cerrar al tocar el fondo
    visor.addEventListener("click", function (e) {
      if (e.target === visor || e.target.classList.contains("visor-imagen")) visor.close();
    });

    // Deslizar con el dedo
    var inicioX = null;
    visor.addEventListener("touchstart", function (e) { inicioX = e.touches[0].clientX; }, { passive: true });
    visor.addEventListener("touchend", function (e) {
      if (inicioX === null) return;
      var dx = e.changedTouches[0].clientX - inicioX;
      if (Math.abs(dx) > 50) mostrar(actual + (dx < 0 ? 1 : -1));
      inicioX = null;
    });
  }

  // Desfile de máscaras: botón para pausarlo y, con el teclado, se detiene para mostrar la máscara enfocada
  var desfile = document.getElementById("desfile");
  var pausa = document.querySelector(".desfile-pausa");
  if (desfile && pausa) {
    // El desfile se mueve con una animación CSS: el navegador no nota cuándo entra cada máscara y las «lazy» se quedarían
    // sin cargar. Después de cargar la página se piden todas.
    addEventListener("load", function () { desfile.querySelectorAll('img[loading="lazy"]').forEach(function (i) { i.loading = "eager"; }); });
    pausa.addEventListener("click", function () {
      var pausado = desfile.classList.toggle("pausado");
      pausa.textContent = pausado ? "Reanudar el desfile" : "Pausar el desfile";
    });
    desfile.addEventListener("focusin", function (e) {
      if (enVisor || !e.target.matches(":focus-visible")) return;
      desfile.classList.add("detenido");
      e.target.scrollIntoView({ block: "nearest", inline: "center" });
    });
    desfile.addEventListener("focusout", function (e) {
      var destino = e.relatedTarget;
      if (destino && (desfile.contains(destino) || destino.closest("#visor"))) return;
      desfile.classList.remove("detenido");
      desfile.scrollLeft = 0;
    });
  }

  // Navegación entre salas: marca la sala que se está viendo
  var salasNav = document.querySelector(".salas-nav ul");
  // Hasta dónde llegan el encabezado y la barra de salas (una o dos filas, según el ancho y la letra): de ahí salen el
  // scroll-padding y, con «reducir movimiento», el alto de las portadas (--alto-barras en css/galeria.css)
  var barraSalas = document.querySelector(".salas-nav");
  if (barraSalas && "ResizeObserver" in window) new ResizeObserver(function () {
    var abajo = (parseFloat(getComputedStyle(barraSalas).top) || 0) + barraSalas.offsetHeight + 6;
    document.documentElement.style.setProperty("--alto-barras", abajo + "px");
  }).observe(barraSalas);
  if (salasNav && "IntersectionObserver" in window) {
    var porSala = {};
    salasNav.querySelectorAll("a").forEach(function (a) { porSala[a.hash.slice(1)] = a; });
    var quieto = window.matchMedia("(prefers-reduced-motion: reduce)");
    // Cada sala cuenta desde su portada (.zoom): así la marca también sigue a los saltos de js/portadas.js
    var vigiladas = document.querySelectorAll(".zoom[id], .sala[id]");
    var primeraSala = vigiladas[0];
    var observador = new IntersectionObserver(function (entradas) {
      // Al volver arriba de la primera sala ninguna queda marcada. Se mira dónde está en cada aviso, porque un salto
      // directo hasta arriba no avisa por ella (pasa de «debajo» a «debajo» sin cruzar la franja)
      var raiz = entradas[0].rootBounds;
      if (raiz && primeraSala.getBoundingClientRect().top >= raiz.bottom) {
        if (salasNav.querySelector("a[aria-current]")) {
          salasNav.querySelectorAll("a[aria-current]").forEach(function (o) { o.removeAttribute("aria-current"); });
          salasNav.scrollTo({ left: 0 });
        }
        return;
      }
      entradas.forEach(function (en) {
        var a = porSala[en.target.id.replace(/^zoom-/, "sala-")];
        if (!en.isIntersecting || !a || a.hasAttribute("aria-current")) return;
        salasNav.querySelectorAll("a[aria-current]").forEach(function (o) { o.removeAttribute("aria-current"); });
        a.setAttribute("aria-current", "location");
        var ru = salasNav.getBoundingClientRect(), ra = a.getBoundingClientRect();
        salasNav.scrollBy({ left: ra.left + ra.width / 2 - (ru.left + ru.width / 2), behavior: quieto.matches ? "auto" : "smooth" });
      });
    }, { rootMargin: "-35% 0px -60% 0px" });
    vigiladas.forEach(function (s) { observador.observe(s); });
    // La entrada y el desfile también avisan: así un salto desde el pie de página hasta arriba quita la marca
    document.querySelectorAll(".galeria-entrada, .desfile").forEach(function (s) { observador.observe(s); });
  }
  // Con teclado, la sala enfocada se trae al centro de la barra si queda cortada o bajo el desvanecido de la derecha
  if (salasNav) salasNav.addEventListener("focusin", function (e) {
    if (!e.target.matches(":focus-visible")) return;
    var ru = salasNav.getBoundingClientRect(), ra = e.target.getBoundingClientRect();
    if (ra.left - 8 >= ru.left && ra.right + 8 <= ru.right - 48) return;
    salasNav.scrollBy({ left: ra.left + ra.width / 2 - (ru.left + ru.width / 2) });
  });

  // Videos: la portada se pide a YouTube cuando el video se acerca a la pantalla; el reproductor, solo con el clic
  var ponerPortada = function (b) { b.style.backgroundImage = "url(https://i.ytimg.com/vi/" + b.dataset.video + "/hqdefault.jpg)"; };
  var ioVideos = "IntersectionObserver" in window && new IntersectionObserver(function (es) {
    es.forEach(function (en) { if (en.isIntersecting) { ponerPortada(en.target); ioVideos.unobserve(en.target); } });
  }, { rootMargin: "1000px 0px" });
  document.querySelectorAll(".video-portada").forEach(function (b) {
    if (ioVideos) ioVideos.observe(b); else ponerPortada(b);
    b.addEventListener("click", function () {
      var f = document.createElement("iframe");
      f.src = "https://www.youtube-nocookie.com/embed/" + b.dataset.video + "?autoplay=1&rel=0";
      f.title = b.getAttribute("aria-label").replace(/^Reproducir video:\s*/, "Video: ");
      f.allow = "accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture";
      f.allowFullscreen = true;
      b.replaceWith(f);
      f.focus();
    });
  });
})();
