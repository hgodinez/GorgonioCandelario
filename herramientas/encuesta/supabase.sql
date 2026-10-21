-- Base de datos de la encuesta para don Gorgonio, en Supabase.
-- Cómo usarlo: en el proyecto de Supabase, abre «SQL Editor», pega todo este archivo,
-- cambia CAMBIA-ESTA-CLAVE (aparece 2 veces) por la clave secreta del enlace de la encuesta
-- (la misma que va en ...?clave=XXXX) y toca «Run».
--
-- Qué hace:
--   * Una tabla «respuestas» donde la página SOLO puede agregar renglones, y solo si trae la clave.
--     Nadie puede leer, cambiar ni borrar renglones desde la página: se leen en el panel de Supabase.
--   * Un depósito privado «audios» donde la página SOLO puede subir audios dentro de la carpeta
--     que se llama como la clave. Los audios se escuchan o descargan desde el panel.
--   * Una vista «ultimas_respuestas» con la respuesta más reciente de cada pregunta, para leerla
--     en el panel (Table Editor o SQL Editor). La vista no queda abierta a la página.

create table if not exists public.respuestas (
  id uuid primary key default gen_random_uuid(),
  creado timestamptz not null default now(),
  clave text not null check (length(clave) between 8 and 100),
  dispositivo text check (dispositivo is null or length(dispositivo) <= 100),
  tipo text not null check (tipo in ('mascara', 'general', 'audio')),
  pregunta text not null check (length(pregunta) <= 200),
  numero int,
  nombre text check (nombre is null or length(nombre) <= 300),
  respuesta jsonb not null check (pg_column_size(respuesta) < 20000)
);

alter table public.respuestas enable row level security;

-- La página (rol anon) solo puede agregar renglones, y solo con la clave
revoke all on public.respuestas from anon, authenticated;
grant insert on public.respuestas to anon;
drop policy if exists "la encuesta agrega respuestas con su clave" on public.respuestas;
create policy "la encuesta agrega respuestas con su clave" on public.respuestas
  for insert to anon
  with check (clave = 'CAMBIA-ESTA-CLAVE');

-- La respuesta más reciente de cada pregunta (para leer en el panel; no se abre a la página)
create or replace view public.ultimas_respuestas with (security_invoker = true) as
  select distinct on (tipo, pregunta) creado, tipo, numero, nombre, pregunta, respuesta
  from public.respuestas
  where tipo <> 'audio'
  order by tipo, pregunta, creado desc;
revoke all on public.ultimas_respuestas from anon, authenticated;

-- Depósito privado para los audios (hasta 25 MB cada uno)
insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values ('audios', 'audios', false, 26214400,
        array['audio/webm', 'audio/mp4', 'audio/ogg', 'audio/mpeg', 'audio/aac', 'audio/wav', 'audio/x-m4a'])
on conflict (id) do update set public = false, file_size_limit = excluded.file_size_limit,
  allowed_mime_types = excluded.allowed_mime_types;

drop policy if exists "la encuesta sube audios con su clave" on storage.objects;
create policy "la encuesta sube audios con su clave" on storage.objects
  for insert to anon
  with check (bucket_id = 'audios' and (storage.foldername(name))[1] = 'CAMBIA-ESTA-CLAVE');

-- Para leer las respuestas en el SQL Editor:
--   select numero, nombre, respuesta, creado from public.ultimas_respuestas order by tipo, numero;
-- Los audios están en Storage → audios → (carpeta con la clave).
