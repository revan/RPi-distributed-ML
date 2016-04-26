import numpy as np
import time
from clustermessaging.Messager import Messager
import os
import sys
import csv
import pprint

assignment = {
	"1": 94,
	"2": 55,
	"3": 66
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

	# Get own weights
	w = W[ID-1]

	return w

if __name__ == "__main__":

	# Parse command line options
	# usage_string = 'Usage: python avg_sync.py <assignment file> <iterations>'

	# if len(sys.argv) != 4:
	# 	print(usage_string)
	# 	sys.exit(1)
	# else:
	# 	assignment = json.load(open(sys.argv[1]))
	# 	iterations = sys.argv[2]

	# Initialize lock and Messager objects
	m = Messager()
	m.registerCallbackSync()
	m.start()

	# Get necessary values
	ID = int(os.environ["DEVICE_ID"])
	my_val = assignment[str(ID)]
	w = get_weights(m.topo,ID)

	# Create x vector
	nodes = len(assignment)
	x = np.zeros(nodes,dtype=float)
	x[ID-1] = my_val # Insert own value

	iterations = 10
	for i in range(iterations):
		# time.sleep(1)
		# All of the communication to neighbors

		for recipient in m.getNeighbors().keys():
			message = {
				'value' : my_val,
				'sync'  : i
			}
			m.sendMessage(recipient,message)

		m.waitForMessageFromAllNeighbors(i)

		# Construct X
		for message in m.sync[i]:
			node = int(message['from'])
			value = float(message['value'])

			x[node-1] = value

		my_val = np.dot(w,x)
		x[ID-1] = my_val
		print(my_val)


	sys.exit(0)


