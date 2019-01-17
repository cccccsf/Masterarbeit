#!/usr/bin/python3


def choose_shrink(lattice_parameter):
    length = []
    angle = []
    for i in lattice_parameter:
        i = float(i)
        if i <= 20:
            length.append(i)
        else:
            angle.append(i)
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

    return  shrink
