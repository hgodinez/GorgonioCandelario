-- Base de datos de la encuesta para don Gorgonio, en Supabase.
-- Cómo usarlo: en el proyecto de Supabase, abre «SQL Editor», pega todo este archivo, cambia
-- CAMBIA-ESTA-CLAVE (aparece 1 vez, en el bloque do $$ de abajo) por la clave secreta del enlace de la
-- encuesta (la misma que va en ...?clave=XXXX) y toca «Run». Cambia la clave solo en el SQL Editor: no la
-- guardes en este archivo, que está en un repositorio público.
-- La clave: de 16 a 100 letras sin acento, números, - o _. Para sacar una:
--   python3 -c "import secrets; print('gc-' + secrets.token_hex(12))"
-- Se puede volver a correr completo sin perder respuestas.
--
-- Qué hace:
--   * Una tabla «respuestas» donde la página SOLO puede agregar renglones, y solo si trae la clave.
--     Nadie puede leer, cambiar ni borrar renglones desde la página: se leen en el panel de Supabase.
--   * Un depósito privado «audios» donde la página SOLO puede subir audios dentro de la carpeta
--     que se llama como la clave. Los audios se escuchan o descargan desde el panel.
--   * Una vista «ultimas_respuestas» con la respuesta más reciente de cada pregunta en cada teléfono, para
--     leerla en el panel (Table Editor o SQL Editor). La vista no queda abierta a la página.

create table if not exists public.respuestas (
  id uuid primary key default gen_random_uuid(),
  creado timestamptz not null default now(),
  clave text not null check (length(clave) between 8 and 100),
  dispositivo text check (dispositivo is null or length(dispositivo) <= 100),
  tipo text not null check (tipo in ('mascara', 'general', 'audio')),
  pregunta text not null check (length(pregunta) <= 300),
  numero int,
  nombre text check (nombre is null or length(nombre) <= 1000),
  respuesta jsonb not null check (pg_column_size(respuesta) < 200000)
);
-- Si la tabla ya existía con límites más chicos, se ponen los de arriba
alter table public.respuestas
  drop constraint if exists respuestas_pregunta_check,
  add constraint respuestas_pregunta_check check (length(pregunta) <= 300),
  drop constraint if exists respuestas_nombre_check,
  add constraint respuestas_nombre_check check (nombre is null or length(nombre) <= 1000),
  drop constraint if exists respuestas_respuesta_check,
  add constraint respuestas_respuesta_check check (pg_column_size(respuesta) < 200000);

alter table public.respuestas enable row level security;

-- La página (rol anon) solo puede agregar renglones, y solo en las columnas que manda: el id y la hora
-- (creado) los pone siempre la base
revoke all on public.respuestas from anon, authenticated;
grant insert (clave, dispositivo, tipo, pregunta, numero, nombre, respuesta) on public.respuestas to anon;

-- La respuesta más reciente de cada pregunta en cada teléfono (para leer en el panel; no se abre a la página)
create or replace view public.ultimas_respuestas with (security_invoker = true) as
  select distinct on (dispositivo, tipo, pregunta) creado, tipo, numero, nombre, pregunta, respuesta, dispositivo
  from public.respuestas
  where tipo <> 'audio'
  order by dispositivo, tipo, pregunta, creado desc;
revoke all on public.ultimas_respuestas from anon, authenticated;

-- Depósito privado para los audios (hasta 25 MB cada uno)
insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values ('audios', 'audios', false, 26214400,
        array['audio/webm', 'audio/mp4', 'audio/ogg', 'audio/mpeg', 'audio/aac', 'audio/wav', 'audio/x-m4a'])
on conflict (id) do update set public = false, file_size_limit = excluded.file_size_limit,
  allowed_mime_types = excluded.allowed_mime_types;

-- Los permisos con la clave: se escribe UNA vez aquí y se revisa antes de usarla
do $$
declare k text := 'CAMBIA-ESTA-CLAVE';
begin
  if k like 'CAMBIA%' or k !~ '^[A-Za-z0-9_-]{16,100}$' then
    raise exception 'Falta poner la clave secreta: de 16 a 100 letras sin acento, números, - o _';
  end if;
  execute 'drop policy if exists "la encuesta agrega respuestas con su clave" on public.respuestas';
  execute format('create policy "la encuesta agrega respuestas con su clave" on public.respuestas for insert to anon with check (clave = %L)', k);
  execute 'drop policy if exists "la encuesta sube audios con su clave" on storage.objects';
  execute format('create policy "la encuesta sube audios con su clave" on storage.objects for insert to anon with check (bucket_id = %L and (storage.foldername(name))[1] = %L)', 'audios', k);
end $$;

-- Para leer las respuestas en el SQL Editor:
--   select dispositivo, numero, nombre, respuesta, creado from public.ultimas_respuestas order by dispositivo, tipo, numero;
-- Los audios están en Storage → audios → (carpeta con la clave): toca el archivo para oírlo o descargarlo.
--
-- Después de probar el enlace tú mismo, y ANTES de mandárselo, borra tus pruebas:
--   truncate public.respuestas;
-- y borra tus audios de prueba en el panel (Storage → audios → carpeta de la clave), no con SQL.
--
-- Cuando termine la encuesta (o si el enlace se filtra), cierra las escrituras:
--   drop policy if exists "la encuesta agrega respuestas con su clave" on public.respuestas;
--   drop policy if exists "la encuesta sube audios con su clave" on storage.objects;
-- Si se filtró, vuelve a correr el bloque do $$ con una clave nueva y manda el enlace nuevo (la clave del
-- enlace reemplaza a la que quedó guardada en el teléfono).
-- La página no usa cuentas de usuario: conviene apagar «Allow new users to sign up» en Authentication.
