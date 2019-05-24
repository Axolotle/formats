from math import floor
from json import load, dump

from utils import getJson, dumpJson
from formulae import surfaceAreaOfOblateEllipsoid, rectSize


def defineFormats():
    planets = {}
    for planet in getJson('surfaces.json'):
        # 'surface' is in km²
        surface = surfaceAreaOfOblateEllipsoid(*planet['radius'])
        serie = planet['serie']
        width, height = rectSize(surface)
        planet['surface'] = surface
        planet['size_km'] = [width, height]

        # turn kilometers into millimeter and round to the nearest integrer
        # Planet's paper format '0' surface area ~= planet surface area (rounded
        # to the nearest millimeter) so height / width is now ~= √2
        height = round(height * 1000000)
        width = round(width * 1000000)
        planet['rounded_size_mm'] = [width, height]
        planet['a4equi'] = {}

        serieNumber = 0
        planet['formats_mm'] = []
        planet['formats_mm'].append(
            {'name': serie + str(serieNumber), 'size': [width, height]}
        )
        a4equi = None

        while serieNumber < 61:
            serieNumber += 1
            [height, width] = [width, floor(height / 2)]
            planet['formats_mm'].append(
                {'name': serie + str(serieNumber), 'size': [width, height]}
            )
            if a4equi is None and height <= 297:
                a4equi = [width, height] if height > width else [height, width]
                planet['a4equi'] = {'number': serieNumber, 'format': a4equi}

        planets[planet['name']] = planet
    return planets

if __name__ == '__main__':
    planets = defineFormats()
    for planet in planets.values():
        dumpJson('series/' + planet['name'].lower() + '.json', planet)
