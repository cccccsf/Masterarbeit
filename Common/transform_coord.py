#!/usr/bin/python3

def coordinate_transformer(coor, sequece=True):
    if sequece == True:
        coor = coor[1:-1]
        coor = coor.split(', ')
        coordinate = []
        for c in coor:
            c = float(c[1:-1])
            coordinate.append(c)
        return coordinate
    else:
        coor = '({}, {})'.format(coor[0], coor[1])
        return coor



# a = "('2.5', '5.00')"
# transform_coordinate(a)
