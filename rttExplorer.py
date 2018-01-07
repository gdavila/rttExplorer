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
    parserOPt.add_argument('-o', metavar = 'outFile', type = str, help = 'File name to save the results', default = defaults.scamper.monitorname)

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
    targets = []
    
    
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
        time.sleep(0.1)
        t.start()
