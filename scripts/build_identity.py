from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import random

ROOT = Path(__file__).resolve().parents[1]
random.seed(42)
font_path = Path('C:/Windows/Fonts/segoeui.ttf')
font = ImageFont.truetype(str(font_path), 224)
bounds = font.getbbox('harnakam')
mask = Image.new('L', (bounds[2] + 10, bounds[3] - bounds[1] + 10))
ImageDraw.Draw(mask).text((0, -bounds[1]), 'harnakam', font=font, fill=255)
mask = mask.resize((1064, 192), Image.Resampling.LANCZOS)
groups = [[] for _ in range(12)]
for y in range(0, 192, 4):
    for x in range(0, 1064, 4):
        if mask.getpixel((x,y)) < 100:
            continue
        color = '#7e8fc8' if random.random() < .045 else '#e2e0db'
        opacity = random.uniform(.78, 1)
        groups[(x//4+y//4)%12].append(f'<circle cx="{x+68}" cy="{y+105}" r="1.05" fill="{color}" opacity="{opacity:.2f}"/>')
head = '''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="410" viewBox="0 0 1200 410" role="img" aria-labelledby="title desc">
<title id="title">harnakam · Developer</title>
<desc id="desc">A name formed from points of light.</desc>
<style>@media(prefers-reduced-motion:reduce){.animated{display:none}.rest{display:inline}}.rest{display:none}</style>
<rect width="1200" height="410" fill="#080808"/>
'''
# Keep the name readable throughout; motion is a slow shimmer through its points.
static = ''.join(''.join(g) for g in groups)
animated = []
for i, group in enumerate(groups):
    animated.append(f'<g opacity="1"><animate attributeName="opacity" values="1;.65;1" dur="8s" begin="-{i*8/12:.3f}s" repeatCount="indefinite"/>{"".join(group)}</g>')
footer = '''<text x="68" y="365" fill="#cfcdc8" font-family="Segoe UI,Arial,sans-serif" font-size="22">Developer</text>
<path d="M1109 352h19v19m0-19-23 23" fill="none" stroke="#cfcdc8" stroke-width="1.3"/>
</svg>'''
# CSS declaration order must allow the reduced-motion preference to override defaults.
head = head.replace('@media(prefers-reduced-motion:reduce){.animated{display:none}.rest{display:inline}}.rest{display:none}', '.rest{display:none}@media(prefers-reduced-motion:reduce){.animated{display:none}.rest{display:inline}}')
(ROOT/'assets/identity.svg').write_text(head+'<g class="animated">'+''.join(animated)+'</g><g class="rest">'+static+'</g>'+footer, encoding='utf-8')
(ROOT/'assets/identity-still.svg').write_text(head+static+footer, encoding='utf-8')
print('Generated animated and still particle wordmarks')