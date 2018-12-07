# USAGE
# python detect_shapes.py --image shapes_and_colors.png

# import the necessary packages
from pyimagesearch.shapedetector import ShapeDetector
import argparse
import imutils
import cv2
import numpy as np
from pprint import pprint

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True,
	help="path to the input image")
	
args = vars(ap.parse_args())

# load the image and resize it to a smaller factor so that
# the shapes can be approximated better
sd = ShapeDetector(args["image"])
sd.process()

for b in sd.boxes:
	pprint(vars(b))
for l in sd.lines:
	pprint(vars(l))

# show the output image
cv2.imwrite("{origname}.processed.jpg".format(origname=args["image"]),sd.processed_image)
#cv2.waitKey()
#cv2.destroyAllWindows()
