--
-- PostgreSQL database dump
--

-- Dumped from database version 11.14 (Ubuntu 11.14-1.pgdg18.04+1)
-- Dumped by pg_dump version 11.14 (Ubuntu 11.14-1.pgdg18.04+1)

--
-- Name: slug; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.slug (
    id integer NOT NULL,
    count bigint NOT NULL
);


ALTER TABLE public.slug OWNER TO postgres;

--
-- Name: urls; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.urls (
    id character varying(7) NOT NULL,
    url character varying(249) NOT NULL,
    owner character varying(100) NOT NULL,
    times_accessed bigint DEFAULT 0 NOT NULL,
    created timestamp without time zone NOT NULL
);


ALTER TABLE public.urls OWNER TO postgres;

--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    email character varying(100) NOT NULL,
    password character varying(256) NOT NULL,
    is_premium boolean NOT NULL
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Data for Name: slug; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.slug (id, count) FROM stdin;
1	0
\.


--
-- Data for Name: urls; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.urls (id, url, owner, times_accessed, created) FROM stdin;
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (email, password, is_premium) FROM stdin;
\.


--
-- Name: slug slug_pk; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.slug
    ADD CONSTRAINT slug_pk PRIMARY KEY (id);


--
-- Name: urls urls_pk; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.urls
    ADD CONSTRAINT urls_pk PRIMARY KEY (id);


--
-- Name: users users_pk; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pk PRIMARY KEY (email);


--
-- Name: urls urls_fk; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.urls
    ADD CONSTRAINT urls_fk FOREIGN KEY (owner) REFERENCES public.users(email);


--
-- PostgreSQL database dump complete
--

