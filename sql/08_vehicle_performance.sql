-- Dialect: SQLite 3.25+ (window functions). Grain: source booking row.
SELECT vehicle_type,COUNT(*) bookings,SUM(is_completed) completed,ROUND(100.0*SUM(is_completed)/COUNT(*),2) completion_pct,
 SUM(completed_value) completed_value,ROUND(AVG(completed_value),2) avg_completed_value,ROUND(AVG(completed_distance),2) avg_completed_distance,
 ROUND(AVG(CASE WHEN is_completed=1 THEN avg_vtat END),2) completed_avg_vtat,ROUND(AVG(driver_rating),3) driver_rating
 FROM bookings GROUP BY vehicle_type ORDER BY completed_value DESC;
