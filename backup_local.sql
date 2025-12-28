--
-- PostgreSQL database dump
--

\restrict xMyl68khiv2aYrx3KsADVMLJxL6erYeS7rRA2rTfYQrYdA27v3cZLk1YT48gGLU

-- Dumped from database version 16.11
-- Dumped by pg_dump version 16.11

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: animalstatus; Type: TYPE; Schema: public; Owner: pethope
--

CREATE TYPE public.animalstatus AS ENUM (
    'available',
    'in_process',
    'adopted'
);


ALTER TYPE public.animalstatus OWNER TO pethope;

--
-- Name: gender; Type: TYPE; Schema: public; Owner: pethope
--

CREATE TYPE public.gender AS ENUM (
    'male',
    'female',
    'unknown'
);


ALTER TYPE public.gender OWNER TO pethope;

--
-- Name: size; Type: TYPE; Schema: public; Owner: pethope
--

CREATE TYPE public.size AS ENUM (
    'small',
    'medium',
    'large'
);


ALTER TYPE public.size OWNER TO pethope;

--
-- Name: species; Type: TYPE; Schema: public; Owner: pethope
--

CREATE TYPE public.species AS ENUM (
    'dog',
    'cat',
    'bird',
    'rodent',
    'other'
);


ALTER TYPE public.species OWNER TO pethope;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: pethope
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO pethope;

--
-- Name: animals; Type: TABLE; Schema: public; Owner: pethope
--

CREATE TABLE public.animals (
    id uuid NOT NULL,
    name character varying(100) NOT NULL,
    species public.species NOT NULL,
    breed character varying(100),
    age_months integer,
    size public.size NOT NULL,
    gender public.gender NOT NULL,
    description text NOT NULL,
    status public.animalstatus DEFAULT 'available'::public.animalstatus NOT NULL,
    traits json DEFAULT '[]'::json NOT NULL,
    special_needs text,
    location character varying(100) NOT NULL,
    contact_info json NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    edit_key_hash character varying(255)
);


ALTER TABLE public.animals OWNER TO pethope;

--
-- Name: images; Type: TABLE; Schema: public; Owner: pethope
--

CREATE TABLE public.images (
    id uuid NOT NULL,
    animal_id uuid NOT NULL,
    original_url character varying(500) NOT NULL,
    thumbnail_url character varying(500) NOT NULL,
    is_primary boolean DEFAULT false NOT NULL,
    "order" integer DEFAULT 0 NOT NULL
);


ALTER TABLE public.images OWNER TO pethope;

--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: pethope
--

COPY public.alembic_version (version_num) FROM stdin;
002
\.


--
-- Data for Name: animals; Type: TABLE DATA; Schema: public; Owner: pethope
--

COPY public.animals (id, name, species, breed, age_months, size, gender, description, status, traits, special_needs, location, contact_info, created_at, updated_at, edit_key_hash) FROM stdin;
0b80d29f-af4d-44c7-acec-bbcbc32c3bb9	Nêga	dog	SRD	\N	medium	female	Muito dócil e brincalhona.	available	[]	\N	Paulista	{"phone": "81992828262", "email": "etasso@gmail.com", "whatsapp": "81992828262"}	2025-12-24 10:26:14.046089+00	2025-12-28 12:35:55.918788+00	$2b$12$ieDD/RKyg.DZTZV39NdwGeywvYiasF7yECfS/CzScUhLeFVu1h2sS
0a758edc-58e6-4110-be13-f82405b7e5ec	Faísca	dog	srd	2	medium	unknown	Buscando um lar...	available	["Vermifugado"]	\N	paulista	{"phone": "81992828262", "email": "etasso@gmail.com", "whatsapp": "81992828262"}	2025-12-24 10:33:30.709209+00	2025-12-28 13:10:12.246158+00	$2b$12$ieDD/RKyg.DZTZV39NdwGeywvYiasF7yECfS/CzScUhLeFVu1h2sS
e441a0b8-e6a4-4e37-88ff-a09ee7a87ece	Piolho	dog	SRD	2	medium	male	Buscando um lar...	available	["Vermifugado"]	\N	Paulista	{"phone": "81992828262", "email": "etasso@gmail.com", "whatsapp": "81992828262"}	2025-12-28 13:12:02.472707+00	2025-12-28 13:12:02.472707+00	$2b$12$QQbnKPOSW48UzEvX20DKTOrkd4JjRyNykkQSGsjnIlb2Wv5dHvNnq
e43e9f7c-6ffa-4042-9a7d-9c3fccfacda4	Clara	dog	SRD	\N	medium	female	Adulta, extremamente dócil e carente.	available	[]	\N	Paulista	{"phone": "81992828262", "email": "etasso@gmail.com", "whatsapp": "81992828262"}	2025-12-28 13:13:59.465389+00	2025-12-28 13:13:59.465389+00	$2b$12$u5PNM76YcD52mVSrdjB2tulpL2PCsclP1yfltH53sXvTdj3L43rHy
17814215-6c31-4c56-8466-a963f3a9e8ff	Loyd	dog	SRD	\N	medium	male	Um grande abestalhado.	available	["Castrado"]	\N	Paulista	{"phone": "81992828262", "email": "etasso@gmail.com", "whatsapp": "81992828262"}	2025-12-28 13:15:34.358262+00	2025-12-28 13:15:34.358262+00	$2b$12$AOQUsu0hrFessvVLzSWT1uAatK41Vxyi.x8AqfTeiobQdXbQOXtl6
9625a532-8690-4d1a-b8d3-c7f5eaa1d2bb	Debian	dog	SRD	\N	medium	male	Um bebê grande.	available	[]	\N	Paulista	{"phone": "81992828262", "email": "etasso@gmail.com", "whatsapp": "81992828262"}	2025-12-28 13:17:15.332821+00	2025-12-28 13:17:15.332821+00	$2b$12$MdfevYOKHfPH6cQqQnQ38O1NgRAWH2oF/zqAMrJVFTRO4/kBhSCgS
5250702c-fe45-4a23-b7cb-f6c86539da94	Júlia	dog	srd	2	medium	female	Busacando um lar...	available	["Vermifugado"]	\N	paulista	{"phone": "81992828262", "email": "etasso@gmail.com", "whatsapp": "81992828262"}	2025-12-24 10:27:38.738157+00	2025-12-28 13:20:32.44303+00	$2b$12$ieDD/RKyg.DZTZV39NdwGeywvYiasF7yECfS/CzScUhLeFVu1h2sS
\.


--
-- Data for Name: images; Type: TABLE DATA; Schema: public; Owner: pethope
--

COPY public.images (id, animal_id, original_url, thumbnail_url, is_primary, "order") FROM stdin;
09814d71-32cf-4fcf-99c7-8d3e5201b22e	0a758edc-58e6-4110-be13-f82405b7e5ec	https://02f6d2b8d3f3.ngrok-free.app/storage/originals/af808ea9-17f1-4e65-b7b9-845bac93f8a7.jpg	https://02f6d2b8d3f3.ngrok-free.app/storage/thumbnails/af808ea9-17f1-4e65-b7b9-845bac93f8a7.jpg	t	0
de18fc56-74d1-48e1-9290-7e0c2f55fc66	0a758edc-58e6-4110-be13-f82405b7e5ec	https://02f6d2b8d3f3.ngrok-free.app/storage/originals/e3ecbe19-bcbf-4506-89fa-a7478304cd01.jpg	https://02f6d2b8d3f3.ngrok-free.app/storage/thumbnails/e3ecbe19-bcbf-4506-89fa-a7478304cd01.jpg	f	0
3c0b043f-84a8-4d74-896e-bcf06f556127	5250702c-fe45-4a23-b7cb-f6c86539da94	https://02f6d2b8d3f3.ngrok-free.app/storage/originals/1b277f6a-5692-4bdf-a1c1-17127a754898.jpg	https://02f6d2b8d3f3.ngrok-free.app/storage/thumbnails/1b277f6a-5692-4bdf-a1c1-17127a754898.jpg	t	0
dd6302ee-7758-4e4f-abf6-484835aa2d2e	0b80d29f-af4d-44c7-acec-bbcbc32c3bb9	https://02f6d2b8d3f3.ngrok-free.app/storage/originals/6ebbd804-bb6d-4395-b354-a1973b34e70c.jpg	https://02f6d2b8d3f3.ngrok-free.app/storage/thumbnails/6ebbd804-bb6d-4395-b354-a1973b34e70c.jpg	t	0
ed6e1ed1-db2f-4027-af02-2fcdce1d0eda	e441a0b8-e6a4-4e37-88ff-a09ee7a87ece	https://02f6d2b8d3f3.ngrok-free.app/storage/originals/84fb471f-e6ca-4255-98ac-1dfd5f7d28d9.jpg	https://02f6d2b8d3f3.ngrok-free.app/storage/thumbnails/84fb471f-e6ca-4255-98ac-1dfd5f7d28d9.jpg	t	0
dce5a336-bf8e-48cd-85d1-806546e6ecde	e43e9f7c-6ffa-4042-9a7d-9c3fccfacda4	https://02f6d2b8d3f3.ngrok-free.app/storage/originals/17c8937a-fdee-423e-a91a-a36b61b283b1.jpg	https://02f6d2b8d3f3.ngrok-free.app/storage/thumbnails/17c8937a-fdee-423e-a91a-a36b61b283b1.jpg	t	0
3427746e-3a0d-46f5-9fde-7af6c93b4fbc	17814215-6c31-4c56-8466-a963f3a9e8ff	https://02f6d2b8d3f3.ngrok-free.app/storage/originals/9386e572-1d80-4699-a685-67c2750b0587.jpg	https://02f6d2b8d3f3.ngrok-free.app/storage/thumbnails/9386e572-1d80-4699-a685-67c2750b0587.jpg	t	0
750e2b1c-3e55-4acf-8347-abe765f2e388	9625a532-8690-4d1a-b8d3-c7f5eaa1d2bb	https://02f6d2b8d3f3.ngrok-free.app/storage/originals/6b7d5c00-d0ec-4c61-acbf-bb91da36d561.jpg	https://02f6d2b8d3f3.ngrok-free.app/storage/thumbnails/6b7d5c00-d0ec-4c61-acbf-bb91da36d561.jpg	t	0
\.


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: pethope
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: animals animals_pkey; Type: CONSTRAINT; Schema: public; Owner: pethope
--

ALTER TABLE ONLY public.animals
    ADD CONSTRAINT animals_pkey PRIMARY KEY (id);


--
-- Name: images images_pkey; Type: CONSTRAINT; Schema: public; Owner: pethope
--

ALTER TABLE ONLY public.images
    ADD CONSTRAINT images_pkey PRIMARY KEY (id);


--
-- Name: idx_animals_created_at; Type: INDEX; Schema: public; Owner: pethope
--

CREATE INDEX idx_animals_created_at ON public.animals USING btree (created_at);


--
-- Name: idx_images_animal_order; Type: INDEX; Schema: public; Owner: pethope
--

CREATE INDEX idx_images_animal_order ON public.images USING btree (animal_id, "order");


--
-- Name: ix_animals_location; Type: INDEX; Schema: public; Owner: pethope
--

CREATE INDEX ix_animals_location ON public.animals USING btree (location);


--
-- Name: ix_animals_name; Type: INDEX; Schema: public; Owner: pethope
--

CREATE INDEX ix_animals_name ON public.animals USING btree (name);


--
-- Name: ix_animals_size; Type: INDEX; Schema: public; Owner: pethope
--

CREATE INDEX ix_animals_size ON public.animals USING btree (size);


--
-- Name: ix_animals_species; Type: INDEX; Schema: public; Owner: pethope
--

CREATE INDEX ix_animals_species ON public.animals USING btree (species);


--
-- Name: ix_animals_status; Type: INDEX; Schema: public; Owner: pethope
--

CREATE INDEX ix_animals_status ON public.animals USING btree (status);


--
-- Name: ix_images_animal_id; Type: INDEX; Schema: public; Owner: pethope
--

CREATE INDEX ix_images_animal_id ON public.images USING btree (animal_id);


--
-- Name: ix_images_is_primary; Type: INDEX; Schema: public; Owner: pethope
--

CREATE INDEX ix_images_is_primary ON public.images USING btree (is_primary);


--
-- Name: images images_animal_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pethope
--

ALTER TABLE ONLY public.images
    ADD CONSTRAINT images_animal_id_fkey FOREIGN KEY (animal_id) REFERENCES public.animals(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict xMyl68khiv2aYrx3KsADVMLJxL6erYeS7rRA2rTfYQrYdA27v3cZLk1YT48gGLU

