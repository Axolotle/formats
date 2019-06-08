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
from formulae import sqrt2, sqrt1_2, radiusOfSphere


class Catalog():
    """ Build a catalog for a planet format with cover and specimen
    """

    def __init__(self, planet):
        self.symbol = planet['symbol']
        self.name = planet['name']
        # width and height of the document
        [self.w, self.h] = planet['a4like']
        # center x and y of the format
        self.c = [self.w / 2, self.h / 2]
        # margins x and y of the format
        self.m = [self.w / 16, self.h / 16]
        # number of folding to operate to get a format that can be filled in a A4
        self.times = planet['formats_mm'].index(planet['a4like']) + 1
        # radius of the planet scaled to planet's A4-like
        # [0] = equatorial, [1] = polar
        ratio = self.h / km2mm(planet['size_km'][1])
        self.radius = [ratio * km2mm(planet['radius'][0]), ratio * km2mm(planet['radius'][1])]
        self.fontSizes = [round(self.radius[1] * sqrt1_2**n, 3)
                          for n in range(21)]
        self.totalPages = 2 + self.times * 2
        self.pages = [None] * self.totalPages

    def generate(self, pages=None):
        doc = Drawing(
            size=(str(self.w) + 'mm', str(self.h) + 'mm'),
            viewBox='0 0 {} {}'.format(self.w, self.h),
        )
        doc.defs.add(Style(''.join(
            getText('data/stylesheet.css').replace('MAINFONTSIZE', str(self.fontSizes[8])
        ).split())))

        pageRecto = self.drawLines(deepcopy(doc))

        if pages == None:
            pages = range(self.totalPages)
        elif type(pages) is int:
            pages = [pages]

        for n in pages:
            print(n)
            if n == 0:
                self.pages[n] = self.drawCoverRecto(deepcopy(doc))
            elif n == 1:
                pass
            elif n % 2 == 0:
                self.pages[n] = self.drawPageRecto(deepcopy(pageRecto), round(n / 2 - 1))
            else:
                pass

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
        page.add(Text(
            self.symbol,
            insert=self.c,
            class_='center',
            style='font-size:{};'.format(self.fontSizes[0])
        ))
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
            lines.add(Path(d=line, style='stroke-width:{};'.format(round(thickness, 3))))
            number += 1
            thickness *= sqrt1_2

        page.add(lines)
        return page

    def drawPageRecto(self, page, number):
        w, h = self.w, self.h
        klass = 'center filledstroked'
        for i in range(0, 21):
            if i == 0:
                textPos = self.c
            elif i % 2 != 0:
                h /= 2
                textPos = [self.w - w / 2, h + h / 2]
            else:
                w /= 2
                textPos = [self.w - w - w / 2, h / 2]
            page.add(Text(
                self.symbol + str(i + number),
                insert=textPos,
                class_=klass,
                style='font-size:{};'.format(self.fontSizes[i])
            ))
            if i == 0:
                klass = 'center'

        return page

    def drawPageVerso(self, page):
        pass

    def saveAsSVG(self, folder='print/svg/'):
        ''' Save every generated svg as single files.
        '''
        for i, page in enumerate(self.pages):
            if page is not None:
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
    earth = Catalog(getJson('data/planets/earth.json'))
    earth.generate()
    earth.saveAsSVG()
    # earth.saveAsPDF()
