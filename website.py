from yattag import Doc, indent

from catalog import Catalog
from utils import getJson


def generate(planet, svg):
    doc, tag, text, line = Doc().ttl()
    doc.asis('<!DOCTYPE html>')
    with tag('html', lang='fr'):
        doc.asis(head(planet['name']))
        with tag('body'):
            with tag('header'):
                line('h1', '{} => {} ({}) serie'.format(planet['name'].upper(), planet['symbol'], planet['symbolName']))
                doc.asis(menu())
            with tag('main'):
                with tag('div', klass='side'):
                    line('h2', 'DAC|PlanetaryFormats({}):2019'.format(planet['symbol']))
                    doc.asis(mainText(planet))
                with tag('div'):
                    with tag('div', id='svg'):
                        with tag('div', klass='height'):
                            line('span', '26857805126 mm')
                        doc.asis(svg)
                        with tag('div', klass='width'):
                            line('span', '18991336133 mm')
                with tag('div', klass='side'):
                    doc.asis(formatList(planet))
                line('script', '', type='text/javascript', src='script.js')

    with open('web/{}.html'.format(planet['name'].lower()), 'w') as output:
        output.write(indent(doc.getvalue()))

def head(name):
    doc, tag, text, line = Doc().ttl()
    with tag('head'):
        doc.stag('meta', charset='utf-8')
        doc.stag('meta', name='viewport', content='width=device-width, initial-scale=1')
        line('title', 'Planetary Formats - ' + name)
        doc.stag('link', rel='stylesheet', href='stylesheet.css')
    return doc.getvalue()

def menu():
    doc, tag, text, line = Doc().ttl()
    menu = [
        ['home', 'index'],
        ['Ε', 'mercury'],
        ['Α', 'venus'],
        ['Γ', 'earth'],
        ['α', 'mars'],
        ['Ζ', 'jupiter'],
        ['Κ', 'saturn'],
        ['Ο', 'uranus'],
        ['Π', 'neptune'],
    ]
    with tag('nav'):
        with tag('ul'):
            for elem in menu:
                with tag('li'):
                    line('a', elem[0], href=elem[1]+'.html')
    return doc.getvalue()

def formatList(planet):
    doc, tag, text, line = Doc().ttl()
    with tag('ul', id='formats'):
        line('span', 'FORMATS:')
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

def mainText(planet):
    doc, tag, text, line = Doc().ttl()
    concat = ''
    for line in planet['text']:
        if line.endswith('.') or line == '':
            with tag('p'):
                text(concat + ' ' + line)
            concat = ''
        else:
            concat += ' ' + line

    return doc.getvalue()

if __name__ == '__main__':
    data = getJson('data/planets/earth.json')
    earth = Catalog(data)
    generate(data, earth.generateWebVersion())
