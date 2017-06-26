# -*- coding: utf-8 -*-
"""
Created on Mon Jun 19 09:41:55 2017

@author: Randall Reese for Caterpillar Inc. 
"""



import datetime
import geopy
import numpy as np


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

###Implements the class "Record"
class Record:
    def __init__(self, fullVisitorId, visitId, hitNumber, startTime, totalTime,addedToCart,removedFromCart,
                 wentToCheckout, purchased, continent):
        self.fullVisitorId = fullVisitorId
        self.visitId = visitId
        self.startTime = startTime
        self.totalTime = totalTime
        self.addedToCart = addedToCart
        self.removedFromCart = removedFromCart
        self.wentToCheckout = wentToCheckout
        self.purchased = purchased
        self.continent = continent
        self.hitNumber = hitNumber
    



##**************************************************************************************************************************
##**************************************************************************************************************************
###  PARTSSESSION
##**************************************************************************************************************************
##**************************************************************************************************************************

###Implements the class "PartsSession"
class PartsSession:
    def __init__(self, visitorId, visitId, startTime, totalTime, continent, addedToCart = False,
                 wentToCheckout = False, removedFromCart = False, purchased= False):
        self.sessionId = makeSessId(int(visitorId), int(visitId))
        self.fullVisitorId = visitorId
        self.visitId = visitId
        self.date = datetime.datetime.fromtimestamp(int(startTime)).strftime('%y-%m-%d')
        self.startTime = startTime
        self.totalTime = totalTime
        self.endTimePOSIX = startTime + totalTime
        
        self.addedToCart = addedToCart
        self.wentToCheckout = wentToCheckout
        self.removedFromCart = removedFromCart
        self.completedPurchase = purchased
        
        self.continent = continent
        self.totalHits = 0 ####See findTotalHits()
        ####totalHits is NOT unified (necessarily) with totals.hits.
        ####totalHits is just the largest hit observed in the session. 
        
        
        ####implement more boolenas here
        
        self.recordSet = set()
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
    def findTotalHits(self):
        for rec in self.recordSet:
            self.totalHits = max(rec.hitNumber, self.totalHits) 
            
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
        self.everAddedToCart()
        self.everRemovedFromCart()
        self.everWentToCheckout()
        self.everPurchased()              
                


##**************************************************************************************************************************
##**************************************************************************************************************************
###  VISITOR
##**************************************************************************************************************************
##**************************************************************************************************************************

###Implements the class "Visitor"
#####At some point, this could maybe be made into its own file. Right now it is just a collection class for PartsSessions
class Visitor(set): #inherits from class "set"
    def __init__(self, fullVisitorId, firstSeen = datetime.datetime(1900,1,1), addedToCart = False, purchased = False):
        self.fullVisitorId = fullVisitorId
        self.firstSeen = firstSeen ##Initialized to Jan 1, 1900 unless otherwise specified.
        
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
        self.aveTimeBetweenSess = 0 ##findAveTimeBetweenSession()
        self.minTimeBetweenSess = 0 ##findMinTimeBetweenSession()

##-----------------------------------------------------------------------------        
    def __str__(self):
        return "fullVisitorId: {0}, firstSeen: {1}, Number of Sessions: {2}".format(self.fullVisitorId,
                               self.firstSeen, self.totalNumSessions())


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
        stopTimes =  [sess.endTimePOSIX for sess in self]
                
        if(len(stopTimes) > 1):  ####If stopTimes <= 1, then  the aveTimeBetweenSess = 0 is correct as hard coded. 
           
            stopTimes.sort()###Sorts in place.
            gapTimes = [np.diff(stopTimes)- sess.totalTime for sess in self]
            ##### Find the difference bewteen the session end times. Then chop off the session time. 
            ##### Results in the gap between the beginning and the end. 
            
            self.aveTimeBetweenSess = np.mean(gapTimes)        
            
            return(self.aveTimeBetweenSess)
        
        else:
            return(0)


##-----------------------------------------------------------------------------        
    def findMinTimeBetweenSession(self):
       stopTimes =  [sess.endTimePOSIX for sess in self]
               
       if(len(stopTimes) > 1):  ####If stopTimes <= 1, then  the minTimeBetweenSess = 0 is correct as hard coded. 
          
           stopTimes.sort()###Sorts in place.
           gapTimes = [np.diff(stopTimes)- sess.totalTime for sess in self]
           
           
           self.minTimeBetweenSess = np.min(gapTimes)
           
           return(self.minTimeBetweenSess)
       
       else:
           return(0)   
    

##-----------------------------------------------------------------------------      
    def everPurchased(self):
        
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
    def everAddedToCart(self):
        
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
    def finalVisitorGather(self):  #Update all values for the visitor as necessary. 
       
        print("Doing final Visitor gather on: {0}".format(self))
        self.findAveTimeBetweenSession()
        self.findMinTimeBetweenSession()
        self.everAddedToCart()
        self.everRemovedFromCart()
        self.everWentToCheckout()
        self.everPurchased()
        
        













