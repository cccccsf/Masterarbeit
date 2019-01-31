#!/usr/bin/python3
import os
import sys
import Initialization
from datetime import datetime
from copy import deepcopy
from Crystal import Geometry
from Common import mkdir
from Common import Job_path
from Common import record
from Common import ReadIni
from Common import look_for_in_list
import geometry_optimization
import HF1
import Localization
import HF2
import LMP2
import RPA


def end_programm(path):
    now = datetime.now()
    now = now.strftime("%b %d %Y %H:%M:%S")
    try:
        sys.exit(1)
    except:
        rec = now + '\n'
        rec += 'Programm End...'
        print(rec)
        record(path, rec)


def pipeline(path, start, end):
    anchor = start
    while anchor < end:
        if anchor == 0:
            geometry_optimization.geo_opt(path)
        elif anchor == 1:
            HF1.hf1(path)
        elif anchor == 2:
            Localization.localization(path)
        elif anchor == 3:
            HF2.hf2(path)
        elif anchor == 4:
            LMP2.lmp2(path)
        elif anchor == 5:
            rpa(path)
        anchor += 1
    end_programm(path)

