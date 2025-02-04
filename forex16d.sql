--
-- PostgreSQL database dump
--

-- Dumped from database version 17.2 (Debian 17.2-1.pgdg120+1)
-- Dumped by pg_dump version 17.2 (Debian 17.2-1.pgdg120+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: roles; Type: TYPE; Schema: public; Owner: admin
--

CREATE TYPE public.roles AS ENUM (
    'admin',
    'user'
);


ALTER TYPE public.roles OWNER TO admin;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: models; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.models (
    model_id character varying NOT NULL,
    name character varying NOT NULL,
    price double precision NOT NULL,
    commission double precision NOT NULL,
    file_path character varying NOT NULL,
    created_at date NOT NULL,
    updated_at date NOT NULL
);


ALTER TABLE public.models OWNER TO admin;

--
-- Name: portfolios; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.portfolios (
    portfolio_id character varying(255) NOT NULL,
    user_id character varying(255) NOT NULL,
    model_id character varying(255),
    login integer NOT NULL,
    name character varying NOT NULL,
    connected boolean DEFAULT false NOT NULL,
    create_at date DEFAULT now() NOT NULL,
    token_id character varying
);


ALTER TABLE public.portfolios OWNER TO admin;

--
-- Name: tokens; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.tokens (
    token_id character varying NOT NULL,
    portfolio_id character varying NOT NULL,
    token character varying NOT NULL,
    created_at date NOT NULL,
    updated_at date,
    expiry_date date NOT NULL,
    revoked_at date
);


ALTER TABLE public.tokens OWNER TO admin;

--
-- Name: users; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.users (
    user_id character varying(255) NOT NULL,
    email character varying(255) NOT NULL,
    password character varying(255) NOT NULL,
    role public.roles DEFAULT 'user'::public.roles NOT NULL,
    create_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.users OWNER TO admin;

--
-- Data for Name: models; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.models (model_id, name, price, commission, file_path, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: portfolios; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.portfolios (portfolio_id, user_id, model_id, login, name, connected, create_at, token_id) FROM stdin;
1	39d7b66a-f020-4815-bf30-d575a5da7766	\N	5002	test	f	2025-02-02	\N
\.


--
-- Data for Name: tokens; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.tokens (token_id, portfolio_id, token, created_at, updated_at, expiry_date, revoked_at) FROM stdin;
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.users (user_id, email, password, role, create_at) FROM stdin;
1	admin@admin.com	password	admin	2025-01-25 02:57:07.257137+00
2	user1@user.com	password	user	2025-01-25 03:00:42.023021+00
3	user2@user.com	password	user	2025-01-25 03:00:52.768626+00
39d7b66a-f020-4815-bf30-d575a5da7766	test@test.com	$argon2id$v=19$m=65536,t=3,p=4$0THQSeMwwDrtnpMyPPBh3w$tNB3VSVbB9iTMEWCEcBX3qP4D0hoy7p00Qp8PsJOwzU	user	2025-01-31 14:56:54.892964+00
fd7cdc2f-2cb1-480d-aa40-e377ab9b9b74	nitid@nitid.com	$argon2id$v=19$m=65536,t=3,p=4$mSUtPkabtKL+XEbIDchQRA$1HdiErvxHMi8U5j08GW8fsJNN2dTy1JlFa0XD5Za9nU	user	2025-02-03 14:18:58.449644+00
\.


--
-- Name: models models_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.models
    ADD CONSTRAINT models_pkey PRIMARY KEY (model_id);


--
-- Name: portfolios portfolios_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.portfolios
    ADD CONSTRAINT portfolios_pkey PRIMARY KEY (portfolio_id);


--
-- Name: tokens tokens_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.tokens
    ADD CONSTRAINT tokens_pkey PRIMARY KEY (token_id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (user_id);


--
-- Name: portfolios portfolios_bot_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.portfolios
    ADD CONSTRAINT portfolios_bot_id_fkey FOREIGN KEY (model_id) REFERENCES public.models(model_id);


--
-- Name: portfolios portfolios_token_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.portfolios
    ADD CONSTRAINT portfolios_token_id_fkey FOREIGN KEY (token_id) REFERENCES public.tokens(token_id);


--
-- Name: portfolios portfolios_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.portfolios
    ADD CONSTRAINT portfolios_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id);


--
-- Name: tokens tokens_portfolio_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.tokens
    ADD CONSTRAINT tokens_portfolio_id_fkey FOREIGN KEY (portfolio_id) REFERENCES public.portfolios(portfolio_id);


--
-- PostgreSQL database dump complete
--

