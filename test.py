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
import sys, pymongo, json

"""       
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
"""

def uploadColletion(collection, srcFile):
    with open(srcFile) as f:
        data = []
        maxLines = 1000
        counter =0
        for line in f:
            counter+=1
            data.append(json.loads(line))
            if counter == maxLines:
                collection.insert_many(data)
                counter=0
                data=[]
        if data: collection.insert_many(data)
    return
 


file = 'results/rtt_Fernandos-MacBook-Air.local.json'
uri_mongodb='mongodb://conexdat:14058712@ds163656.mlab.com:63656/conexdat'
client = pymongo.MongoClient(uri_mongodb)
db = client.conexdat
collection = db.test_collection
try:
    uploadColletion(collection, file)
except FileNotFoundError:
    print ('A')
except Exception as e:
    print(e)
    