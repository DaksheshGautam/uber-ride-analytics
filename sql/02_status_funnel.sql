-- Dialect: SQLite 3.25+ (window functions). Grain: source booking row.
SELECT status, COUNT(*) AS bookings, ROUND(100.0*COUNT(*)/(SELECT COUNT(*) FROM bookings),2) AS share_pct,
 COUNT(booking_value) AS value_observations,SUM(booking_value) AS recorded_booking_value FROM bookings GROUP BY status ORDER BY bookings DESC;
