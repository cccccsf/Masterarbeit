#!/usr/bin/python3


def get_extrapolated_correction(e1, e2, x, y):
    """
    get the extrapolated basis-set limit Exy
    :param e1: energy with basis-set of cardinal number x
    :param e2: energy with basis-set of cardinal number y
    :param x: the cardinal number of the first basis-set
    :param y: the cardinal number of the second basis-set
    :return:
    """
    return (x**3 * e1 - y**3 * e2) / (x**3 - y**3)

# print(get_extrapolated_correction(-84.4, -99.7, 2, 3))
# print(get_extrapolated_correction(-45, -52.8, 2, 3))
# print(get_extrapolated_correction(-52.8, -55, 3, 4))
