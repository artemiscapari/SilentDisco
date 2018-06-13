import os, csv, cv2, sys
import numpy as np
from matplotlib import pyplot as plt
import argparse

from Functions import*

imdir = '/Gray_images_test/'

ap = argparse.ArgumentParser()

ap.add_argument("-v", "--video", required = True, help = "Path to the video file.")
args = vars(ap.parse_args())
video = args["video"]


frame_start = 1
frame_end = 2
frame_step = 1


for i in range(frame_start, frame_end, frame_step):
    print 'Jooe'
    
    frame = extract_frame_frame(video, i)

    separate_colors(frame, i)


find_headphones('g1.png', 'frame1.png')