-- Dialect: SQLite 3.25+ (window functions). Grain: source booking row.
SELECT status,failure_reason,COUNT(*) bookings,
 ROUND(100.0*COUNT(*)/SUM(COUNT(*)) OVER(PARTITION BY status),2) pct_within_status,
 ROUND(100.0*COUNT(*)/(SELECT SUM(is_failed) FROM bookings),2) pct_all_unsuccessful FROM bookings WHERE is_failed=1 GROUP BY status,failure_reason ORDER BY bookings DESC;
