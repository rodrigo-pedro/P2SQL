CREATE TABLE public.prompts
(
    id serial,
    client_id character varying(100),
    session_id character varying(100),
    application character varying(150),
    datetime timestamp,
    prompt text,
    intermediate_steps text,
    final_answer text,
    sql_queries text [],
    model character varying(50),
    effective boolean,
    attack_type character varying(50),
    framework character varying(50),
    injected_prompt text,
    PRIMARY KEY (id)
);

ALTER TABLE IF EXISTS public.prompts
    OWNER to postgres;
