#!/usr/bin/python3
import os
from Common import  Job_path
from HF2.generation_input_hf2 import Input
from HF2 import Layer_Inp
from HF2 import hf2

def test_Input():
    path = r'C:\Users\ccccc\Documents\Theoritische Chemie\Masterarbeit\test\hf_1\x_-0.150\z_-0.106'
    hf1_path = Job_path(path)
    Inp = Input(hf1_path, 'blackP', 'SLAB', '1')
    Inp.gen_input()

def test_Inp_Layer():
    path = r'C:\Users\ccccc\Documents\Theoritische Chemie\Masterarbeit\test\hf_1\x_-0.150\z_-0.106\underlayer'
    hf1_path = Job_path(path)
    Inp = Layer_Inp(hf1_path, 'blackP', 'SLAB', '1', 'underlayer')
    #print(Inp.ghost)
    Inp.gen_input()

def test_hf2():
    path = r'C:\Users\ccccc\Documents\Theoritische Chemie\Masterarbeit\test'
    hf2(path)



def test_suite():
    #test_Input()
    #test_Inp_Layer()
    test_hf2()

test_suite()
