#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CoNexDat
    Grupo de investigación de redes complejas y comunicación de datos
    Facultad de Ingenieria 
    Universidad de Buenos Aires, Argentina

@author: Gabriel Davila Revelo
"""

import argparse
import exploration
import defaults
import threading
import time
import pymongo, mongo
import json
import os
import logging
import socket 


def uploadColletion(collection, srcFile):
    with open(srcFile) as file:
        data = []
        maxLines = 10000
        counter =0
        for line in file:
            counter+=1
            try:
                data.append(json.loads(line))
            except Exception as e:
                print(("<MongoDB> " + "JSON: " + str(e)))
                continue
            if counter == maxLines:
                try:
                    collection.insert_many(data, ordered = False)
                except pymongo.errors.BulkWriteError as e:
                    print("<MongoDB> " + e.details['writeErrors'][0]['errmsg'])
                    data =[]
                    break
                counter=0
                data=[]
        if data:
            try:
                collection.insert_many(data)
            except pymongo.errors.BulkWriteError as e:
                print("<MongoDB> " + e.details['writeErrors'][0]['errmsg'])
                pass
    return 


print("<MongoDB> Start Uploading data")



rttFile = 'results/rtt_raspberrypi.json'
pathFile = 'results/path_raspberrypi.json'
uri_mongodb='mongodb://rttExplorer:rttExplorer@localhost:12345/rttExploration'
client = pymongo.MongoClient(uri_mongodb)
db = client.rttExploration
collection = db.rtt

print("<MongoDB> Uploading rtt data...")
uploadColletion(collection, rttFile)

collection = db.path
print("<MongoDB> Uploading path data...")

uploadColletion(collection, pathFile)
    
print("<MongoDB> Data Uploaded")


 


    
