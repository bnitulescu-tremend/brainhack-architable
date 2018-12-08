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
ocr =json.loads(u'{"status":"Succeeded","recognitionResult":{"lines":[{"boundingBox":[326,260,395,271,389,309,320,298],"text":"HA","words":[{"boundingBox":[300,260,391,268,397,309,306,301],"text":"HA"}]},{"boundingBox":[138,507,216,517,212,550,135,540],"text":"FE","words":[{"boundingBox":[132,492,189,509,178,550,120,532],"text":"FE"}]},{"boundingBox":[328,510,423,523,418,559,323,546],"text":"FE Z","words":[{"boundingBox":[310,512,380,518,378,553,308,547],"text":"FE"},{"boundingBox":[375,518,419,521,417,556,373,553],"text":"Z"}]},{"boundingBox":[738,522,832,529,830,562,735,555],"text":"FEB","words":[{"boundingBox":[718,517,842,531,838,566,714,552],"text":"FEB"}]},{"boundingBox":[407,744,522,759,518,791,403,776],"text":"ESB","words":[{"boundingBox":[387,746,506,753,505,785,385,778],"text":"ESB"}]},{"boundingBox":[141,900,225,900,219,900,136,900],"text":"DB","words":[{"boundingBox":[124,900,203,900,208,900,128,900],"text":"DB"}]},{"boundingBox":[626,899,809,900,799,900,617,900],"text":"ELASTIC","words":[{"boundingBox":[626,900,812,900,814,900,628,900],"text":"ELASTIC"}]}]}}')
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
