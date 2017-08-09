# Part I: makes an expression matrix based on gene library and 3000 randomly chosen samples

# R script to download selected samples
# Copy code and run on a local machine to initiate download

# Check for dependencies and install if missing
packages <- c("rhdf5","downloader")
if (length(setdiff(packages, rownames(installed.packages()))) > 0) {
  print("Install required packages")
  source("https://bioconductor.org/biocLite.R")
  biocLite("rhdf5")
  install.packages("downloader", dependencies=T)
}
library("rhdf5")
library("downloader")

# install package
source("https://bioconductor.org/biocLite.R")
biocLite("preprocessCore")

# load package
library(preprocessCore)

destination_file = "human_matrix_download.h5"
#destination_file_mouse = "mouse_matrix.h5"
# destination_file = "clean_gtex.rda"
extracted_expression_file = "sample_expression_matrix.tsv"

# Check if gene expression file was already downloaded, if not in current directory download file form repository
if(!file.exists(destination_file)){
  print("Downloading compressed gene expression matrix.")
  url = "https://s3.amazonaws.com/mssm-seq-matrix/human_matrix.h5"
  download(url, destination_file, mode="wb")
} else{
  print("Local files already exist.")
}

# Retrieve information from compressed data
samples = h5read(destination_file, "meta/samples")
tissue = h5read(destination_file, "meta/tissue")
# library = h5read(destination_file, "meta/library")
genes = h5read(destination_file, "meta/genes")
# instrument = h5read(destination_file, "meta/instrument")


# Identify columns to be extracted
sample_locations = sample(1:length(samples), 3000)


# extract gene expression from compressed data
expression = h5read(destination_file, "data/expression", index=list(1:length(genes), sample_locations))
H5close()
rownames(expression) = genes
colnames(expression) = samples[sample_locations]


# Print file
write.table(expression, file=extracted_expression_file, sep="\t", quote=FALSE)
print(paste0("Expression file was created at ", getwd(), "/", extracted_expression_file))


# take log2
expression = log2(expression + 1)

# Part II: Make the expression matrix only the genes also in the gmt file. To do so, read the gmt file.

# This script just extracts all the genes from the H_P_O file and removes duplicates. It puts them into a vector.
# it first reads the gmt file

# Reading the gmt file
# gmt = readLines("ENCODE_TF_2015.txt")
gmt = readLines("~/Desktop/Projects/KEA3/Combined Dataset/Combined_human.gmt")

go = list()
for(line in gmt){
  # splits line into the tabbed words
  sp = unlist(strsplit(line, "\t"))
  
  # term is the name of the current phenotype
  term = sp[1]
  
  # t ends up being all the current phenotype's genes, but it's currently empty
  t = c()
  
  # starts at 3 because that's where the genes begin (the name of the phenotype, an empty space, then first gene)
  for(m in 3:length(sp)){
    sp1 = unlist(strsplit( sp[m], ","))
    t = c(t, sp1[1])
  }
  # holds all the phenotypes and their genes in the list format, where the name of the phenotype is the category name
  # Each phenotype is a vector of its genes
  # taking the intersection of the names in expression and the names in this particular list element/phenotype
  go[[length(go)+1]] = intersect(rownames(expression), t) 
  names(go)[length(go)] = term
}

# because of the "intersect()", we now have only the unique genes in both expression library and H_P_O file
gene_vector <- unlist(go, use.names = FALSE)
gene_vector <- unique(gene_vector, incomparables = FALSE, fromLAST = FALSE, nmax = NA)

# now let's normalize matrix of the gene library genes
# We can do this outside of the loop - should be the same for all steps
norm_exprTxt <- normalize.quantiles(expression[gene_vector,])
rownames(norm_exprTxt) <- rownames(expression[gene_vector,])
norm_transposeTxt <- t(norm_exprTxt)

# we want to do quantile normalization on the entire expression matrix
expression <- normalize.quantiles(expression)
rownames(expression) = genes
colnames(expression) = samples[sample_locations]

install.packages('pracma')
library(pracma)

# ok - let's loop now.
auc <- c()
steps <- 20
total <- nrow(expression)
size <- total %/% steps

# scales to a range
scale_vector <- function(x, start, end)
  (x - min(x)) / max(x - min(x)) * (end - start) + start

# so instead of normalizing subsets, expression is already normalized. Take only the subset you need.
# exprTxt <- expression[gene_vector,]

allCrrAvg <- matrix(NA, nrow = nrow(expression), ncol = length(go))
rownames(allCrrAvg) = rownames(expression)
colnames(allCrrAvg) = names(go)

for (i in 1:steps) {
  print(i)  
  
  # so instead of normalizing subsets (again), take only the subset you need...
  exprStep <- expression[(i + size * (i - 1) ):(min(i + size * i, total)),]
  
  # attempting to normalize matrix of [step] human genes and 3,000 randomly chosen samples from humans
  # HERE'S A SECTION THAT MIGHT HAVE TO BE EDITED LATER ON
  # normalizedStep <- normalize.quantiles(expression[(i + size * (i - 1) ):(min(i + size * i, total)),])
  # rownames(normalizedStep) <- rownames(expression)[(i + size * (i - 1) ):(min(i + size * i, total))]
  # colnames(normalizedStep) <- colnames(expression)
  
  # transpose to take the correlation
  # normStepTranspose <- t(normalizedStep)
  
  # making the correlation between all genes and genes in the text file
  stepCorrelation <- cor(x = t(exprStep), y = norm_transposeTxt)
  rownames(stepCorrelation) <- rownames(exprStep)
  colnames(stepCorrelation) <- colnames(norm_transposeTxt)
  
  # now calculate the means of each gene's correlation to each of the gene sets
  
  co_means <- matrix(NA, nrow = nrow(stepCorrelation), ncol = length(names(go)))
  rownames(co_means) <- rownames(stepCorrelation)
  colnames(co_means) <- names(go)
  
  # fixed_correlation <- stepCorrelation
  stepCorrelation[which(stepCorrelation == 1)] <- NaN
  
  # more efficient matrix making - taking a subset of genes based on gene set and averaging the correlations all at once
  for (j in 1:length(go)) {
    gene_set <- go[[j]]
    
    if (length(gene_set) == 1) {
      co_means[, j] <- stepCorrelation[, gene_set]
    } else {
      # now we subset and take the row means
      # co_sums[, j] <- rowSums(stepCorrelation[,gene_set], na.rm = TRUE)
      co_means[, j] <- rowMeans(stepCorrelation[,gene_set], na.rm = TRUE)
    }
  }
  
  allCrrAvg[(i + size * (i - 1) ):(min(i + size * i, total)) , ] <- co_means
  
  # so we construct the auc vector here - remember, the auc vector must be initialized outside of the giant step loop
  # now apply to all rows/genes
  for (current_gene in rownames(co_means)) {
    
    # this will eventually identify which sets have the gene and which sets do not
    containing_gene <- co_means[current_gene,]
    
    # sorts the correlation averages
    # sorted_means <- sort(containing_gene, decreasing = TRUE)
    containing_gene <- sort(containing_gene, decreasing = TRUE)
    
    # for each gene_set in which the gene is a member, we want a 1 to be associated; for the rest, a zero.
    for (k in 1:length(go)) {
      if (current_gene %in% go[[k]]) {
        containing_gene[names(go)[k]] <- 1
      } else {
        containing_gene[names(go)[k]] <- 0
      }
    }
    
    cumulative <- cumsum(containing_gene)
    # putting cumulative into a matrix - hope this works...
    # allCumulative[current_gene,] <- cumulative
    
    # Part II: Now going to make a vector of AUC for all genes. 
    
    # positions of tick marks and labels
    # v1 <- c(0.0, 0.2, 0.4, 0.6, 0.8, 1.0)
    # v2 <- c("0.0", "0.2", "0.4", "0.6", "0.8", "1.0")
    
    scaled_y <- scale_vector(cumulative, 0, 1)
    scaled_x <- scale_vector(1:length(cumulative), 0, 1)
    
    # find the area under the curve
    # height <- max(scaled_x) / length(scaled_x)
    # trap_area <- c(0)
    
    # eliminate the for loop - this can be calculated without
    # for (b in 1:(length(scaled_y)-1)) {
    #   trap_area[b+1] <- 0.5 * height * (scaled_y[b] + scaled_y[b+1])
    # }
    
    # sum all the trapezoids
    # auc[current_gene] <- sum(trap_area)
    
    auc[current_gene] <- trapz(scaled_x, scaled_y)
  }
  
}

# by standard deviation cut-off

newGmt = list()
# # pop_mean = mean(allCrrAvg)
# # pop_sd = sd(allCrrAvg)

for (n in 1:ncol(allCrrAvg)) {
  setOne = (allCrrAvg)[,n] 
  names(setOne) = rownames(allCrrAvg)
  
  setOne = sort(setOne, decreasing = TRUE)
  
  pop_mean = mean(setOne)
  pop_sd = sd(setOne)
  
  pop_z = (setOne - pop_mean) / pop_sd
  
  # cutting off at 3 standard deviations
  # cutOff = sort(pop_z[pop_z >= 3], decreasing = TRUE)
  newSet = names(pop_z[pop_z >= 3])
  
  #creates intersection between newSet and gene_vector
  #ensures only gene present in original gmt will be in
  #final gmt
  newSet = intersect(newSet, gene_vector)
  
  newGmt[[length(newGmt) + 1]] = newSet
  names(newGmt)[length(newGmt)] = colnames(allCrrAvg)[n]
  
}

for (i in 1:length(newGmt)) {
  cat(names(newGmt)[i], paste0(paste(newGmt[[i]], collapse = "\t"), ""), sep = "\t\t")
  cat("\n")
}

sink("Combined_mouse_coexpr.gmt")

