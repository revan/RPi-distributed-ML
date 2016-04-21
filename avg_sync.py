import numpy as np
import time
from threading import Lock
import random
from clustermessaging.Messager import Messager
import os
import csv
from numpy import linalg as la
import pprint

pp = pprint.PrettyPrinter()

assignment = {
	"1": 6,
	"2": 9,
	"3": 12
}

# Used to deal with infinity values
MAXINT = 65535 

# Initialize lock and Messager objects
# m = Messager()
# m.registerCallbackSync()
# m.start()

# # Get list of neighbors
# neighbors = list(m.getNeighbors().keys())

ID = int(os.environ["DEVICE_ID"])
# Get value assignment
my_val = assignment[str(ID)]
# my_val = float(np.random.randint(100))
# print("Starting val is: {0}".format(my_val))

def get_adjacency_matrix(topo):
	n = len(topo)
	mat = np.zeros([n,n],dtype=float)
	for key in topo:
		edges = topo[key]
		for node in edges:
			mat[int(key)-1,int(node)-1] = 1

	return mat

def generate_stochastic_matrix(topo):
	'''
		While easy to construct, suffers from poor convergence rate.
		Averaging breaks down at large iteration counts.	
'''
	A = a^2
	n,m = A.shape

	D = np.zeros((n,n),dtype=float)
	for i in range(n):
		D[i,i] = A[i,i]

	# L is the Laplacian Matrix: D is the degree matrix, A is the adjacency matrix
	L = D + a

	W = np.zeros((n,m),dtype=float)

	for i in range(n):
		a = sum(L[i,i:n])
		b = sum(W[i,0:i])
		factor = abs(a / (1-b))

		row = L[i,i:n]
		row = row / factor

		j = i
		for value in row:
			W[i,j] = value
			W[j,i] = value
			j += 1

	return W

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
	# for recipient in m.getNeighbors().keys():
	# 	message = {
	# 		'value' : my_val,
	# 		'sync'  : i
	# 	}
	# 	# print("Sending {0} to {1} from {2}".format(my_val,recipient,ID))
	# 	m.sendMessage(recipient,message)

	# # print("Waiting for all values to arrive")
	# m.waitForMessageFromAllNeighbors(i)

	# # print("Got all values. Constructing x vector")
	# # Construct X
	# for message in m.sync[i]:
	# 	node = int(message['from'])
	# 	value = float(message['value'])

	# 	x[node-1] = value


	# print("x is {0}".format(x))
	my_val = np.dot(w,x)[0]
	print("my_val is {0}".format(my_val))
	# writer.writerow((i,my_val))

# f.close()



