DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS gruppi;
DROP TABLE IF EXISTS componenti;
DROP TABLE IF EXISTS decodifica;
DROP TABLE IF EXISTS post;



CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE post (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  author_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  FOREIGN KEY (author_id) REFERENCES user (id)
);


CREATE TABLE gruppi (
    id integer NOT NULL PRIMARY KEY AUTOINCREMENT, 
    codice varchar(50) NOT NULL, 
    descrizione varchar(50) NOT NULL, 
    ordinamento integer NOT NULL, 
    topic varchar(10) NOT NULL, 
    modifica bool NOT NULL
    section varchar(10) NOT NULL,
);



CREATE TABLE componenti (
    id integer NOT NULL PRIMARY KEY AUTOINCREMENT, 
    codice varchar(50) NOT NULL, 
    descrizione varchar(50) NOT NULL, 
    ordinamento integer NOT NULL, 
    tipo varchar(20) NOT NULL, 
    livello integer NOT NULL, 
    modifica bool NOT NULL, 
    gruppo_id integer NOT NULL ,
    FOREIGN KEY (gruppo_id) REFERENCES gruppi (id) 
);

CREATE TABLE decodifica (
    id integer NOT NULL PRIMARY KEY AUTOINCREMENT, 
    codice varchar(50) NOT NULL, 
    valore varchar(10) NOT NULL, 
    descrizione varchar(50) NOT NULL
);





