from json import load, dump
from ruamel.yaml import YAML

def getJson(filename):
    with open(filename, 'r') as f:
        return load(f)

def getYaml(filename):
    yaml=YAML(typ='safe')
    with open(filename, 'r') as f:
        return yaml.load(f)

def getText(filename):
    with open(filename, 'r') as f:
        return f.read()

def dumpJson(filename, data):
    with open(filename, 'w') as f:
        dump(data, f, ensure_ascii=False, indent=2, separators=(',', ': '))

def km2mm(value):
    return value * 10**6
