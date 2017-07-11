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