import jinja2

from utils import getJson, getText
from formulae import sqrt1_2, km2mm


class Pages():
    def __init__(self, templates, css, planetData):
        self.symbol = planetData['symbol']
        self.w = planetData['serieAequi']['4']['size'][0]
        self.h = planetData['serieAequi']['4']['size'][1]
        self.formats = planetData['formats_mm']

        ratio = self.h / km2mm(planetData['size_km'][1])
        radius = ratio * km2mm(planetData['radius'][1])
        self.fontSizes = [round(radius * sqrt1_2**n, 3) for n in range(21)]

        self.css = css.replace('MAINFONTSIZE', str(self.fontSizes[8]))
        self.templates = [
            templates.get_template('format-recto.svg.jinja2'),
            templates.get_template('format-verso.svg.jinja2'),
        ]

    def generate(self, number=None, range=None, side=None):
        pages = []
        if number is not None:
            return [self.verso(number)]
        else:
            for i, format in enumerate(self.formats):
                # pages.append(self.recto(i))
                pages.append(self.verso(i))

    def recto(self, index):
        pass

    def verso(self, index):
        return self.templates[1].stream(
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
                line['d'] = 'M{},{} h{}'.format(width - w, h, w)
            else:
                w /= 2
                line['d'] = 'M{},{} v{}'.format(width - w, 0, h)
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













number = 0

templateLoader = jinja2.FileSystemLoader(searchpath='print/templates/')
templateEnv = jinja2.Environment(loader=templateLoader)
css = getText('print/stylesheet.css')

planetData = getJson('data/planets/earth.json')
catalog = Pages(templateEnv, css, planetData)
pages = catalog.generate(number=number)

for i, page in enumerate(pages):
    page.dump('output/test/p' + str(i) + '.svg')
