#!/usr/bin/python3


def look_for_in_list(list, ziel):
    point = 0
    i = 0
    for j in list:
        if j == ziel:
            point = i
        i += 1
    return point
