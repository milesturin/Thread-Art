from math import sin, cos, pi

DIAMETER = 18
MARGIN = 0.25
NAILS = 300
actual_nails = NAILS // 2
actual_dist = DIAMETER / 2 - MARGIN
for i in range(actual_nails):
    rad = i / actual_nails * pi
    print(f'{i}: ({round(cos(rad) * actual_dist, 3)}, {round(sin(rad) * actual_dist, 3)')
