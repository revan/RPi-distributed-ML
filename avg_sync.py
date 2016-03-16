import numpy as np
import time
from threading import Lock
import random
from clustermessaging.Messager import Messager
import os
import csv

# assignment = {
# 	"1": 6,
# 	"2": 9,
# 	"3": 12
# }

# Used to deal with infinity values
MAXINT = 65535 

# Initialize lock and Messager objects
m = Messager()
m.registerCallbackSync()
m.start()

# Get list of neighbors
neighbors = list(m.getNeighbors().keys())

ID = int(os.environ["DEVICE_ID"])
# Get value assignment
# my_val = assignment[str(ID)]
my_val = float(np.random.randint(100))
print("Starting val is: {0}".format(my_val))

def get_incidence_matrix(topo):
	n = len(topo)
	mat = np.zeros([n,n],dtype=int)
	for key in topo:
		edges = topo[key]
		for node in edges:
			mat[int(key)-1,int(node)-1] = 1

	return mat

def generate_stochastic_matrix(topo):

	mat = get_incidence_matrix(topo)
	# Algorithm pulled from: http://cvxr.com/cvx/examples/graph_laplacian/html/mh.html
	# unweighted Laplacian matrix
	Lunw = np.dot(mat,mat.T)
	n,m = Lunw.shape
	degrees = Lunw.diagonal()


	diag_mat = np.zeros([n,m])
	for i in range(len(degrees)):
		diag_mat[i,i] = degrees[i]

	mh_degs = np.dot(abs(mat).T,diag_mat)

	a,b = mh_degs.shape
	# Column vector of the maximum value in each row
	max_vals = np.zeros([a,1],dtype=int)

	for i in range(a):
		max_vals[i] = max(mh_degs[i])

	weights = np.divide(1,max_vals)
	# Correct for division by zero
	for i in range(a):
		if weights[i] == float('inf'):
			weights[i] = 0

	stoc_mat = np.zeros([n,n],dtype=float)
	for i in range(weights.size):
		for j in range(n):
			stoc_mat[j,i] = weights[i][0] * mat[j,i]

	return stoc_mat

def get_weights(m,ID):
	# Get stochastic matrix 
	W = generate_stochastic_matrix(m.topo)
	# print("W is {0}".format(W))

	# Get own weights
	w = W[ID-1]

	return w


w = get_weights(m,ID)
# print("w is {0}".format(w))

# Generate x vector
nodes = len(neighbors) + 1
x = np.zeros([nodes,1],dtype=float)

# Insert own value
x[ID-1] = my_val

iterations = 100
for iter in range(iterations):
	# All of the communication to neighbors
	for recipient in m.getNeighbors().keys():
		message = {
			'value' : my_val,
			'sync'  : iter
		}
		# print("Sending {0} to {1} from {2}".format(my_val,recipient,ID))
		m.sendMessage(recipient,message)

	# print("Waiting for all values to arrive")
	m.waitForMessageFromAllNeighbors(iter)

	# print("Got all values. Constructing x vector")
	# Construct X
	for message in m.sync[iter]:
		node = int(message['from'])
		value = float(message['value'])

		x[node-1] = value


	# print("w is {0}, x is {1}".format(w,x))
	my_val = np.dot(w,x)[0]
	print("my_val is {0}".format(my_val))



