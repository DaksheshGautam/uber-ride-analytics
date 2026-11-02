# Queries run

Dialect: SQLite 3.25+; database: outputs/uber_analytics.sqlite. All 24 queries were executed by scripts/analyze.py. Full CSV results and hashes are in outputs/.

## 01_executive_kpis

```sql
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
```

Result: 1 rows. Preview (first 12 rows):

```csv
bookings,completed,completion_pct,cancellations,unsuccessful,completed_booking_value,completed_avg_booking_value,completed_avg_distance,completed_avg_vtat,completed_avg_ctat,avg_driver_rating,avg_customer_rating

150000,93000,62.0,37500,57000,47260574.0,508.18,26.0,8.51,30.03,4.231,4.405

```

## 02_status_funnel

```sql
-- Dialect: SQLite 3.25+ (window functions). Grain: source booking row.
SELECT status, COUNT(*) AS bookings, ROUND(100.0*COUNT(*)/(SELECT COUNT(*) FROM bookings),2) AS share_pct,
 COUNT(booking_value) AS value_observations,SUM(booking_value) AS recorded_booking_value FROM bookings GROUP BY status ORDER BY bookings DESC;
```

Result: 5 rows. Preview (first 12 rows):

```csv
status,bookings,share_pct,value_observations,recorded_booking_value

Completed,93000,62.0,93000,47260574.0

Cancelled by Driver,27000,18.0,0,

Cancelled by Customer,10500,7.0,0,

No Driver Found,10500,7.0,0,

Incomplete,9000,6.0,9000,4585609.0

```

## 03_monthly_trend

```sql
-- Dialect: SQLite 3.25+ (window functions). Grain: source booking row.
WITH m AS (SELECT month,COUNT(*) bookings,SUM(is_completed) completed,SUM(completed_value) completed_value,
 ROUND(100.0*SUM(is_completed)/COUNT(*),2) completion_pct FROM bookings GROUP BY month)
 SELECT *, ROUND(100.0*(bookings-LAG(bookings) OVER(ORDER BY month))/NULLIF(LAG(bookings) OVER(ORDER BY month),0),2) mom_bookings_pct FROM m ORDER BY month;
```

Result: 12 rows. Preview (first 12 rows):

```csv
month,bookings,completed,completed_value,completion_pct,mom_bookings_pct

2024-01,12861,7951,4001547.0,61.82,

2024-02,11927,7368,3756610.0,61.78,-7.26

2024-03,12719,7954,4174900.0,62.54,6.64

2024-04,12199,7632,3885255.0,62.56,-4.09

2024-05,12778,7905,3935207.0,61.86,4.75

2024-06,12440,7757,3964298.0,62.36,-2.65

2024-07,12897,7926,3961939.0,61.46,3.67

2024-08,12636,7780,3867753.0,61.57,-2.02

2024-09,12248,7542,3820536.0,61.58,-3.07

2024-10,12651,7905,4008403.0,62.49,3.29

2024-11,12394,7659,3938458.0,61.8,-2.03

2024-12,12250,7621,3945668.0,62.21,-1.16

```

## 04_calendar_normalized

```sql
-- Dialect: SQLite 3.25+ (window functions). Grain: source booking row.
SELECT b.month,COUNT(*) bookings,COUNT(DISTINCT b.booking_date) observed_days,
 ROUND(1.0*COUNT(*)/COUNT(DISTINCT b.booking_date),2) bookings_per_observed_day FROM bookings b GROUP BY b.month ORDER BY b.month;
```

Result: 12 rows. Preview (first 12 rows):

```csv
month,bookings,observed_days,bookings_per_observed_day

2024-01,12861,31,414.87

2024-02,11927,29,411.28

2024-03,12719,31,410.29

2024-04,12199,30,406.63

2024-05,12778,31,412.19

2024-06,12440,30,414.67

2024-07,12897,31,416.03

2024-08,12636,31,407.61

2024-09,12248,30,408.27

2024-10,12651,31,408.1

2024-11,12394,30,413.13

2024-12,12250,30,408.33

```

## 05_hour_demand

```sql
-- Dialect: SQLite 3.25+ (window functions). Grain: source booking row.
SELECT hour,COUNT(*) bookings,SUM(is_completed) completed,ROUND(100.0*SUM(is_completed)/COUNT(*),2) completion_pct,
 SUM(CASE WHEN status='No Driver Found' THEN 1 ELSE 0 END) no_driver,
 ROUND(AVG(CASE WHEN is_completed=1 THEN avg_vtat END),2) completed_avg_vtat FROM bookings GROUP BY hour ORDER BY hour;
```

Result: 24 rows. Preview (first 12 rows):

```csv
hour,bookings,completed,completion_pct,no_driver,completed_avg_vtat

0,1373,858,62.49,93,8.38

1,1360,828,60.88,110,8.31

2,1339,853,63.7,107,8.59

3,1383,860,62.18,99,8.47

4,1321,830,62.83,89,8.56

5,2786,1715,61.56,187,8.43

6,4160,2609,62.72,308,8.52

7,5450,3346,61.39,387,8.53

8,6861,4267,62.19,477,8.58

9,8234,5084,61.74,588,8.53

10,9577,5983,62.47,647,8.53

11,8390,5254,62.62,601,8.53

```

## 06_weekday_demand

```sql
-- Dialect: SQLite 3.25+ (window functions). Grain: source booking row.
SELECT weekday_number,weekday,COUNT(*) bookings,COUNT(DISTINCT booking_date) observed_days,
 ROUND(1.0*COUNT(*)/COUNT(DISTINCT booking_date),2) bookings_per_day,ROUND(100.0*SUM(is_completed)/COUNT(*),2) completion_pct FROM bookings GROUP BY weekday_number,weekday ORDER BY weekday_number;
```

Result: 7 rows. Preview (first 12 rows):

```csv
weekday_number,weekday,bookings,observed_days,bookings_per_day,completion_pct

1,Monday,21644,53,408.38,61.53

2,Tuesday,21391,52,411.37,61.57

3,Wednesday,21413,52,411.79,62.09

4,Thursday,21215,52,407.98,62.25

5,Friday,21397,52,411.48,61.94

6,Saturday,21542,52,414.27,62.4

7,Sunday,21398,52,411.5,62.22

```

## 07_hour_weekday_heatmap

```sql
-- Dialect: SQLite 3.25+ (window functions). Grain: source booking row.
SELECT weekday_number,weekday,hour,COUNT(*) bookings,ROUND(100.0*SUM(is_completed)/COUNT(*),2) completion_pct FROM bookings GROUP BY weekday_number,weekday,hour ORDER BY weekday_number,hour;
```

Result: 168 rows. Preview (first 12 rows):

```csv
weekday_number,weekday,hour,bookings,completion_pct

1,Monday,0,204,65.2

1,Monday,1,209,56.46

1,Monday,2,206,59.22

1,Monday,3,203,63.05

1,Monday,4,183,58.47

1,Monday,5,446,60.76

1,Monday,6,594,63.97

1,Monday,7,770,62.6

1,Monday,8,1026,62.18

1,Monday,9,1204,61.79

1,Monday,10,1335,62.47

1,Monday,11,1207,62.05

```

## 08_vehicle_performance

```sql
-- Dialect: SQLite 3.25+ (window functions). Grain: source booking row.
SELECT vehicle_type,COUNT(*) bookings,SUM(is_completed) completed,ROUND(100.0*SUM(is_completed)/COUNT(*),2) completion_pct,
 SUM(completed_value) completed_value,ROUND(AVG(completed_value),2) avg_completed_value,ROUND(AVG(completed_distance),2) avg_completed_distance,
 ROUND(AVG(CASE WHEN is_completed=1 THEN avg_vtat END),2) completed_avg_vtat,ROUND(AVG(driver_rating),3) driver_rating
 FROM bookings GROUP BY vehicle_type ORDER BY completed_value DESC;
```

Result: 7 rows. Preview (first 12 rows):

```csv
vehicle_type,bookings,completed,completion_pct,completed_value,avg_completed_value,avg_completed_distance,completed_avg_vtat,driver_rating

Auto,37419,23155,61.88,11727615.0,506.48,25.99,8.49,4.232

Go Mini,29806,18549,62.23,9411418.0,507.38,25.99,8.52,4.228

Go Sedan,27141,16676,61.44,8538560.0,512.03,25.98,8.49,4.232

Bike,22517,14034,62.33,7144913.0,509.11,26.0,8.57,4.23

Premier Sedan,18111,11252,62.13,5733655.0,509.57,25.95,8.47,4.235

eBike,10557,6551,62.05,3298157.0,503.46,26.34,8.54,4.226

Uber XL,4449,2783,62.55,1406256.0,505.3,25.72,8.59,4.238

```

## 09_failure_reasons

```sql
-- Dialect: SQLite 3.25+ (window functions). Grain: source booking row.
SELECT status,failure_reason,COUNT(*) bookings,
 ROUND(100.0*COUNT(*)/SUM(COUNT(*)) OVER(PARTITION BY status),2) pct_within_status,
 ROUND(100.0*COUNT(*)/(SELECT SUM(is_failed) FROM bookings),2) pct_all_unsuccessful FROM bookings WHERE is_failed=1 GROUP BY status,failure_reason ORDER BY bookings DESC;
```

Result: 13 rows. Preview (first 12 rows):

```csv
status,failure_reason,bookings,pct_within_status,pct_all_unsuccessful

No Driver Found,No driver found,10500,100.0,18.42

Cancelled by Driver,Customer related issue,6837,25.32,11.99

Cancelled by Driver,The customer was coughing/sick,6751,25.0,11.84

Cancelled by Driver,Personal & Car related issues,6726,24.91,11.8

Cancelled by Driver,More than permitted people in there,6686,24.76,11.73

Incomplete,Customer Demand,3040,33.78,5.33

Incomplete,Vehicle Breakdown,3012,33.47,5.28

Incomplete,Other Issue,2948,32.76,5.17

Cancelled by Customer,Wrong Address,2362,22.5,4.14

Cancelled by Customer,Change of plans,2353,22.41,4.13

Cancelled by Customer,Driver is not moving towards pickup location,2335,22.24,4.1

Cancelled by Customer,Driver asked to cancel,2295,21.86,4.03

```

## 10_pickup_priorities

```sql
-- Dialect: SQLite 3.25+ (window functions). Grain: source booking row.
SELECT pickup,COUNT(*) bookings,SUM(is_failed) unsuccessful,
 SUM(CASE WHEN status='No Driver Found' THEN 1 ELSE 0 END) no_driver,
 ROUND(100.0*SUM(is_failed)/COUNT(*),2) unsuccessful_pct,
 ROUND(100.0*SUM(CASE WHEN status='No Driver Found' THEN 1 ELSE 0 END)/COUNT(*),2) no_driver_pct
 FROM bookings GROUP BY pickup HAVING COUNT(*)>=500 ORDER BY unsuccessful DESC;
```

Result: 176 rows. Preview (first 12 rows):

```csv
pickup,bookings,unsuccessful,no_driver,unsuccessful_pct,no_driver_pct

Pragati Maidan,920,382,70,41.52,7.61

Saket,931,374,65,40.17,6.98

Vinobapuri,823,373,76,45.32,9.23

Akshardham,839,368,59,43.86,7.03

Badshahpur,868,362,70,41.71,8.06

Udyog Vihar,897,358,62,39.91,6.91

AIIMS,918,356,63,38.78,6.86

Badarpur,921,354,62,38.44,6.73

Nehru Place,885,352,61,39.77,6.89

Keshav Puram,865,352,65,40.69,7.51

GTB Nagar,872,352,58,40.37,6.65

Barakhamba Road,946,352,58,37.21,6.13

```

## 11_routes

```sql
-- Dialect: SQLite 3.25+ (window functions). Grain: source booking row.
SELECT pickup,dropoff,COUNT(*) bookings,SUM(is_completed) completed,
 ROUND(100.0*SUM(is_completed)/COUNT(*),2) completion_pct,SUM(completed_value) completed_value
 FROM bookings GROUP BY pickup,dropoff HAVING COUNT(*)>=10 ORDER BY bookings DESC,pickup,dropoff;
```

Result: 879 rows. Preview (first 12 rows):

```csv
pickup,dropoff,bookings,completed,completion_pct,completed_value

DLF City Court,Bhiwadi,17,13,76.47,5925.0

Akshardham,RK Puram,16,7,43.75,4207.0

Janakpuri,Faridabad Sector 15,16,9,56.25,4248.0

Ghaziabad,Badshahpur,15,6,40.0,2538.0

Jor Bagh,Rohini East,15,7,46.67,1457.0

Rithala,Udyog Vihar Phase 4,15,11,73.33,6325.0

Vatika Chowk,Rithala,15,9,60.0,3277.0

Chirag Delhi,Noida Film City,14,7,50.0,2973.0

Connaught Place,Paharganj,14,9,64.29,4766.0

Indirapuram,Vaishali,14,8,57.14,2822.0

Kashmere Gate ISBT,Tilak Nagar,14,7,50.0,1835.0

Mayur Vihar,Vidhan Sabha,14,10,71.43,5058.0

```

## 12_payment_mix

```sql
-- Dialect: SQLite 3.25+ (window functions). Grain: source booking row.
SELECT payment_method,COUNT(*) completed,SUM(completed_value) completed_value,
 ROUND(AVG(completed_value),2) avg_completed_value,
 ROUND(100.0*COUNT(*)/(SELECT SUM(is_completed) FROM bookings),2) completed_share_pct
 FROM bookings WHERE is_completed=1 GROUP BY payment_method ORDER BY completed DESC;
```

Result: 5 rows. Preview (first 12 rows):

```csv
payment_method,completed,completed_value,avg_completed_value,completed_share_pct

UPI,41834,21274591.0,508.55,44.98

Cash,23114,11756071.0,508.61,24.85

Uber Wallet,11206,5669070.0,505.9,12.05

Credit Card,9320,4753767.0,510.06,10.02

Debit Card,7526,3807075.0,505.86,8.09

```

## 13_value_distribution

```sql
-- Dialect: SQLite 3.25+ (window functions). Grain: source booking row.
SELECT CASE WHEN completed_value<250 THEN '01 | <250' WHEN completed_value<500 THEN '02 | 250-499'
 WHEN completed_value<1000 THEN '03 | 500-999' ELSE '04 | >=1000' END value_band,COUNT(*) completed,SUM(completed_value) completed_value
 FROM bookings WHERE is_completed=1 GROUP BY value_band ORDER BY value_band;
```

Result: 4 rows. Preview (first 12 rows):

```csv
value_band,completed,completed_value

01 | <250,25273,3842511.0

02 | 250-499,32091,12015416.0

03 | 500-999,28331,20678935.0

04 | >=1000,7305,10723712.0

```

## 14_vtat_association

```sql
-- Dialect: SQLite 3.25+ (window functions). Grain: source booking row.
SELECT vtat_band,COUNT(*) bookings,SUM(is_completed) completed,
 ROUND(100.0*SUM(is_completed)/COUNT(*),2) completion_pct FROM bookings GROUP BY vtat_band ORDER BY vtat_band;
```

Result: 5 rows. Preview (first 12 rows):

```csv
vtat_band,bookings,completed,completion_pct

00 | Not observed,10500,0,0.0

01 | <=5,31311,21670,69.21

02 | >5-10,59896,35849,59.85

03 | >10-15,44772,35481,79.25

04 | >15,3521,0,0.0

```

## 15_customer_frequency

```sql
-- Dialect: SQLite 3.25+ (window functions). Grain: source booking row.
WITH c AS (SELECT customer_id,COUNT(*) bookings,SUM(is_completed) completed FROM bookings GROUP BY customer_id)
 SELECT bookings AS bookings_per_customer,COUNT(*) customers,SUM(bookings) booking_rows,SUM(completed) completed FROM c GROUP BY bookings ORDER BY bookings;
```

Result: 3 rows. Preview (first 12 rows):

```csv
bookings_per_customer,customers,booking_rows,completed

1,147582,147582,91516

2,1200,2400,1471

3,6,18,13

```

## 16_identifier_collisions

```sql
-- Dialect: SQLite 3.25+ (window functions). Grain: source booking row.
SELECT booking_id,COUNT(*) rows,COUNT(DISTINCT customer_id) customers,COUNT(DISTINCT booking_date) dates,
 COUNT(DISTINCT status) statuses FROM bookings GROUP BY booking_id HAVING COUNT(*)>1 ORDER BY rows DESC,booking_id;
```

Result: 1,224 rows. Preview (first 12 rows):

```csv
booking_id,rows,customers,dates,statuses

CNR2726142,3,3,3,1

CNR3648267,3,3,3,1

CNR5292943,3,3,3,1

CNR6337479,3,3,3,1

CNR7199036,3,3,3,1

CNR7585544,3,3,3,1

CNR7642097,3,3,3,2

CNR7908610,3,3,3,1

CNR9603232,3,3,3,2

CNR1026036,2,2,2,2

CNR1029172,2,2,2,2

CNR1051228,2,2,2,1

```

## 17_status_missingness

```sql
-- Dialect: SQLite 3.25+ (window functions). Grain: source booking row.
SELECT status,COUNT(*) rows,COUNT(avg_vtat) vtat_observations,COUNT(avg_ctat) ctat_observations,
 COUNT(booking_value) value_observations,COUNT(ride_distance) distance_observations,COUNT(driver_rating) driver_rating_observations,
 COUNT(payment_method) payment_observations FROM bookings GROUP BY status;
```

Result: 5 rows. Preview (first 12 rows):

```csv
status,rows,vtat_observations,ctat_observations,value_observations,distance_observations,driver_rating_observations,payment_observations

Cancelled by Customer,10500,10500,0,0,0,0,0

Cancelled by Driver,27000,27000,0,0,0,0,0

Completed,93000,93000,93000,93000,93000,93000,93000

Incomplete,9000,9000,9000,9000,9000,0,9000

No Driver Found,10500,0,0,0,0,0,0

```

## 18_ratings_segments

```sql
-- Dialect: SQLite 3.25+ (window functions). Grain: source booking row.
SELECT vehicle_type,COUNT(*) rated_completed,ROUND(AVG(driver_rating),3) driver_rating,
 ROUND(AVG(customer_rating),3) customer_rating,SUM(CASE WHEN driver_rating<4 THEN 1 ELSE 0 END) driver_ratings_below_4,
 ROUND(100.0*SUM(CASE WHEN driver_rating<4 THEN 1 ELSE 0 END)/COUNT(*),2) below_4_pct FROM bookings WHERE is_completed=1 GROUP BY vehicle_type ORDER BY driver_rating;
```

Result: 7 rows. Preview (first 12 rows):

```csv
vehicle_type,rated_completed,driver_rating,customer_rating,driver_ratings_below_4,below_4_pct

eBike,6551,4.226,4.404,1500,22.9

Go Mini,18549,4.228,4.404,4261,22.97

Bike,14034,4.23,4.404,3195,22.77

Auto,23155,4.232,4.402,5188,22.41

Go Sedan,16676,4.232,4.41,3762,22.56

Premier Sedan,11252,4.235,4.403,2504,22.25

Uber XL,2783,4.238,4.405,611,21.95

```

## 19_distance_value_association

```sql
-- Dialect: SQLite 3.25+ (window functions). Grain: source booking row.
SELECT CASE WHEN ride_distance<10 THEN '01 | <10' WHEN ride_distance<25 THEN '02 | 10-24.99' ELSE '03 | >=25' END distance_band,
 COUNT(*) completed,ROUND(AVG(completed_value),2) avg_value,ROUND(SUM(completed_value)/SUM(completed_distance),2) weighted_value_per_distance
 FROM bookings WHERE is_completed=1 GROUP BY distance_band ORDER BY distance_band;
```

Result: 3 rows. Preview (first 12 rows):

```csv
distance_band,completed,avg_value,weighted_value_per_distance

01 | <10,15502,503.4,83.69

02 | 10-24.99,28992,508.68,29.02

03 | >=25,48506,509.4,13.6

```

## 20_weekend_comparison

```sql
-- Dialect: SQLite 3.25+ (window functions). Grain: source booking row.
SELECT is_weekend,COUNT(*) bookings,COUNT(DISTINCT booking_date) days,
 ROUND(1.0*COUNT(*)/COUNT(DISTINCT booking_date),2) bookings_per_day,
 ROUND(100.0*SUM(is_completed)/COUNT(*),2) completion_pct FROM bookings GROUP BY is_weekend;
```

Result: 2 rows. Preview (first 12 rows):

```csv
is_weekend,bookings,days,bookings_per_day,completion_pct

0,107060,261,410.19,61.88

1,42940,104,412.88,62.31

```

## 21_recovery_scenarios

```sql
-- Dialect: SQLite 3.25+ (window functions). Grain: source booking row.
WITH base AS (SELECT COUNT(*) n,SUM(is_completed) c,AVG(completed_value) abv FROM bookings),
 scenarios AS (SELECT 1 pp UNION ALL SELECT 3 UNION ALL SELECT 5)
 SELECT pp AS completion_improvement_pp,ROUND(n*pp/100.0) additional_completed,
 ROUND(n*pp/100.0*abv,2) illustrative_additional_booking_value FROM base CROSS JOIN scenarios;
```

Result: 3 rows. Preview (first 12 rows):

```csv
completion_improvement_pp,additional_completed,illustrative_additional_booking_value

1,1500.0,762267.32

3,4500.0,2286801.97

5,7500.0,3811336.61

```

## 22_reason_flag_reconciliation

```sql
-- Dialect: SQLite 3.25+ (window functions). Grain: source booking row.
SELECT SUM(CASE WHEN (status='Cancelled by Customer')<>COALESCE(customer_cancel_flag,0) THEN 1 ELSE 0 END) customer_flag_mismatches,
 SUM(CASE WHEN (status='Cancelled by Driver')<>COALESCE(driver_cancel_flag,0) THEN 1 ELSE 0 END) driver_flag_mismatches,
 SUM(CASE WHEN (status='Incomplete')<>COALESCE(incomplete_flag,0) THEN 1 ELSE 0 END) incomplete_flag_mismatches FROM bookings;
```

Result: 1 rows. Preview (first 12 rows):

```csv
customer_flag_mismatches,driver_flag_mismatches,incomplete_flag_mismatches

0,0,0

```

## 23_daily_control_series

```sql
-- Dialect: SQLite 3.25+ (window functions). Grain: source booking row.
SELECT c.booking_date,COUNT(b.booking_row_key) bookings,COALESCE(SUM(b.is_completed),0) completed,
 ROUND(100.0*SUM(b.is_completed)/NULLIF(COUNT(b.booking_row_key),0),2) completion_pct FROM calendar c LEFT JOIN bookings b USING(booking_date) GROUP BY c.booking_date ORDER BY c.booking_date;
```

Result: 365 rows. Preview (first 12 rows):

```csv
booking_date,bookings,completed,completion_pct

2024-01-01,414,251,60.63

2024-01-02,389,240,61.7

2024-01-03,384,245,63.8

2024-01-04,414,254,61.35

2024-01-05,416,257,61.78

2024-01-06,409,234,57.21

2024-01-07,437,271,62.01

2024-01-08,387,250,64.6

2024-01-09,434,257,59.22

2024-01-10,407,269,66.09

2024-01-11,436,277,63.53

2024-01-12,388,248,63.92

```

## 24_booking_id_sensitivity

```sql
-- Dialect: SQLite 3.25+ (window functions). Grain: source booking row.
SELECT CASE WHEN booking_id_reused=1 THEN 'Reused ID rows' ELSE 'Unique ID rows' END segment,
 COUNT(*) bookings,SUM(is_completed) completed,ROUND(100.0*SUM(is_completed)/COUNT(*),2) completion_pct,SUM(completed_value) completed_value FROM bookings GROUP BY booking_id_reused;
```

Result: 2 rows. Preview (first 12 rows):

```csv
segment,bookings,completed,completion_pct,completed_value

Unique ID rows,147543,91510,62.02,46489770.0

Reused ID rows,2457,1490,60.64,770804.0

```
