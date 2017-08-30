USE test_db;

DROP TABLE IF EXISTS User;
CREATE TABLE User (
	username varchar(20) PRIMARY KEY,
	firstname varchar(20),
	lastname varchar(20),
	password varchar(20),
	email varchar(40)
);

DROP TABLE IF EXISTS Album;
CREATE TABLE Album (
	albumid int PRIMARY KEY AUTO_INCREMENT,
	title varchar(50),
	created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	lastupdated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	username varchar(20),
	FOREIGN KEY (username) REFERENCES User(username)
);


DROP TABLE IF EXISTS Photo;
CREATE TABLE Photo (
	picid varchar(40) PRIMARY KEY,
	format char(3),
	date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

DROP TABLE IF EXISTS Contain;
CREATE TABLE Contain (
	sequencenum int NOT NULL, #START FROM 0
	albumid int,
	picid varchar(40),
	caption varchar(255),
	PRIMARY KEY (sequencenum),
	FOREIGN KEY (albumid) REFERENCES Album(albumid),
	FOREIGN KEY (picid) REFERENCES Photo(picid)
);

ALTER table Contain AUTO_INCREMENT = 0;

