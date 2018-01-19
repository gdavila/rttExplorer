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
  print("bins")
  if (bins[length(bins)]!=rtt_list[length(rtt_list)]) {
    bins<-append(bins,rtt_list[length(rtt_list)])
  }
  print(bins)
  for (i in seq(2,length(bins), by=1)){
    print (i)
    delta<-append(delta, bins[i]-bins[i-1] )
  }
  print (delta)
  h <- hist(rtt_list, breaks = bins, plot=FALSE)
  print(h)
  h$counts=1/(sum(h$counts)*delta)
  rtt=data.frame(mids=h$mids, counts=h$counts)
  return(rtt)
}


require ("mongolite")

# ---- mongoDB connector PATH----
rttExplorer <-  mongo( collection = 'path',
                       db = 'conexdat',
                       url = 'mongodb://conexdat:1405871@ds163656.mlab.com:63656/conexdat'
)

# mongoDB queries
# ---- IPsrc and IPdst List ----
query <- rttExplorer$aggregate('[
                               { "$group" : { "_id" : {"src": "$src", "dst": "$dst"} } }
                               ]')
print(query$`_id`$dst)


# ---- Hops, IP, MPLS labels ----
query <- rttExplorer$find ( query = '{ "dst": "81.200.198.6"}',
                            fields = '{ "Hops.ICMPExtensions.ICMPExtensionMPLS" : true, "Hops.from" : true, "Hops.hop" : true, "start.sec": true, "_id" : false}',
                            limit = 1000
)

Paths <- query

# ---- Hops, IP, MPLS labels ----
changePathTimes<- c()
changePath <- c()
for (i in 2: nrow(Paths$start)){
  if (!all(Paths$Hops[[i]][['from']][2:17] == Paths$Hops[[i-1]][['from']][2:17])){
    changePathTimes <- append(changePathTimes,Paths$start[['sec']][i])
    changePath <- append(changePath,Paths$Hops[[i]]['from'])
    print (Paths$Hops[[i]][['from']])
  }
}

# ---- Different Paths ----

query <- rttExplorer$aggregate('[
                               { "$match" : { "dst" : "81.200.198.6"} },
                               { "$project" : { "Hops.from": 1,  "_id" : 0 } },
                               { "$group" : { "_id" : "$Hops.from" } }
                               ]')

print(c('Paths: ', length(query$`_id`)))
View(as.data.frame(query$`_id`))


# ---- mongoDB connector RTT----
rttExplorer <-  mongo( collection = 'rtt',
                       db = 'conexdat',
                       url = 'mongodb://conexdat:1405871@ds163656.mlab.com:63656/conexdat'
)

# ---- RTT ----

query <- rttExplorer$find ( query = '{ "dst": "81.200.198.6", "hops.addr": "200.89.160.25", "start.sec": {"$gt": 1515829787 , "$lt": 1515831599  }}',
                            fields = '{ "hops.rtt" : true, "hops.tx.sec":true, "_id" : false}',
                            sort = '{"hops.rtt" : 1}'
                          )


#ordernar query$hops
rtt <-  apply(query, 1,unlist)
rtt  <-  t(rtt)
rtt <- as.data.frame(rtt)

rttMeas <-sort(as.numeric(rtt$hops.rtt))
rttDensity <- rtt_density(rttMeas)

ggplot()+
  geom_line(data=rttDensity , aes(x=mids, y=counts), color="gray")+
  scale_y_log10()+
  scale_x_log10()
  #ggtitle(paste0('DESTINO: ',dest, '\n', 'HOP: ' ,address))

ggplot()+
  geom_point(data=rtt, aes(x=hops.tx.sec, y=hops.rtt), color="gray")
  #ggtitle(paste0('DESTINO: ',dest, '\n', 'HOP: ' ,address))
