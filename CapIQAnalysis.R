
#######
library(BBmisc)
library(glmnet)
library(data.table)
library(dplyr)
library(tm)
library(readxl)
library(glmnet)
library(Amelia)
library(RColorBrewer)
library(scales)

CapIQ<- read_excel("C:/Users/reeserd2/Desktop/JSS Analysis/data/JSS_fixed_CIM_CapIQ_20170525_fixed.xlsx")[,c(11,151:162)]

names(CapIQ)

SmallCapIQ = select(CapIQ, ISWON, RoAPer:NumofEmployees)
SmallCapIQ

palette =brewer.pal(5,name="Set3")

missmap(SmallCapIQ, main = "Missing values vs observed", col = c(palette[2], palette[5]))
###The blue is the observed (not missing) values. The tan/yellow is where we have missing values. 

numberOfNA = vector(length =  158)
for(rowNum in 1:158)
{
  numberOfNA[rowNum] = sum(is.na(SmallCapIQ[rowNum,-(1:3)]))
}

numberOfNA
allNAIndices = which(numberOfNA == 10)
125/158####Almost 80% of the obesrvations are absolutely blank. No a priori information. Why so many missing values?

strongCleanedCapIQ = SmallCapIQ[-allNAIndices,]
#### This is the data set when we removed rows with only NA values. I am ignoring the `# Employees` and the `Total Revenue (mm)` columns here.

strictLogistic = glm(ISWON ~., family = "binomial" (link = "logit"), data = strongCleanedCapIQ)
summary(strictLogistic)####ALL rows of only NA removed. 
###Note that R will automatically remove the rows with ALL NA anyway. 

length(na.omit(strongCleanedCapIQ$NumofEmployees))##26
length(na.omit(strongCleanedCapIQ$Rev))##33

bothExist = which(!is.na(strongCleanedCapIQ$NumofEmployees)*!is.na(strongCleanedCapIQ$Rev))

colinear = alias(strictLogistic, partial = TRUE)

colinear$Partial
colinear$Complete
linComb = as.double(colinear$Complete)####Coeffcients for linear combination of the other variables yielding NumOfEmployees

estimatedNumEmployees = as.matrix(cbind(rep(1,33),strongCleanedCapIQ[,-c(1,13)])) %*% linComb

round(sum(estimatedNumEmployees - strongCleanedCapIQ$NumofEmployees, na.rm = TRUE), digits = 9)
###In essence this turns out to be zero. So numOfEmployees is pretty much a perfect linear combination of the other 11 variables. 

###Early work testing ElasticNet
glmnet_1_Logistic = glm(as.numeric(ISWON) ~ `# Employees` + `Total Revenue (mm)` + RoAPer + RoEPer + RoCPer + EBITDAMarginPer + EBITMarginPer +
                           CurrentRatio + QuickRatio + CashfromOpstoCurrLiab, family = "binomial", data = SmallCapIQ)
summary(glmnet_1_Logistic)



elasticNet = cv.glmnet(x=as.matrix(SmallCapIQ[c(49,50,63,80:98,139:142),-c(1, 2,3)]), 
          y=as.numeric(SmallCapIQ$ISWON[c(49,50,63,80:98,139:142)]),
          type.measure = "class", family = "binomial", alpha = 1, intercept = FALSE)
##Fitting the elastic net model. 

round(elasticNet$glmnet.fit$beta[,88],digits = 3)####Gives final non-zero coefficients. 

####With less harsh rounding of the coefficients.
glmnet_2_Logistic = glm(as.numeric(ISWON) ~  RoAPer+ RoEPer+ GrossMarginPer + EBITDAMarginPer  +EBITMarginPer+ FixedAssetTurnover+
                          CurrentRatio + QuickRatio + CashfromOpstoCurrLiab +Rev -1, family = "binomial", data = SmallCapIQ)
summary(glmnet_2_Logistic)

###With harsher rounding of the coefficients. 
glmnet_3_Logistic = glm(as.numeric(ISWON) ~  RoAPer + GrossMarginPer + EBITDAMarginPer  + FixedAssetTurnover+
                          CurrentRatio + QuickRatio + CashfromOpstoCurrLiab -1, family = "binomial", data = SmallCapIQ)
summary(glmnet_3_Logistic)



