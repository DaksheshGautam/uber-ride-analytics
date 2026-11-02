-- Dialect: SQLite 3.25+ (window functions). Grain: source booking row.
SELECT hour,COUNT(*) bookings,SUM(is_completed) completed,ROUND(100.0*SUM(is_completed)/COUNT(*),2) completion_pct,
 SUM(CASE WHEN status='No Driver Found' THEN 1 ELSE 0 END) no_driver,
 ROUND(AVG(CASE WHEN is_completed=1 THEN avg_vtat END),2) completed_avg_vtat FROM bookings GROUP BY hour ORDER BY hour;
