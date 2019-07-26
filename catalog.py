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
from svgwrite.text import Text, TSpan

from utils import getJson, getText, km2mm
from formulae import sqrt2, sqrt1_2, radiusOfSphere

distribution = getJson('data/formatsDistribution.json')

class Catalog():
    """ Build a catalog for a planet format with cover and specimen
    """

    def __init__(self, planet):
        self.symbol = planet['symbol']
        self.name = planet['name']
        self.area = planet['area']
        self.size = planet['size_km']
        # width and height of the document (A4 like) in mm
        [self.w, self.h] = planet['serieAequi']['4']['size']
        # center x and y of the document
        self.c = [self.w / 2, self.h / 2]
        # margins x and y of the document
        self.m = [self.w / 16, self.h / 16]
        # extra distance of text from line
        self.dist = 7
        # list of every formats in mm
        self.formats = planet['formats_mm']
        # area in km² of the format[0]
        self.format0area = self.formats[0][0] * self.formats[0][1] * 10**-12
        # number of folding to operate to get a format that can be filled in a A4
        self.times = planet['serieAequi']['4']['number']
        # radius of the planet scaled to planet's A4-like
        # [0] = equatorial, [1] = polar
        ratio = self.h / km2mm(planet['size_km'][1])
        self.realRadius = planet['radius']
        self.radius = [ratio * km2mm(rad) for rad in self.realRadius]
        self.fontSizes = [round(self.radius[1] * sqrt1_2**n, 3)
                          for n in range(21)]
        # define line-height for successive text span
        self.leading = self.fontSizes[8] * 1.2
        self.totalPages = 2 + self.times * 2
        self.pages = [None] * self.totalPages

    def generate(self, pages=None, paperSize=None):
        if paperSize is None:
            doc = Drawing(
                size=(str(self.w) + 'mm', str(self.h) + 'mm'),
                viewBox='0 0 {} {}'.format(self.w, self.h)
            )
        else:
            extraWidth = (paperSize[0] - self.w) / 2
            extraHeight = (paperSize[1] - self.h) / 2
            doc = self.drawCutLines(Drawing(
                size=(str(paperSize[0])+ 'mm', str(paperSize[1]) + 'mm'),
                viewBox='{} {} {} {}'.format(-extraWidth, -extraHeight, self.w + extraWidth * 2, self.h + extraHeight * 2)
            ), extraWidth, extraHeight)

        doc.defs.add(Style(''.join(
            getText('data/stylesheet.css').replace('MAINFONTSIZE', str(self.fontSizes[8])
        ).split())))

        pageRecto = self.drawLines(deepcopy(doc))
        pageVerso = self.drawHelpers(deepcopy(doc))

        if pages == None:
            pages = range(self.totalPages)
        elif type(pages) is int:
            pages = [pages]

        for n in pages:
            print('Generating SVG p{}…'.format(n))
            if n == 0:
                self.pages[n] = self.drawCoverRecto(deepcopy(doc))
            elif n == 1:
                self.pages[n] = self.drawCoverVerso(deepcopy(pageVerso))
            elif n % 2 == 0:
                self.pages[n] = self.drawPageRecto(deepcopy(pageRecto), round(n / 2) - 1)
            else:
                self.pages[n] = self.drawPageVerso(deepcopy(pageVerso), round((n - 1) / 2) - 1)

        return self

    def generateWebVersion(self):
        doc = Drawing(
            size=(str(self.w) + 'mm', str(self.h) + 'mm'),
            viewBox='0 0 {} {}'.format(self.w, self.h)
        )
        main = Group(id='main')
        main.add(Rect(insert=(0, 0), size=(self.w, self.h)))
        main.add(self.drawLinesSpiral())
        main.add(self.drawPageRectoSpiral(0))
        doc.add(main)

        return doc.tostring()

    def drawCutLines(self, page, mx, my):
        cutLines = Group()
        lines = [
            Path(d='M{0},0 h{2} M{1},0 h{2}'.format(-mx, self.w + 1, mx - 1), class_='cutLines'),
            Path(d='M{0},{3} h{2} M{1},{3} h{2}'.format(-mx, self.w + 1, mx - 1, self.h), class_='cutLines'),
            Path(d='M0,{0} v{2} M0,{1} v{2}'.format(-my, self.h + 1, my - 1), class_='cutLines'),
            Path(d='M{3},{0} v{2} M{3},{1} v{2}'.format(-my, self.h + 1, my - 1, self.w), class_='cutLines')
        ]
        # cutLines.add(Rect(insert=(0, 0), size=(200, 282)))
        for line in lines:
            cutLines.add(line)
        page.add(cutLines)
        return page

    def drawHelpers(self, page):
        helpers = Group()
        arrowcmd = 'M{},{} l{},{} l{},{}'
        elems = [
            # Arrows
            Path(d=arrowcmd.format(self.m[0]-2, 2.7, 2, -2, 2, 2)),
            Path(d=arrowcmd.format(self.m[0]-2, self.h-2.7, 2, 2, 2, -2)),
            Path(d=arrowcmd.format(2.7, self.m[1]-2, -2, 2, 2, 2)),
            Path(d=arrowcmd.format(self.w-2.7, self.m[1]-2, 2, 2, -2, 2)),
            # Lines
            Path(d='M{},{} h{}'.format(0.7, self.m[1], self.w-1.4)),
            Path(d='M{},{} v{}'.format(self.m[0], 0.7, self.h-1.4)),
        ]
        for elem in elems:
            helpers.add(elem)
        page.add(helpers)
        return page

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

    def drawLinesSpiral(self):
        lines = Group()
        w, h = self.w, self.h
        cx, cy = self.w, self.h / 2
        thickness = 1
        number = 1
        dir = -1
        for n in range(1, 21):
            if n % 2 != 0:
                line = 'M{},{} h{}'.format(cx, cy, w * dir)
                cx += (w / 2) * dir
                h /= 2
            else:
                line = 'M{},{} v{}'.format(cx, cy, h * dir)
                cy += (h / 2) * dir
                w /= 2
                dir *= -1

            lines.add(Path(d=line, style='stroke-width:{};'.format(round(thickness, 3))))
            number += 1
            thickness *= sqrt1_2

        return lines

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
            style='font-size:{};'.format(self.fontSizes[2])
        ))
        page.add(Text('1', insert=(self.c[0], self.m[1]), class_='center'))
        page.add(Text(
            '√2',
            insert=(self.m[0], self.c[1]),
            transform='rotate(-90 {} {})'.format(self.m[0], self.c[1]),
            class_='center'
        ))
        page.add(Text(
            '{}0 -> {}{}'.format(self.symbol, self.symbol, self.times - 1),
            insert=(self.c[0], self.h - self.m[1]),
            class_='center'
        ))
        page.add(Text(
            '{}0 ±=== {} AREA'.format(self.symbol, self.name.upper()),
            insert=(self.c[0], self.h - self.m[1] - (self.c[1] - self.radius[1] - self.m[1]) / 2),
            class_='center'
        ))
        page.add(Text(
            '{} km'.format(self.realRadius[0]),
            insert=(self.c[0] + self.radius[0] / 2, self.c[1] + self.dist),
            class_='center'
        ))
        page.add(Text(
            '{} km'.format(self.realRadius[1]),
            insert=(self.c[0] + self.dist, self.c[1] - self.radius[1] / 2),
            transform='rotate(-90 {} {})'.format(
                self.c[0] + self.dist, self.c[1] - self.radius[1] / 2
            ),
            class_='center'
        ))

        return page

    def drawCoverVerso(self, page):
        [width, height] = self.size

        page.add(Text(
            '{} km'.format(width),
            insert=(self.c[0], self.m[1] + self.dist),
            class_='center',
        ))
        page.add(Text(
            '{} km'.format(height),
            insert=(self.m[0] + 5, self.c[1]),
            transform='rotate(-90 {} {})'.format(self.m[0] + self.dist, self.c[1]),
            class_='center',
        ))

        textBot = Text(
            '', insert=(0, 0), class_='right',
            transform='translate({}, {})'.format(
                self.w - self.m[0], self.h - self.m[1] - self.leading
            )
        )
        spans = [
            TSpan(self.nameDesc),
            TSpan('{} km² = {} × {} km'.format(self.area, *self.size), x=[0], y=[self.leading]),
        ]
        for span in spans:
            textBot.add(span)
        page.add(textBot)

        intro = Text(
            '', insert=(0, 0),
            transform='translate({}, {})'.format(
                self.c[0] + self.m[0] / 2 - 62.3,
                self.c[1] + self.m[0] / 2 - len(self.intro) / 2 * self.leading + self.leading
            )
        )
        for i, sentence in enumerate(self.intro):
            intro.add(TSpan(sentence, x=[0], y=[self.leading * i]))
        page.add(intro)
        return page

    def drawPageRecto(self, page, number):
        w, h = self.w / 2, self.h / 2
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

    def drawPageRectoSpiral(self, number):
        texts = Group(id='texts')
        w, h = self.w / 2, self.h / 2
        cx, cy = w, h
        dir = -1
        klass = 'center filledstroked'
        for i in range(0, 21):
            if i == 0:
                textPos = self.c
            elif i % 2 != 0:
                h /= 2
                textPos = [cx, cy + h * -dir]
                cy += h * dir
                dir *= -1
            else:
                w /= 2
                textPos = [cx + w * -dir, cy]
                cx += w * dir
            texts.add(Text(
                self.symbol + str(i + number),
                insert=textPos,
                class_=klass,
                font_size=str(self.fontSizes[i]) + 'px'
            ))
            if i == 0:
                klass = 'center'

        texts.elements = texts.elements[::-1]

        return texts

    def drawPageVerso(self, page, number):
        [width, height] = self.formats[number]

        page.add(Text(
            '{} mm'.format(width),
            insert=(self.c[0], self.m[1] + self.dist),
            class_='center',
        ))
        page.add(Text(
            '{} mm'.format(height),
            insert=(self.m[0] + 5, self.c[1]),
            transform='rotate(-90 {} {})'.format(self.m[0] + self.dist, self.c[1]),
            class_='center',
        ))

        text = Text(
            '', insert=(0, 0), class_='right',
            transform='translate({}, {})'.format(
                self.w - self.m[0], self.h - self.m[1] - 3 * self.leading
            )
        )
        areaLost = self.format0area - (width * height * distribution[number]['total'] * 10**-12)
        spans = [
            TSpan('{0}({1}) -> {1}{2}'.format(self.name.upper(), self.symbol, number)),
            TSpan('{} × {} mm'.format(width, height), x=[0], y=[self.leading]),
            TSpan('{} per {}0'.format(distribution[number]['total'], self.symbol), x=[0], y=[self.leading * 2]),
            TSpan('{} km² lost due to previous rounding'.format(round(areaLost, 4)), x=[0], y=[self.leading * 3])
        ]
        for span in spans:
            text.add(span)
        page.add(text)
        return page

    def saveAsSVG(self, folder='print/svg/'):
        ''' Save every generated svg as single files.
        '''
        for i, page in enumerate(self.pages):
            if page is not None:
                print('Saving p{}…'.format(i))
                page.saveas('{}{}-p{}.svg'.format(folder, self.name, i), pretty=True)

    def saveAsPDF(self, folder='print/'):
        ''' Generate a single pdf with every page.
        '''
        pdf = PdfFileMerger()
        for page in self.pages:
            # Had to use a temp file so inkscape can open it.
            # Had to use inkscape since other svg2pdf converters can't manage
            # 'font-variant-ligature' nor 'dominant-baseline' css rules.
            if page is not None:
                with NamedTemporaryFile() as temp:
                    temp.write(page.tostring().encode('utf-8'))
                    temp.flush()
                    process = subprocess.run(
                        ['inkscape', temp.name, '--export-pdf=-', '-z'],
                        input=temp.read(),
                        stdout=subprocess.PIPE
                    )
                    pdf.append(BytesIO(process.stdout))

        with open('{}{}.pdf'.format(folder, self.name.lower()), 'wb') as target:
            pdf.write(target)


if __name__ == '__main__':
    earth = Catalog(getJson('data/planets/earth.json'))
    earth.generate(2)
    earth.saveAsSVG()
    # earth.saveAsPDF()
