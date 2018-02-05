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
import pymongo
import json
import os
import logging


def get_args():
    '''This function parses and return arguments passed in'''
    parser = argparse.ArgumentParser(prog = 'rttmeas', description = 'script to measure the rrt along a path')

    parserReq = parser.add_argument_group('required arguments:')
    group = parserReq.add_mutually_exclusive_group(required = True)
    group.add_argument('-i', metavar = 'ipTarget' , type = str, help = 'IP target')
    group.add_argument('-I', metavar = 'inputTargetFile' ,type = str, help = 'input file containing a list of IP targets line by line')
    parserReq.add_argument('-t', metavar = 'explorationTime', help = 'Duration time of the exploration (minutes)', type = int, required = True)

    parserOPt = parser.add_argument_group('optional arguments:')
    parserOPt.add_argument('-D', metavar = 'pathInterval', help = 'time interval between path discovery probes (minutes). Default is 5',type = int, default = 5)
    parserOPt.add_argument('-T', metavar = 'rttInterval', help = 'time interval between rtt measurement probes (seconds). Default is 1', type = int, default = 1)
    parserOPt.add_argument('-m', metavar = 'method', type = str, help = 'UDP or TCP-ACK. Default is UDP', choices =  ['UDP', 'TCP-ACK'], default = 'UDP')
    parserOPt.add_argument('-f', metavar = 'firstTTL', type = str, help = 'ttl for the first hop used in traceroute. Default is 1', default = '1')
    parserOPt.add_argument('-M', metavar = 'maxTTL', type = str, help = 'max ttl used in traceroute. Default is 20', default = '20')
    parserOPt.add_argument('-d', metavar = 'dstPort',type = str, help = 'destination Port. Default is 44444', default = '44444')
    parserOPt.add_argument('-s', metavar = 'srcPort',type = str, help = 'source Port. Default is 33333', default = '33333')
    parserOPt.add_argument('-o', metavar = 'outFile', type = str, help = 'File name to save the results (exploration name)', default = defaults.scamper.monitorname)
    parserOPt.add_argument('--mongodb', help = 'upload the results in a mongoDB. See defaults.py to change the default mongodb uri', action = 'store_true')

    return parser.parse_args()


def rttExplorer(target, srcPort, dstPort, method, outFile, pathInterval, rttInterval,explorationTime, minTTL, maxTTL):
        probe = exploration.exploration(TARGET = target, 
                     SPORT = srcPort , 
                     DPORT =  dstPort, 
                     METHOD = method,
                     OUTFILE = outFile,
                     PATH_INTERVAL = pathInterval,
                     RTT_INTERVAL = rttInterval,
                     EXPLORATION_TIME = explorationTime,
                     MIN_TTL = minTTL,
                     MAX_TTL = maxTTL) 
        probe.run()


 

def uploadColletion(collection, srcFile):
    with open(srcFile) as file:
        data = []
        maxLines = 10000
        counter =0
        for line in file:
            counter+=1
            data.append(json.loads(line))
            if counter == maxLines:
                collection.insert_many(data)
                counter=0
                data=[]
        if data: collection.insert_many(data)
    return 

if __name__ == '__main__':
    
    cmdParser=get_args()
    ipTarget = cmdParser.i
    inputTargetFile = cmdParser.I
    explorationTime = cmdParser.t
    pathInterval = cmdParser.D
    rttInterval = cmdParser.T
    method = cmdParser.m
    minTTL = cmdParser.f
    maxTTL = cmdParser.M
    dstPort = cmdParser.d
    srcPort = cmdParser.s
    outFile = cmdParser.o
    mongoOption = cmdParser.mongodb
    targets = []
    
    folderLogs = os.path.dirname(os.path.abspath(__file__))+'/logs/'
    logFile = folderLogs + outFile + '.log'
    try: os.remove(logFile) 
    except FileNotFoundError:pass

    logging.basicConfig(level=logging.INFO, 
                        filename=logFile,
                        format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    logger = logging.getLogger()
    logger.info("<rttExplorer> START")
        
        
    if inputTargetFile == None:
        targets.append(ipTarget)
    else:
        with open(inputTargetFile ) as file:
            targets = file.readlines()
    targets = [x.strip() for x in targets]
    
    for target in targets:
        t = threading.Thread(target = rttExplorer, args = (  target, 
                                                         srcPort , 
                                                         dstPort, 
                                                         method,
                                                         outFile,
                                                         pathInterval,
                                                         rttInterval,
                                                         explorationTime,
                                                         minTTL,
                                                         maxTTL,))
        time.sleep(1)
        t.start()

    while (t.isAlive()):
        time.sleep(1)
    
    time.sleep(5)
    logger.info("<rttExplorer> FINISH")
    
    folderResults = os.path.dirname(os.path.abspath(__file__))+'/results/'
    rttFile = folderResults + 'rtt_' + outFile + '.json'
    pathFile = folderResults + 'path_' + outFile + '.json'
    
    if mongoOption:
        logger.info("<MongoDB> Start Uploading data")
        
        
        uri_mongodb=defaults.mongodb.uri
        client = pymongo.MongoClient(uri_mongodb)
        db = client.conexdat
        collection = db.rtt
    
        try:
            uploadColletion(collection, rttFile)
        except Exception as e:
            logger.info("<MongoDB> "+e)
        
        collection = db.path
        try:
            uploadColletion(collection, pathFile)
        except Exception as e:
            logger.info("<MongoDB> "+e)
            
        logger.info("<MongoDB> Data Uploaded")
        
    