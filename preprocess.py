"""
script for preprocessing all edf files 
stored in the data folder

outputs cleaned csv files in the processed 
folder

saves frequency graphs in graphs folder
after preprocessing has taken place
"""

import os
import sys
import mne
import scipy
import datetime

import numpy              as np
import pandas             as pd
import matplotlib.pyplot  as plt

# global variables
cwd           = "."
slash         = "/"
data_dir      = "data"
graph_dir     = "graphs"
processed_dir = "processed"

"""
set global variable configurations
"""
def configure():
	global cwd
	global slash 
	global data_dir
	global graph_dir
	global processed_dir

	# if windows use \ for slash
	if os.name == "nt":
		slash = "\\"

	# expand current working directory 
	cwd = os.path.abspath(cwd)

	# expand resource and output directories
	data_dir      = os.path.join(cwd, data_dir)
	graph_dir     = os.path.join(cwd, graph_dir)
	processed_dir = os.path.join(cwd, processed_dir)

	# if necessary directories don't exist, make them
	if not os.path.isdir(data_dir):
		os.mkdir(data_dir)
	if not os.path.isdir(graph_dir):
		os.mkdir(graph_dir)
	if not os.path.isdir(processed_dir):
		os.mkdir(processed_dir)

def get_filepaths():
	global data_dir
	
	filepaths = os.listdir(data_dir)
	
	for i in range(len(filepaths)):
		filepaths[i] = os.path.join(data_dir, filepaths[i])

	return filepaths
	
# remove unnecessary channels
def trim_channels(raw):
	extra_ch = raw.ch_names[0:2] + raw.ch_names[16:40]
	raw.drop_channels(extra_ch)

def preprocess(raw):
	l_freq = 8
	h_freq = 30

	raw.filter(l_freq=l_freq, h_freq=h_freq)

def get_csvpath(edf_path):
	global slash

	path = ""	

	# get edf filename
	path = edf_path.split(slash)[-1]

	# remove time stamp and file extension
	path = path.split(".")[0][:-5]

	# get current time 
	timestamp = datetime.datetime.now()	
	timestamp = str(timestamp.strftime("%Y_%m_%d__%H:%M"))

	# append timestamp 
	path = path + "-" + timestamp + ".csv"

	return path
	
def save_csv(raw, outfile):
	data = {}	

	for i in range(len(raw.ch_names)):
		data[raw.ch_names[i]] = raw.get_data()[i]
	
	data["Time"] = raw.times

	df = pd.DataFrame(data=data)

	outpath = os.path.join(processed_dir, outfile)
	
	df.to_csv(path_or_buf=outpath)

if __name__ == "__main__":
	configure()
	filepaths = get_filepaths()

	#fig = raw.plot_psd()
	
	for fp in filepaths:
		raw = mne.io.read_raw_edf(fp, preload=True)
		trim_channels(raw)
		preprocess(raw)
	
		outfile = get_csvpath(fp)
		save_csv(raw, outfile)

	print("Total Preprocessed Files: {}".format(len(filepaths)))
