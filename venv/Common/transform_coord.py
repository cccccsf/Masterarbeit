#!/usr/bin/python3

def coordinate_transformer(coor):
    coor = coor[1:-1]
    coor = coor.split(', ')
    coordinate = []
    for c in coor:
        c = float(c[1:-1])
        coordinate.append(c)
    return coordinate


# a = "('2.5', '5.00')"
# transform_coordinate(a)
