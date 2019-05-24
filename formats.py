from math import sqrt, floor
from json import load, dump


def getJson(filename):
    with open(filename, 'r') as f:
        return load(f)

def rectSize(surfaceArea):
    # Define rectangle's size so height * width == surfaceArea
    # and height / width == √2 == 1.4142135623730951
    height = sqrt(surfaceArea * 1.4142135623730951)
    return [surfaceArea / height, height]

def defineFormats():
    for planet in getJson('surfaces.json'):
        # 'surface' is in km²
        surface = planet['surface']
        serie = planet['serie']
        width, height = rectSize(surface)
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
            # '{}0: {} × {} mm'.format(serie, width, height)
            {'name': serie + str(serieNumber), 'size': [width, height]}
        )
        a4equi = None

        while serieNumber < 61:
            serieNumber += 1
            [height, width] = [width, floor(height / 2)]
            planet['formats_mm'].append(
                # '{}{}: {} × {} mm'.format(serie, serieNumber, width, height)
                {'name': serie + str(serieNumber), 'size': [width, height]}
            )
            if a4equi is None and height <= 297:
                a4equi = [width, height] if height > width else [height, width]
                planet['a4equi'] = {'number': serieNumber, 'format': a4equi}

        with open('series/' + planet['planet'].lower() + '.json', 'w') as f:
            dump(planet, f, ensure_ascii=False, indent=2, separators=(',', ': '))

if __name__ == '__main__':
    defineFormats()
