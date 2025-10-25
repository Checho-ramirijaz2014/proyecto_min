-- AJUSTAR LOS PATHS AL EJECUTAR EL CÓDIGO SQL, TUVE QUE MOVERLOS A UN LADO PÚBLICO DEL COMPUTADOR
-- YA QUE PGADMIN4 ME ODIA. 

-- Tabla Temporal de kaggle
DROP TABLE IF EXISTS csv_kaggle;
CREATE TEMP TABLE csv_kaggle(
	appid int,
    nombre varchar(300),
    release_date date,
    english boolean,
    developer varchar(300),
    publisher varchar(300),
    platforms varchar(300),
    required_age int,
    categories varchar(300),
    genres varchar(300),
    steamspy_tags varchar(300),
    achievements int,
    positive_ratings int,
    negative_ratings int,
    average_playtime float,
    median_playtime float,
    owners varchar(300),
    price float
);

-- Llena la tabla con los csv
COPY csv_kaggle FROM 'C:\Users\Public\Quiero acceder\datos\steam\steam.csv' DELIMITER ',' CSV HEADER;


-- Cosas de gamalytic
DROP TABLE IF EXISTS csv_gamalytic;
CREATE TEMP TABLE csv_gamalytic(
	steamId int,
    id int,
    nombre varchar(200),
    copiesSold int,
    revenue bigint,
    unreleased varchar(5),
    earlyAccess varchar(5),
    firstReleaseDate varchar(40),
    releaseDate varchar(40),
    price float,
    developers varchar(400),
    publishers varchar(400),
    publisherClass varchar(10),
    reviewScore int,
    genres varchar(400)
);

-- Llena la tabla con los csv

COPY csv_gamalytic FROM 'C:\Users\Public\Quiero acceder\datos\gamalytic.csv' DELIMITER ',' CSV HEADER;

DROP TABLE IF EXISTS csv_final;
CREATE TEMP TABLE csv_final(
	appid int,
    nombre varchar(200),
    release_date date,
    english boolean,
    developer varchar(300),
    publisher varchar(300),
    platforms varchar(300),
    required_age int,
    categories varchar(300),
    genres varchar(300),
    steamspy_tags varchar(300),
    achievements int,
    positive_ratings int,
    negative_ratings int,
    average_playtime float,
    median_playtime float,
    owners varchar(300),
    price float,
    copiesSold int,
    revenue bigint,
    unreleased varchar(5),
    earlyAccess varchar(5),
    firstReleaseDate varchar(40),
    reviewScore int
);

INSERT INTO csv_final (appid, nombre, release_date, english, developer, publisher, platforms, required_age, categories,
    				   genres, steamspy_tags, achievements, positive_ratings, negative_ratings, average_playtime, median_playtime,
    				   owners, price, copiesSold, revenue, unreleased, earlyAccess, firstReleaseDate, reviewScore)
	(SELECT appid, ck.nombre, release_date, english, developer, publisher, platforms, required_age, categories,
    		 ck.genres, steamspy_tags, achievements, positive_ratings, negative_ratings, average_playtime, median_playtime,
    		 owners, ck.price, copiesSold, revenue, unreleased, earlyAccess, firstReleaseDate, reviewScore
	FROM csv_kaggle as ck, csv_gamalytic as cg
	WHERE ck.appid = cg.steamId);


COPY csv_final TO 'C:\Users\Public\Quiero acceder\datos\datos.csv' DELIMITER ',' CSV HEADER;