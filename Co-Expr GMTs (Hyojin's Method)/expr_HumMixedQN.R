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

# install package
source("https://bioconductor.org/biocLite.R")
biocLite("preprocessCore")

# load package
library(preprocessCore)

# now let's normalize matrix of the gene library genes
# We can do this outside of the loop - should be the same for all steps
norm_exprTxt <- normalize.quantiles(expression[gene_vector,])
rownames(norm_exprTxt) <- rownames(expression[gene_vector,])
norm_transposeTxt <- t(norm_exprTxt)

# we want to do quantile normalization on the entire expression matrix
expression <- normalize.quantiles(expression)
rownames(expression) = genes
colnames(expression) = samples[sample_locations]
