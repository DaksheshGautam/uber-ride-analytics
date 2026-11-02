-- Dialect: SQLite 3.25+ (window functions). Grain: source booking row.
SELECT booking_id,COUNT(*) rows,COUNT(DISTINCT customer_id) customers,COUNT(DISTINCT booking_date) dates,
 COUNT(DISTINCT status) statuses FROM bookings GROUP BY booking_id HAVING COUNT(*)>1 ORDER BY rows DESC,booking_id;
