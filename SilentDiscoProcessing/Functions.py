#Functions for Silent Disco Processing

import os
import cv2
import numpy as np
import math
from matplotlib import pyplot as plt
import operator
from operator import itemgetter
from os import listdir
from os.path import isfile, join
import glob


#############################
# Video processing#
#############################

def read_video(vidin):
    """ Reads a video from filepath.
    
    Args:
        vidin:
    Returns:
        Video capture.
    """
    
    
    # If vidin is not a string, assume it's already a videocapture thing.
    if isinstance(vidin, str):
        vidin = os.path.expanduser(vidin)
        return cv2.VideoCapture(vidin)
    else:
        return vidin


def get_number_frames(vidin):
    """ Returns the number of frames in a video.
    
    Args:
        vidin
    Returns:
    
    """
        
    vidcap = read_video(vidin)
    return int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))



def extract_frame(vidin, frame):
    """
    """
    
    
    vidcap = read_video(vidin)
    
    vidcap.set(cv2.CAP_PROP_POS_FRAMES, frame)
    success, image = vidcap.read()
    
    if success:
        # print frame

        return image


##########################
#  Image Processing  #
##########################

def read_image(imin, colorspace = None):
    """ Reads an image from filepath.
    
    Args:
        imin: full path to image (absolute or relative), if it's not a string the function assumes 
              it to be an image.
        colorspace: one of the following cv2.imread flags: cv2.IMREAD_COLOR, cv2.IMREAD_GRAYSCALE,
                    cv2.IMREAD_UNCHANGED (optional).
    Returns:
        An image array.
    """
    
    if isinstance(imin, str):
        imin = os.path.expanduser(imin)
        
        return cv2.imread(imin)
        
        # FIXME: colorspace doesn't get passed through properly.
        #if colorspace:
        #    return cv2.imread(imin, colorspace)
        #else:
        #    return cv2.imread(imin)
    else:
        return imin

def save_images(images, imnames, f, imdir = None):
    """ Save multiple images to files (calls save_image)
    
    Args:
        images: list of images to save.
        imnames: list of image names to append to imdir.
        imdir: path to target directory (absolute or relative path), if none is given, image is
               saved to the current working directory.
    """
    
    if imdir:
        for imname, image in zip(imnames, images):
            save_image(image, imname, f, imdir)
    else:
        for imname, image in zip(imnames, images):
            save_image(image, imname, f)


def save_image(image, imname, f, imdir = None):
    """ Save image to file.
    
    Args:
        image: image to save (array of values)
        imname: name of image to append to imdir, if it contains no extension default to png.
        imdir: full path to target directory (absolute or relative path), if none is given, image is
               saved to the current working directory.
    """
    imname = imname + str(f)
    # Test if imname contains an extension, if not: default to png.
    if len(imname.rsplit('.')) == 1:
        imname = imname + ".png"
    
    if imdir:
    
        imname = imdir + imname
        cv2.imwrite(imname, image)
    else:
        cv2.imwrite(imname, image)

def separate_colors(imin, imdir = None):
    """ Takes a colour image and separates the colour layers.
    
    Args:
        imin: path to image (absolute or relative) or color image to separate.
        imdir: 
    
    Returns:
        saves individual color layers to file
        b, g, r: individual color layers of the original image.
    """
    
    img = read_image(imin)
    
    r, g, b = cv2.split(img)


    return r, g, b


########################
#  Headphone Detection #
########################




def double_contour(img):
    ''' Takes an image, most likely black and white, and applies in order: Blurring, thresholding,
        contour detection, contour drawing with big white lines, contour detection. All opencv packages.

    Args:
        img: An image opened with cv2.imread()
    
    Returns:
        contours

    '''
    blurred_image = cv2.blur(img,(4,4))
    retval2,threshold = cv2.threshold(blurred_image,80,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)

    _, contours, _ = cv2.findContours(threshold, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)


    cv2.drawContours(threshold, contours, -1, (255,255,255), 10)

    _, contours, _ = cv2.findContours(threshold, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)


    return contours

def find_boxes(contours):

    ''' Takes an array of contours, from double_contour(), and draws boxes around them with cv2.boundingRect(). Also checks 
        if the boxes arent too small, too big, or too small relative to its y coordinate.

    Args:
        contours: Array of contours from cv2.findContours()
    
    Returns:
        a list of boxes with for instance boxes[1] == [x,y, x+w, y+h].

    '''

    boxes = []

    for contour in contours:

        # get rectangle bounding contour

        [x,y,w,h] = cv2.boundingRect(contour)
        
        if len(contour)/ math.sqrt(y+1) <2.5:
            continue
        
        # discard areas that are too large
        
        if h>60 or w>60:
    
            continue
        # discard areas that are too small
    
        if h<7 or w<7:
    
            continue
        # draw rectangle around contour on original image

        box = [x,y, x+w, y+h]
        # cv2.rectangle(original_image,(x,y),(x+w,y+h),(b,g,r),1)
        boxes.append(box)

    return boxes
    

            # show original image with added contours  



##########################
#  Crop Save for ML      #
##########################


def crop_save(filename):


    '''
    
    Takes a filename/path and splits the colors into b, g ,r values. Afterwards it processes every color with double contour detection
    and runs crop_checking_saving() with the found boxes, filename and color.

    Args:
        Filepath
    
    '''

    frame = read_image(filename)

    b, g, r  = separate_colors(frame)

    j = 0

    colors = ['blue', 'green', 'red']
    for color in colors:

        if color == 'blue':
            contours = double_contour(b)
            boxes = find_boxes(contours)
            crop_checking_saving(boxes, filename, color)

        if color == 'green':
            contours = double_contour(g)
            boxes = find_boxes(contours)
            crop_checking_saving(boxes, filename, color)

        if color == 'red':
            contours = double_contour(r)
            boxes = find_boxes(contours)
            crop_checking_saving(boxes, filename, color)

        
        
def crop_checking_saving(boxes, filename, color):  

    '''

    Takes the found boxes around headphones of a certain color and asks wheter it should save them or not. The input can be 'y' to save
    or any other key to discard. Saves are made into a created directory 
    with form wd >> filename    >> Blue
                                >> Green
                                >> Red


    Args:
        boxes: list of lists with coordinates of boxes headphones
        filename: filename or path from wd
        color: str with the color of the corresponding headphones 
    
    Output:
        shows an image of a proposed headphone and saves if input is 'y'
        

    '''

    j = 0
    frame = read_image(filename)

    new_directory = filename.split('.')[0]+'_cropped_saving/'+color+'/'

    if not os.path.exists(new_directory):
        os.makedirs(new_directory)
        

    for box in boxes:
        j+=1

        w = box[2]-box[0]
        h = box[3]-box[1]
        if h>w:
            w=h

        crop_img = frame[box[1]:box[1]+w, box[0]:box[0]+w]

        while True:
            cv2.imshow(new_directory+color+'_'+str(j)+'.png',crop_img)
            k = cv2.waitKey(0)

            if k == 121:
                cv2.imwrite(new_directory+color+'_'+str(j)+'.png',crop_img)
                cv2.destroyAllWindows()
                break
            else:
                cv2.destroyAllWindows()
                break



#############################
#           SIFT            #
#############################


# Creates sift features
sift = cv2.xfeatures2d.SIFT_create()


def find_keypoints(images):
    """ Stores needed information about the headphones.
    
    Args: 
        images: original list of images

    Returns:
        keypoints: tuple with the keypoints, number of keypoints and desciptors
    
    """

    keypoints = []
    id = 0

    for img in images :
        
        kp, des = sift.detectAndCompute(img,None)
        keypoints.append((kp,des,len(kp)))
        id+=1
        print(id, len(kp))

    return keypoints


def sort_points(pts):
    """ Sorts the list of keypoints of the original images by distance from zero point.
    
    Args:
        pts: unsorted list of keypoints found

    Returns:
        sorted_pts: sorted list of keypoints by distance from zero point

    """
    
    indices = {}
    sorted_pts = []

    for i in range(0,len(pts)):  
        distance = math.sqrt( ((0-pts[i][0])**2)+((0- pts[i][1])**2))
        indices[i] = distance

    indices = sorted(indices.items(), key=operator.itemgetter(1))
    
    for i in indices:
        index = i[0]
        sorted_pts.append(pts[index])

    return sorted_pts


def group_keypoints(sorted_pts):
    """ Groups the overlapping boxes together in seperate keys.
    
    Args:
        sorted_pts: sorted list of keypoints of original images

    Returns:
        headphones: dictionary with the overlapping boxes in seperate keys
    
    """

    max_kp_distance = 15
    headphones = {}
    coordinates = []
    hp_id = 0
    for i in range(0,len(sorted_pts)):
        distance = math.sqrt(((sorted_pts[i-1][0]-sorted_pts[i][0])**2)+((sorted_pts[i-1][1]- sorted_pts[i][1])**2))
        coordinates.append(sorted_pts[i-1])
        if distance < max_kp_distance:
            coordinates.append(sorted_pts[i])
        else:
            headphones[hp_id] = coordinates
            hp_id +=1
            coordinates = []
    return headphones


def closest_box(grouped_boxes, box_list):
    """ Finds the nearest box from the original list of boxes. This results in more accurate boxes around the headphones.

    Args: 
        grouped_boxes: grouped boxes
        box_list: original list of boxes

    Returns:
        best_boxes: list with nearest boxes


    """

    best_boxes = []
    rgb_code = []

    for new_box in grouped_boxes:
        shortest_dist = 100 

        for old_box in box_list:
            distance = math.sqrt(((new_box[0]-old_box[0])**2)+((new_box[1]- old_box[1])**2))

            if shortest_dist > distance: 

                if distance > 4: # so it doesn't respond to white light
                    shortest_dist = distance
                    best_box = old_box

        best_boxes.append(best_box)

    return best_boxes  #rgb_code


def find_rect_bounds(x, y, points):
    """ Uses the keypoints which describe one headphone got the right size of rectangle.

    Args:
        x: average x-value of the keypoints describing one headphone
        y: average y-value of the keypoints describing on eheadphone
        points: list of points which describe one headphone

    Returns:
        longest_distance_x: longest x-direction of the rectangle around the headphone
        longest_distance_y: longest y-direction of the rectangle around the headphone
    
    """
    
    longest_distance_x = 0
    longest_distance_y = 0

    for rectangle in points:

        if abs(x - rectangle[0]) > longest_distance_x: 
            longest_distance_x = abs(x - rectangle[0]) 

        if abs(y - rectangle[1]) > longest_distance_y:
            longest_distance_y = abs(y - rectangle[1]) 

    return longest_distance_x, longest_distance_y


def detect_objects(keypoints, input_image):
    """ Uses the keypoints of the original iages of the headphones to detect headphones in the input image.
    
    Args:
        keypoints: dictionary of the keypoints found in the original images of the headphones
        input_image: input image of the disco

    Returns:
        rect_list: list with all the rectangels which are detected
        clr_list: list with the colors of all the rectangles

    """

    sift = cv2.xfeatures2d.SIFT_create()

    r,g,b = separate_colors(input_image)

    kpr, desr = sift.detectAndCompute(r ,None)
    kpg, desg = sift.detectAndCompute(g ,None)
    kpb, desb = sift.detectAndCompute(b ,None)
    

    FLANN_INDEX_KDTREE = 0
    index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
    search_params = dict(checks = 50)
    flann = cv2.FlannBasedMatcher(index_params, search_params)
    colors = [['red', kpr, desr, (255,0,0) ], ['green',kpg, desg, (0,255,0) ],['blue',kpb, desb, (0,0, 255) ] ]  
    rect_list = []
    clr_list= []

    for image in keypoints: # for every headphone image 
        [kp1, des1, k] = image
        print(k)
        for color in colors: # detect this headphone in every color
            [colorname, kpt, desc, rgb_code] = color
            matches = flann.knnMatch(des1,desc,k)            
            pts = []
            kp_thresh = int(k*0.5)
            wall = 50

            for keypoints in matches: 

                for m in keypoints:
                    pts.append(list(kpt[m.trainIdx].pt))

            sorted_pts = sort_points(pts)

            headphones = group_keypoints(sorted_pts)


            for headphone in headphones:  
                points = headphones[headphone]

                if len(points) > kp_thresh :

                    if points:
                        [x,y] = map(itemgetter(0),points), map(itemgetter(1),points)
                        [x,y] = int(sum(x)/len(x)),int(sum(y)/len(y)) # average of the keypoints, use it as center of headphone
                        longest_distance_x,longest_distance_y = find_rect_bounds(x, y, points)
                        x1,y1,x2,y2 = [int(x-longest_distance_x-15) ,int(y-longest_distance_y-15),int(x+longest_distance_x+15) ,int(y+ longest_distance_y+15)]
                        
                        if y1 > wall: # filter out the lights on the wall
                            rect_list.append((x1,y1,x2,y2))
                            clr_list.append(rgb_code)

    return rect_list, clr_list

def find_best_detections(rect_list, clr_list, input_image):
    """ Finds the best boxes and draw these with the rigth color in the original disco image.

    Args:
        rect_list: list with all the rectangles detected
        clr_list: list with the right color for the rectangles
        input_image: original image of the disco
    
    Returns:
        input_image: image of the disco with the rectangles in the right color

    """

    box_grouped = cv2.groupRectangles(rect_list,1,0.03)
    best_boxes = closest_box(box_grouped[0], rect_list)

    for box in best_boxes:
        x1 = box[0]
        y1 = box[1]
        x2 = box[2]
        y2 = box[3]
        coloridx = rect_list.index(box)
        rgb_code = clr_list[coloridx]
        cv2.rectangle(input_image, (x1, y1), (x2, y2),rgb_code,2)

    return input_image


