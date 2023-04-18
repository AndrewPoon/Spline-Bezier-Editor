import math

class Point:
    def __init__(self,x=500,y=500):
        self.x=x
        self.y=y
    def set(self,x,y):
        self.x=x
        self.y=y
    def move(self,x,y):
        self.x+=x
        self.y+=y

class Handle(Point):
    def __init__(self,x,y,parent):
        Point.__init__(self,x,y)
        self.parent=parent
        self.type=None
    class type:
        HANDLE1=1
        HANDLE2=2
class Node(Point):
    def __init__(self,x,y):
        Point.__init__(self,x,y)
        self.handle1=Handle(0,0,self)
        self.handle2=Handle(0,0,self)
        self.has_handle1=False
        self.has_handle2=False
    def addHandle1(self,x,y):
        self.handle1=Handle(x,y,self)
        self.handle1.type=Handle.type.HANDLE1
        self.has_handle1=True
    def addHandle2(self,x,y):
        self.handle2=Handle(x,y,self)
        self.handle2.type=Handle.type.HANDLE2
        self.has_handle2=True
#bezier curve 
def bezier(A,c1,c2,B,t):
    return math.pow((1-t),3)*A+3*math.pow((1-t),2)*t*c1+3*(1-t)*math.pow(t,2)*c2+math.pow(t,3)*B
# calculate the euclidean distance between two points
def euclid_dist(p1,p2):
    return math.sqrt((p1.x-p2.x)*(p1.x-p2.x)+(p1.y-p2.y)*(p1.y-p2.y))
# get a colinear point based on the the root point and the next point
def get_colinear_point(rp,p):
    tx=p.x-rp.x
    ty=p.y-rp.y
    return Point(rp.x-tx,rp.y-ty)