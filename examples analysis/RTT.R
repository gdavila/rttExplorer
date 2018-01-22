"
CoNexDat
Grupo de investigación de redes complejas y comunicación de datos
Facultad de Ingenieria 
Universidad de Buenos Aires, Argentina

@author: Gabriel Davila Revelo
"

require ("mongolite")

#---- Functions ----
rtt_density <- function(rtt_list){
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

get_mplsInfo <- function(ICMPEsxtensionsInfo){
  mpls_path <- ICMPEsxtensionsInfo
  mpls_info <- c()
  for (i in 1: length(mpls_path)){
    if (is.null(mpls_path[[i]][[1]]$Info[3])) {
      mpls_info <- append (mpls_info,"< NoICMPExtensionMPLS >" )
    } else {
      mpls_info <- append (mpls_info, mpls_path[[i]][[1]]$Info[3])
    }
  }
  return(list(mpls_info))
}

# ---- mongoDB connector: PATH  ----
pathCollection <-  mongo( collection = 'path',
                       db = 'conexdat',
                       url = 'mongodb://conexdat:1405871@ds163656.mlab.com:63656/conexdat'
)

# ---- mongoDB connector: RTT  ----
rttCollection <-  mongo( collection = 'rtt',
                       db = 'conexdat',
                       url = 'mongodb://conexdat:1405871@ds163656.mlab.com:63656/conexdat'
)

# mongoDB queries

# ---- mongoDB query: IPsrc and IPdst List ----
query <- pathCollection$aggregate('[
                               { "$group" : { "_id" : {"src": "$src", "dst": "$dst"} } }
                               ]')

ip_src_dst <- query 
rm(query)

# ---- mongoDB query: paths given a ip_src ip_dst ----
query <- pathCollection$find ( query = '{ "dst": "81.200.198.6"}',
                            fields = '{ "Hops.ICMPExtensions.ICMPExtensionMPLS.Info" : true, "Hops.from" : true, "Hops.hop" : true, "start.sec": true, "_id" : false}'
                              )
paths <- query
rm(query)
# ---- R algorithim: different paths analysis ----
start <- c()
finish <- c()
changing_paths <- c()
mpls_info <- c()

for (i in 1: nrow(paths$start)){
  if (i==1){
    print (c(i, paths$start[['sec']][i]))
    start <- append(start,paths$start[['sec']][i])
    changing_paths <- append(changing_paths,list(paths$Hops[[i]]['from']$from))
    mpls_info <- append(mpls_info, get_mplsInfo(paths$Hops[[i]][['ICMPExtensions']]))
  } else if (!all(paths$Hops[[i]][['from']][2:17] == paths$Hops[[i-1]][['from']][2:17]) &&
      !all(get_mplsInfo(paths$Hops[[i]][['ICMPExtensions']][2:17])[[1]] == get_mplsInfo(paths$Hops[[i-1]][['ICMPExtensions']][2:17])[[1]])
      ){
    print (c(i, paths$start[['sec']][i]))
        finish <- append(finish,paths$start[['sec']][i])
        start <- append(start,paths$start[['sec']][i])
        changing_paths <- append(changing_paths,list(paths$Hops[[i]]['from']$from))
        mpls_info <- append(mpls_info, get_mplsInfo(paths$Hops[[i]][['ICMPExtensions']]))
  }
  if (i == nrow(paths$start)){
    finish <- append(finish,paths$start[['sec']][i])
  }
}

paths_stability_df <- data.frame(start)
paths_stability_df$finish <- finish
paths_stability_df$duration <- paths_stability_df$finish - paths_stability_df$start
paths_stability_df$paths <- changing_paths
paths_stability_df$mplsInfo <- mpls_info


rm(start)
rm(changing_paths)
rm(mpls_info)




# ---- Different Paths ----

#query <- rttExplorer$aggregate('[
#                               { "$match" : { "dst" : "81.200.198.6"} },
#                               { "$project" : { "Hops.from": 1,  "_id" : 0 } },
#                               { "$group" : { "_id" : "$Hops.from" } }
#                               ]')


# ---- RTT ----

query <- rttCollection$find ( query = '{ "dst": "81.200.198.6", "hops.probe_ttl": 6, "start.sec": {"$gt": 1515833719 , "$lt": 1515839767  }}',
                            fields = '{ "hops.rtt" : true, "hops.tx.sec":true,  "hops.addr" : 1, "_id" : false}',
                            sort = '{"hops.rtt" : 1}'
                          )


#ordernar query$hops
rtt <-  apply(query, 1,unlist)
rtt  <-  t(rtt)
rtt <- as.data.frame(rtt,stringsAsFactors = FALSE)
rtt$hops.tx.sec <- as.numeric(rtt$hops.tx.sec)
rtt$hops.rtt <- as.numeric(rtt$hops.rtt)

rttMeas <-sort(rtt$hops.rtt)
rttDensity <- rtt_density(rttMeas)

ggplot()+
  geom_line(data=rttDensity , aes(x=mids, y=counts), color="gray")+
  scale_y_log10()+
  scale_x_log10()
  #ggtitle(paste0('DESTINO: ',dest, '\n', 'HOP: ' ,address))

ggplot()+
  geom_point(data=rtt, aes(x=hops.tx.sec, y=hops.rtt), color="gray")
  #ggtitle(paste0('DESTINO: ',dest, '\n', 'HOP: ' ,address))
