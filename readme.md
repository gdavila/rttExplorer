# About

`rttExplorer` is a python-based tool to meassure round-trip-times (RTT) over Internet Paths. `rttExplorer` is based on [Scamper](https://www.caida.org/tools/measurement/scamper/) and [Tracebox](http://www.tracebox.org/). Tracebox is used to reveal paths through IPv4 targets; and Scamper is used to meassure the rtt to each hop revealed by tracebox.

`rttExplorer` also allows to make periodic meassurements over the Internet Path, i. e., given a IPv4 target, the path is discovered every *path Interval*, then the RTT is meassured to each revealed hop every *RTT Interval*. Both probes (path discovery and rtt measurements) are generated with identical flow id in order to assure uniqueness in the forward path. At the moment, it supports UDP and TCP-ACK probes. However, is prety easy to add new probes in the code.

# Requierements

* Python3 or greater.
* Pymongo library.

	```
	sudo pip3 install pymongo
	```
	
* [Scamper cvs-20180504](https://www.caida.org/tools/measurement/scamper/code/scamper-cvs-20180504.tar.gz) or greater. Download from the source and build it.

	```
	wget https://www.caida.org/tools/measurement/scamper/code/scamper-cvs-20180504.tar.gz
	tar -xzf scamper-cvs-20180504.tar.gz
	cd scamper-cvs-20180504/
	sudo ./configure
	sudo make
	sudo make install 
	```


* [Tracebox v0.4.4](https://github.com/tracebox/tracebox) or greater. Download from the source and build it.

	```
	sudo apt-get install autotools-dev autoconf automake libtool lua5.2 liblua5.2-dev lua5.2-doc libpcap-dev libjson-c-dev libcurl4-gnutls-dev libnetfilter-queue-dev 
	git clone https://github.com/tracebox/tracebox.git
	cd tracebox
	sudo ./bootstrap.sh
	sudo ./configure
	sudo make
	sudo make install
	```


# Installation


Just clone or download the latest version of rttExplorer



`git clone https://github.com/gdavila/rttExplorer.git`

Go to the folder rttExplorer and use it!

```
cd rttExplorer/
sudo python3 rttExplorer.py -h

```

**Important**: rttExplorer require *sudo* privileges 



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



# Mongodb upload


*mongo.py* file includes the settings required to set the mongo database where the results can be stored. Otherwise, results are saved locally  in json format in *results/* folder.  By default a [mlab](https://mlab.com) free-sandbox is used as mongo database.

The mongodb is based on two collections:

* **path Collection**: includes each hop revealed through tracebox. Each document has the following format:

```
{
    "_id": {
        "$oid": "5a794ce874fece0dc2c5fc91"
    },
    "method": "tcp-ack",
    "dst": "181.30.134.83",
    "dport": "44444",
    "type": "tracebox",
    "Hops": [
        {
            "delay": 14102,
            "hop": 6,
            "from": "200.89.161.118",
            "Modifications": [
                {
                    "IP::ExpCongestionNot": {
                        "Expected": "0",
                        "Received": "3"
                    }
                },
                {
                    "IP::TTL": {
                        "Expected": "6",
                        "Received": "1"
                    }
                },
                {
                    "IP::CheckSum": {
                        "Expected": "0x825a",
                        "Received": "0x8757"
                    }
                }
            ],
            "Additions": [
                {
                    "PartialTCP": {
                        "Info": "< PartialTCP (8 bytes) :: SrcPort = 33335 , DstPort = 44444 , SeqNumber = 1351198137 , >\n"
                    }
                }
            ],
            "name": "118-161-89-200.fibertel.com.ar",
            "Deletions": []
        },
        {
            "delay": 37541,
            "hop": 7,
            "from": "181.30.134.83",
            "Modifications": [
                {
                    "TCP::SrcPort": {
                        "Expected": "33335",
                        "Received": "44444"
                    }
                },
                {
                    "TCP::DstPort": {
                        "Expected": "44444",
                        "Received": "33335"
                    }
                },
                {
                    "TCP::SeqNumber": {
                        "Expected": "1351198137",
                        "Received": "0"
                    }
                },
                {
                    "TCP::Flags": {
                        "Expected": "( ACK )",
                        "Received": "( RST )"
                    }
                },
                {
                    "TCP::WindowsSize": {
                        "Expected": "5840",
                        "Received": "0"
                    }
                },
                {
                    "TCP::CheckSum": {
                        "Expected": "0x7655",
                        "Received": "0x8374"
                    }
                },
                {
                    "IP::ExpCongestionNot": {
                        "Expected": "0",
                        "Received": "3"
                    }
                },
                {
                    "IP::Identification": {
                        "Expected": "0xf5dd",
                        "Received": "0x0"
                    }
                },
                {
                    "IP::TTL": {
                        "Expected": "7",
                        "Received": "58"
                    }
                },
                {
                    "IP::CheckSum": {
                        "Expected": "0x815a",
                        "Received": "0x4435"
                    }
                },
                {
                    "IP::SourceIP": {
                        "Expected": "192.168.0.126",
                        "Received": "181.30.134.83"
                    }
                },
                {
                    "IP::DestinationIP": {
                        "Expected": "181.30.134.83",
                        "Received": "192.168.0.126"
                    }
                }
            ],
            "Additions": [],
            "name": "83-134-30-181.fibertel.com.ar",
            "Deletions": []
        }
    ],
    "sport": "33335",
    "explorationName": "raspberrypi",
    "date": "02/06/18 02:18:16 +0000",
    "start": {
        "sec": 1517883496,
        "usec": 96460
    },
    "src": "192.168.0.126"
}
```

* **rtt Collection**: includes the rtt meassurements to every hop in the revealed path. Each document has the following format:
 
```
{
    "_id": {
        "$oid": "5a7948c074fece0dc2c18f4b"
    },
    "stop_data": 0,
    "attempts": 1,
    "userid": 0,
    "version": "0.1",
    "probe_size": 40,
    "wait_probe": 0,
    "stop_reason": "HOPLIMIT",
    "start": {
        "sec": 1517883496,
        "ftime": "2018-02-06 02:18:16",
        "usec": 696807
    },
    "wait": 1,
    "method": "tcp-ack",
    "firsthop": 6,
    "dst": "181.30.134.83",
    "hop_count": 6,
    "explorationName": "raspberrypi",
    "hops": [
        {
            "probe_ttl": 6,
            "icmp_code": 0,
            "reply_size": 56,
            "icmp_q_tos": 3,
            "probe_id": 1,
            "icmp_q_ttl": 1,
            "probe_size": 40,
            "reply_ipid": 0,
            "reply_tos": 195,
            "reply_ttl": 250,
            "addr": "200.89.161.118",
            "icmp_q_ipl": 40,
            "tx": {
                "sec": 1517883496,
                "usec": 747040
            },
            "rtt": 41.129,
            "icmp_type": 11
        }
    ],
    "type": "trace",
    "tos": 0,
    "hoplimit": 6,
    "sport": 33335,
    "src": "192.168.0.126",
    "dport": 44444
}

```


# Examples

1. The next example send a discovery path probe to 8.8.8.8 every 2 minutes *[-D pathInterval]* for 10 minutes *[-t explorationTime]*. 

	To each revealed hop, the RTT is meassured every 1 second *[-T rttInterval]* . The probes used are TCP-ACK *[-m method]* and the first probe's ttl is 6 *[-f firstTTL]*. Finally, the results are stored in the mongo database *[--mongodb]*.


 `sudo python3 rttExplorer.py -i 8.8.8.8 -t 10 -D 2 -m TCP-ACK -f 6 -—mongodb`
 
2. The second example is similar to the previous one but the targets are read from the targets.txt file  *[-I inputTargetFile]*.

 `sudo python3 rttExplorer.py -I targets.txt -t 10 -D 2 -m TCP-ACK -f 6 -—mongodb `
 
3. To see some output results try to connect to the sandbox mongodb.

	To connect using the mongo shell:
		
	`% mongo ds163656.mlab.com:63656/conexdat -u <dbuser> -p <dbpassword>`
	
	To connect using a driver via the standard MongoDB URI:
	
	`mongodb://<dbuser>:<dbpassword>@ds163656.mlab.com:63656/conexdat`
	
		read-only credentials:
	
		<dbuser>: conexdat_uba
	
		<dbpassword>: 12345678
