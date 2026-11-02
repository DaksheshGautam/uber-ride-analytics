-- Dialect: SQLite 3.25+ (window functions). Grain: source booking row.
SELECT weekday_number,weekday,hour,COUNT(*) bookings,ROUND(100.0*SUM(is_completed)/COUNT(*),2) completion_pct FROM bookings GROUP BY weekday_number,weekday,hour ORDER BY weekday_number,hour;
