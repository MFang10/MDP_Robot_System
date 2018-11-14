'''
CZ3004 MDP 18/19 S1 Group 5
Algorithm > FinalSystem > fastest_path.py
Modified from online resources.

Module for Fastest Path Planning
Robot is modelled to occupy one grid.
'''

import numpy as np
import Explored

class astar():
	def __init__(self,row,col):
		self.row = row
		self.col = col
		self.map = np.zeros([row,col],dtype=np.float32)
		self.testedmtx = np.zeros([row,col],dtype=np.float32)

	# Set the explored blocks and their neighbours to obstacles.
	def set_obstacle(self):
		obstacles = []
		for i in range(Explored.EXP_MAP_ROW):
			for j in range(Explored.EXP_MAP_COL):
				if Explored.exp_map[i][j] != 1:
					obstacles.append([i, j])
					if Explored.exp_map[i][j] == 2:
						for a in range(3):
							for b in range(3):
								row = i - 1 + a
								col = j - 1 + b
								if Explored.X_MIN <= row <= Explored.X_MAX and Explored.Y_MIN <= col <= Explored.Y_MAX:
									if Explored.exp_map[row][col] == 1:
										obstacles.append([row, col])
		for index in obstacles:
			r, c = index
			self.testedmtx[r][c] = 1
		#print(self.testedmtx)


	def remove_obstacle(self,indices):
		for index in indices:
			r,c = index
			self.testedmtx[r][c] = 0


	# Compute the fastest path
	def compute_path(self,start,dest):
		obst_mtx = self.testedmtx.copy()
		self.nq = node_queue()
		# distance and position of current node
		curr_node = node(None, start, 0)
		position = start
		index = 0
		
		while not ((position[0]==dest[0]) and (position[1]==dest[1])):
			if curr_node.parent is not None:
				parent_r = curr_node.parent.coor[0]
				parent_c = curr_node.parent.coor[1]
				curr_r = curr_node.coor[0]
				curr_c = curr_node.coor[1]

				# Get the child nodes in an order that promotes straight paths
				# The order depends on the direction towards which the robot is moving
				# moving to north
				if curr_c == parent_c - 1:
					children = self.get_child(position, 0)
				# moving to east
				elif curr_r == parent_r + 1:
					children = self.get_child(position, 1)
				# moving to south
				elif curr_c == parent_c + 1:
					children == self.get_child(position, 2)
				# moving to west
				elif curr_r == parent_r - 1:
					children == self.get_child(position, 3)
			else:
				children = self.get_child(position, 0)
			
			if (children == []):
				_, curr_node = self.nq.get()
				position = curr_node.coor
				continue
			for child in children:
				r, c = child
				self.testedmtx[r][c] = 1
			for child in children:
				dist_pass = curr_node.dist_pass # actual distance from the starting point to the current node.
				new_dist_pass = dist_pass + self.compute_dist(position,child) # Compute actual cost to the child and set it.
				new_node = node(curr_node, child, new_dist_pass) # create a new node for the child
				dist_buff = self.compute_dist(child, dest) + new_dist_pass # Estimate the dist of the entire path through the child
				self.nq.put([dist_buff, new_node]) # insert the child node into the buffer in which elements are arranged in increasing total distance.
			_, curr_node = self.nq.get() # get the child that yields the lowest total distance.
			position = curr_node.coor
			
		path = curr_node.trace_back() # trace back to the starting point
		self.testedmtx = obst_mtx
		return path


	def compute_dist(self,pt1,pt2):
		return np.abs(pt1[0]-pt2[0]) + np.abs(pt1[1]- pt2[1])


	def get_child(self,pnt, parent_dir):
		result = []
		r,c = pnt
		# Order of children determined by robot movement direction. 
		if parent_dir == 0:
			neighbor_coords = [(r,c-1), (r+1, c), (r, c+1), (r-1, c)]
		elif parent_dir == 1:
			neighbor_coords = [(r+1,c), (r, c+1), (r-1, c), (r, c-1)]
		elif parent_dir == 2:
			neighbor_coords = [(r,c+1), (r-1, c), (r, c-1), (r+1, c)]
		elif parent_dir == 3:
			neighbor_coords = [(r-1,c), (r, c-1), (r+1, c), (r, c+1)]
		else:
			neighbor_coords = [(r,c-1), (r+1, c), (r, c+1), (r-1, c)]

		for element in neighbor_coords:
			row = element[0]
			col = element[1]
			if (row <= self.row -1) and (row >= 0): ## within arena
				if (col <= self.col -1) and (col >= 0):
					if not self.testedmtx[row][col]==1: ## prevent setting parent as child
						result.append([row,col])

		return result


	# Compute the direction from one point to the next
	def comp(self, next_pt, pt):
		if next_pt[0] - pt[0] == 1:
			return 1
		elif next_pt[0] - pt[0] == -1:
			return 3
		elif next_pt[1] - pt[1] == 1:
			return 2
		elif next_pt[1] - pt[1] == -1:
			return 0

	# Get the consective steps from a list of discrete steps 
	# such that the robot can move n steps at a time instead of moving step by step
	def consec_step(self, start_pt, end_pt):
		path = self.compute_path(start_pt, end_pt)
		step_list = []
		if len(path) > 0:
			i = 1
			cnt = 1
			prev_dir = None
			while i < len(path):
				if i == 1:
					prev_dir = self.comp(path[i], path[i-1])
				else:
					cur_dir = self.comp(path[i], path[i-1])
					if cur_dir == prev_dir:
						cnt += 1
					else:
						step_list.append([prev_dir, cnt])
						cnt = 1
					prev_dir = cur_dir
					if i == len(path)-1:
						step_list.append([prev_dir, cnt])
					
				i += 1

		return step_list


# Define node
class node:
	def __init__(self, parent, coor, dist_pass):
		self.parent = parent
		self.coor = coor
		self.dist_pass = dist_pass
		
	def trace_back(self):
		path = []
		path.insert(0, self.coor)
		parent = self.parent
		
		while parent!=None:
			path.insert(0, parent.coor)
			parent = parent.parent
		return path

# node_queue in increasing estimated total distance		
class node_queue:
	def __init__(self):
		self.queue = []
		
	def put(self, new_item): # new_item: [dist_buff, new_node]
		index = 0
		for item in self.queue:
			if item[0] <= new_item[0]:
				index += 1;
			else:
				break
		self.queue.insert(index, new_item)
		
	def get(self):
		item = None
		if self.queue != []:
			item = self.queue[0]
			self.queue = self.queue[1:]
		return item

if __name__=='__main__':
	fastest_path = astar(10,10)
	obstacle = [[0,2],[1,2],[2,2],[3,2],[4,2],[5,2],[3,4],[3,5],[3,6],[3,7]]
	fastest_path.set_obstacle(obstacle)
	fastest_path.compute_path([0,0],[0,9])