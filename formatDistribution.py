from math import sqrt
from json import dump


def formatsInFormat0():
    total = 1
    formatsInSerie = []
    for n in range(1, 70):
        step = {'formatNumber': n, 'total': total * 2}
        if n % 2 is 0:
            size = int(sqrt(total * 2))
            step['distribution'] = [size, size]
            step['orientation'] = "portrait"
        else:
            size = int(sqrt(total))
            step['distribution'] = [size, size * 2]
            step['orientation'] = "landscape"
        formatsInSerie.append(step)
        total *= 2
    return formatsInSerie

if __name__ == '__main__':
    result = formatsInFormat0()

    with open('data/formatsDistribution.json', 'w') as f:
        dump(result, f, ensure_ascii=False, indent=2, separators=(',', ': '))
