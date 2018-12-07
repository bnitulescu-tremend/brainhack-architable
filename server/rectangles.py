from pprint import pprint

class Box:
	type = "box"

r1 = Box()
r1.id = 1
r1.text = "Box 1"
r1.box = [1,1,100,100]

r2 = Box()
r2.id = 2
r2.text = "Box 2"
r2.box = [200,1,300,100]

r3 = Box()
r3.id = 3
r3.text = "Box 2"
r3.box = [100,200,200,200]


class Line:
	type = "line"

l1 = Line()
l1.boxes = [1,3]

l2 = Line()
l2.boxes = [2,3]


boxes = [r1, r2, r3]
lines = [l1, l2]

for b in boxes:
	pprint(vars(b))
for l in lines:
	pprint(vars(l))

