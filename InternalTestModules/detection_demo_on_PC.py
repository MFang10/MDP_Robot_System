import numpy as np
import cv2

cap = cv2.VideoCapture(0) 
img_width = 640
img_height = 480
cap.set(3, img_width)
cap.set(4, img_height)

# color range
lower_black = (0,0,0)
upper_black = (255,255,90)
lower_white = (0,0,200)
upper_white = (255,20, 255)
#kernel_blur = np.ones((5,5),np.float32)/25              
kernel_morph = np.ones((5,5), np.uint8)
# cv2.Canny parameters
threshold1 = 100
threshold2 = 50

min_target_ratio = 0.05
min_triangle_ratio = 0.05
max_target_ratio = 0.50
region_ratio = 0.25

def findTriangle(region):
	contours = cv2.findContours(region, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[-2]
	for c in contours:
		if cv2.contourArea(c) < region.shape[0]*region.shape[1]*min_triangle_ratio:
			continue
		perimeter = cv2.arcLength(c, True)
		approx = cv2.approxPolyDP(c, 0.085 * perimeter, True)
		print(len(approx))
		#edges = cv2.Canny(region, threshold1, threshold2)
		#if dir == 1:
			#cv2.drawContours(img, [approx], -1, (0,0,255), 5)
		#cv2.imshow("Region", img);
		#cv2.waitKey(20)
		if len(approx) == 2:
			return True
	return False


def findDirection(img):
	height = img.shape[0]
	width = img.shape[1]
	
	y_upper = 0
	x_upper = 0
	y_left = 0
	x_left = 0
	y_lower = int((1-region_ratio)*height)
	x_lower = 0
	y_right = 0
	x_right = int((1-region_ratio)*width)

	w_horizontal = int(width)
	h_horizontal = int(region_ratio * height)
	w_vertical = int(region_ratio * width)
	h_vertical = int(height)

	region_upper = img[y_upper:y_upper+h_horizontal, x_upper:x_upper+w_horizontal]
	region_left = img[y_left:y_left+h_vertical, x_left:x_left+w_vertical]
	region_lower = img[y_lower:y_lower+h_horizontal, x_lower:x_lower+w_horizontal]
	region_right = img[y_right:y_right+h_vertical, x_right:x_right+w_vertical]

	#cv2.imshow("region", region_right)

	triangle_upper = findTriangle(region_upper)
	triangle_left = findTriangle(region_left)
	triangle_lower = findTriangle(region_lower)
	triangle_right = findTriangle(region_right)

	if triangle_upper :
		if triangle_left:
			if triangle_lower:
				print("Right")
				return "Right"
			elif triangle_right:
				print("Down")
				return "Down"
		elif triangle_right and triangle_lower:
			print("Left")
			return "Left"
	elif triangle_lower and triangle_left and triangle_right:
		print("Up")
		return "Up"
	else:
		print("No arrow")
		return "No arrow"



while True:
	ret,frame = cap.read() 
	# hsv_max: 255
	hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
	mask = cv2.inRange(hsv, lower_black, upper_black)
	mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel_morph)
	mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel_morph)
	# find contours
	contours = cv2.findContours(mask.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[-2]
	contours = sorted(contours, key = cv2.contourArea, reverse=True)
	#contours = contours[1]
	#contours = sorted(contours, key = cv2.contourArea. reverse = True)
	#edges = cv2.Canny(mask, threshold1, threshold2)
	crop_img = None
	crop_img2 = frame
	result_contour = None
	x,w,y,h = 0,0,0,0
	result = ""

	for c in contours:
		if cv2.contourArea(c) < img_width*img_height*min_target_ratio or cv2.contourArea(c) > img_width*img_height*max_target_ratio:
			continue
		perimeter = cv2.arcLength(c, True)
		approx = cv2.approxPolyDP(c, 0.02 * perimeter, True)
		#print(len(approx))
		if len(approx) == 7:
			result_contour = approx
			x,y,w,h = cv2.boundingRect(result_contour)
			crop_img = mask[y-5:y+h+5, x-5:x+w+5]
			result = findDirection(crop_img)
			cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)
			break

	cv2.drawContours(frame, [result_contour], -1, (0,0,255), 5)
	cv2.putText(frame, result, (x - 20, y - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2, cv2.LINE_AA)
	cv2.imshow("Frame", frame)

	if cv2.waitKey(50) == 27:
		break
	
#print(up, down, left, right)
cv2.destroyAllWindows()
cap.release()








