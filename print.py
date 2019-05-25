from json import load
from svgwrite import Drawing
from svgwrite.shapes import Ellipse, Line
from svgwrite.text import Text

from formats import getJson
from utils import km2mm


def getNewDocument(name, width, height):
    return Drawing(
        size=(str(width) + 'mm', str(height) + 'mm'),
        viewBox='0 0 {} {}'.format(width, height),
        # profile='tiny',
    )

def getEllipseSize(radius, baseFormat, a4equi):
    ratio = a4equi[1] / km2mm(baseFormat[1])
    return [ratio * km2mm(radius[0]),
            ratio * km2mm(radius[1])]

def genCover(planet):
    [width, height] = planet['a4equi']['format']
    doc = getNewDocument(planet['name'] + '-cover', width, height)
    doc.defs.add(doc.style('text {font-size: 16px}'))
    center = [width/2, height/2]
    ellRadius = getEllipseSize(planet['radius'], planet['size_km'], [width, height])
    ellipse = Ellipse(center=center, r=ellRadius)
    # doc.add(ellipse)
    polarRadius = Line(start=center, end=[center[0], center[1] - ellRadius[1]])
    equaRadius = Line(start=center, end=[center[0] + ellRadius[0], center[1]])
    doc.add(polarRadius)
    doc.add(equaRadius)

    title = Text(planet['serie'], insert=center, text_anchor='middle', dominant_baseline='middle', font_family='Fira Code', font_size="65")
    doc.add(title)
    return doc

if __name__ == '__main__':
    earth = getJson('series/earth.json')
    cover = genCover(earth)
    cover.saveas('cover.svg', pretty=True)
