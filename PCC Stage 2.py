# -*- coding: utf-8 -*-
"""
Created on Wed Jun 28 15:01:53 2017

@author: reeserd2
"""

#####PCC Analysis Stage 2.

#### I am now looking at creating a flow of events for the PCC data.

'''
####Specifically we are first concerned with sessions WITH CWS Ids. 
#### I am going to start with sparse session and record data. 
### This is done in hopes of condensing the size of what we need to analyze
If this is not enough, we may need to look into making an external datbase. MongoDB, DiscoDB.

As it later becomes necessary, we can begin using the full record and session data.

'''


# %%
import pandas as pd
# import numpy as np

import datetime
import cPickle as pickle
import shelve

#import sys
#sys.path.append("C:/Users/reeserd2/Desktop/PCC Analysis/")
import pccpy ###To import pccpy. 


from collections import Counter

import csv
import os

#%%

##### Moving now into the actual analysis of the real data set. 
fullPCCdata = pd.read_csv("C:/Users/reeserd2/Desktop/PCC Analysis/data 4 Visitor Aggregation.csv")
fullPCCdata.drop(fullPCCdata.columns[[0]], axis=1, inplace=True)
###This is a clean csv that Excel has not perverted. 

#%%
###Full transaction data. Should be clean and unadulterated by Excel. 

fullTransactionData = pd.read_csv("C:/Users/reeserd2/Desktop/PCC Analysis/txn_raw.csv")
##The goal is to match this to the sessions contructed by the session data. 



#%%

#####Some data clean up as necessary.
fullPCCdata['timeOnSite']=fullPCCdata['timeOnSite'].fillna(0)

fullPCCdata["rev"] = fullPCCdata["rev"].fillna(0)
####Anything without
#fullTransactionData["qty"] = fullTransactionData["qty"].fillna(0)

    ####Clean up the outliers for hitNumber and timeOnSite. These are GLOBAL outliers. 
hitNumber_outlier_mask = ((fullPCCdata.hitNumber - fullPCCdata.hitNumber.mean()) / fullPCCdata.hitNumber.std()).abs() > 3
timeonsite_outlier_mask = ((fullPCCdata.timeOnSite - fullPCCdata.timeOnSite.mean()) /fullPCCdata.timeOnSite.std()).abs() > 3

nrow_start = fullPCCdata.shape[0]

fullPCCdata = fullPCCdata[~((hitNumber_outlier_mask) & (timeonsite_outlier_mask))]

1.0*fullPCCdata.shape[0] / nrow_start ####0.9915760437320437
#%%

###Trying to clear all the head space possible. 
del nrow_start
del hitNumber_outlier_mask
del timeonsite_outlier_mask
                     

#%%


###We now need to move on to analysing just those records with CWS IDs. 

##recordsHavingCWS = fullPCCdata[pd.notnull(fullPCCdata.cwsid)]
#recordsHavingNoCWS = fullPCCdata[pd.isnull(fullPCCdata.cwsid)]

#%%



#%%

###A short cut to getting the session IDs without having to have the sessDict loaded.
### If sessDict is loaded, just get the key-set.

sessIDSet = set()

idPairs = zip(recordsHavingCWS["fullVisitorId"], recordsHavingCWS["visitId"])

for pair in idPairs:
    sessID = pccpy.makeSessId(int(pair[0]), int(pair[1]))
    sessIDSet.add(sessID)


#%%

#####  Looking into how many CWS sessions have recorded transaction data. 

txn_sessIDSet = set()
txn_event_count = 0


txn_idPairs = zip(fullTransactionData["fullVisitorId"], fullTransactionData["visitId"])

for pair in txn_idPairs:
    txn_sessID = pccpy.makeSessId(int(pair[0]), int(pair[1]))
    txn_sessIDSet.add(txn_sessID)
    if(txn_sessID in sessIDSet):
       txn_event_count += 1

#%%
sessWithTxn = sessIDSet.intersection(txn_sessIDSet)

len(sessWithTxn)##### 159277


#%%

for row in range(0, len(fullTransactionData)):
   dfRow = fullTransactionData[row:row+1]
   
   key = pccpy.makeSessId(int(dfRow["fullVisitorId"]), int(dfRow["visitId"]))
   
   if(key in sessWithTxn):
       txn_event_count += 1


#%%

print(datetime.datetime.now())

numRecords = (recordsHavingCWS.shape)

sessDict = {} ###a new session dictionary. 

for row in range(0, numRecords[0]):
   dfRow = recordsHavingCWS[row:row+1]
   
   key = pccpy.makeSessId(int(dfRow["fullVisitorId"]), int(dfRow["visitId"]))
   
   #####Start of if statement
   if(key in sessWithTxn):
           raw_record = pccpy.SparseRecord(fullVisitorId = int(dfRow["fullVisitorId"]),
                            
                            visitId = dfRow["visitId"],
                            hitNumber = int(dfRow["hitNumber"]),
                            startTime = int(dfRow["visitStartTime"]),
                            totalTime = int(dfRow["timeonsite"]),
                            added_to_cart = int(dfRow["added_to_cart"]),
                            removedFromCart =int(dfRow["removed_to_cart"]), 
                            wentToCheckout = int(dfRow["went_to_checkout"]),
                            completed_purchase = int(dfRow["completed_purchase"]),
                            
                            click_thru_product_list = dfRow["click_thru_product_list"],
                            cwsid = dfRow["cwsid"].values[0], ###
                            ###CWSId is over wrapped by Pandas. This strips away just the string value. 
                            
                            pageViews = int(dfRow["pageviews"]),
                            refund_of_purchase = dfRow["refund_of_purchase"],
                            
                            total_transactions = int(dfRow["total_transactions"]),
                            viewed_product_detail = int(dfRow["viewed_product_detail"]),
                            visitNumber = int(dfRow["visitNumber"]))
   
           if key in sessDict:
               sessDict[key].addToSession(raw_record)
           else:
               sessDict[key] = pccpy.SparseSession(visitorId = raw_record.fullVisitorId,
                       visitId = raw_record.visitId,
                       startTime = raw_record.startTime,
                       totalTime = raw_record.totalTime,
                       
                       visitNumber = raw_record.visitNumber,
                       
                       click_thru_product_list = raw_record.clickProductList,
                       cwsid = raw_record.cwsid,
                       
                       pageViews = raw_record.pageViews,
                       refund_of_purchase = raw_record.refund,
                       
                       viewed_product_detail = raw_record.viewedProdDetail
                       )
               sessDict[key].addToSession(raw_record)
   # end of if statement if(key in sessWithTxn):


print(datetime.datetime.now())


#%%
sessShelf = shelve.open("C:/Users/reeserd2/Desktop/PCC Analysis/sess_txn_dictionary", flag='c',
            protocol=pickle.HIGHEST_PROTOCOL, writeback=True)

#%%
#sessShelf.update(sessDict)
#%%
#sessShelf.close()
#%%

####Try to pickle the sessDict. Or JSON it. 
def save_obj(obj, fileName ): ###fileName is the complete path minus the file extension. (.pkl will be the extension)
    with open(fileName + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(fileName):
    with open(fileName + '.pkl', 'rb') as f:
        return pickle.load(f)
    

#%%
###save_obj(sessDict, "C:/Users/reeserd2/Desktop/PCC Analysis/session_dict") 

#%%

visitorDict = {} ###a new visitor dictionary. 

for sess in sessShelf.itervalues():
     
   key = sess.fullVisitorId
   
   ###print(key)
  
   if key in visitorDict:
       visitorDict[key].update(sess)###Remember that a Visitor is a set. (Inheritance). 
   else:
       visitorDict[key] = pccpy.Visitor(fullVisitorId = key, cwsid = sess.cwsid)
       visitorDict[key].update(sess)
   #print(raw_record.fullVisitorId)

for visitors in visitorDict.itervalues():
    visitors.finalVisitorGather()



#%%

print(datetime.datetime.now())

numRecords = (fullTransactionData.shape)

txnDict = {} ###a new transaction dictionary. 

for row in range(0, numRecords[0]):
   dfRow = fullTransactionData[row:row+1]
   
   assocSess = pccpy.makeSessId(int(dfRow["fullVisitorId"]), int(dfRow["visitId"]))
   
   #####Start of if statement
   if(assocSess in sessWithTxn):
          raw_txn_piece = pccpy.TransactionEvent(
               fullVisitorId = int(dfRow["fullVisitorId"]),            
               visitId = int(dfRow["visitId"]),
               currency = dfRow["currency"].values[0],
               product_category = dfRow["product_category"].values[0],
               qty = int(dfRow["qty"]),
               rev = float(dfRow["rev"]),
               sku = dfRow["sku"].values[0],
               txn_id = int(dfRow["txn_id"]))
        
        #~~~~~~~~~~~~~~~                          
   
          key = "TXN"+str(raw_txn_piece.txnId)
  
          if key in txnDict:
               txnDict[key].addTxn(raw_txn_piece)
          else:
               txnDict[key] = pccpy.Transaction(fullVisitorId = raw_txn_piece.fullVisitorId,
                       visitId = raw_txn_piece.visitId,
                       currency = raw_txn_piece.currency,
                       txn_id = raw_txn_piece.txnId)
               
               txnDict[key].addTxn(raw_txn_piece)
           #We take the first values for these. TxnId, currency, revenue


for txn in txnDict.itervalues():
    txn.txnGather()


print(datetime.datetime.now())

#%%
for visitors in visitorDict.itervalues():
    print(visitors.addedToCart)


#%%
txnShelf = shelve.open("C:/Users/reeserd2/Desktop/PCC Analysis/txn_dictionary", flag='c',
            protocol=pickle.HIGHEST_PROTOCOL, writeback=True)



#%%
#txnShelf.update(txnDict)
#%%
#txnShelf.close()
#%%



#print(len(sessShelf))

print(len(txnShelf))



#%%

txnShelf["TXN1415168"].associatedSessionId


#%%

sessShelf.keys()


#%%
sessShelf['KC0G8T4A7GME1J934P'].cwsid
         
#%%

for txn in txnShelf.itervalues():
    key = txn.associatedSessionId
    sessShelf[key] .addTxnToSess(txn)

#%%
##sessShelf["KC0G8T4A7GME1J934P"].transactionSet

for sess in sessShelf.itervalues():
    if(len(sess.transactionSet) > 12):
        print("Session {0} has multiple transactions".format(sess.sessionId))           
           


#%%



def WriteDictToCSV(csv_file,csv_columns,dict_data):
    try:
        with open(csv_file, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for data in dict_data:
                writer.writerow(data)
    except IOError as (errno, strerror):
            print("I/O error({0}): {1}".format(errno, strerror))    
    return            



#%%

currentPath = os.getcwd().replace("\\", "/")
csv_file = currentPath + "/csv/Names.csv"

csv_columns = fullTransactionData.columns

WriteDictToCSV(csv_file,csv_columns,txnDict)

#%%
count = 0

for sess in sessShelf.iteritems():
    if(count < 25):
        print(sess)
        count += 1


#%%

low_cutoff = 10
high_cutoff = 100
count = 0

for v in visitorDict.itervalues():
    if((high_cutoff >= len(v) >= low_cutoff) and v.completedPurchase):
        print("This visitor has at least {0} sessions, but no more than {2} sessions: {1}".format(low_cutoff,
              v.cwsid, high_cutoff))
        count +=1
print("We have " + str(count) + " total visitors")        



#%%
counts = Counter(recordsHavingCWS["cwsid"])

countTuples = counts.most_common()[-27020:-27000]

#%%

cwsID_list = [x[0] for x in countTuples]

cwsID_list

#%%
HAMdata = recordsHavingCWS[recordsHavingCWS.cwsid.isin(cwsID_list)]

HAMdata.drop(["ecid","eguid","isMobile" ,"keyword"], axis=1, inplace=True)
HAMdata.drop(["source","searchKeyword","region","medium" ,"metro"], axis=1, inplace=True)
HAMdata.drop(["hitNumber", "language", "latitude", "longitude", "pageviews"], axis=1, inplace=True)



#%%

HAMdata = HAMdata[["cwsid",	"fullVisitorId",	"visitId", 	"click_thru_product_list",
	"viewed_product_detail",	"added_to_cart",	"removed_to_cart",	"went_to_checkout",
	"completed_purchase",	"refund_of_purchase","visitNumber",	"visitStartTime",
	"date",	"country", "timeonsite"]]




#%%

HAMdata.to_csv('C:/Users/reeserd2/Desktop/PCC Analysis/HAM_InitialPCC.csv', index=False)


#%%


######################################################################################################
######################################################################################################

#### Clustering of the PCC data based on 




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
