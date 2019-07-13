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

        planet['formats_mm'] = []
        planet['formats_mm'].append([width, height])
        serieAequi = {}

        i = 1
        a = 0
        # search for folded versions until we reach the equivalent of A10
        while a <= 10:
            [height, width] = [width, floor(height / 2)]
            planet['formats_mm'].append([width, height])
            if a == 0 and height <= 1189:
                serieAequi[str(a)] = {'number': i, 'size': [width, height]}
                a = 1
            elif a > 0:
                serieAequi[str(a)] = {'number': i, 'size': [width, height]}
                a += 1
            i += 1

        planet['serieAequi'] = serieAequi
        planets[planet['name']['en']] = planet
    return planets

if __name__ == '__main__':
    planets = defineFormats()
    for planet in planets.values():
        dumpJson('data/planets/' + planet['name']['en'].lower() + '.json', planet)
