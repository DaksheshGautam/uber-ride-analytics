-- Dialect: SQLite 3.25+ (window functions). Grain: source booking row.
SELECT weekday_number,weekday,COUNT(*) bookings,COUNT(DISTINCT booking_date) observed_days,
 ROUND(1.0*COUNT(*)/COUNT(DISTINCT booking_date),2) bookings_per_day,ROUND(100.0*SUM(is_completed)/COUNT(*),2) completion_pct FROM bookings GROUP BY weekday_number,weekday ORDER BY weekday_number;
