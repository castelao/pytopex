#!/usr/bin/env python
# -*- coding: Latin-1 -*-
# vim: tabstop=4 shiftwidth=4 expandtab

"""
"""

__author__ = ["Guilherme Castelao <guilherme@castelao.net>", "Roberto De Almeida <rob@pydap.org>"]

import os
import itertools
from datetime import datetime, timedelta
from UserDict import IterableUserDict
try:
    import cPickle as pickle
except ImportError:
    import pickle

from numpy import ma
import dap.client

def topex_time_table(dt_days,dt_seconds,dt_microseconds,base_date=None):
    """
    """
    if base_date is None:
        base_date=datetime(year=1950,month=01,day=01,hour=0,minute=0,second=0)
    t=[]
    for d, s, ms in itertools.izip(dt_days.compressed(),dt_seconds.compressed(),dt_microseconds.compressed()):
	    dt=timedelta(days=int(d),seconds=int(s),microseconds=int(ms))
            t.append(base_date+dt)
    t=ma.masked_equal(t,-1)
    return t

def topex_track_table(ndata,tracks,cycles):
    """
    """
    track_list=[]
    cycle_list=[]
    for track, n, cycle in itertools.izip(tracks.compressed(),ndata.compressed(),cycles.compressed()):
        for i in range(n):
            track_list.append(track)
            cycle_list.append(cycle)
    track_list=ma.masked_equal(track_list,-1)
    cycle_list=ma.masked_equal(cycle_list,-1)
    return cycle_list,track_list

def read_file(filename,vars=['CorSSH','MSS','Bathy']):
    """
    """
    import dap.client
    try:
        dataset = dap.client.open(filename)
    except:
        return
    cycles=ma.masked_equal(dataset['Cycles'][:,0],dataset['Cycles']._FillValue)
    cycles.set_fill_value(dataset['Cycles']._FillValue)
    tracks=ma.masked_equal(dataset['Tracks'][:],dataset['Tracks']._FillValue)
    tracks.set_fill_value(dataset['Tracks']._FillValue)
    ndata=ma.masked_equal(dataset['NbPoints'][:],dataset['NbPoints']._FillValue)
    ndata.set_fill_value(dataset['NbPoints']._FillValue)
    [cycle_list,track_list]=topex_track_table(ndata,tracks,cycles)
    # Time related
    TimeDay=ma.masked_equal(dataset['TimeDay'][:,0],dataset['TimeDay']._FillValue)
    TimeDay.set_fill_value(dataset['TimeDay']._FillValue)
    TimeSec=ma.masked_equal(dataset['TimeSec'][:,0],dataset['TimeSec']._FillValue)
    TimeSec.set_fill_value(dataset['TimeSec']._FillValue)
    TimeMicroSec=ma.masked_equal(dataset['TimeMicroSec'][:,0],dataset['TimeMicroSec']._FillValue)
    TimeMicroSec.set_fill_value(dataset['TimeMicroSec']._FillValue)
    # Improve and include the check of the BeginDates
    time_list=topex_time_table(TimeDay,TimeSec,TimeMicroSec)
    # Position related
    lat=ma.masked_equal(dataset['Latitudes'][:],dataset['Latitudes']._FillValue)*dataset['Latitudes'].scale_factor
    lat.set_fill_value(dataset['Latitudes']._FillValue)
    lon=ma.masked_equal(dataset['Longitudes'][:],dataset['Longitudes']._FillValue)*dataset['Longitudes'].scale_factor
    lon.set_fill_value(dataset['Longitudes']._FillValue)
    #
    #data={'Cycles':cycles,'Tracks':tracks,'NbPoints':ndata,'Tracks Table':tracks_list,'TimeDay':TimeDay,'TimeSec':TimeSec,'TimeMicroSec':TimeMicroSec,'Time Table':time_list,'CorSSH':CorSSH,'Latitudes':lat,'Longitudes':lon,'MSS':MSS}
    #data={'Cycles':cycle_list,'Tracks':track_list,'TimeDay':TimeDay,'TimeSec':TimeSec,'TimeMicroSec':TimeMicroSec,'Datetime':time_list,'CorSSH':CorSSH,'Latitudes':lat,'Longitudes':lon,'MSS':MSS}
    data={'Cycles':cycle_list,'Tracks':track_list,'TimeDay':TimeDay,'TimeSec':TimeSec,'TimeMicroSec':TimeMicroSec,'Datetime':time_list,'Latitude':lat,'Longitude':lon}
    #
    for var in vars:
        tmp=ma.masked_equal(dataset[var][:,0],dataset[var]._FillValue)*dataset[var].scale_factor
        tmp.set_fill_value(dataset[var]._FillValue)
	data[var]=tmp
    return data

def filter(data,var,limits):
    """

    ATENTION, change it to cond instead of limits, so give complete freedom for
      the conditions, like choose >= instead of > or only a lower limit.

      In work
    """
    index=(data[var].data>limits[0])&(data[var].data<limits[1])
    data_out={}
    for key in data:
        data_out[key]=data[key][index]
    return data_out

def load_TP_dataset(files,filtercond=None):
    """
    """
    data_out={}
    for file in files:
        try:
	    data = read_file(file)
	    if filtercond is not None:
	        for var in filtercond:
		  data=filter(data,var,filtercond[var])
            #
            for c in set(data['Cycles']):
	        print "Doing cycle: %s" % c
                if c not in data_out:
	            data_out[c]={}
                index_c = (data['Cycles'].data==c)
                for tck in set(data['Tracks'][index_c]):
		    #print "Doing track: %s" % tck
	            #if tck not in data_out[c].keys():
	            #    data_out[c][tck]={}
                    index_tck = index_c & (data['Tracks'].data==tck)
		    # Change it for a generic all keys
                    data_out[c][tck]={'Datetime':data['Datetime'][index_tck],'Latitude':data['Latitude'][index_tck],'Longitude':data['Longitude'][index_tck],'CorSSH':data['CorSSH'][index_tck],'MSS':data['MSS'][index_tck],'Bathy':data['Bathy'][index_tck]}
        except:
            pass
    #
    return data_out

def load_from_path(path,filtercond=None):
    """

    Improve it to accept a URL too, in the case of a path for a DODS server.
    Maybe a regex too to restrict to nc files? Maybe to pattern of names.
    """
    import os
    filenames=os.listdir(path)
    filenames.sort()
    files=[os.path.join(path,filename) for filename in filenames]
    data=load_TP_dataset(files,filtercond)
    return data

def save_dataset(data,filename):
    """
    """
    import pickle
    output = open(filename,'wb')
    pickle.dump(data, output)
    output.close()
    return

def load_dataset(filename):
    """
    """
    import pickle
    pkl_file = open(filename, 'rb')
    data = pickle.load(pkl_file)
    pkl_file.close()
    return data

def join_cycles(data):
    """Join all cycles, so that from data[c][t][vars] return data[t][vars] with all cycles
    """
    import numpy
    vars=data[data.keys()[0]][data[data.keys()[0]].keys()[0]].keys()

    data_out={}
    mask_out={}
    for t in data[data.keys()[0]]:
        data_out[t]={}
        mask_out[t]={}
        for var in vars:
            data_out[t][var]=numpy.array([])
            mask_out[t][var]=numpy.array([],dtype=bool)

    for c in data:
        for t in data[c]:
            for var in data[c][t]:
	        data_out[t][var]=numpy.concatenate((data_out[t][var],data[c][t][var].data))
                mask_out[t][var]=numpy.concatenate((mask_out[t][var],data[c][t][var].mask))

    data_masked={}
    for t in data_out:
        data_masked[t]={}
        for var in vars:
            data_masked[t][var]=ma.masked_array(data_out[t][var],mask_out[t][var])

    return data_masked


def invert_keys(data):
    """ Invert the hirerachy of the first 2 level keys in the dictionary.

        This is usable to group the data in tracks instead of cycles, like
	  data[tracks][cycles] = invert_keys(data[cycles][tracks])
    """
    data_out={}
    for c in data:
        for t in data[c]:
	    if t not in data_out:
	        data_out[t]={}
            if c not in data_out[t]:
	        data_out[t][c]={}
            data_out[t][c] = data[c][t]
    return data_out

def make_SSA(data):
    """
    """
    for c in data:
        for t in data[c]:
	    data[c][t]['SSA'] = data[c][t]['CorSSH']-data[c][t]['MSS']
    return

class TOPEX(IterableUserDict):
    """
    """
    def __init__(self,tracks=None,nbpoints=None,Cycles=None):
        """
        """
        self.data={1:{11:[1,2,3],12:[1.1,1.2,1.3],'teste':['orange','apple','pear']},2:[10,20,30],3:[100,200,300]}
        return
    def __getitem__(self, key):
        print "Chave tipo %s" % type(key).__name__
        if isinstance(key, basestring):
            if key=='join':
	        print "key is join"
	    data_out={}
	    for k in self.data:
                if k not in data_out:
                    pass
        if isinstance(key, slice):
	    print "It's a slice"
	    if (key.start==0) & (key.stop>max(self.data.keys())+1) & (key.step==None):
	      return self.data
	    print "I'm not ready for that. Only full return, like x[:]"
	    return
        if key not in self.data:
	    print "%s is not a valid key" % key
	    return
            print "key: %s" % key
            return self.data[key]
