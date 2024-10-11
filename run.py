# -*- coding: utf-8 -*-
"""
@authors: noedi
    
September 2024
"""

# Import required modules
from load_profiles import simulate
import os
if __name__ == '__main__':
    path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Config.json")
    simulate(path, disp=True)
    