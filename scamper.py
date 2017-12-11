#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CoNexDat
    Grupo de investigación de redes complejas y comunicación de datos
    Facultad de Ingenieria 
    Universidad de Buenos Aires, Argentina

@author: Gabriel Davila Revelo
"""

import defaults
import time
from subprocess import Popen, PIPE

class scamperError(Exception):
    """scamper base error"""
    
class commitError(scamperError):
    """raised when no probe to commit"""
    
class runError(scamperError):
    """raised when no probes to run"""
    

class scamper():
    """A scamper instance.
    Class Attributes:
        command:
            
    Instance Attributes:
        pps:
        window:
        monitorname:
        outfile:
        filetype:
        IPtarget:
        probe:
        probes:
    
    Methods:
        newTraceProbe(IPtarget):
        commitProbe():
        run():     
    """
    
    command = defaults.scamper.command
    ppsArg = '-p'
    windowArg = '-w'
    monitornameArg = '-M'
    outfileArg = '-o'
    optionsArg = '-O'
    cmdsArg = '-I'
    
    
    def __init__(self):
        self.pps = defaults.scamper.pps
        self.window = defaults.scamper.window
        self.monitorname = defaults.scamper.monitorname
        self.outfile = defaults.scamper.outfile
        self.filetype = defaults.scamper.filetype #text, json, warts
        self.probe = None
        self.probes = list()

        return 
     
        
    def newTraceProbe(self, IPtarget):
        self.probe = trace(IPtarget)
        return self.probe
    
            
    def newPingProbe(self, IPtarget):
        self.probe = ping(IPtarget)
        return self.probe

    
    def commitProbe(self):
        if self.probe == None: raise commitError('No probe to commit')
            
        self.probes.append(self.probe)
        self.probe = None
        return

    
    def run(self, outfile= None):
        if self.probes==list(): raise runError('No probes to run')
            
        self.command = ' '.join('\"' + probe.getCmd() + '\"' for probe in self.probes)

        self.cmdList = []
        

        for probe in self.probes:
            self.cmdList = self.cmdList+ [probe.getCmd()]
            
        self.cmdList = [ scamper.command,
                 scamper.ppsArg, self.pps,
                 scamper.windowArg, self.window,
                 scamper.monitornameArg, self.monitorname,
                 #scamper.outfileArg, self.outfile,
                 scamper.optionsArg, self.filetype,
                 scamper.cmdsArg,
                 ] + self.cmdList
        
        self.command = ' '.join([scamper.command,
                                 scamper.ppsArg, self.pps,
                                 scamper.windowArg, self.window,
                                 scamper.monitornameArg, self.monitorname,
                                 #scamper.outfileArg, self.outfile,
                                 scamper.optionsArg, self.filetype,
                                 scamper.cmdsArg, self.command,
                                 ])         
        
        #print (self.command)
        process = Popen(self.cmdList, stdout=PIPE, stderr=PIPE)
        self.date = time.strftime("%D %H:%M:%S +0000", time.gmtime())
        process.wait()
        self.stdout, self.stderr = process.communicate()
        
        if self.stderr: raise runError(self.stderr, self.command)
        
        if  outfile != None:
            with open(outfile, 'ab') as file:
                file.write(self.stdout)
                
        return self.stdout, self.stderr
    

class trace():
    """A trace scamper instance.
    Initialization:
        trace(IPtarget):
            
    Instance attributes:
        IPtarget:
        method:
        dport:
        sport:
        firsthop:
        wait:
        maxttl:
        gaplimit:
        attempts:
        tos:
         
    Methods:
        getCmd():   
    """
    
    
    command = 'trace'
    methodArg = '-P'
    dportArg = '-d'
    sportArg = '-s'
    firsthopArg = '-f'
    waitArg = '-w'
    maxttlArg = '-m'
    gaplimitArg = '-g'
    QArg = '-Q'
    #QArg = ''
    attemptsArg = '-q'
    tosArg = '-t'
    
    
    def __init__(self, IPtarget):
        self.IPtarget = IPtarget
        self.method = defaults.trace.method
        self.dport = defaults.trace.dport
        self.sport = defaults.trace.sport
        self.firsthop = defaults.trace.firsthop
        self.wait = defaults.trace.wait
        self.maxttl = defaults.trace.maxttl
        self.gaplimit = defaults.trace.gaplimit
        self.attempts = defaults.trace.attempts
        self.tos = defaults.trace.tos
        self.__cmd = ''
        return
    
    
    def getCmd(self):
        self.__cmd = ' '.join([trace.command, \
                              trace.methodArg, self.method,\
                              trace.dportArg, self.dport,\
                              trace.sportArg, self.sport,\
                              trace.firsthopArg, self.firsthop,\
                              trace.waitArg, self.wait,\
                              trace.maxttlArg, self.maxttl,\
                              trace.gaplimitArg, self.gaplimit,\
                              trace.QArg,\
                              trace.attemptsArg, self.attempts,\
                              trace.tosArg, self.tos,\
                              self.IPtarget,\
                              ])
        return self.__cmd
    
    
class ping():
    """A ping scamper instance.
    Initialization:
        ping(IPtarget):
            
    Instance attributes:
        IPtarget:
        method:
        dport:
        sport:
        wait:
        ttl:
        probecount:
        tos:
         
    Methods:
        getCmd():   
    """
    
    
    command = 'ping'
    methodArg = '-P'
    dportArg = '-d'
    sportArg = '-F'
    waitArg = '-i'
    ttlArg = '-m'
    probecountArg = '-c'
    tosArg = '-z'
    
    
    def __init__(self, IPtarget):
        self.IPtarget = IPtarget
        self.method = defaults.ping.method
        self.dport = defaults.ping.dport
        self.sport = defaults.ping.sport
        self.wait = defaults.ping.wait
        self.ttl = defaults.ping.ttl
        self.probecount = defaults.ping.probecount
        self.tos = defaults.ping.tos
        self.__cmd = ''
        return
    
    
    def getCmd(self):
        self.__cmd = ' '.join([ping.command, \
                              ping.methodArg, self.method,\
                              ping.dportArg, self.dport,\
                              ping.sportArg, self.sport,\
                              ping.waitArg, self.wait,\
                              ping.ttlArg, self.ttl,\
                              ping.probecountArg, self.probecount,\
                              ping.tosArg, self.tos,\
                              self.IPtarget,\
                              ])
        return self.__cmd