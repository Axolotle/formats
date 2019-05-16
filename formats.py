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

        serieNumber = 0
        planet['formats'] = []
        planet['formats'].append(
            '{}0: {} × {} mm'.format(serie, width, height)
        )

        # Based on Earth format serie 'E', E49 seems to be the closest format
        # to A0 and can be contained in it. We also choose to stop calculating
        # formats after 59 iterations (E59 ~= A10).
        while serieNumber < 59:
            serieNumber += 1
            if height > width:
                height = floor(height / 2)
                planet['formats'].append(
                    '{}{}: {} × {} mm'.format(serie, serieNumber, height, width)
                )
            else:
                width = floor(width / 2)
                planet['formats'].append(
                    '{}{}: {} × {} mm'.format(serie, serieNumber, width, height)
                )

        with open('series/' + serie + '.json', 'w') as f:
            dump(planet, f, ensure_ascii=False, indent=2, separators=(',', ': '))

if __name__ == '__main__':
    defineFormats()
