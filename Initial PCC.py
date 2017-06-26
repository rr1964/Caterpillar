# -*- coding: utf-8 -*-
"""
Created on Tue Jun 06 16:13:02 2017

@author: reeserd2
"""

#%%
import pandas as pd
import numpy as np

import datetime


import sys
sys.path.append("C:/Users/reeserd2/Desktop/PCC Analysis/")
import pccpy ###To import pccpy. 


#from collections import Counter
#from collections import defaultdict
 
sales = pd.read_csv("C:/Users/reeserd2/Desktop/PCC Analysis/txn_full.csv")


sales['date'] = pd.to_datetime(sales.date, format='%Y%m%d')###Convert the dates over

sales['sku'] = sales.sku.str.replace('-', '')###Remove the '-' in the SKU

curr_conv = pd.read_csv('C:/Users/reeserd2/Desktop/PCC Analysis/currency_conversions_AVE.csv',
                        usecols=["name","currency","one_usd","inv_one_usd"])

curr_conv = curr_conv[pd.notnull(curr_conv.currency)]

#%%

curr_conv = curr_conv[pd.notnull(curr_conv.currency)]


sales = sales.merge(curr_conv, on='currency', how='left')####Merge sales and curr_conv based on the key 'currency'
###The key name must match ("currency" to "currency"). Left join/merge only uses keys from the left object ("sales" here)

sales['rev_adj'] = sales.rev / sales.one_usd

sales['rev'] = sales.rev_adj
sales.drop(['name', 'one_usd', 'inv_one_usd', 'rev_adj'], axis=1, inplace=True)
sales['currency'] = 'USD'

sales = sales[pd.notnull(sales.rev)] ###Remove anything that does not have a revenue value. 

sales.head()
#%%
sess = pd.read_csv('C:/Users/reeserd2/Desktop/PCC Analysis/sess_full.csv')

sess['date'] = pd.to_datetime(sess.date, format='%Y%m%d')###Reformat the dates. 

sess = sess.sort_values(by = 'hitNumber', ascending=False)
sess = sess.groupby(['date', 'fullVisitorId', 'visitId']).first().reset_index()
#fullVisitorId: The unique visitor ID (also known as client ID).
#visitId: An identifier for this session. This is part of the value usually stored as the _utmb cookie.
    # visitId is only unique to the user. For a completely unique ID, use a combination of fullVisitorId and visitId.
#%%

mdn_timeonsite = np.median(sess[pd.notnull(sess.timeonsite)].timeonsite)
sess.loc[pd.isnull(sess.timeonsite), 'timeonsite'] = mdn_timeonsite ###impute time on site when missing. 


#%%
hitNumber_outlier_mask = ((sess.hitNumber - sess.hitNumber.mean()) / sess.hitNumber.std()).abs() > 3
timeonsite_outlier_mask = ((sess.timeonsite - sess.timeonsite.mean()) / sess.timeonsite.std()).abs() > 3

nrow_start = sess.shape[0]
sess = sess[~((hitNumber_outlier_mask) & (timeonsite_outlier_mask))]

1.0*sess.shape[0] / nrow_start ####0.990828159895097
              
              
              
#%%

sess['month'] = sess.date.dt.month
sess['dow'] = sess.date.dt.dayofweek

#%%    
sales['month'] = sales.date.dt.month
sales['dow'] = sales.date.dt.dayofweek       


#%%
#sess.shape ##(967187, 13)

#%%
bannerIndex = sess.loc[sess["trafficSource_medium"].str.contains("banner")].index
sess.loc[bannerIndex, 'trafficSource_medium'] = "banner" ###Just call anything bannerXXXXX a banner ad."                     
#sess.shape    ##(967187, 13)                   
                       
#%%
cpcIndex = sess.loc[sess["trafficSource_medium"]=="cpc"].index
sess.loc[cpcIndex, 'trafficSource_medium'] = "ppc" ###Change CPC to PPC.                   

#sess.shape ##(967187, 13)     
        
#%%
sess.to_csv('C:/Users/reeserd2/Desktop/PCC Analysis/sess_prepped.csv', index=False)

#%%
sess_LARGE = pd.read_csv("C:/Users/reeserd2/Desktop/PCC Analysis/results-20170623-094700.csv")
###This is a clean csv that Excel has not perverted. 

sess_LARGE['timeonsite']=sess_LARGE['timeonsite'].fillna(0)

convertedTimes = [datetime.datetime.fromtimestamp(int(time)).strftime('%y-%m-%d %H:%M:%S') < 1497330060
 for time  in sess_LARGE.visitStartTime]

#%%

before1201 = [1497329970 < (time) < 1497330030 for time  in sess_LARGE.visitStartTime]

##np.count_nonzero(before1201)


##sess_LARGE[before1201]

#%%

sess1 = pccpy.PartsSession(visitorId = 2222, visitId = 1400001, 
                           startTime = 1485111211, totalTime = 1290, addedToCart = True, purchased = True, 
                 continent = "N. America", totalHits = 100)
sess2 = pccpy.PartsSession( visitorId = 2222, visitId = 2400001,
                           startTime = 1485133211, totalTime = 1111, addedToCart = True, purchased = True,
                 continent = "N. America", totalHits = 100)
sess3 = pccpy.PartsSession( visitorId = 2222, visitId = 3400001,
                           startTime = 1485155211, totalTime = 1233, addedToCart = True, purchased = True, 
                 continent = "N. America", totalHits = 100)
sess4 = pccpy.PartsSession( visitorId = 2222, visitId = 4400001,
                           startTime = 1485187211, totalTime = 15422, addedToCart = True, purchased = True, 
                 continent = "N. America", totalHits = 100)
sess5 = pccpy.PartsSession( visitorId = 2222, visitId = 5400001,
                           startTime =1485202635, totalTime = 15422, addedToCart = True, purchased = True, 
                 continent = "N. America", totalHits = 100)

print(sess1.sessionId)
print(sess2.sessionId)
print(sess3.sessionId)
print(sess4.sessionId)
print(sess5.sessionId)

#%%

visitor2 = pccpy.Visitor(fullVisitorId=2222)

#
visitor2.update(sess1,sess2, sess3, sess4, sess5)

print(visitor2)

print(visitor2.findAveTimeBetweenSession())

print(visitor2.findMinTimeBetweenSession())



#%%
sess_LARGE[1:2]["totalTime"]
#%%

numRecords = (sess_LARGE.shape)

sessDict = {} ###a new session dictionary. 

for row in range(0, numRecords[0]):
   dfRow = sess_LARGE[row:row+1]
   raw_record = pccpy.Record(fullVisitorId = int(dfRow["fullVisitorId"]),
                             visitId = dfRow["visitId"], hitNumber = int(dfRow["hitNumber"]),
                                            startTime = int(dfRow["visitStartTime"]),
                                            totalTime = int(dfRow["timeonsite"]),
                                            addedToCart = int(dfRow["added_to_cart"]),
                                            removedFromCart =int(dfRow["removed_to_cart"]), 
                                            wentToCheckout = int(dfRow["went_to_checkout"]),
                                            purchased = int(dfRow["completed_purchase"]),
                                            continent = dfRow["geoNetwork_subContinent"])
   
   ##if not raw_record.addedToCart:
       ##print("Testing here")
   
   key = pccpy.makeSessId(int(raw_record.fullVisitorId), int(raw_record.visitId))
   ##3Do some sort of IF NULL CREATE AND ADD, else just add record to extant session. 
   if key in sessDict:
       sessDict[key].addToSession(raw_record)
   else:
       sessDict[key] = pccpy.PartsSession(visitorId = raw_record.fullVisitorId, visitId = raw_record.visitId,
               startTime = raw_record.startTime, totalTime = raw_record.totalTime,
               continent = raw_record.continent)
       sessDict[key].addToSession(raw_record)
   #print(raw_record.fullVisitorId)



#%%
total = 0
for sess in sessDict.itervalues():
    sess.finalSessionGather()
    if(sess.addedToCart):
        print("Session {0} added to cart!".format(sess.sessionId))
        total +=1

#%%

##Just a fast validity check.  

for val in sessDict.itervalues():
    if len(val.recordSet) > 3:
        print(val.sessionId)
        print(val.fullVisitorId)            
        print(val.recordSet)


#%%

visitorDict = {} ###a new visitor dictionary. 

for sess in sessDict.itervalues():
     
   key = sess.fullVisitorId
   
   ###print(key)
  
   if key in visitorDict:
       visitorDict[key].update(sess)###Remember that a Visitor is a set. (Inheritance). 
   else:
       visitorDict[key] = pccpy.Visitor(fullVisitorId = key)
       visitorDict[key].update(sess)
   #print(raw_record.fullVisitorId)



#%%
print(len(sessDict))
print(len(visitorDict.keys()))


#%%

for visitors in visitorDict.itervalues():
    visitors.finalVisitorGather()


#%%

len(visitorDict)

#%%

for visitor in visitorDict.itervalues():
    if len(visitor) > 1 and visitor.minTimeBetweenSess < 0: ###has more than only 1 session recorded.  
          print("Min time between sessions is {0}".format(visitor.minTimeBetweenSess))
          print("The associated visitor ID is {0} \n".format(visitor.fullVisitorId))
          
#%%

for sess in visitorDict[8361919491331785015]:
    print("Session {0} has an end time of {1}".format(sess.sessionId, sess.endTimePOSIX))
    print("Session {0} has a start time of {1}".format(sess.sessionId,sess.startTime))
    print("Session {0} has a total time of {1} \n".format(sess.sessionId, sess.totalTime))



#%%

np.diff([1497301308, 1497301315, 1497301452])

#%%

#%%

#%%

#%%

#%%

#%%

#%%

#%%

#%%

#%%

#%%

#%%

#%%

#%%

#%%

#%%

#%%

#%%

#%%

#%%

#%%

#%%

#%%

#%%

#%%

#%%

#%%

#%%

#%%

#%%

#%%

#%%

#%%

#%%

#%%

#%%

#%%

































