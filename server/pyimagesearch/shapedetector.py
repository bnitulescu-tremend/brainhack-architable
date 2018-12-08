# import the necessary packages
import cv2
import imutils
import cv2
import numpy as np
from pprint import pprint

class Box:
	def __init__(self, _id):
		self.id = _id
	type = "box"
	
	def overlaps(self, b):
		(x, y, w, h) = self.box
		(bx, by, bw, bh) = b.box
		
		#print("{i}:{px}.{py}.{pw}.{ph}".format(px=x,py=y,pw=w,ph=h,i=self.id))
		#print("{i}:{px}.{py}.{pw}.{ph}".format(px=bx,py=by,pw=bw,ph=bh,i=b.id))

		# minimal significant overlap - as % of the smallest rectangle
		minArea = min(w*h, bw*bh) * 0.2
		#print(minArea)
	
		dx = max(min(x + w - bx,bx + bw - x), 0)
		dy = max(min(y + h - by,by + bh - y), 0)
		#print("{x}-{y}".format(x=dx,y=dy))
		
		return dx * dy > minArea
		
	def merge(self, b):
		(x, y, w, h) = self.box
		(bx, by, bw, bh) = b.box
		dx = max (x+w,bx+bw)
		x = min(x,bx)
		w = dx-x
		
		dy = max (y+h,by+bh)
		y = min(y,by)
		h = dy-y
		
		self.box = (x, y, w, h)

class Line:
	type = "line"

class Label:
	def __init__(self, text, box, ratio):
		self.x = int((box[0]/ratio))
		self.y = int(box[1]/ratio)
		self.w = int((box[4]-box[0])/ratio)
		self.h = int((box[5]-box[1])/ratio)
		self.text = text
		
def remove_overlaps(boxes):
	#for b in boxes:
	#	pprint (" {i}".format(i=b.id))
	newboxes = []
	while len(boxes) > 0:
		box = boxes.pop()
		copy = True
		for b in boxes:
			if box.overlaps(b):
				#pprint (" {i} <=> {j}".format(i=b.id, j=box.id))
				b.merge(box)
				copy = False
				break
		if copy:
			newboxes.append(box)
	return newboxes

class ShapeDetector:
	def __init__(self, source_file_path, ocr):
		self.boxes = []
		self.lines = []
		self.labels = []
		self.image = cv2.imread(source_file_path)
		self.boxid = 0
		self.ocr = ocr
		pass
		
	def nextboxid(self):
		self.boxid = self.boxid + 1
		return self.boxid
		
	def closestbox(self,x,y):
		#print("{px}.{py}".format(px=x,py=y))
		minbox = None
		mindist = self.image.size * self.image.size
		for b in self.boxes:
			(bx, by, bw, bh) = b.box
			cx = bx + bw / 2
			cy = by + bh / 2
			dx = max(abs(cx - x) - bw / 2, 0);
			dy = max(abs(cy - y) - bh / 2, 0);
			dist = dx * dx + dy * dy;
			#print("{i}:{px}.{py}.{pw}.{ph}=>{d}".format(px=bx,py=by,pw=bw,ph=bh,d=dist,i=b.id))
			if dist < mindist:
				mindist = dist
				minbox = b
		return minbox, mindist
		
	def closestid(self,x,y):
		b, _ = self.closestbox(x,y)
		if b is None:
			return 0
		else:
			return b.id
			
	def getlabels(self, ratio):
		if self.ocr is None:
			return

		try:
			recognitionResult = self.ocr['recognitionResult']
			lines = recognitionResult['lines']
			for line in lines:
				txt = line['text']
				box = line['boundingBox']
				self.labels.append(Label(txt, box, ratio))

		except KeyError:
			return
		except NameError:
			return
		

	def process(self):
		# load the image and resize it to a smaller factor so that
		# the shapes can be approximated better
		image = imutils.resize(self.image, width=600)
		ratio = self.image.shape[0] / float(image.shape[0])
		self.getlabels(ratio)
		
		# convert the resized image to grayscale, blur it slightly,
		# and threshold it
		gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
		
		for lb in self.labels:
			gray[lb.y:lb.y+lb.h,lb.x:lb.x+lb.w] = 255
			
		blurred = cv2.GaussianBlur(gray, (5, 5), 0)
		ret,thresh = cv2.threshold(blurred,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
		image = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
		
		# thresh = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY)[1]
		thresh = cv2.Canny(thresh, 50, 200)
		#thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(2,2)))
		#thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(2,2)))

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
				(x, y, w, h) = r.box
				
				if w > 7 and h > 7:
					r.text = ""
					#r.text = "*R{id}".format(id=r.id)
					self.boxes.append(r)
				
			elif shape == "line":
				l = Line()
				l.box = cv2.boundingRect(c)
				[vx,vy,x,y] = cv2.fitLine(c, cv2.DIST_L2,0,0.01,0.01)
				if vy < 0:
					#line going low left - upper right
					(x, y, w, h) = l.box
					l.box = (x, y+h, w, -h)
					
				l.text = "L{id}".format(id=self.nextboxid())
				self.lines.append(l)
				#cv2.drawContours(image, [c], -1, (0, 255, 0), 2)
				#cv2.putText(image, l.text, (cX, cY), cv2.FONT_HERSHEY_SIMPLEX,
				#	0.5, (255, 255, 0), 2)
			
			# multiply the contour (x, y)-coordinates by the resize ratio,
			# then draw the contours and the name of the shape on the image
			c = c.astype("float")
			#c *= ratio
			c = c.astype("int")
			#cv2.drawContours(image, [c], -1, (0, 255, 0), 2)
			
		# reduce overlapping rectangles
		self.boxes = remove_overlaps(self.boxes)		
		
		# put labels on rectangles

		for lb in self.labels:
			b, d = self.closestbox(lb.x+lb.w/2,lb.y+lb.h/2)
			if d == 0 and not b is None:
				b.text = lb.text + b.text
			#cv2.rectangle(image, (lb.x,lb.y), (lb.x+lb.w,lb.y+lb.h),(0,0,255),1)
			
		# link rectangles with lines
		
		for r in self.boxes:
			(x, y, w, h) = r.box
			cv2.rectangle(image,(x,y),(x+w,y+h),(255,0,0),2)
			cv2.putText(image, r.text, (x+w/2, y+h/2), cv2.FONT_HERSHEY_SIMPLEX,
				0.5, (0, 0, 255), 2)
			
		
		self.processed_image = image

		newlines = []
		for l in self.lines:
			(x, y, w, h) = l.box
			l.boxes = [ self.closestid(x,y), self.closestid(x+w,y+h) ]
			if l.boxes[0] != l.boxes[1]:
				newlines.append(l)
			cv2.line(image,(x,y),(x+w,y+h),(0,255,0),2)
		self.lines = newlines

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
			#ar = w / float(h)

			# a square will have an aspect ratio that is approximately
			# equal to one, otherwise, the shape is a rectangle
			shape = "rectangle"

		# if the shape is a pentagon, it will have 5 vertices
		#elif len(approx) == 5:
		#	shape = "pentagon"

		# otherwise, we assume the shape is a circle
		else:
			shape = "line"

		# return the name of the shape
		return shape
