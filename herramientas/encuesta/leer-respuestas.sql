-- Para leer las respuestas de la encuesta en Supabase (SQL Editor → pega una consulta → Run).
-- Cada vez que don Gorgonio cambia algo, la página agrega un renglón nuevo con la respuesta completa de esa
-- pregunta; los renglones viejos quedan como historial. La buena es siempre la más reciente: la vista
-- ultimas_respuestas deja solo esa (una por pregunta y por teléfono).

-- 1) Las máscaras, una por renglón y en orden, con cada respuesta en su columna
select numero, nombre,
  case respuesta->>'es'
    when 'si' then 'sí, está bien'
    when 'otra' then 'es otra cosa: ' || coalesce(nullif(respuesta->>'que_es', ''), '(no dijo qué)')
    when 'nose' then 'no sabe'
    else coalesce(respuesta->>'es', '') end as nombre_esta_bien,
  (select string_agg(u, ', ') from jsonb_array_elements_text(respuesta->'uso') as u) as danza_o_fiesta,
  nullif(respuesta->>'uso_otro', '') as cual_otra,
  case respuesta->>'sexo' when 'macho' then 'macho' when 'hembra' then 'hembra' when 'nose' then 'no sabe' end as macho_o_hembra,
  nullif(respuesta->>'significado', '') as significado,
  case respuesta->>'suya' when 'si' then 'sí' when 'no' then 'no, otra persona' when 'nose' then 'no sabe' end as la_hizo_el,
  creado
from public.ultimas_respuestas
where tipo = 'mascara'
order by numero;

-- 2) Las preguntas sobre él y su taller
select numero, nombre as pregunta, nullif(respuesta->>'opcion', '') as opcion, nullif(respuesta->>'texto', '') as texto, creado
from public.ultimas_respuestas
where tipo = 'general'
order by numero;

-- 3) Los audios que grabó: el archivo está en Storage → audios (tócalo ahí para oírlo)
select numero, nombre, pregunta as archivo, (respuesta->>'segundos')::int as segundos, creado
from public.respuestas
where tipo = 'audio'
order by numero, creado;

-- 4) El historial de una máscara (todas sus versiones, la más nueva arriba); cambia el número
select creado, respuesta from public.respuestas where tipo = 'mascara' and numero = 1 order by creado desc;
