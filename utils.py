from json import load, dump
from ruamel.yaml import YAML

decSep = {
    'si': '.',
    'fr': ',',
    'en': '.',
}
sep = {
    'si': ' ',
    'fr': ' ',
    'en': ',',
}

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

def stringifyNumber(value, lang='fr'):
    num = str(value)
    if '.' in num:
        num = num.split('.')
        number = sep[lang].join(chunk_str(num[0][::-1], 3))[::-1]
        dec = sep[lang].join(chunk_str(num[1], 3))
        return number + decSep[lang] + dec
    else:
        return sep[lang].join(chunk_str(num[::-1], 3))[::-1]

def chunk_str(str, chunk_size):
   return [str[i:i+chunk_size] for i in range(0, len(str), chunk_size)]
