-- Schema for PostgreSQL / Neon.
-- Compatible with the same logical structure as initdb.sql (SQLite).
-- Uses explicit types rather than SQLite-style type affinity.

DROP TABLE IF EXISTS ssa_names;

CREATE TABLE ssa_names (
    name    TEXT        NOT NULL,
    gender  CHAR(1)    NOT NULL,
    count   INTEGER    NOT NULL,
    year    INTEGER    NOT NULL
);

DROP TABLE IF EXISTS ssa_names_by_state;

CREATE TABLE ssa_names_by_state (
    state   CHAR(2)    NOT NULL,
    name    TEXT        NOT NULL,
    gender  CHAR(1)    NOT NULL,
    count   INTEGER    NOT NULL,
    year    INTEGER    NOT NULL
);
