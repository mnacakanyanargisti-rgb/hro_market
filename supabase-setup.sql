-- Run in Supabase SQL editor after creating the owner in Authentication.
-- Replace the UUID below with the owner's actual user UUID before running.
create table public.store_owner (id uuid primary key references auth.users(id));
insert into public.store_owner values ('REPLACE_WITH_OWNER_UUID');
alter table public.store_owner enable row level security;
create policy "Owner reads own membership" on public.store_owner for select to authenticated using (id=auth.uid());
create table public.catalog (id int primary key check(id=1), products jsonb not null check(jsonb_typeof(products)='array'));
alter table public.catalog enable row level security;
create policy "Public catalog read" on public.catalog for select to anon,authenticated using (true);
create policy "Owner catalog insert" on public.catalog for insert to authenticated with check (exists(select 1 from public.store_owner where id=auth.uid()));
create policy "Owner catalog update" on public.catalog for update to authenticated using (exists(select 1 from public.store_owner where id=auth.uid())) with check (exists(select 1 from public.store_owner where id=auth.uid()));
insert into storage.buckets(id,name,public,file_size_limit,allowed_mime_types) values ('product-photos','product-photos',true,5242880,array['image/jpeg','image/png','image/webp']);
create policy "Owner uploads photos" on storage.objects for insert to authenticated with check(bucket_id='product-photos' and exists(select 1 from public.store_owner where id=auth.uid()));
