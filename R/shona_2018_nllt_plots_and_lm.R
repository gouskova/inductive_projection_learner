basedir = '/home/maria/git/phonotactics'

lgname='shona'

datadir = paste(basedir, 'data', lgname, sep='/')
simdir = paste(basedir, 'sims', sep = '/')

plotdir = '~/Dropbox/mg-gg_grant2015/2017_paper/plots/'

dataversions=list('verbs')
dataversions = list('verbs', 'allexwds')


#the testing data files tell us which words are supposed to be legal and illegal
test_key = read.csv(paste(basedir, '/data/shona/verbs/TestingData.txt', sep=""), sep="\t", header=F)

head(test_key)

colnames(test_key) = c("item", "Vseq", "Cons")
test_key$Cons=gsub('attested', 'VCC+V', as.character(test_key$Cons))
test_key$Cons=factor(gsub('singleton', 'VCV', as.character(test_key$Cons)))


head(test_key)
summary(test_key)



#OE calculations for Shona Verbs corpus, with final -a excluded:
#   a	    e	    i	    o	    u
#a	1.884	0.062	1.251	0.0	0.884
#e	0.559	4.77	0.009	0.0	0.751
#i	0.638	0.019	2.539	0.03	0.622
#o	0.295	1.538	0.092	8.135	0.025
#u	0.551	0.006	0.817	0.0	2.185

#the bad ones have O/E at 0 or near 0, these are 'disharmonic':
OEzero = c('ae', 'ao', 'ei', 'eo', 'ie', 'io', 'oi', 'ou', 'ue', 'uo')
#the ones not in OEzero with O/E below 0.8, these are "harmonic-marginal":
OEbelo80 = c('ea', 'eu', 'ia', 'iu', 'oa', 'ua')
#we'll call the others 'good'.
test_key$status = ifelse(test_key$Vseq %in% OEzero, 'disharmonic', 'harmonic-good')
test_key$status = as.factor(ifelse(test_key$Vseq %in% OEbelo80, 'harmonic-marginal', test_key$status))

summary(test_key)

simfolders = list.dirs(simdir)[grepl(lgname, list.dirs(simdir)) & grepl('output_baseline|output_final|output_custom', list.dirs(simdir))]

simfolders


simnames=lapply(simfolders, function(x) gsub(simdir, '', x))
simnames

simtableaux = lapply(simfolders, function(x) read.csv(paste(x, 'tableau.txt', sep='/'), sep="\t", header=T))


#this collects the results for each of the sims in 'dataversions' and puts them into a list, to be combined into a dataframe later
#since the simulation test files do not identify inside them which simulation the data came from, they need to get a column from the folder they came from
for (i in 1:length(simnames)){
  simnames[[i]]=gsub('/', '', simnames[[i]])
  simnames[[i]]=gsub('_Projection', "", simnames[[i]])
  simtableaux[[i]] = simtableaux[[i]][,1:3]
  colnames(simtableaux[[i]])=c('item', 'harmony', 'logprob')
  simtableaux[[i]]$simname = simnames[[i]]
  }

#paste them together using rbind
sims = do.call(rbind, simtableaux)

head(sims)
length(sims$item)
sims = merge(sims, test_key)
sims$simname=factor(sims$simname)
sims$status=relevel(sims$status, "harmonic-marginal")
sims$status=relevel(sims$status, "harmonic-good")

sims$binstat = relevel(factor(ifelse(sims$status!='disharmonic', 'harmonic', 'disharmonic')), 'harmonic')

summary(sims)

#PLOTS  #PLOTS  #PLOTS  #PLOTS  #PLOTS  #PLOTS  #PLOTS  #PLOTS

library(ggplot2)

setwd(plotdir)


#defining the plot viewing device so that it works on linux and mac os

#violin plot function
#this feeds into two wrapper functions: one saves a PDF of the plot, and other displays it to the screen

makeplot= function(dframe, var_to_plot, ptitle, facet=T) {
      p = ggplot(dframe, aes_string(x=var_to_plot, y='harmony'))+
		  geom_violin(trim=TRUE, scale="width")+
	   	ggtitle(ptitle)+
	   	ylab('Harmony scores')+
	  	theme_bw()+
	  	stat_summary(fun.y=mean, geom='point', shape=18, size=3, color='red')+
	  	theme(text=element_text(family="Linux Biolinum"), 
	        panel.grid.major.x=element_blank(),
	        panel.grid.minor.x=element_blank(),
	        panel.grid.major.y=element_blank(),
	        axis.title.x=element_blank()
	        )
		if (facet==T){
			p = p+ facet_grid(.~Cons, scales='free', space='free')
			}
		p
	}

#saving the plot to pdf
save_plot<-function(dframe, var_to_plot, fname, ptitle, facet=T, pwidth=7, pheight=5){
  fname=paste(plotdir,fname, sep="/")
  platform<-sessionInfo()$platform
  if(grepl("linux", platform)){
    cairo_pdf(filename=fname, width=pwidth, height=pheight, pointsize=16, family = 'Linux Biolinum', antialias=c('subpixel'))
  }
  else if(grepl('apple', platform)){
    quartz(type='pdf', file=fname, width=pwidth, height=pheight)
  }	
  p<-makeplot(dframe, var_to_plot, ptitle, facet)
  print(p) 
  dev.off()
  }

view_plot<-function(dframe, var_to_plot, ptitle, facet=T, pwidth=7, pheight=5){
  platform<-sessionInfo()$platform
  if(grepl("linux", platform)){
    X11(width=pwidth, height=pheight, pointsize=16, family = 'Linux Biolinum', antialias=c('subpixel'), type='cairo')
  }
  else if(grepl('apple', platform)){
    quartz(width=pwidth, height=pheight)
  }	
  p<-makeplot(dframe, var_to_plot, ptitle, facet)
  p 
  }

head(sims)
summary(sims)
levels(sims$simname)


sym = '2018-01-16_shona_verbs_wbsmall_vi_gain170_con60output_'
sym = '2018-01-17_shona_allexwds_customoutput_custom_+syll'

temp= subset(sims, simname==sym)
summary(temp)
tit = "Shona words, custom +syllabic simulation"
view_plot(temp, var_to_plot='binstat', ptitle = tit, facet=T)
save_plot(temp, var_to_plot="binstat", fname=paste(sym, 'by_ctype.pdf', sep=""), ptitle=tit, facet=T)


temp= subset(sims, simname==paste(sym, 'final', sep=""))
summary(temp)
tit = "Shona verbs, with projection induction"
view_plot(temp, var_to_plot='binstat', ptitle = tit, facet=T)
save_plot(temp, var_to_plot="binstat", fname=paste(sym, '_final_', 'by_ctype.pdf', sep=""), ptitle=tit, facet=T)


temp= subset(sims, simname==paste(sym, 'baseline', sep=""))
summary(temp)
tit = "Shona verbs, baseline"
view_plot(temp, var_to_plot='binstat', ptitle = tit, facet=T)
save_plot(temp, var_to_plot="binstat", fname=paste(sym,'_baseline_', 'by_ctype.pdf', sep=""), ptitle=tit, facet=T)


sym = '2018-01-16_shona_verbs_customoutput_custom_+syll'

temp= subset(sims, simname==sym)
summary(temp)
tit = "Shona verbs, custom +syllabic simulation"
view_plot(temp, var_to_plot='binstat', ptitle = tit, facet=T)
save_plot(temp, var_to_plot="binstat", fname=paste(sym,'_custom_', 'by_ctype.pdf', sep=""), ptitle=tit, facet=T)


####################################################################
# STATS
####################################################################

options("scipen"=100, "digits"=4)
library(lme4)


sims$Cons = relevel(sims$Cons, "VCV")
levels(sims$simname)

# a linear model comparing the baseline simulation and the final grammar produced by the learner.
#the subset to take has gain 170 and con sized 60

finalsims = c('2018-01-16_shona_verbs_wbsmall_vi_gain170_con60output_final', '2018-01-16_shona_verbs_wbsmall_vi_gain170_con60output_baseline')
R3final<-sims[sims$simname=='2018-01-16_shona_verbs_wbsmall_vi_gain170_con60output_final',]
R3final$simname=factor(R3final$simname)
levels(R3final$simname)
levels(R3final$binstat)
levels(R3final$Cons)
summary(R3final)

R3finmod = lm(harmony~binstat*Cons, data=R3final)
summary(R3finmod)


R3baseline<-sims[sims$simname=='2018-01-16_shona_verbs_wbsmall_vi_gain170_con60output_baseline',]
R3baseline$simname=factor(R3baseline$simname)
levels(R3baseline$simname)
levels(R3baseline$binstat)
levels(R3baseline$Cons)
summary(R3baseline)

R3basemod = lm(harmony~binstat*Cons, data=R3baseline)
summary(R3basemod)

R3custom = sims[sims$simname=='2018-01-16_shona_verbs_customoutput_custom_+syll',]
head(R3custom)
head(R3final)

#R3custom = rbind(R3custom, R3final)
R3custom$simname = factor(R3custom$simname)
summary(R3custom)

R3custmod = lm(harmony~binstat, data=R3custom)
R3finmod = lm(harmony~binstat, data=R3final)

summary(R3custmod)
summary(R3finmod)

AIC(R3custmod)
AIC(R3finmod)
AIC(R3basemod)
