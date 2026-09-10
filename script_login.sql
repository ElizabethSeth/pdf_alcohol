-- Active: 1786649388369@@127.0.0.1@5432@mydb

create SCHEMA if not exists data;

create table data.login (
    id_key int NOT NULL PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_unique VARCHAR(255),
    login_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO data.login (email, password_unique)
VALUES 
    ('admin', '1234');
