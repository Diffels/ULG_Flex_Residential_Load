# -*- coding: utf-8 -*-
"""
@authors: noedi
    
September 2024
"""

# Import required modules
from load_profiles import simulate

if __name__ == '__main__':
    path = r"C:\Users\noedi\OneDrive - Universite de Liege\Ordi - Bureau\Ordi - ULG\Job - Load Shifting\ULG_Flex_Residential_Load\Config.json"
    simulate(path, disp=True)
    