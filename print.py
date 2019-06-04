from json import load
from svgwrite import Drawing
from svgwrite.container import Style, Group
from svgwrite.shapes import Ellipse, Line, Rect
from svgwrite.path import Path
from svgwrite.text import Text

from utils import getJson, getText, km2mm

def getNewDocument(width, height):
    return Drawing(
        size=(str(width) + 'mm', str(height) + 'mm'),
        viewBox='0 0 {} {}'.format(width, height),
        # profile='tiny',
    )

def getEllipseSize(radius, baseFormat, a4equi):
    ratio = a4equi[1] / km2mm(baseFormat[1])
    return {
        'equa': ratio * km2mm(radius[0]),
        'polar': ratio * km2mm(radius[1])
    }

def genCover(planet, width, height, marges):
    doc = getNewDocument(width, height)
    doc.defs.add(Style(getText('stylesheet.css')))
    center = [width/2, height/2]
    # get scaled size of the planet radius
    ellRadius = getEllipseSize(planet['radius'], planet['size_km'], [width, height])

    doc.add(Ellipse(center=center, r=[ellRadius['equa'], ellRadius['polar']]))
    # planet's polar and equatorial radius
    doc.add(Path(d='M{},{} v{} h{}'.format(
        center[0],
        center[1] - ellRadius['polar'],
        ellRadius['polar'],
        ellRadius['equa']
    )))
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
        insert=(center[0], height - marges[1] - 3 - (center[1] - ellRadius['polar'] - marges[1]) / 2),
        class_='center'
    ))

    return doc

def genSpecimen(planet, width, height, marges, number):
    doc = getNewDocument(width, height)
    doc.defs.add(Style(getText('stylesheet.css')))
    center = [width/2, height/2]
    lines = Group()
    doc.add(lines)
    doc.add(Text(planet['serie'] + str(number), insert=center, class_='center f' + str(number)))

    w = width
    h = height
    thickness = 1
    number += 1
    for n in range(1, 21):
        if n % 2 != 0:
            h /= 2
            line = 'M{},{} h{}'.format(width - w, h, w)
            textPos = [width - w / 2, h + h / 2]
        else:
            w /= 2
            line = 'M{},{} v{}'.format(width - w, 0, h)
            textPos = [width - w - w / 2, h / 2]
        lines.add(Path(d=line, stroke_width=round(thickness, 3)))
        doc.add(Text(planet['serie'] + str(number), insert=textPos, class_='center f' + str(number)))
        number += 1
        thickness *= 0.7071067811865476

    return doc

if __name__ == '__main__':
    planet = getJson('series/earth.json')
    marges = [12.5, 17.625]
    [width, height] = planet['a4equi']['format']
    cover = genCover(planet, width, height, marges)
    cover.saveas('{}-cover.svg'.format(planet['name']), pretty=True)
    format0 = genSpecimen(planet, width, height, marges, 0)
    format0.saveas('{}-{}{}.svg'.format(planet['name'], planet['serie'], 0), pretty=True)
