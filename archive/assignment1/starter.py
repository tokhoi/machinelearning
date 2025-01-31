import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt

 #object for saving performance data every iteration in grad descent
class Performance:
    def __init__(self, iterations): #needed to initialize arrays
        self.iterations = iterations
        self.errorTrain = np.zeros(iterations)*np.nan
        self.errorValid = np.zeros(iterations)*np.nan
        self.errorTest = np.zeros(iterations)*np.nan
        self.trainSetAcc = np.zeros(iterations)*np.nan
        self.validSetAcc = np.zeros(iterations)*np.nan
        self.testSetAcc = np.zeros(iterations)*np.nan
        
        
def loadData():
    with np.load('notMNIST.npz') as data :
        Data, Target = data ['images'], data['labels']
        posClass = 2
        negClass = 9
        dataIndx = (Target==posClass) + (Target==negClass)
        Data = Data[dataIndx]/255.
        Target = Target[dataIndx].reshape(-1, 1)
        Target[Target==posClass] = 1 
        Target[Target==negClass] = 0
        np.random.seed(421)
        randIndx = np.arange(len(Data))
        np.random.shuffle(randIndx)
        Data, Target = Data[randIndx], Target[randIndx]
        trainData, trainTarget = Data[:3500], Target[:3500]
        validData, validTarget = Data[3500:3600], Target[3500:3600]
        testData, testTarget = Data[3600:], Target[3600:]
    return trainData, validData, testData, trainTarget, validTarget, testTarget

def MSE(W, b, x, y, reg):
    N = x.shape[0] #number of data vectors we have
    meanSquaredError = ((1/(2*N))*(np.linalg.norm((np.matmul(x, W)) + b - y)**2) 
                        + (reg/2)*(np.linalg.norm(W))**2) #I tested with test data and worked

    return meanSquaredError

    
def gradMSE(W, b, x, y, reg):
    N = x.shape[0] #number of data vectors we have   
    #Gradient with respect to b
    grad_wrtb = (1/N)*(np.matmul(x,W) + b - y).sum()  #checked with test and is correct
    #Gradient with respect to W, the last term, python adds it to every row, getting the intended effect
    grad_wrtW = (1/N)*(np.matmul(x,W) + b - y)
    grad_wrtW = np.multiply(grad_wrtW,x).sum(axis=0) + reg*W.T 
    grad_wrtW = grad_wrtW.T    

    return grad_wrtW, grad_wrtb
    
  
def crossEntropyLoss(W, b, x, y, reg):
    def _sigmoid(z):
        return 1/(1+np.exp(-z))
    
    y_predicted = _sigmoid (np.dot(x, W) + b)
    L_D = - np.mean (y * np.log(y_predicted) + (1-y) * np.log(1-y_predicted))
    
    L_W = reg/2 * (np.linalg.norm(W)**2)

    L = L_D + L_W
    return L   
    

def gradCE(W, b, x, y, reg):
    def _sigmoid(z):
        return 1/(1+np.exp(-z))
    
    y_predicted = _sigmoid (np.dot(x, W) + b)
    
    N = len(y)
    grad_W = 1/N * np.dot(x.T, y_predicted - y) + reg*W
    grad_b = np.sum(y_predicted - y)
    return grad_W, grad_b
    
def grad_descent(W, b, trainData, trainTarget, alpha, iterations, reg, error_tol, \
                 validData, validTarget, testData, testTarget, lossType='MSE'):                       
    
    perfRecord = Performance(iterations) #Make the object to store performance
    
    errorDifference = 0 #used in stopping condition
    oldError = np.inf
    
    for i in range(0, iterations):
        if lossType == 'MSE':  
            error = MSE(W, b, trainData, trainTarget, reg)
            grad_wrtW, grad_wrtb = gradMSE(W, b, trainData, trainTarget, reg)
        elif lossType == 'CE':
            error = crossEntropyLoss(W, b, trainData, trainTarget, reg)
            grad_wrtW, grad_wrtb = gradCE(W, b, trainData, trainTarget, reg)
            
        v_t_W = -grad_wrtW
        v_t_b = -grad_wrtb
        W = W + alpha*v_t_W
        b = b + alpha*v_t_b
        print('iteration = %d error = %f' % (i, error))
        
        
        #Save the per iteration errors: Error, Training Set performance, 
        #Validation Set Performance, Test Set performance
        
        perfRecord.errorTrain[i] = error
        if lossType == 'MSE':
            perfRecord.errorValid[i] = MSE(W, b, validData, validTarget, reg)
            perfRecord.errorTest[i] = MSE(W, b, testData, testTarget, reg)
        elif lossType == 'CE':
            perfRecord.errorValid[i] = crossEntropyLoss(W, b, validData, validTarget, reg)
            perfRecord.errorTest[i] = crossEntropyLoss(W, b, testData, testTarget, reg)
            
        _, perfRecord.trainSetAcc[i] ,_ = classify(W, b, trainData, trainTarget, lossType)
        _, perfRecord.validSetAcc[i] ,_ = classify(W, b, validData, validTarget, lossType)
        _, perfRecord.testSetAcc[i] ,_ = classify(W, b, testData, testTarget, lossType)
        
        errorDifference = oldError - error 
        oldError = error
        print('error diff is %f' % errorDifference)
        
        if errorDifference < error_tol:
            #Early stop, so array was initialized to be bigger than it needs to be, so resize
            perfRecord.testSetAcc.resize(i)
            perfRecord.validSetAcc.resize(i)
            perfRecord.trainSetAcc.resize(i)
            perfRecord.errorTest.resize(i)
            perfRecord.errorValid.resize(i)
            perfRecord.errorTrain.resize(i)

            print("error_tol stop condition met") 
            break

    return W, b, perfRecord
    
def buildGraph(B1=None, B2=None, eps=None, lossType=None, learning_rate=None):
    assert (lossType == 'MSE' or lossType == 'CE')
    tf.set_random_seed(421)
    
    featureVectorDim = 784
    learnRate = 0.001
    reg = 0.0
    
    #Initialize weight and bias tensors, regularizer for W
    regularizer = tf.contrib.layers.l2_regularizer(scale = reg)
    W = tf.Variable(tf.truncated_normal([featureVectorDim,1], stddev = 0.5, name = 'weight'), dtype = tf.float32)
    tf.add_to_collection(tf.GraphKeys.REGULARIZATION_LOSSES, W)
    b = tf.Variable(tf.truncated_normal([1,1], stddev = 0.5, name = 'bias'), dtype = tf.float32)
    
    #Tensors to hold the variables: data, labels and reg. 
    x = tf.placeholder(tf.float32, name = 'x')
    y = tf.placeholder(tf.float32, name = 'y')
    
    # A = y_predicted in MSE
    A = tf.matmul(x, W, name = 'predictions') + b
    
    #Loss tensor. 
    reg_variables = tf.get_collection(tf.GraphKeys.REGULARIZATION_LOSSES)
    reg_term = tf.contrib.layers.apply_regularization(regularizer, reg_variables)  
    
    if lossType == 'MSE':
        loss = reg_term + tf.losses.mean_squared_error(labels = y, predictions = A, weights = 1/2)
    elif lossType == 'CE':
        loss = reg_term + tf.losses.sigmoid_cross_entropy(multi_class_labels = y, logits = A)
        
    #optimizer
    optimizer = tf.train.AdamOptimizer(learning_rate = learnRate, beta1 = B1, beta2 = B2, epsilon = eps)
    training_op = optimizer.minimize(loss)
    
    return W, b, x, y, loss, training_op, reg
    
def classify(W, b, x, y, lossType='MSE'):
    A = np.matmul(x,W) + b
    if lossType == 'MSE':
        y_hat = A
    elif lossType == 'CE':
        y_hat = 1 / (1+np.exp(-1 * A))
        
    #threshold
    indicesPos = y_hat >= 0.5
    indicesNeg = y_hat < 0.5
    y_hat[indicesPos] = 1
    y_hat[indicesNeg] = 0

    accuracy = np.mean( y_hat == y )
    misclassIndices = y_hat != y
    print('From classify function: accuracy is %f' % accuracy)
    
    return y_hat, accuracy, misclassIndices
    
    
    
