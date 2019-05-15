from math import sqrt, floor
from json import load, dump


def getJson(filename):
    with open(filename, 'r') as f:
        return load(f)

def defineFormats():
    objects = getJson('surfaces.json')
    formats = []

    for object in objects:
        # 'surface' is in km²
        surface = object['surface']
        # sqrt(2) == 1.4142135623730951
        height = sqrt(surface * 1.4142135623730951)
        width = surface / height
        object['preciseSizeKm2'] = [width, height]

        # turn kilometers into millimeter
        height = round(height * 1000000)
        width = round(width * 1000000)
        object['sizeMM'] = [width, height]

        n = 0
        while height > 1000:
            if height > width:
                height = floor(height / 2)
            else:
                width = floor(width / 2)
            n += 1
        object['number'] = str(n) + ' (' + str(width) + ', ' + str(height) +')'
        formats.append(object)

    with open('output.json', 'w') as f:
        dump(formats, f, indent=2, separators=(',', ': '))

if __name__ == '__main__':
    defineFormats()
