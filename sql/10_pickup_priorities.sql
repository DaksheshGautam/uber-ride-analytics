-- Dialect: SQLite 3.25+ (window functions). Grain: source booking row.
SELECT pickup,COUNT(*) bookings,SUM(is_failed) unsuccessful,
 SUM(CASE WHEN status='No Driver Found' THEN 1 ELSE 0 END) no_driver,
 ROUND(100.0*SUM(is_failed)/COUNT(*),2) unsuccessful_pct,
 ROUND(100.0*SUM(CASE WHEN status='No Driver Found' THEN 1 ELSE 0 END)/COUNT(*),2) no_driver_pct
 FROM bookings GROUP BY pickup HAVING COUNT(*)>=500 ORDER BY unsuccessful DESC;
