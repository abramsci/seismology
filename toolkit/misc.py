#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# abramsci/seismology/toolkit/misc.py
"""
Miscellaneous quality of life functions.

**Copyright:** 2023, Sergei Abramenkov (https://github.com/abramsci)

**License:** [MIT](../LICENSE)
"""
################################## IMPORTS ####################################
# Python standard library imports
import math


############################ BASIC MATH FUNCTIONS #############################
def is_power_of_two(n: int) -> bool:
    return (n & (n-1) == 0) and n != 0

def prev_power_of_two(x: float) -> int:
    return int(math.pow(2, math.floor(math.log2(x))))

def next_power_of_two(x: float) -> int:
    return int(math.pow(2, math.ceil(math.log2(x))))

def nearest_power_of_two(x: float) -> int:
    lesser = prev_power_of_two(x)
    bigger = next_pow_of_two(x)
    return lesser if abs(x - lesser) < abs(bigger - x) else bigger

