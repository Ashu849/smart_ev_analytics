-- ============================================================
-- Smart EV Charging Station Analytics System
-- Load CSV data into MySQL tables
-- ============================================================
-- NOTE: Run this from the MySQL client with --local-infile=1,
-- or adjust paths to match your machine. Order matters because
-- of foreign key dependencies (parents before children).
-- ============================================================

USE ev_charging;

SET GLOBAL local_infile = 1;

-- 1. Stations (no dependencies)
LOAD DATA LOCAL INFILE 'data/raw/stations.csv'
INTO TABLE stations
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

-- 2. Chargers (depends on stations)
LOAD DATA LOCAL INFILE 'data/raw/chargers.csv'
INTO TABLE chargers
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

-- 3. Customers (no dependencies)
LOAD DATA LOCAL INFILE 'data/raw/customers.csv'
INTO TABLE customers
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

-- 4. Vehicles (depends on customers)
LOAD DATA LOCAL INFILE 'data/raw/vehicles.csv'
INTO TABLE vehicles
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

-- 5. Charging sessions -- load the CLEANED file, not raw
--    (data/processed/ev_sessions_clean.csv has duplicates/nulls already handled)
LOAD DATA LOCAL INFILE 'data/raw/charging_sessions.csv'
INTO TABLE charging_sessions
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(session_id, customer_id, vehicle_id, station_id, charger_id, charger_type,
 start_time, end_time, initial_soc, target_soc, energy_consumed_kwh,
 charging_duration_minutes, station_utilization, queue_length, cost_inr,
 payment_method);

-- 6. Queue logs
LOAD DATA LOCAL INFILE 'data/raw/queue_logs.csv'
INTO TABLE queue_logs
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

-- 7. Electricity cost
LOAD DATA LOCAL INFILE 'data/raw/electricity_cost.csv'
INTO TABLE electricity_cost
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

-- Sanity check row counts
SELECT 'stations' AS tbl, COUNT(*) AS rows_loaded FROM stations
UNION ALL SELECT 'chargers', COUNT(*) FROM chargers
UNION ALL SELECT 'customers', COUNT(*) FROM customers
UNION ALL SELECT 'vehicles', COUNT(*) FROM vehicles
UNION ALL SELECT 'charging_sessions', COUNT(*) FROM charging_sessions
UNION ALL SELECT 'queue_logs', COUNT(*) FROM queue_logs
UNION ALL SELECT 'electricity_cost', COUNT(*) FROM electricity_cost;
