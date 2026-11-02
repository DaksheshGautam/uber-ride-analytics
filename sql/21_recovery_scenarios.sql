-- Dialect: SQLite 3.25+ (window functions). Grain: source booking row.
WITH base AS (SELECT COUNT(*) n,SUM(is_completed) c,AVG(completed_value) abv FROM bookings),
 scenarios AS (SELECT 1 pp UNION ALL SELECT 3 UNION ALL SELECT 5)
 SELECT pp AS completion_improvement_pp,ROUND(n*pp/100.0) additional_completed,
 ROUND(n*pp/100.0*abv,2) illustrative_additional_booking_value FROM base CROSS JOIN scenarios;
