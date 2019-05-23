#!/usr/bin/python3
from Common import unit_transform
from Common.is_number_func import is_number


def cal_layer_energy(bilayer, upperlayer, underlayer):

    # split energy value and unit
    e_bilayer, unit_bilayer = bilayer
    e_upper, unit_upper = upperlayer
    e_under, unit_under = underlayer

    if not is_number(e_bilayer) or not is_number(e_upper) or not is_number(e_under):
        print('Energy form not crect.')
        print('Please check and try again.')
        return 0

    # transform unit if needed
    if unit_upper != unit_bilayer:
        e_upper = unit_transform(e_upper, unit_upper, unit_bilayer)
    if unit_under != unit_bilayer:
        e_under = unit_transform(e_under, unit_under, unit_bilayer)

    layer_energy = str(float(e_bilayer) - float(e_upper) - float(e_under))
    return [layer_energy, unit_bilayer]
