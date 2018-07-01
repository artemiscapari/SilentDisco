#Image Processing with double contour detection

import os, csv, cv2, sys
import numpy as np
from matplotlib import pyplot as plt
import argparse

from Functions import*

'''
This script loops through a directory of a file with only images. Screenshots of silent disco's in this example.
For each image:
    It seperates the colors into B&W images of red, green and blue values
For each color of each image: 
    Finds contours using double_contour()
    Finds correct boxes using find_boxes()
    Draws boxes on original frame with corresponding color

The boxes can also be used to save pictures of individual headphones for future use


'''

file_path = "./test_images/"
for _, _, files in os.walk(file_path):

    for file in files:
        if file == '.DS_Store':
            continue  
        print file 

        filename = file_path+file
        
        frame = read_image(filename)
        frame_name = 'contours/'+file.split(".")[0]+'_contours.png'

        r, g, b  = separate_colors(frame)
        
        
        colors = ['red', 'green', 'blue']

        for color in colors: 
            
            if color == 'red':
                contours = double_contour(b)
                boxes = find_boxes(contours)
                for box in boxes:
                    cv2.rectangle(frame,(box[0],box[1]),(box[2],box[3]),(0,0,255),1)

            if color == 'green':
                contours = double_contour(g)
                boxes = find_boxes(contours)
                for box in boxes:
                    cv2.rectangle(frame,(box[0],box[1]),(box[2],box[3]),(0,255,0),1)


            if color == 'blue':
                contours = double_contour(r)
                boxes = find_boxes(contours)
                for box in boxes:
                    cv2.rectangle(frame,(box[0],box[1]),(box[2],box[3]),(255,0,0),1)


    #Can show or save original frame with boxes
        cv2.imshow(frame_name,frame)
        # cv2.imwrite(frame_name, frame)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

