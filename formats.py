from json import load, dump


def getJson(filename):
    with open(filename, 'r') as f:
        return load(f)

def defineFormat():
    objects = getJson('surfaces.json')
    formats = []

    for object in objects:
        object['result'] = []
        surface = round(object['surface'] / 1000000)
        object['surfaceApprox'] = surface
        prevY = surface + 1
        x = 1
        while x < prevY:
            result = surface / x
            y = round(result, 2)
            if y == result:
                object['result'].append([x, y])
                prevY = y
            x = round(x + 0.01, 2)
        formats.append(object)

    with open('output.json', 'w') as f:
        dump(formats, f, indent=2, separators=(',', ': '))

if __name__ == '__main__':
    defineFormat()
