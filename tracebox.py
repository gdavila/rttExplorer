#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CoNexDat
    Grupo de investigación de redes complejas y comunicación de datos
    Facultad de Ingenieria 
    Universidad de Buenos Aires, Argentina

@author: Gabriel Davila Revelo
"""
import time
import math
import defaults
from subprocess import Popen, PIPE

class traceboxError(Exception):
    """scamper base error"""
    
class commitError(traceboxError):
    """raised when no probe to commit"""
    
class runError(traceboxError):
    """raised when no probes to run"""
    
    

class tracebox():
    """A tracebox instance.
            
    Instance Attributes:
        IPtarget:
        method:
        dport:
        sport:
        hops_min:
        timeout:
        hops_max:
        tos:
    
    Methods:
        newProbe(IPtarget):
        commitProbe():
        run():     
    """
    command = defaults.tracebox.command
    dportArg = '-d'
    hops_minArg = '-M'
    timeoutArg = '-t'
    hops_maxArg = '-m'
    filenameArg = '-f'
    jsonArg = '-j'
    probeArg = '-p' 
    verbose = '-v'
    
    def __init__(self, IPtarget):
        self.command= defaults.tracebox.command
        self.hops_min = defaults.tracebox.hops_min
        self.timeout = defaults.tracebox.timeout
        self.hops_max = defaults.tracebox.hops_max
        self.tos = defaults.tracebox.tos
        self.pcapfile = defaults.tracebox.outfile
        self.jsonfile = defaults.tracebox.jsonfile
        self.IPtarget = IPtarget
        self.method(defaults.tracebox.method)
        self.sport(defaults.tracebox.sport)
        self.dport(defaults.tracebox.dport)
        
    def _buildProbe(self):
        self.buildedProbe = ' / '.join([self.probe.ip.getPckt(),
                                      self.probe.protocol.getPckt(),
                                        ])
        #self.buildedProbe = '\"' + self.buildedProbe + '\"'
        return 
    
    def method(self, method = None):
        if method == None: return self.methodValue
        
        self.methodValue = method
        if self.methodValue == 'TCP-ACK':
            self.probe = protocol.tcp()
            self.probe.protocol.flags= str(16)
            
        if self.methodValue == 'UDP':
            self.probe = protocol.udp()
        
    
    def sport(self, sport):
        self.probe.protocol.sport =  sport
    
    def dport(self, dport):
        self.probe.protocol.dport =  dport
        
    def outType(self):
        if self.jsonfile : return '-j'
        else : return ''
        
    def run(self, outfile = None):
        self._buildProbe()
        
        self.cmdList = []
        self.cmdList = [  tracebox.command,
                          tracebox.probeArg, self.buildedProbe,
                          #tracebox.dportArg, self.dport,
                          tracebox.hops_minArg, self.hops_min,
                          tracebox.timeoutArg, self.timeout,
                          tracebox.hops_maxArg, self.hops_max,
                          #tracebox.filenameArg, self.outpcapfile,
                          self.outType(),
                          tracebox.verbose,
                          self.IPtarget, ]
        
        self.command = ' '.join([ tracebox.command,
                                  tracebox.probeArg, self.buildedProbe,
                                  #tracebox.dportArg, self.dport,
                                  tracebox.hops_minArg, self.hops_min,
                                  tracebox.timeoutArg, self.timeout,
                                  tracebox.hops_maxArg, self.hops_max,
                                  #tracebox.filenameArg, self.outpcapfile,
                                  self.outType(),
                                  tracebox.verbose,
                                  self.IPtarget, ])
        
        #print( self.command)
        
        process = Popen(self.cmdList, stdout=PIPE, stderr=PIPE)
        t= time.time()
        self.start = {"sec": int(math.modf(t)[1]), "usec": int(math.modf(t)[0]*1000000) }
        self.date = time.strftime("%D %H:%M:%S +0000", time.gmtime())
        process.wait()
        self.stdout, self.stderr = process.communicate()
        
        if self.stderr: raise runError(self.stderr)

        
        if outfile != None:
            with open(outfile, 'ab') as file:
                file.write(self.stdout)
                
        return self.stdout, self.stderr

class protocol():
    def __init__(self, protocol):
        self.protocol = protocol()
        self.ip = ip()
        
    @classmethod
    def udp(cls):
        return cls(udp)
    
    @classmethod
    def tcp(cls):
        return cls(tcp)


class udp:
    layerId = 'udp'
    def __init__(self):
        self.sport = defaults.tracebox.sport
        self.dport = defaults.tracebox.dport
    
    def getPckt(self):
        return ' '.join([ udp.layerId,
                         '{',
                          'src =', self.sport, ',',
                          'dst =', self.dport, ',',

                          '}',])
class tcp:
    layerId = 'tcp'
    def __init__(self):
        self.sport = defaults.tracebox.sport
        self.dport = defaults.tracebox.dport
        self.flags = str(16) # tcp-ack
        
    def getPckt(self):
        return ' '.join([ tcp.layerId,
                         '{',
                          'flags =', self.flags, ',',
                          'src =', self.sport, ',',
                          'dst =', self.dport, ',',
                          '}',])
class ip:
    layerId = 'ip'
    def __init__(self):
        self.dscp = str(0) #ToS
        self.ecn = str(0) #ToS
    
    def getPckt(self):
        return ' '.join([ ip.layerId ,
                         '{',
                          'dscp =', self.dscp, ',',
                          'ecn =', self.ecn, ',',
                          '}',])
        
        
        
        