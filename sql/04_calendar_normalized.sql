-- Dialect: SQLite 3.25+ (window functions). Grain: source booking row.
SELECT b.month,COUNT(*) bookings,COUNT(DISTINCT b.booking_date) observed_days,
 ROUND(1.0*COUNT(*)/COUNT(DISTINCT b.booking_date),2) bookings_per_observed_day FROM bookings b GROUP BY b.month ORDER BY b.month;
