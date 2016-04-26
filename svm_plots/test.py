import numpy as np
import math

def read_data(train_file,test_file,ID):
	nodes = 3
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

	print(y_train)
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

if __name__ == '__main__':
	x_train, y_train, x_test, y_test = read_data("../data/setosa_train.csv","../data/setosa_test.csv",2)

	print(x_train)
	print(y_train)
	print(x_test)
	print(y_test)