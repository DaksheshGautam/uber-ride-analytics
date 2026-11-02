-- Dialect: SQLite 3.25+ (window functions). Grain: source booking row.
SELECT SUM(CASE WHEN (status='Cancelled by Customer')<>COALESCE(customer_cancel_flag,0) THEN 1 ELSE 0 END) customer_flag_mismatches,
 SUM(CASE WHEN (status='Cancelled by Driver')<>COALESCE(driver_cancel_flag,0) THEN 1 ELSE 0 END) driver_flag_mismatches,
 SUM(CASE WHEN (status='Incomplete')<>COALESCE(incomplete_flag,0) THEN 1 ELSE 0 END) incomplete_flag_mismatches FROM bookings;
