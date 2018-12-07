from bottle import route, run, template, request, static_file, HTTPResponse
from pyimagesearch.shapedetector import ShapeDetector

import os
import imutils
import cv2
import numpy as np

save_path = "/tmp/brainhack"


@route('/static/<filepath:re:.*\.(jpg|jpeg|png)>')
def staticfile(filepath):
    return static_file(filepath, root = save_path)

@route('/upload', method='POST')
def index():
    upload     = request.files.get('upload')

    name, ext = os.path.splitext(upload.filename)

    if ext not in ('.png','.jpg','.jpeg'):
        return 'File extension not allowed.'

    file_path = get_save_path(upload.filename)

    # save source image to disk
    rmfile(file_path)
    upload.save(file_path)

    # process image from disk
    img = process(file_path)

    # write processed image on disk

    cv2.imwrite("{path}/{file}_processed{ext}".format(path=save_path, file=name, ext=ext), img)


    processed_url = '{scheme}://{host}/static/{file}_processed{ext}'.format(scheme=request.urlparts.scheme, host=request.get_header('host'), path=save_path, file=name, ext=ext)
    return HTTPResponse(
                body={'processedFileUrl': processed_url,
                    'archimateFileUrl' : processed_url,
                    'message': "We've processed for you the image. You're welcome!"},
                status=201,
                headers={'Location': processed_url}
            )

def get_save_path(filename):
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    file_path = "{path}/{file}".format(path=save_path, file=filename)
    return file_path

def rmfile(filename):
    try:
        os.remove(filename)
    except OSError:
        pass
def process(source_file_path):
    sd = ShapeDetector(source_file_path)
	sd.process()
	return sd.processed_image, sd.boxes, sd.lines

    # load the image and resize it to a smaller factor so that
    # the shapes can be approximated better
    image = cv2.imread(source_file_path)
    resized = imutils.resize(image, width=300)
    ratio = image.shape[0] / float(resized.shape[0])

    # convert the resized image to grayscale, blur it slightly,
    # and threshold it
    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    # thresh = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY)[1]
    thresh = cv2.Canny(blurred, 50, 200)

    # find contours in the thresholded image and initialize the
    # shape detector

    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
    	cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)

    # loop over the contours
    for c in cnts:
    	# compute the center of the contour, then detect the name of the
    	# shape using only the contour
    	M = cv2.moments(c)
    	if M["m00"] == 0:
    		continue

    	cX = int((M["m10"] / M["m00"]) * ratio)
    	cY = int((M["m01"] / M["m00"]) * ratio)
    	shape = sd.detect(c)

    	# multiply the contour (x, y)-coordinates by the resize ratio,
    	# then draw the contours and the name of the shape on the image
    	c = c.astype("float")
    	c *= ratio
    	c = c.astype("int")
    	cv2.drawContours(image, [c], -1, (0, 255, 0), 2)
    	cv2.putText(image, shape, (cX, cY), cv2.FONT_HERSHEY_SIMPLEX,
    		0.5, (255, 0, 0), 2)

    return image


run(host='0.0.0.0', port=8080)
