# Uber Ride Analytics

Operational Performance Analysis

Reporting period: 1 January - 30 December 2024
Prepared: 2 November 2026
Source: public NCR ride-booking dataset published on Kaggle

## Executive summary

The principal issue in this dataset is booking completion. Of 150,000 recorded booking observations, 93,000 completed and 57,000 did not. Driver cancellations account for 27,000 observations: 18% of all bookings and 47.37% of unsuccessful bookings. They are therefore the first category to investigate, although the supplied reason labels do not establish a verified operational cause.

Key results

| Measure | Result |
| --- | --- |
| Booking observations | 150,000 |
| Completed bookings | 93,000 (62.0%) |
| Unsuccessful bookings | 57,000 (38.0%) |
| Completed recorded booking value | 47,260,574; currency unspecified |

Demand is concentrated by hour rather than by weekday. The 17:00-20:59 window contains 44,118 bookings (29.41% of the extract), and 18:00 is the busiest individual hour. In contrast, weekday demand differs by only about 1.5% after normalizing for the number of observed dates. A targeted availability investigation is better supported than a general weekend expansion.

Vehicle categories differ mainly in volume. Auto and Go Mini together represent 44.82% of requests. Completion rates and average completed booking values are relatively similar across categories, providing little support for claims that one service is materially better or commands a premium in this extract. UPI accounts for 44.98% of completed bookings.

Recommended action. First audit driver-cancellation attribution and the underlying records. Then test a limited availability or pickup-communication intervention in preselected time/location cells, with completion as the primary measure and a comparison group. In parallel, resolve reused booking identifiers and confirm field definitions before production use. These are proposed investigations, not demonstrated remedies.

Interpretation. The dataset is a public case-study extract with unverified provenance and sampling. Currency, distance and timing units are not confirmed. Recorded booking value is not recognized revenue or profit, and no causal effect of any proposed intervention can be estimated from this file. The report supports descriptive findings within the extract, not company-wide conclusions about Uber.

## 1. Scope and methodology

The analysis examines completion reliability, demand patterns, service mix, pickup locations, payments and the limits of experience/customer analysis. The source file contains 150,000 rows and 21 fields. Its coverage is 365 consecutive dates from 1 January through 30 December 2024, including leap day; 31 December is outside the extract. Annual or December comparisons must disclose this coverage.

The unit of analysis is a source booking row. Booking IDs are reused, so counts use rows rather than distinct booking IDs. All records are retained under a unique source-order row key. Text identifiers are trimmed, ISO dates are parsed, and month, hour, weekday and outcome flags are derived. Empty numeric fields remain null; unsuccessful rides are not assigned zero value or zero ratings.

Twenty-four SQLite queries were executed and their complete results retained as CSV files. The main totals reconcile independently against pandas, and 12 transformation checks passed. These checks establish arithmetic and processing consistency, not source authenticity. Query references such as Q02 identify the evidence listed in Appendix B. Detailed field definitions and quality results are in Appendix A.

## 2. Booking completion and unsuccessful outcomes

The completion rate is 62.0%. The remaining 38.0% comprises four distinct outcomes, as shown in Table 1. Cancellation-only metrics combine driver and customer cancellations (25.0% of all rows); they exclude no-driver and incomplete outcomes. Treating all unsuccessful bookings as cancellations would obscure different operational problems. (Q01, Q02, Q22)

Table 1. Booking outcomes

| Outcome | Booking rows | Share of all rows (%) |
| --- | --- | --- |
| Completed | 93,000 | 62 |
| Cancelled by Driver | 27,000 | 18 |
| Cancelled by Customer | 10,500 | 7 |
| No Driver Found | 10,500 | 7 |
| Incomplete | 9,000 | 6 |

Source: Q02. Denominator: all 150,000 booking rows. Categories are mutually exclusive in the source.

### 2.1 Cancellation reasons

Driver cancellations are the largest unsuccessful category, accounting for 47.37% of the 57,000 unsuccessful observations. Their four recorded reasons are almost evenly distributed: customer-related issue (6,837), customer coughing/sick (6,751), personal/car-related issues (6,726), and more than permitted people (6,686). The small differences and broad labels do not justify selecting one cause as the main intervention target. Verification of cancellation attribution should precede incentives, penalties or product changes. (Q09)

Among customer cancellations, Wrong Address is the largest label at 2,362, or 22.50% of that category. Driver not moving toward pickup (2,335) and Driver asked to cancel (2,295) together represent 44.10% of customer cancellations. This supports investigating address confirmation, arrival communication and driver-requested cancellation attribution. It does not show that messaging changes would recover those bookings. (Q09)

Incomplete rides account for 9,000 observations. Customer Demand (3,040), Vehicle Breakdown (3,012) and Other Issue (2,948) are similarly represented. They should remain a separate review stream because incomplete trips have recorded value and distance, unlike cancelled and no-driver observations. (Q02, Q09, Q17)

## 3. Demand by time

The 18:00 hour contains 12,397 bookings, 7,617 completions and 891 no-driver outcomes. The broader 17:00-20:59 window accounts for 29.41% of all requests. The hourly distribution therefore identifies a useful window for investigating availability and dispatch conditions. It cannot establish a fleet shortage because online drivers, concurrent requests and dispatch events are absent. (Q05, Q07)

Figure 1. Booking observations by hour

Hourly booking counts are available in outputs/05_hour_demand.csv.

Source: Q05. Times are source time-of-day values; the timezone is unverified. The dark bar identifies 18:00.

Demand is comparatively stable across weekdays after accounting for unequal exposure. Daily averages range from 407.98 on Thursday to 414.27 on Saturday, about 1.5% apart. Weekend demand averages 412.88 bookings per observed day versus 410.19 on weekdays, a difference of approximately 0.66%. These differences are too small to support a blanket weekend capacity recommendation from this extract alone. (Q06, Q20)

Monthly totals also require exposure adjustment. February records 7.26% fewer bookings than January, but it has 29 observed days versus 31. Their daily averages are 411.28 and 414.87 respectively, a much smaller difference. Across all months, observed daily averages range from 406.63 to 416.03. Use daily-normalized figures when comparing months, particularly December, which ends on the 30th. There is no prior-year extract with which to establish year-on-year growth. (Q03, Q04)

## 4. Vehicle mix, booking value and payments

Auto generates the most requests and completed booking value, followed by Go Mini and Go Sedan. Auto and Go Mini together account for 67,225 requests, or 44.82% of all rows. They offer the broadest reach for a category-stratified reliability review, but volume leadership should not be interpreted as a higher quality of service. (Q08)

Table 2. Vehicle performance

| Vehicle | Requests | Completion (%) | Completed value | Average value |
| --- | --- | --- | --- | --- |
| Auto | 37,419 | 61.88 | 11,727,615 | 506.48 |
| Go Mini | 29,806 | 62.23 | 9,411,418 | 507.38 |
| Go Sedan | 27,141 | 61.44 | 8,538,560 | 512.03 |
| Bike | 22,517 | 62.33 | 7,144,913 | 509.11 |
| Premier Sedan | 18,111 | 62.13 | 5,733,655 | 509.57 |
| eBike | 10,557 | 62.05 | 3,298,157 | 503.46 |
| Uber XL | 4,449 | 62.55 | 1,406,256 | 505.30 |

Source: Q08. Value figures include Completed rows only. Currency is unspecified.

Completion rates range from 61.44% for Go Sedan to 62.55% for Uber XL, a spread of 1.11 percentage points. Uber XL has only 4,449 observations. Approximate independent-binomial 95% intervals for Uber XL (61.13%-63.97%) and Go Sedan (60.86%-62.02%) overlap. The ranking is therefore weak evidence for a service-quality difference; these intervals also do not resolve selection bias or possible synthetic structure. (Q08)

Average completed value ranges from 503.46 to 512.03 across vehicles, a spread of roughly 1.7%. The data does not demonstrate a premium-service fare hierarchy. Completed recorded value totals 47,260,574, while incomplete rides carry another 4,585,609. Combining both would exceed completed value by 9.70%. Neither total establishes recognized revenue, platform commission, cash collected or profit. (Q01, Q02, Q08)

The average completed value is 508.18 and the median is 414; the mean is 22.75% above the median. The 90th, 95th and 99th percentiles are 958, 1,222 and approximately 1,963 respectively. Typical booking value should therefore be described with the median and percentiles as well as the mean. Large observations are not automatically errors or fraud. (Source profile; Q13)

The completed value-distance correlation is approximately 0.0057, close to zero in this extract. It does not support a distance-based fare model. Because distance units are unverified and no fare rules are supplied, a price-per-kilometre or profitability claim would be unsupported. (Q19; source profile)

Table 3. Payment mix among completed bookings

| Payment method | Completed rows | Share (%) | Completed value |
| --- | --- | --- | --- |
| UPI | 41,834 | 44.98 | 21,274,591 |
| Cash | 23,114 | 24.85 | 11,756,071 |
| Uber Wallet | 11,206 | 12.05 | 5,669,070 |
| Credit Card | 9,320 | 10.02 | 4,753,767 |
| Debit Card | 7,526 | 8.09 | 3,807,075 |

Source: Q12. Payment is missing on cancellations and no-driver rows, so these shares do not describe all attempted bookings.

UPI accounts for 44.98% of completed bookings and approximately 45.02% of completed value; cash accounts for 24.85% of completed bookings. Payment-method averages are similar. The extract supports a description of completed transaction mix, not a conclusion about payment preference or payment-related cancellation behaviour across all requests. (Q12, Q17)

## 5. Pickup-location priorities

Location comparisons need both counts and rates. Pragati Maidan has the largest unsuccessful count (382 of 920 bookings), while Vinobapuri has fewer total bookings but a higher unsuccessful rate (373 of 823). The former is a volume-based review candidate and the latter a rate-based candidate. Neither establishes a verified dispatch or geographic coverage problem. (Q10)

Table 4. Pickup areas ranked by unsuccessful count

| Pickup area | Requests | Unsuccessful | Failure (%) | No driver (%) |
| --- | --- | --- | --- | --- |
| Pragati Maidan | 920 | 382 | 41.52 | 7.61 |
| Saket | 931 | 374 | 40.17 | 6.98 |
| Vinobapuri | 823 | 373 | 45.32 | 9.23 |
| Akshardham | 839 | 368 | 43.86 | 7.03 |
| Badshahpur | 868 | 362 | 41.71 | 8.06 |
| Udyog Vihar | 897 | 358 | 39.91 | 6.91 |
| AIIMS | 918 | 356 | 38.78 | 6.86 |
| Badarpur | 921 | 354 | 38.44 | 6.73 |

Source: Q10. The query requires at least 500 requests per area. This reporting threshold is not a guarantee of statistical reliability.

Vinobapuri is 7.32 percentage points above the overall 38% unsuccessful rate. A rough independent-binomial 95% interval is 41.9%-48.7%, but screening 176 locations increases the chance of apparent extremes. Validate selected locations on a later time window and account for multiple comparisons before making broad resource changes. Old Gurgaon is a separate availability candidate, with 83 no-driver outcomes from 807 requests (10.29% versus 7% overall). (Q10)

Route analysis retains origin-destination pairs with at least 10 bookings. This removes the sparsest displayed cells but does not establish stable route-level performance. With no coordinates, travel times or driver-supply measures, the project cannot estimate geographic coverage, repositioning requirements or route profitability. (Q11)

## 6. Ratings, timing and customer-analysis limits

Average driver and customer ratings are 4.231 and 4.405 respectively. All 93,000 completed rows have ratings, whereas unsuccessful bookings do not. These averages describe the completed subset and cannot be used as overall customer-experience measures. Vehicle driver-rating averages differ only from 4.226 to 4.238, which provides little practical basis for a service ranking. Driver identifiers are absent, preventing driver-level performance analysis. (Q01, Q17, Q18)

Completed rides have average source VTAT of 8.51 and CTAT of 30.03, but the field definitions and units remain unverified. Completion by VTAT band is non-monotonic: 69.21% at 5 or below, 59.85% above 5 through 10, and 79.25% above 10 through 15. No observations above 15 complete, and no-driver rows have no VTAT. These patterns may reflect measurement or generation rules; they do not establish that waiting causes cancellation. (Q14, Q17)

There are 148,788 distinct customer IDs, of which 147,582 appear once. Only 1,206 IDs appear more than once: 1,200 twice and six three times. Sparse repeats and uncertain identifier provenance prevent credible retention, churn or lifetime-value conclusions. This is a coverage limitation of the extract, not evidence that Uber riders rarely return. A valid customer study would require persistent keys, complete booking histories and a defined observation/eligibility window. (Q15)

## 7. Completion-recovery scenarios

Table 5 translates improvements in completion into a sensitivity calculation. A one-percentage-point improvement on 150,000 requests means 1,500 additional completed bookings; it is not a 1% relative increase in the 62% rate. The value calculation applies the existing average completed booking value to those additional completions. (Q21)

Table 5. Illustrative completion-recovery scenarios

| Completion uplift (pp) | Additional completed | Illustrative additional value |
| --- | --- | --- |
| 1 | 1,500 | 762,267.32 |
| 3 | 4,500 | 2,286,801.97 |
| 5 | 7,500 | 3,811,336.61 |

Source: Q21. Figures are scenarios, not forecasts. Value is in unspecified source units and is not profit.

The scenarios assume fixed request volume, unchanged service/rider mix, the same average value on recovered rides, and no substitution or cannibalization. Incentives, operating costs, refunds and capacity constraints are not modelled. The analysis cannot estimate what fraction of unsuccessful bookings is recoverable; these values should not be used as an investment-return forecast.

## 8. Recommendations and evaluation

### 8.1 Verify cancellation attribution before intervening

Evidence: driver cancellations account for nearly half of unsuccessful bookings, while their reason labels are broad and nearly evenly split. Proposed action: an operations lead should review a sample of underlying records, verify who initiated cancellation, and distinguish assignment, arrival and trip-start stages. Preserve driver-requested customer cancellations as a separate attribution field. Decision measure: reason completeness and attribution accuracy should improve before reason-specific operational measures are acted on.

### 8.2 Test a limited availability or pickup intervention

Evidence: evening hours contain the greatest demand, and several pickup areas show elevated failure counts or rates. Proposed action: a dispatch/product lead should preselect a small set of time/location cells and test one well-defined change against a comparison group. Candidate hypotheses include improved pickup communication or availability management; the extract cannot choose between them. Primary measure: completion rate. Guardrails: no-driver rate, cancellation attribution, complaints, safety, driver economics and cost per completed trip. The latter measures require additional operational data.

### 8.3 Establish a data contract

Evidence: 1,233 excess rows beyond distinct booking IDs, outcome-dependent missingness, and unverified units limit interpretation. Proposed action: an analytics/data lead should agree persistent event identifiers, status definitions, financial meaning and timestamp rules. Add request, assignment, acceptance, arrival, trip-start and trip-end events; online supply; driver/session keys; refunds and costs. Acceptance measures: key integrity, event-order validity, agreed field coverage and reconciliation to an authoritative source.

### 8.4 Predefine the evaluation

Use randomized zone/time blocks where feasible and address spillover and clustering in the design. An illustrative independent two-proportion calculation from 62% to 65%, with 5% two-sided significance and 80% power, requires approximately 4,100 bookings per arm before design adjustments. This is a planning approximation, not a completed power analysis. Set the evaluation window, eligibility rules and stopping criteria in advance; avoid repeated significance checks followed by opportunistic stopping.

The defensible next decision is to validate attribution and operational data, then run a limited measured test. Broad fleet reallocations, punitive driver policies, fare-model changes and customer-retention programmes are not established by the present evidence.

## Appendix A. Data quality and metric definitions

### A.1 Identifier integrity and coverage

There are no identical rows. Booking ID has 148,767 distinct values and 1,233 excess rows; 2,457 rows carry a reused ID. All observations are retained under a row key because deduplication would remove non-identical records without a supported rule. Unique-ID rows complete at 62.02%, versus 60.64% for reused-ID rows. This sensitivity split does not resolve upstream identity. (Q16, Q24)

Table A1. Non-null field coverage by booking status

| Status | Rows | VTAT observed | Value observed | Rating observed |
| --- | --- | --- | --- | --- |
| Cancelled by Customer | 10,500 | 10,500 | 0 | 0 |
| Cancelled by Driver | 27,000 | 27,000 | 0 | 0 |
| Completed | 93,000 | 93,000 | 93,000 | 93,000 |
| Incomplete | 9,000 | 9,000 | 9,000 | 0 |
| No Driver Found | 10,500 | 0 | 0 | 0 |

Source: Q17. Counts are observations, not percentages. CTAT, distance and payment have the same broad completed/incomplete eligibility as value.

Missingness is outcome-dependent: value, distance, CTAT and payment are present on completed/incomplete rides; ratings cover completed rides; no-driver rows lack VTAT. Do not impute zeros or discard failures. Round status proportions and weak segment/value-distance differences warrant caution about possible educational or synthetic structure, without proving how the file was generated.

### A.2 Metric definitions

Table A2. Principal metric definitions

| Metric | Definition |
| --- | --- |
| Bookings | Number of selected source rows; not distinct Booking IDs. |
| Completion rate | Completed rows divided by all selected booking rows. |
| Cancellation rate | Driver plus customer cancellation rows divided by all selected rows. |
| Unsuccessful rate | Every non-Completed row divided by all selected rows. |
| Completed booking value | Sum of Booking Value on Completed rows only. Not recognized revenue. |
| Average completed value | Completed booking value divided by completed row count. |
| Bookings per observed day | Selected booking rows divided by distinct selected booking dates. |
| Rating / timing averages | Mean of eligible non-null values; report averages use Completed rows. |
| Recovery value | Selected request volume x completion uplift in percentage points / 100 x average completed value. |

Status slicers condition the denominator: Completed alone gives 100% conditional completion. Clear selections to restore the 150,000-row baseline. KEEPFILTERS intersects outcome-specific measures with selected statuses.

## Appendix B. Reproducibility and technical implementation

The cleaned fact and calendar are stored in outputs/uber_analytics.sqlite. Each of the 24 queries is available under sql/, with a full result CSV under outputs/. The execution log records timestamps, result row counts and SHA-256 hashes. report/Queries_Run.md contains the exact SQL and previews. The SQL dialect is SQLite 3.25 or later, including window functions.

The Power BI import model contains Bookings, Calendar, Vehicle, Status, Payment and Pickup, with five one-way relationships and 35 DAX measures. The six-page PBIX includes embedded data; local CSVs are needed for refresh. No Power BI Service connection or cloud account is required. Page names and operating instructions are documented in README.md.

Table B1. Executed query catalogue

| Reference | Executed analysis | Result rows |
| --- | --- | --- |
| Q01 | Executive kpis | 1 |
| Q02 | Status funnel | 5 |
| Q03 | Monthly trend | 12 |
| Q04 | Calendar normalized | 12 |
| Q05 | Hour demand | 24 |
| Q06 | Weekday demand | 7 |
| Q07 | Hour weekday heatmap | 168 |
| Q08 | Vehicle performance | 7 |
| Q09 | Failure reasons | 13 |
| Q10 | Pickup priorities | 176 |
| Q11 | Routes | 879 |
| Q12 | Payment mix | 5 |
| Q13 | Value distribution | 4 |
| Q14 | Vtat association | 5 |
| Q15 | Customer frequency | 3 |
| Q16 | Identifier collisions | 1,224 |
| Q17 | Status missingness | 5 |
| Q18 | Ratings segments | 7 |
| Q19 | Distance value association | 3 |
| Q20 | Weekend comparison | 2 |
| Q21 | Recovery scenarios | 3 |
| Q22 | Reason flag reconciliation | 1 |
| Q23 | Daily control series | 365 |
| Q24 | Booking id sensitivity | 2 |

Rebuild with scripts/analyze.py, scripts/redesign_powerbi.py and scripts/build_professional_report.py. Refresh and save the dashboard in Desktop after regenerating its definitions. The field dictionary and source profile contain the full column inventory.

## Appendix C. Sources and interpretation limits

Dataset: [Yashdev Laddha, Uber Ride Analytics Dashboard, Kaggle](https://www.kaggle.com/datasets/yashdevladdha/uber-ride-analytics-dashboard), downloaded 2 November 2026. Numerical findings were derived independently from ncr_ride_bookings.csv; the author-supplied sample PBIX is preserved separately. The source file hash is recorded in outputs/provenance.json.

Technical references: Microsoft documentation for [Power BI Desktop projects](https://learn.microsoft.com/power-bi/developer/projects/projects-overview), [report definitions](https://learn.microsoft.com/power-bi/developer/projects/projects-report), and [semantic-model definitions](https://learn.microsoft.com/power-bi/developer/projects/projects-dataset). These describe file formats; they do not support or endorse the operational recommendations.

The extract has unverified provenance, sampling and representativeness. It cannot establish Uber-wide performance, causal explanations, realized financial returns or operational capacity requirements. Currency, distance units and timing definitions are unverified. Driver supply, coordinates, costs, commissions, refunds, persistent customer histories and experiment assignment are absent. Ratings exclude unsuccessful rides. Coverage ends on 30 December 2024. These limitations should accompany any presentation of the findings.
