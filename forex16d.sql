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
-- Name: bill_status; Type: TYPE; Schema: public; Owner: admin
--

CREATE TYPE public.bill_status AS ENUM (
    'pending',
    'paid',
    'overdue'
);


ALTER TYPE public.bill_status OWNER TO admin;

--
-- Name: order_types; Type: TYPE; Schema: public; Owner: admin
--

CREATE TYPE public.order_types AS ENUM (
    'buy',
    'sell'
);


ALTER TYPE public.order_types OWNER TO admin;

--
-- Name: roles; Type: TYPE; Schema: public; Owner: admin
--

CREATE TYPE public.roles AS ENUM (
    'admin',
    'user'
);


ALTER TYPE public.roles OWNER TO admin;

--
-- Name: symbols; Type: TYPE; Schema: public; Owner: admin
--

CREATE TYPE public.symbols AS ENUM (
    'USDJPY',
    'XAUUSD',
    'GBPUSD',
    'EURUSD'
);


ALTER TYPE public.symbols OWNER TO admin;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: bills; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.bills (
    bill_id integer NOT NULL,
    net_amount double precision NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    due_date timestamp with time zone,
    status public.bill_status,
    net_amount_usd double precision,
    exchange_rate double precision,
    user_id character varying NOT NULL
);


ALTER TABLE public.bills OWNER TO admin;

--
-- Name: bills_bill_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.bills_bill_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.bills_bill_id_seq OWNER TO admin;

--
-- Name: bills_bill_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.bills_bill_id_seq OWNED BY public.bills.bill_id;


--
-- Name: market_data; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.market_data (
    "timestamp" timestamp without time zone NOT NULL,
    open numeric,
    high numeric,
    low numeric,
    close numeric,
    volume bigint
);


ALTER TABLE public.market_data OWNER TO admin;

--
-- Name: models; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.models (
    model_id character varying NOT NULL,
    name character varying NOT NULL,
    file_path character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone,
    commission double precision,
    symbol public.symbols,
    active boolean DEFAULT true NOT NULL
);


ALTER TABLE public.models OWNER TO admin;

--
-- Name: orders; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.orders (
    order_id bigint NOT NULL,
    portfolio_id character varying(255) NOT NULL,
    model_id character varying(255) NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    order_type public.order_types NOT NULL,
    symbol public.symbols NOT NULL,
    profit double precision NOT NULL,
    volume double precision NOT NULL,
    entry_price double precision NOT NULL,
    exit_price double precision NOT NULL,
    bill_id integer
);


ALTER TABLE public.orders OWNER TO admin;

--
-- Name: portfolios; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.portfolios (
    portfolio_id character varying(255) NOT NULL,
    user_id character varying(255) NOT NULL,
    model_id character varying(255),
    login bigint NOT NULL,
    name character varying(20) NOT NULL,
    connected boolean DEFAULT false NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    lot_size numeric(2,0),
    expert_id character varying(255),
    is_expert boolean DEFAULT false NOT NULL,
    commission numeric(3,2) DEFAULT 0.00 NOT NULL,
    CONSTRAINT commission_check CHECK (((commission >= (0)::numeric) AND (commission <= (1)::numeric)))
);


ALTER TABLE public.portfolios OWNER TO admin;

--
-- Name: receipts; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.receipts (
    receipt_id integer NOT NULL,
    bill_id integer NOT NULL,
    user_id character varying NOT NULL,
    amount_paid double precision NOT NULL,
    payment_date timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    reference_number character varying(100),
    receipt_image character varying(255),
    notes text,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    method character varying,
    CONSTRAINT receipts_amount_paid_check CHECK ((amount_paid > (0)::double precision))
);


ALTER TABLE public.receipts OWNER TO admin;

--
-- Name: receipts_receipt_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.receipts_receipt_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.receipts_receipt_id_seq OWNER TO admin;

--
-- Name: receipts_receipt_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.receipts_receipt_id_seq OWNED BY public.receipts.receipt_id;


--
-- Name: tokens; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.tokens (
    portfolio_id character varying(255) NOT NULL,
    access_token character varying NOT NULL,
    issued_at timestamp without time zone DEFAULT now() NOT NULL,
    expires_at date,
    is_active boolean DEFAULT true NOT NULL
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
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    is_banned boolean DEFAULT false NOT NULL,
    balance double precision DEFAULT 0
);


ALTER TABLE public.users OWNER TO admin;

--
-- Name: withdraw_requests; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.withdraw_requests (
    withdraw_id bigint NOT NULL,
    user_id character varying NOT NULL,
    amount numeric(15,2) NOT NULL,
    method character varying NOT NULL,
    bank_account character varying,
    wallet_address character varying,
    status character varying DEFAULT 'pending'::character varying NOT NULL,
    created_date timestamp with time zone DEFAULT now() NOT NULL,
    approved_date timestamp with time zone,
    CONSTRAINT withdraw_requests_check CHECK (((((method)::text = 'bank'::text) AND (bank_account IS NOT NULL) AND (wallet_address IS NULL)) OR (((method)::text = 'crypto'::text) AND (wallet_address IS NOT NULL) AND (bank_account IS NULL)))),
    CONSTRAINT withdraw_requests_method_check CHECK (((method)::text = ANY ((ARRAY['bank'::character varying, 'crypto'::character varying])::text[]))),
    CONSTRAINT withdraw_requests_status_check CHECK (((status)::text = ANY ((ARRAY['pending'::character varying, 'approved'::character varying, 'rejected'::character varying])::text[])))
);


ALTER TABLE public.withdraw_requests OWNER TO admin;

--
-- Name: withdraw_requests_withdraw_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.withdraw_requests_withdraw_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.withdraw_requests_withdraw_id_seq OWNER TO admin;

--
-- Name: withdraw_requests_withdraw_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.withdraw_requests_withdraw_id_seq OWNED BY public.withdraw_requests.withdraw_id;


--
-- Name: bills bill_id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.bills ALTER COLUMN bill_id SET DEFAULT nextval('public.bills_bill_id_seq'::regclass);


--
-- Name: receipts receipt_id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.receipts ALTER COLUMN receipt_id SET DEFAULT nextval('public.receipts_receipt_id_seq'::regclass);


--
-- Name: withdraw_requests withdraw_id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.withdraw_requests ALTER COLUMN withdraw_id SET DEFAULT nextval('public.withdraw_requests_withdraw_id_seq'::regclass);


--
-- Name: bills bills_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.bills
    ADD CONSTRAINT bills_pkey PRIMARY KEY (bill_id);


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
-- Name: receipts receipts_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.receipts
    ADD CONSTRAINT receipts_pkey PRIMARY KEY (receipt_id);


--
-- Name: receipts receipts_reference_number_key; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.receipts
    ADD CONSTRAINT receipts_reference_number_key UNIQUE (reference_number);


--
-- Name: tokens tokens_access_token_key; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.tokens
    ADD CONSTRAINT tokens_access_token_key UNIQUE (access_token);


--
-- Name: tokens tokens_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.tokens
    ADD CONSTRAINT tokens_pkey PRIMARY KEY (portfolio_id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (user_id);


--
-- Name: withdraw_requests withdraw_requests_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.withdraw_requests
    ADD CONSTRAINT withdraw_requests_pkey PRIMARY KEY (withdraw_id);


--
-- Name: bills bills_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.bills
    ADD CONSTRAINT bills_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id) ON DELETE SET NULL;


--
-- Name: tokens fk_portfolio; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.tokens
    ADD CONSTRAINT fk_portfolio FOREIGN KEY (portfolio_id) REFERENCES public.portfolios(portfolio_id) ON DELETE CASCADE;


--
-- Name: receipts fk_receipt_bill; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.receipts
    ADD CONSTRAINT fk_receipt_bill FOREIGN KEY (bill_id) REFERENCES public.bills(bill_id);


--
-- Name: receipts fk_receipt_user; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.receipts
    ADD CONSTRAINT fk_receipt_user FOREIGN KEY (user_id) REFERENCES public.users(user_id);


--
-- Name: orders orders_bill_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_bill_id_fkey FOREIGN KEY (bill_id) REFERENCES public.bills(bill_id) ON DELETE SET NULL;


--
-- Name: portfolios portfolio_id; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.portfolios
    ADD CONSTRAINT portfolio_id FOREIGN KEY (user_id) REFERENCES public.users(user_id) ON DELETE CASCADE;


--
-- Name: portfolios portfolios_bot_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.portfolios
    ADD CONSTRAINT portfolios_bot_id_fkey FOREIGN KEY (model_id) REFERENCES public.models(model_id) ON DELETE SET NULL;


--
-- Name: portfolios portfolios_expert_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.portfolios
    ADD CONSTRAINT portfolios_expert_id_fkey FOREIGN KEY (expert_id) REFERENCES public.portfolios(portfolio_id) ON DELETE SET NULL;


--
-- Name: withdraw_requests withdraw_requests_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.withdraw_requests
    ADD CONSTRAINT withdraw_requests_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

