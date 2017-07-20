# -*- coding: utf-8 -*-
"""
Created on Tue Jul 18 10:36:56 2017

@author: reeserd2
"""

import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn import cluster
from sklearn.neighbors import kneighbors_graph
from sklearn.preprocessing import StandardScaler
from mpl_toolkits.mplot3d import Axes3D
from sklearn.cluster import KMeans
from sklearn import datasets

from sklearn.decomposition import PCA as sklearnPCA

from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.ensemble.partial_dependence import plot_partial_dependence, partial_dependence
from patsy import dmatrices, dmatrix



np.random.seed(0)
#%%

visitorData = pd.read_csv("C:/Users/reeserd2/Desktop/PCC Analysis/visitorData.csv")

visitorData.drop(visitorData.columns[[0,2]], axis=1, inplace=True)

# Generate datasets. We choose the size big enough to see the scalability
# of the algorithms, but not too big to avoid too long running times

#%%
hitNumber_outlier_mask = (((visitorData.medHitTotal - visitorData.medHitTotal.mean()) / visitorData.medHitTotal.std()).abs()) > 4
rev_outlier_mask = ((visitorData.medRevenuePerSess - visitorData.medRevenuePerSess.mean()) / visitorData.medRevenuePerSess.std()).abs() > 5
#no_purchase_mask = (visitorData.numOfSess) <= 1                 
                   

                    
ever_purchase_mask = (visitorData.percentSessWithPurchase) > 0                      
                   
nrow_start = visitorData.shape[0]

visitorData = visitorData[~((hitNumber_outlier_mask) | (rev_outlier_mask) )]

1.0*visitorData.shape[0] / nrow_start ####0.9994975814064566

                     
visitorData["everPurchased"] = ever_purchase_mask                    
                     
                     

#%%
colors = np.array([x for x in 'grc'])
colors = np.hstack([colors] * 20)

clustering_names = [
    'MiniBatchKMeans']#, 'AffinityPropagation', 'MeanShift',
    #'SpectralClustering', 'Ward', 'AgglomerativeClustering',
    #'DBSCAN', 'Birch']

#%%


#%%

# normalize dataset for easier parameter selection
X = StandardScaler().fit_transform(visitorData[[0,1,2,3,4,5,6,7]])



#%%


fig = plt.figure(figsize=(len(clustering_names) * 2 + 3, 9.5))
plt.subplots_adjust(left=.02, right=.98, bottom=.001, top=.96, wspace=.05,
                    hspace=.01)
##ax = Axes3D(fig, rect=[0, 0, .95, 1], elev=48, azim=134)
plot_num = 1

## estimate bandwidth for mean shift
#bandwidth = cluster.estimate_bandwidth(X, quantile=0.3)
#
## connectivity matrix for structured Ward
#connectivity = kneighbors_graph(X, n_neighbors=10, include_self=False)
## make connectivity symmetric
#connectivity = 0.5 * (connectivity + connectivity.T)

# create clustering estimators
#ms = cluster.MeanShift(bandwidth=bandwidth, bin_seeding=True)
#two_means = cluster.MiniBatchKMeans(n_clusters=2)
k_means = cluster.MiniBatchKMeans(n_clusters=3)
#ward = cluster.AgglomerativeClustering(n_clusters=2, linkage='ward',
#                                       connectivity=connectivity)
#spectral = cluster.SpectralClustering(n_clusters=2,
#                                      eigen_solver='arpack',
#                                      affinity="nearest_neighbors")
#dbscan = cluster.DBSCAN(eps=.2)
#affinity_propagation = cluster.AffinityPropagation(damping=.9,
#                                                   preference=-200)
#
#average_linkage = cluster.AgglomerativeClustering(
#    linkage="average", affinity="cityblock", n_clusters=2,
#    connectivity=connectivity)
#
#birch = cluster.Birch(n_clusters=2)
clustering_algorithms = [
    k_means]#, affinity_propagation, ms, spectral, ward, average_linkage,
    #dbscan, birch]

for name, algorithm in zip(clustering_names, clustering_algorithms):
    # predict cluster memberships
    t0 = time.time()
    algorithm.fit(X)
    t1 = time.time()
    if hasattr(algorithm, 'labels_'):
        y_pred = algorithm.labels_.astype(np.int)
    else:
        y_pred = algorithm.predict(X)

    # plot
    plt.subplot(4, len(clustering_algorithms), plot_num)
    #if i_dataset == 0:
     #   plt.title(name, size=18)
    plt.scatter(X[:, 0], X[:, 1], color=colors[y_pred].tolist(), s=10)

    if hasattr(algorithm, 'cluster_centers_'):
        centers = algorithm.cluster_centers_
        center_colors = colors[:len(centers)]
        plt.scatter(centers[:, 0],centers[:, 1], s=100, c=center_colors)
    plt.xlim(-0.3, 10)
    plt.ylim(-1.5, 9)
    plt.xticks(())
    plt.yticks(())
    plt.text(.99, .01, ('%.2fs' % (t1 - t0)).lstrip('0'),
             transform=plt.gca().transAxes, size=15,
             horizontalalignment='right')
    plot_num += 1

plt.show()


#%%
# connectivity matrix for structured Ward
connectivity = kneighbors_graph(X, n_neighbors=10, include_self=False)
#make connectivity symmetric
connectivity = 0.5 * (connectivity + connectivity.T)

##'spectral': cluster.SpectralClustering(n_clusters=3, eigen_solver='arpack', affinity="nearest_neighbors")

estimators = {'kMeans-3': KMeans(n_clusters=3),
              
              'Birch':cluster.Birch(n_clusters=3),
              'Ward': cluster.AgglomerativeClustering(n_clusters=3, linkage='ward', connectivity=connectivity)
              
             }


fignum = 1
for name, est in estimators.items():
    fig = plt.figure(fignum, figsize=(4, 3))
    plt.clf()
    ax = Axes3D(fig, rect=[0, 0, .95, 1], elev=48, azim=134)

    plt.cla()
    est.fit(X)
    
    if hasattr(est, 'labels_'):
        y = est.labels_.astype(np.int)
    else:
        y = est.predict(X)
    labels = est.labels_

    #ax.scatter(X[:, 1], X[:, 3], X[:, 7], c=labels.astype(np.float))
    #ax.scatter(visitorData.medHitTotal, visitorData.medRevenuePerSess, visitorData.percentSessWithPurchase, c=labels.astype(np.float))
    ax.scatter(visitorData.medHitTotal, visitorData.medRevenuePerSess, visitorData['medTimeBtwnSess'], c=labels.astype(np.float))
    ax.text2D(0.05, 0.95, name, transform=ax.transAxes)


    #ax.w_xaxis.set_ticklabels([])
    #ax.w_yaxis.set_ticklabels([])
    #ax.w_zaxis.set_ticklabels([])
    #ax.set_zlabel('% Purchase')
    ax.set_zlabel('TimeBetweenSess')
    ax.set_xlabel('HitNumber')
    ax.set_ylabel('Revenue')
    fignum = fignum + 1

#%%
completedPurchase, modeldata = dmatrices('everPurchased ~ hitNumber + timeonsite + \
                 C(trafficSource_medium) + C(dow) + C(searched)', visitorData)

completedPurchase = completedPurchase.ravel()

gb = GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, random_state=42)




