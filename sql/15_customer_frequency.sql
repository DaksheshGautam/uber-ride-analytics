-- Dialect: SQLite 3.25+ (window functions). Grain: source booking row.
WITH c AS (SELECT customer_id,COUNT(*) bookings,SUM(is_completed) completed FROM bookings GROUP BY customer_id)
 SELECT bookings AS bookings_per_customer,COUNT(*) customers,SUM(bookings) booking_rows,SUM(completed) completed FROM c GROUP BY bookings ORDER BY bookings;
