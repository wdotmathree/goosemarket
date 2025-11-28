-- WARNING: This schema is for context only and is not meant to be run.
-- Table order and constraints may not be valid for execution.

CREATE TABLE public.poll_tags (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL UNIQUE,
  poll_id bigint NOT NULL,
  tag_id bigint NOT NULL,
  CONSTRAINT poll_tags_pkey PRIMARY KEY (id),
  CONSTRAINT poll_tags_poll_id_fkey FOREIGN KEY (poll_id) REFERENCES public.polls(id),
  CONSTRAINT poll_tags_tag_id_fkey FOREIGN KEY (tag_id) REFERENCES public.tags(id)
);
CREATE TABLE public.polls (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  title text NOT NULL,
  description text NOT NULL,
  created_at timestamp with time zone NOT NULL,
  ends_at timestamp with time zone,
  public boolean NOT NULL DEFAULT false,
  creator bigint NOT NULL,
  outcome boolean,
  deleted boolean NOT NULL DEFAULT false,
  CONSTRAINT polls_pkey PRIMARY KEY (id),
  CONSTRAINT polls_creator_fkey FOREIGN KEY (creator) REFERENCES public.profiles(id)
);
CREATE TABLE public.profiles (
  auth_id uuid NOT NULL,
  current_streak smallint DEFAULT '1'::smallint,
  balance bigint DEFAULT '5000'::bigint,
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  username text UNIQUE,
  email text NOT NULL UNIQUE,
  admin boolean NOT NULL DEFAULT false,
  active boolean NOT NULL DEFAULT false,
  last_bonus date NOT NULL DEFAULT now(),
  CONSTRAINT profiles_pkey PRIMARY KEY (id),
  CONSTRAINT users_auth_id_fkey FOREIGN KEY (auth_id) REFERENCES auth.users(id)
);
CREATE TABLE public.tags (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL UNIQUE,
  name text NOT NULL UNIQUE,
  CONSTRAINT tags_pkey PRIMARY KEY (id)
);
CREATE TABLE public.trades (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL UNIQUE,
  poll_id bigint NOT NULL,
  user_id bigint NOT NULL,
  num_shares bigint NOT NULL CHECK (num_shares <> 0),
  outcome boolean NOT NULL,
  timestamp timestamp with time zone NOT NULL DEFAULT now(),
  share_price real NOT NULL,
  CONSTRAINT trades_pkey PRIMARY KEY (id),
  CONSTRAINT trades_poll_id_fkey FOREIGN KEY (poll_id) REFERENCES public.polls(id),
  CONSTRAINT trades_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.profiles(id)
);
CREATE TABLE public.user_tags (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL UNIQUE,
  tag_id bigint NOT NULL,
  user_id bigint NOT NULL,
  CONSTRAINT user_tags_pkey PRIMARY KEY (id),
  CONSTRAINT user_tags_tag_id_fkey FOREIGN KEY (tag_id) REFERENCES public.tags(id),
  CONSTRAINT user_tags_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.profiles(id)
);