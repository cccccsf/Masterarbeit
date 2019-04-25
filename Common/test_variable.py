#!/usr/bin/python3
from Basis_Set import basis_set_catalog
from Data.Functionals import functionals

def test_slab_or_molecule(slab_or_molecule):
    slab_or_molecule = slab_or_molecule.upper()
    if slab_or_molecule == 'SLAB' or 'MOLECULE':
        return True
    else:
        return False


def test_group(group, slab_or_molecule):
    group = int(group)
    if slab_or_molecule == 'SLAB':
        if group >= 1 and group <= 80:
            return True
        else:
            return False
    else:
        if group >= 1 and group <= 47:
            return True
        else:
            return False


def test_lattice_parameter(lattice_parameter, slab_or_molecule):
    return True


def transfer_to_float(geometry):
    new_geometry = []
    for atom in geometry:
        new_atom = []
        for unit in atom:
            new_unit = float(unit)
            new_atom.append(new_unit)
        new_geometry.append(new_atom)
    return new_geometry


def test_geometry(atom_number, geometry, slab_or_molecule):
    geometry = transfer_to_float(geometry)
    atom_number = int(atom_number)
    if len(geometry) != atom_number:
        return False
    for atom in geometry:
        if len(atom) != 4:
            return False
        if atom[0] < 1 or atom[0] > 119:
            return False
        if slab_or_molecule == 'SLAB':
            if (atom[1] < -1 or atom[1] > 1) or (atom[2] < -1 or atom[2] > 1):
                return False
    return True


def test_bs_type(bs_type):
    if bs_type == 'default':
        print('Basis Set default...')
        return True
    bs_type = bs_type.lower()
    if bs_type not in basis_set_catalog.bs_dicts:
        return False
    return True


def test_functional(functional):
    functional = functional.upper()
    if functional not in functionals:
        return False
    return True


def test_variable(slab_or_molecule, group, lattice_para, number_of_atoms, geometry, bs_type, functional):
    test_variable = []
    test_variable.append(test_slab_or_molecule(slab_or_molecule))
    test_variable.append(test_group(group))
    test_variable.append(test_lattice_parameter(lattice_para))
    test_variable.append(test_geometry(number_of_atoms, geometry))
    test_variable.append(test_bs_type(bs_type))
    test_variable.append(test_functional(functional))
