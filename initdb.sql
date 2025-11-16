BEGIN TRANSACTION;

DROP TABLE IF EXISTS ssa_names;

CREATE TABLE ssa_names(
    name text,
    gender char,
    count integer,
    year integer
);

COMMIT;