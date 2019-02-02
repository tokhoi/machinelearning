# -*- coding: utf-8 -*-
import starter
import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt


#Load the data
trainData, validData, testData, trainTarget, validTarget, testTarget = starter.loadData()

#shape the data into proper dimensions and initialize some matrices
error_tol = 10**-7
#W = np.zeros((784,1)) #weight matrix
W = np.random.normal(0, 0.1, size = [784,1])
b = 0#np.zeros((3500,1)) #bias matrix
reg = 0#0.1 #regularization parameter
origTrainData = trainData
origTestData = testData
trainData = trainData.reshape([3500,784]) #train data matrix
testData = testData.reshape([145,784]) #test data matrix
validData = validData.reshape([100,784]) #validation data matrix
alpha = 0.005
epochs = 5000


#very small test data
#==============================================================================
# W = np.matrix('1;1')
# b = 1
# trainData = np.matrix('1,1; 2,2; 3,3')
# trainTarget = np.matrix('1;0;1')
# reg = 0
#==============================================================================
                              

value = starter.MSE(W, b, trainData, trainTarget, reg) #call MSE that I just implemented, but I need to check it
grad_wrtb, grad_wrtW = starter.gradMSE(W, b, trainData, trainTarget, reg)

W,b = starter.grad_descent(W, b, trainData, trainTarget, alpha, epochs, reg, error_tol)


y_hat, accuracy, misclassIndices = starter.classify(W, b, testData, testTarget)



#Old test code below
#Check classifications
#perform a classification
#positive class is C, negative is J
#==============================================================================
# letterIndex = 77;
# print('classification is %f' % (np.matmul(testData[letterIndex,:], W) + b))
# plt.imshow(origTestData[letterIndex,:,:], cmap = 'gray')
#==============================================================================


