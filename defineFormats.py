from math import floor
from json import load, dump

from utils import getJson, dumpJson
from formulae import surfaceAreaOfOblateEllipsoid, rectSize


def defineFormats():
    planets = {}
    for planet in getJson('data/planetsInput.json'):
        # 'surface' is in km²
        surface = surfaceAreaOfOblateEllipsoid(*planet['radius'])
        symbol = planet['symbol']
        width, height = rectSize(surface)
        planet['surface'] = surface
        planet['size_km'] = [width, height]

        # turn kilometers into millimeter and round to the nearest integrer
        # Planet's paper format '0' surface area ~= planet surface area (rounded
        # to the nearest millimeter) so height / width is now ~= √2
        height = round(height * 1000000)
        width = round(width * 1000000)
        planet['a4like'] = {}

        planet['formats_mm'] = []
        planet['formats_mm'].append([width, height])
        a4like = None

        i = 0
        # search for folded versions until we reach the equivalent of A10
        while i < 8:
            [height, width] = [width, floor(height / 2)]
            planet['formats_mm'].append([width, height])
            if a4like is None and height <= 297:
                a4like = [width, height] if height > width else [height, width]
                planet['a4like'] = a4like
                i = 1
            if i > 0:
                i += 1

        planets[planet['name']] = planet
    return planets

if __name__ == '__main__':
    planets = defineFormats()
    for planet in planets.values():
        dumpJson('data/planets/' + planet['name'].lower() + '.json', planet)
