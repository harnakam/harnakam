"""Accept only passive SVG artwork from the isolated, read-only generation job."""
from pathlib import Path
import re
import xml.etree.ElementTree as ET

root = Path(__file__).resolve().parents[1]
allowed = {'svg','desc','title','metadata','defs','style','g','rect','path','circle','ellipse','line','polyline','polygon','text','tspan','clipPath','mask','linearGradient','radialGradient','stop'}
for name in ('snake.svg','snake-dark.svg'):
    source = root/'output'/'snake'/name
    if source.is_symlink() or source.stat().st_size > 2_000_000:
        raise ValueError('Unexpected artifact file')
    data = source.read_text(encoding='utf-8')
    if re.search(r'<!DOCTYPE|<!ENTITY|@import|https?://(?!www\.w3\.org/2000/svg)', data, re.I):
        raise ValueError('External reference in SVG')
    tree = ET.fromstring(data)
    if tree.tag != '{http://www.w3.org/2000/svg}svg':
        raise ValueError('Not SVG')
    for element in tree.iter():
        if element.tag.rsplit('}',1)[-1] not in allowed:
            raise ValueError('Unexpected SVG element: '+element.tag)
        for attribute, value in element.attrib.items():
            attribute=attribute.rsplit('}',1)[-1].lower()
            if attribute.startswith('on') or attribute in {'href','src'}:
                raise ValueError('Active attribute')
    for target in re.findall(r'url\((.*?)\)', data, re.I):
        if not target.strip(' "\'').startswith('#'):
            raise ValueError('External CSS URL')
    (root/'assets'/name).write_text(data,encoding='utf-8')
    print('Validated',name)