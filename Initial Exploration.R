##### JSS initial code. 
install.packages("tm")
library(glmnet)
library(data.table)
library(dplyr)
library(tm)

JSS_fixed <- fread("P:/JSS Analysis/data/JSS_fixed_20170518.csv")

#####What does the data look like? ##There seems to be a good deal of missing data and sporadics. 

sum(is.na(JSS_fixed$SIGNING_COMMERCIAL_MANAGER__C))/158#### 38%
sum(is.na(JSS_fixed$INITIAL_IMPLEMENTATION_MANAGER__C))/158 ### 92%
sum(is.na(JSS_fixed$IMPLEMENTATION_MANAGER__C))/158 ### 53%
sum(is.na(JSS_fixed$Customer))/158 ### NONE
sum(is.na(JSS_fixed$LEADSOURCE))/158 ### 51%

sum(table(JSS_fixed$LEADSOURCE)) ###Nearly half of the entries for LEADSOURCE have no record. 

sum(is.na(JSS_fixed$REASON__C))/158 ### 74%
sum(is.na(JSS_fixed$`EQUIPMENT-WL`))/158 ### 65%

JSS_fixed$EQUIPMENT_TYPE__C


table(JSS_fixed$OPPORTUNITY_DISTRICT__C)
(table(JSS_fixed$`State_Ab Hybrid`))
(table(JSS_fixed$`BILLINGSTATECODE`))
(table(JSS_fixed$DEALER_STATUS__C))
(table(JSS_fixed$CAT_CHALLENGES__C))####Diverse. 

sum(is.na(JSS_fixed$CONTRACT_DURATION__C))/158 ### 80% That's not good. And is it even independent from ISWON?

JSS_fixed$CONTRACT_DURATION__C[is.na(JSS_fixed$CONTRACT_DURATION__C)] = 0
sum((JSS_fixed$CONTRACT_DURATION__C > 0)* JSS_fixed$ISWON)
sum(JSS_fixed$ISWON)
sum(JSS_fixed$CONTRACT_DURATION__C > 0)
##### Contract Duration seems to be somehow independent from ISWON. 
### It is entirely unlcear how Contract Duration is at all ACTUALLY meaningful as we have it. 
sum(is.na(JSS_fixed$EQUIPMENT_TYPE__C))/158 ####  58% missing.....not catestrophic. 


grepl("77[2-9]|78[0-5]|988|989|99[0-2]","781")#####This abstruse regex filters for text containing 772-785 or 988-992

hasLoadORHaul = grepl("77[2-9]|78[0-5]|988|989|99[0-2]",JSS_fixed$EQUIPMENT_TYPE__C)##Has load/haul equiptment.  

JSS_withHaul = cbind(JSS_fixed, hasLoadORHaul)



