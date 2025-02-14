CREATE DATABASE moviefinder;

use moviefinder

CREATE TABLE users (
    user_id BINARY(16) PRIMARY KEY,
    username VARCHAR(40) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(40) NOT NULL UNIQUE
);

CREATE TABLE movies (
    
)

DELIMITER $$

CREATE TRIGGER auto_id_on_insert
BEFORE INSERT ON users
FOR EACH ROW
BEGIN
    IF NEW.user_id IS NULL THEN
        SET NEW.user_id = UUID_TO_BIN(UUID());
    END IF;
END $$

DELIMITER ;

CREATE TABLE users_movies (
    users_id BINARY(16),
    movies_id INT,
    FOREIGN KEY users_id REFERENCES users(id) ON CASCADE DELETE,
    FOREIGN KEY movies_id REFERENCES movies(id) ON CASCADE DELETE,
    PRIMARY KEY (users_id, movies_id)
) 