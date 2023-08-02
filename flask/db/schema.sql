CREATE TABLE IF NOT EXISTS Page (
    path    TEXT PRIMARY KEY,
    name    TEXT NOT NULL,
    content TEXT
);

CREATE TABLE IF NOT EXISTS User (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    -- Поле UNIQUE может быть NULL, причем NULL может встречаться
    -- несколько раз
    email   TEXT NOT NULL UNIQUE,
    passwd  TEXT NOT NULL,
    time    INTEGER NOT NULL,
    picture BLOB DEFAULT NULL
);

CREATE TABLE IF NOT EXISTS Info (
    -- NOT NULL подразумевается для PRIMARY KEY
    user_id INTEGER PRIMARY KEY,
    is_male BOOLEAN NOT NULL,
    -- Родительскиая строка должна быть UNIQUE или PRIMARY KEY
    -- Поле внешнего ключа может быть NULL
    FOREIGN KEY (user_id) REFERENCES User (id)
);
