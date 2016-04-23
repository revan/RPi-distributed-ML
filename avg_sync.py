import numpy as np
import time
from threading import Lock
from clustermessaging.Messager import Messager
import os
import sys

assignment = {
	"1": 5,
	"2": 10,
	"3": 29
}

def get_adjacency_matrix(topo):
	n = len(topo)
	mat = np.zeros([n,n],dtype=float)
	for key in topo:
		edges = topo[key]
		for node in edges:
			mat[int(key)-1,int(node)-1] = 1

	return mat

def generate_stochastic_matrix(topo):
	adj = get_adjacency_matrix(topo)
	n,m = adj.shape # The matrix should be square, implying that n = m

	squared = np.dot(adj,adj)
	degrees = list()
	for i in range(n):
		degrees.append(squared[i][i])

	d_max = max(degrees)

	stoc_mat = np.zeros((n,m))
	for i in range(n):
		for j in range(m):
			if i != j and adj[i][j] == 1:
				stoc_mat[i][j] = float(1/(d_max + 1))
			elif i == j:
				stoc_mat[i][j] = 1.0 - (degrees[i] / (d_max+1))

	return stoc_mat

def get_weights(topo,ID):
	# Get stochastic matrix 
	W = generate_stochastic_matrix(topo)
	print("W is {0}".format(W))

	# Get own weights
	w = W[ID-1]

	return w

if __name__ == "__main__":

	# Initialize lock and Messager objects
	m = Messager()
	# m.registerCallbackSync()
	m.start()


	# Get necessary values
	ID = int(os.environ["DEVICE_ID"])
	my_val = assignment[str(ID)]
	w = get_weights(m.topo,ID)

	# Create x vector
	nodes = len(assignment)
	x = np.zeros([nodes,1],dtype=float)
	x[ID-1] = my_val # Insert own value


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

		my_val = np.dot(w,x)[0]
		print("my_val is {0}".format(my_val))




