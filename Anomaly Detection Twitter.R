
##### Detecting anomalies in univariate data. 
##### Applications to time series. 

#devtools::install_github("twitter/AnomalyDetection")
library(AnomalyDetection)


data(raw_data)
tsLength = nrow(raw_data) 

#multipliers = abs(rnorm(tsLength,mean=1, sd = 0.65))
#raw_data[,2] = raw_data[,2]*multipliers 
res = AnomalyDetectionTs(raw_data, max_anoms=0.05, 
                         direction='both', plot=TRUE)
res$plot



