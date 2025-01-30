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
    connected boolean NOT NULL,
    create_at date NOT NULL,
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
    role public.roles NOT NULL,
    created_at timestamp with time zone NOT NULL
);


ALTER TABLE public.users OWNER TO admin;

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

