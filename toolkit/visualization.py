#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# abramsci/seismology/toolkit/visualization.py
"""
Classes and functions for custom plotting of a seismic event.

**Copyright:** 2023, Sergei Abramenkov (https://github.com/abramsci)

**License:** [MIT](../LICENSE)

**Core dependencies:**
* Python 3.5+ (standard lib packages)
* matplotlib (tested for 3.7.1)
* obspy (tested for 1.4.0)
* numpy (tested for 1.24.4)
"""
################################## IMPORTS ####################################
# Python standard library imports
import copy
from pathlib import Path

# Necessary packages (not in standard lib)
from matplotlib import mlab
from matplotlib import pyplot
import obspy
import numpy

# Local application/library specific imports
from misc import is_power_of_two, get_code, nearest_power_of_two
from misc import TOOLKIT_DIR
import ssd_report


############################## GLOBAL CONSTANTS ###############################
# Paths to directories/files - may/should evolve to command line arguments
DATACHUNK_EXAMPLE_PATH = TOOLKIT_DIR.joinpath('data', '_example.mseed')
RESULTS_DIR = Path('./results/')
RESULTS_DIR.mkdir(exist_ok=True)

# Processing parameters
NFFT: int = nearest_power_of_two(64)
OVERLAP = 0.8
WIN_LEN_SEC = 2.0                   # Phase spectrum window in seconds
TAPER_PERCENT = float(0.05)         # 0.05 (5%) means 2.5% from each end
DETREND_ORDER = int(3)              # Polynomial order for detrending

# Plotting parameters
IS_LOG_SCALE = False
PRECISION = 6                       # Digits for float values combined
COLOURS = ['red', 'green', 'blue', 'orange', 'purple']
THIN_LINE = {'linewidth': 0.08}
NORMAL_LINE = {'linewidth': 0.3, 'color': 'black'}
THICK_LINE = {'linewidth': 0.8}
LIGHT_BLOCK = {'alpha': 0.3, 'linewidth': 0.0}
NORMAL_BLOCK = {'alpha': 0.5, 'linewidth': 0.0}
DARK_BLOCK = {'alpha': 0.7, 'linewidth': 0.0}
IMAGE_BLOCK = {'cmap': 'hot_r', 'zorder': None, 'interpolation': 'nearest',
               'alpha': 0.8, 'aspect': 'auto'}
FIG_LEGEND_BLOCK = {'fontsize': 'xx-small'}
AX_LEGEND_BLOCK = {'fontsize': 'x-small'}

pyplot.style.use('seaborn-v0_8-whitegrid')
#pyplot.style.use('dark_background')



############################# AUXILIARY FUNCTIONS #############################
def calc_spectrogram(data: numpy.ndarray, delta: float, lap=0.0):
    """
    Calculates spectrogram of an obspy seismic trace
    """
    nlap = int(NFFT * float(lap))
    data = data - data.mean()
    spcgrm, freq, time = mlab.specgram(data, Fs=1/delta, NFFT=NFFT,
                                       noverlap=nlap)
    spcgrm = numpy.sqrt(spcgrm[1:, :])
    freq = freq[1:]
    return numpy.flipud(spcgrm), freq, time

def calc_spectrum(window: numpy.ndarray, delta: float):
    """
    Calculate spectrum for selected piece of data.

    len(data) must be a power of 2.

    Returns tuple of the same size numpy arrays (frequencies, spectrum).
    """
    if not is_power_of_two(len(window)):
        print('WARNING: window size to calc spectrum should be power of 2')
    window = window - window.mean()
    spectr, freq = mlab.magnitude_spectrum(window)
    return spectr * len(window) / delta, freq / delta / 2


################################### CLASSES ###################################
# Core object-oriented concept - order of definition matters!
# Importing in other modules will look like so:
# from template import Foo


############################### CORE FUNCTIONS ################################
def plot_picking(chunk: obspy.Stream, event=None, spectrogram=False):
    """
    Plot waveforms and spectra with travel time picks of event.

    There are few requirements for a `datachunk` so it would look good:
        (1) len(datachunk) <= len(COLOURS) - too many traces look messy
        (2) datachunk has to be synchronized and (3) chunk-sized
        This means that all traces inside must have same starttime
        and have exactly same npts which should be equal to power of 2
    """
    # So first of all - check that provided datachunk meets requirements
    if not chunk:
        print('Empty stream - no plotting.')
        return
    starts = [trace.stats.starttime for trace in chunk]
    t0 = starts[0] if starts.count(starts[0]) == len(starts) else None
    if not t0:
        print('No synchronized stream - no plotting.')
        return
    sizes_ok = [is_power_of_two(trace.stats.npts) for trace in chunk]
    if False in sizes_ok:
        print('One (or more) of the traces in stream is not chunk-sized')
        return
    if event:
        label = f'Origin: {event.origin.time}'
        event = copy.deepcopy(event)
        if spectrogram:
            event.origin.time = event.origin.time - t0
            for pick in event.picks.values():
                pick.time = pick.time - t0
                arrival = pick.time + event.origin.time
                pick.label = f'{pick.phase} travel time: {arrival:.4f}'
        else:
            for pick in event.picks.values():
                pick.label = f'{pick.phase}: {pick.time.time}'
    print(chunk)
    print('Plotting...')

    # Now initializing some needed variables
    codes = [get_code(trace.stats) for trace in chunk]
    powers = {trace.stats.npts: max(calc_spectrum(trace.data,
                                                  trace.stats.delta)[0])
              for trace in chunk}
    print(powers)
    npts = max([p for p in powers])
    amp_max = max([powers[p] / p for p in powers])
    print(npts, amp_max)
    axis_tags = [[code, code, 'spectr-freq'] for code in codes]
    fig, axs = pyplot.subplot_mosaic(axis_tags, figsize=(10, 6),
                                     layout='tight')

    # For each trace - plot its data in both time and frequency domain
    for ch, trace in zip(codes, chunk):
        colour = COLOURS[int(codes.index(ch) % len(COLOURS))]
        delta = trace.stats.delta
        data = trace.data
        ymax = max(data)
        ymin = min(data)
        if spectrogram:
            utc = trace.times()
        else:
            utc = [(t0 + t).datetime for t in trace.times()]
        ax = axs[ch].twinx()
        ax.set_ylabel(f'{trace.stats.station}\n{trace.stats.channel}',
                      color=colour, rotation=0, loc='top', labelpad=-25)
        ax.spines['top'].set_linewidth(0.0)
        ax.spines['bottom'].set_linewidth(0.0)
        ax.spines['left'].set_linewidth(0.0)
        ax.spines['right'].set_linewidth(0.0)
        ax.tick_params(axis='x', labelsize='small')
        ax.tick_params(axis='y', labelsize='x-small')
        axs[ch].spines['top'].set_linewidth(0.0)
        axs[ch].spines['bottom'].set_linewidth(0.0)
        axs[ch].spines['left'].set_linewidth(0.0)
        axs[ch].spines['right'].set_linewidth(0.0)
        axs[ch].grid(visible=False)
        ax.grid(visible=False)
        if spectrogram:
            spcgrm, fs, ts = calc_spectrogram(data, trace.stats.delta,
                                              lap=OVERLAP)
            dt = (ts[1] - ts[0]) / 2.0
            df = (fs[1] - fs[0]) / 2.0
            ex = (ts[0] - dt, ts[-1] + dt, fs[0] - df, fs[-1] + df)
            vmax = numpy.sqrt(amp_max * trace.stats.npts / npts)
            axs[ch].imshow(spcgrm, extent=ex, vmax=vmax, **IMAGE_BLOCK)
            axs[ch].set_ylim(fs[0]-df, fs[-1] + df)
            axs[ch].set_ylabel('Frequency (Hz)', fontsize='x-small')
            axs[ch].set_xlabel('Time (s)')
            if IS_LOG_SCALE:
                axs[ch].set_yscale('log')
        else:
            axs[ch].set_xlabel('Time (UTC)')
            axs[ch].set_xlim(utc[0], utc[-1])
            axs[ch].set_yticks([])
        h = []
        lbls = ['raw data']
        h += ax.plot(utc, data, color=colour, **THIN_LINE)

        # Lastly (if event provided) - more plotting
        if event:
            for channel, pick in event.picks.items():
                net_pick, sta_pick, *_ = channel.get_code().split('.')
                net, sta, *_ = ch.split('.')
                arrival = pick.time if spectrogram else pick.time - t0
                if sta == sta_pick:
                    if pick.phase == 'P':
                        ax.vlines(arrival, ymin=ymin, ymax=ymax,
                                            linestyles='dashed', **NORMAL_LINE)
                        lbls.append(pick.label)
                        ax.annotate(f'P', (arrival, ymax))
                    elif pick.phase == 'S':
                        ax.vlines(arrival, ymin=ymin, ymax=ymax,
                                         linestyles='dotted', **NORMAL_LINE)
                        lbls.append(pick.label)
                        ax.annotate(f'S', (arrival, ymax))
                    else:
                        ax.vlines(arrival, ymin=ymin, ymax=ymax,
                                        linestyles='dashdot', **NORMAL_LINE)
        ax.legend(lbls, loc='lower right', **AX_LEGEND_BLOCK)

         # Next - plotting right side - spectrum in frequency domain
        #axs['spectr-freq'].magnitude_spectrum(data, color=colour, **THICK_LINE)
        spectr, freq = calc_spectrum(data, delta)
        #axs['spectr-freq'].plot(spectr, freq, color='grey', **THIN_LINE)
        axs['spectr-freq'].fill_between(spectr, freq, color='yellow', **LIGHT_BLOCK)
        # Plotting spectrum in windows (P-wave, S-wave, noise)
        win_size = nearest_power_of_two(WIN_LEN_SEC / delta)
        win_sec = win_size * delta
        print(win_size, win_sec)

        # Lastly (if event provided) - plotting highlighted blocks
        if event:
            base_color = 'grey' if not spectrogram else 'white'
            h_origin = ax.vlines(event.origin.time, ymin=ymin, ymax=ymax,
                            linestyles='solid', **NORMAL_LINE)
            for channel, pick in event.picks.items():
                net_pick, sta_pick, *_ = channel.get_code().split('.')
                net, sta, *_ = ch.split('.')
                arrival = pick.time if spectrogram else pick.time - t0
                if sta == sta_pick:
                    if pick.phase == 'P':
                        noise_r = p_index = int(arrival / delta)
                        noise_l = p_index - win_size
                        noise_l if noise_l > 0 else 0
                        noise_r if noise_l > 0 else win_size
                        noise = data[noise_l:noise_r]
                        print(delta)
                        n_spectr, n_freq = calc_spectrum(noise, delta)
                        n_spectr = n_spectr * win_size / npts
                        axs['spectr-freq'].plot(n_spectr, n_freq,
                                                color=colour, **THICK_LINE)
                        h_noise = ax.axvspan(arrival - win_sec, arrival,
                                             color=base_color, **LIGHT_BLOCK)
                        lbl_noise = f'  Noise: {win_sec} sec ({win_size})'
                        p_end = p_index + win_size
                        p_wave = data[p_index:p_end]
                        p_spectr, p_freq = calc_spectrum(p_wave, delta)
                        p_spectr = p_spectr * win_size / npts
                        axs['spectr-freq'].plot(p_spectr, p_freq,
                                                linestyle='dashed',
                                                color=colour, **THICK_LINE)
                        h_pwave = ax.axvspan(arrival, arrival + win_sec,
                                             color=base_color, **NORMAL_BLOCK)
                        lbl_pwave = f'  P-wave: {win_sec} sec ({win_size})'
                    elif pick.phase == 'S':
                        s_index = int(arrival / delta)
                        s_end = s_index + win_size
                        s_wave = data[s_index:s_end]
                        s_spectr, s_freq = calc_spectrum(s_wave, delta)
                        s_spectr = s_spectr * win_size / npts
                        axs['spectr-freq'].plot(s_spectr, s_freq,
                                                linestyle='dotted',
                                                color=colour, **THICK_LINE)
                        h_swave = ax.axvspan(arrival, arrival + win_sec,
                                             color=base_color, **DARK_BLOCK)
                        lbl_swave = f'  S-wave: {win_sec} sec ({win_size})'
                    else:
                        ax.axvspan(arrival, arrival + win_sec,
                                   color=base_color, **DARK_BLOCK)
    if IS_LOG_SCALE:
            axs['spectr-freq'].set_yscale('log')
    axs['spectr-freq'].set_xlim(0, amp_max * WIN_LEN_SEC / delta)
    axs['spectr-freq'].set_ylim(freq[2], freq[-2])
    axs['spectr-freq'].set_ylabel('Frequency (Hz)')
    #axs['spectr-freq'].set_ylim(0, amp_max * ratio)
    axs['spectr-freq'].set_xlabel('Magnitude (energy)')
    axs['spectr-freq'].yaxis.tick_right()
    if event:
        fig.legend((h_origin,),
                   (label,),
                    loc='upper left', **FIG_LEGEND_BLOCK)
        fig.legend((h_origin, h_noise, h_pwave, h_swave),
                   ('Calculation windows:', lbl_noise, lbl_pwave, lbl_swave),
                    loc='upper right', **FIG_LEGEND_BLOCK)
    fig.autofmt_xdate()
    fig.suptitle(f'{trace.stats.starttime}    {trace.stats.endtime}')
    temp = RESULTS_DIR.joinpath('temp.svg')
    fig.savefig(temp, dpi=300, bbox_inches='tight')
    print('\tDone.')
    # filtered_stream = raw_stream.copy()
    # filtered_stream.filter('bandpass', freqmin=1.0, freqmax=6.0)
    #filename = RESULTS_DIR.joinpath(f'{event_id}.{station}.png')
    #plt.savefig(filename, dpi=180, bbox_inches='tight')
    return


############################## SCRIPT BEHAIVIOR ###############################
# Python idiom to check if the module is not imported (i.e. script behaivior)
# Also a good place to call testing routines for the module
if __name__ == '__main__':
    event_record = ssd_report.EventRecord.read(ssd_report.SSD_EXAMPLE_PATH)
    raw_stream = obspy.read(DATACHUNK_EXAMPLE_PATH)
    #print(raw_stream)
    #data_chunk = raw_stream.select(station='SHZ').detrend('linear')
    data_chunk = raw_stream.select(component='Z').detrend('linear')[:5]
    #print(data_chunk)
    plot_picking(data_chunk, event_record, spectrogram=True)
    #plot_picking(data_chunk, event_record)
    #plot_picking(data_chunk)
    #plot_picking(data_chunk, spectrogram=True)
    # Return error code 0 back to shell if everything works ok.
    exit(0)
###############################################################################