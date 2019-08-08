from math import floor
from json import load, dump

from utils import getJson, dumpJson
from formulae import areaOfOblateEllipsoid, rectSize


def defineFormats(distribution):
    planets = {}
    for planet in getJson('data/planetsInput.json'):
        # 'area' is in km²
        area = areaOfOblateEllipsoid(*planet['radius'])
        symbol = planet['symbol']
        width, height = rectSize(area)
        planet['area'] = area
        planet['size_km'] = [width, height]

        # turn kilometers into millimeter and round to the nearest integrer
        # Planet's paper format '0' area ~= planet area (rounded to the nearest
        # millimeter) so height / width is now ~= √2
        height = floor(height * 1000000)
        width = floor(width * 1000000)

        planet['formats_mm'] = [[width, height]]
        serieAequi = {}
        planet['areaLost'] = [area - (width * height * distribution[0]['total'] * 10**-12)]

        i = 1
        a = 0
        # search for folded versions until we reach the equivalent of A10
        while a <= 10:
            [height, width] = [width, floor(height / 2)]
            planet['formats_mm'].append([width, height])
            planet['areaLost'].append(area - (width * height * distribution[i]['total'] * 10**-12))
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
    distribution = getJson('data/formatsDistribution.json')
    planets = defineFormats(distribution)
    for planet in planets.values():
        dumpJson('data/planets/' + planet['name']['en'].lower() + '.json', planet)
