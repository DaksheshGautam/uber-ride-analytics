-- Dialect: SQLite 3.25+ (window functions). Grain: source booking row.
SELECT c.booking_date,COUNT(b.booking_row_key) bookings,COALESCE(SUM(b.is_completed),0) completed,
 ROUND(100.0*SUM(b.is_completed)/NULLIF(COUNT(b.booking_row_key),0),2) completion_pct FROM calendar c LEFT JOIN bookings b USING(booking_date) GROUP BY c.booking_date ORDER BY c.booking_date;
