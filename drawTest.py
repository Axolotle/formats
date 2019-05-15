from json import load
from svgwrite import Drawing
from svgwrite.container import Group
from svgwrite.shapes import Rect
from svgwrite.text import Text

from formats import getJson


def generateSVGFile():
    doc = Drawing('formats.svg',
        size=(str(1000) + 'mm', str(1000) + 'mm'),
        viewBox='0 0 {} {}'.format(1000, 1000),
        profile='tiny',
    )
    data = getJson('output.json')

    for planet in data:
        group = Group(id=planet['name'])
        group.add(Text(planet['name']))
        for size in planet['result']:
            rect = Rect((10, 10), (size[0], size[1]) )
            group.add(rect)
        doc.add(group)

    doc.save(pretty=True)

if __name__ == '__main__':
    generateSVGFile()
