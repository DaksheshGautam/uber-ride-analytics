"""Conventional narrative analytics report with flowing sections and appendices."""
from pathlib import Path
import json, html, re, shutil
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT,TA_RIGHT
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak,KeepTogether
from reportlab.graphics.shapes import Drawing,Rect,Line,String
from reportlab.graphics import renderSVG

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'report';OUT.mkdir(exist_ok=True)
archive=OUT/'archive';archive.mkdir(exist_ok=True)
for ext in ['pdf','html','md']:
    src=OUT/f'Uber_Analytics_Report.{ext}';dest=archive/f'Uber_Analytics_Report_v2_dashboard_style.{ext}'
    if src.exists() and not dest.exists():shutil.copy2(src,dest)
for name,file in [('Arial','arial.ttf'),('Arial-Bold','arialbd.ttf'),('Arial-Italic','ariali.ttf')]:pdfmetrics.registerFont(TTFont(name,'C:/Windows/Fonts/'+file))
pdfmetrics.registerFontFamily('Arial',normal='Arial',bold='Arial-Bold',italic='Arial-Italic',boldItalic='Arial-Bold')
WIDTH=487.28
S={
'title':ParagraphStyle('ReportTitle',fontName='Arial-Bold',fontSize=19,leading=24,spaceAfter=7,textColor=colors.black),
'subtitle':ParagraphStyle('Subtitle',fontName='Arial',fontSize=12,leading=17,spaceAfter=8),
'meta':ParagraphStyle('Metadata',fontName='Arial',fontSize=9,leading=13,spaceAfter=12,textColor=colors.HexColor('#4B5563')),
'h1':ParagraphStyle('H1',fontName='Arial-Bold',fontSize=13,leading=17,spaceBefore=17,spaceAfter=8,keepWithNext=True),
'h2':ParagraphStyle('H2',fontName='Arial-Bold',fontSize=11,leading=15,spaceBefore=10,spaceAfter=6,keepWithNext=True),
'p':ParagraphStyle('Body',fontName='Arial',fontSize=10.5,leading=14.8,spaceAfter=8,allowWidows=0,allowOrphans=0),
'caption':ParagraphStyle('Caption',fontName='Arial-Bold',fontSize=9.2,leading=13,spaceBefore=7,spaceAfter=5,keepWithNext=True),
'note':ParagraphStyle('Note',fontName='Arial',fontSize=8.6,leading=12,spaceAfter=9,textColor=colors.HexColor('#4B5563')),
'th':ParagraphStyle('TableHeader',fontName='Arial-Bold',fontSize=9,leading=12),
'td':ParagraphStyle('TableCell',fontName='Arial',fontSize=9,leading=12),
'num':ParagraphStyle('TableNumber',fontName='Arial',fontSize=9,leading=12,alignment=TA_RIGHT),
}
story=[];content=[]
def p(text,kind='p'):
    story.append(Paragraph(text,S[kind]));content.append((kind,text))
def h(text,level=1):p(html.escape(text),'h1' if level==1 else 'h2')
def br():story.append(PageBreak());content.append(('break',''))
def q(n):return pd.read_csv(next((ROOT/'outputs').glob(f'{n:02}_*.csv')))
def fmt(v):
    if pd.isna(v):return '-'
    if isinstance(v,(float,int)):return f'{v:,.0f}' if float(v).is_integer() else f'{v:,.2f}'
    return str(v)
def table(caption,data,widths=None,note=None):
    p(caption,'caption')
    if isinstance(data,pd.DataFrame):data=[list(data.columns)]+[[fmt(v) for v in row] for row in data.itertuples(index=False,name=None)]
    data=[[str(v) for v in row] for row in data]
    widths=widths or [WIDTH/len(data[0])]*len(data[0])
    cells=[]
    for i,row in enumerate(data):
        cells.append([Paragraph(html.escape(v),S['th'] if i==0 else S['num'] if (caption=='Key results' and j==1) or re.fullmatch(r'[+\-]?[\d,.]+%?',v) else S['td']) for j,v in enumerate(row)])
    t=Table(cells,colWidths=widths,repeatRows=1,hAlign='LEFT')
    pad=2.5 if caption.startswith('Table B1') else 5
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#EEEEEE')),('LINEABOVE',(0,0),(-1,0),.7,colors.black),('LINEBELOW',(0,0),(-1,0),.5,colors.HexColor('#777777')),('LINEBELOW',(0,1),(-1,-1),.25,colors.HexColor('#D6D6D6')),('LINEBELOW',(0,-1),(-1,-1),.6,colors.HexColor('#777777')),('VALIGN',(0,0),(-1,-1),'TOP'),('TOPPADDING',(0,0),(-1,-1),pad),('BOTTOMPADDING',(0,0),(-1,-1),pad),('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6)]))
    # append rather than combining tables and prose into rigid page templates
    story.append(t);story.append(Spacer(1,7));content.append(('table',data))
    if note:p(note,'note')
def hourly():
    d=Drawing(WIDTH,158);df=q(5);bottom=25;ph=108;plotw=WIDTH-34
    for value in [0,5000,10000,15000]:
        yy=bottom+ph*value/15000;d.add(Line(31,yy,WIDTH,yy,strokeColor=colors.HexColor('#D9D9D9'),strokeWidth=.4));d.add(String(26,yy-3,f'{value:,}',textAnchor='end',fontName='Arial',fontSize=7.5))
    for _,r in df.iterrows():
        x=33+r.hour*plotw/24;d.add(Rect(x,bottom,plotw/24-3,ph*r.bookings/15000,fillColor=colors.HexColor('#374151' if r.hour==18 else '#A3AAB3'),strokeColor=None))
        if r.hour%3==0 or r.hour==23:d.add(String(x+4,12,f'{int(r.hour):02}',textAnchor='middle',fontName='Arial',fontSize=8))
    d.add(String(WIDTH,147,'18:00: 12,397 bookings',textAnchor='end',fontName='Arial-Bold',fontSize=9));return d

p('Uber Ride Analytics','title')
p('Operational Performance Analysis','subtitle')
p('Reporting period: 1 January - 30 December 2024<br/>Prepared: 2 November 2026<br/>Source: public NCR ride-booking dataset published on Kaggle','meta')
h('Executive summary')
p('The principal issue in this dataset is booking completion. Of 150,000 recorded booking observations, 93,000 completed and 57,000 did not. Driver cancellations account for 27,000 observations: 18% of all bookings and 47.37% of unsuccessful bookings. They are therefore the first category to investigate, although the supplied reason labels do not establish a verified operational cause.')
table('Key results',[
['Measure','Result'],['Booking observations','150,000'],['Completed bookings','93,000 (62.0%)'],['Unsuccessful bookings','57,000 (38.0%)'],['Completed recorded booking value','47,260,574; currency unspecified']],widths=[290,197.28])
p('Demand is concentrated by hour rather than by weekday. The 17:00-20:59 window contains 44,118 bookings (29.41% of the extract), and 18:00 is the busiest individual hour. In contrast, weekday demand differs by only about 1.5% after normalizing for the number of observed dates. A targeted availability investigation is better supported than a general weekend expansion.')
p('Vehicle categories differ mainly in volume. Auto and Go Mini together represent 44.82% of requests. Completion rates and average completed booking values are relatively similar across categories, providing little support for claims that one service is materially better or commands a premium in this extract. UPI accounts for 44.98% of completed bookings.')
p('<b>Recommended action.</b> First audit driver-cancellation attribution and the underlying records. Then test a limited availability or pickup-communication intervention in preselected time/location cells, with completion as the primary measure and a comparison group. In parallel, resolve reused booking identifiers and confirm field definitions before production use. These are proposed investigations, not demonstrated remedies.')
p('<b>Interpretation.</b> The dataset is a public case-study extract with unverified provenance and sampling. Currency, distance and timing units are not confirmed. Recorded booking value is not recognized revenue or profit, and no causal effect of any proposed intervention can be estimated from this file. The report supports descriptive findings within the extract, not company-wide conclusions about Uber.','p')
br()

h('1. Scope and methodology')
p('The analysis examines completion reliability, demand patterns, service mix, pickup locations, payments and the limits of experience/customer analysis. The source file contains 150,000 rows and 21 fields. Its coverage is 365 consecutive dates from 1 January through 30 December 2024, including leap day; 31 December is outside the extract. Annual or December comparisons must disclose this coverage.')
p('The unit of analysis is a source booking row. Booking IDs are reused, so counts use rows rather than distinct booking IDs. All records are retained under a unique source-order row key. Text identifiers are trimmed, ISO dates are parsed, and month, hour, weekday and outcome flags are derived. Empty numeric fields remain null; unsuccessful rides are not assigned zero value or zero ratings.')
p('Twenty-four SQLite queries were executed and their complete results retained as CSV files. The main totals reconcile independently against pandas, and 12 transformation checks passed. These checks establish arithmetic and processing consistency, not source authenticity. Query references such as Q02 identify the evidence listed in Appendix B. Detailed field definitions and quality results are in Appendix A.')

h('2. Booking completion and unsuccessful outcomes')
p('The completion rate is 62.0%. The remaining 38.0% comprises four distinct outcomes, as shown in Table 1. Cancellation-only metrics combine driver and customer cancellations (25.0% of all rows); they exclude no-driver and incomplete outcomes. Treating all unsuccessful bookings as cancellations would obscure different operational problems. (Q01, Q02, Q22)')
status=q(2)[['status','bookings','share_pct']].copy();status.columns=['Outcome','Booking rows','Share of all rows (%)']
table('Table 1. Booking outcomes',status,widths=[247.28,105,135],note='Source: Q02. Denominator: all 150,000 booking rows. Categories are mutually exclusive in the source.')
h('2.1 Cancellation reasons',2)
p('Driver cancellations are the largest unsuccessful category, accounting for 47.37% of the 57,000 unsuccessful observations. Their four recorded reasons are almost evenly distributed: customer-related issue (6,837), customer coughing/sick (6,751), personal/car-related issues (6,726), and more than permitted people (6,686). The small differences and broad labels do not justify selecting one cause as the main intervention target. Verification of cancellation attribution should precede incentives, penalties or product changes. (Q09)')
p('Among customer cancellations, Wrong Address is the largest label at 2,362, or 22.50% of that category. Driver not moving toward pickup (2,335) and Driver asked to cancel (2,295) together represent 44.10% of customer cancellations. This supports investigating address confirmation, arrival communication and driver-requested cancellation attribution. It does not show that messaging changes would recover those bookings. (Q09)')
p('Incomplete rides account for 9,000 observations. Customer Demand (3,040), Vehicle Breakdown (3,012) and Other Issue (2,948) are similarly represented. They should remain a separate review stream because incomplete trips have recorded value and distance, unlike cancelled and no-driver observations. (Q02, Q09, Q17)')

h('3. Demand by time')
p('The 18:00 hour contains 12,397 bookings, 7,617 completions and 891 no-driver outcomes. The broader 17:00-20:59 window accounts for 29.41% of all requests. The hourly distribution therefore identifies a useful window for investigating availability and dispatch conditions. It cannot establish a fleet shortage because online drivers, concurrent requests and dispatch events are absent. (Q05, Q07)')
p('Figure 1. Booking observations by hour','caption');fig=hourly();story.append(fig);content.append(('figure',None));p('Source: Q05. Times are source time-of-day values; the timezone is unverified. The dark bar identifies 18:00.','note')
p('Demand is comparatively stable across weekdays after accounting for unequal exposure. Daily averages range from 407.98 on Thursday to 414.27 on Saturday, about 1.5% apart. Weekend demand averages 412.88 bookings per observed day versus 410.19 on weekdays, a difference of approximately 0.66%. These differences are too small to support a blanket weekend capacity recommendation from this extract alone. (Q06, Q20)')
p('Monthly totals also require exposure adjustment. February records 7.26% fewer bookings than January, but it has 29 observed days versus 31. Their daily averages are 411.28 and 414.87 respectively, a much smaller difference. Across all months, observed daily averages range from 406.63 to 416.03. Use daily-normalized figures when comparing months, particularly December, which ends on the 30th. There is no prior-year extract with which to establish year-on-year growth. (Q03, Q04)')

h('4. Vehicle mix, booking value and payments')
p('Auto generates the most requests and completed booking value, followed by Go Mini and Go Sedan. Auto and Go Mini together account for 67,225 requests, or 44.82% of all rows. They offer the broadest reach for a category-stratified reliability review, but volume leadership should not be interpreted as a higher quality of service. (Q08)')
v=q(8)[['vehicle_type','bookings','completion_pct','completed_value','avg_completed_value']].copy();v.columns=['Vehicle','Requests','Completion (%)','Completed value','Average value']
table('Table 2. Vehicle performance',v,widths=[116,73,85,116,97.28],note='Source: Q08. Value figures include Completed rows only. Currency is unspecified.')
p('Completion rates range from 61.44% for Go Sedan to 62.55% for Uber XL, a spread of 1.11 percentage points. Uber XL has only 4,449 observations. Approximate independent-binomial 95% intervals for Uber XL (61.13%-63.97%) and Go Sedan (60.86%-62.02%) overlap. The ranking is therefore weak evidence for a service-quality difference; these intervals also do not resolve selection bias or possible synthetic structure. (Q08)')
p('Average completed value ranges from 503.46 to 512.03 across vehicles, a spread of roughly 1.7%. The data does not demonstrate a premium-service fare hierarchy. Completed recorded value totals 47,260,574, while incomplete rides carry another 4,585,609. Combining both would exceed completed value by 9.70%. Neither total establishes recognized revenue, platform commission, cash collected or profit. (Q01, Q02, Q08)')
p('The average completed value is 508.18 and the median is 414; the mean is 22.75% above the median. The 90th, 95th and 99th percentiles are 958, 1,222 and approximately 1,963 respectively. Typical booking value should therefore be described with the median and percentiles as well as the mean. Large observations are not automatically errors or fraud. (Source profile; Q13)')
p('The completed value-distance correlation is approximately 0.0057, close to zero in this extract. It does not support a distance-based fare model. Because distance units are unverified and no fare rules are supplied, a price-per-kilometre or profitability claim would be unsupported. (Q19; source profile)')
pay=q(12)[['payment_method','completed','completed_share_pct','completed_value']].copy();pay.columns=['Payment method','Completed rows','Share (%)','Completed value']
table('Table 3. Payment mix among completed bookings',pay,widths=[157.28,110,90,130],note='Source: Q12. Payment is missing on cancellations and no-driver rows, so these shares do not describe all attempted bookings.')
p('UPI accounts for 44.98% of completed bookings and approximately 45.02% of completed value; cash accounts for 24.85% of completed bookings. Payment-method averages are similar. The extract supports a description of completed transaction mix, not a conclusion about payment preference or payment-related cancellation behaviour across all requests. (Q12, Q17)')

h('5. Pickup-location priorities')
p('Location comparisons need both counts and rates. Pragati Maidan has the largest unsuccessful count (382 of 920 bookings), while Vinobapuri has fewer total bookings but a higher unsuccessful rate (373 of 823). The former is a volume-based review candidate and the latter a rate-based candidate. Neither establishes a verified dispatch or geographic coverage problem. (Q10)')
g=q(10).head(8)[['pickup','bookings','unsuccessful','unsuccessful_pct','no_driver_pct']].copy();g.columns=['Pickup area','Requests','Unsuccessful','Failure (%)','No driver (%)']
table('Table 4. Pickup areas ranked by unsuccessful count',g,widths=[156,70,92,83,86.28],note='Source: Q10. The query requires at least 500 requests per area. This reporting threshold is not a guarantee of statistical reliability.')
p('Vinobapuri is 7.32 percentage points above the overall 38% unsuccessful rate. A rough independent-binomial 95% interval is 41.9%-48.7%, but screening 176 locations increases the chance of apparent extremes. Validate selected locations on a later time window and account for multiple comparisons before making broad resource changes. Old Gurgaon is a separate availability candidate, with 83 no-driver outcomes from 807 requests (10.29% versus 7% overall). (Q10)')
p('Route analysis retains origin-destination pairs with at least 10 bookings. This removes the sparsest displayed cells but does not establish stable route-level performance. With no coordinates, travel times or driver-supply measures, the project cannot estimate geographic coverage, repositioning requirements or route profitability. (Q11)')

h('6. Ratings, timing and customer-analysis limits')
p('Average driver and customer ratings are 4.231 and 4.405 respectively. All 93,000 completed rows have ratings, whereas unsuccessful bookings do not. These averages describe the completed subset and cannot be used as overall customer-experience measures. Vehicle driver-rating averages differ only from 4.226 to 4.238, which provides little practical basis for a service ranking. Driver identifiers are absent, preventing driver-level performance analysis. (Q01, Q17, Q18)')
p('Completed rides have average source VTAT of 8.51 and CTAT of 30.03, but the field definitions and units remain unverified. Completion by VTAT band is non-monotonic: 69.21% at 5 or below, 59.85% above 5 through 10, and 79.25% above 10 through 15. No observations above 15 complete, and no-driver rows have no VTAT. These patterns may reflect measurement or generation rules; they do not establish that waiting causes cancellation. (Q14, Q17)')
p('There are 148,788 distinct customer IDs, of which 147,582 appear once. Only 1,206 IDs appear more than once: 1,200 twice and six three times. Sparse repeats and uncertain identifier provenance prevent credible retention, churn or lifetime-value conclusions. This is a coverage limitation of the extract, not evidence that Uber riders rarely return. A valid customer study would require persistent keys, complete booking histories and a defined observation/eligibility window. (Q15)')

h('7. Completion-recovery scenarios')
p('Table 5 translates improvements in completion into a sensitivity calculation. A one-percentage-point improvement on 150,000 requests means 1,500 additional completed bookings; it is not a 1% relative increase in the 62% rate. The value calculation applies the existing average completed booking value to those additional completions. (Q21)')
sc=q(21).copy();sc.columns=['Completion uplift (pp)','Additional completed','Illustrative additional value']
table('Table 5. Illustrative completion-recovery scenarios',sc,widths=[133,141,213.28],note='Source: Q21. Figures are scenarios, not forecasts. Value is in unspecified source units and is not profit.')
p('The scenarios assume fixed request volume, unchanged service/rider mix, the same average value on recovered rides, and no substitution or cannibalization. Incentives, operating costs, refunds and capacity constraints are not modelled. The analysis cannot estimate what fraction of unsuccessful bookings is recoverable; these values should not be used as an investment-return forecast.')

h('8. Recommendations and evaluation')
h('8.1 Verify cancellation attribution before intervening',2)
p('<b>Evidence:</b> driver cancellations account for nearly half of unsuccessful bookings, while their reason labels are broad and nearly evenly split. <b>Proposed action:</b> an operations lead should review a sample of underlying records, verify who initiated cancellation, and distinguish assignment, arrival and trip-start stages. Preserve driver-requested customer cancellations as a separate attribution field. <b>Decision measure:</b> reason completeness and attribution accuracy should improve before reason-specific operational measures are acted on.')
h('8.2 Test a limited availability or pickup intervention',2)
p('<b>Evidence:</b> evening hours contain the greatest demand, and several pickup areas show elevated failure counts or rates. <b>Proposed action:</b> a dispatch/product lead should preselect a small set of time/location cells and test one well-defined change against a comparison group. Candidate hypotheses include improved pickup communication or availability management; the extract cannot choose between them. <b>Primary measure:</b> completion rate. <b>Guardrails:</b> no-driver rate, cancellation attribution, complaints, safety, driver economics and cost per completed trip. The latter measures require additional operational data.')
h('8.3 Establish a data contract',2)
p('<b>Evidence:</b> 1,233 excess rows beyond distinct booking IDs, outcome-dependent missingness, and unverified units limit interpretation. <b>Proposed action:</b> an analytics/data lead should agree persistent event identifiers, status definitions, financial meaning and timestamp rules. Add request, assignment, acceptance, arrival, trip-start and trip-end events; online supply; driver/session keys; refunds and costs. <b>Acceptance measures:</b> key integrity, event-order validity, agreed field coverage and reconciliation to an authoritative source.')
h('8.4 Predefine the evaluation',2)
p('Use randomized zone/time blocks where feasible and address spillover and clustering in the design. An illustrative independent two-proportion calculation from 62% to 65%, with 5% two-sided significance and 80% power, requires approximately 4,100 bookings per arm before design adjustments. This is a planning approximation, not a completed power analysis. Set the evaluation window, eligibility rules and stopping criteria in advance; avoid repeated significance checks followed by opportunistic stopping.')
p('The defensible next decision is to validate attribution and operational data, then run a limited measured test. Broad fleet reallocations, punitive driver policies, fare-model changes and customer-retention programmes are not established by the present evidence.')
br()

h('Appendix A. Data quality and metric definitions')
h('A.1 Identifier integrity and coverage',2)
p('There are no identical rows. Booking ID has 148,767 distinct values and 1,233 excess rows; 2,457 rows carry a reused ID. All observations are retained under a row key because deduplication would remove non-identical records without a supported rule. Unique-ID rows complete at 62.02%, versus 60.64% for reused-ID rows. This sensitivity split does not resolve upstream identity. (Q16, Q24)')
cov=q(17)[['status','rows','vtat_observations','value_observations','driver_rating_observations']].copy();cov.columns=['Status','Rows','VTAT observed','Value observed','Rating observed']
table('Table A1. Non-null field coverage by booking status',cov,widths=[147.28,80,86,87,87],note='Source: Q17. Counts are observations, not percentages. CTAT, distance and payment have the same broad completed/incomplete eligibility as value.')
p('Missingness is outcome-dependent: value, distance, CTAT and payment are present on completed/incomplete rides; ratings cover completed rides; no-driver rows lack VTAT. Do not impute zeros or discard failures. Round status proportions and weak segment/value-distance differences warrant caution about possible educational or synthetic structure, without proving how the file was generated.')
h('A.2 Metric definitions',2)
table('Table A2. Principal metric definitions',[
['Metric','Definition'],['Bookings','Number of selected source rows; not distinct Booking IDs.'],['Completion rate','Completed rows divided by all selected booking rows.'],['Cancellation rate','Driver plus customer cancellation rows divided by all selected rows.'],['Unsuccessful rate','Every non-Completed row divided by all selected rows.'],['Completed booking value','Sum of Booking Value on Completed rows only. Not recognized revenue.'],['Average completed value','Completed booking value divided by completed row count.'],['Bookings per observed day','Selected booking rows divided by distinct selected booking dates.'],['Rating / timing averages','Mean of eligible non-null values; report averages use Completed rows.'],['Recovery value','Selected request volume x completion uplift in percentage points / 100 x average completed value.']],widths=[145,342.28])
p('Status slicers condition the denominator: Completed alone gives 100% conditional completion. Clear selections to restore the 150,000-row baseline. KEEPFILTERS intersects outcome-specific measures with selected statuses.')

br()
h('Appendix B. Reproducibility and technical implementation')
p('The cleaned fact and calendar are stored in <font name="Arial-Bold">outputs/uber_analytics.sqlite</font>. Each of the 24 queries is available under <font name="Arial-Bold">sql/</font>, with a full result CSV under <font name="Arial-Bold">outputs/</font>. The execution log records timestamps, result row counts and SHA-256 hashes. <font name="Arial-Bold">report/Queries_Run.md</font> contains the exact SQL and previews. The SQL dialect is SQLite 3.25 or later, including window functions.')
p('The Power BI import model contains Bookings, Calendar, Vehicle, Status, Payment and Pickup, with five one-way relationships and 35 DAX measures. The six-page PBIX includes embedded data; local CSVs are needed for refresh. No Power BI Service connection or cloud account is required. Page names and operating instructions are documented in README.md.')
catalog=[['Reference','Executed analysis','Result rows']]
for path in sorted((ROOT/'sql').glob('*.sql')):
    catalog.append(['Q'+path.stem[:2],path.stem[3:].replace('_',' ').capitalize(),f'{len(pd.read_csv(ROOT/"outputs"/(path.stem+".csv"))):,}'])
table('Table B1. Executed query catalogue',catalog,widths=[68,339.28,80])
p('Rebuild with scripts/analyze.py, scripts/redesign_powerbi.py and scripts/build_professional_report.py. Refresh and save the dashboard in Desktop after regenerating its definitions. The field dictionary and source profile contain the full column inventory.')

br()
h('Appendix C. Sources and interpretation limits')
p('Dataset: <link href="https://www.kaggle.com/datasets/yashdevladdha/uber-ride-analytics-dashboard" color="#233F64">Yashdev Laddha, Uber Ride Analytics Dashboard, Kaggle</link>, downloaded 2 November 2026. Numerical findings were derived independently from ncr_ride_bookings.csv; the author-supplied sample PBIX is preserved separately. The source file hash is recorded in outputs/provenance.json.')
p('Technical references: Microsoft documentation for <link href="https://learn.microsoft.com/power-bi/developer/projects/projects-overview" color="#233F64">Power BI Desktop projects</link>, <link href="https://learn.microsoft.com/power-bi/developer/projects/projects-report" color="#233F64">report definitions</link>, and <link href="https://learn.microsoft.com/power-bi/developer/projects/projects-dataset" color="#233F64">semantic-model definitions</link>. These describe file formats; they do not support or endorse the operational recommendations.')
p('The extract has unverified provenance, sampling and representativeness. It cannot establish Uber-wide performance, causal explanations, realized financial returns or operational capacity requirements. Currency, distance units and timing definitions are unverified. Driver supply, coordinates, costs, commissions, refunds, persistent customer histories and experiment assignment are absent. Ratings exclude unsuccessful rides. Coverage ends on 30 December 2024. These limitations should accompany any presentation of the findings.')

class NumberedCanvas(canvas.Canvas):
    def __init__(self,*a,**kw):super().__init__(*a,**kw);self.saved=[]
    def showPage(self):self.saved.append(dict(self.__dict__));self._startPage()
    def save(self):
        count=len(self.saved)
        for state in self.saved:
            self.__dict__.update(state);self.setStrokeColor(colors.HexColor('#C4C4C4'));self.setLineWidth(.4);self.line(54,41,541.28,41)
            self.setFont('Arial',8);self.setFillColor(colors.HexColor('#555555'));self.drawString(54,27,'Uber Ride Analytics | Operational Performance Analysis');self.drawRightString(541.28,27,f'Page {self._pageNumber} of {count}')
            super().showPage()
        super().save()
def header(c,d):
    if d.page>1:
        c.saveState();c.setFont('Arial',8);c.setFillColor(colors.HexColor('#555555'));c.drawString(54,810,'Uber Ride Analytics');c.drawRightString(541.28,810,'2 November 2026');c.setStrokeColor(colors.HexColor('#D0D0D0'));c.setLineWidth(.4);c.line(54,800,541.28,800);c.restoreState()
class ReportDoc(SimpleDocTemplate):
    def afterFlowable(self,f):
        if isinstance(f,Paragraph) and f.style.name=='H1':
            key='section'+str(self.seq.nextf('heading'));self.canv.bookmarkPage(key);self.canv.addOutlineEntry(f.getPlainText(),key,0,False)
doc=ReportDoc(str(OUT/'Uber_Analytics_Report.pdf'),pagesize=(595.28,841.89),leftMargin=54,rightMargin=54,topMargin=56,bottomMargin=58,title='Uber Ride Analytics: Operational Performance Analysis',author='Analytics Project')
doc.build(story,onFirstPage=header,onLaterPages=header,canvasmaker=NumberedCanvas)

css='''body{font:16px/1.65 Arial,sans-serif;color:#222;background:white;max-width:900px;margin:48px auto;padding:0 28px}h1{font-size:28px;margin-bottom:6px}h2{font-size:22px;margin-top:36px}h3{font-size:18px;margin-top:24px}.subtitle{font-size:19px}.meta,.note{font-size:13px;color:#555}.caption{font-weight:bold;font-size:14px;margin:22px 0 7px}p{margin:0 0 14px}.tbl{overflow:auto}table{width:100%;border-collapse:collapse;font-size:14px;margin-bottom:16px}th,td{text-align:left;vertical-align:top;padding:9px 10px;border-bottom:1px solid #ddd}th{background:#eee;border-top:1px solid #555;border-bottom:1px solid #777}svg{width:100%;height:auto;max-height:300px}svg text{font-family:Arial,sans-serif}a{color:#233f64}@media print{body{margin:0;max-width:none}.pagebreak{break-after:page}}'''
ht=['<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Uber Ride Analytics: Operational Performance Analysis</title><style>'+css+'</style></head><body>'];md=[]
for kind,value in content:
    if kind=='table':
        ht.append('<div class="tbl"><table><thead><tr>'+''.join('<th>'+html.escape(v)+'</th>' for v in value[0])+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+html.escape(v)+'</td>' for v in row)+'</tr>' for row in value[1:])+'</tbody></table></div>')
        md += ['| '+' | '.join(value[0])+' |','| '+' | '.join(['---']*len(value[0]))+' |']+['| '+' | '.join(row)+' |' for row in value[1:]]+['']
    elif kind=='figure':
        s=renderSVG.drawToString(fig);s=s.decode() if isinstance(s,bytes) else s;ht.append(re.sub(r'<\?xml[^>]*>|<!DOCTYPE[^>]*>','',s));md += ['Hourly booking counts are available in outputs/05_hour_demand.csv.\n']
    elif kind=='break':ht.append('<div class="pagebreak"></div>')
    else:
        web=re.sub(r'<link href="([^"]+)"[^>]*>(.*?)</link>',r'<a href="\1">\2</a>',value)
        web=web.replace('<font name="Arial-Bold">','<strong>').replace('</font>','</strong>')
        tag={'title':'h1','h1':'h2','h2':'h3'}.get(kind,'p');ht.append(f'<{tag} class="{kind}">'+web+f'</{tag}>')
        markdown=re.sub(r'<link href="([^"]+)"[^>]*>(.*?)</link>',r'[\2](\1)',value)
        clean=re.sub('<[^>]+>','',markdown.replace('<br/>','\n'));md += [('# ' if kind=='title' else '## ' if kind=='h1' else '### ' if kind=='h2' else '')+html.unescape(clean)+'\n']
(OUT/'Uber_Analytics_Report.html').write_text(''.join(ht)+'</body></html>',encoding='utf-8')
(OUT/'Uber_Analytics_Report.md').write_text('\n'.join(md),encoding='utf-8')
(OUT/'report_content_professional.json').write_text(json.dumps(content,indent=2),encoding='utf-8')
from pypdf import PdfReader
r=PdfReader(OUT/'Uber_Analytics_Report.pdf')
print('Created conventional report:',len(r.pages),'pages; flowing sections, white pages, technical appendices.')
print([(i+1,len(pg.extract_text()),pg.extract_text()[:75]) for i,pg in enumerate(r.pages)])
