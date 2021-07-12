FROM mysql:8

ADD tables.sql /docker-entrypoint-initdb.d/01_tables.sql
ADD data.sql /docker-entrypoint-initdb.d/02_tables.sql

