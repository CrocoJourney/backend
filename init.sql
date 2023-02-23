-- Simule un create database if not exists car le create database if not exists n'existe pas en postgresql
SELECT 'CREATE DATABASE crocojourney' 
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'crocojourney');

alter database crocojourney set timezone to 'Europe/Paris';

select * from user;

GRANT ALL PRIVILEGES ON DATABASE crocojourney TO croco;
ALTER USER croco WITH PASSWORD 'crocojourneypassword';
ALTER DATABASE crocojourney OWNER TO croco;