--
-- PostgreSQL database dump
--

\restrict OFt7EcrBHOUaSlqo99bhA3PqIFOHfQa9goxJiKhsdg9FDU55wcV7jzHryTl3d6K

-- Dumped from database version 17.6
-- Dumped by pg_dump version 18.1

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

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: artefact; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.artefact (
    id integer NOT NULL,
    site_id integer NOT NULL,
    artefact_type_id integer NOT NULL,
    artefact_code text,
    display_name text,
    metadata jsonb,
    installed_at timestamp without time zone
);


ALTER TABLE public.artefact OWNER TO postgres;

--
-- Name: artefact_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.artefact_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.artefact_id_seq OWNER TO postgres;

--
-- Name: artefact_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.artefact_id_seq OWNED BY public.artefact.id;


--
-- Name: artefactlogattributevalue; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.artefactlogattributevalue (
    id bigint NOT NULL,
    artefact_log_instance_id bigint NOT NULL,
    artefact_type_attribute_id integer NOT NULL,
    numeric_value double precision,
    text_value text,
    unit_override text,
    quality smallint
);


ALTER TABLE public.artefactlogattributevalue OWNER TO postgres;

--
-- Name: artefactlogattributevalue_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.artefactlogattributevalue_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.artefactlogattributevalue_id_seq OWNER TO postgres;

--
-- Name: artefactlogattributevalue_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.artefactlogattributevalue_id_seq OWNED BY public.artefactlogattributevalue.id;


--
-- Name: artefactloginstance; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.artefactloginstance (
    id bigint NOT NULL,
    artefact_id integer NOT NULL,
    ts timestamp without time zone NOT NULL,
    date date GENERATED ALWAYS AS ((ts)::date) STORED,
    hour integer GENERATED ALWAYS AS ((EXTRACT(hour FROM ts))::integer) STORED,
    minute integer GENERATED ALWAYS AS ((EXTRACT(minute FROM ts))::integer) STORED,
    second integer GENERATED ALWAYS AS ((EXTRACT(second FROM ts))::integer) STORED,
    msec integer GENERATED ALWAYS AS (((EXTRACT(milliseconds FROM ts))::integer % 1000)) STORED
);


ALTER TABLE public.artefactloginstance OWNER TO postgres;

--
-- Name: artefactloginstance_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.artefactloginstance_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.artefactloginstance_id_seq OWNER TO postgres;

--
-- Name: artefactloginstance_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.artefactloginstance_id_seq OWNED BY public.artefactloginstance.id;


--
-- Name: artefacttype; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.artefacttype (
    id integer NOT NULL,
    code text NOT NULL,
    name text NOT NULL,
    notes text
);


ALTER TABLE public.artefacttype OWNER TO postgres;

--
-- Name: artefacttype_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.artefacttype_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.artefacttype_id_seq OWNER TO postgres;

--
-- Name: artefacttype_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.artefacttype_id_seq OWNED BY public.artefacttype.id;


--
-- Name: artefacttypeattribute; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.artefacttypeattribute (
    id integer NOT NULL,
    artefact_type_id integer NOT NULL,
    attribute_name text NOT NULL,
    attribute_unit text,
    data_type text DEFAULT 'number'::text,
    description text
);


ALTER TABLE public.artefacttypeattribute OWNER TO postgres;

--
-- Name: artefacttypeattribute_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.artefacttypeattribute_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.artefacttypeattribute_id_seq OWNER TO postgres;

--
-- Name: artefacttypeattribute_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.artefacttypeattribute_id_seq OWNED BY public.artefacttypeattribute.id;


--
-- Name: enphase; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.enphase (
    id integer NOT NULL,
    date timestamp without time zone,
    energy_produced double precision,
    energy_consumed double precision,
    grid_exported double precision,
    grid_imported double precision,
    locationid integer
);


ALTER TABLE public.enphase OWNER TO postgres;

--
-- Name: enphase_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.enphase ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.enphase_id_seq
    START WITH 89569
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: enphase_panel_production; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.enphase_panel_production (
    id integer NOT NULL,
    panel_id character varying(45) DEFAULT NULL::character varying,
    date date,
    production integer,
    panel_group character varying(45) DEFAULT NULL::character varying,
    locationid integer
);


ALTER TABLE public.enphase_panel_production OWNER TO postgres;

--
-- Name: enphase_panel_production_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.enphase_panel_production ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.enphase_panel_production_id_seq
    START WITH 21202
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: location; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.location (
    locationid integer NOT NULL,
    locationname character varying(100)
);


ALTER TABLE public.location OWNER TO postgres;

--
-- Name: open_weather; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.open_weather (
    id integer NOT NULL,
    date_time timestamp without time zone,
    timezone integer,
    city_name character varying(255) DEFAULT NULL::character varying,
    latitude double precision,
    longitude double precision,
    temperature double precision,
    visibility double precision,
    dew_point double precision,
    feels_like_temperature double precision,
    temperature_min double precision,
    temperature_max double precision,
    pressure double precision,
    sea_level double precision,
    ground_level double precision,
    humidity double precision,
    wind_speed double precision,
    wind_degree integer,
    wind_gust integer,
    rain_1h double precision,
    rain_3h double precision,
    snow_1h double precision,
    snow_3h double precision,
    clouds_all integer,
    weather_id integer,
    weather_main character varying(45) DEFAULT NULL::character varying,
    weather_description character varying(255) DEFAULT NULL::character varying,
    weather_icon character varying(45) DEFAULT NULL::character varying,
    locationid integer
);


ALTER TABLE public.open_weather OWNER TO postgres;

--
-- Name: open_weather_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.open_weather ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.open_weather_id_seq
    START WITH 15886
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: panel; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.panel (
    id integer NOT NULL,
    site_id integer NOT NULL,
    vendor_id text,
    group_id integer,
    model text,
    capacity_w integer,
    installed_at date
);


ALTER TABLE public.panel OWNER TO postgres;

--
-- Name: panel_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.panel_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.panel_id_seq OWNER TO postgres;

--
-- Name: panel_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.panel_id_seq OWNED BY public.panel.id;


--
-- Name: panelgroup; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.panelgroup (
    id integer NOT NULL,
    site_id integer NOT NULL,
    name text NOT NULL
);


ALTER TABLE public.panelgroup OWNER TO postgres;

--
-- Name: panelgroup_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.panelgroup_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.panelgroup_id_seq OWNER TO postgres;

--
-- Name: panelgroup_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.panelgroup_id_seq OWNED BY public.panelgroup.id;


--
-- Name: panelproduction; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.panelproduction (
    id bigint NOT NULL,
    site_id integer NOT NULL,
    panel_id integer NOT NULL,
    date date NOT NULL,
    production_wh integer
);


ALTER TABLE public.panelproduction OWNER TO postgres;

--
-- Name: panelproduction_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.panelproduction_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.panelproduction_id_seq OWNER TO postgres;

--
-- Name: panelproduction_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.panelproduction_id_seq OWNED BY public.panelproduction.id;


--
-- Name: solarsite; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.solarsite (
    id integer NOT NULL,
    site_code text NOT NULL,
    site_name text NOT NULL,
    timezone_name text DEFAULT 'UTC'::text,
    latitude double precision,
    longitude double precision,
    created_at timestamp without time zone DEFAULT now()
);


ALTER TABLE public.solarsite OWNER TO postgres;

--
-- Name: solarsite_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.solarsite_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.solarsite_id_seq OWNER TO postgres;

--
-- Name: solarsite_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.solarsite_id_seq OWNED BY public.solarsite.id;


--
-- Name: studer; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.studer (
    id integer NOT NULL,
    date_time timestamp without time zone,
    battery_voltage_l1 double precision,
    battery_voltage_l2 double precision,
    battery_voltage_l3 double precision,
    grid_input_voltage_l1 double precision,
    grid_input_voltage_l2 double precision,
    grid_input_voltage_l3 double precision,
    grid_input_current_l1 double precision,
    grid_input_current_l2 double precision,
    grid_input_current_l3 double precision,
    apparent_power_output_l1 double precision,
    apparent_power_output_l2 double precision,
    apparent_power_output_l3 double precision,
    power_output_w_external_l1 double precision,
    power_output_w_external_l2 double precision,
    power_output_w_external_l3 double precision,
    output_frequency_l1 double precision,
    output_frequency_l2 double precision,
    output_frequency_l3 double precision,
    grid_input_frequency_l1 double precision,
    grid_input_frequency_l2 double precision,
    grid_input_frequency_l3 double precision,
    xt_phase_l1 double precision,
    xt_phase_l2 double precision,
    xt_phase_l3 double precision,
    xt_mode_l1 integer,
    xt_mode_l2 integer,
    xt_mode_l3 integer,
    grid_status_l1 integer,
    grid_status_l2 integer,
    grid_status_l3 integer,
    xt_rme_l1 integer,
    xt_rme_l2 integer,
    xt_rme_l3 integer,
    xt_aux1_l1 integer,
    xt_aux1_l2 integer,
    xt_aux1_l3 integer,
    xt_aux2_l1 integer,
    xt_aux2_l2 integer,
    xt_aux2_l3 integer,
    battery_voltage_l1_1 double precision,
    battery_voltage_l2_2 double precision,
    battery_voltage_l3_3 double precision,
    battery_current_l1 double precision,
    battery_current_l2 double precision,
    battery_current_l3 double precision,
    studer_grid_imp_exp_l1 double precision,
    studer_grid_imp_exp_l2 double precision,
    studer_grid_imp_exp_l3 double precision,
    power_output_l1 double precision,
    power_output_l2 double precision,
    power_output_l3 double precision,
    studer_temperature_l1 double precision,
    studer_temperature_l2 double precision,
    studer_temperature_l3 double precision,
    battery_voltage double precision,
    battery_current double precision,
    battery_state_of_charge double precision,
    battery_temperature double precision,
    solar_power double precision,
    xt_dbg1 double precision,
    bsp_loce double precision,
    sys_msg double precision,
    sys_scom_err double precision,
    vt_psom_1 double precision,
    vt_psom_all double precision,
    vt_mode double precision,
    vt_tp1m double precision,
    vt_upvm double precision,
    vt_ibam double precision,
    vt_ubam double precision,
    vt_phas double precision,
    vt_rme double precision,
    vt_aux_1 double precision,
    vt_aux_2 double precision
);


ALTER TABLE public.studer OWNER TO postgres;

--
-- Name: studer_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.studer ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.studer_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: v_enphase; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.v_enphase AS
 SELECT (ali.id)::integer AS id,
    ali.ts AS date,
    max(
        CASE
            WHEN (alav.artefact_type_attribute_id = 1) THEN COALESCE(alav.numeric_value,
            CASE
                WHEN (alav.text_value ~ '^[+-]?\d+(\.\d+)?$'::text) THEN (alav.text_value)::double precision
                ELSE NULL::double precision
            END)
            ELSE NULL::double precision
        END) AS energy_produced,
    max(
        CASE
            WHEN (alav.artefact_type_attribute_id = 2) THEN COALESCE(alav.numeric_value,
            CASE
                WHEN (alav.text_value ~ '^[+-]?\d+(\.\d+)?$'::text) THEN (alav.text_value)::double precision
                ELSE NULL::double precision
            END)
            ELSE NULL::double precision
        END) AS energy_consumed,
    max(
        CASE
            WHEN (alav.artefact_type_attribute_id = 33) THEN COALESCE(alav.numeric_value,
            CASE
                WHEN (alav.text_value ~ '^[+-]?\d+(\.\d+)?$'::text) THEN (alav.text_value)::double precision
                ELSE NULL::double precision
            END)
            ELSE NULL::double precision
        END) AS grid_exported,
    max(
        CASE
            WHEN (alav.artefact_type_attribute_id = 44) THEN COALESCE(alav.numeric_value,
            CASE
                WHEN (alav.text_value ~ '^[+-]?\d+(\.\d+)?$'::text) THEN (alav.text_value)::double precision
                ELSE NULL::double precision
            END)
            ELSE NULL::double precision
        END) AS grid_imported,
    a.site_id AS locationid
   FROM ((public.artefactloginstance ali
     JOIN public.artefact a ON ((a.id = ali.artefact_id)))
     LEFT JOIN public.artefactlogattributevalue alav ON ((alav.artefact_log_instance_id = ali.id)))
  WHERE (ali.artefact_id = 2)
  GROUP BY ali.id, ali.ts, a.site_id;


ALTER VIEW public.v_enphase OWNER TO postgres;

--
-- Name: v_open_weather; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.v_open_weather AS
 SELECT (ali.id)::integer AS id,
    ali.ts AS date_time,
    a.site_id AS locationid,
    (max(
        CASE
            WHEN (alav.artefact_type_attribute_id = 6) THEN alav.numeric_value
            ELSE NULL::double precision
        END))::integer AS timezone,
    max(
        CASE
            WHEN (alav.artefact_type_attribute_id = 7) THEN alav.text_value
            ELSE NULL::text
        END) AS city_name,
    max(
        CASE
            WHEN (alav.artefact_type_attribute_id = 8) THEN alav.numeric_value
            ELSE NULL::double precision
        END) AS latitude,
    max(
        CASE
            WHEN (alav.artefact_type_attribute_id = 9) THEN alav.numeric_value
            ELSE NULL::double precision
        END) AS longitude,
    max(
        CASE
            WHEN (alav.artefact_type_attribute_id = 11) THEN alav.numeric_value
            ELSE NULL::double precision
        END) AS visibility,
    max(
        CASE
            WHEN (alav.artefact_type_attribute_id = 12) THEN alav.numeric_value
            ELSE NULL::double precision
        END) AS dew_point,
    max(
        CASE
            WHEN (alav.artefact_type_attribute_id = 16) THEN alav.numeric_value
            ELSE NULL::double precision
        END) AS pressure,
    max(
        CASE
            WHEN (alav.artefact_type_attribute_id = 17) THEN alav.numeric_value
            ELSE NULL::double precision
        END) AS sea_level,
    max(
        CASE
            WHEN (alav.artefact_type_attribute_id = 18) THEN alav.numeric_value
            ELSE NULL::double precision
        END) AS ground_level,
    max(
        CASE
            WHEN (alav.artefact_type_attribute_id = 19) THEN alav.numeric_value
            ELSE NULL::double precision
        END) AS humidity,
    max(
        CASE
            WHEN (alav.artefact_type_attribute_id = 20) THEN alav.numeric_value
            ELSE NULL::double precision
        END) AS wind_speed,
    (max(
        CASE
            WHEN (alav.artefact_type_attribute_id = 21) THEN alav.numeric_value
            ELSE NULL::double precision
        END))::integer AS wind_degree,
    (max(
        CASE
            WHEN (alav.artefact_type_attribute_id = 22) THEN alav.numeric_value
            ELSE NULL::double precision
        END))::integer AS wind_gust,
    max(
        CASE
            WHEN (alav.artefact_type_attribute_id = 23) THEN alav.numeric_value
            ELSE NULL::double precision
        END) AS rain_1h,
    max(
        CASE
            WHEN (alav.artefact_type_attribute_id = 24) THEN alav.numeric_value
            ELSE NULL::double precision
        END) AS rain_3h,
    max(
        CASE
            WHEN (alav.artefact_type_attribute_id = 25) THEN alav.numeric_value
            ELSE NULL::double precision
        END) AS snow_1h,
    max(
        CASE
            WHEN (alav.artefact_type_attribute_id = 26) THEN alav.numeric_value
            ELSE NULL::double precision
        END) AS snow_3h,
    (max(
        CASE
            WHEN (alav.artefact_type_attribute_id = 27) THEN alav.numeric_value
            ELSE NULL::double precision
        END))::integer AS clouds_all,
    (max(
        CASE
            WHEN (alav.artefact_type_attribute_id = 28) THEN alav.numeric_value
            ELSE NULL::double precision
        END))::integer AS weather_id,
    max(
        CASE
            WHEN (alav.artefact_type_attribute_id = 29) THEN alav.text_value
            ELSE NULL::text
        END) AS weather_main,
    max(
        CASE
            WHEN (alav.artefact_type_attribute_id = 30) THEN alav.text_value
            ELSE NULL::text
        END) AS weather_description,
    max(
        CASE
            WHEN (alav.artefact_type_attribute_id = 31) THEN alav.text_value
            ELSE NULL::text
        END) AS weather_icon
   FROM ((public.artefactloginstance ali
     JOIN public.artefact a ON ((a.id = ali.artefact_id)))
     LEFT JOIN public.artefactlogattributevalue alav ON ((alav.artefact_log_instance_id = ali.id)))
  WHERE (ali.artefact_id = 3)
  GROUP BY ali.id, ali.ts, a.site_id;


ALTER VIEW public.v_open_weather OWNER TO postgres;

--
-- Name: v_studer; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.v_studer AS
 WITH vals AS (
         SELECT (ali.id)::integer AS id,
            ali.ts AS date_time,
            lower(ata.attribute_name) AS attr_name,
            COALESCE(alav.numeric_value,
                CASE
                    WHEN (alav.text_value ~ '^[+-]?\d+(\.\d+)?$'::text) THEN (alav.text_value)::double precision
                    ELSE NULL::double precision
                END) AS val
           FROM (((public.artefactloginstance ali
             JOIN public.artefact a ON ((a.id = ali.artefact_id)))
             LEFT JOIN public.artefactlogattributevalue alav ON ((alav.artefact_log_instance_id = ali.id)))
             LEFT JOIN public.artefacttypeattribute ata ON ((ata.id = alav.artefact_type_attribute_id)))
          WHERE (ali.artefact_id = 1)
        )
 SELECT v0.id,
    v0.date_time,
    max(
        CASE
            WHEN (v.attr_name = 'battery_voltage_l1'::text) THEN v.val
            ELSE NULL::double precision
        END) AS battery_voltage_l1,
    max(
        CASE
            WHEN (v.attr_name = 'battery_voltage_l2'::text) THEN v.val
            ELSE NULL::double precision
        END) AS battery_voltage_l2,
    max(
        CASE
            WHEN (v.attr_name = 'battery_voltage_l3'::text) THEN v.val
            ELSE NULL::double precision
        END) AS battery_voltage_l3,
    max(
        CASE
            WHEN (v.attr_name = 'grid_input_voltage_l1'::text) THEN v.val
            ELSE NULL::double precision
        END) AS grid_input_voltage_l1,
    max(
        CASE
            WHEN (v.attr_name = 'grid_input_voltage_l2'::text) THEN v.val
            ELSE NULL::double precision
        END) AS grid_input_voltage_l2,
    max(
        CASE
            WHEN (v.attr_name = 'grid_input_voltage_l3'::text) THEN v.val
            ELSE NULL::double precision
        END) AS grid_input_voltage_l3,
    max(
        CASE
            WHEN (v.attr_name = 'grid_input_current_l1'::text) THEN v.val
            ELSE NULL::double precision
        END) AS grid_input_current_l1,
    max(
        CASE
            WHEN (v.attr_name = 'grid_input_current_l2'::text) THEN v.val
            ELSE NULL::double precision
        END) AS grid_input_current_l2,
    max(
        CASE
            WHEN (v.attr_name = 'grid_input_current_l3'::text) THEN v.val
            ELSE NULL::double precision
        END) AS grid_input_current_l3,
    max(
        CASE
            WHEN (v.attr_name = 'apparent_power_output_l1'::text) THEN v.val
            ELSE NULL::double precision
        END) AS apparent_power_output_l1,
    max(
        CASE
            WHEN (v.attr_name = 'apparent_power_output_l2'::text) THEN v.val
            ELSE NULL::double precision
        END) AS apparent_power_output_l2,
    max(
        CASE
            WHEN (v.attr_name = 'apparent_power_output_l3'::text) THEN v.val
            ELSE NULL::double precision
        END) AS apparent_power_output_l3,
    max(
        CASE
            WHEN (v.attr_name = 'power_output_w_external_l1'::text) THEN v.val
            ELSE NULL::double precision
        END) AS power_output_w_external_l1,
    max(
        CASE
            WHEN (v.attr_name = 'power_output_w_external_l2'::text) THEN v.val
            ELSE NULL::double precision
        END) AS power_output_w_external_l2,
    max(
        CASE
            WHEN (v.attr_name = 'power_output_w_external_l3'::text) THEN v.val
            ELSE NULL::double precision
        END) AS power_output_w_external_l3,
    max(
        CASE
            WHEN (v.attr_name = 'output_frequency_l1'::text) THEN v.val
            ELSE NULL::double precision
        END) AS output_frequency_l1,
    max(
        CASE
            WHEN (v.attr_name = 'output_frequency_l2'::text) THEN v.val
            ELSE NULL::double precision
        END) AS output_frequency_l2,
    max(
        CASE
            WHEN (v.attr_name = 'output_frequency_l3'::text) THEN v.val
            ELSE NULL::double precision
        END) AS output_frequency_l3,
    max(
        CASE
            WHEN (v.attr_name = 'grid_input_frequency_l1'::text) THEN v.val
            ELSE NULL::double precision
        END) AS grid_input_frequency_l1,
    max(
        CASE
            WHEN (v.attr_name = 'grid_input_frequency_l2'::text) THEN v.val
            ELSE NULL::double precision
        END) AS grid_input_frequency_l2,
    max(
        CASE
            WHEN (v.attr_name = 'grid_input_frequency_l3'::text) THEN v.val
            ELSE NULL::double precision
        END) AS grid_input_frequency_l3,
    (max(
        CASE
            WHEN (v.attr_name = 'xt_phase_l1'::text) THEN v.val
            ELSE NULL::double precision
        END))::integer AS xt_phase_l1,
    (max(
        CASE
            WHEN (v.attr_name = 'xt_phase_l2'::text) THEN v.val
            ELSE NULL::double precision
        END))::integer AS xt_phase_l2,
    (max(
        CASE
            WHEN (v.attr_name = 'xt_phase_l3'::text) THEN v.val
            ELSE NULL::double precision
        END))::integer AS xt_phase_l3,
    (max(
        CASE
            WHEN (v.attr_name = 'xt_mode_l1'::text) THEN v.val
            ELSE NULL::double precision
        END))::integer AS xt_mode_l1,
    (max(
        CASE
            WHEN (v.attr_name = 'xt_mode_l2'::text) THEN v.val
            ELSE NULL::double precision
        END))::integer AS xt_mode_l2,
    (max(
        CASE
            WHEN (v.attr_name = 'xt_mode_l3'::text) THEN v.val
            ELSE NULL::double precision
        END))::integer AS xt_mode_l3,
    (max(
        CASE
            WHEN (v.attr_name = 'grid_status_l1'::text) THEN v.val
            ELSE NULL::double precision
        END))::integer AS grid_status_l1,
    (max(
        CASE
            WHEN (v.attr_name = 'grid_status_l2'::text) THEN v.val
            ELSE NULL::double precision
        END))::integer AS grid_status_l2,
    (max(
        CASE
            WHEN (v.attr_name = 'grid_status_l3'::text) THEN v.val
            ELSE NULL::double precision
        END))::integer AS grid_status_l3,
    (max(
        CASE
            WHEN (v.attr_name = 'xt_rme_l1'::text) THEN v.val
            ELSE NULL::double precision
        END))::integer AS xt_rme_l1,
    (max(
        CASE
            WHEN (v.attr_name = 'xt_rme_l2'::text) THEN v.val
            ELSE NULL::double precision
        END))::integer AS xt_rme_l2,
    (max(
        CASE
            WHEN (v.attr_name = 'xt_rme_l3'::text) THEN v.val
            ELSE NULL::double precision
        END))::integer AS xt_rme_l3,
    (max(
        CASE
            WHEN (v.attr_name = 'xt_aux1_l1'::text) THEN v.val
            ELSE NULL::double precision
        END))::integer AS xt_aux1_l1,
    (max(
        CASE
            WHEN (v.attr_name = 'xt_aux1_l2'::text) THEN v.val
            ELSE NULL::double precision
        END))::integer AS xt_aux1_l2,
    (max(
        CASE
            WHEN (v.attr_name = 'xt_aux1_l3'::text) THEN v.val
            ELSE NULL::double precision
        END))::integer AS xt_aux1_l3,
    (max(
        CASE
            WHEN (v.attr_name = 'xt_aux2_l1'::text) THEN v.val
            ELSE NULL::double precision
        END))::integer AS xt_aux2_l1,
    (max(
        CASE
            WHEN (v.attr_name = 'xt_aux2_l2'::text) THEN v.val
            ELSE NULL::double precision
        END))::integer AS xt_aux2_l2,
    (max(
        CASE
            WHEN (v.attr_name = 'xt_aux2_l3'::text) THEN v.val
            ELSE NULL::double precision
        END))::integer AS xt_aux2_l3,
    max(
        CASE
            WHEN (v.attr_name = 'battery_voltage_l1_1'::text) THEN v.val
            ELSE NULL::double precision
        END) AS battery_voltage_l1_1,
    max(
        CASE
            WHEN (v.attr_name = 'battery_voltage_l2_2'::text) THEN v.val
            ELSE NULL::double precision
        END) AS battery_voltage_l2_2,
    max(
        CASE
            WHEN (v.attr_name = 'battery_voltage_l3_3'::text) THEN v.val
            ELSE NULL::double precision
        END) AS battery_voltage_l3_3,
    max(
        CASE
            WHEN (v.attr_name = 'battery_current_l1'::text) THEN v.val
            ELSE NULL::double precision
        END) AS battery_current_l1,
    max(
        CASE
            WHEN (v.attr_name = 'battery_current_l2'::text) THEN v.val
            ELSE NULL::double precision
        END) AS battery_current_l2,
    max(
        CASE
            WHEN (v.attr_name = 'battery_current_l3'::text) THEN v.val
            ELSE NULL::double precision
        END) AS battery_current_l3,
    max(
        CASE
            WHEN (v.attr_name = 'studer_grid_imp_exp_l1'::text) THEN v.val
            ELSE NULL::double precision
        END) AS studer_grid_imp_exp_l1,
    max(
        CASE
            WHEN (v.attr_name = 'studer_grid_imp_exp_l2'::text) THEN v.val
            ELSE NULL::double precision
        END) AS studer_grid_imp_exp_l2,
    max(
        CASE
            WHEN (v.attr_name = 'studer_grid_imp_exp_l3'::text) THEN v.val
            ELSE NULL::double precision
        END) AS studer_grid_imp_exp_l3,
    max(
        CASE
            WHEN (v.attr_name = 'power_output_l1'::text) THEN v.val
            ELSE NULL::double precision
        END) AS power_output_l1,
    max(
        CASE
            WHEN (v.attr_name = 'power_output_l2'::text) THEN v.val
            ELSE NULL::double precision
        END) AS power_output_l2,
    max(
        CASE
            WHEN (v.attr_name = 'power_output_l3'::text) THEN v.val
            ELSE NULL::double precision
        END) AS power_output_l3,
    max(
        CASE
            WHEN (v.attr_name = 'studer_temperature_l1'::text) THEN v.val
            ELSE NULL::double precision
        END) AS studer_temperature_l1,
    max(
        CASE
            WHEN (v.attr_name = 'studer_temperature_l2'::text) THEN v.val
            ELSE NULL::double precision
        END) AS studer_temperature_l2,
    max(
        CASE
            WHEN (v.attr_name = 'studer_temperature_l3'::text) THEN v.val
            ELSE NULL::double precision
        END) AS studer_temperature_l3,
    max(
        CASE
            WHEN (v.attr_name = 'battery_voltage'::text) THEN v.val
            ELSE NULL::double precision
        END) AS battery_voltage,
    max(
        CASE
            WHEN (v.attr_name = 'battery_current'::text) THEN v.val
            ELSE NULL::double precision
        END) AS battery_current,
    max(
        CASE
            WHEN (v.attr_name = 'battery_state_of_charge'::text) THEN v.val
            ELSE NULL::double precision
        END) AS battery_state_of_charge,
    max(
        CASE
            WHEN (v.attr_name = 'battery_temperature'::text) THEN v.val
            ELSE NULL::double precision
        END) AS battery_temperature,
    max(
        CASE
            WHEN (v.attr_name = 'solar_power'::text) THEN v.val
            ELSE NULL::double precision
        END) AS solar_power,
    max(
        CASE
            WHEN (v.attr_name = 'xt_dbg1'::text) THEN v.val
            ELSE NULL::double precision
        END) AS xt_dbg1,
    max(
        CASE
            WHEN (v.attr_name = 'bsp_loce'::text) THEN v.val
            ELSE NULL::double precision
        END) AS bsp_loce,
    max(
        CASE
            WHEN (v.attr_name = 'sys_msg'::text) THEN v.val
            ELSE NULL::double precision
        END) AS sys_msg,
    max(
        CASE
            WHEN (v.attr_name = 'sys_scom_err'::text) THEN v.val
            ELSE NULL::double precision
        END) AS sys_scom_err,
    max(
        CASE
            WHEN (v.attr_name = 'vt_psom_1'::text) THEN v.val
            ELSE NULL::double precision
        END) AS vt_psom_1,
    max(
        CASE
            WHEN (v.attr_name = 'vt_psom_all'::text) THEN v.val
            ELSE NULL::double precision
        END) AS vt_psom_all,
    max(
        CASE
            WHEN (v.attr_name = 'vt_mode'::text) THEN v.val
            ELSE NULL::double precision
        END) AS vt_mode,
    max(
        CASE
            WHEN (v.attr_name = 'vt_tp1m'::text) THEN v.val
            ELSE NULL::double precision
        END) AS vt_tp1m,
    max(
        CASE
            WHEN (v.attr_name = 'vt_upvm'::text) THEN v.val
            ELSE NULL::double precision
        END) AS vt_upvm,
    max(
        CASE
            WHEN (v.attr_name = 'vt_ibam'::text) THEN v.val
            ELSE NULL::double precision
        END) AS vt_ibam,
    max(
        CASE
            WHEN (v.attr_name = 'vt_ubam'::text) THEN v.val
            ELSE NULL::double precision
        END) AS vt_ubam,
    max(
        CASE
            WHEN (v.attr_name = 'vt_phas'::text) THEN v.val
            ELSE NULL::double precision
        END) AS vt_phas,
    max(
        CASE
            WHEN (v.attr_name = 'vt_rme'::text) THEN v.val
            ELSE NULL::double precision
        END) AS vt_rme,
    max(
        CASE
            WHEN (v.attr_name = 'vt_aux_1'::text) THEN v.val
            ELSE NULL::double precision
        END) AS vt_aux_1,
    max(
        CASE
            WHEN (v.attr_name = 'vt_aux_2'::text) THEN v.val
            ELSE NULL::double precision
        END) AS vt_aux_2
   FROM (( SELECT DISTINCT vals.id,
            vals.date_time
           FROM vals) v0
     LEFT JOIN vals v ON (((v.id = v0.id) AND (v.date_time = v0.date_time))))
  GROUP BY v0.id, v0.date_time;


ALTER VIEW public.v_studer OWNER TO postgres;

--
-- Name: artefact id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.artefact ALTER COLUMN id SET DEFAULT nextval('public.artefact_id_seq'::regclass);


--
-- Name: artefactlogattributevalue id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.artefactlogattributevalue ALTER COLUMN id SET DEFAULT nextval('public.artefactlogattributevalue_id_seq'::regclass);


--
-- Name: artefactloginstance id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.artefactloginstance ALTER COLUMN id SET DEFAULT nextval('public.artefactloginstance_id_seq'::regclass);


--
-- Name: artefacttype id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.artefacttype ALTER COLUMN id SET DEFAULT nextval('public.artefacttype_id_seq'::regclass);


--
-- Name: artefacttypeattribute id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.artefacttypeattribute ALTER COLUMN id SET DEFAULT nextval('public.artefacttypeattribute_id_seq'::regclass);


--
-- Name: panel id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.panel ALTER COLUMN id SET DEFAULT nextval('public.panel_id_seq'::regclass);


--
-- Name: panelgroup id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.panelgroup ALTER COLUMN id SET DEFAULT nextval('public.panelgroup_id_seq'::regclass);


--
-- Name: panelproduction id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.panelproduction ALTER COLUMN id SET DEFAULT nextval('public.panelproduction_id_seq'::regclass);


--
-- Name: solarsite id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.solarsite ALTER COLUMN id SET DEFAULT nextval('public.solarsite_id_seq'::regclass);


--
-- Name: artefact artefact_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.artefact
    ADD CONSTRAINT artefact_pkey PRIMARY KEY (id);


--
-- Name: artefact artefact_site_id_artefact_type_id_artefact_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.artefact
    ADD CONSTRAINT artefact_site_id_artefact_type_id_artefact_code_key UNIQUE (site_id, artefact_type_id, artefact_code);


--
-- Name: artefactlogattributevalue artefactlogattributevalue_artefact_log_instance_id_artefact_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.artefactlogattributevalue
    ADD CONSTRAINT artefactlogattributevalue_artefact_log_instance_id_artefact_key UNIQUE (artefact_log_instance_id, artefact_type_attribute_id);


--
-- Name: artefactlogattributevalue artefactlogattributevalue_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.artefactlogattributevalue
    ADD CONSTRAINT artefactlogattributevalue_pkey PRIMARY KEY (id);


--
-- Name: artefactloginstance artefactloginstance_artefact_id_ts_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.artefactloginstance
    ADD CONSTRAINT artefactloginstance_artefact_id_ts_key UNIQUE (artefact_id, ts);


--
-- Name: artefactloginstance artefactloginstance_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.artefactloginstance
    ADD CONSTRAINT artefactloginstance_pkey PRIMARY KEY (id);


--
-- Name: artefacttype artefacttype_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.artefacttype
    ADD CONSTRAINT artefacttype_code_key UNIQUE (code);


--
-- Name: artefacttype artefacttype_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.artefacttype
    ADD CONSTRAINT artefacttype_pkey PRIMARY KEY (id);


--
-- Name: artefacttypeattribute artefacttypeattribute_artefact_type_id_attribute_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.artefacttypeattribute
    ADD CONSTRAINT artefacttypeattribute_artefact_type_id_attribute_name_key UNIQUE (artefact_type_id, attribute_name);


--
-- Name: artefacttypeattribute artefacttypeattribute_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.artefacttypeattribute
    ADD CONSTRAINT artefacttypeattribute_pkey PRIMARY KEY (id);


--
-- Name: enphase_panel_production enphase_panel_production_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.enphase_panel_production
    ADD CONSTRAINT enphase_panel_production_pkey PRIMARY KEY (id);


--
-- Name: enphase enphase_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.enphase
    ADD CONSTRAINT enphase_pkey PRIMARY KEY (id);


--
-- Name: location location_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.location
    ADD CONSTRAINT location_pkey PRIMARY KEY (locationid);


--
-- Name: open_weather open_weather_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.open_weather
    ADD CONSTRAINT open_weather_pkey PRIMARY KEY (id);


--
-- Name: panel panel_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.panel
    ADD CONSTRAINT panel_pkey PRIMARY KEY (id);


--
-- Name: panel panel_site_id_vendor_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.panel
    ADD CONSTRAINT panel_site_id_vendor_id_key UNIQUE (site_id, vendor_id);


--
-- Name: panelgroup panelgroup_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.panelgroup
    ADD CONSTRAINT panelgroup_pkey PRIMARY KEY (id);


--
-- Name: panelgroup panelgroup_site_id_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.panelgroup
    ADD CONSTRAINT panelgroup_site_id_name_key UNIQUE (site_id, name);


--
-- Name: panelproduction panelproduction_panel_id_date_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.panelproduction
    ADD CONSTRAINT panelproduction_panel_id_date_key UNIQUE (panel_id, date);


--
-- Name: panelproduction panelproduction_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.panelproduction
    ADD CONSTRAINT panelproduction_pkey PRIMARY KEY (id);


--
-- Name: solarsite solarsite_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.solarsite
    ADD CONSTRAINT solarsite_pkey PRIMARY KEY (id);


--
-- Name: solarsite solarsite_site_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.solarsite
    ADD CONSTRAINT solarsite_site_code_key UNIQUE (site_code);


--
-- Name: studer studer_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.studer
    ADD CONSTRAINT studer_pkey PRIMARY KEY (id);


--
-- Name: artefact artefact_artefact_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.artefact
    ADD CONSTRAINT artefact_artefact_type_id_fkey FOREIGN KEY (artefact_type_id) REFERENCES public.artefacttype(id);


--
-- Name: artefact artefact_site_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.artefact
    ADD CONSTRAINT artefact_site_id_fkey FOREIGN KEY (site_id) REFERENCES public.solarsite(id);


--
-- Name: artefactlogattributevalue artefactlogattributevalue_artefact_log_instance_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.artefactlogattributevalue
    ADD CONSTRAINT artefactlogattributevalue_artefact_log_instance_id_fkey FOREIGN KEY (artefact_log_instance_id) REFERENCES public.artefactloginstance(id);


--
-- Name: artefactlogattributevalue artefactlogattributevalue_artefact_type_attribute_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.artefactlogattributevalue
    ADD CONSTRAINT artefactlogattributevalue_artefact_type_attribute_id_fkey FOREIGN KEY (artefact_type_attribute_id) REFERENCES public.artefacttypeattribute(id);


--
-- Name: artefactloginstance artefactloginstance_artefact_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.artefactloginstance
    ADD CONSTRAINT artefactloginstance_artefact_id_fkey FOREIGN KEY (artefact_id) REFERENCES public.artefact(id);


--
-- Name: artefacttypeattribute artefacttypeattribute_artefact_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.artefacttypeattribute
    ADD CONSTRAINT artefacttypeattribute_artefact_type_id_fkey FOREIGN KEY (artefact_type_id) REFERENCES public.artefacttype(id);


--
-- Name: panel panel_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.panel
    ADD CONSTRAINT panel_group_id_fkey FOREIGN KEY (group_id) REFERENCES public.panelgroup(id);


--
-- Name: panel panel_site_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.panel
    ADD CONSTRAINT panel_site_id_fkey FOREIGN KEY (site_id) REFERENCES public.solarsite(id);


--
-- Name: panelgroup panelgroup_site_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.panelgroup
    ADD CONSTRAINT panelgroup_site_id_fkey FOREIGN KEY (site_id) REFERENCES public.solarsite(id);


--
-- Name: panelproduction panelproduction_panel_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.panelproduction
    ADD CONSTRAINT panelproduction_panel_id_fkey FOREIGN KEY (panel_id) REFERENCES public.panel(id);


--
-- Name: panelproduction panelproduction_site_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.panelproduction
    ADD CONSTRAINT panelproduction_site_id_fkey FOREIGN KEY (site_id) REFERENCES public.solarsite(id);


--
-- PostgreSQL database dump complete
--

\unrestrict OFt7EcrBHOUaSlqo99bhA3PqIFOHfQa9goxJiKhsdg9FDU55wcV7jzHryTl3d6K

