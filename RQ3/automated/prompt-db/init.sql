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

CREATE TABLE public.new_prompts
(
    id serial,
    new_prompt text,
    original_prompt_id integer REFERENCES public.prompts(id),
    attack_type character varying(50),
    PRIMARY KEY (id)
);

ALTER TABLE IF EXISTS public.prompts
    OWNER to postgres;

ALTER TABLE IF EXISTS public.new_prompts
    OWNER to postgres;
