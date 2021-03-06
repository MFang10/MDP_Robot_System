import numpy as np

class astar():
	def __init__(self,row,col):
		self.row = row
		self.col = col
		self.map = np.zeros([row,col],dtype=np.float32)
		self.testedmtx = np.zeros([row,col],dtype=np.float32)

	def set_obstacle(self,indices):
		for index in indices:
			r, c = index
			self.testedmtx[r][c] = 1
		#print(self.testedmtx)

	def remove_obstacle(self,indices):
		for index in indices:
			r,c = index
			self.testedmtx[r][c] = 0

	def compute_path(self,start,dest):
		obst_mtx = self.testedmtx.copy()
		self.nq = node_queue()
		# distance and position of current node
		curr_node = node(None, start, 0)
		position = start
		index = 0
		
		while not ((position[0]==dest[0]) and (position[1]==dest[1])):
			# print(self.testedmtx)
			# print(position)
			if curr_node.parent is not None:
				parent_r = curr_node.parent.coor[0]
				parent_c = curr_node.parent.coor[1]
				curr_r = curr_node.coor[0]
				curr_c = curr_node.coor[1]
				# moving to north
				if curr_c == parent_c - 1:
					children = self.get_child(position, 0)
					print("facing north")
				# moving to east
				elif curr_r == parent_r + 1:
					children = self.get_child(position, 1)
					print("facing east")
				# moving to south
				elif curr_c == parent_c + 1:
					children == self.get_child(position, 2)
				# moving to west
				elif curr_r == parent_r - 1:
					children == self.get_child(position, 3)
			else:
				children = self.get_child(position, 0)

			#children = self.get_child(position)
			if (children == []):
				_, curr_node = self.nq.get()
				position = curr_node.coor
				continue
			for child in children:
				r, c = child
				self.testedmtx[r][c] = 1
			for child in children:
				dist_pass = curr_node.dist_pass
				new_dist_pass = dist_pass + self.compute_dist(position,child) # Compute actual cost to the child and set it.
				new_node = node(curr_node, child, new_dist_pass)
				dist_buff = self.compute_dist(child, dest) + new_dist_pass # Estimate the dist of the entire path through the child
				self.nq.put([dist_buff, new_node])
			_, curr_node = self.nq.get()
			position = curr_node.coor
			
		path = curr_node.trace_back()
		# print(path)
		self.testedmtx = obst_mtx
		return path

	def compute_dist(self,pt1,pt2):
		#return np.sqrt((pt1[0]-pt2[0])**2 + (pt1[1]-pt2[1])**2)
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

	def comp(self, next_pt, pt):
		if next_pt[0] - pt[0] == 1:
			return 1
		elif next_pt[0] - pt[0] == -1:
			return 3
		elif next_pt[1] - pt[1] == 1:
			return 2
		elif next_pt[1] - pt[1] == -1:
			return 0


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
					if i == len(path)-1:
						step_list.append([prev_dir, cnt])
					prev_dir = cur_dir
				i += 1

		return step_list

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