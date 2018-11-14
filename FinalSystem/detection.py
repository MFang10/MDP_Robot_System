'''
CZ3004 MDP 18/19 S1 Group 5
Algorithm > FinalSystem > detection.py
By: Fang Meiyi

Module for Arrow Detection on Raspberry Pi.
See group project wiki for detailed illustrations.

'''


import numpy as np
import cv2
from picamera import PiCamera
from picamera.array import PiRGBArray
import time
import threading

# This module is run as a background thread in the final system
class detection_thread(threading.Thread): 
    def __init__(self):
        print("Initializing detection .. ")
        # Image dimensions
        self.img_width = 640
        self.img_height = 480
        # Camera configuration
        self.camera = PiCamera()
        self.camera.resolution = (self.img_width, self.img_height)
        self.camera.framerate = 90
        self.camera.brightness = 48
        self.camera.rotation = 0
        self.index = 0
        self.rawCapture = PiRGBArray(self.camera, size=(self.img_width, self.img_height))
        time.sleep(0.1) # Allow some time for the camera to warm up

        # Color range to define 'black'. For filtering the arrow shape.
        self.lower_black = (0,0,0)
        self.upper_black = (255,255,70)

        # For adjusting noise level in the binary image  
        self.kernel_morph = np.ones((5,5), np.uint8)

        # cv2.Canny parameters
        self.threshold1 = 100
        self.threshold2 = 50

        # Acceptance range for the arrow segments's area ratio over the frame
        self.min_target_ratio = 0.10
        self.max_target_ratio = 0.70
        self.min_triangle_ratio = 0.05

        # Parameter for cropping sub-segments from the detected arrow
        self.region_ratio = 0.25

        # Number of arrows detected since the program started.
        self.upcount = 0
        
        threading.Thread.__init__(self)
        

    # finding triangles in the sub-segments. Number of vertices computed depends on the resolution.    
    def findTriangle(self, region):
        contours = cv2.findContours(region, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[-2]
        for c in contours:
            if cv2.contourArea(c) < region.shape[0]*region.shape[1]*self.min_triangle_ratio:
                continue
            perimeter = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.085 * perimeter, True)
            if len(approx) == 2:
                return True
            return False
    

    # Find the direction of the 7-vertices segment
    # If this function outputs a direction for the segment, then the segment is an arrow
    def findDirection(self, img):
        height = img.shape[0]
        width = img.shape[1]

        # Parameter for cropping the segment
        y_upper = 0
        x_upper = 0
        y_left = 0
        x_left = 0
        y_lower = int((1-self.region_ratio)*height)
        x_lower = 0
        y_right = 0
        x_right = int((1-self.region_ratio)*width)
        
        w_horizontal = int(width)
        h_horizontal = int(self.region_ratio * height)
        w_vertical = int(self.region_ratio * width)
        h_vertical = int(height)
        
        # Crop the segment
        region_upper = img[y_upper:y_upper+h_horizontal, x_upper:x_upper+w_horizontal]
        region_left = img[y_left:y_left+h_vertical, x_left:x_left+w_vertical]
        region_lower = img[y_lower:y_lower+h_horizontal, x_lower:x_lower+w_horizontal]
        region_right = img[y_right:y_right+h_vertical, x_right:x_right+w_vertical]
        
        # Check the presence of a triangle in each cropped segment.
        triangle_upper = self.findTriangle(region_upper)
        triangle_left = self.findTriangle(region_left)
        triangle_lower = self.findTriangle(region_lower)
        triangle_right = self.findTriangle(region_right)

        '''
        if triangle_upper :
            if triangle_left:
                if triangle_lower:
                    print("Right")
                    return 4
                elif triangle_right:
                    print("Down")
                    return 2
            elif triangle_right and triangle_lower:
                print("Left")
                return 3
        elif triangle_lower and triangle_left and triangle_right:
            print("Up")
            return 1
        else:
            print("No arrow")
            return 0
        '''
        # We only need to check if the segment is an upward-pointing arrow.
        if triangle_lower and triangle_left and triangle_right:
            #print("Up")
            return 1
        return 0
    

    # Running the detection 
    def run(self):
        print("Starting detection ..")
        for frame in self.camera.capture_continuous(self.rawCapture, format='bgr', use_video_port=True):
            self.frame = self.rawCapture.array
            hsv = cv2.cvtColor(self.frame, cv2.COLOR_BGR2HSV)

            # Create a mask for filtering out non-black colours and obtain a binary image.
            mask = cv2.inRange(hsv, self.lower_black, self.upper_black)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, self.kernel_morph)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, self.kernel_morph)

            # find contours
            contours = cv2.findContours(mask.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[-2]
            crop_img = None
            result_contour = None
            
            for c in contours:
                # Check if the segment's area is similar to an arrow's
                if cv2.contourArea(c) < self.img_width*self.img_height*self.min_target_ratio or cv2.contourArea(c) > self.img_width*self.img_height*self.max_target_ratio:
                    continue
                perimeter = cv2.arcLength(c, True)
                approx = cv2.approxPolyDP(c, 0.02 * perimeter, True)
                # Check the number of vertices on the contour of the segment
                if len(approx) == 7:
                    result_contour = approx
                    #cv2.drawContours(self.frame, [result_contour], -1, (0,0,255), 5) ##**********uncomment to draw arrow contour*******
                    # Get the bounding box of the detected segment
                    x,y,w,h = cv2.boundingRect(result_contour)
                    crop_img = mask[y-5:y+h+5, x-5:x+w+5]
                    
                    dir = self.findDirection(crop_img) - 1
                    if not dir == -1:
                        self.upcount += 1
                        self.index += 1
                        # save the detected image
                        cv2.imwrite("image" + str(self.index) + ".png", self.frame)                  
                    #cv2.rectangle(self.frame,(x,y),(x+w,y+h),(0,255,0),2) ##***************uncomment to draw bounding box*****************
                    break

            #cv2.imshow("Frame", self.frame)
            cv2.waitKey(1) & 0xFF
            self.rawCapture.truncate(0)

    
    # Return the current number of arrows detected         
    def get_res(self):
        return self.upcount
    
	
    def finish(self):
        cv2.destroyAllWindows()
        self.cap.release()
        

