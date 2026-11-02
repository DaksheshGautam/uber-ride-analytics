-- Dialect: SQLite 3.25+ (window functions). Grain: source booking row.
SELECT vtat_band,COUNT(*) bookings,SUM(is_completed) completed,
 ROUND(100.0*SUM(is_completed)/COUNT(*),2) completion_pct FROM bookings GROUP BY vtat_band ORDER BY vtat_band;
