-- ============================================================
-- Smart EV Charging Station Analytics System
-- Database Schema (MySQL)
-- ============================================================

CREATE DATABASE IF NOT EXISTS ev_charging;
USE ev_charging;

-- ------------------------------------------------------------
-- 1. STATIONS
-- ------------------------------------------------------------
DROP TABLE IF EXISTS stations;
CREATE TABLE stations (
    station_id      VARCHAR(10) PRIMARY KEY,
    station_name    VARCHAR(100) NOT NULL,
    city            VARCHAR(50),
    total_chargers  INT,
    latitude        DECIMAL(10,6),
    longitude       DECIMAL(10,6),
    opening_date    DATE
);

-- ------------------------------------------------------------
-- 2. CHARGERS
-- ------------------------------------------------------------
DROP TABLE IF EXISTS chargers;
CREATE TABLE chargers (
    charger_id      VARCHAR(10) PRIMARY KEY,
    station_id      VARCHAR(10),
    charger_type    VARCHAR(20),   -- AC / DC / DC_FAST
    power_kw        FLOAT,
    status          VARCHAR(20),   -- Active / Under Maintenance
    installed_date  DATE,
    FOREIGN KEY (station_id) REFERENCES stations(station_id)
);

-- ------------------------------------------------------------
-- 3. CUSTOMERS
-- ------------------------------------------------------------
DROP TABLE IF EXISTS customers;
CREATE TABLE customers (
    customer_id         VARCHAR(10) PRIMARY KEY,
    customer_type        VARCHAR(20),   -- Individual / Fleet
    city                 VARCHAR(50),
    registration_date    DATE
);

-- ------------------------------------------------------------
-- 4. VEHICLES
-- ------------------------------------------------------------
DROP TABLE IF EXISTS vehicles;
CREATE TABLE vehicles (
    vehicle_id            VARCHAR(10) PRIMARY KEY,
    customer_id           VARCHAR(10),
    vehicle_type          VARCHAR(30),
    vehicle_model         VARCHAR(50),
    battery_capacity_kwh  FLOAT,
    vehicle_age_years     INT,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- ------------------------------------------------------------
-- 5. CHARGING SESSIONS (main fact table)
-- ------------------------------------------------------------
DROP TABLE IF EXISTS charging_sessions;
CREATE TABLE charging_sessions (
    session_id                   INT PRIMARY KEY,
    customer_id                  VARCHAR(10),
    vehicle_id                   VARCHAR(10),
    station_id                   VARCHAR(10),
    charger_id                   VARCHAR(10),
    charger_type                 VARCHAR(20),
    start_time                   DATETIME,
    end_time                     DATETIME,
    initial_soc                  INT,
    target_soc                   INT,
    energy_consumed_kwh          FLOAT,
    charging_duration_minutes    FLOAT,
    station_utilization          FLOAT,
    queue_length                 INT,
    cost_inr                     FLOAT,
    payment_method                VARCHAR(20),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (vehicle_id)  REFERENCES vehicles(vehicle_id),
    FOREIGN KEY (station_id)  REFERENCES stations(station_id),
    FOREIGN KEY (charger_id)  REFERENCES chargers(charger_id),

    INDEX idx_station_time (station_id, start_time),
    INDEX idx_customer (customer_id)
);

-- ------------------------------------------------------------
-- 6. QUEUE LOGS
-- ------------------------------------------------------------
DROP TABLE IF EXISTS queue_logs;
CREATE TABLE queue_logs (
    queue_id                INT PRIMARY KEY,
    station_id               VARCHAR(10),
    log_date                 DATE,
    hour                      INT,
    vehicles_waiting         INT,
    avg_wait_time_minutes    FLOAT,
    FOREIGN KEY (station_id) REFERENCES stations(station_id)
);

-- ------------------------------------------------------------
-- 7. ELECTRICITY COST
-- ------------------------------------------------------------
DROP TABLE IF EXISTS electricity_cost;
CREATE TABLE electricity_cost (
    station_id                   VARCHAR(10),
    cost_date                    DATE,
    electricity_consumed_kwh     FLOAT,
    electricity_cost_inr         FLOAT,
    PRIMARY KEY (station_id, cost_date),
    FOREIGN KEY (station_id) REFERENCES stations(station_id)
);
