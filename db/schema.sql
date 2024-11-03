-- SQL script for creating database schema

DROP TABLE IF EXISTS request_interaction;
DROP TABLE IF EXISTS rating_interaction;
DROP TABLE IF EXISTS exhibition;
DROP TABLE IF EXISTS request;
DROP TABLE IF EXISTS rating;
DROP TABLE IF EXISTS floor;
DROP TABLE IF EXISTS department;


CREATE TABLE department (
    department_id SMALLINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    department_name VARCHAR(100) NOT NULL
);

CREATE TABLE floor (
    floor_id SMALLINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    floor_name VARCHAR(100) NOT NULL
);

CREATE TABLE request (
    request_id SMALLINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    request_value SMALLINT NOT NULL CHECK (request_value IN (0, 1)),
    request_description VARCHAR(100)
);

CREATE TABLE rating (
    rating_id SMALLINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    rating_value SMALLINT NOT NULL CHECK (rating_value >= 0 AND rating_value <= 4),
    rating_description VARCHAR(100)
);

CREATE TABLE exhibition (
    exhibition_id SMALLINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    exhibition_name VARCHAR(100) NOT NULL,
    exhibition_description TEXT,
    department_id SMALLINT,
    floor_id SMALLINT,
    exhibition_start_date DATE,
    public_id TEXT UNIQUE NOT NULL,
    CONSTRAINT chk_exhibition_start_date CHECK (exhibition_start_date <= CURRENT_DATE),
    FOREIGN KEY (department_id) REFERENCES department(department_id),
    FOREIGN KEY (floor_id) REFERENCES floor(floor_id)
);

CREATE TABLE request_interaction (
    request_interaction_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    exhibition_id SMALLINT,
    request_id SMALLINT,
    event_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (exhibition_id) REFERENCES exhibition(exhibition_id),
    FOREIGN KEY (request_id) REFERENCES request(request_id)
);

CREATE TABLE rating_interaction (
    rating_interaction_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    exhibition_id SMALLINT,
    rating_id SMALLINT,
    event_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (exhibition_id) REFERENCES exhibition(exhibition_id),
    FOREIGN KEY (rating_id) REFERENCES rating(rating_id)
);

CREATE INDEX idx_exhibition_department_id ON exhibition(department_id);
CREATE INDEX idx_exhibition_floor_id ON exhibition(floor_id);
CREATE INDEX idx_request_interaction_exhibition_id ON request_interaction(exhibition_id);
CREATE INDEX idx_request_interaction_request_id ON request_interaction(request_id);
CREATE INDEX idx_rating_interaction_exhibition_id ON rating_interaction(exhibition_id);
CREATE INDEX idx_rating_interaction_rating_id ON rating_interaction(rating_id);

INSERT INTO rating (rating_value, rating_description)
VALUES 
    (0, 'Terrible'),
    (1, 'Bad'),
    (2, 'Neutral'),
    (3, 'Good'),
    (4, 'Amazing')
;

INSERT INTO request (request_value, request_description)
VALUES 
    (0, 'Assistance'),
    (1, 'Emergency')
;

INSERT INTO floor (floor_name) VALUES
('Vault'),
('1'),
('2'),
('3')
;

INSERT INTO department (department_name) VALUES
('Entomology'),
('Geology'),
('Paleontology'),
('Zoology'),
('Ecology')
;

INSERT INTO exhibition (public_id, exhibition_name, exhibition_start_date, exhibition_description, floor_id, department_id) VALUES
('EXH_01', 'Adaptation', '07/01/2019', 'How insect evolution has kept pace with an industrialised world.', 1, 1),
('EXH_00', 'Measureless to Man', '08/23/2021', 'An immersive 3D experience: delve deep into a previously-inaccessible cave system.', 2, 2),
('EXH_05', 'Thunder Lizards', '02/01/2023', 'How new research is making scientists rethink what dinosaurs really looked like.', 2, 3),
('EXH_02', 'The Crenshaw Collection', '03/03/2021', 'An exhibition of 18th Century watercolours, mostly focused on South American wildlife.', 4, 4),
('EXH_04', 'Our Polluted World', '05/12/2021', 'A hard-hitting exploration of humanity''s impact on the environment.', 4, 5),
('EXH_03', 'Cetacean Sensations', '07/01/2019', 'Whales: from ancient myth to critically endangered.', 2, 4)
;