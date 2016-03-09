import numpy as np
import time
from threading import Lock
import random
from clustermessaging.Messager import Messager
import os

assignment = {
	"1": 6,
	"2": 9,
	"3": 12
}

ID = int(os.environ["DEVICE_ID"])
# Get value assignment
my_val = assignment[str(ID)]
# print("My val is {0}".format(my_val))

def get_incidence_matrix(topo):

	# total_edges = 0
	# total_nodes = len(topo)
	# for key in topo:
	# 	total_edges += len(topo[key])

	# mat = np.zeros([total_nodes,total_edges], dtype=int)

	# for key in topo:
	# 	edge_list = topo[key]
	# 	for node in edge_list:
	# 		mat[int(key)-1,int(node)] = 1
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

	# print(mat)
	# print(weights)

	stoc_mat = np.zeros([n,n],dtype=float)
	for i in range(weights.size):
		for j in range(n):
			stoc_mat[j,i] = weights[i][0] * mat[j,i]

	return stoc_mat

def all_vals_received(vals):
	total = 0
	for num in vals:
		if vals[num] is not None:
			total += 1

	if total == len(neighbors):
		return True
	else:
		return False

def reset_received_vals(vals):
	for key in vals:
		vals[key] = None

def callback(message,name):
	# print("Got {0} from {1}. My ID is {2}".format(message["value"],message["sender"],ID))
	global node_val_map

	if node_val_map[name] is None:
		node_val_map[name] = message['value']

	if message['rsvp']:
		print('Replying...')
		reply = {
			'value': my_val,
			'rsvp': False
		}
		m.sendMessage(name,reply)
	# elif message['rsvp'] == False:
	# 	if node_val_map[name] is None:
	# 		node_val_map[name] = message['value']

	# x[message['sender']-1] = message['value']


# Used to deal with infinity values
MAXINT = 65535 

# Initialize lock and Messager objects
lock = Lock()
m = Messager()
m.registerCallback(callback)
m.start()


# Get list of neighbors
neighbors = list(m.getNeighbors().keys())
# print("My neighbors are {0}".format(neighbors))

node_val_map = {}
for n in neighbors:
	node_val_map[n] = None

# Get stochastic matrix 
W = generate_stochastic_matrix(m.topo)
# print("The stochastic matrix is {0}".format(W))
# Get stochastic matrix 
W = generate_stochastic_matrix(m.topo)
# print("The stochastic matrix is {0}".format(W))

# Get own weights
w = W[ID-1]
# print("My weights are {0}".format(w))

# Generate x vector
nodes = len(neighbors) + 1
x = np.zeros([nodes,1],dtype=float)
# print("My x is {0}".format(x))

# Insert own value
x[ID-1] = my_val
# print("The new x is {0}".format(x))


iterations = 3

for i in range(iterations):
	# Send my_val to all neighbors
	time.sleep(1)
	# All of the communication
	for recipient in neighbors:
		message = {
			'value' : my_val,
			'rsvp'  : True
		}
		print("Sending {0} to {1} from {2}".format(my_val,recipient,ID))
		m.sendMessage(recipient,message)

	print("The node_value_map is {0}".format(node_val_map))
	
	# if not all_vals_received(node_val_map):
	# 	for recipient in neighbors:
	# 		if node_val_map[recipient] == None:
	# 			message = {
	# 				'value' : my_val,
	# 				'rsvp'  : True
	# 			}
	# 			print("Sending {0} to {1} from {2}".format(my_val,recipient,ID))
	# 			m.sendMessage(recipient,message)
				
	# Construct X
	for key in node_val_map:
		x[int(key)-1] = node_val_map[key]

	print("x is {0}".format(x))
	my_val = np.dot(w,x)[0]
	reset_received_vals(node_val_map)

# 	print("x is {0}".format(x))
# 	if all_vals_received(node_val_map):
# 		# Multiply w by own vector and update my_val
# 		my_val = np.dot(w,x)[0] # The value is inside the numpy array
# 		# x[ID-1] = my_val
# 		print('Node {0} changed its value to {1}'.format(ID,my_val))
# 		reset_received_vals(node_val_map)
# # Receive values from other nodes and place them in the vector

