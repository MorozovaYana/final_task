drop table if exists entries;
create table entries (
  id serial primary key not null,
  date timestamp with time zone not null default now(),
  title varchar(80) not null,
  content text not null
);


-- AIRLINE TABLES

DROP TABLE IF EXISTS bookings CASCADE;
DROP TABLE IF EXISTS flights CASCADE;
DROP TABLE IF EXISTS logs CASCADE;

CREATE TABLE flights (
    id SERIAL PRIMARY KEY,
    flight_number VARCHAR(10),
    origin VARCHAR(50),
    destination VARCHAR(50),
    available_seats INT
);

CREATE TABLE bookings (
    id SERIAL PRIMARY KEY,
    passenger_name VARCHAR(50),
    flight_id INT REFERENCES flights(id),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE logs (
    id SERIAL PRIMARY KEY,
    log_message TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

---------------------------------------------------------
-- FUNCTION: записувати події у логи
---------------------------------------------------------

CREATE OR REPLACE FUNCTION log_event(msg TEXT)
RETURNS VOID AS $$
BEGIN
    INSERT INTO logs(log_message) VALUES (msg);
END;
$$ LANGUAGE plpgsql;

---------------------------------------------------------
-- TRIGGER FUNCTION: логувати створення бронювання
---------------------------------------------------------

CREATE OR REPLACE FUNCTION booking_created()
RETURNS TRIGGER AS $$
BEGIN
    PERFORM log_event('New booking for passenger ' || NEW.passenger_name);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

---------------------------------------------------------
-- TRIGGER: викликати лог при створенні бронювання
---------------------------------------------------------

CREATE TRIGGER trg_booking_created
AFTER INSERT ON bookings
FOR EACH ROW EXECUTE FUNCTION booking_created();

---------------------------------------------------------
-- PROCEDURE: створення бронювання
---------------------------------------------------------

CREATE OR REPLACE PROCEDURE make_booking(p_passenger VARCHAR, p_flight_id INT)
LANGUAGE plpgsql
AS $$
DECLARE
    seats INT;
BEGIN
    SELECT available_seats INTO seats FROM flights WHERE id = p_flight_id;

    IF seats <= 0 THEN
        RAISE EXCEPTION 'No available seats!';
    END IF;

    INSERT INTO bookings(passenger_name, flight_id)
    VALUES (p_passenger, p_flight_id);

    UPDATE flights
    SET available_seats = available_seats - 1
    WHERE id = p_flight_id;

    -- FIX here: call function using PERFORM
    PERFORM log_event('Procedure booking created for ' || p_passenger);
END;
$$;