# import the necessary packages
import cv2
import imutils
import cv2
import numpy as np

class Box:
	def __init__(self, _id):
		self.id = _id
	type = "box"

class Line:
	type = "line"



class ShapeDetector:
	def __init__(self, source_file_path):
		self.boxes = []
		self.lines = []
		self.image = cv2.imread(source_file_path)
		self.boxid = 0
		pass
		
	def nextboxid(self):
		self.boxid = self.boxid + 1
		return self.boxid
		
	def closestbox(self,x,y):
		#print("{px}.{py}".format(px=x,py=y))
		minid = 0
		mindist = self.image.size * self.image.size
		for b in self.boxes:
			(bx, by, bw, bh) = b.box
			cx = bx + bw / 2
			cy = by + bh / 2
			dx = max(abs(cx - x) - bw / 2, 0);
			dy = max(abs(cx - y) - bh / 2, 0);
			dist = dx * dx + dy * dy;
			#print("{i}:{px}.{py}.{pw}.{ph}=>{d}".format(px=bx,py=by,pw=bw,ph=bh,d=dist,i=b.id))
			if dist < mindist:
				mindist = dist
				minid = b.id
		return minid
		

	def process(self):
		# load the image and resize it to a smaller factor so that
		# the shapes can be approximated better
		image = self.image
		#resized = imutils.resize(image, width=300)
		#ratio = image.shape[0] / float(resized.shape[0])

		# convert the resized image to grayscale, blur it slightly,
		# and threshold it
		gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
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

			cX = int((M["m10"] / M["m00"]))
			cY = int((M["m01"] / M["m00"]))
			shape = self.detect(c)
			
			displaytxt = shape
			
			if shape == "rectangle":
				r = Box(self.nextboxid())
				r.box = cv2.boundingRect(c)
				r.text = "rectangle {id}".format(id=r.id)
				displaytxt = r.text
				self.boxes.append(r)
				
				(x, y, w, h) = r.box
				cv2.rectangle(image,(x,y),(x+w,y+h),(255,0,0),2)
				
			elif shape == "line":
				l = Line()
				l.box = cv2.boundingRect(c)
				l.text = "line {id}".format(id=self.nextboxid())
				displaytxt = l.text
				self.lines.append(l)
			
			# multiply the contour (x, y)-coordinates by the resize ratio,
			# then draw the contours and the name of the shape on the image
			c = c.astype("float")
			#c *= ratio
			c = c.astype("int")
			cv2.drawContours(image, [c], -1, (0, 255, 0), 2)
			cv2.putText(image, displaytxt, (cX, cY), cv2.FONT_HERSHEY_SIMPLEX,
				0.5, (255, 0, 0), 2)

		self.processed_image = image

		for l in self.lines:
			(x, y, w, h) = l.box
			l.boxes = [ self.closestbox(x,y), self.closestbox(x+w,y+h) ]


	def detect(self, c):
		# initialize the shape name and approximate the contour
		shape = "unidentified"
		peri = cv2.arcLength(c, True)
		approx = cv2.approxPolyDP(c, 0.04 * peri, True)

		# if the shape is a triangle, it will have 3 vertices
		#if len(approx) == 3:
		#	shape = "triangle"

		# if the shape has 4 vertices, it is either a square or
		# a rectangle
		if len(approx) >= 4:
			# compute the bounding box of the contour and use the
			# bounding box to compute the aspect ratio
			(x, y, w, h) = cv2.boundingRect(approx)
			ar = w / float(h)

			# a square will have an aspect ratio that is approximately
			# equal to one, otherwise, the shape is a rectangle
			shape = "square" if ar >= 0.95 and ar <= 1.05 else "rectangle"

		# if the shape is a pentagon, it will have 5 vertices
		#elif len(approx) == 5:
		#	shape = "pentagon"

		# otherwise, we assume the shape is a circle
		else:
			shape = "line"

		# return the name of the shape
		return shape
