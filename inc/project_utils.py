import os
import mne
import numpy as np

from enum import Enum


class Subject(Enum):
    Keaton = 1
    Alyse = 2
    Morty = 3
    Jay = 4
    Richard = 5

class Sensor(Enum):
    AF3 = 0
    F7 = 1
    F3 = 2
    FC5 = 3
    T7 = 4
    P7 = 5
    O1 = 6
    O2 = 7
    P8 = 8
    T8 = 9
    FC6 = 10
    F4 = 11
    F8 = 12
    AF4 = 13

"""
	return paths to the files starting with the 'head' 
	string in the data directory

	@param head: the string search criteria
		equivelent to regex ^"head".*
	@param d: path to the directory where the data
		is stored on the local system

	@return: a list of absolute filepaths to the files 
		returned by the search 
	
"""
def get_files_starting_with(head, d):
    filenames = []

    for filename in os.listdir(d):
        if filename[0:len(head)] == head:
            path = os.path.join(d, filename)
            filenames.append(path)

    return filenames

"""
	when a raw object is read in from the Emotiv generated using
	the MNE library, this function formats the raw object for 
	MNE analysis

	@param raw: the MNE raw object being prepared
"""
def prepare_raw_for_mne(raw):
    # drop unnecessary channels
    extra_ch = raw.ch_names[0:2] + raw.ch_names[16:40]
    raw.drop_channels(extra_ch)
    
    # manually add stim channel
    stim_data = np.zeros((1, len(raw.times)))
    info = mne.create_info(['STI'], raw.info['sfreq'], ['stim'])
    stim_raw = mne.io.RawArray(stim_data, info)
    raw.add_channels([stim_raw], force_update_info=True)


"""
    converts a raw MNE object that has been created using an Emotiv Pro generated EDF 
    file into a set of the average power across the specified frequencies
    
    @param raw: MNE raw object
    @param l_freq: frequency lower bound (int) 
    @param h_freq: frequency upper bound (int)
    
    @return: an MNE TRAverage with the average frequency from l_freq to h_freq
"""
def get_power(raw, l_freq, h_freq):
    # define montage 
    montage = mne.channels.read_montage('standard_1020')
    raw.set_montage(montage)
    
    # add events 
    events = np.array([[0, 0, 1]]) 
    raw.add_events(events)
    
    # add picks
    picks = mne.pick_types(raw.info, eeg=True, eog=False, meg=False, stim=False, 
            exclude='bads')
    
    # add epochs
    event_id, tmin, tmax = 1, 0, 39
    baseline = (None, 0)
    epochs = mne.Epochs(raw, events, event_id, tmin, tmax,
        picks=picks,
        baseline=baseline,
        preload=True)
    
    # extract the average power across the specified range of frequencies
    freqs = np.logspace(*np.log10([l_freq, h_freq]), num=1)
    n_cycles = freqs / 2
    power, itc = mne.time_frequency.tfr_morlet(epochs, freqs=freqs, 
                                                n_cycles=n_cycles,
                                                use_fft=True,
                                                return_itc=True,
                                                decim=3, 
                                                n_jobs=1)
    
    return power

"""
	returns the lower and upper time bound of a power data array

	@param power:  an MNE AverageTFR object
	@param sensor: sensor object (Sensor.<name of sensor>
	@param tmin:   the minimum time desired
	@param tmax:   the maximum time desired
                   if tmax out of bounds, maximum data selected

	@return:       An array of time values and an array of power
                   values
"""
class TimeException(Exception):
	pass

def get_time_bounds_from_power(power, tmin, tmax):
    l = 0
    while l < len(power.times) and power.times[l] < tmin:
        l += 1	

    h = l + 1
    while h < len(power.times) and power.times[h] < tmax:
	    h += 1

    return l, h 


















		

	
	

