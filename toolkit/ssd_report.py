#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# abramsci/seismology/toolkit/ssd_report.py
"""
A collection of (data)classes for handling SSD report format (DIMAS app)
 
**Copyright:** 2023, Sergei Abramenkov (https://github.com/abramsci)
                     Viktoria Komzeleva (https://github.com/Wehmut-kvp)

**License:** [MIT](../LICENSE)

**Core dependencies:**
* Python 3.10+ (match-statement=3.10, `dataclasses`=3.7, f-strings=3.6)
* obspy (tested for 1.4.0)
"""
################################## IMPORTS ####################################
# Python standard library imports
from dataclasses import dataclass
from pathlib import Path

# Necessary packages (not in standard library)
from obspy import UTCDateTime
from obspy.core.event.base import QuantityError

# Local application/library specific imports
from misc import TOOLKIT_DIR, get_paths


############################## GLOBAL CONSTANTS ###############################
# Paths to directories/files - may/should evolve to command line arguments
SSD_EXAMPLE_PATH = TOOLKIT_DIR.joinpath('data', 'example.ssd')
SSD_OLD_EXAMPLE_PATH = TOOLKIT_DIR.joinpath('data', 'old_example.ssd')


############################# AUXILIARY FUNCTIONS #############################
def _cleanup(line: str):
    """
    Clearing the SSD line string from different whitespace symbols.

    Ex: '#CHANNEL SV05 TC 20-HHN\t 1 6 "##03 55.9952,160.429,1835,0"\n'
    will becomes '#CHANNEL SV05 TC 20-HHN 1 6 ##03 55.9952,160.429,1835,0'
    """
    words = line.replace('\t', ' ').replace('"', '').split()
    return ' '.join(words)


################################## CLASSES ####################################
@dataclass(frozen=True)
class ChannelInfo:
    """
    CHANNEL information line of SSD report.

    Attributes/content:
        net - Network code (ex. 'D0' or 'X9', default 'XX').
        sta - Station code (ex. 'GRL' or 'SV05').
        loc - Location code (ex. '00' or '20').
        cha - Channel code (ex. 'SHZ' or 'BHN').
        info - Remaining part of the string with various channel info.
                TODO: Figure out what contains in this part.

    Methods:
        get_code() - Return SEED code (<net>.<sta>.<loc>.<cha>)
    """
    net: str
    sta: str
    loc: str
    cha: str
    info: str

    @classmethod
    def _parse(cls, line: str):
        """
        Ex. of words:
        ['SV05', 'TC', '20-HHN', '1', '6', '##03', '55.9952,160.429,1835,0']
        Two basic parts: (1) channel code parts and (2) info
        """
        words = _cleanup(line).split(' ')[1:]
        if len(words) < 3:
            print('WARNING: Not enough codes in CHANNEL line!')
            return None
        station, network, loc_cha, *info = words
        *location, channel = loc_cha.split('-')
        info = ' '.join(info)
        if not location:
            location = ''
        else:
            location = ''.join(location)
        return cls(network, station, location, channel, info)

    def get_code(self) -> str:
        return f'{self.net}.{self.sta}.{self.loc}.{self.cha}'


@dataclass
class PickRecord:
    """
    Parameters of the ARRIVAL block in SSD file.

    Attributes/parameters:
        phase - Phase identification letter (i.e. 'S' or 'P').
        time - Observed onset time of signal (“pick time”).
        level - Signal amplitude at the onset time.
        qual - Onset quality (ex. 'i' - impulsive, 'e' - emeregent)
        sign - Sign of the phase following onset ('-', '+', '?').
        dist - Distance to the origin (km).
        baz - Back-azimuth to the origin (degrees)
    """
    phase: str
    time: UTCDateTime
    level: float
    qual: str
    sign: str
    dist: float
    baz: float

    @classmethod
    def _parse(cls, block: list[str]):
        # Empty (for now) definitions for the class default contructor
        phase = None; time = None; level = None; qual = None
        sign = None; dist = None; baz = None
        # Eliminating loop to parse block info into attributes
        while block:
            line = _cleanup(block[0])
            words = line.split(' ')[1:]
            block.pop(0)
            match words:
                case '[Phase]', ph_str:
                    phase = str(ph_str)
                case '[Time]', date_str, time_str:
                    year, month, day = date_str.split('.')
                    hour, min, sec = time_str.split(':')
                    time = UTCDateTime(int(year), int(month), int(day),
                                       int(hour), int(min), float(sec))
                case '[Level]', level_str:
                    level = float(level_str)
                case '[Quality]', qual_str:
                    qual = str(qual_str)
                case '[Sign]', sign_str:
                    sign = str(sign_str)
                case '[Dist-Az]', distaz_str:
                    dist, baz, *_ = tuple(float (i) for i
                                          in distaz_str.split(';'))
        # After block is exhausted - call default class constructor
        return cls(phase, time, level, qual, sign, dist, baz)


@dataclass
class AmplitudeRecord:
    """
    Parameters of the AMPLITUDE block in SSD file.

    Attributes/parameters:
        phase - Phase used to determine the amplitude (likely 'S').
        time -  UTC time moment used for amplitude measurement.
        kind -  Amplitude type ('A' for uspecified amplitude).
        sens - Channel sensetivity.
        counts - Channel digital value at the time moment.
        ampl - Waveform measured amplitude (microns per second).
        per - Dominant period in the measurement window.
        mag - Energy class (magnitude?) at the channel.
    """
    phase: str
    time: UTCDateTime
    kind: str
    sens: float
    counts: float
    ampl: float
    unit: str
    per: float
    mag: float

    @classmethod
    def _parse(cls, block: list[str]):
        # Empty (for now) definitions for the class default contructor
        phase = None; time = None; kind = None; sens = None
        counts = None; ampl = None; unit = None; per = None; mag = None
        # Eliminating loop to parse block info into attributes
        while block:
            line = _cleanup(block[0])
            words = line.split(' ')[1:]
            block.pop(0)
            match words:
                case '[Phase]', ph_str:
                    phase = str(ph_str)
                case '[Time]', date_str, time_str:
                    year, month, day = date_str.split('.')
                    hour, min, sec = time_str.split(':')
                    time = UTCDateTime(int(year), int(month), int(day),
                                       int(hour), int(min), float(sec))
                case '[Pribor]', kind_str:
                    kind = str(kind_str)
                case '[Sens]', sens_str:
                    sens = float(sens_str)
                case '[Counts]', counts_str:
                    counts = float(counts_str)
                case '[Amplitude]', ampl_str, unit_str:
                    ampl = float(ampl_str)
                    unit = str(unit_str)
                case '[Period]', per_str:
                    per = float(per_str)
                case '[Magnitude]', _, mag_str, *_:
                    mag = float(mag_str)
        # After block is exhausted - call default class constructor
        return cls(phase, time, kind, sens, counts, ampl, unit, per, mag)


@dataclass
class OriginRecord:
    """
    Parameters of the EARTHQUAKE block in SSD file.

    Attributes/parameters:
        time - Origin time (necessary parameter).
        t_err - Origin time error estimation.
        lat - Hypocenter longitude (degrees, WGS84 geoid).
        lon - Hypocenter latitude, (degrees, WGS84 geoid).
        l_err - Lateral error.
        depth - Hypocenter depth from the sea level (km, WGS84 geoid).
        d_err - Depth error.
        gdg - String ID of the DIMAS 1D velocity model.
        loc_lim - Location limits ??? TODO: figure out what they are?
        mag - Energy class value (or magnitude? - TODO: figure out)
        n_sta - Number of station used to determine magnitude/energy.
    """
    time: UTCDateTime
    t_err: QuantityError
    lat: float
    lon: float
    l_err: QuantityError
    depth: float
    d_err: QuantityError
    gdg: str
    loc_lim: tuple[float, float, float, float]
    mag_type: str
    mag: float
    n_sta: int

    @classmethod
    def _parse(cls, block: list[str]):
        # Empty (for now) definitions for the class default contructor
        time = None; t_err = None; lat = None; lon = None
        l_err = None; depth = None; d_err = None; gdg = None
        loc_lim = None; mag_type = None; mag = None; n_sta = None
        # Eliminating loop to parse block info into attributes
        while block:
            line = _cleanup(block[0].replace('=',' '))
            words = line.split(' ')[1:]
            block.pop(0)
            match words:
                case '[Origin', 'Time]', date_str, time_str:
                    year, month, day = date_str.split('.')
                    hour, min, sec = time_str.split(':')
                    time = UTCDateTime(int(year), int(month), int(day),
                                       int(hour), int(min), float(sec))
                case '[Origin', 'Error]', t_err_str:
                    t_err = QuantityError(float(t_err_str))
                case '[Latitude]', lat_str:
                    if lat_str[-1] == 'S':
                        lat = -float(lat_str[:-1])
                    elif lat_str[-1] == 'N':
                        lat = float(lat_str[:-1])
                    else:
                        lat = float(lat_str)
                case '[Delta', 'Error]', err_str:
                    l_err = QuantityError(float(err_str))
                case '[Longitude]', lon_str:
                    if lon_str[-1] == 'W':
                        lon = -float(lon_str[:-1])
                    elif lon_str[-1] == 'E':
                        lon = float(lon_str[:-1])
                    else:
                        lon = float(lon_str)
                case '[Delta', 'Error]', l_err_str:
                    l_err = QuantityError(float(l_err_str))
                case '[Depth]', depth_str:
                    depth = float(depth_str)
                case '[Depth', 'Error]', d_err_str:
                    d_err = QuantityError(float(d_err_str))
                case '[Travel', 'Times]', gdg:
                    pass
                case '[Location', 'Limits]', loc_lim_str:
                    # Using tuple comprehension - less code, more sense
                    loc_lim = tuple(float(i) for i in loc_lim_str.split(';'))
                case '[Magnitude]', mag_type, mag_str, *n_sta_str:
                    mag = float(mag_str)
                    if n_sta_str:
                        n_sta = int(n_sta_str[0].strip('()'))
        # After block has exhausted - check for nessesary parameter
        if not time:
            return None
        # If necessary parameter exists - call default constructor
        return cls(time, t_err, lat, lon, l_err, depth,
                   d_err, gdg, loc_lim, mag_type, mag, n_sta)


@dataclass
class EventRecord:
    """
    A representation of a seismic event info based on DIMAS SSD report.

    NOTE:
        Old versions use misspelled keyword #ARRIVEL so during parsing
        we simply rely on .startswith('#ARRIV') to catch either.
        Also - instead of #SSDREPORT, old versions use #FILENAME word.
    """
    name: str
    origin: OriginRecord
    picks: dict[PickRecord]
    amplitudes: dict[AmplitudeRecord]

    @staticmethod
    def _warning_SSD_line_order(next_line):
        """
        Print a warning that SSD file has CHANNEL line not followed by
        ARRIVAL or AMPLITUDE block.
        """
        print('WARNING: Check SSD file validity.')
        print('No ARRIVAL or AMPLITUDE block after CHANNEL line!')

    @classmethod
    def _parse(cls, content: list[str]):
        """
        Parse a list of strings to g instance.
        """
        # Empty (for now) definitions for the class default contructor
        name = None; origin = None; picks = []; amplitudes = []
        # Support/running variables
        channel_line = None     # Current channel (block header)
        arrs = {}               # Dict of ARRIVAL blocks -> picks
        amps = {}               # Dict of AMPLITUDE blocks -> amplitudes
        equake = []             # List of EARTHQUAKE block -> origin
        # Key part - tossing whole content line by line to blocks
        while content:
            if content[0].startswith('#SSDREPORT') or \
                            content[0].startswith('#FILENAME'):
                words = _cleanup(content[0].replace('=',' ')).split()
                name = words[-1] if len(words) >= 2 else 'Unknown'
                content.pop(0)
            elif content[0].startswith('#EARTHQUAKE'):
                equake.append(content[0])
                content.pop(0)
            elif content[0].startswith('#ARRIV'):
                if not channel_line in arrs.keys():
                    arrs[channel_line] = []
                arrs[channel_line].append(content[0])
                content.pop(0)
            elif content[0].startswith('#AMPLITUDE'):
                if not channel_line in amps.keys():
                    amps[channel_line] = []
                amps[channel_line].append(content[0])
                content.pop(0)
            elif content[0].startswith('#CHANNEL'):
                channel_line = content[0]
                next_line = content[1]
                if next_line.startswith('#ARRIV'):
                    arrs[channel_line] = []
                elif next_line.startswith('#AMPLITUDE'):
                    amps[channel_line] = []
                else:
                    cls._warning_SSD_line_order(next_line)
                content.pop(0)
            else:
                print(f'Unknown line to parse: {content[0]}')
                content.pop(0)
        # Delegating part - creating new instances (of class attibutes)
        origin = OriginRecord._parse(equake)
        picks = {ChannelInfo._parse(chan): PickRecord._parse(arr)
                    for chan, arr in arrs.items()}
        amplitudes = {ChannelInfo._parse(chan): AmplitudeRecord._parse(amp)
                    for chan, amp in amps.items()}
        # Final part - uniting newly made attributes into an instance
        if not origin or not picks:
            return None
        return cls(name, origin, picks, amplitudes)

    @classmethod
    def read(cls, path: Path):
        """
        Returns new instance read from SSD file (DIMAS-specific format).
        """
        with open(path) as f:
            try:
                content = f.readlines()
            except UnicodeDecodeError:
                print(f'{path} is not a text file!')
                return None
            # After content is read simply call _parse_ssd to proceed
            return cls._parse(content)

    def to_LOTOS(self, stations: list) -> str:
        """
        Formats event record info to text block of LOTOS `rays.dat`.
        """
        source = f'{self.origin.lon}\t{self.origin.lat}\t{self.origin.lat}'
        header_line = f'{source}\t{len(self.picks)}\n'
        lines = []
        for chan, pick in self.picks.items():
            if pick.phase == 'P' or pick.phase == 'p':
                phase = '1'
            elif pick.phase == 'S' or pick.phase == 's':
                phase = '2'
            else:
                phase = '3'
            lines.append(f'\t{phase}\t{stations.index(chan.sta)}\t{pick.time}')               
        return header_line + '\n'.join(lines) 


@dataclass
class WaveArrival:
    """
    All info that can be used to describe a single seismic ray.
    
    Attributes/content:
        source - 
        receiver -
        phase -
        time_sec -
        time_picked - 
        #time_modeled -
    """
    source: str
    receiver: str
    phase: str
    time_sec: float
    time_picked: UTCDateTime

############################### CORE FUNCTIONS ################################
def read_catalog(pattern: Path) -> dict[EventRecord]:
    """
    Read and parse SSD report(s), return dictionary of records - catalog.
    """
    catalog = {}
    for path in get_paths(pattern):
        event = EventRecord.read(path)
        if event:
            catalog[event.name] = event
    return catalog


def get_arrivals(catalog: dict[EventRecord], receiver_code: str) -> list:
    """
    Get list of arrivals from catalog for specific station/receiver code. 
    """
    arrivals = []
    for src, event in catalog.items():
        channels_needed = [chan for chan in event.picks.keys()
                                if f'{chan.net}.{chan.sta}' == receiver_code]
        for channel in channels_needed:
            utc = event.picks[channel].time
            t = utc - event.origin.time
            phase = event.picks[channel].phase
            arrivals.append(WaveArrival(src, receiver_code, phase, t, utc))
    return arrivals#, receiver


def extract_LOTOS_inidata(catalog: dict[EventRecord]):
    """
    Extract and reformat arrivals for the LOTOS algorithm inidata folder.
    """
    channels_all = []
    for event in catalog.values():
        channels = list(event.picks.keys())
        channels_all.extend(channels)
    print(f'Checking catalog - {len(channels_all)} arrivals in total.')
    sts = {f'{chan.net}.{chan.sta}' for chan in channels_all}
    arrs = [get_arrivals(catalog, station) for station in sts]
    info = [(i, station, len(arrivals)) 
            for i, station, arrivals in zip(range(len(sts)), sts, arrs)]
    info = sorted(info, key=lambda x:x[2])
    # Formating inidata/stat_ft.dat file 
    print(f'\nForming |stat_ft.dat| file content as long string:')
    stat_ft = ''
    rule = {}
    for i, line in zip(range(1, len(info) + 1), info):
        stat_ft += f'LON\tLAT\tDEPTH\t{line[1]}\n'
        rule[line[1]] = i
        print(f'{line[2]}\t arrivals for \t|{line[1]}|\t - indexed |{i}|')
    # Formating inidata/rays.dat file 
    print(f'\nForming |stat_ft.dat| file content as long string')
    rays = ''
    for record, event in catalog.items():
        n = len(event.picks)
        avg = 0
        source_line = f'{event.origin.lon}\t{event.origin.lat}\t'
        source_line += f'{event.origin.depth}\t{n}\n'        
        #print(source_line)
        block = ''
        for channel, pick in event.picks.items():
            phase = '1' if pick.phase == 'P' else '2'   # ! quick and dirty !
            station_index = rule[f'{channel.net}.{channel.sta}']
            arrival = pick.time - event.origin.time
            avg += arrival
            block += f'\t{phase}\t{station_index}\t{arrival}\n'
        rays += source_line + block
        print(f'Event {record}: {n} picks, average arrival time: {avg / n:.4f}')
    return stat_ft, rays


############################## SCRIPT BEHAIVIOR ###############################
# Python idiom to check if the module is not imported (script behaivior)
if __name__ == '__main__':
    record = EventRecord.read(SSD_EXAMPLE_PATH)
    print(record)
    old_record = EventRecord.read(SSD_OLD_EXAMPLE_PATH)
    print(old_record)
    exit(0)
###############################################################################
