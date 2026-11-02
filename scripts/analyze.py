"""Rebuild the local analytics warehouse, execute SQL, and export audit evidence."""
from pathlib import Path
import pandas as pd
import numpy as np
import sqlite3, json, hashlib, datetime

ROOT=Path(__file__).resolve().parents[1]
raw=ROOT/'data/raw/ncr_ride_bookings.csv'
out=ROOT/'outputs'; out.mkdir(exist_ok=True)
df=pd.read_csv(raw)
original=df.copy()
mapping={
'Date':'booking_date','Time':'booking_time','Booking ID':'booking_id','Booking Status':'status',
'Customer ID':'customer_id','Vehicle Type':'vehicle_type','Pickup Location':'pickup','Drop Location':'dropoff',
'Avg VTAT':'avg_vtat','Avg CTAT':'avg_ctat','Cancelled Rides by Customer':'customer_cancel_flag',
'Reason for cancelling by Customer':'customer_cancel_reason','Cancelled Rides by Driver':'driver_cancel_flag',
'Driver Cancellation Reason':'driver_cancel_reason','Incomplete Rides':'incomplete_flag',
'Incomplete Rides Reason':'incomplete_reason','Booking Value':'booking_value','Ride Distance':'ride_distance',
'Driver Ratings':'driver_rating','Customer Rating':'customer_rating','Payment Method':'payment_method'}
df=df.rename(columns=mapping)
for c in df.select_dtypes(include=['object','str']).columns:
    df[c]=df[c].str.strip().str.strip('"')
df.insert(0,'booking_row_key',np.arange(1,len(df)+1))
dt=pd.to_datetime(df.booking_date)
df['month']=dt.dt.strftime('%Y-%m'); df['hour']=df.booking_time.str[:2].astype(int)
df['weekday_number']=dt.dt.dayofweek+1; df['weekday']=dt.dt.day_name()
df['is_weekend']=(df.weekday_number>=6).astype(int)
df['is_completed']=(df.status=='Completed').astype(int)
df['is_cancelled']=df.status.isin(['Cancelled by Driver','Cancelled by Customer']).astype(int)
df['is_failed']=1-df.is_completed
df['completed_value']=df.booking_value.where(df.is_completed==1)
df['completed_distance']=df.ride_distance.where(df.is_completed==1)
df['failure_reason']=df.customer_cancel_reason.fillna(df.driver_cancel_reason).fillna(df.incomplete_reason)
df.loc[df.status=='No Driver Found','failure_reason']='No driver found'
df['booking_id_reused']=df.booking_id.duplicated(keep=False).astype(int)
df['vtat_band']=pd.cut(df.avg_vtat,[0,5,10,15,100],labels=['01 | <=5','02 | >5-10','03 | >10-15','04 | >15']).astype('str')
df.loc[df.avg_vtat.isna(),'vtat_band']='00 | Not observed'
df.to_csv(ROOT/'data/bookings_clean.csv',index=False)
date=pd.DataFrame({'booking_date':pd.date_range(dt.min(),dt.max()).strftime('%Y-%m-%d')})
dd=pd.to_datetime(date.booking_date); date['month']=dd.dt.strftime('%Y-%m');date['weekday']=dd.dt.day_name();date['weekday_number']=dd.dt.dayofweek+1
date.to_csv(ROOT/'data/calendar.csv',index=False)
conn=sqlite3.connect(out/'uber_analytics.sqlite')
df.to_sql('bookings',conn,if_exists='replace',index=False)
date.to_sql('calendar',conn,if_exists='replace',index=False)
conn.executescript('CREATE UNIQUE INDEX IF NOT EXISTS ix_row ON bookings(booking_row_key); CREATE INDEX IF NOT EXISTS ix_date ON bookings(booking_date); CREATE INDEX IF NOT EXISTS ix_status ON bookings(status);')
queries={
'01_executive_kpis':'''SELECT COUNT(*) AS bookings, SUM(is_completed) AS completed,
 ROUND(100.0*SUM(is_completed)/COUNT(*),2) AS completion_pct,
 SUM(is_cancelled) AS cancellations, SUM(is_failed) AS unsuccessful,
 SUM(completed_value) AS completed_booking_value,
 ROUND(AVG(completed_value),2) AS completed_avg_booking_value,
 ROUND(AVG(completed_distance),2) AS completed_avg_distance,
 ROUND(AVG(CASE WHEN is_completed=1 THEN avg_vtat END),2) AS completed_avg_vtat,
 ROUND(AVG(CASE WHEN is_completed=1 THEN avg_ctat END),2) AS completed_avg_ctat,
 ROUND(AVG(driver_rating),3) AS avg_driver_rating, ROUND(AVG(customer_rating),3) AS avg_customer_rating
 FROM bookings''',
'02_status_funnel':'''SELECT status, COUNT(*) AS bookings, ROUND(100.0*COUNT(*)/(SELECT COUNT(*) FROM bookings),2) AS share_pct,
 COUNT(booking_value) AS value_observations,SUM(booking_value) AS recorded_booking_value FROM bookings GROUP BY status ORDER BY bookings DESC''',
'03_monthly_trend':'''WITH m AS (SELECT month,COUNT(*) bookings,SUM(is_completed) completed,SUM(completed_value) completed_value,
 ROUND(100.0*SUM(is_completed)/COUNT(*),2) completion_pct FROM bookings GROUP BY month)
 SELECT *, ROUND(100.0*(bookings-LAG(bookings) OVER(ORDER BY month))/NULLIF(LAG(bookings) OVER(ORDER BY month),0),2) mom_bookings_pct FROM m ORDER BY month''',
'04_calendar_normalized':'''SELECT b.month,COUNT(*) bookings,COUNT(DISTINCT b.booking_date) observed_days,
 ROUND(1.0*COUNT(*)/COUNT(DISTINCT b.booking_date),2) bookings_per_observed_day FROM bookings b GROUP BY b.month ORDER BY b.month''',
'05_hour_demand':'''SELECT hour,COUNT(*) bookings,SUM(is_completed) completed,ROUND(100.0*SUM(is_completed)/COUNT(*),2) completion_pct,
 SUM(CASE WHEN status='No Driver Found' THEN 1 ELSE 0 END) no_driver,
 ROUND(AVG(CASE WHEN is_completed=1 THEN avg_vtat END),2) completed_avg_vtat FROM bookings GROUP BY hour ORDER BY hour''',
'06_weekday_demand':'''SELECT weekday_number,weekday,COUNT(*) bookings,COUNT(DISTINCT booking_date) observed_days,
 ROUND(1.0*COUNT(*)/COUNT(DISTINCT booking_date),2) bookings_per_day,ROUND(100.0*SUM(is_completed)/COUNT(*),2) completion_pct FROM bookings GROUP BY weekday_number,weekday ORDER BY weekday_number''',
'07_hour_weekday_heatmap':'''SELECT weekday_number,weekday,hour,COUNT(*) bookings,ROUND(100.0*SUM(is_completed)/COUNT(*),2) completion_pct FROM bookings GROUP BY weekday_number,weekday,hour ORDER BY weekday_number,hour''',
'08_vehicle_performance':'''SELECT vehicle_type,COUNT(*) bookings,SUM(is_completed) completed,ROUND(100.0*SUM(is_completed)/COUNT(*),2) completion_pct,
 SUM(completed_value) completed_value,ROUND(AVG(completed_value),2) avg_completed_value,ROUND(AVG(completed_distance),2) avg_completed_distance,
 ROUND(AVG(CASE WHEN is_completed=1 THEN avg_vtat END),2) completed_avg_vtat,ROUND(AVG(driver_rating),3) driver_rating
 FROM bookings GROUP BY vehicle_type ORDER BY completed_value DESC''',
'09_failure_reasons':'''SELECT status,failure_reason,COUNT(*) bookings,
 ROUND(100.0*COUNT(*)/SUM(COUNT(*)) OVER(PARTITION BY status),2) pct_within_status,
 ROUND(100.0*COUNT(*)/(SELECT SUM(is_failed) FROM bookings),2) pct_all_unsuccessful FROM bookings WHERE is_failed=1 GROUP BY status,failure_reason ORDER BY bookings DESC''',
'10_pickup_priorities':'''SELECT pickup,COUNT(*) bookings,SUM(is_failed) unsuccessful,
 SUM(CASE WHEN status='No Driver Found' THEN 1 ELSE 0 END) no_driver,
 ROUND(100.0*SUM(is_failed)/COUNT(*),2) unsuccessful_pct,
 ROUND(100.0*SUM(CASE WHEN status='No Driver Found' THEN 1 ELSE 0 END)/COUNT(*),2) no_driver_pct
 FROM bookings GROUP BY pickup HAVING COUNT(*)>=500 ORDER BY unsuccessful DESC''',
'11_routes':'''SELECT pickup,dropoff,COUNT(*) bookings,SUM(is_completed) completed,
 ROUND(100.0*SUM(is_completed)/COUNT(*),2) completion_pct,SUM(completed_value) completed_value
 FROM bookings GROUP BY pickup,dropoff HAVING COUNT(*)>=10 ORDER BY bookings DESC,pickup,dropoff''',
'12_payment_mix':'''SELECT payment_method,COUNT(*) completed,SUM(completed_value) completed_value,
 ROUND(AVG(completed_value),2) avg_completed_value,
 ROUND(100.0*COUNT(*)/(SELECT SUM(is_completed) FROM bookings),2) completed_share_pct
 FROM bookings WHERE is_completed=1 GROUP BY payment_method ORDER BY completed DESC''',
'13_value_distribution':'''SELECT CASE WHEN completed_value<250 THEN '01 | <250' WHEN completed_value<500 THEN '02 | 250-499'
 WHEN completed_value<1000 THEN '03 | 500-999' ELSE '04 | >=1000' END value_band,COUNT(*) completed,SUM(completed_value) completed_value
 FROM bookings WHERE is_completed=1 GROUP BY value_band ORDER BY value_band''',
'14_vtat_association':'''SELECT vtat_band,COUNT(*) bookings,SUM(is_completed) completed,
 ROUND(100.0*SUM(is_completed)/COUNT(*),2) completion_pct FROM bookings GROUP BY vtat_band ORDER BY vtat_band''',
'15_customer_frequency':'''WITH c AS (SELECT customer_id,COUNT(*) bookings,SUM(is_completed) completed FROM bookings GROUP BY customer_id)
 SELECT bookings AS bookings_per_customer,COUNT(*) customers,SUM(bookings) booking_rows,SUM(completed) completed FROM c GROUP BY bookings ORDER BY bookings''',
'16_identifier_collisions':'''SELECT booking_id,COUNT(*) rows,COUNT(DISTINCT customer_id) customers,COUNT(DISTINCT booking_date) dates,
 COUNT(DISTINCT status) statuses FROM bookings GROUP BY booking_id HAVING COUNT(*)>1 ORDER BY rows DESC,booking_id''',
'17_status_missingness':'''SELECT status,COUNT(*) rows,COUNT(avg_vtat) vtat_observations,COUNT(avg_ctat) ctat_observations,
 COUNT(booking_value) value_observations,COUNT(ride_distance) distance_observations,COUNT(driver_rating) driver_rating_observations,
 COUNT(payment_method) payment_observations FROM bookings GROUP BY status''',
'18_ratings_segments':'''SELECT vehicle_type,COUNT(*) rated_completed,ROUND(AVG(driver_rating),3) driver_rating,
 ROUND(AVG(customer_rating),3) customer_rating,SUM(CASE WHEN driver_rating<4 THEN 1 ELSE 0 END) driver_ratings_below_4,
 ROUND(100.0*SUM(CASE WHEN driver_rating<4 THEN 1 ELSE 0 END)/COUNT(*),2) below_4_pct FROM bookings WHERE is_completed=1 GROUP BY vehicle_type ORDER BY driver_rating''',
'19_distance_value_association':'''SELECT CASE WHEN ride_distance<10 THEN '01 | <10' WHEN ride_distance<25 THEN '02 | 10-24.99' ELSE '03 | >=25' END distance_band,
 COUNT(*) completed,ROUND(AVG(completed_value),2) avg_value,ROUND(SUM(completed_value)/SUM(completed_distance),2) weighted_value_per_distance
 FROM bookings WHERE is_completed=1 GROUP BY distance_band ORDER BY distance_band''',
'20_weekend_comparison':'''SELECT is_weekend,COUNT(*) bookings,COUNT(DISTINCT booking_date) days,
 ROUND(1.0*COUNT(*)/COUNT(DISTINCT booking_date),2) bookings_per_day,
 ROUND(100.0*SUM(is_completed)/COUNT(*),2) completion_pct FROM bookings GROUP BY is_weekend''',
'21_recovery_scenarios':'''WITH base AS (SELECT COUNT(*) n,SUM(is_completed) c,AVG(completed_value) abv FROM bookings),
 scenarios AS (SELECT 1 pp UNION ALL SELECT 3 UNION ALL SELECT 5)
 SELECT pp AS completion_improvement_pp,ROUND(n*pp/100.0) additional_completed,
 ROUND(n*pp/100.0*abv,2) illustrative_additional_booking_value FROM base CROSS JOIN scenarios''',
'22_reason_flag_reconciliation':'''SELECT SUM(CASE WHEN (status='Cancelled by Customer')<>COALESCE(customer_cancel_flag,0) THEN 1 ELSE 0 END) customer_flag_mismatches,
 SUM(CASE WHEN (status='Cancelled by Driver')<>COALESCE(driver_cancel_flag,0) THEN 1 ELSE 0 END) driver_flag_mismatches,
 SUM(CASE WHEN (status='Incomplete')<>COALESCE(incomplete_flag,0) THEN 1 ELSE 0 END) incomplete_flag_mismatches FROM bookings''',
'23_daily_control_series':'''SELECT c.booking_date,COUNT(b.booking_row_key) bookings,COALESCE(SUM(b.is_completed),0) completed,
 ROUND(100.0*SUM(b.is_completed)/NULLIF(COUNT(b.booking_row_key),0),2) completion_pct FROM calendar c LEFT JOIN bookings b USING(booking_date) GROUP BY c.booking_date ORDER BY c.booking_date''',
'24_booking_id_sensitivity':'''SELECT CASE WHEN booking_id_reused=1 THEN 'Reused ID rows' ELSE 'Unique ID rows' END segment,
 COUNT(*) bookings,SUM(is_completed) completed,ROUND(100.0*SUM(is_completed)/COUNT(*),2) completion_pct,SUM(completed_value) completed_value FROM bookings GROUP BY booking_id_reused'''
}
sql_dir=ROOT/'sql';sql_dir.mkdir(exist_ok=True)
results={};audit=[]
for name,q in queries.items():
    (sql_dir/f'{name}.sql').write_text('-- Dialect: SQLite 3.25+ (window functions). Grain: source booking row.\n'+q+';\n',encoding='utf-8')
    r=pd.read_sql_query(q,conn);r.to_csv(out/f'{name}.csv',index=False);results[name]=r
    audit.append({'query':name,'result_rows':len(r),'executed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'result_sha256':hashlib.sha256((out/f'{name}.csv').read_bytes()).hexdigest()})
(out/'query_execution_log.json').write_text(json.dumps(audit,indent=2))
profile=pd.DataFrame({'source_column':original.columns,'type':original.dtypes.astype(str).values,'non_null':original.notna().sum().values,'null_count':original.isna().sum().values,'null_pct':(original.isna().mean()*100).round(2).values,'distinct_non_null':original.nunique().values})
profile.to_csv(out/'data_dictionary_profile.csv',index=False)
checks={
'row_count_150000':len(df)==150000,'row_key_unique':df.booking_row_key.is_unique,
'no_exact_duplicate_rows':int(original.duplicated().sum())==0,
'status_counts_reconcile':int(results['02_status_funnel'].bookings.sum())==len(df),
'completed_value_reconciles':float(df.completed_value.sum())==47260574,
'all_dates_parse':dt.notna().all(),'calendar_365_dates':len(date)==365,
'no_missing_calendar_dates':len(set(date.booking_date)-set(df.booking_date))==0,
'rating_range_1_to_5':df.driver_rating.dropna().between(1,5).all() and df.customer_rating.dropna().between(1,5).all(),
'flag_reconciliation':int(results['22_reason_flag_reconciliation'].sum(axis=1).iloc[0])==0,
'sql_vs_pandas_completed':int(results['01_executive_kpis'].completed.iloc[0])==int(df.is_completed.sum()),
'sql_vs_pandas_value':float(results['01_executive_kpis'].completed_booking_value.iloc[0])==float(df.completed_value.sum())}
(out/'validation.json').write_text(json.dumps({k:bool(v) for k,v in checks.items()},indent=2))
manifest={'source_url':'https://www.kaggle.com/datasets/yashdevladdha/uber-ride-analytics-dashboard','download_date':'2026-11-02',
'raw_sha256':hashlib.sha256(raw.read_bytes()).hexdigest(),'rows':len(df),'columns':len(original.columns),
'date_min':str(dt.min().date()),'date_max':str(dt.max().date()),'missing_calendar_dates':list(set(date.booking_date)-set(df.booking_date)),
'duplicate_rows':int(original.duplicated().sum()),'distinct_booking_ids':df.booking_id.nunique(),
'excess_booking_id_rows':int(df.booking_id.duplicated().sum()),'rows_with_reused_booking_id':int(df.booking_id_reused.sum()),
'distinct_customers':df.customer_id.nunique(),'python_packages':{'pandas':pd.__version__,'numpy':np.__version__},
'completed_value_distance_pearson':float(df.loc[df.is_completed==1,['booking_value','ride_distance']].corr().iloc[0,1]),
'completed_value_quantiles':df.completed_value.dropna().quantile([.25,.5,.75,.9,.95,.99]).to_dict(),
'limitations':['Public educational data; real Uber operational provenance and sampling are unverified.','Currency, distance units and VTAT/CTAT definitions are not verified in the CSV.','Exact status proportions and weak identifier integrity warrant caution about synthetic data.','Booking value is not recognized revenue, profit, net receipts or platform commission.','Coverage is January 1 through December 30, 2024 (365 consecutive dates, including leap day); December 31 is outside the extract.']}
(out/'provenance.json').write_text(json.dumps(manifest,indent=2))
conn.close()
assert all(checks.values()),checks
print(json.dumps(manifest,indent=2));print(results['01_executive_kpis'].to_string(index=False))
