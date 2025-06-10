--
-- PostgreSQL database dump
--

-- Dumped from database version 16.9 (Debian 16.9-1.pgdg120+1)
-- Dumped by pg_dump version 16.9 (Debian 16.9-1.pgdg120+1)

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

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: category; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.category (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    description text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.category OWNER TO postgres;

--
-- Name: category_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.category_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.category_id_seq OWNER TO postgres;

--
-- Name: category_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.category_id_seq OWNED BY public.category.id;


--
-- Name: customer; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.customer (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    phone character varying(20) NOT NULL,
    email character varying(120),
    birth_date date,
    address text,
    notes text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.customer OWNER TO postgres;

--
-- Name: customer_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.customer_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.customer_id_seq OWNER TO postgres;

--
-- Name: customer_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.customer_id_seq OWNED BY public.customer.id;


--
-- Name: employee; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.employee (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    hire_date date,
    status character varying(20),
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.employee OWNER TO postgres;

--
-- Name: employee_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.employee_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.employee_id_seq OWNER TO postgres;

--
-- Name: employee_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.employee_id_seq OWNED BY public.employee.id;


--
-- Name: service; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.service (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    price double precision NOT NULL,
    duration integer NOT NULL,
    description text,
    notes text,
    status character varying(20),
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.service OWNER TO postgres;

--
-- Name: service_history; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.service_history (
    id integer NOT NULL,
    customer_id integer NOT NULL,
    service_id integer NOT NULL,
    employee_id integer NOT NULL,
    service_date timestamp without time zone NOT NULL,
    price double precision NOT NULL,
    payment_method character varying(20) NOT NULL,
    notes text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.service_history OWNER TO postgres;

--
-- Name: service_history_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.service_history_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.service_history_id_seq OWNER TO postgres;

--
-- Name: service_history_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.service_history_id_seq OWNED BY public.service_history.id;


--
-- Name: service_history_image; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.service_history_image (
    id integer NOT NULL,
    service_history_id integer NOT NULL,
    image_url character varying(255) NOT NULL,
    created_at timestamp without time zone
);


ALTER TABLE public.service_history_image OWNER TO postgres;

--
-- Name: service_history_image_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.service_history_image_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.service_history_image_id_seq OWNER TO postgres;

--
-- Name: service_history_image_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.service_history_image_id_seq OWNED BY public.service_history_image.id;


--
-- Name: service_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.service_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.service_id_seq OWNER TO postgres;

--
-- Name: service_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.service_id_seq OWNED BY public.service.id;


--
-- Name: user; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."user" (
    id integer NOT NULL,
    username character varying(80) NOT NULL,
    email character varying(120) NOT NULL,
    password_hash character varying(256),
    role character varying(20),
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public."user" OWNER TO postgres;

--
-- Name: user_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.user_id_seq OWNER TO postgres;

--
-- Name: user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.user_id_seq OWNED BY public."user".id;


--
-- Name: category id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.category ALTER COLUMN id SET DEFAULT nextval('public.category_id_seq'::regclass);


--
-- Name: customer id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.customer ALTER COLUMN id SET DEFAULT nextval('public.customer_id_seq'::regclass);


--
-- Name: employee id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.employee ALTER COLUMN id SET DEFAULT nextval('public.employee_id_seq'::regclass);


--
-- Name: service id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.service ALTER COLUMN id SET DEFAULT nextval('public.service_id_seq'::regclass);


--
-- Name: service_history id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.service_history ALTER COLUMN id SET DEFAULT nextval('public.service_history_id_seq'::regclass);


--
-- Name: service_history_image id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.service_history_image ALTER COLUMN id SET DEFAULT nextval('public.service_history_image_id_seq'::regclass);


--
-- Name: user id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."user" ALTER COLUMN id SET DEFAULT nextval('public.user_id_seq'::regclass);


--
-- Data for Name: category; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.category (id, name, description, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: customer; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.customer (id, name, phone, email, birth_date, address, notes, created_at, updated_at) FROM stdin;
1	Cô Wang	0965558585	\N	1996-06-12	Đài Loan		2025-06-06 04:25:16.394575	2025-06-06 04:25:16.394579
2	Keo Lì	0965858757	\N	1900-07-01	Bình Tân		2025-06-06 04:25:43.03098	2025-06-06 04:25:43.031056
\.


--
-- Data for Name: employee; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.employee (id, name, hire_date, status, created_at, updated_at) FROM stdin;
1	Male	2025-06-06	active	2025-06-06 04:23:27.169046	2025-06-06 04:23:27.16905
2	Pha	2025-06-06	active	2025-06-06 04:23:34.220303	2025-06-06 04:23:34.220309
3	Chan	2025-06-06	active	2025-06-06 04:23:39.537387	2025-06-06 04:23:39.537393
4	Gina	2025-06-06	active	2025-06-06 04:23:46.994915	2025-06-06 04:23:46.994919
5	Bonine	2025-06-06	active	2025-06-06 04:23:52.957045	2025-06-06 04:23:52.957059
6	Jolie	2025-06-06	active	2025-06-06 04:23:59.055065	2025-06-06 04:23:59.055071
\.


--
-- Data for Name: service; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.service (id, name, price, duration, description, notes, status, created_at, updated_at) FROM stdin;
1	Classic	0	0	Classic\r\n	\N	active	2025-06-06 04:24:11.416948	2025-06-06 04:24:11.416954
2	Volume	0	0	Volume	\N	active	2025-06-06 04:24:20.748149	2025-06-06 04:24:20.748155
3	Thiết Kế	0	0	Thiết Kế	\N	active	2025-06-06 04:24:32.753262	2025-06-06 04:24:32.753269
\.


--
-- Data for Name: service_history; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.service_history (id, customer_id, service_id, employee_id, service_date, price, payment_method, notes, created_at, updated_at) FROM stdin;
3	1	3	4	2025-06-06 07:17:00	599000	tiền mặt		2025-06-06 07:17:36.024102	2025-06-06 07:17:46.607401
2	1	1	5	2025-06-06 04:25:00	399000	Combo 5 lần 1	Mi Ánh Dương Athena 0.07 400s cong D	2025-06-06 04:40:45.251559	2025-06-06 07:24:29.345365
4	2	3	5	2025-06-01 07:25:00	599000	chuyển khoản	asd asd asd á	2025-06-06 07:25:46.730425	2025-06-06 07:25:46.730433
\.


--
-- Data for Name: service_history_image; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.service_history_image (id, service_history_id, image_url, created_at) FROM stdin;
7	2	static/uploads/z6621252770426_90891c76f9bc2bc34bafde9ead421a2a.jpg	2025-06-06 07:24:24.003495
8	4	static/uploads/z6621252742081_cff9a16bbf997190629924c74f4a0ce5.jpg	2025-06-06 07:25:46.806974
\.


--
-- Data for Name: user; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public."user" (id, username, email, password_hash, role, created_at, updated_at) FROM stdin;
\.


--
-- Name: category_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.category_id_seq', 1, false);


--
-- Name: customer_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.customer_id_seq', 2, true);


--
-- Name: employee_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.employee_id_seq', 6, true);


--
-- Name: service_history_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.service_history_id_seq', 4, true);


--
-- Name: service_history_image_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.service_history_image_id_seq', 8, true);


--
-- Name: service_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.service_id_seq', 3, true);


--
-- Name: user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.user_id_seq', 1, false);


--
-- Name: category category_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.category
    ADD CONSTRAINT category_pkey PRIMARY KEY (id);


--
-- Name: customer customer_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.customer
    ADD CONSTRAINT customer_pkey PRIMARY KEY (id);


--
-- Name: employee employee_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.employee
    ADD CONSTRAINT employee_pkey PRIMARY KEY (id);


--
-- Name: service_history_image service_history_image_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.service_history_image
    ADD CONSTRAINT service_history_image_pkey PRIMARY KEY (id);


--
-- Name: service_history service_history_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.service_history
    ADD CONSTRAINT service_history_pkey PRIMARY KEY (id);


--
-- Name: service service_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.service
    ADD CONSTRAINT service_pkey PRIMARY KEY (id);


--
-- Name: user user_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_email_key UNIQUE (email);


--
-- Name: user user_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_pkey PRIMARY KEY (id);


--
-- Name: user user_username_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_username_key UNIQUE (username);


--
-- Name: service_history service_history_customer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.service_history
    ADD CONSTRAINT service_history_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES public.customer(id);


--
-- Name: service_history service_history_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.service_history
    ADD CONSTRAINT service_history_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employee(id);


--
-- Name: service_history_image service_history_image_service_history_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.service_history_image
    ADD CONSTRAINT service_history_image_service_history_id_fkey FOREIGN KEY (service_history_id) REFERENCES public.service_history(id);


--
-- Name: service_history service_history_service_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.service_history
    ADD CONSTRAINT service_history_service_id_fkey FOREIGN KEY (service_id) REFERENCES public.service(id);


--
-- PostgreSQL database dump complete
--

