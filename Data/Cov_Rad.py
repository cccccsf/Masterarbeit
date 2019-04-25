#!/usr/bin/python3
import os
import csv


def read_csc():
    path = os.path.dirname(os.path.realpath(__file__))
    radii_path = os.path.join(path, 'radii.csv')
    list = []
    with open(radii_path, encoding='utf-8') as f:
        radii_csv = csv.reader(f)
        headers = next(radii_csv)
        for row in radii_csv:
            list.append(row)

    return headers, list


def read_cov_rad(ele, unit='pm'):
    headers, list = read_csc()
    cov_rad = {}
    for e in list:
        cov_rad[e[0]] = e[6]
    rad = cov_rad[str(ele)]
    if rad == 'no data':
        return rad
    else:
        rad = float(rad)
        if unit.startswith('a'):
            rad = rad/100
        elif unit == 'nm':
            rad = rad/1000
        return rad











def test():
    read_cov_rad('15')

#test()
