import sys,random
import math
from OpenGL.GL import *
import glfw
from helper import *

#list to store node in
nodes=[]
#position of the mouse 
mx=0
my=0
#dimension of window
width=1000
height=1000
#grabbed point object
grabbedNode=None
grabbedHandle=None


def addNode(x,y):
    new_node=Node(x,y)
    #if the node list have no nodes, add one to the list
    if(len(nodes)==0):
        new_node.addHandle1(x,y+50)
        nodes.append(new_node)
        return 0
    # if there are more than 2 nodes
    if(len(nodes)!=1):
        #calculate the distance front/back distance to determine what handle to add
        front_dist=euclid_dist(new_node,nodes[0])
        back_dist=euclid_dist(new_node,nodes[-1])
        if(front_dist<=back_dist):
            #add handle1 and get the colinear point to get the handle2
            new_node.addHandle1(x,y+50)
            previous_endpoint=nodes[0]
            colinear=get_colinear_point(previous_endpoint,previous_endpoint.handle1)
            previous_endpoint.addHandle2(colinear.x,colinear.y)
            nodes.insert(0,new_node)
        else:
            #add handle2 and get the colinear point to get handle1 
            new_node.addHandle2(x,y+50)
            previous_endpoint=nodes[-1]
            colinear=get_colinear_point(previous_endpoint,previous_endpoint.handle2)
            previous_endpoint.addHandle1(colinear.x,colinear.y)
            nodes.append(new_node)
     # if there is only 1 node, only add handle to the list.
    else:
        new_node.addHandle2(x,y+50)
        nodes.append(new_node)
#move the point and bind to new position
def moveAndBind(point,x_loc,y_loc):
    point.x=x_loc
    point.y=y_loc
    point.x=max(5,min(point.x,width-10))
    point.y=max(5,min(point.y,height-10))
#reset function for the pointer and node list
def reset():
    global grabbedNode
    global grabbedHandle
    grabbedNode=None
    grabbedHandle=None
    nodes.clear()
# update function for user input
def update():
    global grabbedHandle
    global grabbedNode
    global window
    #reset if e pressed
    if(glfw.get_key(window,glfw.KEY_E)==glfw.PRESS):
        reset()
    #if a node is grabbed, move and bind node and handles to new point
    if(grabbedNode):
        prev_x=grabbedNode.x
        prev_y=grabbedNode.y
        moveAndBind(grabbedNode,mx,my)
        if(grabbedNode.has_handle1):
            grabbedNode.handle1.move(grabbedNode.x-prev_x,grabbedNode.y-prev_y)
        if(grabbedNode.has_handle2):
            grabbedNode.handle2.move(grabbedNode.x-prev_x,grabbedNode.y-prev_y)
    #if the handle is grabbed, update the corresponding handle only
    elif(grabbedHandle):
        moveAndBind(grabbedHandle,mx,my)
        if(grabbedHandle.type==Handle.type.HANDLE1 and grabbedHandle.parent.has_handle2):
            p=get_colinear_point(grabbedHandle.parent,grabbedHandle)
            grabbedHandle.parent.handle2.set(p.x,p.y)
        if(grabbedHandle.type==Handle.type.HANDLE2 and grabbedHandle.parent.has_handle1):
            p=get_colinear_point(grabbedHandle.parent,grabbedHandle)
            grabbedHandle.parent.handle1.set(p.x,p.y)

#render the nodes list, bezier curve, dotted lines 
def render():
    glClearColor(1,1,1,1)
    glClear(GL_COLOR_BUFFER_BIT)
    if(len(nodes)==0):
        glfw.swap_buffers(window)
        return
    glLineWidth(3)
    #render bezier curve
    glBegin(GL_LINE_STRIP)
    glColor3f(0,0,0)
    for i in range(0,len(nodes)-1,1):
        current_node=nodes[i]
        next_node=nodes[i+1]
        for j in range (0,200,1):
            x=bezier(current_node.x,current_node.handle1.x,next_node.handle2.x,next_node.x,float(j)/200)
            y=bezier(current_node.y,current_node.handle1.y,next_node.handle2.y,next_node.y,float(j)/200)
            glVertex2f(x,y)
    #connecting the last line
    if(nodes):
        glVertex2f(nodes[-1].x,nodes[-1].y)
    glEnd()
    #draw the dotted line between handles and nodes
    glEnable(GL_LINE_STIPPLE)
    glLineWidth(2)
    glLineStipple(8,0x8888)
    glBegin(GL_LINES)
    glColor3f(0.4,0.4,0.4)
    for i in range (0,len(nodes),1):
        current_node=nodes[i]
        if(current_node.has_handle1):
            glVertex2f(current_node.handle1.x,current_node.handle1.y)
            glVertex2f(current_node.x,current_node.y)
        if(current_node.has_handle2):
            glVertex2f(current_node.handle2.x,current_node.handle2.y)
            glVertex2f(current_node.x,current_node.y)
    glEnd()
    glDisable(GL_LINE_STIPPLE)
    #draw the node
    glPointSize(10)
    glColor3f(0,0,1)
    glBegin(GL_POINTS)
    for i in range (0,len(nodes),1):
        current_node=nodes[i]
        glVertex2f(current_node.x,current_node.y)
    glEnd()

    glEnable(GL_POINT_SMOOTH)
    #draw the handle
    glBegin(GL_POINTS)
    glColor3f(1,0,0)
    for i in range(0,len(nodes),1):
        current_node=nodes[i]
        if(current_node.has_handle1):
            glVertex2f(current_node.handle1.x,current_node.handle1.y)
        if(current_node.has_handle2):
            glVertex2f(current_node.handle2.x,current_node.handle2.y)
    glEnd()
    glDisable(GL_POINT_SMOOTH)
    glfw.swap_buffers(window)
# frame buffer callback to adjust viewport/projection
def frame_buffer_callback(window,w,h):
    global width
    global height
    width=w
    height=h
    glViewport(0,0,w,h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0,w,0,h,-1,1)
    render()
# cursor callback to get mx and my
def cursor_callback(window,x_pos,y_pos):
    global mx
    global my
    mx=x_pos
    my=height-y_pos

#mouse callback
def mouse_callback(window,button,action,mods):
    global grabbedNode
    global grabbedHandle
    #if a node is pressed down, determine if it is a node, handle1 or handle 2 is pressed down.
    if(button==glfw.MOUSE_BUTTON_LEFT and action==glfw.PRESS):
        missing_node=True
        for i in range (0,len(nodes),1):
            current_node=nodes[i]
            if(mx>=current_node.x-10 and mx<=current_node.x+10 and
            my>=current_node.y-10 and my<=current_node.y+10):
                grabbedNode=current_node
                missing_node=False
                break;
            if(current_node.has_handle1):
                if(mx>=current_node.handle1.x-10 and mx<=current_node.handle1.x+10 and
            my>=current_node.handle1.y-10 and my<=current_node.handle1.y+10):
                    grabbedHandle=current_node.handle1
                    grabbedHandle.type=Handle.type.HANDLE1
                    missing_node=False
                    break;
            if(current_node.has_handle2):
                if(mx>=current_node.handle2.x-10 and mx<=current_node.handle2.x+10 and
            my>=current_node.handle2.y-10 and my<=current_node.handle2.y+10):
                    grabbedHandle=current_node.handle2
                    grabbedHandle.type=Handle.type.HANDLE2
                    missing_node=False
                    break;
        #if none are true above, add node
        if(missing_node):
            addNode(mx,my)
    #after release, reset the pointer
    if(button==glfw.MOUSE_BUTTON_LEFT and action==glfw.RELEASE):
        grabbedNode=None
        grabbedHandle=None

#set width/height
if(len(sys.argv)==3):
    width=int(sys.argv[1])
    height=int(sys.argv[2])
glfw.init()
#enable 4x multisampling 
glfw.window_hint(glfw.SAMPLES,4)
window = glfw.create_window(int(width),int(height),'A Spline tool', None,None)
#set the callback function to the window.
glfw.make_context_current(window)
glfw.set_mouse_button_callback(window,mouse_callback)
glfw.set_cursor_pos_callback(window,cursor_callback)
glfw.set_framebuffer_size_callback(window,frame_buffer_callback)
glViewport(0,0,width,height)
glfw.window_hint(glfw.SAMPLES,4)
glEnable(GL_MULTISAMPLE)
glEnable(GL_LINE_SMOOTH)
glEnable(GL_BLEND)
#glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)
glMatrixMode(GL_PROJECTION)
glLoadIdentity()
glOrtho(0,width,0,height,-1,1)
while not glfw.window_should_close(window):
    glfw.poll_events()
    update()
    render()

reset()
glfw.terminate()


