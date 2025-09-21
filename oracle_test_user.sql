ALTER SESSION SET CONTAINER = CDB$ROOT;

-- run as a DBA
CREATE USER c##ci_user IDENTIFIED BY "5ZA1V$D4MCKLW" QUOTA UNLIMITED ON USERS;
GRANT CREATE SESSION TO c##ci_user;
GRANT CREATE TABLE, CREATE SEQUENCE, CREATE VIEW, CREATE PROCEDURE TO c##ci_user;
GRANT CREATE TRIGGER TO c##ci_user;

-- optional: allow dropping/creating during tests
GRANT DROP ANY TABLE TO c##ci_user;   -- or tightly scope to schema if possible
