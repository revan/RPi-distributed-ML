import requests
import numpy as np
import sys
import csv
import math
import os
import matplotlib.pyplot as plt
from sklearn import svm
from clustermessaging.Messager import Messager
from threading import Lock
from sklearn.decomposition import PCA
import time

import pprint

pp = pprint.PrettyPrinter()

SERVER_URL = 'http://162.243.59.63:58982/' if 'ON_DEVICE' in os.environ else 'http://127.0.0.1:8000/'

def mse(preds,actuals):
    return np.mean((preds-actuals)**2)

def rss_gradient(w,X,y):
    # print("w shape = {0}".format(w.shape))
    # print("X shape = {0}".format(X.shape))
    # print("y shape = {0}".format(y.shape))

    m = float(y.shape[0])
    b = np.dot(X,w)
    # print("b shape = {0}".format(b.shape))
    a = (b - y)
    return (1/m) * np.dot(X.T,a)
 
def rss_error(w,X,y):
    m = float(y.shape[0])
    # First (1/m) is to help algorithm converge faster for larger data sets
    # Second(1/m) is associated with the average in the rest of the expression
    return (1/(2*m)) * np.dot((np.dot(X,w)-y).T,np.dot(X,w)-y)

def update_learning_rate(learning_rate,old_w,new_w,X,y):

    last_error = rss_error(old_w,X,y)
    current_error = rss_error(new_w,X,y)
    if current_error < last_error:
        return (learning_rate * 1.05), new_w
    elif current_error >= last_error:
        return (learning_rate * .5), old_w

def read_data(train_file,test_file,ID,nodes):
    # Read in the training data
    train = np.loadtxt(fname=train_file,dtype=float,delimiter=",",skiprows=1)
    y_train = train[:,4]
    x_train = np.delete(train,4,1)

    # Read in the test data
    test = np.loadtxt(fname=test_file,dtype=float,delimiter=',',skiprows=1)
    y_test = test[:,4]
    x_test = np.delete(test,4,1)

    n,m = x_train.shape # rows and columns of x_train. Corresponds to training samples and parameters respectively
    if nodes == 0:
        division = n
    else:
        division = math.floor(n/nodes)

    # This node's portion of the data
    x_train = x_train[(division*(ID-1)):(division*(ID)),:]

    y_train = y_train[(division*(ID-1)):(division*(ID))]


    n,m = x_train.shape # rows and columns of x_train. Corresponds to training samples and parameters respectively
    if nodes == 0:
        division = n
    else:
        division = math.floor(n/nodes)

    # This node's portion of the data
    x_test = x_test[(division*(ID-1)):(division*(ID)),:]

    y_test = y_test[(division*(ID-1)):(division*(ID))]

    return x_train, y_train, x_test, y_test

m = Messager()
m.registerCallbackSync()
m.start()

while True:
    requests.delete(SERVER_URL + '/classifier_stream/').text
    # if len(sys.argv) != 5:
    # 	print("Usage: python svm.py <training_data_file> <test_data_file> <tolerance> <flower_type>")
    # 	sys.exit(1)
    # else:
    # 	train_file = sys.argv[1]
    # 	test_file = sys.argv[2]
    # 	tolerance = float(sys.argv[3])
    # 	flower_type = sys.argv[4]

    train_file = "data/setosa_train.csv"
    test_file = "data/setosa_test.csv"
    ID = int(os.environ["DEVICE_ID"])
    flower_type = "setosa"

    X_train, y_train, X_test, y_test = read_data(train_file,test_file,ID,3)

    # Create the classifier
    clf = svm.SVC(kernel='linear',C=1.0)

    # Do the learning
    clf.fit(X_train,y_train)

    # Predict
    predictions = clf.predict(X_test)

    print("The error is {0}".format(mse(predictions,y_test)))
    print("The coefficients are {0}".format(clf.coef_[:]))

    # Gradient descent for fine tuning
    nodes = len(m.getNeighbors()) + 1

    w = np.array(clf.coef_[0]).T
    learning_rate = .5
    iterations = 30

    errors_per_iteration = list()
    it = list()
    for i in range(iterations):
        # print("w shape before gradient = {0}".format(w.shape))
        print(i)
        new_w = w - (learning_rate) * rss_gradient(w,X_train,y_train)
        learning_rate, w = update_learning_rate(learning_rate,w,new_w,X_train,y_train)

        # writer.writerow(tuple([i,rss_error(w,X,y)]))
        # Send w to all neighbors, receive other nodes' w

        # print("w shape before exchange = {0}".format(w.shape))
        for recipient in m.getNeighbors().keys():
            message = {
                'weights' : w,
                'sync' : i
            }
            m.sendMessage(recipient,message)

        m.waitForMessageFromAllNeighbors(i)

        # print(w.shape[0])
        a = w.shape[0]
        vector_sum = np.zeros((a,1),dtype=float)

        # print("w shape before averaging = {0}".format(w.shape))
        for message in m.sync[i]:
            vector_sum = vector_sum + message['weights']

        vector_sum = vector_sum[0]
        size = float(len(m.sync[i]))

        w = vector_sum * (1.0 / size)
        # pp.pprint(w)
        # time.sleep(.0000001)
        # print("w shape after averaging = {0}".format(w.shape))

        # Should now have the best weight vector for setosa
        y_est = np.dot(X_test,w)

        # errors = 0
        # for i in range(len(y_est)):
        # 	if y_est[i] != y_test[i]:
        # 		errors += 1
        error = mse(y_est,y_test)
        errors_per_iteration.append(error)
        it.append(i+1)
        # writer.writerow((i,error))

        # POST error to server
        requests.post(SERVER_URL + 'classifier_error/' + str(m.getOwnName()), data={'value': error}).text


    print('Reloading topology!')
    m.resetSyncInbox()
    time.sleep(5)
    m.reloadTopology()

