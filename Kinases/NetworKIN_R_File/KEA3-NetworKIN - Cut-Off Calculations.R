network = read.csv('~/Desktop/Projects/KEA3/networkin_human_predictions.tsv', sep = '\t')
colnames = c('substrate_name', 'id', 'networkin_score')
network = network[ , colnames]
network = network[order(network$networkin_score), ]

library(MASS)
fit = fitdistr(network$networkin_score, 'exponential')
para = fit$estimate
#    rate 
#  4.056384 

cut = qexp(0.05, rate = 4.056384, lower.tail = FALSE, log.p = FALSE)
