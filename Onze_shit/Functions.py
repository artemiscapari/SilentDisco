import os
import cv2
import numpy as np
import math
from matplotlib import pyplot as plt



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



def extract_frame_frame(vidin, frame):
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

def separate_colors(imin, f, imdir = None):
    """ Takes a colour image and separates the colour layers.
    
    Args:
        imin: path to image (absolute or relative) or color image to separate.
        imdir: 
    
    Returns:
        saves individual color layers to file
        b, g, r: individual color layers of the original image.
    """
    
    img = read_image(imin)
    
    b, g, r = cv2.split(img)

    # Display image for debugging purposes.
    # show_image(img)

    imnames = ['b', 'g', 'r']
    images = [b, g, r]
    
    if imdir:
        save_images(images, imnames, f, imdir)
        save_image(img, 'frame', f, imdir)

    else:
        save_image(img, 'frame', f)
        save_images(images, imnames, f)

    return b, g, r


########################
#  Headphone Detection #
########################


def double_contour(imdir):


    image = cv2.imread(imdir)
    blurred = cv2.pyrMeanShiftFiltering(image, 31, 40)
    gray_img = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)
    retval2,threshold = cv2.threshold(gray_img,170,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)

    _, contours, _ = cv2.findContours(threshold, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)

    cv2.drawContours(threshold, contours, -1, (255,255,255), 10)

    _, contours, _ = cv2.findContours(threshold, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)

    cv2.drawContours(threshold, contours, -1, (255,0,255), 2)

    return contours

def find_headphones(imdir, original):

    original_image = cv2.imread(original)
    contours = double_contour(imdir)

    print "Number of contours found " , len(contours)

    for contour in contours:

        [x,y,w,h] = cv2.boundingRect(contour)
        if len(contour)/ math.sqrt(y+1) >2.5:
            # get rectangle bounding contour
        
            # discard areas that are too large
        
            if h>60 or w>60:
        
                continue
            # discard areas that are too small
        
            if h<5 or w<5:
        
                continue
            # draw rectangle around contour on original image

            cv2.rectangle(original_image,(x,y),(x+w,y+h),(255,0,255),1)


            # show original image with added contours  
            
        

    cv2.imshow('threshold',original_image)
    #cv2.imwrite('contours1.png', threshold)
    cv2.waitKey(0)
    cv2.destroyAllWindows()