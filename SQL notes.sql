
####################################################################################################
## base queries from Keith

SELECT
  date,
  hits.item.productSKU AS productSKU,
  hits.item.productName AS productName,
  hits.item.itemQuantity AS quantity,
  hits.item.itemRevenue/1000000 AS Revenue,
  hits.item.currencyCode AS currency,
FROM
  TABLE_DATE_RANGE([70057421.ga_sessions_],TIMESTAMP('2016-12-01'), TIMESTAMP('2016-12-31'))
WHERE
  hits.item.productSKU IS NOT NULL
LIMIT
  500


SELECT
	date,
	totals.timeonsite,
	fullVisitorId,
	visitId,
	trafficSource.source,
	hits.hitNumber
from
	TABLE_DATE_RANGE([70057421.ga_sessions_], TIMESTAMP('2016-12-01'), TIMESTAMP('2016-12-31'))
where 
	hits.type = 'PAGE' ## what does this mean?
limit
	100


########################################################################################################


SELECT
	date,
	max(CASE WHEN hits.customdimensions.index = 1 THEN hits.customdimensions.value END) as cwsid,
	fullVisitorId,
	visitId,
	totals.pageviews as pageViews
	hits.transaction.transactionId AS txn_id,
	hits.product.productSKU AS sku,
	hits.product.productQuantity AS qty,
	hits.product.productRevenue/1000000 AS rev,
	hits.item.currencyCode AS currency
FROM
	TABLE_DATE_RANGE([70057421.ga_sessions_], TIMESTAMP('2017-01-22'), TIMESTAMP('2017-04-24'))
WHERE
	hits.product.productSKU IS NOT NULL
	AND hits.product.productQuantity IS NOT NULL
	AND hits.transaction.transactionId IS NOT NULL
--LIMIT
--	100


SELECT date,
max(CASE WHEN hits.customdimensions.index = 1 THEN hits.customdimensions.value END) as cwsid,
fullVisitorId,
visitId,
visitStartTime,
totals.timeOnSite AS timeOnSite,
geoNetwork.city AS city, 
geoNetwork.latitude as latitude,
geoNetwork.longitude AS longitude,
hits.product.productRevenue/1000000 AS rev,
hits.item.currencyCode AS currency,
trafficSource.source as source,
trafficSource.medium as medium,
trafficSource.keyword as keyword,
max(hits.hitNumber) AS hitNumber,
max(CASE WHEN hits.eCommerceAction.action_type == '3' THEN 1 ELSE 0 END) AS added_to_cart,
max(CASE WHEN hits.eCommerceAction.action_type == '4' THEN 1 ELSE 0 END) AS removed_from_cart,
max(CASE WHEN hits.eCommerceAction.action_type == '5' THEN 1 ELSE 0 END) AS went_to_checkout,
max(CASE WHEN hits.eCommerceAction.action_type == '6' THEN 1 ELSE 0 END) AS completed_purchase
FROM FLATTEN(
(SELECT date,
fullVisitorId,
visitId,
visitNumber,
visitStartTime,
totals.timeOnSite,
geoNetwork.city,
hits.customDimensions.index,
hits.customDimensions.value,
hits.product.productRevenue,
hits.item.currencyCode,
geoNetwork.latitude,
geoNetwork.longitude,
hits.eCommerceAction.action_type,
hits.hitNumber,
trafficSource.keyword,
trafficSource.source,
trafficSource.medium
FROM TABLE_DATE_RANGE([70057421.ga_sessions_], TIMESTAMP('2017-01-05'), TIMESTAMP('2017-07-05'))), hits.product)
WHERE hits.item.currencyCode == "USD" 
GROUP BY date,
fullVisitorId,
visitId,
visitStartTime,
timeOnSite,
city,
latitude,
longitude,
rev,
currency,
source,
medium,
keyword
HAVING cwsid <> "" AND cwsid <> "null" AND timeOnSite IS NOT NULL AND hitNumber IS NOT NULL AND (added_to_cart+removed_from_cart+went_to_checkout+completed_purchase) > 0
ORDER BY cwsid,
visitStartTime,
hitNumber
--LIMIT
--	100






# number of user interactions before a purchase
SELECT one.hits.item.productName AS product_name, product_revenue, ( sum_of_hit_number / total_hits ) AS avg_hit_number
FROM (
  SELECT hits.item.productName, SUM(hits.hitNumber) AS sum_of_hit_number, SUM( hits.item.itemRevenue ) AS product_revenue
  FROM (TABLE_DATE_RANGE([6191731.ga_sessions_], TIMESTAMP('2016-12-01'), TIMESTAMP('2016-12-31'))) 
  WHERE hits.item.productName IS NOT NULL
    AND totals.transactions>=1
  GROUP BY hits.item.productName
  ORDER BY sum_of_hit_number DESC ) as one
JOIN (
  SELECT hits.item.productName, COUNT( fullVisitorId ) AS total_hits
  FROM (TABLE_DATE_RANGE([6191731.ga_sessions_], TIMESTAMP('2016-12-01'), TIMESTAMP('2016-12-31'))) 
  WHERE hits.item.productName IS NOT NULL
    AND totals.transactions>=1
  GROUP BY hits.item.productName ) as two
ON one.hits.item.productName = two.hits.item.productName
ORDER BY product_revenue DESC





SELECT
	date,
	fullVisitorId,
	visitId,
	trafficSource.source,
	sum(hits.hitNumber) AS hitNumber,
	sum(totals.timeonsite) as timeonsite,
	sum(case when hits.eCommerceAction.action_type == '3' then 1 else 0 end) as added_to_cart, 
	sum(case when totals.transactions > 0 then 1 else 0 end) as completed_txn ## maybe we just want the totals.transaction value here?
FROM
	TABLE_DATE_RANGE([70057421.ga_sessions_], TIMESTAMP('2016-12-01'), TIMESTAMP('2016-12-31'))
WHERE
	hits.item.productSKU IS NOT NULL
LIMIT
	100



SELECT
	date AS date,
	fullVisitorId AS fullVisitorId,
	visitId AS visitId,
	trafficSource.source AS source,
	trafficSource.medium AS medium,
	hits.page.searchKeyword AS searchKeyword,
	sum(hits.hitNumber) AS hitNumber,
	sum(totals.timeonsite) as timeonsite,
	sum(CASE WHEN hits.eCommerceAction.action_type == '3' THEN 1 ELSE 0 END) AS added_to_cart, 
	sum(CASE WHEN totals.transactions > 0 THEN 1 ELSE 0 END) AS completed_txn 
FROM
	TABLE_DATE_RANGE([70057421.ga_sessions_], TIMESTAMP('2016-12-01'), TIMESTAMP('2016-12-31'))
GROUP BY
	date,
	fullVisitorId,
	visitId,
	trafficSource.source,
	trafficSource.medium,
	hits.page.searchKeyword
LIMIT
	100


	SELECT
	date,
	fullVisitorId,
	visitId,
	hits.transaction.transactionId AS txn_id,
	hits.item.productSKU AS sku,
	hits.item.itemQuantity AS qty,
	hits.item.itemRevenue/1000000 AS rev,
	hits.item.currencyCode AS currency
FROM
	TABLE_DATE_RANGE([70057421.ga_sessions_], TIMESTAMP('2017-01-22'), TIMESTAMP('2017-04-24'))
WHERE
	hits.item.productSKU IS NOT NULL
LIMIT
	500
	
	
	
################################################################################################################################
	########################################################################################################
	
	## FROM HERE ON ARE MY QUERIES. MODIFIED FROM PREVIOUS QUERIES ABOVE. IMPLEMENTING SOME FIXES. 
	
	########################################################################################################
	########################################################################################################
	


SELECT	
	fullVisitorId AS fullVisitorId,
	sum(CASE WHEN hits.eCommerceAction.action_type == '3' THEN 1 ELSE 0 END) AS added_to_cart, 
	sum(CASE WHEN hits.eCommerceAction.action_type == '6' THEN 1 ELSE 0 END) AS completed_txn, 
FROM
	TABLE_DATE_RANGE([70057421.ga_sessions_], TIMESTAMP('2017-1-22'), TIMESTAMP('2017-4-24'))
GROUP BY
	fullVisitorId,
  HAVING added_to_cart == completed_txn; ####Should be empty. How can someone buy something without adding to cart?
  ####I think what happens is that someone adds something to the cart but does not buy it ON THAT DAY.
  ####They then return, put some more stuff in their cart maybe, and purchase it all.
  

##########This query brings up some records where there was a completed purchase by a "new" user, but there is no record of them ever adding anything to their cart.
##### Who knows how that works. 
##### The only thing I can think is that a purchase/cart add is not being properly recorded. We are reliant on the person who set up the BigQuery records.  
SELECT	
  date as date,
	fullVisitorId AS fullVisitorId,
  (CASE WHEN totals.newVisits IS NOT NULL THEN 1 ELSE 0 END) AS isNewUser,
  hits.eCommerceAction.action_type
FROM
	TABLE_DATE_RANGE([70057421.ga_sessions_], TIMESTAMP('2017-1-01'), TIMESTAMP('2017-4-01'))
WHERE 
  (hits.eCommerceAction.action_type == '3' OR hits.eCommerceAction.action_type == '5') AND totals.newVisits IS NOT NULL
GROUP BY
  fullVisitorId,
  date,
  isNewUser,
  hits.eCommerceAction.action_type
ORDER BY
  fullVisitorId,
  date;
  


SELECT	
  date as date,
	fullVisitorId AS fullVisitorId,
  device.language as dl,
  (CASE WHEN totals.newVisits IS NOT NULL THEN 1 ELSE 0 END) AS isNewUser,
  hits.eCommerceAction.action_type
FROM
	TABLE_DATE_RANGE([70057421.ga_sessions_], TIMESTAMP('2017-1-01'), TIMESTAMP('2017-4-01'))
WHERE 
  (hits.eCommerceAction.action_type == '3' OR hits.eCommerceAction.action_type == '5') AND totals.newVisits IS NOT NULL
  AND  device.language != 'en-us'
GROUP BY
  fullVisitorId,
  date,
  isNewUser,
  hits.eCommerceAction.action_type,
  dl
ORDER BY
  fullVisitorId,
  date;
 


SELECT
	max(CASE WHEN hits.customdimensions.index = 1 THEN hits.customdimensions.value END) as cwsid,
	fullVisitorId,
	visitId,
	visitNumber,
	visitStartTime,
	date,
	hits.transaction.transactionId AS txn_id,
	hits.product.productSKU AS sku,
	hits.product.v2ProductCategory as product_category,
	hits.product.productQuantity AS qty,
	hits.product.productRevenue/1000000 AS rev,
	hits.item.currencyCode AS currency,
	max(hits.hitNumber) AS hitNumber,
	max(totals.timeonsite) as timeonsite,
	max(totals.pageviews) as pageviews,
FROM
	FLATTEN(
		(SELECT 
			fullVisitorId,
			visitId,
			visitNumber,
			visitStartTime,
			date,
			geoNetwork.country,
			geoNetwork.city,
			hits,
			totals
		FROM	
			TABLE_DATE_RANGE([70057421.ga_sessions_], TIMESTAMP('2017-01-01'), TIMESTAMP('2017-04-01'))), hits.customdimensions)
WHERE
	hits.transaction.transactionId IS NOT NULL AND hits.product.v2ProductCategory <> "CAT-MASTER-CATEGORY" AND hits.product.v2ProductCategory <> "Cat Category Not To Display" AND hits.product.v2ProductCategory <> "CAT-CATEGORY-NOT-TO-DISPLAY"
GROUP BY
	2,3,4,5,6,7,8,9,10,11,12,13, 14
HAVING
  timeonsite IS NOT NULL
ORDER BY
  fullVisitorId, visitId
LIMIT 14000
 
  
SELECT
date,
customDimensions.value AS customDimension,
hits.page.pagePath AS pagePath
FROM
FLATTEN(
(SELECT date, customDimensions, hits FROM TABLE_DATE_RANGE ([<project>:<dataset>.ga_sessions_],
TIMESTAMP('2013-09-10'),TIMESTAMP ('2014-06-10')))
, customDimensions)
WHERE
hits.page.pagePath CONTAINS '/helmets' 
AND customDimensions.index IN (1,2,3)  
  


########################################################################################################
########################################################################################################
This is the query in BQ that I used to get the data being used from July 10th onward (until otherwise noted).
This query is also in the PCC notes.txt file. 	
  
  
SELECT
  max(CASE WHEN hits.customdimensions.index = 1 THEN hits.customdimensions.value END) as cwsid,
  fullVisitorId,
  visitId,
  max(hits.hitNumber) AS hitNumber,
  hits.product.productSKU AS sku,
  hits.product.v2ProductCategory as product_category,
	--max(CASE WHEN hits.eCommerceAction.action_type == '1' THEN 1 ELSE 0 END) AS click_thru_product_list,
  --max(CASE WHEN hits.eCommerceAction.action_type == '2' THEN 1 ELSE 0 END) AS viewed_product_detail,
  max(CASE WHEN hits.eCommerceAction.action_type == '3' THEN 1 ELSE 0 END) AS added_to_cart,
  max(CASE WHEN hits.eCommerceAction.action_type == '4' THEN 1 ELSE 0 END) AS removed_from_cart,
  max(CASE WHEN hits.eCommerceAction.action_type == '5' THEN 1 ELSE 0 END) AS went_to_checkout,
  max(CASE WHEN hits.eCommerceAction.action_type == '6' THEN 1 ELSE 0 END) AS completed_purchase,
  visitNumber,
  visitStartTime,
  date,
  geoNetwork.city AS city,
  hits.product.productQuantity AS qty,
  hits.product.productRevenue/1000000 AS rev,
  hits.item.currencyCode AS currency,
  hits.transaction.transactionId AS txn_id,
  max(totals.timeonsite) AS timeonsite
FROM
	FLATTEN(
		(SELECT 
			fullVisitorId,
      visitId,
      visitNumber,
      visitStartTime,
      date,
      geoNetwork.country as country,
      geoNetwork.city,
			hits.customDimensions.index,
      hits.customDimensions.value,
      hits.transaction.transactionId,
      hits.product.productSKU,
      hits.product.v2ProductCategory,
      hits.product.productQuantity,
      hits.product.productRevenue,
      hits.item.currencyCode,
      totals.timeonsite,
      hits.eCommerceAction.action_type,
      hits.hitNumber
		FROM	
			TABLE_DATE_RANGE([70057421.ga_sessions_], TIMESTAMP('2017-01-05'), TIMESTAMP('2017-07-05'))), hits.product)
WHERE
  country == "United States" AND hits.product.productSKU IS NOT NULL and hits.product.productQuantity IS NOT NULL
GROUP BY
  fullVisitorId,visitId,
  txn_id,
  sku, 
  visitNumber,
  visitStartTime,
  date,
  city,
  product_category,
  qty,
  rev,
  currency 
HAVING
  cwsid !="" AND cwsid !="null" AND timeonsite IS NOT NULL AND hitNumber IS NOT NULL 
    AND (added_to_cart+removed_from_cart+went_to_checkout+completed_purchase) > 0
ORDER BY
  cwsid, sku, visitStartTime, hitNumber
LIMIT 14000  
  

###########################################################################
Fresh data set for machine learning purposes. ADD some more to this. Get the traffic medium and source type data. Longitude, latitude


SELECT fullVisitorId,
visitId,
max(CASE WHEN hits.customdimensions.index = 1 THEN hits.customdimensions.value END) as cwsid,
max(hits.hitNumber) AS hitNumber,
max(CASE WHEN hits.eCommerceAction.action_type == '1' THEN 1 ELSE 0 END) AS click_thru_product_list,
max(CASE WHEN hits.eCommerceAction.action_type == '2' THEN 1 ELSE 0 END) AS viewed_product_detail,
max(CASE WHEN hits.eCommerceAction.action_type == '3' THEN 1 ELSE 0 END) AS added_to_cart,
max(CASE WHEN hits.eCommerceAction.action_type == '4' THEN 1 ELSE 0 END) AS removed_from_cart,
max(CASE WHEN hits.eCommerceAction.action_type == '5' THEN 1 ELSE 0 END) AS went_to_checkout,
max(CASE WHEN hits.eCommerceAction.action_type == '6' THEN 1 ELSE 0 END) AS completed_purchase,
visitStartTime,
totals.timeOnSite AS timeOnSite,
date,
geoNetwork.city AS city,
hits.product.productRevenue/1000000 AS rev,
hits.item.currencyCode AS currency,
geoNetwork.latitude as latitude,
geoNetwork.longitude AS longitude,
trafficSource.source AS source,
trafficSource.medium AS medium
FROM FLATTEN(
(SELECT 
fullVisitorId,
visitId,
visitNumber,
visitStartTime,
totals.timeOnSite,
date,
geoNetwork.country as country,
geoNetwork.city,
hits.customDimensions.index,
hits.customDimensions.value,		  
hits.product.productRevenue,
hits.item.currencyCode,
geoNetwork.latitude,
geoNetwork.longitude,
hits.eCommerceAction.action_type,
hits.hitNumber,
trafficSource.source,
trafficSource.medium
FROM TABLE_DATE_RANGE([70057421.ga_sessions_], TIMESTAMP('2017-01-05'), TIMESTAMP('2017-07-05'))), hits.product)
WHERE  country == "United States" AND hits.item.currencyCode == "USD" 
GROUP BY fullVisitorId,
visitId, 
visitStartTime,
date,
city,
latitude,
longitude,
rev,
currency,
source,
medium,
timeOnSite
HAVING
cwsid <> "" AND cwsid <> "null" AND timeOnSite IS NOT NULL AND hitNumber IS NOT NULL AND (added_to_cart+removed_from_cart+went_to_checkout+completed_purchase) > 0
ORDER BY cwsid,
visitStartTime,
hitNumber
LIMIT 14000  
	
	
####################################################################################################################
####################################################################################################################

####################################################################################################################
####################################################################################################################
This is the Tableau custom query I used to get my data for visitor aggregation. 	
	
SELECT date,
max(CASE WHEN hits.customdimensions.index = 1 THEN hits.customdimensions.value END) as cwsid,
fullVisitorId,
visitId,
visitStartTime,
totals.timeOnSite AS timeOnSite,
totals.pageviews AS pageviews,
geoNetwork.city AS city, 
geoNetwork.latitude as latitude,
geoNetwork.longitude AS longitude,
hits.product.productRevenue/1000000 AS rev,
hits.product.productQuantity AS qty,
hits.item.currencyCode AS currency,
hits.item.productName AS productName,
hits.product.v2ProductCategory AS productCategory,
trafficSource.source as source,
trafficSource.medium as medium,
trafficSource.keyword as keyword,
max(hits.hitNumber) AS hitNumber,
max(CASE WHEN hits.eCommerceAction.action_type == '3' THEN 1 ELSE 0 END) AS added_to_cart,
max(CASE WHEN hits.eCommerceAction.action_type == '4' THEN 1 ELSE 0 END) AS removed_from_cart,
max(CASE WHEN hits.eCommerceAction.action_type == '5' THEN 1 ELSE 0 END) AS went_to_checkout,
max(CASE WHEN hits.eCommerceAction.action_type == '6' THEN 1 ELSE 0 END) AS completed_purchase
FROM FLATTEN(
(SELECT date,
fullVisitorId,
visitId,
visitNumber,
visitStartTime,
totals.timeOnSite,
totals.pageviews,
geoNetwork.city,
hits.customDimensions.index,
hits.customDimensions.value,
hits.product.productRevenue,
hits.product.productQuantity,
hits.item.currencyCode,
hits.item.productName,
hits.product.v2ProductCategory,
geoNetwork.latitude,
geoNetwork.longitude,
hits.eCommerceAction.action_type,
hits.hitNumber,
trafficSource.keyword,
trafficSource.source,
trafficSource.medium
FROM TABLE_DATE_RANGE([70057421.ga_sessions_], TIMESTAMP('2017-01-05'), TIMESTAMP('2017-07-05'))), hits.product)
WHERE hits.item.currencyCode == "USD" 
GROUP BY date,
fullVisitorId,
visitId,
visitStartTime,
timeOnSite,
pageviews,
productName,
productCategory,
city,
latitude,
longitude,
rev,
qty,
currency,
source,
medium,
keyword
HAVING cwsid <> "" AND cwsid <> "null" AND timeOnSite IS NOT NULL AND hitNumber IS NOT NULL AND (added_to_cart+removed_from_cart+went_to_checkout+completed_purchase) > 0
ORDER BY cwsid,
visitStartTime,
hitNumber	
	
	
	
	
#######################################################################################

---------------------------------------------------------------------------------------

#######################################################################################
	
SELECT date,
max(CASE WHEN hits.customdimensions.index = 1 THEN hits.customdimensions.value END) as cwsid,
fullVisitorId,
visitNumber,
totals.timeOnSite AS timeOnSite,
totals.pageviews AS pageviews,
hits.product.productRevenue/1000000 AS rev,
hits.product.productQuantity AS qty,
hits.item.currencyCode AS currency,
max(hits.hitNumber) AS hitNumber,
max(CASE WHEN hits.eCommerceAction.action_type == '6' THEN 1 ELSE 0 END) AS completed_purchase
FROM FLATTEN(
(SELECT date,
fullVisitorId,
visitNumber,
visitStartTime,
totals.timeOnSite,
totals.pageviews,
geoNetwork.city,
hits.customDimensions.index,
hits.customDimensions.value,
hits.product.productRevenue,
hits.product.productQuantity,
hits.item.currencyCode,
hits.eCommerceAction.action_type,
hits.hitNumber
FROM TABLE_DATE_RANGE([70057421.ga_sessions_], TIMESTAMP('2017-01-05'), TIMESTAMP('2017-07-05'))), hits.product)
WHERE hits.item.currencyCode == "USD" 
GROUP BY date,
fullVisitorId,
visitNumber,
visitStartTime,
timeOnSite,
pageviews,
rev,
qty,
currency
HAVING cwsid <> "" AND cwsid <> "null" AND timeOnSite IS NOT NULL AND hitNumber IS NOT NULL AND completed_purchase > 0
ORDER BY cwsid,
visitStartTime,
hitNumber	



#########################################################

SELECT date,
max(CASE WHEN hits.customdimensions.index = 1 THEN hits.customdimensions.value END) as cwsid,
fullVisitorId,
visitNumber,
visitStartTime,
sum(hits.product.productRevenue/1000000) AS totalRev,
sum(hits.product.productQuantity) AS totalQty,
hits.item.currencyCode AS currency,
max(hits.hitNumber) AS hitNumber,
max(CASE WHEN hits.eCommerceAction.action_type == '6' THEN 1 ELSE 0 END) AS completed_purchase
FROM FLATTEN(
(SELECT date,
fullVisitorId,
visitStartTime,
visitNumber,
hits.customDimensions.index,
hits.customDimensions.value,
hits.product.productRevenue,
hits.product.productQuantity,
hits.item.currencyCode,
hits.eCommerceAction.action_type,
hits.hitNumber
FROM TABLE_DATE_RANGE([70057421.ga_sessions_], TIMESTAMP('2016-01-05'), TIMESTAMP('2017-07-05'))), hits.product)
WHERE hits.item.currencyCode == "USD" 
GROUP BY date,
fullVisitorId,
visitNumber,
visitStartTime,
currency
HAVING cwsid <> "" AND cwsid <> "null"  AND hitNumber IS NOT NULL AND completed_purchase > 0
ORDER BY cwsid,
visitStartTime,
hitNumber	



########################
Pulling data down for comparing quantity versus hit number. This is at a transaction level. 
Does not seem to lead to anything significantly enlightening. 

SELECT date,
fullVisitorId,
visitId,
sum(hits.product.productRevenue/1000000) AS totalRev,
sum(hits.product.productQuantity) AS totalQty,
hits.item.currencyCode AS currency,
max(hits.hitNumber) AS hitNumber,
max(CASE WHEN hits.eCommerceAction.action_type == '6' THEN 1 ELSE 0 END) AS completed_purchase
FROM FLATTEN(
(SELECT date,
fullVisitorId,
visitId,
hits.customDimensions.index,
hits.customDimensions.value,
hits.product.productRevenue,
hits.product.productQuantity,
hits.item.currencyCode,
hits.eCommerceAction.action_type,
hits.hitNumber
FROM TABLE_DATE_RANGE([70057421.ga_sessions_], TIMESTAMP('2016-01-01'), TIMESTAMP('2017-07-21'))), hits.product)
WHERE hits.item.currencyCode == 'USD'
GROUP BY fullVisitorId,
date,
visitId,
currency
HAVING totalRev IS NOT NULL AND hitNumber IS NOT NULL AND completed_purchase > 0 AND totalQty IS NOT NULL
ORDER BY fullVisitorId, 
date,
visitId	

#################################################################################################################
I am looking into pulling down some session and transaction data that I can cluster on. Note the totals.sessionQualityDim field.

I use this query to pull session data. 

SELECT date,
fullVisitorId,
visitId,
channelGrouping,
totals.sessionQualityDim AS sessQuality,
sum(hits.product.productRevenue/1000000) AS totalRev,
sum(hits.product.productQuantity) AS totalQty,
hits.product.v2ProductCategory as product_category,
hits.item.currencyCode AS currency,
device.mobileDeviceModel,
device.deviceCategory as deviceCat,
device.browser as browser,
max(hits.hitNumber) AS hitNumber,
totals.timeOnSite as timeOnSite,
geoNetwork.latitude as latitude,
geoNetwork.longitude AS longitude,
max(CASE WHEN hits.eCommerceAction.action_type == '4' THEN 1 ELSE 0 END) AS removed_from_cart,
max(CASE WHEN hits.eCommerceAction.action_type == '6' THEN 1 ELSE 0 END) AS completed_purchase,
sum(CASE WHEN hits.eCommerceAction.action_type == '6' THEN 1 ELSE 0 END) AS num_completed_purchases
FROM FLATTEN(
(SELECT date,
fullVisitorId,
visitId,
totals.sessionQualityDim,
hits.customDimensions.index,
hits.customDimensions.value,
hits.product.productRevenue,
hits.product.productQuantity,
hits.item.currencyCode,
channelGrouping,
totals.timeOnSite,
hits.product.v2ProductCategory,
hits.eCommerceAction.action_type,
device.mobileDeviceModel,
device.deviceCategory,
device.browser,
geoNetwork.latitude,
geoNetwork.longitude,
hits.hitNumber
FROM TABLE_DATE_RANGE([70057421.ga_sessions_], TIMESTAMP('2017-07-01'), TIMESTAMP('2017-07-26'))), hits.product)
WHERE hits.item.currencyCode == 'USD' AND hits.product.v2ProductCategory LIKE '%Filters%'
GROUP BY fullVisitorId,
date,
visitId,
latitude,
longitude,
sessQuality,
product_category,
device.mobileDeviceModel,
deviceCat,
browser,
timeOnSite,
channelGrouping,
currency
HAVING hitNumber IS NOT NULL AND totalQty IS NOT NULL AND product_category <> "CAT-MASTER-CATEGORY"
AND product_category <> "Cat Category Not To Display" AND sessQuality IS NOT NULL
ORDER BY fullVisitorId, 
date,
visitId

