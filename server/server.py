from bottle import route, run, template, request, static_file, HTTPResponse
from pyimagesearch.shapedetector import ShapeDetector

import os
import imutils
import cv2
import numpy as np
from generateModel import generateArchiFile

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
    img, boxes, lines = process(file_path)
	generateArchiFile(boxes,lines,"{path}/{file}_processed{ext}".format(path=save_path, file=name, ext="archimate"))

    # write processed image on disk

    cv2.imwrite("{path}/{file}_processed{ext}".format(path=save_path, file=name, ext=ext), img)


    processed_url = '{scheme}://{host}/static/{file}_processed{ext}'.format(scheme=request.urlparts.scheme, host=request.get_header('host'), path=save_path, file=name, ext=ext)
    archi_url = '{scheme}://{host}/static/{file}_processed{ext}'.format(scheme=request.urlparts.scheme, host=request.get_header('host'), path=save_path, file=name, ext="archimate")
    return HTTPResponse(
                body={'processedFileUrl': processed_url,
                    'archimateFileUrl' : archi_url,
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


run(host='0.0.0.0', port=8080)
