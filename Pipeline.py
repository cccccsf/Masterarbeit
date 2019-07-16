#!/usr/bin/python3
import sys
from datetime import datetime
from Common import record
from Common import ReadIni
import GeoOPt
import HF1
import Localization
import HF2
import LMP2
import RPA
import Cluster
import Correction
import Results
import Monitor


def end_programm(path):
    now = datetime.now()
    now = now.strftime("%b %d %Y %H:%M:%S")
    rec = 'Program End.\n'
    rec += '***'*25
    print(now)
    print(rec)
    record(path, rec)
    try:
        sys.exit(1)
    except Exception:
        print('Program exit.')


def pipeline(path, start, end):
    moni = Monitor.Monitor(path)
    anchor = start
    while anchor < end:
        # print(anchor, end)
        if anchor == 0:
            GeoOPt.geo_opt(path, moni)
        elif anchor == 1:
            HF1.hf1(path)
        elif anchor == 2:
            Localization.localization(path)
        elif anchor == 3:
            HF2.hf2(path, moni)
        elif anchor == 4:
            LMP2.lmp2(path, moni)
            if if_skip_rpa() == 1:
                anchor += 1
        elif anchor == 5:
            RPA.rpa(path)
        elif anchor == 6:
            Cluster.cluster(path)
        elif anchor == 7:
            Correction.correction(path)
        elif anchor == 8:
            Results.results(path)
        anchor += 1
    end_programm(path)


def if_skip_rpa():
    Ini = ReadIni()
    ll = Ini.ll
    if ll.upper() != 'LDRCCD':
        skip_rpa = 1
    else:
        skip_rpa = 0
    return skip_rpa


if __name__ == '__main__':
    if_skip_rpa = if_skip_rpa()
