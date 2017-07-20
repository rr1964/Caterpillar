# -*- coding: utf-8 -*-
"""
Created on Mon Jun 19 09:41:55 2017

@author: Randall Reese for Caterpillar Inc. 
"""



#import datetime
#import geopy
import numpy as np
#from operator import sub


############################################################################################################
############################################################################################################
############################################################################################################
###Suplementry functions.

def base36encode(number, alphabet='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
    """Converts an integer to a base36 string."""
    if not isinstance(number, (int, long)):
        raise TypeError('number must be an integer')

    base36 = ''
    sign = ''

    if number < 0:
        sign = '-'
        number = -number

    if 0 <= number < len(alphabet):
        return sign + alphabet[number]

    while number != 0:
        number, i = divmod(number, len(alphabet))
        base36 = alphabet[i] + base36

    return sign + base36

def base36decode(number):
    return int(number, 36)

##print base36encode(1412823931503067241)
##print base36decode('AQF8AA0006EH')

def makeSessId(fullVisitorId, visitId):
    sessId = base36encode(fullVisitorId)+base36encode(visitId-1400000000)
    return(sessId)


    


############################################################################################################
############################################################################################################
############################################################################################################


###CLASS DEFINITIONS

##**************************************************************************************************************************
##**************************************************************************************************************************
###  RECORD
##**************************************************************************************************************************
##**************************************************************************************************************************


###The column names we have available are as follows:
    
'''
,added_to_cart,city,completed_purchase,currency,cwsid,date,fullVisitorId,hitNumber,keyword,latitude,longitude,
medium,pageviews,qty,removed_from_cart,rev,source,timeOnSite,visitId,visitStartTime,went_to_checkout
'''

###Implements the class "Record"
class Record:
    def __init__(self, added_to_cart,city,completed_purchase,currency,cwsid,date,fullVisitorId,hitNumber,
                 keyword,latitude,longitude,medium,pageViews,qty,removed_from_cart,rev,source,timeOnSite,
                 visitId,visitStartTime,went_to_checkout):
        
        self.fullVisitorId = fullVisitorId
        self.city = city
       
        self.cwsid = cwsid
        self.date = date
        
        self.latitude = latitude
        self.longitude = longitude
        self.sourceSource = source
        self.sourceMedium = medium
        self.sourceKeyword = keyword
        self.pageViews = pageViews
        
        self.revenue = rev
        self.quantity = qty
        
        self.visitId = visitId
        self.visitStartTime = visitStartTime
        self.timeOnSite = timeOnSite
        
        self.addedToCart = added_to_cart
        self.removedFromCart = removed_from_cart
        self.wentToCheckout = went_to_checkout
        self.purchased = completed_purchase
        
        self.hitNumber = hitNumber
    
##**************************************************************************************************************************
##**************************************************************************************************************************
###  SPARSE RECORD
##**************************************************************************************************************************
##**************************************************************************************************************************
class SparseRecord:
    def __init__(self, added_to_cart,click_thru_product_list,
                 completed_purchase,cwsid,fullVisitorId,hitNumber,pageViews,refund_of_purchase,removedFromCart,
                 totalTime,total_transactions,
                 viewed_product_detail,visitId,visitNumber,startTime,wentToCheckout):
        
        self.fullVisitorId = fullVisitorId
        
        self.cwsid = cwsid
        
        self.pageViews = pageViews
        
        
        self.visitId = visitId
        self.visitNumber = visitNumber
        self.startTime = startTime
        self.totalTime = totalTime
        
        
        self.addedToCart = added_to_cart
        self.removedFromCart = removedFromCart
        self.wentToCheckout = wentToCheckout
        self.purchased = completed_purchase
        
        
        self.hitNumber = hitNumber
    

##**************************************************************************************************************************
##**************************************************************************************************************************
###  PARTSSESSION
##**************************************************************************************************************************
##**************************************************************************************************************************

###Implements the class "PartsSession"
class PartsSession:
    def __init__(self, visitorId, visitId, visitStartTime, timeOnSite, city, cwsid, keyword,
                 medium, pageViews,source, latitude, longitude, date,
                 addedToCart = False, wentToCheckout = False, removedFromCart = False, completedPurchase= False):
        
        self.sessionId = makeSessId(int(visitorId), int(visitId))
        self.fullVisitorId = visitorId
        self.visitId = visitId
        self.date = date
        self.visitStartTime = visitStartTime
        self.timeOnSite = timeOnSite
        self.endTimePOSIX = visitStartTime + timeOnSite
        
        self.latitude = latitude
        self.longitude = longitude
        
        self.sourceMedium = medium
        self.sourceSource = source
        self.sourceKeyword = keyword
        
        self.addedToCart = addedToCart
        self.wentToCheckout = wentToCheckout
        self.removedFromCart = removedFromCart
        self.completedPurchase = completedPurchase
        
        self.totalHits = 0 ####See findTotalHits()
        ####totalHits is NOT unified (necessarily) with totals.hits.
        ####totalHits is just the largest hit observed in the session. 
        self.pageViews = pageViews
        self.totalRevenue = 0
        self.totalQty = 0
        self.totalPurchases = 0
        
        self.city = city
        self.cwsid = cwsid        
        
        ####implement more boolenas here
        
        self.recordSet = set()
        ##self.transactionSet = set()
##-----------------------------------------------------------------------------            
    def __str__(self):
        return "SessionId: {0}, Date: {1}, Total Revenue: {2}, Total Qty: {3}".format(self.sessionId,
                               self.date, self.totalRevenue, self.totalQty)

##-----------------------------------------------------------------------------    

    def __repr__(self):
        return self.__str__()
        
##-----------------------------------------------------------------------------        
    def addToSession(self, *records2Add):
        self.recordSet.update(records2Add)

##-----------------------------------------------------------------------------        
    def removeFromSession(self, record2Rem):
        try:
            self.recordSet.remove(record2Rem)
        except KeyError as ke:
            print "KeyError({0}): {1}".format(ke.errno, ke.strerror)
            
##-----------------------------------------------------------------------------   
    def discardFromSession(self, record2Remove):
        self.recordSet.discard(record2Remove)    
    
##-----------------------------------------------------------------------------        
    def addTxnToSess(self, *txns2Add):
        self.transactionSet.update(txns2Add)

##-----------------------------------------------------------------------------        
    def removeTxnFromSession(self, txn2Rem):
        try:
            self.transactionSet.remove(txn2Rem)
        except KeyError as ke:
            print "KeyError({0}): {1}".format(ke.errno, ke.strerror)
            
##-----------------------------------------------------------------------------   
    def discardTxnFromSession(self, txn2Remove):
        self.transactionSet.discard(txn2Remove)   
        
##-----------------------------------------------------------------------------   
    def findTotalHits(self):
        for rec in self.recordSet:
            self.totalHits = max(rec.hitNumber, self.totalHits) 


##-----------------------------------------------------------------------------  
    def findTotalRevenue(self):
        self.totalRevenue = 0 ###Prevents against double counting revenue.
        for rec in self.recordSet:
            if(rec.purchased):##Just a preventative measure.  
                self.totalRevenue += rec.revenue

##-----------------------------------------------------------------------------  
    def findTotalQty(self):
        self.totalQty = 0 ###Prevents against double counting quantity.
        for rec in self.recordSet:
            if(rec.purchased): ###Only count quantity from actual purchases. 
                self.totalQty += rec.quantity

##-----------------------------------------------------------------------------  
    def findTotalPurchases(self):
        self.totalPurchases = 0 ###Prevents against double counting quantity.
        for rec in self.recordSet:
            if(rec.purchased): ###Only count quantity from actual purchases. 
                self.totalPurchases += 1                
            
##-----------------------------------------------------------------------------  
    def everAddedToCart(self):
        
       if self.addedToCart:
            return(True)
       else:
           for rec in self.recordSet:
               if rec.addedToCart:
                   self.addedToCart = True
                   return(True)
               else:
                   continue
                
        ###Finally, at the for loop end, 
       return(False)
            
##-----------------------------------------------------------------------------  
    def everRemovedFromCart(self):
        
       if self.removedFromCart:
            return(True)
       else:
           for rec in self.recordSet:
               if rec.removedFromCart:
                   self.removedFromCart = True
                   return(True)
               else:
                   continue
                
        ###Finally, at the for loop end, 
       return(False)  
   
##-----------------------------------------------------------------------------  
    def everWentToCheckout(self):
        
       if self.wentToCheckout:
            return(True)
       else:
           for rec in self.recordSet:
               if rec.wentToCheckout:
                   self.wentToCheckout = True
                   return(True)
               else:
                   continue
                
        ###Finally, at the for loop end, 
       return(False)      
##-----------------------------------------------------------------------------      
    def everPurchased(self):
        
        if self.completedPurchase:
            return(True)
        else:
            for rec in self.recordSet:
                if rec.purchased:
                    self.completedPurchase = True
                    return(True)
                else:
                    continue
                
        ###Finally, at the for loop end, 
        return(False)
                
##-----------------------------------------------------------------------------         
    def finalSessionGather(self):  #Update all values for the session as necessary. 
       
        ##print("Doing final session gather on {0}".format(self.sessionId))
        self.findTotalHits()
        self.findTotalQty()
        self.findTotalRevenue()
        self.everAddedToCart()
        self.everRemovedFromCart()
        self.everWentToCheckout()
        self.everPurchased()              
    
  
##**************************************************************************************************************************
##**************************************************************************************************************************
###  SPARSE SESSION.
##**************************************************************************************************************************
##**************************************************************************************************************************  
class SparseSession(PartsSession):
    def __init__(self, visitorId, visitId, startTime, totalTime, visitNumber,
             click_thru_product_list, cwsid, pageViews, refund_of_purchase, viewed_product_detail,
             addedToCart = False, wentToCheckout = False, removedFromCart = False, completed_purchase= False):
    
                self.sessionId = makeSessId(int(visitorId), int(visitId))
                self.fullVisitorId = visitorId
                self.visitId = visitId
                self.startTime = startTime
                self.totalTime = totalTime
                self.endTimePOSIX = startTime + totalTime
                
                self.addedToCart = addedToCart
                self.wentToCheckout = wentToCheckout
                self.removedFromCart = removedFromCart
                self.completedPurchase = completed_purchase
                
                self.totalHits = 0 ####See findTotalHits()
                ####totalHits is NOT unified (necessarily) with totals.hits.
                ####totalHits is just the largest hit observed in the session. 
                self.clickProductList = click_thru_product_list
                self.cwsid = cwsid
                
                self.pageViews = pageViews###This is total page views in the entire session. 
                self.refund = refund_of_purchase
                ###totalTransactions is not clear in its meaning. 
                self.viewedProdDetail = viewed_product_detail
                self.visitNumber = visitNumber
                                
                self.recordSet = set()
                self.transactionSet = set()

    

##**************************************************************************************************************************
##**************************************************************************************************************************
###  VISITOR
##**************************************************************************************************************************
##**************************************************************************************************************************

###Implements the class "Visitor"
#####At some point, this could maybe be made into its own file. Right now it is just a collection class for PartsSessions
class Visitor(set): #inherits from class "set"
    def __init__(self, fullVisitorId, cwsid, addedToCart = False, purchased = False):
        self.fullVisitorId = fullVisitorId
        self.cwsid = cwsid
        ## Visitor could be a list containing PartsSession objects. 
        ###Do we need the session list to be ordered? The only reason ordering 'matters' is for the chronology.
        ###But maintaining chronology could be harder than it is worth. 
        ###Although we may actually care about chronology, since we want to track sessions as a time series. 
        ###But will it be easier to store these as a set, then sort AS NEEDED. 
        
        ##The following booleans are to track if an action has EVER taken place.
        ##These booleans are used to check if a visitor has ever done one of these actions.
        ##Should return true if the visitor is associated with a session with any of these true. 
        self.clickThruProd = False
        self.addedToCart = addedToCart
        self.removedFromCart = False
        self.wentToCheckout = False
        self.completedPurchase = purchased
        self.refundOfPurchase = False
        ##Some of these booleans need to be implemented as they become useful. 
        #Also, some of these booleans may not be unified in the data set. Checkouts without cart, purchase with no cart, etc. 
        
        
        ## Ancilliary 
        self.latLongMSE = 0
        self.medTimeBetweenSess = 0 ##findAveTimeBetweenSession()
        self.aveTimeBetweenSess = 0
        self.minTimeBetweenSess = 0 ##findMinTimeBetweenSession()
        self.percentSessionWithPurchase = 0
        self.aveQty = 0
        self.medPageViewPerSess = 0
        self.medRevenuePerSess = 0
        self.medHitTotal = 0

##-----------------------------------------------------------------------------        
    def __str__(self):
        return "fullVisitorId: {0}, Number of Sessions: {1}, Median Page Views: {2}".format(self.fullVisitorId, self.totalNumSessions(),
                               self.medPageViewPerSess)


##-----------------------------------------------------------------------------    
    def __repr__(self):
        return self.__str__()    


##-----------------------------------------------------------------------------        
    def totalNumSessions(self):
        return len(self)


##-----------------------------------------------------------------------------            
    def update(self, *newSessions): ##Add one or more sessions. 
        set.update(self, newSessions)


##-----------------------------------------------------------------------------        
    def remove(self, sess2Remove):
        try:
            set.remove(self, sess2Remove)
        except KeyError as ke:
            print "KeyError({0}): {1}".format(ke.errno, ke.strerror)


##-----------------------------------------------------------------------------        
    def discard(self, sess2Remove):
        set.discard(self, sess2Remove)


##-----------------------------------------------------------------------------        
    def combinedTotalTime(self):
        combTT = 0
        for sess in self:
            combTT += sess.totalTime
        
        return combTT


##-----------------------------------------------------------------------------    
    def findLatLongMSE(self): ####MSE means Mean Squared Error.
        
        print("NOT YET IMPLEMENTED")
        raise ValueError('{0} just called function findLatLongMSE() in Visitor class. NOT IMPLEMENTED'.format(repr(self)))
        ##Look at the distance from the centrod or something. 
        coords_1 = (52.2296756, 21.0122287)
        coords_2 = (52.406374, 16.9251681)
        print geopy.distance.vincenty(coords_1, coords_2).km

        
##-----------------------------------------------------------------------------                                     
    def findAveTimeBetweenSession(self):####This can be modified to be median or max or min, etc. 
        
       timeTuples =  [(sess.visitStartTime, sess.timeOnSite)  for sess in self]
               
       if(len(timeTuples) > 1):  ####If stopTimes <= 1, then  the minTimeBetweenSess = 0 is correct as hard coded. 
          
           timeTuples.sort(key=lambda x: x[0])###Sorts in place.
           durations = [x[1] for x in timeTuples]
                      
           gapTimes = [stopTimeDiff - sessDuration for stopTimeDiff,sessDuration
                       in zip(np.diff(timeTuples, axis = 0)[0:, 0] , durations)]
   #map(sub,np.diff(stopTimes) , np.array(durations) ) is a preferable way IMO.
   #However, numpy is annoyingly bad at type casting and I could not find a way to make np.diff assign a type to its results.  
            ##### Find the difference bewteen the session end times. Then chop off the session time. 
            ##### Results in the gap between the beginning and the end. 
            
           self.aveTimeBetweenSess = np.mean(gapTimes)        
            
           return(self.aveTimeBetweenSess)
        
       else:
            return(0)

##-----------------------------------------------------------------------------                                     
    def findMedTimeBetweenSession(self):####This can be modified to be median or max or min, etc. 
        
       timeTuples =  [(sess.visitStartTime, sess.timeOnSite)  for sess in self]
               
       if(len(timeTuples) > 1):  ####If stopTimes <= 1, then  the minTimeBetweenSess = 0 is correct as hard coded. 
          
           timeTuples.sort(key=lambda x: x[0])###Sorts in place.
           durations = [x[1] for x in timeTuples]
                      
           gapTimes = [stopTimeDiff - sessDuration for stopTimeDiff,sessDuration
                       in zip(np.diff(timeTuples, axis = 0)[0:, 0] , durations)]
   #map(sub,np.diff(stopTimes) , np.array(durations) ) is a preferable way IMO.
   #However, numpy is annoyingly bad at type casting and I could not find a way to make np.diff assign a type to its results.  
            ##### Find the difference bewteen the session end times. Then chop off the session time. 
            ##### Results in the gap between the beginning and the end. 
            
           self.medTimeBetweenSess = np.median(gapTimes)        
            
           return(self.medTimeBetweenSess)
        
       else:
            return(0)


##-----------------------------------------------------------------------------        
    def findMinTimeBetweenSession(self):
       timeTuples =  [(sess.visitStartTime, sess.timeOnSite)  for sess in self]
               
       if(len(timeTuples) > 1):  ####If stopTimes <= 1, then  the minTimeBetweenSess = 0 is correct as hard coded. 
          
           timeTuples.sort(key=lambda x: x[0])###Sorts in place.
           durations = [x[1] for x in timeTuples]
                      
           gapTimes = [stopTimeDiff - sessDuration for stopTimeDiff,sessDuration
                       in zip(np.diff(timeTuples, axis = 0)[0:, 0] , durations)]
           
           self.minTimeBetweenSess = np.min(gapTimes)
           
           return(self.minTimeBetweenSess)
       
       else:
           return(0)   
    

##-----------------------------------------------------------------------------      
    def everPurchased(self):###Did the EVER purchase in ANY session?
        
        if self.completedPurchase:
            return(True)
        else:
            for sess in self:
                if sess.completedPurchase:
                    self.completedPurchase = True
                    return(True)
                else:
                    continue
                
        ###Finally, at the for loop end, 
        return(False)
    



##-----------------------------------------------------------------------------  
    def everAddedToCart(self):##Did they ever add to the cart in ANY session at all?
        
       if self.addedToCart:
            return(True)
       else:
           for sess in self:
               if sess.addedToCart:
                   self.addedToCart = True
                   return(True)
               else:
                   continue
                
        ###Finally, at the for loop end, 
       return(False)
            
 ##-----------------------------------------------------------------------------  
    def everRemovedFromCart(self):
        
       if self.removedFromCart:
            return(True)
       else:
           for sess in self:
               if sess.removedFromCart:
                   self.removedFromCart = True
                   return(True)
               else:
                   continue
                
        ###Finally, at the for loop end, 
       return(False)  
   
##-----------------------------------------------------------------------------  
    def everWentToCheckout(self):
        
       if self.wentToCheckout:
            return(True)
       else:
           for sess in self:
               if sess.wentToCheckout:
                   self.wentToCheckout = True
                   return(True)
               else:
                   continue
                
        ###Finally, at the for loop end, 
       return(False)      

       

##-----------------------------------------------------------------------------
    def findPercentPurchases(self):
        totalSessWithPurchase= 0
        if(not self.completedPurchase):
            return 0
        else:        
            for sess in self:
                if(sess.completedPurchase):
                    totalSessWithPurchase += 1
            self.percentSessionWithPurchase =  totalSessWithPurchase*1.0 / len(self)        
            return(self.percentSessionWithPurchase)   
        
##-----------------------------------------------------------------------------
    def findAveQuantity(self):
        if(not self.completedPurchase):
            return 0
        else:        
            totalQtys = [sess.totalQty  for sess in self]
            
            self.aveQty = np.mean(totalQtys)
            
            return(self.aveQty)         
                   
##-----------------------------------------------------------------------------
    def findMedPageViewPerSess(self):
        totalPageViews = [sess.pageViews for sess in self]
            
        self.medPageViewPerSess = np.median(totalPageViews)
            
        return(self.medPageViewPerSess)             

                  
##-----------------------------------------------------------------------------
    def findMedRevenuePerSess(self):
        totalRevenue = [sess.totalRevenue for sess in self]
            
        self.medRevenuePerSess = np.median(totalRevenue)
            
        return(self.medRevenuePerSess)    
          

##-----------------------------------------------------------------------------
    def findMedHitTotal(self):
        totalHits = [sess.totalHits for sess in self]
            
        self.medHitTotal = np.median(totalHits)
            
        return(self.medHitTotal)   

##-----------------------------------------------------------------------------         
    def finalVisitorGather(self):  #Update all values for the visitor as necessary. 
       
        ##print("Doing final Visitor gather on: {0}".format(self))
        self.findMedTimeBetweenSession()
        self.findMinTimeBetweenSession()
        self.everAddedToCart()
        self.everRemovedFromCart()
        self.everWentToCheckout()
        self.everPurchased()
        self.findPercentPurchases()
        self.findAveQuantity()
        self.findMedPageViewPerSess()
        self.findMedRevenuePerSess()
        self.findMedHitTotal()
        
 



##**************************************************************************************************************************
##**************************************************************************************************************************
###  TRANSACTION EVENT
##**************************************************************************************************************************
##**************************************************************************************************************************

###Implements the class "TransactionEvent"
###currency,date,fullVisitorId,product_category,qty,rev,sku,txn_id,visitId

class TransactionEvent:
    def __init__(self,currency, fullVisitorId,product_category,qty,rev,sku,txn_id,visitId):
        self.fullVisitorId = fullVisitorId
        self.currency = currency
        
        self.productCategory = product_category
        self.quantity = qty
        self.revenue = rev
        self.sku = sku
        self.txnId = txn_id
        self.visitId = visitId
        
        ##############################      
        
        

##-----------------------------------------------------------------------------        
    def __str__(self):
     #   return "transaction Id: {0}, revenue: {1}, currency: {2}, sku: {3}".format(self.txnId,
                               #self.revenue, self.currency, self.sku)
     
         return("<transaction Id: {0}, revenue: {1}, currency: {2}, sku: {3}>".format(self.txnId,
                self.revenue, self.currency, self.sku))
##-----------------------------------------------------------------------------    
    def __repr__(self):
        return self.__str__()

       
        
##**************************************************************************************************************************
##**************************************************************************************************************************
###  TRANSACTION BLOCK
##**************************************************************************************************************************
##**************************************************************************************************************************

###Implements the class "TransactionEvent"
###currency,date,fullVisitorId,product_category,qty,rev,sku,txn_id,visitId

class TransactionBlock:
    def __init__(self,currency, fullVisitorId,product_category,qty,rev,sku,txn_id,visitId):
        self.fullVisitorId = fullVisitorId
        self.currency = currency
        
        self.productCategory = product_category
        self.quantity = qty
        self.revenue = rev
        self.sku = sku
        self.txnId = txn_id
        self.visitId = visitId
        
        ##############################      
        
        self.exitStage = -1 ##
#            The stages are then determined as follows:
#
#            -1 clean removal from cart (without a double flag)
#            0 A double flag. add_to_cart and remove_from_cart in the same hit.
#            1 clean add_to_cart
#            2 went_to_checkout
#            3 completed_purchase

##-----------------------------------------------------------------------------        
    def __str__(self):
     #   return "transaction Id: {0}, revenue: {1}, currency: {2}, sku: {3}".format(self.txnId,
                               #self.revenue, self.currency, self.sku)
     
         return("<transaction Id: {0}, revenue: {1}, currency: {2}, sku: {3}>".format(self.txnId,
                self.revenue, self.currency, self.sku))
##-----------------------------------------------------------------------------    
    def __repr__(self):
        return self.__str__()
    

##**************************************************************************************************************************
##**************************************************************************************************************************
###  TRANSACTION
##**************************************************************************************************************************
##**************************************************************************************************************************

###Implements the class "Transaction"
###currency,date,fullVisitorId,product_category,qty,rev,sku,txn_id,visitId

class Transaction: ##Cannot get this to correctly pickle when it inherits from set. 
    def __init__(self,currency, fullVisitorId, txn_id,visitId):
        self.fullVisitorId = fullVisitorId
        self.currency = currency
        self.totalQuantity = 0
        self.totalRevenue = 0
        self.txnId = txn_id
        self.visitId = visitId
        
        ##############################
        
        self.associatedSessionId = makeSessId(int(fullVisitorId), int(visitId))
        
        self.transactionSet = set()
       
        
        
        

##-----------------------------------------------------------------------------        
    def __str__(self):
        return "transaction Id: {0}, total revenue: {1}, currency: {2}, total quantity: {3}".format(self.txnId,
                               self.totalRevenue, self.currency, self.totalQuantity)


##-----------------------------------------------------------------------------    
    def __repr__(self):
        return self.__str__()    

##-----------------------------------------------------------------------------        
    def addTxn(self, *txns2Add):
        self.transactionSet.update(txns2Add)

##-----------------------------------------------------------------------------        
    def removeTxn(self, txn2Rem):
        try:
            self.transactionSet.remove(txn2Rem)
        except KeyError as ke:
            print "KeyError({0}): {1}".format(ke.errno, ke.strerror)
            
##-----------------------------------------------------------------------------   
    def discardTxn(self, txn2Remove):
        self.transactionSet.discard(txn2Remove)   
 

##-----------------------------------------------------------------------------        
    def txnGather(self):
        if(self.totalRevenue == 0):
            
            for txnEvent in self.transactionSet:
                self.totalRevenue += txnEvent.revenue
          
        else:
            print("For Transaction {0}, totalRevenue did not start as 0".format(self.txnId))
        
        if(self.totalQuantity == 0):
            
            for txnEvent in self.transactionSet:
                self.totalQuantity += txnEvent.quantity
          
        else:
            print("For Transaction {0}, totalQuantity did not start as 0".format(self.txnId))








