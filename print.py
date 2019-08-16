import jinja2
from PyPDF2 import PdfFileMerger
from tempfile import NamedTemporaryFile
import subprocess
from io import BytesIO

from utils import getJson, getText, getYaml, stringifyNumber, numberToCharacter
from formulae import sqrt1_2, km2mm


class Common():
    def __init__(self, planetData):
        self.symbol = planetData['symbol']
        self.symbolName = planetData['symbolName']
        self.w = planetData['serieAequi']['4']['size'][0]
        self.h = planetData['serieAequi']['4']['size'][1]
        # margins x and y of the document
        self.m = [self.w / 16, self.h / 16]
        # center of the document
        self.c = [self.w / 2, self.h / 2]
        self.formats = planetData['formats_mm']

        self.ratio = self.h / km2mm(planetData['size_km'][1])
        radius = self.ratio * km2mm(planetData['radius'][1])
        self.fontSizes = [round(radius * sqrt1_2**n, 3) for n in range(21)]

        self.wPos = [self.c[0], self.m[1]]
        self.hPos = [self.w - self.m[0], self.c[1]]



class Pages(Common):
    def __init__(self, planetData):
        super().__init__(planetData)
        self.texts = getYaml('data/textsPrint.yaml')['pages']
        self.distrib = getJson('data/formatsDistribution.json')
        self.lost = [round(lost, 3) for lost in planetData['areaLost']]

    def generate(self, templates, css, lang, layout=[210, 297], number=None):
        pages = []
        if layout is not None:
            tx = (layout[0] - self.w) / 2
            ty = (layout[1] - self.h) / 2
            self.layout = {
                'viewBox': '-{} -{} {} {}'.format(tx, ty, tx + tx + self.w, self.h + ty + ty),
                'width': tx + tx + self.w,
                'height': ty + ty + self.h,
            }
            self.templates = [
                templates.get_template('format-recto.svg.jinja2'),
                templates.get_template('format-verso.svg.jinja2'),
            ]
        else:
            self.layout = {
                'viewBox': '0 0 {} {}'.format(self.w, self.h),
                'width': self.w,
                'height': self.h,
            }
            self.templates = [
                templates.get_template('partials/format-recto.svg.jinja2'),
                templates.get_template('partials/format-verso.svg.jinja2'),
                templates.get_template('base.svg.jinja2'),
            ]
        
        self.css = css.replace('MAINFONTSIZE', str(self.fontSizes[8]))
        
        arr = range(len(self.formats)) if number is None else [number]            
        for n in arr:
            if layout is None:
                pages.append(self.templates[2].render(
                    l=self.layout,
                    css=self.css,
                    content=self.recto(lang, n) + self.verso(lang, n)
                ))
            else:
                pages.append(self.recto(lang, n))
                pages.append(self.verso(lang, n))
        return pages

    def recto(self, lang, index):
        wNotation = stringifyNumber(self.formats[index][0], lang)
        hNotation = stringifyNumber(self.formats[index][1], lang)
        remaining = len(self.formats) - index
        return self.templates[0].render(
            l=self.layout,
            css=self.css,
            width=self.w,
            height=self.h,
            name={
                'pos': [self.w / 2, self.h / 2],
                'fontSize': self.fontSizes[0 if remaining > 6 else 7 - remaining],
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
            title={
                'pos': [self.w / 2, self.h - self.m[1] / 2],
                'content': self.texts[lang]['recto']['title'].format(
                    symbol=self.symbol,
                    symbolName=self.symbolName,
                    number=index,
                    numberName=numberToCharacter(index, lang),
                ),
            },
            textBlock={
                'pos': [self.m[0], self.h - self.m[1] - 3 * self.fontSizes[8] * 1.25],
                'size': [self.w - self.m[0] * 2, 2 * self.fontSizes[8] * 1.25],
                'paragraphs': self.texts[lang]['recto']['textBlock'].format(
                    symbol=self.symbol,
                    symbolName=self.symbolName,
                    number=index,
                    numberName=numberToCharacter(index, lang),
                    width=wNotation,
                    height=hNotation,
                ).splitlines(),
            },
            rect=None if remaining > 6 else {
                'width': self.formats[index][0],
                'height': self.formats[index][1],
                'pos': [
                    (self.w - self.formats[index][0]) / 2,
                    (self.h - self.formats[index][1]) / 2,
                ]
            }
        )

    def verso(self, lang, index):
        remaining = len(self.formats) - index

        if (remaining <= 6):
            w = self.formats[index][0]
            h = self.formats[index][1]
            tx = (self.w - w) / 2
            ty = (self.h - h) / 2
            fs = 7 - remaining
        else:
            remaining = remaining if remaining < 17 else 17
            w = self.w
            h = self.h
            tx = 0
            ty = 0
            fs = 0

        return self.templates[1].render(
            l=self.layout,
            css=self.css,
            width= self.w,
            height= self.h,
            reverseTranslate=-self.w,
            translate='{} {}'.format(tx, ty),
            textBlock={
                'pos': [self.m[0], self.h - self.m[1] - 3 * self.fontSizes[8] * 1.25],
                'size': [self.w - self.m[0] * 2, 3 * self.fontSizes[8] * 1.25],
                'paragraphs': self.texts[lang]['verso']['textBlock'].format(
                    symbol=self.symbol,
                    numberDistrib=stringifyNumber(self.distrib[index]['total'], lang),
                    lost=stringifyNumber(self.lost[index], lang)
                ).splitlines(),
            },
            lines=self.homothetyLines(w, h, remaining),
            names=self.homothetyTexts(index, w, h, remaining, fs)
        )

    def homothetyLines(self, width, height, amount):
        lines = []
        w, h = width, height
        thickness = 1
        for n in range(1, amount):
            line = {}
            if n % 2 != 0:
                h /= 2
                offset = 2 if amount >= 7 else 0
                if n == 1:
                    line['d'] = 'M{},{} h{}'.format(width - w - offset, h, w + 2 * offset)
                else:
                    line['d'] = 'M{},{} h{}'.format(width - w, h, w + offset)
            else:
                w /= 2
                offset = 2 if amount >= 7 else 0
                line['d'] = 'M{},{} v{}'.format(width - w, -offset, h + offset)
            line['stroke'] = round(thickness, 3)
            lines.append(line)
            thickness *= sqrt1_2
        return lines

    def homothetyTexts(self, number, width, height, amount, fs):
        w, h = width, height
        texts = []
        for i in range(1, amount):
            text = {}
            if i % 2 != 0:
                h /= 2
                text['pos'] = [width - w / 2, h * 1.5]
            else:
                w /= 2
                text['pos'] = [width - w * 1.5, h / 2]
            text['content'] = self.symbol + str(i + number)
            text['fontSize'] = self.fontSizes[fs + i]
            texts.append(text)
        return texts



class Intercalar(Common):
    def __init__(self, planetData):
        super().__init__(planetData)
        self.texts = getYaml('data/textsPrint.yaml')['intercalar']
        self.planetName = planetData['name']
        self.greekGod = planetData['greekGod']
        self.ancientGreekName = planetData['ancientGreekName']
        self.realRadius = planetData['radius']
        self.area = planetData['area']
        self.radius = [self.ratio * km2mm(rad) for rad in planetData['radius']]
        self.sizeKm = planetData['size_km']
        self.n = planetData['serieAequi']['4']['number']
        self.rectPosY = {
            'Mercury': 108.25,
            'Venus': 169.437,
            'Earth': 246.813,
            'Mars': 71.063,
            'Jupiter': 207.625,
            'Saturn': 43.875,
            'Uranus': 0,
            'Neptune': 31.187,
        }[self.planetName['en']]

    def generate(self, templates, css, lang, layout=[210, 297]):
        self.css = css.replace('MAINFONTSIZE', str(self.fontSizes[8]))
        self.templates = [
            templates.get_template('intercalar-recto.svg.jinja2'),
            templates.get_template('intercalar-verso.svg.jinja2'),
        ]
        if layout is not None:
            tx = (layout[0] - self.w - 10) / 2
            ty = (layout[1] - self.h) / 2
            self.layout = {
                'viewBox': '-{} -{} {} {}'.format(tx, ty, tx + tx + self.w, ty + ty + self.h),
                'width': layout[0],
                'height': layout[1],
                'print': True,
            }
            self.css = self.css.replace('MAINCOLOR', 'black').replace('SUBCOLOR', 'white')
        else:
            self.layout = {
                'viewBox': '0 0 {} {}'.format(self.w, self.h),
                'width': self.w,
                'height': self.h,
            }
            self.css = self.css.replace('MAINCOLOR', 'white').replace('SUBCOLOR', 'black')
        return [
            self.recto(lang),
            self.verso(lang)
        ]

    def recto(self, lang):
        return self.templates[0].render(
            l=self.layout,
            css=self.css,
            width=self.w,
            height=self.h,
            int={
                'rect': {
                    'pos': [self.w, self.rectPosY],
                    'size': [10, 35.187]
                },
                'text': {
                    'pos': [self.w + 5, self.rectPosY + 35.187 / 2],
                    'content': self.planetName[lang].upper()
                },
                'translate': -5
            },
            ellipse={
            'pos': self.c,
            'rad': self.radius
            },
            rad='M{},{} v{} h{}'.format(
                self.c[0],
                self.c[1] -
                self.radius[1],
                self.radius[1], self.radius[0]
            ),
            name={
                'pos': self.c,
                'content': self.symbol,
                'fontSize': self.fontSizes[0],
            },
            w=self.wPos,
            h=self.hPos,
            area={
                'pos': [self.c[0], self.c[1] + self.radius[1] + ((self.c[1] - self.radius[1] - self.m[1]) / 2)],
                'content': self.texts[lang]['recto']['area'].format(
                    symbol=self.symbol,
                    planetName=self.planetName[lang],
                )
            },
            range={
                'pos': [self.c[0], self.h - self.m[1]],
                'content': '{0}0 -> {0}{1}'.format(self.symbol, len(self.formats) - 1),
            },
            radius=[
                {
                    'pos': [self.c[0] + self.radius[0] / 2, self.c[1] - self.m[0] / 2],
                    'content': stringifyNumber(self.realRadius[0], lang),
                },
                {
                    'pos': [self.c[0] + self.m[0] / 2, self.c[1] - self.radius[1] / 2],
                    'content': stringifyNumber(self.realRadius[1], lang),
                }
            ]
        )

    def verso(self, lang):
        sizeKm = [stringifyNumber(side, lang) for side in self.sizeKm]
        return self.templates[1].render(
            l=self.layout,
            css=self.css,
            width=self.w,
            height=self.h,
            int={
                'rect': {
                    'pos': [-10, self.rectPosY],
                    'size': [10, 35.187]
                },
                'text': {
                    'pos': [-5, self.rectPosY + 35.187 / 2],
                    'content': self.planetName[lang].upper()
                },
                'translate': 5
            },
            w={
                'pos': self.wPos,
                'content': sizeKm[0],
            },
            h={
                'pos': [self.m[0], self.c[1]],
                'content': sizeKm[1],
            },
            names={
                'pos': [self.c[0], self.h - self.m[1]],
                'content': '{} <== {} === {} >- {}'.format(
                    self.planetName[lang],
                    self.greekGod[lang],
                    self.ancientGreekName,
                    self.symbol
                ),
            },
            textBlock={
                'pos': [self.m[0] * 2, self.m[1] * 3],
                'size': [self.w - self.m[0] * 4, self.h - self.m[1] * 5],
                'paragraphs': [
                    {
                        'lines': ['{} ({})'.format(self.symbol, self.symbolName),
                                  '0-{}'.format(len(self.formats) - 1)],
                        'klass': 'end',
                        'fontSize': self.fontSizes[6]
                    },
                    {
                        'lines': [self.planetName[lang].upper()],
                        'fontSize': self.fontSizes[2]
                    },
                    {
                        'lines': self.texts[lang]['verso']['textBlock'].format(
                            rx=stringifyNumber(self.realRadius[0], lang),
                            ry=stringifyNumber(self.realRadius[1], lang),
                            area=stringifyNumber(self.area, lang),
                            planetName=self.planetName[lang],
                            width=sizeKm[0],
                            height=sizeKm[1],
                            a4equiNumber=self.n,
                            a4equiW=self.w,
                            a4equiH=self.h,
                        ).splitlines()
                    }
                ]
            }
            
        )



def saveAsSVG(pages, folder='output/svg/'):
    for i, page in enumerate(pages):
        with open(folder + 'p' + str(i) + '.svg', 'w') as output:
            output.write(page)


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
    n = 56

    templateLoader = jinja2.FileSystemLoader(searchpath='print/templates/')
    templateEnv = jinja2.Environment(loader=templateLoader)
    css = getText('print/stylesheet.css')

    planetData = getJson('data/planets/earth.json')
    # catalog = Pages(planetData)
    # pages = catalog.generate(templateEnv, css, 'fr', layout=None)
    # saveAsPDF(pages, planetData['name']['en'])
    # saveAsSVG(pages)
    css = getText('print/stylesheet-intercalar.css')
    intercalar = Intercalar(planetData)
    pages = intercalar.generate(templateEnv, css, 'fr')
    saveAsSVG(pages, folder='output/print/intercalar/')
