#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CoNexDat
    Grupo de investigación de redes complejas y comunicación de datos
    Facultad de Ingenieria 
    Universidad de Buenos Aires, Argentina

@author: Gabriel Davila Revelo
"""

import exploration
import schedule
import signal
import sys

        
def signal_handler(signal, frame):
    print('You pressed Ctrl+C!')
    schedule.clear()
    sys.exit(0)

def main():

    targets = ['200.45.32.4']    
    
    signal.signal(signal.SIGINT, signal_handler)
    
    for target in targets:
        explorer = exploration.exploration(target)
        explorer.run()
    

    
main()