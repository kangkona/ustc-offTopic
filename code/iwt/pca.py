#-*- coding:utf-8 -*-
from pylab import *
from numpy import *
def pca(data,nRedDim=0,normalise=1):
   
    # 数据标准化
    m = mean(data,axis=0)
    data -= m
    # 协方差矩阵
    C = cov(transpose(data))
    # 计算特征值特征向量，按降序排序
    evals,evecs = linalg.eig(C)
    indices = argsort(evals)
    indices = indices[::-1]
    evecs = evecs[:,indices]
    evals = evals[indices]
    if nRedDim>0:
        evecs = evecs[:,:nRedDim]
   
    if normalise:
        for i in range(shape(evecs)[1]):
            evecs[:,i] / linalg.norm(evecs[:,i]) * sqrt(evals[i])
    # 产生新的数据矩阵
    x = dot(transpose(evecs),transpose(data))
    # 重新计算原数据
    y=transpose(dot(evecs,x))+m
    return x,y,evals,evecs

def pca2(X):
    # Principal Component Analysis
    # input: X, matrix with training data as flattened arrays in rows
    # return: projection matrix (with important dimensions first),
    # variance and mean
    
    #get dimensions
    num_data,dim = X.shape
    
    #center data
    mean_X = X.mean(axis=0)
    for i in range(num_data):
        X[i] -= mean_X
    
    if dim>100:
        print 'PCA - compact trick used'
        M = dot(X,X.T) #covariance matrix
        e,EV = linalg.eigh(M) #eigenvalues and eigenvectors
        tmp = dot(X.T,EV).T #this is the compact trick
        V = tmp[::-1] #reverse since last eigenvectors are the ones we want
        S = sqrt(e)[::-1] #reverse since eigenvalues are in increasing order
    else:
        print 'PCA - SVD used'
        U,S,V = linalg.svd(X)
        V = V[:num_data] #only makes sense to return the first num_data
    
    #return the projection matrix, the variance and the mean
    return V,S,mean_X