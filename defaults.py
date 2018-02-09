#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CoNexDat
    Grupo de investigación de redes complejas y comunicación de datos
    Facultad de Ingenieria 
    Universidad de Buenos Aires, Argentina

@author: Gabriel Davila Revelo
"""
import socket

class scamper:
    command= "/usr/local/bin/scamper" #default path to scamper command line
    pps = str(20) #default 20
    window = str(0) # default 0
    monitorname = socket.gethostname()
    outfile = 'outfile'
    filetype = 'json' #text, json, warts
    
class trace:
    method = 'TCP-ACK'
    dport = str(44444)
    sport = str(33333)
    firsthop = str(1)
    wait = str(1) #seconds
    maxttl = str(20)
    gaplimit = str(1)
    attempts = str(1)
    tos = str(0)
    
    
class ping:
    method = 'TCP-ACK'
    dport = str(44444)
    sport = str(33333)
    wait = str(1) #seconds
    ttl = str(20)
    probecount = str(1)
    tos = str(0)

class tracebox:
    command= "/usr/local/bin/tracebox" 
    method = 'TCP-ACK'
    dport = str(44444)
    sport = str(33333)
    hops_min = str(1)
    timeout = str(0.5) #seconds
    hops_max = str(20)
    tos = str(0)
    outfile = 'outfile'
    jsonfile = True

class exploration:
    method = 'TCP-ACK'
    dport = str(44444)
    sport = str(33333)
    