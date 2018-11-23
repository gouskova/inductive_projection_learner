basedir = '/home/maria/git/phonotactics'

options(scipen=999)
lgname='aymara'

datadir = paste(basedir, 'data', lgname, sep='/')
simdir = paste(basedir, 'sims', sep = '/')

plotdir = '~/Dropbox/mg-gg_grant2015/aymara/plots/'

dataversions=list('words','roots', 'words_unparsed')

human_key = read.csv(paste(datadir, dataversions[1], 'TestingData_people.txt', sep="/"), sep="\t", header=F)
human_accuracy=read.csv(paste(datadir, 'human_accuracy.txt', sep="/"), sep="\t", header=T)


head(human_key)
head(human_accuracy)


human_accuracy$X<-NULL
human_accuracy$type<-NULL

colnames(human_key) = c("item", "status")
colnames(human_accuracy)=c('experiment', 'word_ipa', 'human_accuracy', 'plotname')
human_accuracy$labels = human_accuracy$plotname
human_accuracy$labels = gsub("EE", 'ejective-ejective', human_accuracy$labels)
human_accuracy$labels = gsub("CT", 'control', human_accuracy$labels)
human_accuracy$labels = gsub("ED", 'ejective-dental', human_accuracy$labels)
human_accuracy$labels = gsub("FL", 'filler', human_accuracy$labels)
human_accuracy$labels = gsub("PD", 'plain-dental', human_accuracy$labels)
human_accuracy$labels = gsub("PE", 'plain-ejective', human_accuracy$labels)
human_accuracy$labels = gsub("EL", 'ejective-labial', human_accuracy$labels)
human_accuracy$labels = as.factor(gsub("PL", 'plain-labial', human_accuracy$labels))

levels(human_accuracy$labels)
human_key=cbind(human_key, human_accuracy)

human_key$word_ipa=gsub('\x96', "ɲ", human_key$word_ipa)
human_key$word_ipa=gsub('ll', 'ʎ', human_key$word_ipa)
human_key$word_ipa=gsub("ch'", "ʧ'", human_key$word_ipa)
human_key$word_ipa=gsub('c', 'ʧ', human_key$word_ipa)
human_key$word_ipa=gsub("h", "ʰ", human_key$word_ipa)
human_key$word_ipa=gsub("y", "j", human_key$word_ipa)
human_key$word_ipa<-factor(human_key$word_ipa)
human_key$item
human_key$item_mbless = gsub('¦ ', '', human_key$item)

head(human_key)
summary(human_key)


simfolders = list.dirs(simdir)[grepl(lgname, list.dirs(simdir)) & grepl('output_|test_', list.dirs(simdir))]

simfolders

simnames=lapply(simfolders, function(x) gsub(simdir, '', x))
simnames

simtableaux = lapply(simfolders, function(x) read.csv(paste(x, 'tableau.txt', sep='/'), sep="\t", header=T))


#this collects the results for each of the sims in 'dataversions' and puts them into a list, to be combined into a dataframe later
#since the simulation test files do not identify inside them which simulation the data came from, they need to get a column from the folder they came from
for (i in 1:length(simnames)){
  simnames[[i]]=gsub('/', '', simnames[[i]])
  simtableaux[[i]] = simtableaux[[i]][,1:3]
  colnames(simtableaux[[i]])=c('item', 'harmony', 'logprob')
  simtableaux[[i]]$simname = simnames[[i]]
  }

#paste them together using rbind
sims = do.call(rbind, simtableaux)
sims = subset(sims, grepl('wbsmall', simname)==F)
sims$item_mbless = gsub('¦ ', '', sims$item)
sims$expharm = exp(-1*sims$harmony)
summary(sims)

head(sims)
length(sims$item)
people = merge(sims, human_key, by='item_mbless')
people$simname=factor(people$simname)

#PLOTS  #PLOTS  #PLOTS  #PLOTS  #PLOTS  #PLOTS  #PLOTS  #PLOTS

library(ggplot2)


#for plotting human experiments

makeplot= function(dframe, var_to_plot, ptitle, facet=F, textlabels=T) {
  if (facet){
    p = ggplot(dframe, aes_string(x=var_to_plot, y='human_accuracy'))+
#    p = ggplot(dframe, aes_string(x=var_to_plot, y='harmony'))+
        facet_grid(.~experiment, scales='free', space='free')
  }
  else{p = ggplot(dframe, aes_string(x=var_to_plot, y='human_accuracy'))}
  p = p +geom_text(aes(label=plotname), size=3.5, position='jitter')+
    stat_smooth(method=lm)+
    coord_cartesian(xlim=c(-40,0), ylim=c(0,100))+
    ggtitle(ptitle)+
    labs(label='Type of word')+
    xlab('Harmony scores, computational model')+
    ylab("Percent accuracy in repetition, humans")+
    theme_bw()+
    theme(text=element_text(family="Linux Biolinum"), 
          panel.grid.major.x=element_blank(),
          panel.grid.minor.x=element_blank(),
          panel.grid.major.y=element_blank()
    )
  p
}

save_plot<-function(dframe, var_to_plot, fname, ptitle, facet, textlabels, pwidth=6, pheight=6){
  fname=paste(plotdir,fname, sep="/")
  platform<-sessionInfo()$platform
  if(grepl("linux", platform)){
    cairo_pdf(filename=fname, width=pwidth, height=pheight, pointsize=16, family = 'Linux Biolinum', antialias=c('subpixel'))
  }
  else if(grepl('apple', platform)){
    quartz(type='pdf', file=fname, width=pwidth, height=pheight)
  }	
  p<-makeplot(dframe, var_to_plot, ptitle, facet, textlabels)
  print(p) 
  dev.off()
}

view_plot<-function(dframe, var_to_plot, ptitle, facet, textlabels, pwidth=7, pheight=5){
  platform<-sessionInfo()$platform
  if(grepl("linux", platform)){
    X11(width=pwidth, height=pheight, pointsize=16, family = 'Linux Biolinum', antialias=c('subpixel'), type='cairo')
  }
  else if(grepl('apple', platform)){
    quartz(width=pwidth, height=pheight)
  }	
  p<-makeplot(dframe, var_to_plot, ptitle, facet, textlabels)
  p 
}


head(people)
summary(people)
levels(people$simname)

plotdir = '~/Dropbox/mg-gg_grant2015/aymara/plots/people_words'
setwd(plotdir)

sym = '2018-09-25_aymara_words_unparsed_customoutput_final'
temp= subset(people, simname==sym & plotname!='FL')
summary(temp)
summary(temp$plotname)
tit = "Modeling Aymara:\n grammar with custom projections, unparsed corpus"
view_plot(temp, var_to_plot='harmony', ptitle = tit, facet=T, textlabels=T)#, pwidth=10)
save_plot(temp, var_to_plot="harmony", fname=paste(sym, '.pdf', sep="_"), ptitle=tit, facet=T, textlabels=T)#,pwidth=10)


sym = '2018-09-23_aymara_words_wb_vi_gain400_con120output_final'
temp= subset(people, simname==sym & experiment=='exp1')
summary(temp)
summary(temp$plotname)
tit = "Modeling Aymara experiment 1:\n final grammar with projections induced from -mb constraints"
view_plot(temp, var_to_plot='harmony', ptitle = tit, facet=T, textlabels=T)#, pwidth=6)
save_plot(temp, var_to_plot="harmony", fname=paste(sym, 'exp1.pdf', sep="_"), ptitle=tit, facet=T, textlabels=T)#,pwidth=6)

temp= subset(people, simname==sym & experiment=='exp2' & plotname!='FL')
summary(temp)
summary(temp$plotname)
tit = "Modeling Aymara experiment 2:\n final grammar with projections induced from -mb constraints"
view_plot(temp, var_to_plot='harmony', ptitle = tit, facet=T, textlabels=T)#, pwidth=6)
save_plot(temp, var_to_plot="harmony", fname=paste(sym, 'no fillers', 'exp2.pdf', sep="_"), ptitle=tit, facet=T, textlabels=T)#,pwidth=6)

sym = '2018-09-10_aymara_words_unparsed_wb_vi_gain500_con500output_final'
temp= subset(people, simname==sym & plotname!='FL')
summary(temp)
summary(temp$plotname)
tit = "Modeling Aymara experiments:\n grammar with projections induced after training on unparsed corpus"
view_plot(temp, var_to_plot='harmony', ptitle = tit, facet=T, textlabels=T, pwidth=7)
save_plot(temp, var_to_plot="harmony", fname=paste(sym, '.pdf', sep="_"), ptitle=tit, facet=T, textlabels=T,pwidth=7)


####################################################################

# STATS STATS STATS

####################################################################
levels(people$simname)
levels(people$status)
unique(people$item.y)
people$morphcomplex = grepl('¦ d a', people$item.y)
people$place = ifelse(grepl(' d ', people$item.y), 'dental', 'control')
people$place = factor(ifelse(grepl(' b ', people$item.y), 'labial', people$place))
people$violtype = ifelse(grepl('cooc', people$status), 'coocc', 'control')
people$violtype = factor(ifelse(grepl('order', people$status), 'order', people$violtype))

summary(people)
head(people)
unique(people[people$place=='labial',]$item.y)

temp = subset(people, simname=='2018-09-25_aymara_words_unparsed_customoutput_final' & plotname!='FL')
summary(temp)
cor(temp$human_accuracy, temp$harmony, method='pearson')
cor(temp$human_accuracy, temp$harmony, method='kendall')
cor(temp$human_accuracy, temp$harmony, method='spearman')

temp = subset(people, simname=='2018-09-23_aymara_words_wb_vi_gain400_con120output_final' & plotname!='FL')
summary(temp)
cor(temp$human_accuracy, temp$harmony, method='pearson')
cor(temp$human_accuracy, temp$harmony, method='kendall')
cor(temp$human_accuracy, temp$harmony, method='spearman')


temp = subset(people, simname=='2018-09-25_aymara_words_unparsed_customoutput_final' & experiment=='exp2' & plotname!="FL")
summary(temp)
cor(temp$human_accuracy, temp$harmony, method='pearson')
cor(temp$human_accuracy, temp$harmony, method='kendall')
cor(temp$human_accuracy, temp$harmony, method='spearman')

temp = subset(people, simname=='2018-09-23_aymara_words_wb_vi_gain400_con120output_final' & experiment=='exp1')
summary(temp)
cor(temp$human_accuracy, temp$harmony, method='pearson')
cor(temp$human_accuracy, temp$harmony, method='kendall')
cor(temp$human_accuracy, temp$harmony, method='spearman')

temp = subset(people, simname=='2018-09-23_aymara_words_wb_vi_gain400_con120output_final' & experiment=='exp2')
summary(temp)
cor(temp$human_accuracy, temp$harmony, method='pearson')
cor(temp$human_accuracy, temp$harmony, method='kendall')
cor(temp$human_accuracy, temp$harmony, method='spearman')

temp = subset(people, simname=='2018-09-10_aymara_words_unparsed_wb_vi_gain500_con500output_final' & plotname!='FL')
summary(temp)
cor(temp$human_accuracy, temp$harmony, method='pearson')
cor(temp$human_accuracy, temp$harmony, method='kendall')
cor(temp$human_accuracy, temp$harmony, method='spearman')


temp = subset(people, simname=='2018-09-10_aymara_words_unparsed_wb_vi_gain500_con500output_final' & experiment=='exp1')
summary(temp)
cor(temp$human_accuracy, temp$harmony, method='pearson')
cor(temp$human_accuracy, temp$harmony, method='kendall')
cor(temp$human_accuracy, temp$harmony, method='spearman')

temp = subset(people, simname=='2018-09-10_aymara_words_unparsed_wb_vi_gain500_con500output_final' & experiment=='exp2' & plotname!='FL')
summary(temp)
cor(temp$human_accuracy, temp$harmony, method='pearson')
cor(temp$human_accuracy, temp$harmony, method='kendall')
cor(temp$human_accuracy, temp$harmony, method='spearman')
