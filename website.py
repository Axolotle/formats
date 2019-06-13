from yattag import Doc, indent

from catalog import Catalog
from utils import getJson


def generate(planet, svg):
    doc, tag, text, line = Doc().ttl()
    doc.asis('<!DOCTYPE html>')
    with tag('html', lang='fr'):
        doc.asis(header(planet['name']))
        with tag('body'):
            doc.asis(svg)
            line('script', '', type='text/javascript', src='script.js')

    with open('web/{}.html'.format(planet['name'].lower()), 'w') as output:
        output.write(indent(doc.getvalue()))

def header(name):
    doc, tag, text, line = Doc().ttl()
    with tag('head'):
        doc.stag('meta', charset='utf-8')
        doc.stag('meta', name='viewport', content='width=device-width, initial-scale=1')
        line('title', 'Planetary Formats - ' + name)
        doc.stag('link', rel='stylesheet', href='stylesheet.css')
    return doc.getvalue()


if __name__ == '__main__':
    data = getJson('data/planets/earth.json')
    earth = Catalog(data)
    generate(data, earth.generateWebVersion())
