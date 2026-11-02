-- Dialect: SQLite 3.25+ (window functions). Grain: source booking row.
SELECT CASE WHEN booking_id_reused=1 THEN 'Reused ID rows' ELSE 'Unique ID rows' END segment,
 COUNT(*) bookings,SUM(is_completed) completed,ROUND(100.0*SUM(is_completed)/COUNT(*),2) completion_pct,SUM(completed_value) completed_value FROM bookings GROUP BY booking_id_reused;
