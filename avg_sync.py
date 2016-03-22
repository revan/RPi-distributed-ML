import numpy as np
import time
from threading import Lock
import random
from clustermessaging.Messager import Messager
import os
import csv

assignment = {
	"1": 6,
	"2": 9,
	"3": 12
}

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

	# incidence_matrix = get_incidence_matrix(topo)

	# # n and m should be equal
	# n,m = incidence_matrix.shape

	# stochastic_matrix = np.random.rand(n,m)

	# # Element-wise multiplication 
	# stochastic_matrix = np.multiply(incidence_matrix,stochastic_matrix)

	# # Normalizes each column
	# for i in range(n):
	# 	stochastic_matrix[:,i] = stochastic_matrix[:,i] / sum(stochastic_matrix[:,i])

	# return stochastic_matrix

	# Algorithm pulled from: http://cvxr.com/cvx/examples/graph_laplacian/html/mh.html
	# unweighted Laplacian matrix
	mat = get_incidence_matrix(topo)
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
	print("W is {0}".format(W))

	# Get own weights
	w = W[ID-1]

	return w

w = get_weights(m,ID)
# print("w is {0}".format(w))

# Generate x vector
nodes = len(m.topo)
x = np.zeros([nodes,1],dtype=float)
# print("x is {0}".format(x))

# Insert own value
x[ID-1] = my_val

# f = open("{0}.csv".format(ID),'w')
# writer = csv.writer(f)


iterations = 20
for i in range(iterations):
	# All of the communication to neighbors
	for recipient in m.getNeighbors().keys():
		message = {
			'value' : my_val,
			'sync'  : i
		}
		# print("Sending {0} to {1} from {2}".format(my_val,recipient,ID))
		m.sendMessage(recipient,message)

	# print("Waiting for all values to arrive")
	m.waitForMessageFromAllNeighbors(i)

	# print("Got all values. Constructing x vector")
	# Construct X
	for message in m.sync[i]:
		node = int(message['from'])
		value = float(message['value'])

		x[node-1] = value


	# print("x is {0}".format(x))
	my_val = np.dot(w,x)[0]
	print("my_val is {0}".format(my_val))
	# writer.writerow((i,my_val))

# f.close()



