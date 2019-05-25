from json import load, dump


def getJson(filename):
    with open(filename, 'r') as f:
        return load(f)

def dumpJson(filename, data):
    with open(filename, 'w') as f:
        dump(data, f, ensure_ascii=False, indent=2, separators=(',', ': '))

def km2mm(value):
    return value * 10**6
