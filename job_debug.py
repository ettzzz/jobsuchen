# -*- coding: utf-8 -*-
"""
Created on Sun Jul 14 09:00:22 2019

@author: ert
"""

"""
debug part
sys.exc_info() 
    print(exc_type)
    print(exc_value)
    print(exc_tb)
"""

import traceback
import sys

class jobDebug():
    def __init__(self):
        pass
    
    def session_bug(self,e):
        exc_type, exc_value, exc_tb = sys.exc_info()
        pass
    
    def get_bug(self,e):
        pass
    
    def css_bug(self,e):
        pass
    
    