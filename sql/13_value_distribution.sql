-- Dialect: SQLite 3.25+ (window functions). Grain: source booking row.
SELECT CASE WHEN completed_value<250 THEN '01 | <250' WHEN completed_value<500 THEN '02 | 250-499'
 WHEN completed_value<1000 THEN '03 | 500-999' ELSE '04 | >=1000' END value_band,COUNT(*) completed,SUM(completed_value) completed_value
 FROM bookings WHERE is_completed=1 GROUP BY value_band ORDER BY value_band;
