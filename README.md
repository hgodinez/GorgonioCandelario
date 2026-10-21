# Gorgonio Candelario Castro · Maestro mascarero

Sitio web del maestro Gorgonio Candelario Castro, mascarero de Suchitlán, Comala, Colima.

Es un sitio estático: HTML, CSS y un poco de JavaScript, sin dependencias ni proceso de compilación. Se puede publicar tal cual en GitHub Pages, Netlify o cualquier hosting.

## Estructura

| Carpeta / archivo | Contenido |
|---|---|
| `index.html` | La página principal: el maestro, la danza, la técnica, una muestra de la galería, reconocimientos, videos y el taller |
| `galeria.html` | La galería completa: 122 piezas en 11 salas, con el desfile de máscaras recortadas |
| `css/estilos.css` | Estilos (colores, tipografía y diseño adaptable a celular) |
| `css/galeria.css` | Estilos de la galería (salas oscuras de museo, mosaico y desfile) |
| `js/sitio.js` | Menú del celular, visor de fotos con sus vistas, desfile, navegación entre salas y videos que se cargan al tocarlos |
| `img/mascaras/` | Fotos de la página principal optimizadas para web (WebP y JPG en varios tamaños) |
| `img/maestro/` | Fotos de don Gorgonio y de su padre, don Herminio, optimizadas para web |
| `img/galeria/` | Fotos del álbum optimizadas para la galería; en `recortes/`, las máscaras sin fondo del desfile |
| `img/icono.svg` | Icono del sitio |
| `fuentes/` | Tipografías Fraunces y Source Sans 3 (licencia SIL OFL) |
| `fotos/originales/` | Fotos originales tal como llegaron (las de la danza, en `fotos/originales/danza/`) |
| `fotos/album/` | Las 172 fotos del álbum de Google Fotos, tal como llegaron |
| `fotos/limpias/` | Fotos listas para optimizar: sin letreros sobrepuestos, un solo panel de los collages y sin las esquinas de color de los marcos ovalados |
| `datos/mascaras.json` | Catálogo de las fotos: título, descripción, texto alternativo, pie y sección de cada máscara |
| `datos/danza.json` | Las nueve parejas de la Danza de los Morenos, la foto de cada una y la caja de la máscara para su tarjeta |
| `datos/detalles.json` | Acercamientos de la sección de técnica (recorte, título y texto) |
| `datos/curaduria.json` | Recomendaciones de la curaduría: fotos que faltan y fotos que conviene repetir |
| `datos/album-catalogo.json` | Clasificación del álbum: qué pieza es cada foto, su certeza, fusiones, duplicados y salas |
| `datos/recortes-revision.json` | Revisión de los recortes sin fondo (cuáles se aprobaron para el desfile) |
| `datos/galeria.json` | Datos finales de la galería (salas, piezas, fotos, mosaico y desfile); lo escribe `armar_galeria.py` |
| `datos/album-indice.json`, `datos/album-tamanos.json` | Índice de las fotos del álbum y sus medidas web |
| `datos/preguntas-familia.md` | Preguntas pendientes para la familia, con los números de foto |
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
   El script imprime el ancho, el alto y los tamaños de cada foto. Para las fotos de la danza, usa `fotos/limpias` como origen. Si una foto trae texto encima, se puede borrar con `herramientas/quitar_texto.py`.
3. Agrega la foto a `datos/mascaras.json`, dentro de `fotos` y de una de las `secciones`. Copia el formato de las demás.
4. Si cambiaste los acercamientos de `datos/detalles.json`, regenéralos con `python3 herramientas/detalles.py .`
5. Regenera la portada, la galería, las parejas de la danza y los acercamientos dentro de `index.html`:
   ```bash
   python3 herramientas/generar_galeria.py .
   ```
   El script solo reemplaza lo que está entre los comentarios `<!-- PORTADA -->`, `<!-- MÁSCARAS -->`, `<!-- IMAGEN-DANZA -->`, `<!-- PAREJAS -->` y `<!-- DETALLES -->`. El resto de la página se edita a mano.

   Para ponerle foto a una pareja de la danza, agrega el nombre del archivo y la caja de la máscara en `datos/danza.json`, corre `python3 herramientas/tarjetas_danza.py .` y vuelve a correr el script.

   Las tarjetas de las parejas muestran la máscara completa. Salen de `herramientas/tarjetas_danza.py` (necesita Pillow y numpy), que encuadra cada foto en proporción 3:4 a partir de la caja de la máscara (`caja` en `datos/danza.json`: izquierda, arriba, derecha y abajo, en pixeles de la foto). Si la foto no alcanza, prolonga la pared con el color de su orilla. Si cambias el archivo de una pareja sin volver a hacer su tarjeta, `generar_galeria.py` te lo avisa; si solo cambias la caja o reemplazas la foto con el mismo nombre, vuelve a correr `tarjetas_danza.py`. La caja se puede medir a mano en cualquier editor de fotos o con el modelo de `recortar_fondo.py`.

## Regenerar la galería

La galería (`galeria.html` y la muestra de `index.html`) sale de las fotos del álbum. Si cambian las fotos, la clasificación o los nombres, corre en este orden (necesita Python con Pillow):

```bash
python3 herramientas/limpiar_album.py .        # versiones limpias en fotos/limpias
python3 herramientas/optimizar_album.py .      # versiones web en img/galeria
python3 herramientas/armar_galeria.py          # escribe datos/galeria.json
python3 herramientas/generar_galeria_completa.py .
```

- Para cambiar el nombre, la descripción o la sala de una pieza, edita las tablas al principio de `armar_galeria.py` (`NOMBRES`, `DESCRIPCIONES`, `SALAS`, `APARTADAS`, etc.) y vuelve a correr los dos últimos pasos.
- Cuando la familia conteste las preguntas de `datos/preguntas-familia.md`, marca las piezas confirmadas en `datos/album-catalogo.json` con `"certeza": "confirmada-familia"`; en la galería aparecen con la leyenda «Confirmada por la familia».
- Las máscaras del desfile van sin fondo. Para agregar una, quita el fondo con `recortar_fondo.py` (necesita onnxruntime, numpy y el modelo isnet-general-use; el enlace está en el script), revisa el recorte, pásalo a tamaños web con `recortes_web.py` y márcalo en `datos/recortes-revision.json` con `"usar_recorte": true`.

## La encuesta para don Gorgonio

`preguntas/index.html` es una página escondida del sitio: no está en el menú y los buscadores no la indexan. Le enseña sus máscaras una por una (qué es, en qué danza o fiesta se usa y qué significa), más unas preguntas sobre él y el taller. Habla en primera persona, de parte de Humberto.

- **Con Supabase** (lo normal): cada respuesta y cada audio que graba en la página se guardan solos por internet. El enlace que se le manda lleva una clave secreta: `…/preguntas/?clave=XXXX`. Sin la clave, la página no puede guardar nada en la base de datos.
- **Sin Supabase o sin la clave**: lo que conteste se guarda en su teléfono y lo manda con el botón verde de WhatsApp.

Para preparar Supabase (una sola vez): en el proyecto, abre «SQL Editor», pega `herramientas/encuesta/supabase.sql`, cambia `CAMBIA-ESTA-CLAVE` (una sola vez, en el bloque `do $$`) por la clave y toca «Run». Cambia la clave solo en el SQL Editor, no en el archivo del repositorio. La clave lleva de 16 a 100 letras sin acento, números, `-` o `_`; para sacar una: `python3 -c "import secrets; print('gc-' + secrets.token_hex(12))"`. El script crea la tabla `respuestas` (la página solo puede agregar renglones, no leerlos), la vista `ultimas_respuestas` y el depósito privado `audios`. Se puede volver a correr sin perder respuestas.

- **Leer las respuestas**: en el panel de Supabase, Table Editor → `respuestas`, o en SQL Editor con `select dispositivo, numero, nombre, respuesta, creado from ultimas_respuestas order by dispositivo, tipo, numero;`. Los renglones `audio` solo dicen qué archivo se grabó.
- **Oír los audios**: Storage → `audios` → la carpeta con la clave → toca el archivo (se oye ahí mismo o se descarga).
- **Antes de mandarle el enlace**: pruébalo tú y luego borra tus pruebas con `truncate public.respuestas;` y tus audios de prueba en Storage.
- **El plan gratis pausa el proyecto tras una semana sin uso.** Antes de mandar el enlace, y cada pocos días mientras conteste, abre el panel de Supabase; si dice *Paused*, toca *Restore*. Mientras tanto la página no pierde nada: lo guarda en el teléfono y lo manda cuando vuelve a funcionar.
- **Al terminar la encuesta, o si el enlace se filtra**, cierra las escrituras con las dos líneas `drop policy …` del final de `supabase.sql`. Si se filtró, vuelve a correr el bloque `do $$` con una clave nueva y manda el enlace nuevo.

Para volver a armar la página (por ejemplo, si cambian las máscaras):

```bash
python3 herramientas/encuesta/generar_encuesta.py . /tmp/encuesta modo=sitio firma=Humberto nombre=Humberto \
  supabase_url=https://xbmlsctofrofspjoyxyw.supabase.co supabase_key=<clave pública sb_publishable_…> \
  enlace=https://humbertogodinez.com/GorgonioCandelario/preguntas/ destino=16466454572
```

La clave pública (`sb_publishable_…`) puede ir en la página; la secreta (`sb_secret_…` o `service_role`) nunca. El mismo script, sin `modo=sitio`, arma la versión para claude.ai.

## Publicar en GitHub Pages

En GitHub, entra a **Settings → Pages**, elige **Deploy from a branch** y selecciona la rama y la carpeta `/ (root)`. Cuando ya haya dominio, agrega `og:url` y `og:image` en `index.html`; está marcado con un comentario `PENDIENTE`.

## Pendiente antes de publicar

Hay que confirmarlo con don Gorgonio o con su familia. En `index.html` están marcados con comentarios `PENDIENTE`.

- [ ] Permiso para usar los dos videos de YouTube.
- [ ] Que la novena pareja de la danza son los perros. Lo dicen el libro del INPI y la ficha de patrimonio, pero falta que lo confirme la familia.
- [ ] Qué simbolizan el burro, la guacamaya, el gallo y el perro; quién es el danzante 19 que cuenta el INPI, y si el bartolo sale con los Morenos.
- [ ] La técnica propia de don Gorgonio. Lo que hay publicado es casi todo del taller de su hermano: la madera que usa, el corte y el secado, el angaro, el tipo de pintura y la fibra.
- [ ] El nombre de los personajes de rostro humano: las tres máscaras negras, el hombre barbado, el rostro con alas y el rostro negro de cresta roja (¿diablo?). También si las máscaras de vida y muerte tienen nombre.
- [ ] Fotos de las parejas que faltan: los perros y el ocelote (las dos máscaras de felino que hay son linces).
- [ ] Que don Gorgonio conteste la encuesta en `preguntas/` (ver «La encuesta para don Gorgonio»). Las mismas preguntas, con los mismos números, están en `datos/preguntas-para-don-gorgonio.md`. La encuesta se arma con `herramientas/encuesta/generar_encuesta.py`.
- [ ] Si son de don Gorgonio las piezas en tonos pastel (un felino y dos toros) y el ave azul de pico amarillo. Por ahora están fuera de la galería (`APARTADAS` en `armar_galeria.py`).
- [ ] El dominio del sitio. Cuando esté, agrega `og:url` y `og:image` en `index.html` y `galeria.html`.
- [ ] Año de nacimiento, a qué edad empezó, si es la tercera o la cuarta generación, qué premio nacional recibió y qué significa "Mi Güelo Baci".
- [ ] Fotos que faltan: el taller, más del proceso de trabajo y la danza. La lista completa está en `datos/curaduria.json`. Ya hay tres fotos de don Gorgonio y una de su padre, don Herminio, en `fotos/originales/maestro/`.
- [ ] Quién tomó las fotos de don Gorgonio y de don Herminio, y si se pueden usar. El retrato frente a la pared azul parece de un fotógrafo profesional, y la foto en la que pinta es un cuadro de un video.
- [ ] De dónde viene la transcripción del testimonio de don Gorgonio, para dar el crédito de sus citas (ver `investigacion/testimonio-don-gorgonio.md`).
- [ ] Mejores versiones de las fotos. Las actuales llegaron por WhatsApp y están comprimidas; conviene pedir los originales del teléfono.
