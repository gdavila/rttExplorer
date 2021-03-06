#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CoNexDat
    Grupo de investigación de redes complejas y comunicación de datos
    Facultad de Ingenieria 
    Universidad de Buenos Aires, Argentina

@author: Gabriel Davila Revelo
"""

import scamper
import tracebox
import json
import socket
import time
import os
import logging
import multiprocessing

def tbFormater(tb):
    
    jsonPath = json.loads(tb.stdout)
    jsonPath['type'] = 'tracebox'
    jsonPath['method'] = tb.method()
    jsonPath['dst'] = tb.IPtarget
    jsonPath['src'] = get_localip_address()
    jsonPath['sport'] = tb.probe.protocol.sport
    jsonPath['dport'] = tb.probe.protocol.dport
    jsonPath['start'] = tb.start
    jsonPath['date'] = tb.date
    return jsonPath

def get_localip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 80))
    return s.getsockname()[0]


    

def seconds(time):
    return time['sec'] + time['usec']/1000000.0


class explorationError(Exception):
    """scamper base error"""
    
class exploration():
    ID = multiprocessing.Value('i', 0)
    offsetSrcPort = multiprocessing.Value('i', 0)
    lock = multiprocessing.Lock()
    
    def __init__(self, 
                 TARGET, 
                 SPORT , 
                 DPORT , 
                 METHOD,
                 OUTFILE,
                 PATH_INTERVAL,
                 RTT_INTERVAL,
                 EXPLORATION_TIME,
                 MIN_TTL ,
                 MAX_TTL ,
                 RTT_TIMEOUT,
                 PATH_TIMEOUT):
        
        #print ("<Exploration ID{} >".format(exploration.ID.value))
        
        self.ID = exploration.ID.value
        self.sport =  str(int(SPORT) + exploration.ID.value + exploration.offsetSrcPort.value)
        
        self.target = TARGET
        self.checkSrcPort()
        self.dport = DPORT
        self.method =  METHOD
        self.minRTT = MIN_TTL
        self.maxRTT = MAX_TTL
        self.pathTimeout = PATH_TIMEOUT 
        self.rttTimeout = RTT_TIMEOUT
        self.exploName = OUTFILE 
        self.outFile = OUTFILE + '.json'
        self.refreshPathTime = PATH_INTERVAL  #minutes
        self.refreshRttTime = RTT_INTERVAL  #second
        self.duration = EXPLORATION_TIME  #minutes
        self.resultsFolder = os.path.dirname(os.path.abspath(__file__))+'/results'
        self.rttFileName = self.resultsFolder + '/rtt_' + self.outFile
        self.pathFileName = self.resultsFolder + '/path_' + self.outFile
        self.logsFolder = os.path.dirname(os.path.abspath(__file__))+'/logs'
        self.logFileName = self.logsFolder + '/' + OUTFILE +'.log'
        self.iniFile()
        self.iniLogger()
        self.rttMeasError = False
        self.pathDiscError = False
        
        exploration.lock.acquire()
        exploration.ID.value += 1
        exploration.lock.release()

    
    def iniLogger(self):
        logging.basicConfig(level=logging.INFO, 
                            filename=self.logFileName,
                            format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        self.logger = logging.getLogger()
        self.logger.info("<Exploration ID{}> ".format(self.ID) +  "  {} ".format(self.target)  + " START")
        
    def iniFile(self):
        if exploration.ID.value == 0: 
            try: os.remove(self.rttFileName) 
            except FileNotFoundError:pass
            try: os.remove(self.pathFileName) 
            except FileNotFoundError:pass


    def SrcPortBussy(self):
        while True:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                s.bind(('', int(self.sport))) ## Try to open port
            except OSError as e:
                if e.errno == 98 or e.errno ==48: ## Errorno 98 means address already bound
                    return True
                raise e
            #time.sleep(0.1)
            s.close()
            return False

    def checkSrcPort(self):
        while self.SrcPortBussy():
            exploration.lock.acquire()
            exploration.offsetSrcPort.value+=1
            exploration.lock.release()
            self.logger.error("<Exploration ID{}> ".format(self.ID) + '[SrcPortBussy] '+ self.sport)
            self.sport = str(int(self.sport) + exploration.offsetSrcPort.value)
            
    def pathDiscovery(self):
        self.tb = tracebox.tracebox(self.target)
        self.tb.hops_min = self.minRTT
        self.tb.hops_max = self.maxRTT
        self.tb.method(self.method)
        self.tb.sport(self.sport)
        self.tb.dport(self.dport)
        self.tb.timeout = self.pathTimeout
        #time.sleep(1)
        try:
            self.tb.run()
        except tracebox.runError as e:
            if not (self.pathDiscError):
                self.logger.error("<Exploration ID{}> ".format(self.ID) + '[tracebox]'+ str(e))
                self.logger.info("<Exploration ID{}> ".format(self.ID)  + 'Internet Paths lost. RTT Measurements stoped')  
            self.path = {}
            self.pathDiscError = True
            return
        
        if self.pathDiscError:
            self.logger.info("<Exploration ID{}> ".format(self.ID) + 'Internet Paths recovered. RTT Measurements restarted')
            self.pathDiscError = False
        self.path = tbFormater(self.tb)
        self.path['explorationName'] =  self.exploName
        with open(self.pathFileName, 'a') as f:
            f.write(json.dumps(self.path)+'\n')
            

    
    def rttMeasurement(self):
        self.sc = scamper.scamper()
        for hop in self.path['Hops']:
            if hop['from'] == '*': continue
            self.sc.newTraceProbe(self.target)
            self.sc.probe.sport = self.sport
            self.sc.probe.dport = self.dport
            self.sc.probe.wait = self.rttTimeout
            if self.method == 'UDP': 
                self.sc.probe.method = 'UDP-PARIS'
            else: self.sc.probe.method = self.method
            self.sc.probe.firsthop= str(hop['hop'])
            self.sc.probe.maxttl= str(hop['hop'])
            self.sc.commitProbe()
        try:
            self.sc.run()
        except scamper.runError as e:
            #print ('error rtt', self.rttMeasError)
            if not(self.rttMeasError): 
                self.logger.error("<Exploration ID{}> ".format(self.ID) + '[scamper]'+ str(e))
                self.logger.info("<Exploration ID{}> ".format(self.ID) + 'RTT Measurements lost. Triying again.')
            self.rttMeas = []
            self.rttMeasError = True
            return
        #print (self.sc.command)
        if self.rttMeasError: 
            self.logger.info("<Exploration ID{}> ".format(self.ID) + "RTT Measurements restarted")
            self.rttMeasError = False
        
        meassurements = self.sc.stdout.decode("utf-8", "strict")
        if meassurements.split('\n') != [] : 
            meassurements=meassurements.split('\n')[1:len(meassurements.split('\n'))-2]
            
        self.rttMeas = []
        
        for meassurement in meassurements:
            jsonMeassurement = json.loads(meassurement)
            jsonMeassurement ['explorationName'] =  self.exploName
            self.rttMeas.append (jsonMeassurement)
            with open(self.rttFileName, 'a') as f:
                f.write(json.dumps(jsonMeassurement)+'\n')
        
    
    def run(self):
        self.pathDiscovery()
        self.start = time.time()
        while self.isPending():
            try:
                if time.time() - seconds(self.path['start']) >= self.refreshPathTime * 60 :
                    self.pathDiscovery()
                    
                self.rttMeasurement()
                timeSinceLastRtt = time.time() - seconds(self.rttMeas[0]['start'])
                
                if timeSinceLastRtt < self.refreshRttTime:
                    time.sleep(self.refreshRttTime - timeSinceLastRtt)
                    
            except KeyError:
                """ no path discovered yet. TRY TO DISCOVER AGAIN"""
                self.pathDiscovery()
                continue

            except IndexError:
                """ rtt not computed. TRY AGAIN"""
                continue
                
            #    continue
        self.logger.info("<Exploration ID{}> ".format(self.ID) + "FINISH")

        
    def isPending(self):
        if time.time() - self.start >= self.duration * 60: return False
        else: return True

        
