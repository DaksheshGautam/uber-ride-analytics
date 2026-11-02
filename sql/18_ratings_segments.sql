-- Dialect: SQLite 3.25+ (window functions). Grain: source booking row.
SELECT vehicle_type,COUNT(*) rated_completed,ROUND(AVG(driver_rating),3) driver_rating,
 ROUND(AVG(customer_rating),3) customer_rating,SUM(CASE WHEN driver_rating<4 THEN 1 ELSE 0 END) driver_ratings_below_4,
 ROUND(100.0*SUM(CASE WHEN driver_rating<4 THEN 1 ELSE 0 END)/COUNT(*),2) below_4_pct FROM bookings WHERE is_completed=1 GROUP BY vehicle_type ORDER BY driver_rating;
