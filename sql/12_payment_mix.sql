-- Dialect: SQLite 3.25+ (window functions). Grain: source booking row.
SELECT payment_method,COUNT(*) completed,SUM(completed_value) completed_value,
 ROUND(AVG(completed_value),2) avg_completed_value,
 ROUND(100.0*COUNT(*)/(SELECT SUM(is_completed) FROM bookings),2) completed_share_pct
 FROM bookings WHERE is_completed=1 GROUP BY payment_method ORDER BY completed DESC;
