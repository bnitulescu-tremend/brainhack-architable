# brainhack-architable


```
pip install bottle opencv-python imutils

# run server
cd server
python server.py
```


# How to upload

`curl -v -F 'upload=@poza.jpeg' http://localhost:8080/upload`

Check Location header for processing result.

# To download procesed picture

`GET http://localhost:8080/static/picture.jpeg`


# De joaca...
```
python detect_shapes.py -i images/dia.jpeg
```
