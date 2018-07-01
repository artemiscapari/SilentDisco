# Can save cropped images of headphones for future use in ML Object Detection

import cv2

from Functions import * 

#An example of how to run crop_save on one image:

#Provide a file path to image
filename = 'test_images/Trimmed_1_7.png'

#Run crop_save
crop_save(filename)

#an image of a supposed individual headphone will be shown. 
#   Give input 'y' to save image and move onto the next one.
#   Give an other input to discard image and move onto the next one