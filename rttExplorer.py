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


def get_args():
    '''This function parses and return arguments passed in'''
    parser = argparse.ArgumentParser(prog = 'rttExplorer', description = 'script to measure the rrt along a path')

    parserReq = parser.add_argument_group('required arguments:')
    group = parserReq.add_mutually_exclusive_group(required = True)
    group.add_argument('-i', metavar = 'ipTarget' , type = str, help = 'IPv4 target')
    group.add_argument('-I', metavar = 'inputTargetFile' ,type = str, help = 'input file with a list of IPv4 targets line by line')
    parserReq.add_argument('-t', metavar = 'explorationTime', help = 'Duration time of the exploration (minutes)', type = int, required = True)

    parserOPt = parser.add_argument_group('optional arguments:')
    parserOPt.add_argument('-D', metavar = 'pathInterval', help = 'time interval between path discovery probes (minutes). Default is 5',type = int, default = 5)
    parserOPt.add_argument('-T', metavar = 'rttInterval', help = 'time interval between rtt measurement probes (seconds). Decimals allowed. Default is 1.0', type = float, default = 1)
    parserOPt.add_argument('-m', metavar = 'method', type = str, help = 'UDP or TCP-ACK. Default is UDP', choices =  ['UDP', 'TCP-ACK'], default = defaults.exploration.method)
    parserOPt.add_argument('-f', metavar = 'firstTTL', type = str, help = 'ttl for the first hop used in traceroute. Default is 1', default = '1')
    parserOPt.add_argument('-M', metavar = 'maxTTL', type = str, help = 'max ttl used in traceroute. Default is 20', default = '20')
    parserOPt.add_argument('-d', metavar = 'dstPort',type = str, help = 'destination Port. Default is 44444', default = defaults.exploration.dport)
    parserOPt.add_argument('-s', metavar = 'srcPort',type = str, help = 'source Port. Default is 33333', default= defaults.exploration.sport )
    parserOPt.add_argument('-o', metavar = 'outFile', type = str, help = 'File name to save the results (exploration name)', default = defaults.scamper.monitorname)
    parserOPt.add_argument('--mongodb', help = 'upload the results in a mongoDB. See defaults.py to change the default mongodb uri', action = 'store_true')
    parserOPt.add_argument('--rttTimeout', type = str, help = 'Timeout for rtt probes. Default is 1. It must be lower or at least equal that rttInterval', default =defaults.trace.wait )
    parserOPt.add_argument('--pathTimeout', type = str, help = 'Timeout for rtt probes. Default is 1', default= defaults.tracebox.timeout)


    return parser.parse_args()


def rttExplorer(target, srcPort, dstPort, method, outFile, pathInterval, rttInterval,explorationTime, minTTL, maxTTL,rttTimeout, pathTimeout ):
        probe = exploration.exploration(TARGET = target, 
                     SPORT = srcPort , 
                     DPORT =  dstPort, 
                     METHOD = method,
                     OUTFILE = outFile,
                     PATH_INTERVAL = pathInterval,
                     RTT_INTERVAL = rttInterval,
                     EXPLORATION_TIME = explorationTime,
                     MIN_TTL = minTTL,
                     MAX_TTL = maxTTL,
                     RTT_TIMEOUT = rttTimeout,
                     PATH_TIMEOUT = pathTimeout) 
        probe.run()

                 
 
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
                logger.info(("<MongoDB> " + "JSON: " + str(e)))
                continue
            if counter == maxLines:
                try:
                    collection.insert_many(data, ordered = False)
                except pymongo.errors.BulkWriteError as e:
                    logger.info("<MongoDB> " + e.details['writeErrors'][0]['errmsg'])
                    data =[]
                    break
                counter=0
                data=[]
        if data:
            try:
                collection.insert_many(data)
            except pymongo.errors.BulkWriteError as e:
                logger.info("<MongoDB> " + e.details['writeErrors'][0]['errmsg'])
                pass
    return 


def timed_join_all(jobs, timeout):
    start = cur_time = time.time()
    while cur_time <= (start + timeout):
        for job in jobs:
            if not job.is_alive():
                job.join()
        time.sleep(1)
        cur_time = time.time()

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
    rttTimeout = cmdParser.rttTimeout
    pathTimeout = cmdParser.pathTimeout
    targets = []
    
    folderLogs = os.path.dirname(os.path.abspath(__file__))+'/logs/'
    logFile = folderLogs + outFile + '.log'
    try: os.remove(logFile) 
    except FileNotFoundError:pass

    logging.basicConfig(level=logging.INFO, 
                        filename=logFile,
                        format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    logger = logging.getLogger()
    
        
        
    if inputTargetFile == None:
        targets.append(ipTarget)
    else:
        with open(inputTargetFile ) as file:
            targets = file.readlines()
    targets = [x.strip() for x in targets]
    
    if float(rttTimeout) >  rttInterval: 
        #rttInterval = float(rttTimeout)
        logger.info("<rttExplorer> rttInterval is lower than 1 second. The periodicity is not guaranteed".format(rttTimeout))
    
    logger.info("<rttExplorer> START")
    #print(mongoOption)
    
    jobs = []
    
    for target in targets:
        try:
            host = socket.gethostbyname(target)
        except Exception as e:
            logger.info("<MongoDB> "+ target +" " + str(e))
            continue
        
        t = threading.Thread(target = rttExplorer, name = target, args = (host, 
                                                         srcPort , 
                                                         dstPort, 
                                                         method,
                                                         outFile,
                                                         pathInterval,
                                                         rttInterval,
                                                         explorationTime,
                                                         minTTL,
                                                         maxTTL,
                                                         rttTimeout,
                                                         pathTimeout))
        
        jobs.append(t)
        time.sleep(1)
        t.start()
     
        
    timed_join_all(jobs, (explorationTime + 10 )* 60  )
    
    for job in jobs:
        if job.is_alive(): 
            logger.info("<rttExplorer>  Timeout in job thread: " + job.getName())
            job.terminate()
        
    #for job in jobs:
    #    job.join(explorationTime*60 + 600)
    #try : 
        #while (t.isAlive()):
        #    time.sleep(5)    
    #except NameError: 
    #    logger.info("Name Error")
    #    pass

    #time.sleep(5)
    
    logger.info("<rttExplorer> FINISH")
    
    folderResults = os.path.dirname(os.path.abspath(__file__))+'/results/'
    rttFile = folderResults + 'rtt_' + outFile + '.json'
    pathFile = folderResults + 'path_' + outFile + '.json'
    
    print(mongoOption)
    if mongoOption:
        logger.info("<MongoDB> Start Uploading data")
        
        uri_mongodb=mongo.uri
        client = pymongo.MongoClient(uri_mongodb)
        db = client.conexdat
        collection = db.rtt
    
        logger.info("<MongoDB> Uploading rtt data...")
        uploadColletion(collection, rttFile)
        
        collection = db.path
        logger.info("<MongoDB> Uploading path data...")
        uploadColletion(collection, pathFile)
            
        logger.info("<MongoDB> Data Uploaded")
        
    