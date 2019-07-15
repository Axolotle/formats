from yattag import Doc, indent
from markdown import markdown

from catalog import Catalog
from utils import getJson, getYaml


planets = [
    ['Ε', 'mercury'],
    ['Α', 'venus'],
    ['Γ', 'earth'],
    ['α', 'mars'],
    ['Ζ', 'jupiter'],
    ['Κ', 'saturn'],
    ['Ο', 'uranus'],
    ['Π', 'neptune'],
]
langs = []

class WebPage():
    def __init__(self, lang, projectTitle, homeName, planetsName):
        self.lang = lang
        self.projectTitle = projectTitle
        self.title = None
        self.isHome = False
        self.homeName = homeName
        self.planetsName = planetsName

    def build(self, title, *args):
        doc, tag, text, line = Doc().ttl()
        doc.asis('<!DOCTYPE html>')
        with tag('html', lang=self.lang):
            doc.asis(self.head())
            with tag('body'):
                with tag('header'):
                    line('h1', title)
                    doc.asis(self.menu())
                doc.asis(self.main(*args))
                if not self.isHome:
                    line('script', '', type='text/javascript', src='../../script.js')

        with open('web/{}/{}'.format(self.lang, self.fileName), 'w') as output:
            output.write(indent(doc.getvalue()))

    def head(self):
        doc, tag, text, line = Doc().ttl()
        with tag('head'):
            doc.stag('meta', charset='utf-8')
            doc.stag('meta', name='viewport', content='width=device-width, initial-scale=1')
            line('title', '{} - {}'.format(self.projectTitle, self.title))
            doc.stag('link',
                rel='stylesheet',
                href='../{}stylesheet.css'.format('' if self.isHome else '../')
            )
        return doc.getvalue()

    def menu(self):
        doc, tag, text, line = Doc().ttl()
        with tag('nav', klass='flex'):
            with tag('ul', klass='lang'):
                for lang in langs:
                    with tag('li'):
                        if lang is not self.lang:
                            line('a', lang, href='../{}{}/{}'.format(
                                '' if self.isHome else '../',
                                lang,
                                self.fileName,
                            ))
            with tag('ul'):
                with tag('li'):
                    line('a', self.homeName,
                        href='{}index.html'.format('' if self.isHome else '../'))
                for planet in planets:
                    with tag('li'):
                        line('a', planet[0],
                            href='{}{}.html'.format(
                                'planets/' if self.isHome else '', planet[1],
                            ),
                            title=self.planetsName[planet[1]],
                        )
        return doc.getvalue()


class IndexPage(WebPage):
    def __init__(self, lang, projectTitle, homeName, planetsName, texts):
        super().__init__(lang, projectTitle, homeName, planetsName)
        self.fileName = 'index.html'
        self.title = homeName
        self.isHome = True

        self.build(self.projectTitle, texts['intro'], texts['content'])

    def main(self, intro, content):
        doc, tag, text, line = Doc().ttl()
        with tag('main'):
            doc.asis(markdown(intro))
            with tag('div', id='planets'):
                for planet in planets:
                    with tag('div', id=planet[1].lower()):
                        line('p', self.planetsName[planet[1]])
                        line('a', planet[0], href='planets/{}.html'.format(planet[1].lower()))
            doc.asis(markdown(content))

        return doc.getvalue()


class PlanetPage(WebPage):
    def __init__(self, lang, projectTitle, homeName, planetsName, texts, planet, svg):
        super().__init__(lang, projectTitle, homeName, planetsName)
        self.fileName = 'planets/{}.html'.format(planet['name']['en'].lower())
        self.title = texts['title'].format(
            name=planet['name'][self.lang].upper(),
            symbol=planet['symbol'],
            symbolName=planet['symbolName']
        )

        self.build(self.title, texts, planet, svg)

    def main(self, texts, planet, svg):
        doc, tag, text, line = Doc().ttl()
        with tag('main', klass='flex'):
            with tag('div', id='svg-surcontainer'):
                with tag('div', id='svg-container'):
                    with tag('div', klass='height'):
                        line('span', '{} mm'.format(planet['formats_mm'][0][1]))
                    doc.asis(svg)
                    with tag('div', klass='width'):
                        line('span', '{} mm'.format(planet['formats_mm'][0][0]))
            with tag('div', id='data'):
                with tag('div', id='list-container'):
                    doc.asis(formatList(planet))
                with tag('div', id='text'):
                    line('h2', texts['standard'].format(symbol=planet['symbol']))
                    doc.asis(mainText(planet, texts['content'], lang))

        return doc.getvalue()

def formatList(planet):
    doc, tag, text, line = Doc().ttl()
    line('h3', 'Liste de formats :')
    with tag('ul', id='formats'):
        extra = ''
        a = 0
        line('li', '{}{} -> {} × {} mm'.format(
            planet['symbol'], '0 ', *planet['formats_mm'][0]
        ), klass='selected')
        for i, size in enumerate(planet['formats_mm'][1:]):
            i += 1
            if i < 10: i = str(i) + ' '
            if size[0] <= 841:
                extra = ' (A{}-compatible)'.format(a)
                a += 1
            line('li', '{}{} -> {} × {} mm{}'.format(
                planet['symbol'], i, *size, extra
            ))
    return doc.getvalue()

def mainText(planet, content, lang):
    doc, tag, text, line = Doc().ttl()
    content = content.format(
        name=planet['name'][lang],
        greekGod=planet['greekGod'][lang],
        ancientGreekName=planet['ancientGreekName'],
        surface=planet['surface'],
        wkm=planet['size_km'][0],
        hkm=planet['size_km'][1],
        symbol=planet['symbol'],
        symbolName=planet['symbolName'],
        w0=planet['formats_mm'][0][0],
        h0=planet['formats_mm'][0][1],
        error='#',
        a10equiNumber=planet['serieAequi']['10']['number'],
        a4equiNumber=planet['serieAequi']['4']['number'],
        re=planet['radius'][0],
        rp=planet['radius'][1],
        radiusSource=planet['radiusSource'],
    )
    return markdown(content)

if __name__ == '__main__':
    texts = getYaml('data/texts.yaml')
    langs = list(texts.keys())
    for lang, content in texts.items():
        homeName = content['homeName']
        planetsName = content['planetsName']
        projectTitle = content['projectTitle']
        IndexPage(lang, projectTitle, homeName, planetsName, content['home'])
        for _, name in planets:
            data = getJson('data/planets/{}.json'.format(name))
            catalog = Catalog(data)
            PlanetPage(lang, projectTitle, homeName, planetsName, content['planets'], data, catalog.generateWebVersion())
