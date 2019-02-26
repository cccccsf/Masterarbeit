#!/usr/bin/python3



class FactorCalculator(object):

    def __init__(self, cluster):
        self.cluster = cluster
        self.dimen = self.cluster.dimensionality
        self.center = self.cluster.centre
        self.lattice_vector = self.cluster.lattice_vector
        print(self.lattice_vector)
