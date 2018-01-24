"
CoNexDat
Grupo de investigación de redes complejas y comunicación de datos
Facultad de Ingenieria 
Universidad de Buenos Aires, Argentina

@author: Gabriel Davila Revelo
"

library ("mongolite")
library ("cowplot")
library("scales")

ip_src <- '"192.168.0.126"'
ip_dst <- '"149.43.80.22"'
probe_ttl <- 14

#---- Functions ----

base_breaks <- function(n = 10){
  function(x) {
    axisTicks(log10(range(x, na.rm = TRUE)), log = TRUE, n = n)
  }
}

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

get_mplsInfo <- function(ICMPExtensionsInfo){
  mpls_path <- ICMPExtensionsInfo
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

get_pathStability <- function(paths){
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
  return(paths_stability_df)
}

plot_rtt <- function(rtt){
  rtt <-  t(apply(rtt, 1, unlist))
  rtt <-  as.data.frame(rtt,stringsAsFactors = FALSE)
  rtt$hops.tx.sec <- as.numeric(rtt$hops.tx.sec)
  rtt$hops.rtt <- as.numeric(rtt$hops.rtt)
  rtt$hops.reply_ttl <- as.numeric(rtt$hops.reply_ttl)
  rtt$hops.icmpext.mpls_labels.mpls_label <- as.numeric(rtt$hops.icmpext.mpls_labels.mpls_label )
  
  p1 <- ggplot(data=rtt_density(sort(rtt$hops.rtt)) , aes(x=mids, y=counts))+
        geom_line(color="gray")+
        scale_y_continuous(name = 'density', trans = log_trans(), breaks = base_breaks()) + 
        scale_x_continuous(name = 'rtt (s)', trans = log_trans(), breaks = base_breaks()) +
        theme_gray()+
        theme(axis.text.x = element_text(angle = 90))
    
  
  p2 <- ggplot(data=rtt, aes(x=hops.tx.sec - min(hops.tx.sec), y=hops.rtt))+
        geom_point(color="gray") +
        theme_gray()+
        labs( x = "time (s)", y = "rtt (s)") 
    
  
  p3 <- ggplot(data=rtt, aes(x=hops.tx.sec - min(hops.tx.sec) , y=hops.reply_ttl))+
        geom_point(color="gray") +
        theme_gray()+
        labs(x = "time (s)", y = "reply ttl") 
  
  p4 <- ggplot(data=rtt, aes(x=hops.tx.sec - min(hops.tx.sec) , y=hops.icmpext.mpls_labels.mpls_label))+
        geom_point(color="gray") +
        theme_gray()+
        labs(x = "time (s)", y = "reply ipid") 
    
    #labs(title = paste0('Addr: ' , unique(rtt$hops.addr), ' Hop: ' , probe_ttl),
    #     subtitle = paste0(ip_src , ' --> ',ip_dst ) , 
    #     x = "time (s)", y = "reply ttl")    
  
  return(plot_grid(p1, p2, p3, p4, ncol = 2))
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


# ---- mongoDB query: IPsrc and IPdst List ----
query <- pathCollection$aggregate('[
                               { "$group" : { "_id" : {"src": "$src", "dst": "$dst"} } }
                               ]')

ip_src_dst <- query 


# ---- mongoDB query: paths given a ip_src ip_dst ----
q <- paste('{ "src" : ', ip_src,', "dst" : ', ip_dst, '}')
f <- '{ "Hops.ICMPExtensions.ICMPExtensionMPLS.Info" : true, "Hops.from" : true, "Hops.hop" : true, "start.sec": true, "_id" : false}'
query <- pathCollection$find ( query = q, fields = f )
paths <- query

# ---- R algorithim: different paths analysis ----
pathStability <- get_pathStability(paths )

# ---- RTT ----
start <- pathStability[pathStability$duration == max(pathStability$duration), 'start'][1] 
finish <- pathStability[pathStability$duration == max(pathStability$duration), 'finish'][1] 
q <- paste('{ "src" : ', ip_src, 
           ', "dst" : ', ip_dst,  
           ', "hops.probe_ttl" : ',  probe_ttl, 
           ', "start.sec": {"$gt": ', start,
           ', "$lt" : ', finish, '}',
           '}')
f <- '{ "hops.rtt" : true, "hops.tx.sec":true,  "hops.addr" : 1, "hops.reply_ttl" : 1, "hops.icmpext.mpls_labels.mpls_label" : 1,  "_id" : false}'
s <- '{"hops.rtt" : 1}'

query <- rttCollection$find ( query = q, fields = f, sort = s )
rtt <- query
plot_rtt(rtt)


# ---- Different Paths ----

#query <- rttExplorer$aggregate('[
#                               { "$match" : { "dst" : "81.200.198.6"} },
#                               { "$project" : { "Hops.from": 1,  "_id" : 0 } },
#                               { "$group" : { "_id" : "$Hops.from" } }
#                               ]')

