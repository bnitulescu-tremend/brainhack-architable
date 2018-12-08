# USAGE
# python detect_shapes.py --image shapes_and_colors.png

# import the necessary packages
from pyimagesearch.shapedetector import ShapeDetector
import argparse
import imutils
import cv2
import numpy as np
from pprint import pprint
import json

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True,
	help="path to the input image")
	
args = vars(ap.parse_args())

# load the image and resize it to a smaller factor so that
# the shapes can be approximated better
ocr =json.loads(u'{"status":"Succeeded","recognitionResult":{"lines":[{"boundingBox":[316,332,392,346,385,385,309,371],"text":"HA","words":[{"boundingBox":[288,333,380,342,389,383,297,374],"text":"HA"}]},{"boundingBox":[128,582,207,589,204,622,125,615],"text":"FEI","words":[{"boundingBox":[108,584,213,588,220,622,115,617],"text":"FEI"}]},{"boundingBox":[321,579,416,589,412,625,317,615],"text":"FE Z","words":[{"boundingBox":[307,580,374,585,373,621,306,616],"text":"FE"},{"boundingBox":[370,585,412,588,411,624,369,621],"text":"Z"}]},{"boundingBox":[760,586,818,585,819,616,761,617],"text":"E 3","words":[{"boundingBox":[745,586,783,586,783,617,745,617],"text":"E"},{"boundingBox":[787,586,825,586,825,617,787,617],"text":"3"}]},{"boundingBox":[404,811,522,824,518,859,400,846],"text":"ESB","words":[{"boundingBox":[395,814,495,818,494,850,394,847],"text":"ESB"}]},{"boundingBox":[109,900,223,900,216,900,102,900],"text":"/DB","words":[{"boundingBox":[61,900,168,900,220,900,114,900],"text":"/DB"}]},{"boundingBox":[655,900,799,900,798,900,654,900],"text":"ELASTIC","words":[{"boundingBox":[637,900,810,900,811,900,639,900],"text":"ELASTIC"}]}]}}')
#ocr =json.loads(u'{"status":"Succeeded","recognitionResult":{"lines":[{"boundingBox":[529,132,614,127,618,193,532,197],"text":"HA","words":[{"boundingBox":[478,135,627,123,637,191,488,202],"text":"HA"}]},{"boundingBox":[871,81,1120,85,1119,161,870,157],"text":"2 DATA","words":[{"boundingBox":[849,90,910,84,923,161,861,167],"text":"2"},{"boundingBox":[904,85,1120,65,1133,142,917,162],"text":"DATA"}]},{"boundingBox":[220,484,334,469,340,514,226,529],"text":"XID","words":[{"boundingBox":[231,481,348,456,327,509,210,533],"text":"XID"}]},{"boundingBox":[755,455,894,445,897,495,759,505],"text":"1 p","words":[{"boundingBox":[740,459,790,444,786,521,736,535],"text":"1"},{"boundingBox":[835,431,885,416,880,493,830,507],"text":"p"}]},{"boundingBox":[537,773,621,795,608,844,524,823],"text":"DB","words":[{"boundingBox":[506,770,622,794,612,843,496,819],"text":"DB"}]}]}}')
sd = ShapeDetector(args["image"], ocr)
sd.process()

for b in sd.boxes:
	pprint(vars(b))
for l in sd.lines:
	pprint(vars(l))
for l in sd.labels:
	pprint(vars(l))

# show the output image
cv2.imwrite("{origname}.processed.jpg".format(origname=args["image"]),sd.processed_image)
#cv2.waitKey()
#cv2.destroyAllWindows()
