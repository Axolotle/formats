import os
import jinja2
from markdown import markdown

from utils import getJson, getYaml, stringifyNumber
from formulae import sqrt1_2, km2mm


class HomePage():
    def __init__(self, templates, lang, texts, planetsInfo):
        self.template = templates.get_template('home.html.jinja2')
        self.lang = lang
        self.root = '../' if lang != 'fr' else ''
        self.planets = planetsInfo
        self.metaDesc = texts['metaDesc']
        self.footer = {
            'title': texts['footer']['title'],
            'content': markdown(texts['footer']['content'])
        }
        self.name = 'index'
        self.globalTitle = texts['globalTitle']
        self.title = self.home = texts['home']['title']
        self.intro = markdown(texts['home']['intro'])
        self.content = markdown(texts['home']['content'])

    def generate(self, folder='output/web/'):
        if self.lang != 'fr':
            folder += self.lang + '/'
        if not os.path.exists(os.getcwd() + '/' + folder):
            os.makedirs(os.getcwd() + '/' + folder)
        self.template.stream(page=self).dump(folder + self.name + '.html')


class PlanetPage():
    def __init__(self, templates, lang, texts, planetsInfo, data):
        self.template = templates.get_template('planet.html.jinja2')
        self.lang = lang
        self.root = '../../' if lang != 'fr' else '../'
        self.planets = planetsInfo
        self.symbol = data['symbol']
        self.metaDesc = texts['metaDesc']
        self.footer = {
            'title': texts['footer']['title'],
            'content': markdown(texts['footer']['content'])
        }
        self.name = data['name']['en']
        self.home = texts['home']['title']
        self.globalTitle = texts['globalTitle']
        self.title = texts['planets']['title'].format(
            name=data['name'][lang],
            symbol=data['symbol'],
            symbolName=data['symbolName'],
        )
        self.standard = texts['planets']['standard'].format(symbol=data['symbol'])
        self.areaLost = texts['planets']['areaLost']
        self.formatList = texts['planets']['formatList']
        self.content = self.getMainContent(texts['planets'], data, lang)
        self.formats = [
            {
                'width': stringifyNumber(format[0], lang),
                'height': stringifyNumber(format[1], lang),
                'areaLost': stringifyNumber(round(data['areaLost'][i], 3), lang),
                'content': '{symbol}{i} -> {width} × {height} mm'.format(
                    symbol=self.symbol,
                    i=i,
                    width=format[0],
                    height=format[1],
                )
            }
            for i, format in enumerate(data['formats_mm'])
        ]
        format = data['serieAequi']['4']['size']
        ratio = format[1] / km2mm(data['size_km'][1])
        radius = ratio * km2mm(data['radius'][1])
        fontSizes = [round(radius * sqrt1_2**n, 3) for n in range(21)]
        self.svg = {
            'width': format[0],
            'height': format[1],
            'lines': self.svgLines(format),
            'names': self.svgTexts(format, fontSizes),
        }

    def generate(self, folder='output/web/'):
        if self.lang != 'fr':
            folder += self.lang + '/'
        if not os.path.exists(os.getcwd() + '/' + folder + 'planets'):
            os.makedirs(os.getcwd() + '/' + folder + 'planets')
        self.template.stream(page=self).dump('{}planets/{}.html'.format(folder, self.name.lower()))

    def getMainContent(self, texts, data, lang):
        main = texts['content'].format(
            name=data['name'][lang],
            greekGod=data['greekGod'][lang],
            ancientGreekName=data['ancientGreekName'],
            area=data['area'],
            wkm=data['size_km'][0],
            hkm=data['size_km'][1],
            symbol=data['symbol'],
            symbolName=data['symbolName'],
            w0=data['formats_mm'][0][0],
            h0=data['formats_mm'][0][1],
            error=data['areaLost'][0] * 10**6,
            a10equiNumber=data['serieAequi']['10']['number'],
            a4equiNumber=data['serieAequi']['4']['number'],
        )
        if data['radius'][0] != data['radius'][1]:
            calculus = texts['calculusEllipse']
        else:
            calculus = texts['calculusSphere']
        calculus = calculus.format(
            re=data['radius'][0],
            rp=data['radius'][1],
            radiusSource=data['radiusSource'],
            area=data['area'],
        )
        rectangle = texts['calculusRectangle'].format(
            area=data['area'],
            wkm=data['size_km'][0],
            hkm=data['size_km'][1],
            w0=data['formats_mm'][0][0],
            h0=data['formats_mm'][0][1],
        )
        return markdown('\n'.join([main, calculus, rectangle]))

    def svgLines(self, format):
        lines = []
        w, h = format
        cx, cy = w, h / 2
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

            lines.append({
                'd': line,
                'strokeW': round(thickness, 3)
            })
            number += 1
            thickness *= sqrt1_2

        return lines

    def svgTexts(self, format, fontSizes):
        texts = []
        w, h = format[0] / 2, format[1] / 2
        cx, cy = w, h
        dir = -1
        for i in range(0, 21):
            if i == 0:
                pos = [w, h]
            elif i % 2 != 0:
                h /= 2
                pos = [cx, cy + h * -dir]
                cy += h * dir
                dir *= -1
            else:
                w /= 2
                pos = [cx + w * -dir, cy]
                cx += w * dir
            texts.append({
                'pos': pos,
                'fontSize': fontSizes[i],
                'content': self.symbol + str(i),
            })

        return texts[::-1]


def main():
    templateLoader = jinja2.FileSystemLoader(searchpath='web/templates/')
    templateEnv = jinja2.Environment(loader=templateLoader)
    texts = getYaml('data/texts.yaml')
    data =  [getJson('data/planets/'+planet+'.json')
             for planet in [p['name']['en'].lower() for p in texts['planets']]]

    for lang in ['fr', 'en']:
        homePage = HomePage(templateEnv, lang, texts[lang], texts['planets'])
        homePage.generate()
        planetPages = [PlanetPage(templateEnv, lang, texts[lang], texts['planets'], d)
                       for d in data]
        for pp in planetPages:
            pp.generate()

    with open('web/script.js', 'r') as copy:
        with open('output/web/script.js', 'w') as paste:
            paste.write(copy.read())


if __name__ == '__main__':
    main()
