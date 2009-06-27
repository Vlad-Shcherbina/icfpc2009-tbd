'''
Created on 27 Jun 2009

@author: Maksims Rebrovs
'''

import glob

from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext


setup(
  name = 'VM',
  cmdclass = {'build_ext': build_ext},
  ext_modules=[
     Extension(
       "VorberVM",                 # name of extension
       ["VorberVM.pyx", "VM.cpp"],           # filename of our Cython source
       language="c++",              # this causes Cython to create C++ source
       include_dirs=["C:\Python26\include"],          # usual stuff
       extra_link_args=[""],       # if needed
       )
     ]
)


