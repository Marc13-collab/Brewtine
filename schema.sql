CREATE TABLE IF NOT EXISTS habits (
    id serial PRIMARY KEY,
    name text NOT NULL CHECK (char_length(name) BETWEEN 1 AND 60),
    weekly_target integer NOT NULL DEFAULT 7 CHECK (weekly_target BETWEEN 1 AND 7),
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS check_ins (
    id serial PRIMARY KEY,
    habit_id integer NOT NULL REFERENCES habits (id) ON DELETE CASCADE,
    check_date date NOT NULL,
    UNIQUE (habit_id, check_date)
);
