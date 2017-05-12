import cv2
import numpy
import time


# read some RGB values from html color picker website, e.g. magenta - R: 237 G: 37 B: 126
#then discarded the above because values were out of whack!


# setting lower and upper bounds in hsv for colors, list has string for each color, lists of lower and upper hsv value bounds 
#ended up sticking with only two colors to simplify the task and get something working

colors = [['magenta', [[140, 50, 50], [179, 200, 200]]],
          ['gold', [[10, 174, 75], [40, 250, 150]]],
          ['red', [[0, 175, 50], [20, 255, 200]]]]

def find_color(image, colors):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV) #test with BGR2HSV

    # list for holding names and location of colors detected, returns empty with no color
    found = []

    for color, bound in colors:
        # lower bound for values of color palette sliders/bars for each color
        lower = numpy.array(bound[0])

        # upper bound for values of color palette sliders/bars
        upper = numpy.array(bound[1])
 
        # mask out pixels that do not match 
        mask = cv2.inRange(hsv, lower, upper)
        #initially thought that maybe the mask function is getting confused with RGB values and HSV?
        
 
##        # we count the pixels that match for each color in our list
##        pixel_count = sum(sum(mask))

        # set parameters for the blob detector
        parameters = cv2.SimpleBlobDetector_Params()
#        parameters.filterByColor = True. Functions that sample code I found online used
        parameters.blobColor = 255
#        parameters.filterByArea = True. However I did not use it and commented it out
        parameters.minArea = 10000
        parameters.maxArea = 100000
    # took out the inertia and convexity features of filtering during blob detection
    #allows for less selective filtering by leaving out criteria on convexity and area and shape
        parameters.filterByInertia = False
        parameters.filterByConvexity = False

        detector = cv2.SimpleBlobDetector(parameters)

        # the detect method of detector returns list of blobs when applied to the mask
        #stores that list in blobs_list variable
        blobs_list = detector.detect(mask)
        # finds the largest blob
        largest = cv2.KeyPoint()
        if len(blobs_list) > 0:
            largest = max(blobs_list)
            

            found.append([color, largest.pt])

        
        # draw a green circle on the largest blob that shows up in the image/camera window
        mask_with_blob = cv2.drawKeypoints(image = mask,
                                        keypoints = blobs_list,
                                        color = (0, 255, 0),
                                        flags = cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
                                        
        
    
        cv2.imshow(color, mask_with_blob)

        #Could've used a blur() function - sum across pixels, 
        #im_with_keypoints = cv2.drawKeypoints(im, keypoints, np.array([]), (0,0,255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        
    # returns the color and position of the largest blob(x, y coordinates) that we see
    return found
    
# initialize the camera and let it sleep for a bit
cam = cv2.VideoCapture(0)
time.sleep(1)



def do_nothing(): #function callback to do with color palette, empty/fake event handler
    pass


# color palettes that allow manual setting/tweaking of HSV values/color settings for each color
#not sure how accurate this is, in terms of color detection/HSV values
#however improvement over only masking as was done in previous version dated May 09

cv2.namedWindow("colors", cv2.WINDOW_NORMAL) #cv2.WINDOW_NORMAL allows resizing of window/color palette
for color, bound in colors:
    #color values (HSV) for use in color palette's sliding bars
    cv2.createTrackbar(color + "H lower", "colors", bound[0][0], 179, do_nothing)
    cv2.createTrackbar(color + "S lower", "colors", bound[0][1], 255, do_nothing)
    cv2.createTrackbar(color + "V lower", "colors", bound[0][2], 255, do_nothing)

    cv2.createTrackbar(color + "H upper", "colors", bound[1][0], 179, do_nothing)
    cv2.createTrackbar(color + "S upper", "colors", bound[1][1], 255, do_nothing)
    cv2.createTrackbar(color + "V upper", "colors", bound[1][2], 255, do_nothing)
        

while True:
    # read frames, skip the empty one
    ret, frame = cam.read()
    if ret == False:
        continue

    
    for color, bound in colors:
        bound[0][0] = cv2.getTrackbarPos(color + "H lower", "colors")
        bound[0][1] = cv2.getTrackbarPos(color + "S lower", "colors")
        bound[0][2] = cv2.getTrackbarPos(color + "V lower", "colors")
        bound[1][0] = cv2.getTrackbarPos(color + "H upper", "colors")
        bound[1][1] = cv2.getTrackbarPos(color + "S upper", "colors")
        bound[1][2] = cv2.getTrackbarPos(color + "V upper", "colors")

        # why can't i update bound with this?
##        bound = [[cv2.getTrackbarPos(color + "H lower", "colors"),
##                cv2.getTrackbarPos(color + "S lower", "colors"),
##                cv2.getTrackbarPos(color + "V lower", "colors")],
##                 [cv2.getTrackbarPos(color + "H upper", "colors"),
##                cv2.getTrackbarPos(color + "S upper", "colors"),
##                cv2.getTrackbarPos(color + "V upper", "colors")]]
        
                 
##    print(colors)

    print(find_color(frame, colors))
                 
    #frame = frame.array was what we did with the Pi Camera.
    #took out the above part and frame capture part because testing with laptop camera not Pi camera
    #convert image to numpy array
   
##    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV) #test with BGR2HSV
    
##    for color, bound in colors:
##
##         # lower bound for values of color palette sliders/bars for each color
##        lower = numpy.array(
##                    [cv2.getTrackbarPos(color + "H lower", "colors"),
##                     cv2.getTrackbarPos(color + "S lower", "colors"),
##                     cv2.getTrackbarPos(color + "V lower", "colors")]
##                    )
##
##        # upper bound for values of color palette sliders/bars
##        upper = numpy.array(
##                    [cv2.getTrackbarPos(color + "H upper", "colors"),
##                     cv2.getTrackbarPos(color + "S upper", "colors"),
##                     cv2.getTrackbarPos(color + "V upper", "colors")]
##                    )
##
##        # mask out pixels that do not match 
##        mask = cv2.inRange(hsv, lower, upper)
##        #initially thought that maybe the mask function is getting confused with RGB values and HSV?
##        
## 
####        # we count the pixels that match for each color in our list
####        pixel_count = sum(sum(mask))
##
##        # set parameters for the blob detector
##        parameters = cv2.SimpleBlobDetector_Params()
###        parameters.filterByColor = True. Functions that sample code I found online used
##        parameters.blobColor = 255
###        parameters.filterByArea = True. However I did not use it and commented it out
##        parameters.minArea = 10000
##        parameters.maxArea = 100000
##    # took out the inertia and convexity features of filtering during blob detection
##    #allows for less selection with sizes and shapes
##        parameters.filterByInertia = False
##        parameters.filterByConvexity = False
##
##        detector = cv2.SimpleBlobDetector(parameters)
##
##        # the detect method of detector returns list of blobs when applied to the mask
##        #storing it in blobs_list variable
##        blobs_list = detector.detect(mask)
##        # finds the largest blob
##        largest = cv2.KeyPoint()
##        if len(blobs_list) > 0:
##            largest = max(blobs_list)
##        # draw a green circle on the largest blob that shows up in the image/camera window
##        mask_with_blob = cv2.drawKeypoints(image = mask,
##                                        keypoints = blobs_list,
##                                        color = (0, 255, 0),
##                                        flags = cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
##                                        
##        
##    
##
##        #Could've used a blur() function - sum across pixels, 
##        #im_with_keypoints = cv2.drawKeypoints(im, keypoints, np.array([]), (0,0,255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
##        
##        # prints the pixel count and position of the largest blob(x, y coordinates) that we see
##        print(color, largest.pt)

 
   
    # put in a wait key to escape/break out of the program/window 
    if cv2.waitKey(15) == 27:
        break
 
cam.release()
cv2.destroyAllWindows()
                           
  
