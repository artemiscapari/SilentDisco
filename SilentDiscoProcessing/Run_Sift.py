import cv2
import numpy as np
import matplotlib.pyplot as plt
import math
import operator
from operator import itemgetter
import glob
from os import listdir
from os.path import isfile, join
import numpy
import cv2
from Functions import *

# read images of headphones

mypath='/Users/artemiscapari/Desktop/SilentDisco/SilentD/all_images'
onlyfiles = [ f for f in listdir(mypath) if isfile(join(mypath,f)) and f[-4:] == '.png']

images = numpy.empty(len(onlyfiles), dtype=object)
for n in range(0, len(onlyfiles)):
  images[n] = cv2.imread( join(mypath,onlyfiles[n]),0)

#images = [cv2.imread('/Users/artemiscapari/Downloads/siften/sd/silent-disco-london-image2.png',0)]
disco = cv2.imread('disco2.png')

#disco = cv2.imread('/Users/artemiscapari/Downloads/siften/test_images/Trimmed_1_4.png')

keypoints = find_keypoints(images)

rect_list, clrs = detect_objects(keypoints, disco)

disco = find_best_detections(rect_list, clrs, disco)

cv2.imshow('threshold',disco)
cv2.imwrite('boxes.jpg',disco)
cv2.waitKey(0)
cv2.destroyAllWindows()
