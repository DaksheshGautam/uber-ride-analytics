-- Dialect: SQLite 3.25+ (window functions). Grain: source booking row.
SELECT COUNT(*) AS bookings, SUM(is_completed) AS completed,
 ROUND(100.0*SUM(is_completed)/COUNT(*),2) AS completion_pct,
 SUM(is_cancelled) AS cancellations, SUM(is_failed) AS unsuccessful,
 SUM(completed_value) AS completed_booking_value,
 ROUND(AVG(completed_value),2) AS completed_avg_booking_value,
 ROUND(AVG(completed_distance),2) AS completed_avg_distance,
 ROUND(AVG(CASE WHEN is_completed=1 THEN avg_vtat END),2) AS completed_avg_vtat,
 ROUND(AVG(CASE WHEN is_completed=1 THEN avg_ctat END),2) AS completed_avg_ctat,
 ROUND(AVG(driver_rating),3) AS avg_driver_rating, ROUND(AVG(customer_rating),3) AS avg_customer_rating
 FROM bookings;
