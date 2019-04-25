#!/usr/bin/python3

exchange = ['LDA', 'VBH', 'BECKE', 'mPW91', 'PBE', 'PBESOL', 'PWGGA', 'SOGGA', 'WCGGA']
correlat = ['PWLSD', 'PZ', 'VBH', 'VWN', 'LYP', 'P86', 'PBE', 'PBESOL', 'PWGGA', 'WL']

global_hybrid_functionals = ['B3PW', 'B3LYP', 'PBE0', 'PBESOL0', 'B97H', 'PBE0-13']
range_separated_hybrid_functionals = ['HSE06', 'HSEsol', 'HISS', 'RSHXLDA', 'wB97', 'wB97X', 'LC-wPBE', 'LC-wPBEsol', 'LC-wBLYP']
meta_GGA = ['M06L', 'M052X', 'M06', 'M062X', 'M06HF']
double_hybrid_functionals = ['B2PLYP', 'B2GPPLYP', 'mPW2PLYP']

functionals = global_hybrid_functionals+range_separated_hybrid_functionals+meta_GGA+double_hybrid_functionals
functionals_upper = []
for func in functionals:
    functionals_upper.append(func.upper())
functionals = dict(zip(functionals_upper, functionals))
#print(functionals)
