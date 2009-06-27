from __future__ import with_statement

import psyco
psyco.full()

import sys
import re

from threading import Thread	
from math import *
from random import *
import time

from orbitvm import OrbitVM

from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
#from OpenGLContext import testingcontext
#BaseContext, MainFunction = testingcontext.getInteractive()
#from OpenGLContext.arrays import array
#from OpenGLContext.scenegraph.text import glutfont
#from pyglet import image, font

name = 'OrbitVIS'


def circle(x,y,r,segments=22):
	glBegin(GL_LINE_LOOP)
	for i in range(segments):
		a = 2*3.1415/segments*i
		glVertex2f(x+r*cos(a),y+r*sin(a))
	glEnd()

def drawText( value, x,y,  windowHeight, windowWidth, step = 18 ):
	"""Draw the given text at given 2D position in window
	"""
	#glMatrixMode(GL_PROJECTION);
	# For some reason the GL_PROJECTION_MATRIX is overflowing with a single push!
	# glPushMatrix()
	#matrix = glGetDouble( GL_PROJECTION_MATRIX )
	
	#glLoadIdentity();
	#glOrtho(0.0, windowHeight or 32, 0.0, windowWidth or 32, -1.0, 1.0)
	#glMatrixMode(GL_MODELVIEW);
	#glPushMatrix();
	#glLoadIdentity();
	glRasterPos2i(x, y);
	lines = 0
##	import pdb
##	pdb.set_trace()
	for character in value:
		if character == '\n':
			glRasterPos2i(x, y+(lines*18))
			lines = lines+1
		else:
			glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(character));
	#glPopMatrix();
	#glMatrixMode(GL_PROJECTION);
	# For some reason the GL_PROJECTION_MATRIX is overflowing with a single push!
	# glPopMatrix();
	#glLoadMatrixd( matrix ) # should have un-decorated alias for this...
	
	#glMatrixMode(GL_MODELVIEW);


class StatsDrawer:
	def __init__(self, vm):
		self.vm = vm
	def __call__(self):
		vm = self.vm
		#glPushMatrix();
		glMatrixMode(GL_PROJECTION);
		glOrtho(0.0, 100, 0.0, 100, -1.0, 1.0)
		glLoadIdentity();
		glColor3f(1,1,1)
		drawText("Fuel:%d\nsx: %09f\nsy:%09f"%(vm.stats.fuel, vm.stats.sx, vm.stats.sy),
				 0, 0, 100, 100)
		#glPopMatrix();
		
				
class SolutionThread(Thread):
	def __init__(self, vm, solver):
		Thread.__init__(self)
		self.vm = vm
		self.solver = solver
		self.term = 0
		
	def run(self):
		while not self.term:
			self.vm.step()
			if self.solver:
				self.solver.step()

			time.sleep(0.00000002+0.00010)
			score = self.vm.readport(0)
			type = self.vm.type+self.vm.config
			if score != 0:
				self.solution = self.vm.getVMImpl().getSolution()
				fname = "solutions/sol_%04d_%06d_%s.osf"%(type, score,
			                re.sub(r'[\s:]', "_", time.ctime()))
				with open(fname,'wb') as fout:
				    fout.write(self.solution)
				print "stored into "+ fname
				break
		return

	def terminate(self):
		self.term = 1
		return
	
	def _idle(self):
		1
		#
					
				
				
class Visualizer(Thread):
	def __init__(self, vm, solver, scaler = 0, keyHandler = None, mouseHandler = None):
		Thread.__init__(self)
		self.terminate = False
		self.drawers = []
		
		self.vm = vm
		self.solver = solver
		
		self.keyHandler = keyHandler
		self.mouseHandler = mouseHandler
		
		self.sx = 0
		self.sy = 0
		self.sradius = OrbitVM.EarthRadius/15

		""" if scaling back is required """
		self.scaler = scaler
		
		self.solutionThread = SolutionThread(vm, solver)
		
	def registerDrawer(self,drawer):
		self.drawers.append(drawer)
		
	def earth(self):
		glColor3f(0,1,0)
		circle(0, 0, OrbitVM.EarthRadius)

	def moon(self, x, y):
		glPushMatrix()
		glTranslatef(x, y, 0)
		glColor3f(1,1,1)
		circle(0, 0, OrbitVM.EarthRadius/5)
		glPopMatrix()

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
		circle(0, 0, self.sradius*0.5)
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

		if self.lastmax < abs(x)*1.1:
			self.lastmax = abs(x)*1.1
		if self.lastmax < abs(y)*1.1:
			self.lastmax = abs(y)*1.1
		
		if self.sx < self.lastmax:
			self.sx = self.lastmax
		if self.sy < self.lastmax:
			self.sy = self.lastmax

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

		# start!
		self.solutionThread.start()

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
			self.vm.terminate()
			return
			#exit()
		time.sleep(0.02)
		glutPostRedisplay()


	def display(self):

		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		
		self.lastmax = 0
		self.relocate(OrbitVM.EarthRadius, OrbitVM.EarthRadius)
		
		glOrtho(-self.sx,
				self.sx,
				-self.sx,
				self.sx, -10,10)
		
		glMatrixMode(GL_MODELVIEW)

		glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)


		#self.font.render( "ffun!" )

		# earth
		self.earth()
		
		# self
		sax = self.vm.readport(0x2)
		say = self.vm.readport(0x3)
		#print "sat x=% 0f y=% 0f"%(sax, say) 
		self.satellite(sax, say)
		
		#print "t %d         sat2 x=% 0f y=% 0f"%(self.vm.gettime(), sax, say)

		if   self.vm.gettype() == OrbitVM.Hohmann:
			1
		elif self.vm.gettype() == OrbitVM.MeetnGreet or self.vm.gettype() == OrbitVM.Eccentric:
			sax = sax - self.vm.readport(0x4)
			say = say - self.vm.readport(0x5)
			
			self.satellite1(sax, say)
		elif self.vm.gettype() == OrbitVM.ClearSkies:
			fx = sax - self.vm.readport(0x4)
			fy = say - self.vm.readport(0x5)
			ffuel = self.vm.readport(0x6)
			self.fuelstation(sax, say, ffuel)
			for c in range(11):
				sanx = sax - self.vm.readport(0x7+c*3)
				sany = say - self.vm.readport(0x8+c*3)
				self.satellite1(sanx, sany)

			sanx = sax - self.vm.getVMImpl().state.moon[0]
			sany = say - self.vm.getVMImpl().state.moon[1]
			self.moon(sanx, sany)

		for drawer in self.drawers:
			drawer()

		if self.scaler:
			self.sx = self.sx*0.95
			self.sy = self.sy*0.95

		glutSwapBuffers()
