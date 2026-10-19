# Gorgonio Candelario Castro · Maestro mascarero

Sitio web del maestro Gorgonio Candelario Castro, mascarero de Suchitlán, Comala, Colima.

Es un sitio estático: HTML, CSS y un poco de JavaScript, sin dependencias ni proceso de compilación. Se puede publicar tal cual en GitHub Pages, Netlify o cualquier hosting.

## Estructura

| Carpeta / archivo | Contenido |
|---|---|
| `index.html` | La página completa |
| `css/estilos.css` | Estilos (colores, tipografía y diseño adaptable a celular) |
| `js/sitio.js` | Menú del celular, filtros de la galería, visor de fotos y videos que se cargan al tocarlos |
| `img/mascaras/` | Fotos optimizadas para web (WebP y JPG en varios tamaños) |
| `img/icono.svg` | Icono del sitio |
| `fuentes/` | Tipografías Fraunces y Source Sans 3 (licencia SIL OFL) |
| `fotos/originales/` | Fotos originales tal como llegaron |
| `datos/mascaras.json` | Catálogo de las fotos: título, descripción, texto alternativo, pie y sección de cada máscara |
| `datos/curaduria.json` | Recomendaciones de la curaduría: fotos que faltan y fotos que conviene repetir |
| `herramientas/` | Scripts para optimizar fotos y regenerar la galería |
| `investigacion/` | Investigación con fuentes sobre el maestro, su familia y la Danza de los Morenos |

## Ver el sitio en tu computadora

```bash
python3 -m http.server 8000
# abrir http://localhost:8000
```

## Agregar o cambiar fotos

1. Copia la foto nueva a `fotos/originales/`.
2. Genera las versiones web (necesita Python con Pillow: `pip install pillow`):
   ```bash
   python3 herramientas/optimizar.py fotos/originales img/mascaras
   ```
   El script imprime el ancho, el alto y los tamaños de cada foto.
3. Agrega la foto a `datos/mascaras.json`, dentro de `fotos` y de una de las `secciones`. Copia el formato de las demás.
4. Regenera la portada, la galería y la imagen de la danza dentro de `index.html`:
   ```bash
   python3 herramientas/generar_galeria.py .
   ```
   El script solo reemplaza lo que está entre los comentarios `<!-- PORTADA -->`, `<!-- MÁSCARAS -->` e `<!-- IMAGEN-DANZA -->`. El resto de la página se edita a mano.

## Publicar en GitHub Pages

En GitHub, entra a **Settings → Pages**, elige **Deploy from a branch** y selecciona la rama y la carpeta `/ (root)`. Cuando ya haya dominio, agrega `og:url` y `og:image` en `index.html`; está marcado con un comentario `PENDIENTE`.

## Pendiente antes de publicar

Hay que confirmarlo con don Gorgonio o con su familia. En `index.html` están marcados con comentarios `PENDIENTE`.

- [ ] Teléfono o WhatsApp actual del taller. El que aparece (312 100 6716) es el que publicó AmoMéxico y podría estar desactualizado.
- [ ] Permiso para usar los dos videos de YouTube.
- [ ] El nombre de los personajes que no están seguros: el ave de cresta roja (¿gallo?), el animal de cuernos largos (¿chivo?), el perro o coyote, y los personajes de rostro humano (las tres caras negras, el hombre barbado, el rostro con alas, el rostro coronado con media luna).
- [ ] Si las máscaras de dos o tres rostros y las de vida y muerte son "máscaras del Tiempo".
- [ ] Año de nacimiento, a qué edad empezó, si es la tercera o la cuarta generación, qué premio nacional recibió y qué significa "Mi Güelo Baci".
- [ ] Fotos que faltan: un retrato del maestro, el taller, el proceso de trabajo y la danza. La lista completa está en `datos/curaduria.json`.
- [ ] Mejores versiones de las fotos. Las actuales llegaron por WhatsApp y están comprimidas; conviene pedir los originales del teléfono.
