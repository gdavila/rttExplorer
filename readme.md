# About

`rttExplorer` is a python-based tool to meassure round-trip-times (RTT) over Internet Paths. `rttExplorer` is based on Scamper and Tracebox. Tracebox is used to reveal paths through IPv4 targets; and Scamper is used to meassure the rtt to each hop revealed by tracebox.

`rttExplorer` also allows to make periodic meassurements over the Internet Path, i. e., given a IPv4 target, the path is discovered every *path Interval*, then the RTT is meassured to each revealed hop every *RTT Interval*. Both probes (path discovery and rtt measurements) are generated with identical flow id in order to assure uniqueness in the forward path. At the moment, it supports UDP and TCP-ACK probes. However, is prety easy to add new probes in the code.

# Requierements

* Python3 or greater
* Tracebox v0.4.4 or greater
* Scamper v20171204 or greater

# Installation

Just clone or download the latest version of rttExplorer


# Usage


```
$ sudo python3 rttExplorer.py -h

usage: rttExplorer [-h] (-i ipTarget | -I inputTargetFile) -t explorationTime
               [-D pathInterval] [-T rttInterval] [-m method] [-f firstTTL]
               [-M maxTTL] [-d dstPort] [-s srcPort] [-o outFile] [--mongodb]

script to measure the rrt along a path

optional arguments:
  -h, --help          show this help message and exit

required arguments::
  -i ipTarget         IPv4 target
  -I inputTargetFile  input file with a list of IPv4 targets line by line
  -t explorationTime  Duration time of the exploration (minutes)

optional arguments::
  -D pathInterval     time interval between path discovery probes (minutes).
                      Default is 5
  -T rttInterval      time interval between rtt measurement probes (seconds).
                      Default is 1
  -m method           UDP or TCP-ACK. Default is UDP
  -f firstTTL         ttl for the first hop used in traceroute. Default is 1
  -M maxTTL           max ttl used in traceroute. Default is 20
  -d dstPort          destination Port. Default is 44444
  -s srcPort          source Port. Default is 33333
  -o outFile          File name to save the results (exploration name)
  --mongodb           upload the results in a mongoDB. See defaults.py to
                      change the default mongodb uri
 ```

# Examples

The next example send a discovery path probe to 8.8.8.8 every 2 minutes (-D) for 10 minutes (-t). To each revealed hop the RTT is meassured every 1 second (default value). The probes used are TCP-ACK and the first ttl is 6. Finally, the results are stored in a mongodb.  If mongodb is not enable the results are saved in json format in *results/* folder. 

 `sudo python3 rttExplorer.py -i 8.8.8.8 -t 10 -D 2 -m TCP-ACK -f 6 -—mongodb`
 
The second example is simila to the previous one but the targets are readed from the file *targets.txt* 

 `sudo python3 rttExplorer.py -I targets.txt -t 10 -D 2 -m TCP-ACK -f 6 -—mongodb `