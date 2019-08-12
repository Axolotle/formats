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

def numberToCharacter(number, lang='fr'):
    trad = numToChar[lang]
    numberStr = str(number)
    link = '-'
    if number <= 20 or (len(numberStr) == 2 and numberStr[1] == '0'):
        return trad[numberStr]
    if lang == 'en':
        return trad[numberStr[0] + '0'] + link + trad[numberStr[1]]
    if numberStr[0] in ['7', '9']:
        if number == 71:
            link = ' et '
        return trad[str(number - 10)[0] + '0'] + link + trad['1' + numberStr[1]]
    if numberStr[1] == '1' and number != 81:
        link = ' et '
    return trad[numberStr[0] + '0'] + link + trad[numberStr[1]]

numToChar = getYaml('data/textsPrint.yaml')['digits']
