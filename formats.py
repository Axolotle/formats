from math import sqrt, floor, pi, atanh
from json import load, dump


def getJson(filename):
    with open(filename, 'r') as f:
        return load(f)

def surfaceAreaOfOblateEllipsoid(a, b):
    # http://www.numericana.com/answer/geometry.htm#oblate
    # e = √(1-b²/a²)
    # S = 2πa² [1 + (b/a)² atanh(e)/e]

    if a == b:
        # if it's a sphere return with Archimedes's formula
        return 4 * pi * a**2
    e = sqrt(1 - b**2 / a**2)
    return 2 * pi * a**2 * (1 + (b/a)**2 * atanh(e) / e)

def surfaceAreaOfOblateSpheroid(a, b):
    # http://www.numericana.com/answer/ellipsoid.htm#oblate
    # e = √(1-b²/a²)
    # A = 2π [a² + b² atanh(e)/e]
    e = sqrt(1 - b**2 / a**2)
    return 2 * pi * (a**2 + b**2 * atanh(e) / e)

def radiusOfSphere(surfaceArea):
    # r = √[A / (4 * π)]
    print(sqrt(surfaceArea / (4 * pi)))

def rectSize(surfaceArea):
    # Define rectangle's size so height * width == surfaceArea
    # and height / width == √2 ~= 1.4142135623730951
    height = sqrt(surfaceArea * 1.4142135623730951)
    return [surfaceArea / height, height]

def defineFormats():
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

        with open('series/' + planet['name'].lower() + '.json', 'w') as f:
            dump(planet, f, ensure_ascii=False, indent=2, separators=(',', ': '))

if __name__ == '__main__':
    defineFormats()
    # for planet in getJson('surfaces.json'):
    # radiusOfSphere(510067420)
    # radiusOfSphere(surfaceAreaOfOblateEllipsoid())
