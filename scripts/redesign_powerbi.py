"""NCR / Ride Atlas: six deliberately different native Power BI compositions.

Keeps the original dashboard intact. Generates a separate report and model.
"""
from pathlib import Path
import json, copy, shutil, re

ROOT=Path(__file__).resolve().parents[1]; BASE=ROOT/'powerbi'
REPORT=BASE/'Uber Ride Atlas.Report'; MODEL=BASE/'Uber Ride Atlas.SemanticModel'
INK='#262338'; PAPER='#F5F0E7'; ORANGE='#D95D39'; LILAC='#ACA2D2'; MUTED='#777184'; LINE='#D9D0C7'; WHITE='#FFFCF7'
def write(p,d):
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2),encoding='utf-8')
def lit(v):
    value=("'"+v.replace("'","''")+"'") if isinstance(v,str) else str(v).lower() if isinstance(v,bool) else str(v)+'D'
    return {'expr':{'Literal':{'Value':value}}}
def color(c):return {'solid':{'color':lit(c)}}
def source(t,c,m=False):return {('Measure' if m else 'Column'):{'Expression':{'SourceRef':{'Entity':t}},'Property':c}}
def proj(t,c,m=False,label=None):
    d={'field':source(t,c,m),'queryRef':t+'.'+c,'nativeQueryRef':c}
    if label:d['displayName']=label
    return d

old=json.loads((BASE/'Uber Ride Atlas.SemanticModel/model.bim').read_text(encoding='utf-8-sig'))
names=['Bookings','Calendar','Vehicle','Status','Payment','Pickup']
tables=copy.deepcopy([t for t in old['model']['tables'] if t['name'] in names])
for t in tables:
    for c in t['columns']:c.pop('variations',None)
fact=next(t for t in tables if t['name']=='Bookings')
extra={
'Failure Rows':('IF([Unsuccessful] > 0, [Unsuccessful])','#,0'),
'Driver Failure Share':('DIVIDE([Driver Cancellations], [Unsuccessful])','0.0%'),
'VTAT Observed':('COUNT(Bookings[avg_vtat])','#,0'),
'CTAT Observed':('COUNT(Bookings[avg_ctat])','#,0'),
'Value Observed':('COUNT(Bookings[booking_value])','#,0'),
'Rating Observed':('COUNT(Bookings[driver_rating])','#,0'),
'Completed Value Millions':('DIVIDE([Completed Booking Value], 1000000)','0.00"m"'),
'Peak Hour':('VAR h = TOPN(1, ADDCOLUMNS(VALUES(Bookings[hour]), "n", [Bookings]), [n], DESC, Bookings[hour], ASC) RETURN FORMAT(MAXX(h, Bookings[hour]), "00") & ":00"',''),
'Peak Hour Requests':('MAXX(ADDCOLUMNS(VALUES(Bookings[hour]), "n", [Bookings]), [n])','#,0'),
'Customer Cancellations':('CALCULATE([Bookings], KEEPFILTERS(Bookings[status]="Cancelled by Customer"))','#,0'),
}
fact['measures'] = [x for x in fact['measures'] if x['name'] not in extra]
fact['measures'] += [{'name':n,'expression':e,'formatString':f,'displayFolder':'Atlas / Editorial measures'} for n,(e,f) in extra.items()]
rels=[r for r in old['model']['relationships'] if r['fromTable'] in names and r['toTable'] in names]
for t in tables:
    for part in t.get('partitions',[]):
        exp=part['source']['expression']
        exp='\n'.join(exp) if isinstance(exp,list) else exp
        exp=re.sub(r'File\.Contents\("[^\"]*/data/([^\"/]+)"\)',r'File.Contents(DataFolder & "/\1")',exp)
        part['source']['expression']=exp
write(MODEL/'model.bim',{'compatibilityLevel':1600,'model':{'culture':'en-US','defaultPowerBIDataSourceVersion':'powerBI_V3','expressions':[{'name':'DataFolder','kind':'m','expression':json.dumps(str(ROOT/'data').replace('\\','/'))+' meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]'}],'tables':tables,'relationships':rels,'annotations':[{'name':'PBI_QueryOrder','value':json.dumps(names)},{'name':'__PBI_TimeIntelligenceEnabled','value':'0'}]}})
write(MODEL/'definition.pbism',{'version':'4.2','settings':{'qnaEnabled':False}})
write(BASE/'Uber Ride Atlas.pbip',{'version':'1.0','artifacts':[{'report':{'path':REPORT.name}}],'settings':{'enableAutoRecovery':True}})
write(REPORT/'definition.pbir',{'version':'4.0','datasetReference':{'byPath':{'path':'../'+MODEL.name}}})
write(REPORT/'definition/version.json',{'$schema':'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/versionMetadata/1.0.0/schema.json','version':'2.0.0'})
theme={'name':'NCR | Ink & Terracotta','dataColors':[ORANGE,INK,LILAC,'#D6A84B','#8A728B','#B8ACA0'],'background':PAPER,'foreground':INK,'tableAccent':ORANGE,
 'visualStyles':{'*':{'*':{'title':[{'fontColor':{'solid':{'color':INK}},'fontFamily':'Segoe UI Semibold','fontSize':13}],'labels':[{'color':{'solid':{'color':INK}},'fontSize':12}],'categoryAxis':[{'labelColor':{'solid':{'color':MUTED}},'fontSize':11}],'valueAxis':[{'labelColor':{'solid':{'color':MUTED}},'fontSize':11}]}}}}
write(BASE/'Ride Atlas Theme.json',theme)
theme_path=REPORT/'StaticResources/RegisteredResources/AtlasTheme.json';write(theme_path,theme)
write(REPORT/'definition/report.json',{'$schema':'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/report/3.1.0/schema.json',
'themeCollection':{'customTheme':{'name':'AtlasTheme','type':'RegisteredResources','reportVersionAtImport':{'visual':'2.4.0','report':'3.1.0','page':'2.0.0'}}},
'resourcePackages':[{'name':'RegisteredResources','type':'RegisteredResources','items':[{'name':'AtlasTheme','path':'AtlasTheme.json','type':'CustomTheme'}]}],
'settings':{'useEnhancedTooltips':True,'exportDataMode':'AllowSummarized'}})
pages=[];visuals=[]
page_dir=(REPORT/'definition/pages').resolve()
assert page_dir.is_relative_to(ROOT.resolve()) and page_dir.parent.parent.name=='Uber Ride Atlas.Report'
if page_dir.exists():shutil.rmtree(page_dir)
def save(f,n,v,x,y,w,h):
    d={'$schema':'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.4.0/schema.json','name':f.name+'_'+n,'position':{'x':x,'y':y,'z':len(visuals),'height':h,'width':w,'tabOrder':len(visuals)},'visual':v}
    write(f/'visuals'/n/'visual.json',d);visuals.append(d)
def boxprops(bg=None):
    d={'background':[{'properties':{'show':lit(bg is not None),'color':color(bg or PAPER),'transparency':lit(0)}}],'border':[{'properties':{'show':lit(False)}}],'padding':[{'properties':{side:lit(0) for side in ['top','bottom','left','right']}}]}
    return d
def text(f,n,s,x,y,w,h,size=13,c=INK,bg=None,font='Segoe UI',bold=False):
    paras=[{'textRuns':[{'value':line,'textStyle':{'fontFamily':font,'fontSize':str(size)+'pt','color':c,'fontWeight':'bold' if bold else 'normal'}}]} for line in s.split('\n')]
    save(f,n,{'visualType':'textbox','objects':{'general':[{'properties':{'paragraphs':paras}}]},'visualContainerObjects':boxprops(bg)},x,y,w,h)
def block(f,n,x,y,w,h,bg):text(f,n,'',x,y,w,h,1,bg,bg)
def metric(f,n,m,x,y,w,h,size=48,c=ORANGE,bg=None):
    save(f,n,{'visualType':'card','query':{'queryState':{'Values':{'projections':[proj('Bookings',m,True)]}}},'objects':{'labels':[{'properties':{'fontSize':lit(size),'color':color(c),'labelDisplayUnits':{'expr':{'Literal':{'Value':'1L'}}}}}],'categoryLabels':[{'properties':{'show':lit(False)}}]},'visualContainerObjects':boxprops(bg)},x,y,w,h)
def slicer(f,n,t,c,title,x):
    v={'visualType':'slicer','query':{'queryState':{'Values':{'projections':[proj(t,c,label=title)]}}},'objects':{'data':[{'properties':{'mode':lit('Dropdown')}}],'header':[{'properties':{'show':lit(False)}}],'items':[{'properties':{'fontSize':lit(10),'fontColor':color(INK)}}]},'visualContainerObjects':boxprops('#E8E1DB')}
    text(f,n+'_label',title.upper(),x,23,204,20,9,MUTED,bold=True)
    save(f,n,v,x,47,204,43)
def page(i,title,sub,tag):
    name=f'atlas{i:02}';pages.append(name);f=REPORT/'definition/pages'/name
    write(f/'page.json',{'$schema':'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.0.0/schema.json','name':name,'displayName':f'{i:02} / {tag}','displayOption':'FitToPage','width':1440,'height':810,'objects':{'background':[{'properties':{'color':color(PAPER),'transparency':lit(0)}}]}})
    text(f,'title',title,28,26,680,62,30,INK,font='Segoe UI Semibold')
    slicer(f,'month','Calendar','month','Month',750)
    slicer(f,'vehicle','Vehicle','vehicle_type','Vehicle',976)
    slicer(f,'status','Status','status','Outcome',1202)
    text(f,'subtitle',sub,30,105,1376,32,12,MUTED)
    block(f,'rule',28,142,1380,2,LINE)
    text(f,'footer',f'NCR RIDE ANALYTICS     {i:02} / 06     |     01 JAN - 30 DEC 2024     |     PUBLIC DATA     |     SOURCE UNITS UNVERIFIED',28,782,1380,24,9,MUTED)
    return f
def chart(f,n,title,typ,cat,ms,x,y,w,h,c=ORANGE,sort=None,table_widths=None,labels=None,rowpad=8):
    pp=[proj(*cat,label=(labels or [None])[0])]+[proj('Bookings',m,True,label=labels[j+1] if labels else None) for j,m in enumerate(ms)]
    qs={'Values':{'projections':pp}} if typ=='tableEx' else {'Category':{'projections':[proj(*cat)]},'Y':{'projections':[proj('Bookings',m,True) for m in ms]}}
    query={'queryState':qs}
    query['sortDefinition']={'sort':[{'field':source('Bookings',sort,True) if sort else source(*cat),'direction':'Descending' if sort else 'Ascending'}],'isDefaultSort':False}
    con=boxprops(None);con['title']=[{'properties':{'show':lit(True),'text':lit(title),'fontSize':lit(13),'fontColor':color(INK),'fontFamily':lit('Segoe UI Semibold')}}]
    objects={}
    if typ=='tableEx':
        objects={'grid':[{'properties':{'rowPadding':lit(rowpad),'gridVertical':lit(False),'gridHorizontal':lit(True),'gridHorizontalColor':color(LINE),'outlineColor':color(LINE),'textSize':lit(13)}}],
         'columnHeaders':[{'properties':{'fontSize':lit(11),'fontColor':color(PAPER),'backColor':color(INK),'wordWrap':lit(True),'autoSizeColumnWidth':lit(False)}}],
         'values':[{'properties':{'fontSize':lit(13),'fontColor':color(INK),'backColor':color(PAPER),'alternateBackColor':color('#EAE3DA'),'wordWrap':lit(False)}}],
         'total':[{'properties':{'fontSize':lit(13),'fontColor':color(ORANGE),'backColor':color('#E3DBD2'),'totals':lit(True)}}]}
        if table_widths:objects['columnWidth']=[{'selector':{'metadata':p['queryRef']},'properties':{'value':lit(width)}} for p,width in zip(pp,table_widths)]
    else:
        objects={'dataPoint':[{'properties':{'defaultColor':color(c)}}],
         'categoryAxis':[{'properties':{'labelColor':color(MUTED),'fontSize':lit(11),'showAxisTitle':lit(False)}}],
         'valueAxis':[{'properties':{'labelColor':color(MUTED),'fontSize':lit(10),'showAxisTitle':lit(False),'gridlineColor':color(LINE)}}],
         'legend':[{'properties':{'show':lit(len(ms)>1),'fontSize':lit(10),'labelColor':color(MUTED)}}]}
        if len(ms)>1:objects['dataPoint'] += [{'selector':{'metadata':'Bookings.'+m},'properties':{'fill':color(cc)}} for m,cc in zip(ms,[INK,ORANGE,LILAC])]
    save(f,n,{'visualType':typ,'query':query,'objects':objects,'visualContainerObjects':con},x,y,w,h)
def kicker(f,n,s,x,y,w=600,c=MUTED):text(f,n,s.upper(),x,y,w,25,9,c,bold=True)

# 01: typographic opening, one oversized live metric, outcome bars and a thin demand ribbon.
f=page(1,'Booking Performance','Completion rate, booking outcomes and monthly request volume.','Performance')
kicker(f,'hero_label','Requests that became completed rides',220,157,420)
metric(f,'hero','Completion Rate',212,187,420,142,80,ORANGE)
text(f,'hero_note','Completion is the central operating measure.\nEvery unsuccessful request stays in the denominator.',224,338,412,67,13,INK)
block(f,'hero_rule',224,421,390,2,LINE)
kicker(f,'count_label','Selected booking rows',224,441,190)
metric(f,'count','Bookings',222,467,220,63,28,INK)
kicker(f,'loss_label','Unsuccessful',445,441,170)
metric(f,'loss','Unsuccessful',437,467,190,63,28,ORANGE)
chart(f,'outcomes','Booking Outcomes','barChart',('Status','status'),['Bookings'],675,156,733,371,ORANGE,'Bookings')
block(f,'lower_rule',220,554,1188,2,LINE)
chart(f,'ribbon','Monthly Bookings','lineChart',('Calendar','month'),['Bookings','Completed'],220,574,1188,177,INK)

# 02: a wide demand clock with a contrasting annotation column; dense useful pickup table below.
f=page(2,'Demand by Hour','Hourly demand, weekday exposure and pickup availability.','Demand')
chart(f,'hour','Bookings by Hour','clusteredColumnChart',('Bookings','hour'),['Bookings'],220,153,867,337,ORANGE)
block(f,'rush_panel',1120,151,288,338,INK)
kicker(f,'peak_label','Busiest selected hour',1140,176,245,LILAC)
metric(f,'peak','Peak Hour',1134,210,258,90,47,PAPER)
metric(f,'peak_n','Peak Hour Requests',1140,308,246,62,29,LILAC)
text(f,'peak_caption','requests in that hour\n\nHourly counts identify demand.\nThey do not measure fleet capacity.',1140,376,244,99,11,PAPER)
chart(f,'weekday','Bookings per Observed Weekday','barChart',('Calendar','weekday'),['Bookings per Observed Day'],220,522,460,231,LILAC)
chart(f,'pickups','Pickup Availability','tableEx',('Pickup','pickup'),['Bookings','No Driver','No Driver Rate'],721,522,687,231,sort='No Driver',table_widths=[247,135,135,148],labels=['Pickup area','Requests','No driver','No-driver %'],rowpad=6)

# 03: failure reasons are a plot, not a sparse 13-row table with a large empty container.
f=page(3,'Cancellation Analysis','Separate cancellation reasons, no-driver outcomes and incomplete rides.','Cancellations')
chart(f,'reasons','Unsuccessful Booking Reasons','barChart',('Bookings','failure_reason'),['Failure Rows'],220,155,843,595,ORANGE,'Failure Rows')
block(f,'separator',1094,155,2,594,LINE)
kicker(f,'driver_label','Driver cancellations',1130,165,270)
metric(f,'driver_n','Driver Cancellations',1112,196,294,104,51,INK)
metric(f,'driver_share','Driver Failure Share',1120,319,280,92,42,ORANGE)
text(f,'driver_text','of unsuccessful bookings\nare driver cancellations.',1135,416,264,60,13,INK)
block(f,'scenario_line',1130,507,260,2,LINE)
kicker(f,'scenario_label','One-point recovery scenario',1130,533,260)
metric(f,'scenario','Recovery Value 1pp',1122,568,280,77,31,INK)
text(f,'scenario_note','Additional recorded value at +1pp\ncompletion and current average value.\nA scenario, not a profit forecast.',1134,662,263,82,11,MUTED)

# 04: service ledger spans the entire main width; 7 rows sized to its frame.
f=page(4,'Vehicle and Payment Analysis','Service performance and completed booking value. Source currency is unspecified.','Value')
chart(f,'ledger','Vehicle Performance','tableEx',('Vehicle','vehicle_type'),['Bookings','Completion Rate','Completed Booking Value','Avg Completed Value'],220,156,1188,333,sort='Completed Booking Value',table_widths=[251,195,195,283,242],labels=['Service','Requests','Completion','Completed value','Average value'],rowpad=5)
chart(f,'payment','Completed Bookings by Payment Method','barChart',('Payment','payment_method'),['Completed'],220,527,576,220,LILAC,'Completed')
chart(f,'value_month','Monthly Completed Booking Value','lineChart',('Calendar','month'),['Completed Booking Value'],836,527,572,220,ORANGE)

# 05: large side-by-side rating numerals; the timing bands become a readable chart.
f=page(5,'Ratings and Timing','Ratings describe completed rides; unsuccessful rides have no ratings.','Ratings')
kicker(f,'driver_rating_label','Driver rating / completed',220,160,390)
metric(f,'driver_rating','Driver Rating',215,192,390,109,62,INK)
kicker(f,'customer_rating_label','Customer rating / completed',652,160,405)
metric(f,'customer_rating','Customer Rating',644,192,405,109,62,ORANGE)
text(f,'rating_note','Completed rides only.\nFailures are unrated.',1115,174,286,112,19,INK,font='Segoe UI Semibold')
block(f,'experience_rule',220,326,1188,2,LINE)
chart(f,'service_ratings','Ratings by Vehicle','tableEx',('Vehicle','vehicle_type'),['Rated Completed','Driver Rating','Customer Rating'],220,356,715,382,table_widths=[235,164,147,147],labels=['Service','Rated rides','Driver','Customer'],rowpad=8)
chart(f,'timing_bands','Completion Rate by VTAT Band','barChart',('Bookings','vtat_band'),['Completion Rate'],980,355,428,261,LILAC)
text(f,'timing_note','Do not read the bands as cause and effect.\nNo-driver rows lack VTAT; the pattern is\nnon-monotonic. Timing units are unverified.',987,652,411,86,12,MUTED)

# 06: full-width field-coverage ledger and a deliberately asymmetric identifier callout.
f=page(6,'Data Quality','Field coverage, reused booking IDs and metric definitions.','Data quality')
chart(f,'coverage','Field Coverage by Booking Status','tableEx',('Status','status'),['Bookings','VTAT Observed','CTAT Observed','Value Observed','Rating Observed'],220,157,1188,279,table_widths=[294,174,174,174,174,176],labels=['Outcome','Rows','VTAT','CTAT','Value','Rating'],rowpad=4)
block(f,'audit_line',220,468,1188,2,LINE)
kicker(f,'id_label','Excess rows beyond distinct booking IDs',220,501,570)
metric(f,'id_count','Excess ID Rows',209,538,560,121,70,ORANGE)
text(f,'id_note','Retained, not silently deleted.\nNo exact duplicate rows were found.',224,676,543,64,14,INK)
block(f,'contract_panel',829,501,579,242,INK)
text(f,'contract_head','METRIC DEFINITIONS',850,519,534,27,12,LILAC,bold=True)
text(f,'contract_text','01   Count source rows, not distinct booking IDs.\n02   Completed value excludes incomplete rides.\n03   Ratings cover completed rides only.\n04   Currency and timing definitions are unverified.\n05   Public-data provenance limits generalization.',850,564,534,159,13,PAPER)

# Expand analytical content into the space formerly occupied by the rail.
# Header controls stay in a shallow horizontal strip.
fixed={'title','subtitle','rule','footer','month','month_label','vehicle','vehicle_label','status','status_label'}
scale=1380/1188
for p in page_dir.rglob('visual.json'):
    d=json.loads(p.read_text());short=p.parent.name
    if short not in fixed:
        pos=d['position'];pos['x']=round(28+(pos['x']-220)*scale,2);pos['width']=round(pos['width']*scale,2)
        if d['visual']['visualType']=='tableEx':
            for col in d['visual']['objects'].get('columnWidth',[]):
                val=col['properties']['value']['expr']['Literal']['Value'];col['properties']['value']=lit(round(float(val[:-1])*scale,1))
        write(p,d)
write(REPORT/'definition/pages/pages.json',{'$schema':'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.0.0/schema.json','pageOrder':pages,'activePageName':pages[0]})
write(BASE/'atlas_build_manifest.json',{'design':'NCR / Ride Atlas','palette':{'ink':INK,'paper':PAPER,'terracotta':ORANGE,'lilac':LILAC},'pages':len(pages),'visuals':len(visuals),'measures':len(fact['measures']),'desktop_validation':'pending'})
print(f'Built Ride Atlas: {len(pages)} pages, {len(visuals)} visuals. Dashboard source definitions rebuilt.')
