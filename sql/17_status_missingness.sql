-- Dialect: SQLite 3.25+ (window functions). Grain: source booking row.
SELECT status,COUNT(*) rows,COUNT(avg_vtat) vtat_observations,COUNT(avg_ctat) ctat_observations,
 COUNT(booking_value) value_observations,COUNT(ride_distance) distance_observations,COUNT(driver_rating) driver_rating_observations,
 COUNT(payment_method) payment_observations FROM bookings GROUP BY status;
