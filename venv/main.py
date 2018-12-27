#!/usr/bin/python3
import os
import Initialization
import Pipeline

def menu():

    path = os.getcwd()
    Pipeline.pipeline(path)








if  __name__ == "__main__":

    menu()
