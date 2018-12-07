from bottle import route, run, template


@route('/upload', method='POST')
def index(name):
    upload     = request.files.get('upload')
    name, ext = os.path.splitext(upload.filename)
    if ext not in ('png','jpg','jpeg'):
        return 'File extension not allowed.'

    return template('OK!')

run(host='localhost', port=8080)
