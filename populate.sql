delete from entries;

insert into entries(date, title, content)
values (now() - interval '10 days', 'First post!', 'This is my first post.  It is exciting!');

insert into entries(date, title, content)
values (now() - interval '1 day', 'I love Flask', 'I am finding Flask incredibly fun.');

insert into entries(title, content)
values ('Databases', 'My databases class is a lot of work, but I am enjoying it.');

insert into entries(title, content)
values ('About the Author', 'This Flask app was written by Yana Morozova.');



-- AIRLINE DEMO DATA

INSERT INTO flights (flight_number, origin, destination, available_seats)
VALUES
('PS101', 'Kyiv', 'Warsaw', 3),
('PS202', 'Lviv', 'Berlin', 2),
('PS303', 'Odessa', 'Paris', 1);