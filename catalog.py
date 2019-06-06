from json import load
from copy import deepcopy
from PyPDF2 import PdfFileMerger
from tempfile import NamedTemporaryFile
import subprocess
from io import BytesIO
from svgwrite import Drawing
from svgwrite.container import Style, Group
from svgwrite.shapes import Ellipse, Line, Rect
from svgwrite.path import Path
from svgwrite.text import Text

from utils import getJson, getText, km2mm
from formulae import sqrt2, sqrt1_2


class Catalog():
    """ Build a catalog for a planet format with cover and specimen
    """

    def __init__(self, planet):
        self.symbol = planet['serie']
        self.name = planet['name']
        # width and height of the document
        [self.w, self.h] = planet['a4equi']['format']
        # center x and y of the format
        self.c = [self.w / 2, self.h / 2]
        # margins x and y of the format
        self.m = [self.w / 16, self.h / 16]
        # number of folding to operate to get a format that can be filled in a A4
        self.times = planet['a4equi']['number']
        # radius of the planet scaled to planet's A4-like
        # [0] = equatorial, [1] = polar
        ratio = self.h / km2mm(planet['size_km'][1])
        self.radius = [ratio * km2mm(planet['radius'][0]), ratio * km2mm(planet['radius'][1])]
        self.fontSize = (self.radius[0] + self.radius[1]) / 2

        self.pages = []

        print(self.fontSize)

    def generate(self):
        doc = Drawing(
            size=(str(self.w) + 'mm', str(self.h) + 'mm'),
            viewBox='0 0 {} {}'.format(self.w, self.h),
            # profile='tiny',
        )
        doc.defs.add(Style(getText('stylesheet.css')))
        page = self.drawLines(deepcopy(doc))
        self.pages.append(self.drawCoverRecto(deepcopy(doc)))
        for n in range(self.times + 1):
            self.pages.append(self.drawPageRecto(deepcopy(page), n))

        return self

    def drawCoverRecto(self, page):
        page.add(Ellipse(center=self.c, r=self.radius))
        # planet's polar and equatorial radius
        page.add(Path(d='M{},{} v{} h{}'.format(
            self.c[0],
            self.c[1] - self.radius[1],
            self.radius[1],
            self.radius[0]
        )))
        # title (greek caps)
        page.add(Text(self.symbol, insert=self.c, id='cover-text', class_='center'))
        page.add(Text('1', insert=(self.c[0], self.m[1] + 5), class_='center'))
        page.add(Text(
            '√2',
            insert=(self.m[0] + 5, self.c[1]),
            transform='rotate(-90 {} {})'.format(self.m[0] + 5, self.c[1]),
            class_='center'
        ))
        page.add(Text(
            '{}0 -> {}{}'.format(self.symbol, self.symbol, self.times),
            insert=(self.c[0], self.h - self.m[1] - 5),
            class_='center'
        ))
        page.add(Text(
            '{}0 ±=== {} SURFACE'.format(self.symbol, self.name.upper()),
            insert=(self.c[0], self.h - self.m[1] - 3 - (self.c[1] - self.radius[1] - self.m[1]) / 2),
            class_='center'
        ))

        return page

    def drawCoverVerso(self, page):
        pass

    def drawLines(self, page):
        lines = Group()
        w, h = self.w, self.h
        thickness = 1
        number = 1
        for n in range(1, 21):
            if n % 2 != 0:
                h /= 2
                line = 'M{},{} h{}'.format(self.w - w, h, w)
            else:
                w /= 2
                line = 'M{},{} v{}'.format(self.w - w, 0, h)
            lines.add(Path(d=line, stroke_width=round(thickness, 3)))
            number += 1
            thickness *= sqrt1_2

        page.add(lines)
        return page

    def drawPageRecto(self, page, number):
        w, h = self.w, self.h
        page.add(Text(self.symbol + str(number), insert=self.c, class_='center f0'))
        number += 1
        for n in range(1, 21):
            if n % 2 != 0:
                h /= 2
                textPos = [self.w - w / 2, h + h / 2]
            else:
                w /= 2
                textPos = [self.w - w - w / 2, h / 2]
            page.add(Text(self.symbol + str(number), insert=textPos, class_='center f' + str(n)))
            number += 1
        return page

    def drawPageVerso(self, page):
        pass

    def saveAsSVG(self, folder='print/svg/', page=None):
        ''' Generate every svg as single files.
        '''
        for i, page in enumerate(self.pages):
            print(i, page)
            page.saveas('{}{}-p{}.svg'.format(folder, self.name, i), pretty=True)

    def saveAsPDF(self, folder='print/'):
        ''' Generate a single pdf with every page.
        '''
        pdf = PdfFileMerger()
        for page in self.pages:
            # Had to use a temp file so inkscape can open it.
            # Had to use inkscape since other svg2pdf converters can't manage
            # 'font-variant-ligature' nor 'dominant-baseline' css rules.
            with NamedTemporaryFile() as temp:
                temp.write(page.tostring().encode('utf-8'))
                temp.flush()
                process = subprocess.run(
                    ['inkscape', temp.name, '--export-pdf=-'],
                    input=temp.read(),
                    stdout=subprocess.PIPE
                )
                pdf.append(BytesIO(process.stdout))

        with open('{}{}.pdf'.format(folder, self.name.lower()), 'wb') as target:
            pdf.write(target)

if __name__ == '__main__':
    earth = Catalog(getJson('series/earth.json'))
    earth.generate()
    # earth.saveAsSVG()
    earth.saveAsPDF()
