
create SCHEMA if not exists data;
create table data.login (
    id_key primary key ,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_unique VARCHAR(255),
    login_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO data.login (email, password_unique)
VALUES 
    ('creator@example.com', '1234'),
    ('boss@example.com', 'boss_pass'),
    ('user@example.com', 'user_pass');