"
CoNexDat
    Grupo de investigación de redes complejas y comunicación de datos
    Facultad de Ingenieria 
    Universidad de Buenos Aires, Argentina

@author: Gabriel Davila Revelo
"

#===============================
# function to compute rtt_density
#===============================
rtt_density<-function(rtt_list){
  # n: number of bins
  # bins: vector with rtt values representing bins limit
  # delta: diference between the values of each bin
  # h: standard histogram
  
  n=trunc(sqrt(length(rtt_list)))
  bins<-c(rtt_list[1])
  delta<-c()
  
  for (i in seq(n,length(rtt_list), by=n)){
    bins<-append(bins,rtt_list[i])
  }
  if (bins[length(bins)]!=rtt_list[length(rtt_list)]) {
    bins<-append(bins,rtt_list[length(rtt_list)])
  }
  
  for (i in seq(2,length(bins), by=1)){
    delta<-append(delta, bins[i]-bins[i-1] )
  }
  
  h <- hist(rtt_list, breaks = bins, plot=FALSE)
  h$counts=1/(sum(h$counts)*delta)
  rtt=data.frame(mids=h$mids, counts=h$counts)
  return(rtt)
}


require ("mongolite")

# mongoDB connector
rttExplorer <-  mongo( collection = 'path',
              db = 'conexdat',
              url = 'mongodb://conexdat:1405871@ds163656.mlab.com:63656/conexdat'
          )

# mongoDB queries

query <- rttExplorer$aggregate('[
                               { "$group" : { "_id" : {"src": "$src", "dst": "$dst"} } }
                               ]')
print(query$`_id`$dst)



query <- rttExplorer$aggregate('[
                                { "$match" : { "dst" : "8.8.8.8", "Hops.hop": 1} },
                                { "$project" : { "Hops.hop": 1,  "_id" : 0 } },
                                { "$group" : { "_id" : "$Hops.from" } }
                               ]')



query <- rttExplorer$aggregate('[
                               { "$match" : { "dst" : "8.8.8.8"} },
                               { "$project" : { "Hops.from": 1,  "Hops.hop": 1,  "_id" : 0 } }
                               ]')


query <- rttExplorer$find ( query = '{ "Hops.from": "192.168.0.1" , "Hops.hop": 4}',
                            fields = '{ "Hops.from" : true, "_id" : false}',
                            limit = 10
                            )

