"""Generate profile artwork from public GitHub data; Python standard library only."""
import collections
import datetime
import html
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
QUERY = '''query { user(login:"harnakam") {
 contributionsCollection { contributionCalendar { totalContributions weeks { contributionDays { contributionCount date } } } }
 repositories(first:100,privacy:PUBLIC,ownerAffiliations:OWNER,isFork:false) { nodes { name stargazerCount languages(first:10,orderBy:{field:SIZE,direction:DESC}) { edges { size node { name color } } } } }
} }'''
result = subprocess.run(['gh','api','graphql','-f','query='+QUERY], check=True, capture_output=True, text=True, encoding='utf-8')
payload = json.loads(result.stdout)
if payload.get('errors'):
    raise RuntimeError(payload['errors'])
user = payload['data']['user']
calendar = user['contributionsCollection']['contributionCalendar']
repos = [r for r in user['repositories']['nodes'] if r['name'] != 'harnakam']
languages = collections.Counter()
colors = {}
for repo in repos:
    for edge in repo['languages']['edges']:
        name = edge['node']['name']
        languages[name] += edge['size']
        colors[name] = edge['node']['color'] or '#9da7b5'
weeks = calendar['weeks']
days = [d for week in weeks for d in week['contributionDays']]
active = sum(d['contributionCount'] > 0 for d in days)
peak = max((d['contributionCount'] for d in days), default=0)
svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="520" viewBox="0 0 1200 520" role="img" aria-labelledby="title desc">',
 '<title id="title">GitHub activity and languages</title>',
 f'<desc id="desc">{calendar["totalContributions"]} contributions, {active} active days. Languages measured by bytes in public original repositories, excluding this profile.</desc>',
 '<rect width="1200" height="520" rx="12" fill="#0d1117"/>',
 '<style>text{font-family:Segoe UI,Arial,sans-serif;fill:#e6edf3}.label{font-size:15px;fill:#a5aebc}.value{font-size:38px;font-weight:600}</style>']
def text(x,y,value,cls='',extra=''):
    svg.append(f'<text x="{x}" y="{y}" class="{cls}" {extra}>{html.escape(str(value))}</text>')
text(40,43,'Activity',extra='font-size="21" font-weight="600"')
text(1160,43,days[0]['date']+' — '+days[-1]['date'],'label','text-anchor="end"')
for x,value,label in [(40,calendar['totalContributions'],'Contributions'),(330,active,'Active days'),(620,peak,'Best day'),(910,len(repos),'Public repositories')]:
    text(x,104,f'{value:,}','value')
    text(x,132,label,'label')
palette=['#202832','#33443d','#53755e','#8caf85','#d0e5b9']
for col,week in enumerate(weeks):
    for day in week['contributionDays']:
        row=(datetime.date.fromisoformat(day['date']).weekday()+1)%7
        count=day['contributionCount']
        level=0 if count==0 else min(4,1+(count>3)+(count>9)+(count>20))
        svg.append(f'<rect x="{40+col*21}" y="{162+row*21}" width="16" height="16" rx="3" fill="{palette[level]}"><title>{day["date"]}: {count} contributions</title></rect>')
text(40,335,'Less','label')
for i,color in enumerate(palette):
    svg.append(f'<rect x="{82+i*21}" y="322" width="16" height="16" rx="3" fill="{color}"/>')
text(193,335,'More','label')
svg.append('<path d="M40 365H1160" stroke="#28313d"/>')
text(40,401,'Languages',extra='font-size="21" font-weight="600"')
text(1160,401,'Public source · by size','label','text-anchor="end"')
top=languages.most_common(5)
other=sum(languages.values())-sum(v for _,v in top)
if other:
    top.append(('Other',other)); colors['Other']='#727e90'
total=sum(languages.values())
x=40
if total:
    for name,size in top:
        width=1120*size/total
        svg.append(f'<rect x="{x:.2f}" y="422" width="{width:.2f}" height="12" fill="{colors[name]}"/>')
        x+=width
    for i,(name,size) in enumerate(top):
        x=40+(i%3)*375; y=465+(i//3)*30
        svg.append(f'<circle cx="{x+5}" cy="{y-5}" r="5" fill="{colors[name]}"/>')
        text(x+20,y,f'{name}  {size/total:.1%}','label')
else:
    text(40,459,'No public language data yet.','label')
svg.append('</svg>')
(ROOT/'assets/activity.svg').write_text('\n'.join(svg)+'\n',encoding='utf-8')
print(f'Generated activity: {len(days)} days, {len(repos)} repositories, {len(languages)} languages')
# A separate compact composition keeps labels readable on narrow profiles.
svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="600" height="700" viewBox="0 0 600 700" role="img" aria-labelledby="title">', '<title id="title">GitHub activity: recent 16 weeks and public languages</title>', '<rect width="600" height="700" rx="12" fill="#0d1117"/>', '<style>text{font-family:Segoe UI,Arial,sans-serif;fill:#e6edf3}.label{font-size:22px;fill:#a5aebc}.value{font-size:42px;font-weight:600}</style>']
text(30,48,'Activity',extra='font-size="28" font-weight="600"')
for x,y,value,label in [(30,109,calendar['totalContributions'],'Contributions'),(320,109,active,'Active days'),(30,199,peak,'Best day'),(320,199,len(repos),'Public repos')]:
    text(x,y,f'{value:,}','value'); text(x,y+29,label,'label')
text(30,279,'Recent 16 weeks','label')
for col,week in enumerate(weeks[-16:]):
    for day in week['contributionDays']:
        row=(datetime.date.fromisoformat(day['date']).weekday()+1)%7
        count=day['contributionCount']
        level=0 if count==0 else min(4,1+(count>3)+(count>9)+(count>20))
        svg.append(f'<rect x="{30+col*34}" y="{302+row*25}" width="27" height="18" rx="3" fill="{palette[level]}"/>')
text(30,525,'Languages',extra='font-size="28" font-weight="600"')
for i,(name,size) in enumerate(top):
    x=30+(i%2)*285; y=573+(i//2)*43
    svg.append(f'<circle cx="{x+6}" cy="{y-7}" r="6" fill="{colors[name]}"/>')
    text(x+24,y,f'{name} {size/total:.1%}','label')
svg.append('</svg>')
(ROOT/'assets/activity-mobile.svg').write_text('\n'.join(svg)+'\n',encoding='utf-8')
