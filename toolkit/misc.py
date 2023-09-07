#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# abramsci/seismology/toolkit/misc.py
"""
Miscellaneous quality of life functions.

**Copyright:** 2023, Sergei Abramenkov (https://github.com/abramsci)

**License:** [MIT](../LICENSE)
* Python 3.4+ (`pathlib`)
"""
################################## IMPORTS ####################################
# Python standard library imports
from pathlib import Path
import math

# Necessary packages (not in standard lib)
import obspy


############################## GLOBAL CONSTANTS ###############################
TOOLKIT_DIR = Path(__file__).parent


############################ BASIC MATH FUNCTIONS #############################
def is_power_of_two(n: int) -> bool:
    return (n & (n-1) == 0) and n != 0

def prev_power_of_two(x: float) -> int:
    return int(math.pow(2, math.floor(math.log2(x))))

def next_power_of_two(x: float) -> int:
    return int(math.pow(2, math.ceil(math.log2(x))))

def nearest_power_of_two(x: float) -> int:
    lesser = prev_power_of_two(x)
    bigger = next_power_of_two(x)
    return lesser if abs(x - lesser) < abs(bigger - x) else bigger


########################### OBSPY RELATED FUNCTIONS ###########################
def get_code(stats: obspy.core.trace.Stats) -> str:
    return f'{stats.network}.{stats.station}.{stats.location}.{stats.channel}'