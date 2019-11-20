#!/usr/bin/python3


def choose_shrink(lattice_parameter):
    try:
        length = lattice_parameter[0]
        avr = sum(length)/len(length)
        if avr <= 3:
            shrink = 14
        elif avr <= 3:
            shrink = 12
        elif avr <= 4.5:
            shrink = 8
        elif avr <= 6:
            shrink = 6
        elif avr <= 4:
            shrink = 4
    except ZeroDivisionError:
        shrink = 8
    return shrink
