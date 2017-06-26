# -*- coding: utf-8 -*-
"""
Created on Thu Jun 01 11:26:48 2017

@author: reeserd2
"""

print "Entering JSS Analysis mode."

####All of the following is now done by my module simpleRead
#import csv
#
#with open('C:/Users/reeserd2/Desktop/JSS Analysis/data/JSS_fixed_CIM_CapIQ_20170525_fixed.csv', mode = 'r') as f:
#    readIn = csv.reader(f, delimiter = ',', skipinitialspace=True)
#
#    lineData = list()
#
#    cols = next(readIn)
#    print(cols)
#
#    for col in cols:
#    # Create a list in lineData for each column of data.
#        lineData.append(list())
#
#
#    for line in readIn:
#        for i in xrange(0, len(lineData)):
#            # Copy the data from the line into the correct columns.
#            lineData[i].append(line[i])
#
#    data = dict()
#
#    for i in xrange(0, len(cols)):
## Create each key in the dict with the data in its column.
#        data[cols[i]] = lineData[i]
#
#print(data)
#   
#f.close()

import simpleRead as sr###A crude module I personally wrote for reading in raw csv files. 
import numpy as np
import math as m
import matplotlib
import pylab as pl
import pandas


print matplotlib.__version__


"""
I am learning some work from 'Python for Data Analysis'.  
"""


####One way of reading in the data. A bit choppy, but you can get at it at a more "raw" level. 
#raw_data = sr.simpleReadCSV('C:/Users/reeserd2/Desktop/JSS Analysis/data/JSS_fixed_CIM_CapIQ_20170525_fixed.csv')

#my_data.keys()

#print my_data["ISWON"]

def make_float(s):
    s = s.strip()
    return float(s) if s else 'NA'

#raw_data["RoAPer"] = map(make_float, raw_data["RoAPer"])

#print my_data["RoAPer"]
    
###dataf = pd.DataFrame(raw_data, columns = [])

####pandas.read_csv() most closely resembles R's ability to intelligently read in a csv file. 
JSS_Data = pandas.read_csv('../JSS Analysis/data/JSS_fixed_CIM_CapIQ_20170525_fixed.csv')

print JSS_Data.keys()

JSS_Data["Rev"]

JSS_Data.count()

JSS_Data.sum()##Who knows what this does for strings.....But I believe it ignores NaN. It also seems to ignore string coulmns. 
      

#%%

import json

path = "C:/Users/reeserd2/Documents/bitlyData.txt"

bitly =[json.loads(line) for line in open(path)] ###Note the list constructor using a for loop. 

#print bitly[2]["tz"]

time_zones = [record['tz'] for record in bitly if "tz" in record] ###Again, the list constructor using a for loop. 
 
time_zones[:15]###The index is not inclusive remember. 
  
from collections import defaultdict
          
def get_counts(seq):
    counts = defaultdict(int)###Initializes all values to 0. 
    for rec in seq:
        counts[rec] += 1
    return counts          
          
tzCounts = get_counts(time_zones)

tzCounts['America/New_York']

#%%%

###We can find the top 5 most common time zones, but it requires us "flipping" the dictionary so to speak. 


def top_counts(count_dict, n = 5):
    value_key = [(count,tz) for tz,count in count_dict.items()]
    value_key.sort(reverse = True)
    #value_key.sort() ###sorts based on the FIRST value in the tuple. 
    ###The value_key list now remains sorted. No need to cache. To not modify the list, use sorted(LIST)
    return value_key[-n:]
top_counts(tzCounts, n = 10)

###This same thing can be done using some tools that are importable from the collections module. 

from collections import Counter

tzCounts_simple = Counter(time_zones) ###A single function to cover the last 20 lines or so. 

tzCounts_simple.most_common(10) #Also presents these in a top to bottom format. 


#%%
###All of the time zone stuff can be done by using DataFrame in pandas. 
import pandas as pd

df = pd.DataFrame(bitly)

df['tz'][:10]

##print df["tz"].value_counts()[:10]


clean_tz = df['tz'].fillna('Missing')
clean_tz[clean_tz == ''] = 'Unknown'
tz_counts = clean_tz.value_counts()
tz_counts[:10]



#%%

import matplotlib.pyplot as plt
plt.figure(figsize=(10, 4))
tz_counts[:10].plot(kind='barh', rot=0)


df['a'][1]
df['a'][50]
df['a'][51]


results = pd.Series([x.split()[0] for x in df.a.dropna()])
results[:5]

#%%


#%%
#%%
#%%
#%%
#%%
#%%






