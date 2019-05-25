from json import load
from svgwrite import Drawing
from svgwrite.container import Style, Group
from svgwrite.shapes import Ellipse, Line, Rect
from svgwrite.text import Text

from utils import getJson, getText, km2mm

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

def genCover(planet, marges):
    [width, height] = planet['a4equi']['format']
    doc = getNewDocument(planet['name'] + '-cover', width, height)
    doc.defs.add(Style(getText('stylesheet.css')))
    center = [width/2, height/2]
    # get scaled size of the planet radius
    ellRadius = getEllipseSize(planet['radius'], planet['size_km'], [width, height])

    doc.add(Ellipse(center=center, r=ellRadius))
    # planet's polar radius
    doc.add(Line(start=center, end=[center[0], center[1] - ellRadius[1]]))
    # planet's equatorial radius
    doc.add(Line(start=center, end=[center[0] + ellRadius[0], center[1]]))
    # title (greek caps)
    doc.add(Text(planet['serie'], insert=center, id='cover-text', class_='center'))
    doc.add(Text('1', insert=(center[0], marges[1] + 5), class_='center'))
    doc.add(Text(
        '√2',
        insert=(marges[0] + 5, center[1]),
        transform='rotate(-90 {} {})'.format(marges[0] + 5, center[1]),
        class_='center'
    ))
    doc.add(Text(
        '{}0 -> {}{}'.format(planet['serie'], planet['serie'], planet['a4equi']['number']),
        insert=(center[0], height - marges[1] - 5),
        class_='center'
    ))
    doc.add(Text(
        '{}0 ±=== {} SURFACE'.format(planet['serie'], planet['name'].upper()),
        insert=(center[0], height - marges[1] - 3 - (center[1] - ellRadius[1] - marges[1]) / 2),
        class_='center'
    ))

    return doc

if __name__ == '__main__':
    marges = [12.5, 17.625]
    earth = getJson('series/earth.json')
    cover = genCover(earth, marges)
    cover.saveas('cover.svg', pretty=True)
