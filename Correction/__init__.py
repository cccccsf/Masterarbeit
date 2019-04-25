#!/usr/bin/python3
from Correction.correction import correction
from Correction.input_generation import generation_input
from Correction.molpro_bs import Molpro_Bs
from Correction.scr_generation import Script
from Correction.submit_job import if_cal_finish
from Correction.submit_job import submit
from Correction.read_results import Result
from Correction.read_results import read_all_results
