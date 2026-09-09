-- ============================================================
-- Smart EV Charging Station Analytics System
-- Business Analytics Queries
-- ============================================================
USE ev_charging;

-- ------------------------------------------------------------
-- A. REVENUE ANALYTICS
-- ------------------------------------------------------------

-- A1. Which station generates the most revenue?
SELECT
    s.station_id,
    s.station_name,
    s.city,
    ROUND(SUM(cs.cost_inr), 2) AS total_revenue,
    COUNT(*) AS total_sessions
FROM charging_sessions cs
JOIN stations s ON cs.station_id = s.station_id
GROUP BY s.station_id, s.station_name, s.city
ORDER BY total_revenue DESC
LIMIT 10;

-- A2. Revenue by charger type
SELECT
    charger_type,
    ROUND(SUM(cost_inr), 2) AS total_revenue,
    ROUND(AVG(cost_inr), 2) AS avg_revenue_per_session,
    COUNT(*) AS sessions
FROM charging_sessions
GROUP BY charger_type
ORDER BY total_revenue DESC;

-- A3. Monthly revenue trend
SELECT
    DATE_FORMAT(start_time, '%Y-%m') AS month,
    ROUND(SUM(cost_inr), 2) AS monthly_revenue,
    COUNT(*) AS sessions
FROM charging_sessions
GROUP BY DATE_FORMAT(start_time, '%Y-%m')
ORDER BY month;

-- ------------------------------------------------------------
-- B. CUSTOMER ANALYTICS
-- ------------------------------------------------------------

-- B1. Customer type mix (Individual vs Fleet)
SELECT
    c.customer_type,
    COUNT(cs.session_id) AS sessions,
    ROUND(100.0 * COUNT(cs.session_id) / (SELECT COUNT(*) FROM charging_sessions), 2) AS pct_of_sessions
FROM charging_sessions cs
JOIN customers c ON cs.customer_id = c.customer_id
GROUP BY c.customer_type;

-- B2. Top 10 customers by total spend
SELECT
    cs.customer_id,
    c.customer_type,
    c.city,
    COUNT(*) AS sessions,
    ROUND(SUM(cs.cost_inr), 2) AS total_spend
FROM charging_sessions cs
JOIN customers c ON cs.customer_id = c.customer_id
GROUP BY cs.customer_id, c.customer_type, c.city
ORDER BY total_spend DESC
LIMIT 10;

-- B3. Customer segmentation using CASE (no ML — rule based)
SELECT
    segment,
    COUNT(*) AS num_customers,
    ROUND(AVG(total_spend), 2) AS avg_spend
FROM (
    SELECT
        cs.customer_id,
        COUNT(*) AS num_sessions,
        SUM(cs.cost_inr) AS total_spend,
        CASE
            WHEN COUNT(*) < 5 THEN 'Occasional'
            WHEN COUNT(*) <= 20 THEN 'Regular'
            ELSE 'Power User'
        END AS segment
    FROM charging_sessions cs
    GROUP BY cs.customer_id
) AS customer_summary
GROUP BY segment
ORDER BY avg_spend DESC;

-- ------------------------------------------------------------
-- C. CHARGER ANALYTICS
-- ------------------------------------------------------------

-- C1. Most-used charger type
SELECT
    charger_type,
    COUNT(*) AS sessions,
    ROUND(AVG(charging_duration_minutes), 1) AS avg_duration_min
FROM charging_sessions
GROUP BY charger_type
ORDER BY sessions DESC;

-- C2. Underutilized chargers (bottom 10 by session count, active only)
SELECT
    ch.charger_id,
    ch.station_id,
    ch.charger_type,
    ch.power_kw,
    COUNT(cs.session_id) AS sessions_handled
FROM chargers ch
LEFT JOIN charging_sessions cs ON ch.charger_id = cs.charger_id
WHERE ch.status = 'Active'
GROUP BY ch.charger_id, ch.station_id, ch.charger_type, ch.power_kw
HAVING sessions_handled < 100
ORDER BY sessions_handled ASC
LIMIT 10;

-- ------------------------------------------------------------
-- D. STATION ANALYTICS
-- ------------------------------------------------------------

-- D1. Busiest stations
SELECT
    s.station_id,
    s.station_name,
    COUNT(cs.session_id) AS total_sessions
FROM stations s
JOIN charging_sessions cs ON s.station_id = cs.station_id
GROUP BY s.station_id, s.station_name
ORDER BY total_sessions DESC
LIMIT 10;

-- D2. Peak charging hours (network-wide)
SELECT
    HOUR(start_time) AS hour_of_day,
    COUNT(*) AS sessions
FROM charging_sessions
GROUP BY HOUR(start_time)
ORDER BY sessions DESC;

-- D3. Stations with above-average utilization (subquery)
SELECT
    station_id,
    ROUND(AVG(station_utilization), 2) AS avg_utilization
FROM charging_sessions
GROUP BY station_id
HAVING AVG(station_utilization) > (
    SELECT AVG(station_utilization) FROM charging_sessions
)
ORDER BY avg_utilization DESC;

-- ------------------------------------------------------------
-- E. QUEUE / WAIT-TIME ANALYTICS
-- ------------------------------------------------------------

-- E1. Hours with the longest average wait time
SELECT
    hour,
    ROUND(AVG(avg_wait_time_minutes), 1) AS avg_wait_minutes,
    ROUND(AVG(vehicles_waiting), 1) AS avg_vehicles_waiting
FROM queue_logs
GROUP BY hour
ORDER BY avg_wait_minutes DESC;

-- ------------------------------------------------------------
-- F. PROFITABILITY ANALYTICS
-- ------------------------------------------------------------

-- F1. Revenue vs electricity cost vs gross margin, by station
SELECT
    s.station_id,
    s.station_name,
    ROUND(rev.total_revenue, 2)      AS total_revenue,
    ROUND(elec.total_elec_cost, 2)   AS total_electricity_cost,
    ROUND(rev.total_revenue - elec.total_elec_cost, 2) AS gross_margin
FROM stations s
JOIN (
    SELECT station_id, SUM(cost_inr) AS total_revenue
    FROM charging_sessions
    GROUP BY station_id
) rev ON s.station_id = rev.station_id
JOIN (
    SELECT station_id, SUM(electricity_cost_inr) AS total_elec_cost
    FROM electricity_cost
    GROUP BY station_id
) elec ON s.station_id = elec.station_id
ORDER BY gross_margin DESC;

-- ------------------------------------------------------------
-- G. TIME-BASED ANALYTICS
-- ------------------------------------------------------------

-- G1. Weekday vs weekend session volume
SELECT
    CASE WHEN DAYOFWEEK(start_time) IN (1,7) THEN 'Weekend' ELSE 'Weekday' END AS day_type,
    COUNT(*) AS sessions,
    ROUND(AVG(cost_inr), 2) AS avg_revenue_per_session
FROM charging_sessions
GROUP BY day_type;

-- G2. Revenue by day of week
SELECT
    DAYNAME(start_time) AS day_of_week,
    COUNT(*) AS sessions,
    ROUND(SUM(cost_inr), 2) AS revenue
FROM charging_sessions
GROUP BY DAYNAME(start_time), DAYOFWEEK(start_time)
ORDER BY DAYOFWEEK(start_time);
