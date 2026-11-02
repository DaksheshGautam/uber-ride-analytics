-- Dialect: SQLite 3.25+ (window functions). Grain: source booking row.
SELECT CASE WHEN ride_distance<10 THEN '01 | <10' WHEN ride_distance<25 THEN '02 | 10-24.99' ELSE '03 | >=25' END distance_band,
 COUNT(*) completed,ROUND(AVG(completed_value),2) avg_value,ROUND(SUM(completed_value)/SUM(completed_distance),2) weighted_value_per_distance
 FROM bookings WHERE is_completed=1 GROUP BY distance_band ORDER BY distance_band;
