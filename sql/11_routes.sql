-- Dialect: SQLite 3.25+ (window functions). Grain: source booking row.
SELECT pickup,dropoff,COUNT(*) bookings,SUM(is_completed) completed,
 ROUND(100.0*SUM(is_completed)/COUNT(*),2) completion_pct,SUM(completed_value) completed_value
 FROM bookings GROUP BY pickup,dropoff HAVING COUNT(*)>=10 ORDER BY bookings DESC,pickup,dropoff;
