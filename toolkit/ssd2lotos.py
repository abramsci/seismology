#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# <author-github>/<repository>/<filepath/name>
"""
Convert SSD files into LOTOS input files: `stat_ft.dat` and `rays.dat`.

**Copyright:** 2023, Sergei Abramenkov (https://github.com/abramsci)

**License:** [MIT](../LICENSE)

**Core dependencies:**
* Python 3.4+ (`pathlib`)
* obspy (tested for 1.4.0)
"""
################################## IMPORTS ####################################
# Python standard library imports
from pathlib import Path

# Necessary packages (not in standard lib)
import obspy

# Local application/library specific imports
from misc import TOOLKIT_DIR
import ssd_report

############################## GLOBAL CONSTANTS ###############################
# Paths to directories/files - may/should evolve to command line arguments
SSD_DIR = TOOLKIT_DIR.joinpath('data', 'in')
LOTOS_DIR = TOOLKIT_DIR.joinpath('data', 'out')


############################## SCRIPT BEHAIVIOR ###############################
# Python idiom to check if the module is not imported (i.e. script behaivior)
if __name__ == '__main__':
    catalog = ssd_report.read_catalog(SSD_DIR)
    stat_ft, rays = ssd_report.extract_LOTOS_inidata(catalog)
    print(stat_ft,  file=open(LOTOS_DIR.joinpath('stat_ft.dat'), 'w'))
    print(rays,  file=open(LOTOS_DIR.joinpath('rays.dat'), 'w'))
    # Return error code 0 back to shell if everything works ok.
    exit(0)
###############################################################################