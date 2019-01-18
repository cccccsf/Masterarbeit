#!/usr/bin/python3
import os
import Initialization
import Pipeline

def menu():

    #path = 'C:\\Users\\ccccc\\Documents\\Theoritische Chemie\\Masterarbeit\\test'
    path = os.getcwd()
    path = os.path.dirname(path)
    path = os.path.join(path, 'Test')
    Pipeline.pipeline(path)








if  __name__ == "__main__":
    menu()
