BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "appointments" (
	"id"	INTEGER,
	"service_id"	INTEGER,
	"barber_id"	INTEGER,
	"customer_name"	TEXT NOT NULL,
	"customer_email"	TEXT,
	"customer_phone"	TEXT NOT NULL,
	"date"	TEXT NOT NULL,
	"time"	TEXT NOT NULL,
	"status"	TEXT DEFAULT 'pendiente',
	"created_at"	TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("barber_id") REFERENCES "barbers"("id"),
	FOREIGN KEY("service_id") REFERENCES "services"("id")
);
CREATE TABLE IF NOT EXISTS "barbers" (
	"id"	INTEGER,
	"name"	TEXT NOT NULL,
	"bio"	TEXT,
	"image_url"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "categories" (
	"id"	INTEGER,
	"name"	TEXT NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "services" (
	"id"	INTEGER,
	"category_id"	INTEGER,
	"name"	TEXT NOT NULL,
	"description"	TEXT,
	"price"	REAL NOT NULL,
	"duration"	INTEGER NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("category_id") REFERENCES "categories"("id")
);
INSERT INTO "barbers" VALUES (1,'Oscar Rosario','Especialista en degradados y estilo clásico.',NULL);
INSERT INTO "barbers" VALUES (2,'Jhensen Noboa','Experto en barbas ',NULL);
INSERT INTO "barbers" VALUES (3,'Illia Topuria','experto de las tijeras y cortes largos.',NULL);
INSERT INTO "barbers" VALUES (4,'Robert Anderson','Experto en cabello corto',NULL);
INSERT INTO "categories" VALUES (1,'Cortes de Pelo');
INSERT INTO "categories" VALUES (2,'Barba y Bigote');
INSERT INTO "categories" VALUES (3,'Combos Premium');
INSERT INTO "services" VALUES (1,1,'Corte Tradicional','Corte con tijera o máquina, incluye lavado y peinado.',500.0,30);
INSERT INTO "services" VALUES (2,1,'Corte Estilizado','Degradado moderno (Fade) con acabados detallados.',650.0,45);
INSERT INTO "services" VALUES (3,2,'Perfilado de Barba','Afeitado con toalla caliente y delineado.',300.0,20);
INSERT INTO "services" VALUES (4,3,'Combo Los Muchachos','Corte premium + Barba completa + Facial rápido.',1200.0,75);
COMMIT;
