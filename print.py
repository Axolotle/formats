import jinja2
from PyPDF2 import PdfFileMerger
from tempfile import NamedTemporaryFile
import subprocess
from io import BytesIO

from utils import getJson, getText, getYaml, stringifyNumber, numberToCharacter
from formulae import sqrt1_2, km2mm


class Pages():
    def __init__(self, templates, css, planetData, lang):
        self.lang = lang

        self.symbol = planetData['symbol']
        self.symbolName = planetData['symbolName']
        self.w = planetData['serieAequi']['4']['size'][0]
        self.h = planetData['serieAequi']['4']['size'][1]
        # margins x and y of the document
        self.m = [self.w / 16, self.h / 16]
        self.formats = planetData['formats_mm']
        self.distrib = getJson('data/formatsDistribution.json')
        self.lost = [round(lost, 3) for lost in planetData['areaLost']]

        ratio = self.h / km2mm(planetData['size_km'][1])
        radius = ratio * km2mm(planetData['radius'][1])
        self.fontSizes = [round(radius * sqrt1_2**n, 3) for n in range(21)]

        self.css = css.replace('MAINFONTSIZE', str(self.fontSizes[8]))
        self.templates = [
            templates.get_template('format-recto.svg.jinja2'),
            templates.get_template('format-verso.svg.jinja2'),
        ]
        self.texts = getYaml('data/textsPrint.yaml')[lang]['pages']

        self.wPos = [self.w / 2, self.m[1]]
        self.hPos = [self.w - self.m[0], self.h/2]

    def generate(self, layout=[210, 297], number=None, arr=None, side=None):
        pages = []
        if layout is not None:
            tx = (layout[0] - self.w) / 2
            ty = (layout[1] -  self.h) / 2
            marg = 2
            x = tx - marg
            y = ty - marg
            layout = {
                'tx': tx,
                'ty': ty,
                'cutLines': [
                    'M0,{ty} h{x} m2,-2 v-{y}'.format(ty=ty, x=x, y=y),
                    'M210,{ty} h-{x} m-2,-2 v-{y}'.format(ty=ty, x=x, y=y),
                    'M{tx},297 v-{y} m-2,-2 h-{x}'.format(tx=tx, x=x, y=y),
                    'M{ttx},297 v-{y} m2,-2 h{x}'.format(ttx=tx + self.w, x=x, y=y),
                ],
            }
        if number is not None:
            arr = [number]
        elif arr is None:
            arr = range(len(self.formats))

        if side is not None:
            sideFunc = self.recto if side == 'recto' else self.verso
            for n in arr:
                pages.append(sideFunc(layout, n))
        else:
            for n in arr:
                pages.append(self.recto(layout, n))
                pages.append(self.verso(layout, n))
        return pages

    def recto(self, layout, index):
        wNotation = stringifyNumber(self.formats[index][0])
        hNotation = stringifyNumber(self.formats[index][1])
        return self.templates[0].render(
            l=layout,
            css=self.css,
            width= self.w,
            height= self.h,
            name={
                'pos': [self.w / 2, self.h / 2],
                'fontSize': self.fontSizes[0],
                'content': self.symbol + str(index)
            },
            w={
                'pos': self.wPos,
                'content': wNotation + ' mm'
            },
            h={
                'pos': self.hPos,
                'content': hNotation + ' mm'
            },
            textBlock={
                'pos': [self.m[0], self.h - self.m[1] - 5 * self.fontSizes[8] * 1.25],
                'size': [self.w - self.m[0] * 2, 5 * self.fontSizes[8] * 1.25],
                'paragraphs': self.texts['recto']['textBlock'].format(
                    symbol=self.symbol,
                    symbolName=self.symbolName,
                    number=index,
                    numberName=numberToCharacter(index, self.lang),
                    width=wNotation,
                    height=hNotation,
                    numberDistrib=stringifyNumber(self.distrib[index]['total'], self.lang),
                    lost=stringifyNumber(self.lost[index], self.lang)
                ).splitlines(),
            },
        )

    def verso(self, layout, index):
        return self.templates[1].render(
            l=layout,
            css=self.css,
            width= self.w,
            height= self.h,
            lines=self.homothetyLines(self.w, self.h),
            names=self.homothetyTexts(index, self.w, self.h)
        )

    def homothetyLines(self, width, height):
        lines = []
        w, h = width, height
        thickness = 1
        for n in range(1, 21):
            line = {}
            if n % 2 != 0:
                h /= 2
                line['d'] = 'M{},{} h{}'.format(width - w if n != 1 else width - w - 2, h, w + 2 )
            else:
                w /= 2
                line['d'] = 'M{},{} v{}'.format(width - w, -2, h + 2)
            line['stroke'] = round(thickness, 3)
            lines.append(line)
            thickness *= sqrt1_2
        return lines

    def homothetyTexts(self, number, width, height):
        w, h = width, height
        texts = []
        for i in range(1, 21):
            text = {}
            if i % 2 != 0:
                h /= 2
                text['pos'] = [width - w / 2, h * 1.5]
            else:
                w /= 2
                text['pos'] = [width - w * 1.5, h / 2]
            text['content'] = self.symbol + str(i + number)
            text['fontSize'] = self.fontSizes[i]
            texts.append(text)
        return texts


def saveAsSVG(pages, folder='output/svg/'):
    for i, page in enumerate(pages):
        with open(folder + 'p' + str(i) + '.svg', 'w') as output:
            output.write(page)
        # page.dump(folder + 'p' + str(i) + '.svg')


def saveAsPDF(pages, name, folder='output/print/'):
    pdf = PdfFileMerger()
    for page in pages:
        # Had to use a temp file so inkscape can open it.
        # Had to use inkscape since other svg2pdf converters can't manage
        # 'font-variant-ligature' nor 'dominant-baseline' css rules.
        with NamedTemporaryFile() as temp:
            temp.write(page.encode('utf-8'))
            temp.flush()
            process = subprocess.run(
                ['inkscape', temp.name, '--export-pdf=-', '-z'],
                input=temp.read(),
                stdout=subprocess.PIPE
            )
            pdf.append(BytesIO(process.stdout))

    with open('{}{}.pdf'.format(folder, name.lower()), 'wb') as target:
        pdf.write(target)





if __name__ == '__main__':
    n = 11

    templateLoader = jinja2.FileSystemLoader(searchpath='print/templates/')
    templateEnv = jinja2.Environment(loader=templateLoader)
    css = getText('print/stylesheet.css')

    planetData = getJson('data/planets/earth.json')
    catalog = Pages(templateEnv, css, planetData, 'en')
    pages = catalog.generate()
    saveAsPDF(pages, planetData['name']['en'])
    # saveAsSVG(pages)
