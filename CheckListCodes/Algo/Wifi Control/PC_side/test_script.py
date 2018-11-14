def comp(pt, next_pt):
	if next_pt[0] - pt[0] == 1:
		return 3
	elif next_pt[0] - pt[0] == -1:
		return 1
	elif next_pt[1] - pt[1] == 1:
		return 0
	elif next_pt[1] - pt[1] == -1:
		return 2

def consec_step():
	#path = self.compute_path(start_pt, end_pt):
	path = [[2, 19], [2, 18], [2, 17], [2, 16], [2, 15], [2, 14], [2, 13], [3, 13], [4, 13], [5, 13], [6, 13], [6, 12], [6, 11], [6, 10], [6, 9], [6, 8], [6, 7], [6, 6], [6, 5], [6, 4], [6, 3], [7, 3], [8, 3], [9, 3], [10, 3], [10, 2], [11, 2], [12, 2], [13, 2], [14, 2]]
	step_list = []
	if len(path) > 0:
		i = 1
		cnt = 1
		prev_dir = None
		while i < len(path):
			if i == 1:
				prev_dir = comp(path[i], path[i-1])
			else:
				print("computing")
				cur_dir = comp(path[i], path[i-1])
				if cur_dir == prev_dir:
					cnt += 1
				else:
					step_list.append([prev_dir, cnt])
					cnt = 1
				prev_dir = cur_dir
			i += 1

	return step_list

alist = consec_step()
print(alist)

