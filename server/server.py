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
    send_arhitecture_request(text)
    #pprint(text)

    # process image from disk
    img, boxes, lines = process(file_path, text)
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

            
class ArchResources:
    resources = []
    
    class ArchRes:
        def __init__(self,type):
            self.type=type
            self.count=1

    def add(self,type):
        for r in self.resources:
            if r.type == type:
                r.count += 1
                return
        self.resources.append(self.ArchRes(type))

    def getjson(self):
        jobj = []
        for r in self.resources:
            jobj.append({"type":r.type,"count":r.count})
        return json.JSONEncoder().encode(jobj)
            
def send_arhitecture_request(text_json):
    if text_json is None:
    return
    try:
        ar = ArchResources()
        
        recognitionResult = text_json['recognitionResult']
        lines = recognitionResult['lines']
        for line in lines:
            #boundingBox = line['boundingBox']
            txt = line['text'][0].upper()
            if txt == "H":
                ar.add("ha")
            elif txt == "W":
                ar.add("wp")
            elif txt == "D":
                ar.add("db")
            elif txt == "V":
                ar.add("varnish")
            
        arch_req=ar.getjson()
        url = "http://88.99.210.90:8000"        
        payload = arch_req
        headers = {
            'content-type': "application/json",
             'cache-control': "no-cache"
        }
        try:
            response = requests.request("POST", url, data=payload, headers=headers, params="",timeout = 3)
            pprint(payload)
            pprint(response)
        except ConnectTimeout:
            return
    except KeyError:
        return
    except NameError:
        return
            
def trigger_recognize_text(file_url):
    url = "https://westeurope.api.cognitive.microsoft.com/vision/v1.0/recognizeText"

    querystring = {"handwriting":"true"}

    payload = "{\"url\":\"" + file_url + "\"}"
    headers = {
        'content-type': "application/json",
        'ocp-apim-subscription-key': "7201b974a7b544ccbc2620f2e922562f",
        'cache-control': "no-cache"
    }

    try:
        response = requests.request("POST", url, data=payload, headers=headers, params=querystring, timeout = 5)
        pprint(payload)
        pprint(response)
        pprint(response.headers)
        return get_recognize_text_response(response.headers.get('Operation-Location',""))
    except ConnectTimeout:
        return None

def get_recognize_text_response(operation_id):
    if operation_id == "":
        return None
    
    url = operation_id
    
    headers = {
        'ocp-apim-subscription-key': "7201b974a7b544ccbc2620f2e922562f",
        'cache-control': "no-cache"
    }

    time.sleep(3)
    try:
        response = requests.request("GET", url, headers=headers, timeout = 5)
        pprint(url)
        pprint(response.text)
        try:
            return json.loads(response.text)
        except json.JSONDecodeError:
            return None
    except ConnectTimeout:
        return None

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

def process(source_file_path, text):
    sd = ShapeDetector(source_file_path, text)
    sd.process()
    for b in sd.boxes:
        pprint(vars(b))
    for l in sd.lines:
        pprint(vars(l))
    return sd.processed_image, sd.boxes, sd.lines

#send_arhitecture_request(json.loads('{"status":"Succeeded","recognitionResult":{"lines":[{"boundingBox":[284,250,367,264,360,306,277,292],"text":"HA","words":[{"boundingBox":[266,247,364,263,351,304,254,288],"text":"HA"}]},{"boundingBox":[111,510,192,498,203,574,122,585],"text":"Ell","words":[{"boundingBox":[87,487,218,507,222,578,91,558],"text":"Ell"}]},{"boundingBox":[296,521,398,532,394,570,292,559],"text":"We","words":[{"boundingBox":[327,530,375,530,373,565,325,565],"text":"We"}]},{"boundingBox":[733,522,834,526,833,561,732,558],"text":"FEB","words":[{"boundingBox":[712,517,846,527,844,565,710,555],"text":"FEB"}]},{"boundingBox":[389,764,513,778,509,814,385,800],"text":"ESB","words":[{"boundingBox":[383,769,482,773,482,806,382,802],"text":"ESB"}]},{"boundingBox":[89,900,206,900,198,900,81,900],"text":"DB","words":[{"boundingBox":[95,900,177,900,190,900,109,900],"text":"DB"}]},{"boundingBox":[653,900,807,900,806,900,652,900],"text":"DELASTIC","words":[{"boundingBox":[636,900,808,900,809,900,637,900],"text":"DELASTIC"}]}]}}'))
#u'{"status":"Succeeded","recognitionResult":{"lines":[{"boundingBox":[326,260,395,271,389,309,320,298],"text":"HA","words":[{"boundingBox":[300,260,391,268,397,309,306,301],"text":"HA"}]},{"boundingBox":[138,507,216,517,212,550,135,540],"text":"FE","words":[{"boundingBox":[132,492,189,509,178,550,120,532],"text":"FE"}]},{"boundingBox":[328,510,423,523,418,559,323,546],"text":"FE Z","words":[{"boundingBox":[310,512,380,518,378,553,308,547],"text":"FE"},{"boundingBox":[375,518,419,521,417,556,373,553],"text":"Z"}]},{"boundingBox":[738,522,832,529,830,562,735,555],"text":"FEB","words":[{"boundingBox":[718,517,842,531,838,566,714,552],"text":"FEB"}]},{"boundingBox":[407,744,522,759,518,791,403,776],"text":"ESB","words":[{"boundingBox":[387,746,506,753,505,785,385,778],"text":"ESB"}]},{"boundingBox":[141,900,225,900,219,900,136,900],"text":"DB","words":[{"boundingBox":[124,900,203,900,208,900,128,900],"text":"DB"}]},{"boundingBox":[626,899,809,900,799,900,617,900],"text":"ELASTIC","words":[{"boundingBox":[626,900,812,900,814,900,628,900],"text":"ELASTIC"}]}]}}'

#run(host='0.0.0.0', port=8080)
application = bottle.default_app()
httpserver.serve(application, host='0.0.0.0', port=8080)
