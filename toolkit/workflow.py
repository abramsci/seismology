#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Wehmut-kvp/PhD/Process/
"""
One-liner for short description of the module.

**Copyright:** 2023, Viktoria Komzeleva (https://github.com/Wehmut-kvp)

**License:** [CC BY-ND 4.0](../LICENSE)

**Core dependencies:**
* Python 3.4+ (`pathlib`)
* obspy (tested for 1.4.0)
"""
################################## IMPORTS ####################################
# Python standard library imports
import copy
from pathlib import Path

# Necessary packages (not in standard library)
import obspy

# Local application/library specific imports
from visualization import plot_picking
from misc import is_power_of_two, prev_power_of_two, TOOLKIT_DIR
from ssd_report import EventRecord

############################## GLOBAL CONSTANTS ###############################
# Paths to directories with waveform data, catalog and output results
# Should evolve to command line arguments as the workflow matures
#SSD_DIR = Path('R:\\', 'KISS_SSD')
SSD_DIR = TOOLKIT_DIR.joinpath('data', 'SSD')
MSEED_DIR = TOOLKIT_DIR.joinpath('data', 'MSEED')


# Processing parameters
MARGIN_SEC = float(10.0)            # Margin for cutting waveform


############################### CORE FUNCTIONS ################################
def read_catalog(dir: Path) -> dict:
    """
    Read and parse all SSD reports in a dir, return catalog - dict of records.
    """
    catalog = {}
    if not dir.is_dir():
        print('Specify a dir with SSD file(s) to read catalog.')
        return catalog
    for path in dir.iterdir():
        event = EventRecord.read(path)
        if event:
            catalog[event.id] = event
    return catalog


def match_waveforms(stream: obspy.Stream, catalog: dict) -> dict:
    """
    Match chosen stream with the catalog to get waveforms dictionary.

    Basic idea: search for any event waveforms inside `stream`
                then cut it to the power of two points window
                datachunk size.

    Returns `waveforms` dictionary: {event_id: datachunk}
        event_id - str (obtained as a key from `catalog` dictionary)
        datachunk - obspy.Stream (deepcopied windowed slice of traces)
    """
    # Preparing returning dictionary as an empty one at the start
    waveforms = {}
    # First we need to get all starttimes and endtimes
    # It is important to check if the datachunk is synchronized
    #       (meaning all the traces start and end at the same time)
    # For the sake of simplicity we need definitive start and end
    #   with which we can compare origin time of events in catalog
    # Going a bit fancy with the syntax (would be too many lines else)
    #   Using list comprehension first and then ternary operator
    #   If all the same then list.count() must be equal to len(list)
    #   This way check and get neseccary start and end at the same time
    starts = [trace.stats.starttime for trace in stream]
    start = starts[0] if starts.count(starts[0]) == len(starts) else None
    ends = [trace.stats.endtime for trace in stream]
    end = ends[0] if ends.count(ends[0]) == len(ends) else None
    if not start or not end:
        print('Not a synchronized stream!\n{stream}')
        return waveforms
    # NOTE: Here are basic ideas of the code below line by line...
    # Key part - checking each event in catalog
    #   A math trick to check if origin inside the datachunk interval
    #       Creating empty stream to store waveforms for catched event
    #       Getting stations that has picks via set comprehension
    #       Checking each station that has picks for the event
    #           and adding selected part of the datachunk to the stream
    #           Setting left side (UTC) of a data window with margin
    #           Calculating middle point of the data window in UTC
    #           Calculating half the size of the data window in seconds
    #           Setting data window right side (UTC)
    #       Adding trimmed stream to the dict with the event_id key
    # Finally returning the whole waveforms dictionary
    for event_id, event in catalog.items():
        if (event.origin.time - start) * (event.origin.time - end) < 0:
            datachunk = obspy.Stream()
            stations = {chan.sta for chan in event.picks.keys()}
            for station in stations:
                datachunk += stream.select(station=station)
            if not datachunk:
                waveforms[event_id] = None
            else:
                dts = {trace.stats.delta for trace in datachunk}
                if len(dts) == 1:
                    delta = datachunk[0].stats.delta
                else:
                    print(f'Different sampling steps in datachunk {datachunk}')
                    print(f'Deltas are {dts}. There might be dragons!')
                    delta = max([dt for dt in dts])
                middle_point_utc = max([pick.time for pick in event.picks.values()])
                size_rough = middle_point_utc - event.origin.time + MARGIN_SEC
                size_sec = prev_power_of_two(size_rough / delta) * delta
                t1 = middle_point_utc - size_sec
                t2 = middle_point_utc + size_sec - delta
                waveforms[event_id] = datachunk.trim(t1, t2)
    return waveforms


def process(stream: obspy.Stream, event: EventRecord, step='raw'):
    stations = {trace.stats.station for trace in stream}
    print(stations)
    #print(f'For {event.id=} we can process:')
    #print(f'\tArrivals total: {len(event.picks)} picks')
    #print(f'\tWaveform data: {len(stations)} stations')
    #stream.select(station='OR13').plot()
    #stream.plot()
    raw_stream = stream.select(station='SV12').detrend('linear')
    #raw_stream = stream.select(component='Z').detrend('linear')[:5]
    #plot_picking(raw_stream)
    #plot_picking(raw_stream, spectrogram=True)
    #plot_picking(raw_stream, event)
    plot_picking(raw_stream, event, spectrogram=True)
    #for trace in raw_stream:
    #    print(trace.stats.npts)
    #for station in stations:
    #    stream.select(station=station).plot()
    return


############################## SCRIPT BEHAIVIOR ###############################
# Python idiom to check if the module is not imported (script behaivior)
if __name__ == '__main__':
    catalog = read_catalog(TOOLKIT_DIR.joinpath('data'))
    stream = obspy.read(TOOLKIT_DIR.joinpath('data', 'example.mseed'), format='MSEED')
    waveforms = match_waveforms(stream, catalog)
    for event_id, datachunk in waveforms.items():
        #datachunk.plot()
        datachunk.write(TOOLKIT_DIR.joinpath('data', '_example.mseed'), format='MSEED')
    exit(0)
###############################################################################

#   # Your script code goes here.
#     catalog = read_catalog(SSD_DIR)
#     # event = catalog['20150911102931.ssd']
#     # print(event)
#     if not catalog:
#         print(f'{SSD_DIR=} does not contain any SSD report files. Aborting.')
#         exit(1)
#     print(f'A catalog of {len(catalog)} events was read from |{SSD_DIR}|\n')
#     for path in MSEED_DIR.iterdir():
#         if path.is_file():
#             try:
#                 datachunk = obspy.read(path, format='MSEED')
#             except Exception as e:
#                 print(f'Skipping... {path=} (not MSEED.) Exception: {e}')
#                 continue
#         if datachunk:
#             waveforms = match_waveforms(datachunk, catalog)
#             if not waveforms:
#                 continue
#             for event_id, stream in waveforms.items():
#                 event = catalog[event_id]
#                 if stream:
#                     print(len(stream))
#                     process(stream, event)
#                 else:
#                     pass
#                     #print('\nWARNING:')
#                     #print(f'No data for {event_id=} read from\n|{path=}|')
#                     #print(f'Yet it fits in time period of the datachunk')