from bottle import route, run, template, request, static_file, HTTPResponse
import bottle
from pyimagesearch.shapedetector import ShapeDetector
import time
import os
import imutils
import cv2
import numpy as np
import json
import requests
from pprint import pprint
from generateModel import generateArchiFile
from paste import httpserver

save_path = "/tmp/brainhack"


@route('/static/<filepath:re:.*\.(jpg|jpeg|png|archimate)>')
def staticfile(filepath):
    return static_file(filepath, root = save_path)

@route('/upload', method='POST')
def index():
    upload     = request.files.get('upload')

    name, ext = os.path.splitext(upload.filename)

    if ext not in ('.png','.jpg','.jpeg'):
        return 'File extension not allowed.'

    file_path = get_save_path(upload.filename)
    file_url = '{scheme}://{host}/static/{file}{ext}'.format(scheme=request.urlparts.scheme, host=request.get_header('host'), path=save_path, file=name, ext=ext)

    # save source image to disk
    rmfile(file_path)
    upload.save(file_path)

    text = trigger_recognize_text(file_url)
    pprint(text)

    # process image from disk
    img, boxes, lines = process(file_path)
    generateArchiFile(boxes,lines,"{path}/{file}_processed.{ext}".format(path=save_path, file=name, ext="archimate"))

    # write processed image on disk

    cv2.imwrite("{path}/{file}_processed{ext}".format(path=save_path, file=name, ext=ext), img)
    
    processed_url = '{scheme}://{host}/static/{file}_processed{ext}'.format(scheme=request.urlparts.scheme, host=request.get_header('host'), path=save_path, file=name, ext=ext)
    archi_url = '{scheme}://{host}/static/{file}_processed.{ext}'.format(scheme=request.urlparts.scheme, host=request.get_header('host'), path=save_path, file=name, ext="archimate")
    return HTTPResponse(
                body={'processedFileUrl': processed_url,
                    'archimateFileUrl' : archi_url,
                    'message': "We've processed for you the image. You're welcome!"},
                status=201,
                headers={'Location': processed_url}
            )

def trigger_recognize_text(file_url):
    url = "https://westeurope.api.cognitive.microsoft.com/vision/v1.0/recognizeText"

    querystring = {"handwriting":"true"}

    payload = "{\"url\":\"" + file_url + "\"}"
    headers = {
        'content-type': "application/json",
        'ocp-apim-subscription-key': "7201b974a7b544ccbc2620f2e922562f",
        'cache-control': "no-cache"
    }

    response = requests.request("POST", url, data=payload, headers=headers, params=querystring)
    pprint(payload)
    pprint(response)
    pprint(response.headers)
    return get_recognize_text_response(response.headers.get('Operation-Location',""))

def get_recognize_text_response(operation_id):
    if operation_id == "":
        return None
    
    url = operation_id
    
    headers = {
        'ocp-apim-subscription-key': "7201b974a7b544ccbc2620f2e922562f",
        'cache-control': "no-cache"
    }

    time.sleep(3)
    response = requests.request("GET", url, headers=headers)
    pprint(url)
    pprint(response.text)
    try:
        return json.loads(response.text)
    except json.JSONDecodeError:
        return None

    recognitionResult = json_response['recognitionResult']
    lines = recognitionResult['lines']
    for line in lines:
        boundingBox = line['boundingBox']
        text = line['text'] 
    
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


#run(host='0.0.0.0', port=8080)
application = bottle.default_app()
httpserver.serve(application, host='0.0.0.0', port=8080)
