// Menú, filtros de la galería, visor de fotos y videos bajo demanda.
(function () {
  "use strict";

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

    function mostrar(i) {
      actual = (i + enlaces.length) % enlaces.length;
      var a = enlaces[actual];
      var miniatura = a.querySelector("img");
      img.src = a.dataset.grande;
      img.alt = miniatura ? miniatura.alt : "";
      titulo.textContent = a.dataset.titulo || "";
      texto.textContent = a.dataset.descripcion || "";
      contador.textContent = (actual + 1) + " de " + enlaces.length;
    }

    document.addEventListener("click", function (e) {
      var a = e.target.closest(".galeria a[data-grande], [data-conjunto] a[data-grande]");
      if (!a || e.metaKey || e.ctrlKey || e.shiftKey) return;
      e.preventDefault();
      enlaces = visibles(a.closest("[data-conjunto]"));
      origen = a;
      mostrar(enlaces.indexOf(a));
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
      if (origen) origen.focus();
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

  // Videos: se carga YouTube solo cuando la persona hace clic
  document.querySelectorAll(".video-portada").forEach(function (b) {
    b.style.backgroundImage = "url(https://i.ytimg.com/vi/" + b.dataset.video + "/hqdefault.jpg)";
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
