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
import defaults


def tbFormater(tb):
    jsonPath = json.loads(tb.stdout)
    jsonPath['type'] = 'tracebox'
    jsonPath['method'] = tb.method()
    jsonPath['dst'] = tb.IPtarget
    jsonPath['src'] = get_localip_address()
    jsonPath['start'] = tb.start
    jsonPath['date'] = tb.date
    return jsonPath

def get_localip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 80))
    return s.getsockname()[0]


    

def seconds(time):
    return time['sec'] + time['usec']/1000000.0

class exploration():
    ID = 0

    
    def __init__(self, TARGET, SPORT = defaults.exploration.sport , DPORT = defaults.exploration.dport, METHOD = defaults.exploration.method):
        self.duration = 5  #minutes
        self.refreshPathTime = 1 #minutes
        self.refreshRttTime = 1  #second
        self.target = TARGET
        self.sport =  str(int(SPORT) + exploration.ID)
        self.dport = DPORT
        self.method =  METHOD
        exploration.ID += exploration.ID 

    
    def pathDiscovery(self):
        print('discovering path...')
        self.tb = tracebox.tracebox(self.target)
        self.tb.sport(self.sport)
        self.tb.dport(self.dport)
        self.tb.method(self.method)
        self.tb.run()
        self.path = tbFormater(self.tb)


    
    def rttMeasurement(self):
        print('measuring rtt...')
        self.sc = scamper.scamper()
        for hop in self.path['Hops']:
            if hop['from'] == '*': continue
            self.sc.newTraceProbe(self.target)
            self.sc.probe.sport = self.sport
            self.sc.probe.dport = self.dport
            self.sc.probe.method = self.method
            self.sc.probe.firsthop= str(hop['hop'])
            self.sc.probe.maxttl= str(hop['hop'])
            self.sc.commitProbe()
        self.sc.run()
        meassurements = self.sc.stdout.decode("utf-8", "strict")
        if meassurements.split('\n') != [] : 
            meassurements=meassurements.split('\n')[1:len(meassurements.split('\n'))-2]
        self.rttMeas = []
        for meassurement in meassurements:
            self.rttMeas.append (json.loads(meassurement))
        
        print (self.rttMeas)


    
    def run(self):
        self.pathDiscovery()
        self.start = time.time()
        
        while self.isPending():
            if time.time() - seconds(self.path['start']) >= self.refreshPathTime * 60 :
                self.pathDiscovery()
                
            self.rttMeasurement()
            timeSinceLastRtt = time.time() - seconds(self.rttMeas[0]['start'])
            
            if timeSinceLastRtt < self.refreshRttTime:
                time.sleep(self.refreshRttTime - timeSinceLastRtt)
        

        
    def isPending(self):
        if time.time() - self.start >= self.duration * 60:
            return False
        else: return True

        