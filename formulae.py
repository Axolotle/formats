from math import pi, sqrt, atanh


sqrt2 = 1.4142135623730951
sqrt1_2 = 0.7071067811865476

def areaOfOblateEllipsoid(a, b):
    # http://www.numericana.com/answer/geometry.htm#oblate
    # e = √(1-b²/a²)
    # S = 2πa² [1 + (b/a)² atanh(e)/e]

    if a == b:
        # if it's a sphere return with Archimedes's formula
        return 4 * pi * a**2
    e = sqrt(1 - b**2 / a**2)
    return 2 * pi * a**2 * (1 + (b/a)**2 * atanh(e) / e)

def areaOfOblateSpheroid(a, b):
    # http://www.numericana.com/answer/ellipsoid.htm#oblate
    # e = √(1-b²/a²)
    # A = 2π [a² + b² atanh(e)/e]
    e = sqrt(1 - b**2 / a**2)
    return 2 * pi * (a**2 + b**2 * atanh(e) / e)

def radiusOfSphere(area):
    # r = √[A / (4 * π)]
    return sqrt(area / (4 * pi))

def sqrt2Rect(area):
    # Define rectangle's size so height * width == area
    # and height / width == √2 ~= 1.4142135623730951
    height = sqrt(area * sqrt2)
    return [area / height, height]

def km2mm(value):
    return value * 10**6
