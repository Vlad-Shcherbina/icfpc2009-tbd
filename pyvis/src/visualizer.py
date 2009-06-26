import psyco
psyco.full()

from threading import Thread	
import sys
from math import *
from random import *
import time

from orbitvm import OrbitVM

from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
#from OpenGLContext.scenegraph.text import glutfont

name = 'OrbitVIS'


def circle(x,y,r,segments=22):
	glBegin(GL_LINE_LOOP)
	for i in range(segments):
		a = 2*3.1415/segments*i
		glVertex2f(x+r*cos(a),y+r*sin(a))
	glEnd()
				
class Visualizer(Thread):
	def __init__(self, orbitVM, keyHandler = None, mouseHandler = None):
		Thread.__init__(self)
		self.terminate = False
		self.drawers = []
		
		self.orbitVM = orbitVM
		self.keyHandler = keyHandler
		self.mouseHandler = mouseHandler
		
		self.sx = 0
		self.sy = 0
		self.sradius = OrbitVM.EarthRadius/10
		
	def registerDrawer(self,drawer):
		self.drawers.append(drawer)
		
	def earth(self):
		glColor3f(0,1,0)
		circle(0, 0, OrbitVM.EarthRadius)

	def satellite(self, x, y):
		self.relocate(x, y)

		glPushMatrix()
		glTranslatef(x,y,0)
		glColor3f(1,0,0)
		circle(0, 0, self.sradius)
		glPopMatrix()
	
	def satellite1(self, x, y):
		self.relocate(x, y)

		glPushMatrix()
		glTranslatef(x,y,0)
		glColor3f(1,1,0)
		circle(0, 0, self.sradius)
		glPopMatrix()
	
	def fuelstation(self, x, y, fuel):
		self.relocate(x, y)

		glPushMatrix()
		glTranslatef(x,y,0)
		glColor3f(1,0,1)
		circle(0, 0, self.sradius)
		circle(0, 0, self.sradius*1.1)
		glPopMatrix()

	def relocate(self, x, y):

		if self.lastmaxx < abs(x):
			self.lastmaxx = abs(x)
		if self.lastmaxy < abs(y):
			self.lastmaxy = abs(y)
		
		if self.sx < self.lastmaxx:
			self.sx = self.lastmaxx
		if self.sy < self.lastmaxy:
			self.sy = self.lastmaxy

#		for c in self.drawers:
#			if maxsx < abs(c.sx):
#				maxsx = abs(c.sx)
#			if maxsy < abs(c.sy):
#				maxsy = abs(c.sy)

	def run(self):
		glutInit([])
		glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
		glutInitWindowSize(700,700)

		self.window = glutCreateWindow(name)
#		self.font = glutfont.GLUTFontProvider.get( FontStyle( family=["Arial","SANS"]))
#		glEnable(GL_DEPTH_TEST)

		glClearColor(0.,0.,0.,1.)
		glutDisplayFunc(self.display)
		glutIdleFunc(self._idle)
		if (self.keyHandler):
			glutKeyboardFunc(self.keyHandler)
		
		glutMouseFunc(self._mouseHandler)

		glutMainLoop()

	def _mouseHandler(self,button,state,x,y):
		if state != GLUT_DOWN:
			return
#		x = (float(x)/800-0.5)*self.initData.dx
#		y = ((600-float(y))/600-0.5)*self.initData.dy
		if self.mouseHandler is not None:
			self.mouseHandler(button,x,y)
		
	def _idle(self):
		# because it is not a message handler
		if self.terminate:
			if self.window:
				glutDestroyWindow(self.window)
				self.window = None
			return
			#exit()
		time.sleep(0.02)
		self.orbitVM.nextStep()
		glutPostRedisplay()


	def display(self):

		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		
		self.lastmaxx = 0
		self.lastmaxy = 0
		self.relocate(OrbitVM.EarthRadius, OrbitVM.EarthRadius)
		
		glOrtho(-self.sx,
				self.sx,
				-self.sy,
				self.sy, -10,10)
		
		glMatrixMode(GL_MODELVIEW)

		glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)


		#self.font.render( "ffun!" )

		# earth
		self.earth()
		
		# self
		sax = self.orbitVM.readport(0x2)
		say = self.orbitVM.readport(0x3)
		self.satellite(sax, say)

		if   self.orbitVM.gettype() == OrbitVM.Hohmann:
			1
		elif self.orbitVM.gettype() == OrbitVM.MeetnGreet or self.orbitVM.gettype() == OrbitVM.Eccentric:
			sax = sax - self.orbitVM.readport(0x4)
			say = say - self.orbitVM.readport(0x5)
			self.satellite1(sax, say)
		elif self.orbitVM.gettype() == OrbitVM.ClearSkies:
			fx = sax - self.orbitVM.readport(0x4)
			fy = say - self.orbitVM.readport(0x5)
			ffuel = self.orbitVM.readport(0x6)
			self.fuelstation(sax, say, ffuel)
			for c in range(11):
				sax = sax - self.orbitVM.readport(0x7+c*3)
				say = say - self.orbitVM.readport(0x8+c*3)
				self.satellite1(sax, say)
			
		
		#self.rover()
		#for o in self.tele.objects:

		for drawer in self.drawers:
			drawer()

		self.sx = self.sx*0.95
		self.sy = self.sy*0.95


		glutSwapBuffers()
