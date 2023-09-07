#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# abramsci/seismology/toolkit/csv2mseed.py
"""
Convert table of numbers from CSV text file to seismic traces in MSEED file.

**Copyright:** 2023, Sergei Abramenkov (https://github.com/abramsci)

**License:** [MIT](../LICENSE)

**Core dependencies:**
* Python 3.4+ (`pathlib`)
* obspy (tested for 1.4.0)
* pandas(tested for 2.0.3)
"""
################################## IMPORTS ####################################
# Python standard library imports
from pathlib import Path

# Necessary packages (not in standard lib)
import obspy
import pandas


############################## GLOBAL CONSTANTS ###############################
# Some hardcoded processing parameters - easier to keep track of
STATION: str = 'XXXXX'
T0 = obspy.UTCDateTime('2023-08-22T14:33:36.57000')
DELTA_T: float = 0.01
CHANNELS: dict = {0: 'N-S', 3: 'E-W', 6: 'Z'}


############################### CORE FUNCTIONS ################################
def make_stream(df: pandas.DataFrame, delta: float) -> obspy.Stream:
    traces = [obspy.Trace(data=df[column].to_numpy(), 
                          header=obspy.core.Stats({'delta': DELTA_T,
                                                   'starttime': T0,
                                                   'npts': len(df[column]),
                                                   'station': STATION,
                                                   'channel': str(column)}))
              for column in df]
    return obspy.Stream(traces)


############################## SCRIPT BEHAIVIOR ###############################
# Python idiom to check if the module is not imported (i.e. script behaivior)
if __name__ == '__main__':
    in_file = input('Input text (CSV) file path: ')
    if Path(in_file).is_file():
        df = pandas.read_csv(in_file, delimiter=' ', header=None, 
                             encoding='latin-1', skiprows=range(0, 21),
                             usecols=CHANNELS.keys())
        df.rename(columns=CHANNELS, inplace=True)
        print(df)
    else:
        print(f'Seems you need to check if {in_file} is an existing file.')
        exit(1) # No input file found.
    stream = make_stream(df, DELTA_T)
    print(stream)
    stream.plot()
    out_file = input('Output MSEED file path: ')
    stream.write(out_file, format='MSEED')
    exit(0)     # Return error code 0 back to shell if everything works ok.
###############################################################################