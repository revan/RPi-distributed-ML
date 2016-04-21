import numpy as np
import time
from threading import Lock
import random
from clustermessaging.Messager import Messager
import os
import sys
import getopt
import csv
import math

# Used to deal with infinity values
MAXINT = 65535 


def arg_handler(argv):

	try:
		opts, args = getopt.getopt(argv,"hd:t:i:",["datafile=","target="])
	except getopt.GetoptError:
		usage_string = ('Usage: python gradient_descent.py'
						' -d <data file>'
						' -t <target column number>'
						' -i <iterations>')
		sys.exit(1)

	datafile = ""
	target_column = -1
	iterations = -1

	for opt, arg in opts:
		if opt == '-h':
			print('Usage: python gradient_descent.py -d <data file> -t <target column number> -l <learning rate>')
			sys.exit(0)	
		elif opt == '-d':
			datafile = arg
		elif opt == '-t':
			target_column = int(arg)
		elif opt == '-i':
			iterations = int(arg)

	return datafile, target_column, iterations

def read_data(datafile,target_column,ID,neighbors):
	# Figure out how much data to load

	# Load data
	data = np.loadtxt(open(datafile,'r'),delimiter=',',skiprows=1)

	y = data[:,target_column]
	y = y.reshape(y.shape[0],1)
	X = np.delete(data,target_column,1)
	np.insert(X,0,1,axis=1) # Accounting for the bias term
 	
	n,m = X.shape # rows and columns of X. Corresponds to training samples and parameters respectively
	division = math.floor(n/neighbors)

	# This node's portion of the data
	X = X[(division*(ID-1)):(division*(ID)),:]

	y = y[(division*(ID-1)):(division*(ID)),:]
	# Initial weight vector with random weights. 
	# We will learn the best weights with the algorithm
	w = np.zeros((m,1),dtype=float)
	num_samples = float(X.shape[0])

	return w,X,y,num_samples

def rss_gradient(w,X,y):

	m = float(y.shape[0])
	return (1/m) * np.dot(X.T,(np.dot(X,w) - y))

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

if __name__ == '__main__':
	
	# Parse command line options
	usage_string = 'Usage: python gradient_descent.py <data file> <target column number> <iterations>'

	if len(sys.argv) != 4:
		print(usage_string)
		sys.exit(1)
	else:
		datafile = sys.argv[1]
		target_column = int(sys.argv[2])
		iterations = int(sys.argv[3])

	# Initialize lock and Messager objects
	m = Messager()
	m.registerCallbackSync()
	neighbors = len(m.getNeighbors())
	# datafile, target_column, iterations = arg_handler(sys.argv[1:])

	# neighbors = 3
	ID = int(os.environ["DEVICE_ID"])
	w, X, y, num_samples = read_data(datafile,target_column,ID,neighbors)
	learning_rate = .5


	import csv
	test = open("test.csv","w")
	writer = csv.writer(test)

	tolerance = float(.000001)
	# i = 0
	# error_difference = 10000000
	for i in range(iterations):
		# old_error = rss_error(w,X,y)
		# old_w = w
		new_w = w - (learning_rate) * rss_gradient(w,X,y)
		learning_rate, w = update_learning_rate(learning_rate,w,new_w,X,y)

		# writer.writerow((i,w[0],w[1],w[2],w[3]))
		print(i,w[0])


		# Send w to all neighbors, receive other nodes' w 

		for recipient in m.getNeighbors().keys():
			message = {
				'weights' : w,
				'sync' : i
			}
			print("Sending weight vector from {0} to {1}".format(ID,recipient))
			m.sendMessage(recipient,message)

		m.waitForMessageFromAllNeighbors(i)

		print("Now we can average")
		# n,m = w.shape
		# vector_sum = np.zeros((n,1),dtype=float)

		# for message in m.sync[i]:
		# 	vector_sum = vector_sum + message['weights']

		# size = float(len(m.sync[i]))

		# w = vector_sum * (size)


		# if not np.array_equal(w,old_w):
		# 	new_error = rss_error(w,X,y)
		# 	error_difference = abs(new_error - old_error)

		# i += 1
	test.close()
	# print("{0}, {1}, {2}".format(i,w[0],new_error))

