# -*- coding: utf-8 -*-
"""
Created on Tue Jun 06 16:13:02 2017

@author: reeserd2
"""

#%%
import pandas as pd
import numpy as np

import datetime
import cPickle as pickle

import sys
sys.path.append("C:/Users/reeserd2/Desktop/PCC Analysis/")
import pccpy ###To import pccpy. 


#%%

#from collections import Counter
#from collections import defaultdict
 
sales = pd.read_csv("C:/Users/reeserd2/Desktop/PCC Analysis/data 4 Visitor Aggregation.csv")


sales['date'] = pd.to_datetime(sales.date, format='%Y%m%d')###Convert the dates over




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
sess.loc[pd.isnull(sess.timeonsite), 'timeonsite'] =0 ###impute time on site when missing. Can use median. 0 is better. 

###In my examination, it seems that when total time on site is null, this means it was a flash hit. 
###The "user" came and went immediately. Every record with timeonsite = NULL has a single pageview. 
###It seems to be a better move to impute these entries with 0 for totalTime.  
         
         

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
    if len(visitor) > 1 and visitor.aveTimeBetweenSess < 0: ###has more than only 1 session recorded.  
          print("Min time between sessions is {0}".format(visitor.minTimeBetweenSess))
          print("The associated visitor ID is {0} \n".format(visitor.fullVisitorId))
          
#%%

###Testing a specific visitor. 
for sess in visitorDict[5699057072235125817]:
    print("Session {0} has an end time of {1}".format(sess.sessionId, sess.endTimePOSIX))
    print("Session {0} has a start time of {1}".format(sess.sessionId,sess.startTime))
    print("Session {0} has a total time of {1} \n".format(sess.sessionId, sess.totalTime))



#%%

finalDiff = [a - b for a,b in zip(np.diff([int(1497301308), int(1497301315), int(1497301452)]),([0,0,47]))]

print(finalDiff)
#%%

AA = [(1497409196,1), (1497406440, 1923), (1497409464, 0)]



AA.sort(key=lambda x: x[0])
durations = [x[1] for x in AA]

print(AA)

print(np.diff(AA, axis = 0)[0:,0])


gapTimes = [stopTimeDiff - sessDuration for stopTimeDiff,sessDuration in zip(np.diff(AA, axis = 0)[0:,0], durations)]


print(gapTimes)

#%%

###################################################################################
###################################################################################

##### Moving now into the actual analysis of the real data set. 
fullPCCdata = pd.read_csv("C:/Users/reeserd2/Desktop/PCC Analysis/session_raw.csv")
###This is a clean csv that Excel has not perverted. 

#%%

#####Some data clean up as necessary.
fullPCCdata['timeonsite']=fullPCCdata['timeonsite'].fillna(0)
fullPCCdata['total_transactions']=fullPCCdata['total_transactions'].fillna(0)
fullPCCdata['pageviews']=fullPCCdata['pageviews'].fillna(0)
fullPCCdata['visitNumber']=fullPCCdata['visitNumber'].fillna(0)

    ####Clean up the outliers for hitNumber and timeOnSite. These are GLOBAL outliers. 
hitNumber_outlier_mask = ((fullPCCdata.hitNumber - fullPCCdata.hitNumber.mean()) / fullPCCdata.hitNumber.std()).abs() > 3
timeonsite_outlier_mask = ((fullPCCdata.timeonsite - fullPCCdata.timeonsite.mean()) /fullPCCdata.timeonsite.std()).abs() > 3

nrow_start = fullPCCdata.shape[0]

fullPCCdata = fullPCCdata[~((hitNumber_outlier_mask) & (timeonsite_outlier_mask))]

1.0*fullPCCdata.shape[0] / nrow_start ####0.9915760437320437

#%%

#### We need to strip out a smaller dat set for figuring out just how many records without CWS Ids we have that can be 
##        associated with an extant CWS Id.

## These are the things we need: cwsid fullVisitorId city eguid	latitude	longitude	visitId

#cws_and_fvId_unify = fullPCCdata["cwsid", "fullVisitorId", "city", "eguid",	"latitude", "longitude", "visitId"]

sortedBy_fvId_cwsId = fullPCCdata.sort_values(by = ["fullVisitorId", "cwsid"], axis = 0)

#%%

cws_and_fvId_unify = sortedBy_fvId_cwsId[["cwsid", "fullVisitorId", "city", "eguid",	"latitude", "longitude", "visitId"]]

#%%
cws_and_fvId_unify.to_csv('C:/Users/reeserd2/Desktop/PCC Analysis/cws_fvid_unify.csv', index=False)

#%%

######################################################################################################################
## +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
######################################################################################################################



###We now need to move on to analysing just those records with CWS IDs. 

recordsHavingCWS = fullPCCdata[pd.notnull(fullPCCdata.cwsid)]
#recordsHavingNoCWS = fullPCCdata[pd.isnull(fullPCCdata.cwsid)]



#%%


recordsHavingCWS = recordsHavingCWS[(recordsHavingCWS.timeonsite > 30)]


#%%

print(datetime.datetime.now())

numRecords = (recordsHavingCWS.shape)

sessDict = {} ###a new session dictionary. 

for row in range(0, numRecords[0]):
   dfRow = recordsHavingCWS[row:row+1]
   raw_record = pccpy.Record(fullVisitorId = int(dfRow["fullVisitorId"]),
                            browser = dfRow["browser"],
                            visitId = dfRow["visitId"],
                            hitNumber = int(dfRow["hitNumber"]),
                            startTime = int(dfRow["visitStartTime"]),
                            totalTime = int(dfRow["timeonsite"]),
                            added_to_cart = int(dfRow["added_to_cart"]),
                            removedFromCart =int(dfRow["removed_to_cart"]), 
                            wentToCheckout = int(dfRow["went_to_checkout"]),
                            completed_purchase = int(dfRow["completed_purchase"]),
                            country = dfRow["country"],
                            cityId = dfRow["cityId"],
                            city = dfRow["city"],
                            click_thru_product_list = dfRow["click_thru_product_list"],
                            cwsid = str(dfRow["cwsid"]), 
                            date = dfRow["date"],
                            ecid = dfRow["ecid"],
                            eguid = dfRow["eguid"],
                            isMobile = dfRow["isMobile"],
                            keyword = dfRow["keyword"],
                            language = dfRow["language"],
                            latitude = dfRow["latitude"],
                            longitude = dfRow["longitude"],
                            medium = dfRow["medium"],
                            metro = dfRow["metro"],
                            pageViews = int(dfRow["pageviews"]),
                            refund_of_purchase = dfRow["refund_of_purchase"],
                            region = dfRow["region"],
                            searchKeyword = dfRow["searchKeyword"],
                            source = dfRow["source"],
                            total_transactions = int(dfRow["total_transactions"]),
                            viewed_product_detail = int(dfRow["viewed_product_detail"]),
                            visitNumber = int(dfRow["visitNumber"]))
   
   ##if not raw_record.addedToCart:
       ##print("Testing here")
   
   key = pccpy.makeSessId(int(raw_record.fullVisitorId), int(raw_record.visitId))
   ##3Do some sort of IF NULL CREATE AND ADD, else just add record to extant session. 
   if key in sessDict:
       sessDict[key].addToSession(raw_record)
   else:
       sessDict[key] = pccpy.PartsSession(visitorId = raw_record.fullVisitorId,
               visitId = raw_record.visitId,
               startTime = raw_record.startTime,
               totalTime = raw_record.totalTime,
               country = raw_record.country,
               visitNumber = raw_record.visitNumber,
               browser = raw_record.browser,
               cityId = raw_record.cityId,
               city = raw_record.city,
               click_thru_product_list = raw_record.clickProductList,
               cwsid = raw_record.cwsid,
               ecid = raw_record.ecid,
               eguid = raw_record.eguid,
               isMobile = raw_record.isMobile,
               keyword = raw_record.sourceKeyword,
               language = raw_record.language,
               medium = raw_record.sourceMedium,
               metro = raw_record.metro,
               pageViews = raw_record.pageViews,
               refund_of_purchase = raw_record.refund,
               region = raw_record.region,
               viewed_product_detail = raw_record.viewedProdDetail
               )
       sessDict[key].addToSession(raw_record)
   #print(raw_record.fullVisitorId)


print(datetime.datetime.now())


#%%

###We are going to pickle (serialize) the session dictionary so we do not need to continually be restoring it each time.

def save_obj(obj, fileName ): ###fileName is the complete path minus the file extension. (.pkl will be the extension)
    with open(fileName + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(fileName):
    with open(fileName + '.pkl', 'rb') as f:
        return pickle.load(f)
    
    


#%%
    
save_obj(visitorDict, "C:/Users/reeserd2/Desktop/PCC Analysis/visitor_dict_06282017") 

#%%

visitor_dict = load_obj("C:/Users/reeserd2/Desktop/PCC Analysis/visitor_dict_06282017")


#%%
total = 0
for sess in sessDict.itervalues():
    sess.finalSessionGather()
    if(sess.addedToCart and total < 100):
        print("Session {0} added to cart!".format(sess.sessionId))
        total +=1
    elif(sess.addedToCart):
        total +=1

#%%

##Just a fast validity check.  

for val in sessDict.itervalues():
    if len(val.recordSet) > 37:
        print(val.sessionId)
        print(val.fullVisitorId)            
        print(val.recordSet)


len(sessDict["6MRLDC56WBR31J63RS"].recordSet)

#%%

visitorDict = {} ###a new visitor dictionary. 

for sess in sessDict.itervalues():
     
   key = sess.fullVisitorId
   
   ###print(key)
  
   if key in visitorDict:
       visitorDict[key].update(sess)###Remember that a Visitor is a set. (Inheritance). 
   else:
       visitorDict[key] = pccpy.Visitor(fullVisitorId = key, cwsid = sess.cwsid)
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
    if len(visitor) > 1 and visitor.aveTimeBetweenSess < 2: ###has more than only 1 session recorded.  
          print("Min time between sessions is {0}".format(visitor.minTimeBetweenSess))
          print("The associated visitor ID is {0} \n".format(visitor.fullVisitorId))
          print("The associated CWS ID is {0} \n".format(visitor.cwsid))



#%%
total = 0
for v in visitorDict.itervalues():
    ##sess.finalSessionGather()
    if(v.addedToCart and total < 100):
        print("Visitor {0} added to cart!".format(v.cwsid))
        total +=1
    elif(v.addedToCart):
        total +=1



#%%
totalPurchasers = 0
for v in visitorDict.itervalues():
    ##sess.finalSessionGather()
    if(v.completedPurchase and totalPurchasers < 100):
        print("Visitor {0} completed at least one purchase!".format(str(v.cwsid)))
        totalPurchasers +=1
    elif(v.completedPurchase):
        totalPurchasers +=1

#%%
count = 0
for v in visitorDict.itervalues():
    ##sess.finalSessionGather()
    if(len(v) > 1 and count < 100 and v.completedPurchase):
        print("Visitor {0} has multiple sessions!".format(str(v.cwsid)))
        count +=1
    elif(len(v) >1 and v.completedPurchase):
        count +=1

#%%

maxSessions = 0
for v in visitorDict.itervalues():
    ##sess.finalSessionGather()
    if(len(v) > maxSessions):
       maxSessions = len(v)
    


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

































