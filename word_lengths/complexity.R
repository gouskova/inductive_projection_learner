comppath = '/home/maria/Dropbox/mg-gg_grant2015/local_nonlocal_trigram_complexity/'
options('scipen'=100, "digits"=4)



aymara = read.csv(paste(comppath, 'aymaracounts.txt', sep=""), sep="\t", header=T)
shona = read.csv(paste(comppath, 'shonacounts.txt', sep=""), sep="\t", header=T)
quechua = read.csv(paste(comppath, 'quechcounts.txt', sep=""), sep="\t", header=T)
mongolian = read.csv(paste(comppath, 'mongocounts.txt', sep=""), sep="\t", header=T)
russian = read.csv(paste(comppath, 'russcounts.txt', sep=""), sep="\t", header=T)
hungarian=read.csv(paste(comppath, 'hungariancounts.txt', sep=""), sep="\t", header=T)


aymara$language = 'Aymara'
shona$language = 'Shona'
quechua$language = 'Quechua'
mongolian$language = 'Mongolian'
russian$language = 'Russian'
hungarian$language='Hungarian'

allgs = rbind(aymara, shona)
allgs = rbind(allgs, quechua)
allgs = rbind(allgs, mongolian) 
allgs = rbind(allgs, russian)
allgs = rbind(allgs, hungarian)
allgs$language = factor(allgs$language)
allgs$word = as.character(allgs$word)

colnames(allgs)= c('word', 'local', 'nonlocal', 'length', 'language')

length(allgs[allgs$length>2,]$word)
length(allgs[allgs$length<3,]$word)

allgs=allgs[allgs$length>2,]
#allgs$loglocal=log(allgs$local, base=exp(1))
#allgs$lognonlocal=log(allgs$nonlocal, base=exp(1))
summary(allgs)
head(allgs)

summary(allgs[allgs$language=='Aymara',])
summary(allgs[allgs$language=='Quechua',])
summary(allgs[allgs$language=='Shona',])
summary(allgs[allgs$language=='Mongolian',])
summary(allgs[allgs$language=='Hungarian',])
summary(allgs[allgs$language=='Russian',])

#for plotting
allgs=subset(allgs, length<26)

allgs$language<-relevel(allgs$language, "Russian")
allgs$language<-relevel(allgs$language, "Mongolian")
allgs$language<-relevel(allgs$language, "Hungarian")
allgs$language<-relevel(allgs$language, "Shona")
allgs$language<-relevel(allgs$language, "Quechua")
allgs$language<-relevel(allgs$language, "Aymara")

allgs$language=factor(allgs$language)
levels(allgs$language)



sem<-function(x, ...) {sqrt(var(x, ...) / length(x)) }


library(ggplot2)
library(plyr)


plotdir = '/home/maria/Dropbox/mg-gg_grant2015/local_nonlocal_trigram_complexity'
save_plot<-function(fname, pwidth=10, pheight=5){
  fname=paste(plotdir,fname, sep="/")
  platform<-sessionInfo()$platform
  if(grepl("linux", platform)){
    cairo_pdf(filename=fname, width=pwidth, height=pheight, pointsize=16, family = 'Linux Biolinum', antialias=c('subpixel'))
  }
  else if(grepl('apple', platform)){
    quartz(type='pdf', file=fname, width=pwidth, height=pheight)
  }	
  p<-makeplot()
  print(p) 
  dev.off()
}

head(allgs)

library(reshape2)
longallgs=melt(allgs, id.vars=c('word','language', 'length'), variable.name='trigramMethod', value.name='NofTrigrams')
summary(longallgs)
head(longallgs)
longallgs[longallgs$word=="z a X a",]
sumlongallgs = ddply(longallgs, .(language, length, trigramMethod), summarize, mean=round(mean(NofTrigrams), 2), sd=round(sd(NofTrigrams), 2))
head(sumlongallgs)
summary(sumlongallgs)
colnames(sumlongallgs)=c('language', 'length', 'trigramMethod', 'trigrams', 'StDev')


makeplot<-function(){
  p<-ggplot(sumlongallgs, aes(x=length, y = trigrams, linetype=trigramMethod))+
    geom_ribbon(aes(ymin=trigrams-StDev, ymax=trigrams+StDev), alpha=0.2)+
    geom_line()+
    facet_grid(.~language, scales='free', space='free')+
    theme_bw()+
    ggtitle('Natural class trigrams by word length')+
    ylim(0,10000000000)+ 
    coord_cartesian(ylim=c(0,45000000))+
    ylab("N of natural class trigrams per word")+
    xlab("length of word, in phonemes")+
    theme(text=element_text(family="Linux Biolinum"), 
          panel.grid.major.x=element_blank(),
          panel.grid.minor.x=element_blank(),
          panel.grid.major.y=element_blank(),
          axis.title.x=element_blank())
  p
  }

save_plot('lineplot_n_local_nonlocal_trigrams.pdf')


