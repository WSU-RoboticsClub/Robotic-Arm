import numpy as np 
import cv2
import serial
import time

ser = serial.Serial('COM4', 115200, timeout = 0)


def morphOps(thresh): 


    #create structuring element that will be used to "dilate" and "erode" image. 
    #the element chosen here is a 3px by 3px rectangle 
    erodeKernel = cv2.getStructuringElement(cv2.MORPH_RECT,(3,3)) 
    #dilate with larger element so make sure object is nicely visible 
    dilateKernel = cv2.getStructuringElement(cv2.MORPH_RECT,(8,8)) 



 
    # correct order erode then dilate 
    # erode is useful for removing small white noises 
    thresh = cv2.erode(thresh,erodeKernel,iterations=2) 
    # dilate is to increase object area, and is also 
    # useful for joining broken parts of an object
    thresh = cv2.dilate(thresh,dilateKernel,iterations=2) 


    # Other option: 
    # cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel) 
    # cv2.MORPH_OPEN is another name of 
    # erosion followed by dilation 
    # cv2.MORPH_CLOSE is the reverse of opening 
    # cv2.MORPH_GRADIENT is the different between dilation and erosion 




def searchForMovement(filteredImage, cameraFeed): 
    global xpos, ypos 


    # deep copy of the filteredImage 
    temp = np.copy(filteredImage)
    
    # Retrieves all contours 
    #contours, hierarchy = cv2.findContours(filteredImage, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE) 


    # Retrieves external contours 
    # contours here is a list of vectors 
    # each vector represent the external points of the contour so you can use 
    # it to draw strokes(lines) around the contour since you have the points 
    # the describes the perimeter of the contour 
    contours, hierarchy = cv2.findContours(temp, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) 


    # boolean if object is detected 
    objectDetected = False 


    # check if any contour is detected 
    if len(contours) > 0: 
        objectDetected = True 
    else: 
        objectDetected = False 


    # contour exist 
    if objectDetected: 
        # assume that the largest contour is the object we are looking for 
        # compute the area for each contour and add them to areas list 
        areas = [cv2.contourArea(c) for c in contours] 
        # find the index of the largest area 
        max_index = np.argmax(areas) 
        # get the vector(contour) that represent the largest area 
        largest = contours[max_index] 
        # make bounding rectangle around the largest contour then find its centroid 
        # x,y are the position, w (width), h (height) 
        x,y,w,h = cv2.boundingRect(largest) 
        # compute for the center of the contour 
        xpos = x + w/2 
        ypos = y + h/2 
        
    # x, y are now the center of the contour 
    x = xpos 
    y = ypos


    # draw some crosshairs around the object 
    cv2.circle (cameraFeed,(x,y), 20,     (0,255,0),2) 
    cv2.line   (cameraFeed,(x,y),(x,y-25),(0,255,0),2) 
    cv2.line   (cameraFeed,(x,y),(x,y+25),(0,255,0),2) 
    cv2.line   (cameraFeed,(x,y),(x-25,y),(0,255,0),2) 
    cv2.line   (cameraFeed,(x,y),(x+25,y),(0,255,0),2) 


    # write the position of the object to the screen, output x-value to serial port
    cv2.putText(cameraFeed,"Tracking object at (" + str(x)+","+str(y)+")",(x,y),1,1,(255,0,0),2) 
    if ser.isOpen():
        ser.write ("B{x},{y}\n".format (x=int(xpos), y=int(ypos)))
    #ser.write(str(100))
    #print (x)
    #print ser.readline()
    #ser.write(y)





# Main Program 


# TODO: change values here to detect different colors 
# use get_HSV.py to get minimum HSV values 
# H_MIN = 98
# H_MAX = 180
# S_MIN = 116
H_MIN = 70
H_MAX = 153
S_MIN = 102
S_MAX = 256
V_MIN = 104
V_MAX = 256


FRAME_WIDTH = 640
FRAME_HEIGHT = 480




# names on top of each window 
winNameOrig = 'Original' 
winNameHSV = 'HSV Image' 
winNameThres = 'Thresholded Image' 
winNameMorph = 'Morph Operations' 




useMorphOps = True   # TODO: set True to use erode-dilate image 
trackObjects = True  # TODO: set True to track object 


# load video or open webcam 
# argument can file video 
# 0 for default webcam 
# 1 for usb webcam 
cap = cv2.VideoCapture(0) 


# 3 horizontal pixels 
# 4 vertical pixels 
# 5 frame rate (not set here) 
cap.set(3, FRAME_WIDTH) 
cap.set(4, FRAME_HEIGHT) 


x = 0 
y = 0 


while True: 
    #s tore image to matrix 
    _, cameraFeed = cap.read() 


    # convert frame from BGR to HSV colorspace 
    HSV = cv2.cvtColor(cameraFeed,cv2.COLOR_BGR2HSV) 
    
    # filter HSV image between values and store filtered image to 
    # threshold matrix 
    threshold = cv2.inRange(HSV,(H_MIN,S_MIN,V_MIN),(H_MAX,S_MAX,V_MAX)) 
    
    # perform morphological operations on thresholded image to eliminate noise 
    # and emphasize the filtered object(s) 
    if useMorphOps: 
        morphOps(threshold) 
        
    # pass in thresholded frame to our object tracking function 
    # to find largest contour and pass the camera feed to add 
    # a centroid marker to the object detected 
    if trackObjects: 
        searchForMovement(threshold, cameraFeed) 


    # show frames in window 
    cv2.imshow(winNameThres,threshold) 
    cv2.imshow(winNameOrig,cameraFeed) 
    cv2.imshow(winNameHSV,HSV)
    
    # delay 5ms so that screen can refresh. 
    # image will not appear without this waitKey() command 
    # press 'q' to break out of loop within 5ms wait
    if cv2.waitKey(5) & 0xFF == ord('q'):
        break



# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
